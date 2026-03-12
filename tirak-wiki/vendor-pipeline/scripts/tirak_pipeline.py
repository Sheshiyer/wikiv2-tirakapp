"""
Tirak Dream Journeys — Circular Vendor Pipeline
Loops: AUDIT → FILL GAPS → ENRICH CONTACTS → VALIDATE → EXPORT → CHECK
Until ALL 10 categories have >= 50 vendors.
"""
import csv
import json
import logging
import os
import re
import ssl
import sys
import time
from collections import Counter
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen, Request
from scrapling import Fetcher, Selector

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

JSON_PATH = os.path.expanduser("~/tirak_thailand_vendors.json")
OUTPUT_DIR = os.path.expanduser("~/")
LOG_PATH = os.path.expanduser("~/tirak_pipeline.log")
ENRICHMENT_LOG = os.path.expanduser("~/tirak_enrichment_log.json")

MIN_PER_CATEGORY = 50
MAX_LOOP_ITERATIONS = 5
ENRICH_DELAY = 0.5
ENRICH_BATCH_SIZE = 80  # max vendors to enrich per iteration

ALL_CATEGORIES = [
    "Leisure & Experience DMCs",
    "MICE & Event DMCs",
    "Transport & Transfer Services",
    "Adventure & Outdoor Operators",
    "Food & Culinary Operators",
    "Wellness & Spa Services",
    "Boutique Hotels & Hostels",
    "Nightlife & Entertainment",
    "Cinema & Entertainment",
    "Lifestyle & Experiences",
]

# ═══════════════════════════════════════════════════════════════════
# SECTION 2: UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def fetch_static(url):
    """Fast fetch using urllib (5s timeout, no retries) + Scrapling Selector for parsing."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        resp = urlopen(req, timeout=5, context=ctx)
        html = resp.read().decode("utf-8", errors="ignore")
        return Selector(html)
    except Exception as e:
        logging.debug(f"Fetch error {url}: {e}")
        return None

def safe_text(el):
    if el is None:
        return ""
    t = el.text
    return t.strip() if t else ""

def safe_attr(el, attr):
    if el is None:
        return ""
    return el.attrib.get(attr, "")

def normalize_name(name):
    n = name.lower().strip()
    for suffix in [
        "co., ltd.", "co., ltd", "co.,ltd.", "co.,ltd", "co. ltd.",
        "co. ltd", "co.,", "co.", "ltd.", "ltd", "inc.", "inc",
        "thailand", "bangkok", "phuket", "chiang mai",
    ]:
        n = n.replace(suffix, "")
    n = re.sub(r"[^\w\s]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n

def ensure_url(url):
    if not url:
        return ""
    url = str(url).strip()
    if url.startswith("http"):
        return url
    return f"https://{url}"

# ═══════════════════════════════════════════════════════════════════
# SECTION 3: VENDOR STORE
# ═══════════════════════════════════════════════════════════════════

class VendorStore:
    def __init__(self, json_path):
        self.json_path = json_path
        self.vendors = []
        self._name_index = {}
        self._url_index = set()
        self.load()

    def load(self):
        with open(self.json_path) as f:
            self.vendors = json.load(f)
        self._rebuild_indices()

    def _rebuild_indices(self):
        self._name_index = {}
        self._url_index = set()
        for i, v in enumerate(self.vendors):
            norm = normalize_name(v["name"])
            self._name_index[norm] = i
            if v.get("url"):
                self._url_index.add(self._normalize_url(v["url"]))

    @staticmethod
    def _normalize_url(url):
        url = url.lower().strip().rstrip("/")
        url = re.sub(r"^https?://", "", url)
        url = re.sub(r"^www\.", "", url)
        return url

    def is_duplicate(self, name, url=""):
        norm = normalize_name(name)
        if norm in self._name_index:
            return True, self._name_index[norm]
        for existing_norm, idx in self._name_index.items():
            if len(norm) > 5 and len(existing_norm) > 5:
                if norm in existing_norm or existing_norm in norm:
                    return True, idx
        if url:
            norm_url = self._normalize_url(url)
            if norm_url and norm_url in self._url_index:
                return True, -1
        return False, -1

    def add_vendor(self, vendor_dict):
        name = vendor_dict.get("name", "").strip()
        url = vendor_dict.get("url", "")
        if not name or len(name) < 3:
            return False, "name too short"
        is_dupe, dupe_idx = self.is_duplicate(name, url)
        if is_dupe:
            if dupe_idx >= 0:
                enriched = self._enrich_existing(dupe_idx, vendor_dict)
                return False, f"dupe (enriched: {enriched})"
            return False, "dupe by URL"
        self.vendors.append(vendor_dict)
        idx = len(self.vendors) - 1
        self._name_index[normalize_name(name)] = idx
        if url:
            self._url_index.add(self._normalize_url(url))
        return True, "added"

    def _enrich_existing(self, idx, new_data):
        existing = self.vendors[idx]
        enriched = []
        for field in ["phone", "email", "address", "description"]:
            if new_data.get(field) and not existing.get(field):
                existing[field] = new_data[field]
                enriched.append(field)
        return enriched

    def category_counts(self):
        return dict(Counter(v.get("category", "Unknown") for v in self.vendors))

    def underfilled_categories(self):
        counts = self.category_counts()
        return [(cat, counts.get(cat, 0)) for cat in ALL_CATEGORIES
                if counts.get(cat, 0) < MIN_PER_CATEGORY]

    def save_json(self):
        with open(self.json_path, "w") as f:
            json.dump(self.vendors, f, indent=2, ensure_ascii=False)

    def save_csvs(self):
        fieldnames = ["category", "name", "url", "location", "description",
                      "type", "source", "phone", "email", "address"]
        master_csv = os.path.join(OUTPUT_DIR, "tirak_thailand_vendors.csv")
        with open(master_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for v in self.vendors:
                writer.writerow(v)
        by_cat = {}
        for v in self.vendors:
            by_cat.setdefault(v.get("category", "Uncategorized"), []).append(v)
        for cat, vendors in by_cat.items():
            safe = cat.lower().replace(" & ", "_").replace(" ", "_")
            path = os.path.join(OUTPUT_DIR, f"tirak_vendors_{safe}.csv")
            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for v in vendors:
                    writer.writerow(v)

# ═══════════════════════════════════════════════════════════════════
# SECTION 4: CURATED VENDOR LISTS
# ═══════════════════════════════════════════════════════════════════

CURATED_NIGHTLIFE = [
    {"name": "Sky Bar at Lebua", "url": "https://lebua.com/sky-bar/", "location": "Bangkok", "description": "Iconic 64th-floor rooftop bar featured in The Hangover II"},
    {"name": "Octave Rooftop Lounge & Bar", "url": "https://www.marriott.com/hotels/hotel-information/restaurant/bkkms-bangkok-marriott-hotel-sukhumvit/", "location": "Bangkok", "description": "360-degree rooftop bar on 45th-49th floors of Marriott Sukhumvit"},
    {"name": "Vertigo and Moon Bar", "url": "https://www.banyantree.com/thailand/bangkok", "location": "Bangkok", "description": "Open-air rooftop bar atop Banyan Tree Bangkok, 61st floor"},
    {"name": "Maggie Choo's", "url": "https://www.maggiechoos.com/", "location": "Bangkok", "description": "Underground speakeasy bar beneath Novotel Silom"},
    {"name": "Iron Fairies", "url": "https://www.theironfairies.com/", "location": "Bangkok", "description": "Gothic fairy-tale themed cocktail bar in Thonglor"},
    {"name": "Tropic City", "url": "https://www.tropiccity.co/", "location": "Bangkok", "description": "Tropical-themed cocktail bar in Charoenkrung creative district"},
    {"name": "Teens of Thailand", "url": "https://www.teensofthailand.com/", "location": "Bangkok", "description": "Award-winning gin bar in Bangkok's Chinatown"},
    {"name": "Havana Social", "url": "https://www.havanasocialbkk.com/", "location": "Bangkok", "description": "Hidden Cuban-themed speakeasy in Sukhumvit"},
    {"name": "Tichuca Rooftop Bar", "url": "https://www.tichuca.com/", "location": "Bangkok", "description": "Jungle-themed rooftop bar with stunning city views"},
    {"name": "Beam Bangkok", "url": "https://www.beambangkok.com/", "location": "Bangkok", "description": "Underground electronic music club in Thonglor"},
    {"name": "Sing Sing Theater", "url": "https://www.singsingtheater.com/", "location": "Bangkok", "description": "1930s Shanghai-inspired nightclub and performance venue"},
    {"name": "Sugar Club Bangkok", "url": "https://www.sugarclub-bangkok.com/", "location": "Bangkok", "description": "Multi-level nightclub with live DJs on Sukhumvit Soi 11"},
    {"name": "Onyx Bangkok", "url": "https://www.onyxbangkok.com/", "location": "Bangkok", "description": "Premier nightclub hosting international DJs at RCA"},
    {"name": "Route 66 Club", "url": "https://www.route66club.com/", "location": "Bangkok", "description": "Legendary multi-zone nightclub at RCA"},
    {"name": "Levels Club & Lounge", "url": "https://www.levelsclub.com/", "location": "Bangkok", "description": "Upscale nightclub on Sukhumvit Soi 11"},
    {"name": "Ce La Vi Bangkok", "url": "https://www.celavi.com/bangkok/", "location": "Bangkok", "description": "Rooftop club and sky bar atop Sathorn Square"},
    {"name": "Above Eleven Bangkok", "url": "https://www.aboveeleven.com/", "location": "Bangkok", "description": "Peruvian-Japanese rooftop bar in Sukhumvit"},
    {"name": "Vesper Rooftop", "url": "https://www.vesperbar.co/", "location": "Bangkok", "description": "Speakeasy-style cocktail bar on Convent Road, Silom"},
    {"name": "Catch Beach Club Phuket", "url": "https://www.catchbeachclub.com/", "location": "Phuket", "description": "Premier beach club on Bangtao Beach"},
    {"name": "Cafe Del Mar Phuket", "url": "https://www.cafedelmarphuket.com/", "location": "Phuket", "description": "Ibiza-branded beach club in Kamala"},
    {"name": "Xana Beach Club", "url": "https://www.xanabeachclub.com/", "location": "Phuket", "description": "Angsana resort beach club on Bangtao"},
    {"name": "Seduction Nightclub Phuket", "url": "https://www.seductionphuket.com/", "location": "Phuket", "description": "Top nightclub on Bangla Road, Patong"},
    {"name": "Zoe in Yellow", "url": "https://www.facebook.com/zoeinyellow/", "location": "Chiang Mai", "description": "Iconic open-air bar complex in old city nightlife zone"},
    {"name": "Warm Up Cafe", "url": "https://www.facebook.com/warmupcafe/", "location": "Chiang Mai", "description": "Chiang Mai's biggest live music and DJ venue"},
    {"name": "North Gate Jazz Co-Op", "url": "https://www.facebook.com/northgatejazz/", "location": "Chiang Mai", "description": "Legendary jazz bar at Tha Phae Gate"},
    {"name": "THC Rooftop Bar", "url": "https://www.thcrooftop.com/", "location": "Chiang Mai", "description": "Panoramic rooftop bar overlooking Doi Suthep"},
    {"name": "Ark Bar Beach Club", "url": "https://www.ark-bar.com/", "location": "Koh Samui", "description": "Famous beach club on Chaweng Beach"},
    {"name": "Green Mango Club", "url": "https://www.greenmango-samui.com/", "location": "Koh Samui", "description": "Koh Samui's biggest nightclub since 1993"},
    {"name": "Full Moon Party Official", "url": "https://www.fullmoonparty-thailand.com/", "location": "Koh Phangan", "description": "World-famous monthly beach rave on Haad Rin"},
    {"name": "Jungle Experience", "url": "https://www.jungleexperiencephangan.com/", "location": "Koh Phangan", "description": "Monthly jungle trance party"},
    {"name": "Calypso Cabaret", "url": "https://www.calypsocabaret.com/", "location": "Bangkok", "description": "Famous cabaret show at Asiatique The Riverfront"},
    {"name": "Saxophone Pub & Restaurant", "url": "https://www.saxophonepub.com/", "location": "Bangkok", "description": "Live jazz and blues institution since 1987"},
    {"name": "Tawan Daeng German Brewery", "url": "https://www.tawandaeng.com/", "location": "Bangkok", "description": "Massive beer hall with live Muay Thai shows and bands"},
    {"name": "Brown Sugar Jazz Boutique", "url": "https://www.brownsugarbangkok.com/", "location": "Bangkok", "description": "Bangkok's oldest jazz bar since 1985"},
    {"name": "Demo Bangkok", "url": "https://www.demobangkok.com/", "location": "Bangkok", "description": "Thonglor dance club with local DJs"},
    {"name": "Mixx Discotheque", "url": "https://www.mixxdiscotheque.com/", "location": "Bangkok", "description": "Long-running international nightclub in Sukhumvit"},
    {"name": "Insanity Nightclub", "url": "https://www.insanitybangkok.com/", "location": "Bangkok", "description": "EDM nightclub on Sukhumvit Soi 11"},
    {"name": "Walking Street Pattaya", "url": "https://www.walkingstreetpattaya.com/", "location": "Pattaya", "description": "Famous nightlife strip with clubs, bars and shows"},
    {"name": "Differ Pattaya", "url": "https://www.differpattaya.com/", "location": "Pattaya", "description": "Pattaya's largest nightclub venue"},
    {"name": "Ku De Ta Bangkok", "url": "https://www.kudeta.com/bangkok/", "location": "Bangkok", "description": "Rooftop restaurant bar and club at Sathorn Square"},
    {"name": "Spicy Nightclub Phuket", "url": "https://www.spicyphuket.com/", "location": "Phuket", "description": "High-energy club on Bangla Road"},
    {"name": "Siam Dragon Show", "url": "https://www.siamdragonshow.com/", "location": "Pattaya", "description": "Spectacular cultural cabaret performance"},
]

CURATED_CINEMA = [
    {"name": "Escape Hunt Bangkok", "url": "https://escapehunt.com/th/bangkok/", "location": "Bangkok", "description": "Global escape room franchise with themed puzzle rooms"},
    {"name": "BreakOut Bangkok", "url": "https://www.breakout.com.my/bangkok/", "location": "Bangkok", "description": "Immersive escape room experiences"},
    {"name": "MAZE Bangkok", "url": "https://www.mazeescaperoom.com/", "location": "Bangkok", "description": "Themed escape room and puzzle challenges"},
    {"name": "The Escape Game Bangkok", "url": "https://www.theescapegamebkk.com/", "location": "Bangkok", "description": "Puzzle-solving entertainment venue"},
    {"name": "VR Hub Bangkok", "url": "https://www.vrhubbkk.com/", "location": "Bangkok", "description": "Virtual reality gaming and entertainment center"},
    {"name": "Zero Latency Bangkok", "url": "https://www.zerolatencyvr.com/", "location": "Bangkok", "description": "Free-roam VR experiences for groups"},
    {"name": "Blu-O Rhythm & Bowl", "url": "https://www.bluobowl.com/", "location": "Multiple", "description": "Premium bowling chain with karaoke in major malls"},
    {"name": "Dream World Bangkok", "url": "https://www.dreamworld.co.th/", "location": "Bangkok", "description": "Amusement park with rides, snow town and gardens"},
    {"name": "Siam Park City", "url": "https://www.siamparkcity.com/", "location": "Bangkok", "description": "Thailand's largest amusement and water park"},
    {"name": "Safari World Bangkok", "url": "https://www.safariworld.com/", "location": "Bangkok", "description": "Open zoo and marine park with shows"},
    {"name": "SEA LIFE Bangkok Ocean World", "url": "https://www.sealifebangkok.com/", "location": "Bangkok", "description": "Southeast Asia's largest aquarium at Siam Paragon"},
    {"name": "Madame Tussauds Bangkok", "url": "https://www.madametussauds.com/bangkok/", "location": "Bangkok", "description": "Wax museum with celebrity figures at Siam Discovery"},
    {"name": "KidZania Bangkok", "url": "https://www.kidzania.co.th/", "location": "Bangkok", "description": "Role-playing theme park for kids at Siam Paragon"},
    {"name": "Pororo Aquapark Bangkok", "url": "https://www.pororoaquapark.com/", "location": "Bangkok", "description": "Indoor water park at CentralPlaza Bangna"},
    {"name": "Rajadamnern Boxing Stadium", "url": "https://www.rajadamnern.com/", "location": "Bangkok", "description": "Thailand's oldest and most prestigious Muay Thai stadium"},
    {"name": "Lumpinee Boxing Stadium", "url": "https://www.lumpinee.com/", "location": "Bangkok", "description": "Legendary Muay Thai arena, national championship venue"},
    {"name": "Joe Louis Puppet Theatre", "url": "https://www.joelouis-theater.com/", "location": "Bangkok", "description": "Traditional Thai puppet performance art"},
    {"name": "Thailand Cultural Centre", "url": "https://www.tcc.or.th/", "location": "Bangkok", "description": "National performing arts and exhibition center"},
    {"name": "Bangkok Art & Culture Centre", "url": "https://www.bacc.or.th/", "location": "Bangkok", "description": "Contemporary art museum and creative event space"},
    {"name": "Muangthai Rachadalai Theatre", "url": "https://www.muangthairachadalai.com/", "location": "Bangkok", "description": "Broadway-style musical theatre venue"},
    {"name": "Sala Chalermkrung Royal Theatre", "url": "https://www.salachalermkrung.com/", "location": "Bangkok", "description": "Historic royal theatre for traditional Thai masked dance"},
    {"name": "The Bangkok Screening Room", "url": "https://www.bkksr.com/", "location": "Bangkok", "description": "Boutique cinema-bar showing indie and classic films"},
    {"name": "Doc Club & Pub", "url": "https://www.docclubandpub.com/", "location": "Bangkok", "description": "Documentary cinema and creative community space"},
    {"name": "EasyKart Bangkok", "url": "https://www.easykart.net/", "location": "Bangkok, Pattaya, Phuket", "description": "Indoor go-kart racing entertainment"},
    {"name": "Sub Zero Ice Skate Club", "url": "https://www.subzeroiceskate.com/", "location": "Bangkok", "description": "Ice skating rink at multiple malls"},
    {"name": "Bounce Thailand", "url": "https://www.bounceinc.co.th/", "location": "Bangkok", "description": "Trampoline park and aerial adventure"},
    {"name": "Jump Arena", "url": "https://www.jumparena.co.th/", "location": "Bangkok", "description": "Indoor trampoline and adventure park"},
    {"name": "Urban Playground Bangkok", "url": "https://www.urbanplayground.co.th/", "location": "Bangkok", "description": "Climbing and bouldering gym with social area"},
    {"name": "The Rink Ice Arena", "url": "https://www.therink.co.th/", "location": "Bangkok", "description": "Ice skating rink at CentralWorld"},
    {"name": "Mega Harborland", "url": "https://www.megaharborland.com/", "location": "Bangkok", "description": "Giant indoor kids and family playground"},
    {"name": "Phuket FantaSea", "url": "https://www.phuket-fantasea.com/", "location": "Phuket", "description": "Thai cultural theme park with spectacular night show"},
    {"name": "Siam Niramit Bangkok", "url": "https://www.siamniramit.com/", "location": "Bangkok", "description": "World-class cultural show about Thai history"},
    {"name": "Ripley's Believe It or Not Pattaya", "url": "https://www.ripleysthailand.com/", "location": "Pattaya", "description": "Oddity museum and entertainment complex"},
    {"name": "Art in Paradise Pattaya", "url": "https://www.artinparadise.co.th/", "location": "Pattaya", "description": "3D art illusion museum and interactive gallery"},
    {"name": "Nong Nooch Tropical Garden", "url": "https://www.nongnoochtropicalgarden.com/", "location": "Pattaya", "description": "Botanical garden with cultural shows"},
    {"name": "Chiang Mai Night Safari", "url": "https://www.chiangmainightsafari.com/", "location": "Chiang Mai", "description": "Nighttime zoo with tram safari tours"},
    {"name": "Tiger Kingdom Chiang Mai", "url": "https://www.tigerkingdom.com/", "location": "Chiang Mai", "description": "Up-close tiger encounter experience"},
    {"name": "Vana Nava Hua Hin", "url": "https://www.vananavahuahin.com/", "location": "Hua Hin", "description": "Premium water jungle park and entertainment"},
    {"name": "Cartoon Network Amazone", "url": "https://www.cartoonnetworkamazone.com/", "location": "Pattaya", "description": "Cartoon Network themed water park"},
    {"name": "Ramayana Water Park", "url": "https://www.ramayanawaterpark.com/", "location": "Pattaya", "description": "Thailand's biggest water park"},
    {"name": "Sriracha Tiger Zoo", "url": "https://www.tigerzoo.com/", "location": "Chonburi", "description": "Zoo and animal show entertainment"},
]

CURATED_LIFESTYLE = [
    {"name": "Hubba Coworking", "url": "https://www.hubbathailand.com/", "location": "Bangkok", "description": "Thailand's pioneering coworking space since 2012"},
    {"name": "The Hive Bangkok", "url": "https://thehive.co.th/", "location": "Bangkok", "description": "Premium coworking in Thonglor and Prakanong"},
    {"name": "Punspace Chiang Mai", "url": "https://www.punspace.com/", "location": "Chiang Mai", "description": "Top-rated coworking space for digital nomads"},
    {"name": "TCDC Bangkok", "url": "https://www.tcdc.or.th/", "location": "Bangkok", "description": "Thailand Creative & Design Center with coworking"},
    {"name": "KoHub Koh Lanta", "url": "https://www.kohub.org/", "location": "Koh Lanta", "description": "Island coworking and coliving for nomads"},
    {"name": "Camp@Maya Chiang Mai", "url": "https://www.facebook.com/campbyMAYA/", "location": "Chiang Mai", "description": "Free 24hr coworking inside Maya mall"},
    {"name": "AIS Design Centre", "url": "https://www.ais.th/designcentre/", "location": "Bangkok", "description": "Tech-forward coworking and innovation hub"},
    {"name": "JustCo Thailand", "url": "https://www.justcoglobal.com/", "location": "Bangkok", "description": "Singapore-based premium coworking chain"},
    {"name": "WeWork Bangkok", "url": "https://www.wework.com/l/bangkok", "location": "Bangkok", "description": "Global coworking brand with 3 Bangkok locations"},
    {"name": "The Great Room Bangkok", "url": "https://www.thegreatroomoffices.com/", "location": "Bangkok", "description": "Hospitality-inspired premium coworking"},
    {"name": "Regus Thailand", "url": "https://www.regus.com/en-th/", "location": "Multiple", "description": "Global flexible workspace chain with 20+ Thai locations"},
    {"name": "Launchpad Coworking", "url": "https://launchpad.co.th/", "location": "Bangkok", "description": "Startup-focused coworking in Sathorn"},
    {"name": "Virgin Active Thailand", "url": "https://www.virginactive.co.th/", "location": "Bangkok", "description": "Premium fitness club chain with luxury facilities"},
    {"name": "Fitness First Thailand", "url": "https://www.fitnessfirst.co.th/", "location": "Multiple", "description": "International gym chain with 20+ Thai locations"},
    {"name": "F45 Training Bangkok", "url": "https://f45training.co.th/", "location": "Bangkok", "description": "High-intensity interval group fitness"},
    {"name": "CrossFit Bangkok", "url": "https://www.crossfitbangkok.com/", "location": "Bangkok", "description": "CrossFit box with community focus"},
    {"name": "Fight District MMA", "url": "https://www.fightdistrict.com/", "location": "Bangkok", "description": "MMA and martial arts training center"},
    {"name": "IconSiam", "url": "https://www.iconsiam.com/", "location": "Bangkok", "description": "Landmark riverside mega-mall and lifestyle destination"},
    {"name": "Terminal 21", "url": "https://www.terminal21.co.th/", "location": "Bangkok", "description": "Airport-themed shopping mall on Sukhumvit"},
    {"name": "Chatuchak Weekend Market", "url": "https://www.chatuchakmarket.org/", "location": "Bangkok", "description": "World's largest weekend market with 15,000+ stalls"},
    {"name": "Asiatique The Riverfront", "url": "https://www.asiatiquethailand.com/", "location": "Bangkok", "description": "Night bazaar and entertainment complex on Chao Phraya"},
    {"name": "Platinum Fashion Mall", "url": "https://www.platinumfashionmall.com/", "location": "Bangkok", "description": "Wholesale and retail fashion shopping center"},
    {"name": "MBK Center", "url": "https://www.mbk-center.co.th/", "location": "Bangkok", "description": "Iconic 8-floor shopping mall for electronics and fashion"},
    {"name": "EmQuartier", "url": "https://www.theemdistrict.com/", "location": "Bangkok", "description": "Upscale shopping complex in Phrom Phong"},
    {"name": "Siam Discovery", "url": "https://www.siamdiscovery.co.th/", "location": "Bangkok", "description": "Lifestyle and concept store shopping experience"},
    {"name": "Thai Visa Centre", "url": "https://www.thaivisacentre.com/", "location": "Bangkok", "description": "Visa assistance and immigration services"},
    {"name": "Siam Legal International", "url": "https://www.siam-legal.com/", "location": "Bangkok", "description": "Legal and visa services for expats and travelers"},
    {"name": "Key Visa Thailand", "url": "https://www.keyvisa.com/", "location": "Bangkok", "description": "Work permit and visa consultancy"},
    {"name": "Iglu Coworking & Visa", "url": "https://iglu.net/", "location": "Multiple", "description": "Coworking, visa, and company services for nomads"},
    {"name": "Duke Language School", "url": "https://www.dukelanguage.com/", "location": "Bangkok", "description": "Thai and English language courses for all levels"},
    {"name": "Pro Language School", "url": "https://www.prolanguage.co.th/", "location": "Bangkok", "description": "Thai language school with ED visa support"},
    {"name": "Thai Language Station", "url": "https://www.thailanguagestation.com/", "location": "Bangkok", "description": "Thai courses for foreigners with online options"},
    {"name": "Raja's Fashions", "url": "https://www.rajasfashions.com/", "location": "Bangkok", "description": "Renowned bespoke tailor since 1979"},
    {"name": "Narry Tailor", "url": "https://www.narrytailor.com/", "location": "Bangkok", "description": "Custom-made suits and formal wear"},
    {"name": "Pinky Tailor", "url": "https://www.pinkytailor.com/", "location": "Bangkok", "description": "Long-established bespoke tailor in Bangkok"},
    {"name": "Ambassador Fashions", "url": "https://www.ambassadorfashion.com/", "location": "Bangkok", "description": "Made-to-measure suits and shirts"},
    {"name": "Float Bangkok", "url": "https://www.floatbangkok.com/", "location": "Bangkok", "description": "Sensory deprivation float tank wellness center"},
    {"name": "CryoFit Bangkok", "url": "https://www.cryofit.co.th/", "location": "Bangkok", "description": "Cryotherapy and recovery center"},
    {"name": "Mellow Coworking", "url": "https://www.mellowcoworking.com/", "location": "Koh Phangan", "description": "Beachside coworking for island nomads"},
    {"name": "Outpost Coworking", "url": "https://www.outpost-asia.com/", "location": "Koh Samui", "description": "Coliving and coworking on Koh Samui"},
    {"name": "CentralWorld", "url": "https://www.centralworld.co.th/", "location": "Bangkok", "description": "One of the world's largest lifestyle shopping complexes"},
    {"name": "Siam Paragon", "url": "https://www.siamparagon.co.th/", "location": "Bangkok", "description": "Luxury shopping mall with entertainment and dining"},
    {"name": "One Nimman Chiang Mai", "url": "https://www.onenimman.com/", "location": "Chiang Mai", "description": "Lifestyle mall and community space in Nimman"},
    {"name": "The Commons Saladaeng", "url": "https://www.thecommonsbkk.com/", "location": "Bangkok", "description": "Community mall with curated food, retail and coworking"},
    {"name": "Samyan CO-OP", "url": "https://www.samyanmitrtown.com/", "location": "Bangkok", "description": "24-hour co-learning and coworking space at Samyan Mitrtown"},
    {"name": "LIDO Connect", "url": "https://www.lidoconnect.com/", "location": "Bangkok", "description": "Creative arts, culture and coworking community space in Siam"},
    {"name": "TCDC Chiang Mai", "url": "https://www.tcdc.or.th/chiangmai/", "location": "Chiang Mai", "description": "Northern branch of Thailand Creative & Design Center"},
    {"name": "Climb Central Bangkok", "url": "https://www.climbcentral.co.th/", "location": "Bangkok", "description": "Indoor rock climbing and bouldering gym"},
]

CURATED_TRANSPORT = [
    {"name": "Nakhonchai Air (NCA)", "url": "https://www.nakhonchaiair.com/", "location": "National", "description": "Thailand's premier VIP long-distance bus service"},
    {"name": "Sombat Tour", "url": "https://www.sombathouse.com/", "location": "National", "description": "Major long-distance bus operator in Thailand"},
]


# ═══════════════════════════════════════════════════════════════════
# SECTION 5: CONTACT ENRICHMENT ENGINE
# ═══════════════════════════════════════════════════════════════════

PHONE_RE = re.compile(r'(?:\+66|0)\s*[\-\.]?\s*\d{1,2}\s*[\-\.]?\s*\d{3,4}\s*[\-\.]?\s*\d{3,4}')
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
SPAM_EMAIL_DOMAINS = {"example.com", "sentry.io", "wixpress.com", "schema.org",
                       "googleapis.com", "w3.org", "wordpress.org", "jquery.com",
                       "cloudflare.com", "google.com", "facebook.com", "gstatic.com"}

def load_enrichment_log():
    if os.path.exists(ENRICHMENT_LOG):
        with open(ENRICHMENT_LOG) as f:
            return set(json.load(f))
    return set()

def save_enrichment_log(attempted):
    with open(ENRICHMENT_LOG, "w") as f:
        json.dump(list(attempted), f)

def extract_contacts_from_page(page):
    contacts = {}
    if not page:
        return contacts
    try:
        text = page.get_all_text() or ""
    except Exception:
        text = ""
    # Phone
    phones = PHONE_RE.findall(text)
    if phones:
        contacts["phone"] = phones[0].strip()
    # Email — mailto links first
    try:
        mailto_links = page.css("a[href^='mailto:']")
        if mailto_links:
            email = safe_attr(mailto_links[0], "href").replace("mailto:", "").split("?")[0]
            if email and "@" in email:
                domain = email.split("@")[1].lower()
                if domain not in SPAM_EMAIL_DOMAINS:
                    contacts["email"] = email.strip()
    except Exception:
        pass
    if "email" not in contacts:
        emails = EMAIL_RE.findall(text)
        valid = [e for e in emails if e.split("@")[1].lower() not in SPAM_EMAIL_DOMAINS]
        if valid:
            contacts["email"] = valid[0]
    # Address
    try:
        addr_els = page.css("address") or page.css("[class*='address']") or page.css("[itemprop='address']")
        if addr_els:
            addr = safe_text(addr_els[0])
            if addr and len(addr) > 10:
                contacts["address"] = addr[:200]
    except Exception:
        pass
    return contacts

def enrich_vendor(vendor, attempted_urls):
    url = vendor.get("url", "")
    if not url or url in attempted_urls:
        return {}
    attempted_urls.add(url)
    contacts = {}
    page = fetch_static(url)
    if page:
        contacts.update(extract_contacts_from_page(page))
    # Try /contact if still missing
    if not contacts.get("phone") or not contacts.get("email"):
        for path in ["/contact", "/contact-us", "/about"]:
            time.sleep(ENRICH_DELAY)
            contact_url = urljoin(url.rstrip("/") + "/", path.lstrip("/"))
            page2 = fetch_static(contact_url)
            if page2:
                new = extract_contacts_from_page(page2)
                for k, v in new.items():
                    if k not in contacts:
                        contacts[k] = v
                if contacts.get("phone") and contacts.get("email"):
                    break
    return contacts


# ═══════════════════════════════════════════════════════════════════
# SECTION 6: VALIDATION
# ═══════════════════════════════════════════════════════════════════

def validate_vendor(v):
    errors = []
    if not v.get("name") or len(v["name"]) < 3:
        errors.append("bad name")
    if v.get("category") not in ALL_CATEGORIES:
        errors.append(f"unknown category: {v.get('category')}")
    if not v.get("url") or not str(v["url"]).startswith("http"):
        errors.append("bad url")
    return errors


# ═══════════════════════════════════════════════════════════════════
# SECTION 7: PIPELINE ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════

def run_pipeline():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler(sys.stdout),
        ]
    )
    store = VendorStore(JSON_PATH)
    attempted_urls = load_enrichment_log()

    CATEGORY_CURATED = {
        "Nightlife & Entertainment": CURATED_NIGHTLIFE,
        "Cinema & Entertainment": CURATED_CINEMA,
        "Lifestyle & Experiences": CURATED_LIFESTYLE,
        "Transport & Transfer Services": CURATED_TRANSPORT,
    }

    for iteration in range(1, MAX_LOOP_ITERATIONS + 1):
        logging.info(f"\n{'='*70}")
        logging.info(f"PIPELINE ITERATION {iteration}")
        logging.info(f"{'='*70}")

        # ── PHASE 1: AUDIT ──
        underfilled = store.underfilled_categories()
        counts = store.category_counts()
        logging.info("Category audit:")
        for cat in ALL_CATEGORIES:
            c = counts.get(cat, 0)
            status = "✅" if c >= MIN_PER_CATEGORY else f"🔴 need {MIN_PER_CATEGORY - c}"
            logging.info(f"  {cat:45s} {c:4d}  {status}")

        if not underfilled:
            logging.info("\n✅ ALL CATEGORIES MEET THRESHOLD. Pipeline complete!")
            break

        # ── PHASE 2: FILL GAPS ──
        for cat, current_count in underfilled:
            needed = MIN_PER_CATEGORY - current_count
            logging.info(f"\nFilling {cat}: need {needed} more")
            curated = CATEGORY_CURATED.get(cat, [])
            added_count = 0
            for vendor_data in curated:
                if added_count >= needed:
                    break
                vendor = dict(vendor_data)
                vendor["category"] = cat
                vendor["url"] = ensure_url(vendor.get("url", ""))
                vendor.setdefault("source", "pipeline-curated")
                errors = validate_vendor(vendor)
                if errors:
                    logging.debug(f"  Skip invalid: {vendor.get('name')} {errors}")
                    continue
                added, reason = store.add_vendor(vendor)
                if added:
                    added_count += 1
                    logging.info(f"  + {vendor['name']}")
                else:
                    logging.debug(f"  Skip: {vendor.get('name')} ({reason})")
            logging.info(f"  → Added {added_count} to {cat}")

        # ── PHASE 3: ENRICH CONTACTS ──
        logging.info(f"\nContact enrichment (batch of {ENRICH_BATCH_SIZE})...")
        to_enrich = [
            v for v in store.vendors
            if v.get("url")
            and (not v.get("phone") or not v.get("email"))
            and v["url"] not in attempted_urls
        ]
        logging.info(f"  {len(to_enrich)} vendors eligible, processing up to {ENRICH_BATCH_SIZE}")
        enriched_count = 0
        for i, vendor in enumerate(to_enrich[:ENRICH_BATCH_SIZE]):
            if i > 0 and i % 20 == 0:
                logging.info(f"  Progress: {i}/{min(len(to_enrich), ENRICH_BATCH_SIZE)}")
            contacts = enrich_vendor(vendor, attempted_urls)
            if contacts:
                for field, value in contacts.items():
                    if not vendor.get(field):
                        vendor[field] = value
                enriched_count += 1
            time.sleep(ENRICH_DELAY)
        logging.info(f"  → Enriched {enriched_count} vendors with new contact data")
        save_enrichment_log(attempted_urls)

        # ── PHASE 4: VALIDATE ──
        logging.info("\nValidation...")
        invalid = sum(1 for v in store.vendors if validate_vendor(v))
        logging.info(f"  {invalid} vendors have validation issues")

        # ── PHASE 5: EXPORT ──
        store.save_json()
        store.save_csvs()
        logging.info(f"\nExported {len(store.vendors)} vendors")

        # ── PHASE 6: LOOP CHECK ──
        still_under = store.underfilled_categories()
        if not still_under:
            logging.info("\n✅ ALL CATEGORIES MEET THRESHOLD!")
            break
        else:
            logging.info(f"\nStill underfilled:")
            for cat, c in still_under:
                logging.info(f"  {cat}: {c}/{MIN_PER_CATEGORY}")

    # ── FINAL REPORT ──
    print_final_report(store)


def print_final_report(store):
    counts = store.category_counts()
    total = len(store.vendors)
    has_phone = sum(1 for v in store.vendors if v.get("phone"))
    has_email = sum(1 for v in store.vendors if v.get("email"))
    has_addr = sum(1 for v in store.vendors if v.get("address"))

    print(f"\n{'='*70}")
    print("TIRAK PIPELINE — FINAL REPORT")
    print(f"{'='*70}")
    print(f"\nTotal vendors: {total}")
    all_met = True
    for cat in ALL_CATEGORIES:
        c = counts.get(cat, 0)
        flag = "✅" if c >= MIN_PER_CATEGORY else "🔴"
        if c < MIN_PER_CATEGORY:
            all_met = False
        print(f"  {cat:45s} {c:4d}  {flag}")
    print(f"\nContact coverage:")
    print(f"  Phone:   {has_phone:4d}/{total} ({100*has_phone//total}%)")
    print(f"  Email:   {has_email:4d}/{total} ({100*has_email//total}%)")
    print(f"  Address: {has_addr:4d}/{total} ({100*has_addr//total}%)")
    print(f"\nThreshold: {'ALL MET ✅' if all_met else 'GAPS REMAIN 🔴'}")

    # Dedup check
    norms = [normalize_name(v["name"]) for v in store.vendors]
    if len(norms) == len(set(norms)):
        print(f"Duplicates: NONE ✅")
    else:
        from collections import Counter as C2
        dupes = [n for n, c in C2(norms).items() if c > 1]
        print(f"Duplicates: {len(dupes)} found ⚠️")
    print(f"{'='*70}")


if __name__ == "__main__":
    run_pipeline()
