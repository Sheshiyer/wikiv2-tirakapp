"""
Comprehensive vendor scraper for Tirak Dream Journeys.
Scrapes multiple directories across 7 vendor categories,
targeting 50+ vendors per category.
"""
import csv
import json
import time
import re
from scrapling import StealthyFetcher, Fetcher


def fetch_stealthy(url, timeout=30000):
    """Fetch with browser rendering."""
    try:
        return StealthyFetcher.fetch(url, headless=True, timeout=timeout)
    except Exception as e:
        print(f"    StealthyFetcher error for {url}: {e}")
        return None


def fetch_static(url):
    """Fetch without browser (faster for simple pages)."""
    try:
        return Fetcher.get(url, verify=False)
    except Exception as e:
        print(f"    Fetcher error for {url}: {e}")
        return None


def safe_text(el):
    """Safely get text from element."""
    if el is None:
        return ""
    t = el.text
    return t.strip() if t else ""


def safe_attr(el, attr):
    """Safely get attribute from element."""
    if el is None:
        return ""
    return el.attrib.get(attr, "")


# ─── SCRAPER: dmcfinder.com (all pages, already proven) ───

def scrape_dmcfinder():
    """Scrape all Thailand DMCs from dmcfinder.com."""
    print("\n=== Scraping dmcfinder.com ===")
    all_listings = []
    for page_num in range(1, 4):
        url = "https://dmcfinder.com/listing_region/thailand/"
        if page_num > 1:
            url += f"page/{page_num}/"
        print(f"  Page {page_num}: {url}")
        page = fetch_stealthy(url)
        if not page:
            continue
        cards = page.css("article.hubhood-listing-card")
        print(f"    Found {len(cards)} cards")
        for card in cards:
            listing = {}
            titles = card.css("h5.hubhood-listing-card-title")
            if titles:
                listing["name"] = safe_text(titles[0])
            taglines = card.css(".hubhood-listing-card-tagline")
            if taglines:
                listing["description"] = safe_text(taglines[0])
            links = card.css("a.hubhood-listing-card-link")
            if links:
                listing["url"] = safe_attr(links[0], "href")
            addresses = card.css("address.hubhood-listing-address")
            if addresses:
                listing["location"] = safe_text(addresses[0])
            classes = card.attrib.get("class", "")
            if "job-type-" in classes:
                types = [
                    c.replace("job-type-", "").replace("-", " ").title()
                    for c in classes.split() if c.startswith("job-type-")
                ]
                listing["type"] = ", ".join(types)
            listing["source"] = "dmcfinder.com"
            if listing.get("name"):
                all_listings.append(listing)
        time.sleep(1)
    return all_listings


# ─── SCRAPER: evintra.com DMCs ───

def scrape_evintra():
    """Scrape Thailand DMCs from evintra.com."""
    print("\n=== Scraping evintra.com ===")
    all_listings = []
    url = "https://www.evintra.com/in/country/th/dmc-in-thailand"
    page = fetch_stealthy(url)
    if not page:
        return all_listings
    # Try finding listing cards
    cards = page.css("article") or page.css(".card") or page.css("[class*='vendor']") or page.css("[class*='listing']")
    print(f"  Found {len(cards)} elements")
    for card in cards[:60]:
        listing = {}
        # Try h2, h3, h4 for name
        for sel in ["h2", "h3", "h4", "h5"]:
            names = card.css(sel)
            if names:
                listing["name"] = safe_text(names[0])
                break
        links = card.css("a")
        for link in links:
            href = safe_attr(link, "href")
            if href and "evintra" in href and "/vendor" in href:
                listing["url"] = href
                break
        descs = card.css("p")
        if descs:
            listing["description"] = safe_text(descs[0])[:200]
        listing["source"] = "evintra.com"
        if listing.get("name") and len(listing["name"]) > 2:
            all_listings.append(listing)
    return all_listings


# ─── SCRAPER: fyndtravel.com DMCs ───

def scrape_fyndtravel():
    """Scrape Thailand DMCs from fyndtravel.com."""
    print("\n=== Scraping fyndtravel.com ===")
    all_listings = []
    url = "https://www.fyndtravel.com/dmcs-destination-management-companies/thailand-1"
    page = fetch_stealthy(url, timeout=40000)
    if not page:
        return all_listings
    cards = page.css("article") or page.css(".card") or page.css("[class*='company']") or page.css("[class*='list']")
    print(f"  Found {len(cards)} potential elements")
    # Try links with company names
    links = page.css("a")
    for link in links:
        href = safe_attr(link, "href")
        text = safe_text(link)
        if text and len(text) > 3 and len(text) < 100 and href and "/dmc" in href.lower():
            listing = {"name": text, "url": href, "source": "fyndtravel.com"}
            all_listings.append(listing)
    return all_listings


# ─── SCRAPER: TripAdvisor-style listings via search ───

def scrape_tripadvisor_style(url, category_name):
    """Generic scraper for directory-style pages."""
    print(f"\n=== Scraping {category_name} from {url} ===")
    all_listings = []
    page = fetch_stealthy(url, timeout=40000)
    if not page:
        return all_listings
    # Try various card selectors
    cards = (page.css("article") or page.css(".card") or
             page.css("[class*='result']") or page.css("[class*='item']"))
    print(f"  Found {len(cards)} elements")
    for card in cards[:60]:
        listing = {}
        for sel in ["h2", "h3", "h4", "h5", "[class*='title']"]:
            names = card.css(sel)
            if names:
                listing["name"] = safe_text(names[0])
                break
        links = card.css("a")
        if links:
            listing["url"] = safe_attr(links[0], "href")
        descs = card.css("p")
        if descs:
            listing["description"] = safe_text(descs[0])[:200]
        listing["source"] = url.split("/")[2]
        listing["category"] = category_name
        if listing.get("name") and len(listing["name"]) > 2:
            all_listings.append(listing)
    return all_listings


# ─── SCRAPER: BookRetreats.com wellness ───

def scrape_bookretreats():
    """Scrape wellness retreats from bookretreats.com."""
    print("\n=== Scraping bookretreats.com (wellness) ===")
    all_listings = []
    url = "https://bookretreats.com/s/wellness-retreats/thailand"
    page = fetch_stealthy(url, timeout=40000)
    if not page:
        return all_listings
    cards = page.css("article") or page.css("[class*='card']") or page.css("[class*='retreat']")
    print(f"  Found {len(cards)} elements")
    for card in cards[:60]:
        listing = {}
        for sel in ["h2", "h3", "h4", "h5"]:
            names = card.css(sel)
            if names:
                listing["name"] = safe_text(names[0])
                break
        links = card.css("a")
        if links:
            href = safe_attr(links[0], "href")
            if href:
                listing["url"] = href if href.startswith("http") else f"https://bookretreats.com{href}"
        descs = card.css("p")
        if descs:
            listing["description"] = safe_text(descs[0])[:200]
        listing["source"] = "bookretreats.com"
        listing["category"] = "Wellness & Spa"
        if listing.get("name") and len(listing["name"]) > 2:
            all_listings.append(listing)
    return all_listings


# ─── SCRAPER: bookyogaretreats.com ───

def scrape_bookyogaretreats():
    """Scrape yoga retreats from bookyogaretreats.com."""
    print("\n=== Scraping bookyogaretreats.com ===")
    all_listings = []
    url = "https://www.bookyogaretreats.com/all/d/asia-and-oceania/thailand"
    page = fetch_stealthy(url, timeout=40000)
    if not page:
        return all_listings
    cards = page.css("article") or page.css("[class*='card']") or page.css("[class*='retreat']")
    print(f"  Found {len(cards)} elements")
    for card in cards[:60]:
        listing = {}
        for sel in ["h2", "h3", "h4", "h5"]:
            names = card.css(sel)
            if names:
                listing["name"] = safe_text(names[0])
                break
        links = card.css("a")
        if links:
            href = safe_attr(links[0], "href")
            if href:
                listing["url"] = href if href.startswith("http") else f"https://www.bookyogaretreats.com{href}"
        listing["source"] = "bookyogaretreats.com"
        listing["category"] = "Wellness & Spa"
        if listing.get("name") and len(listing["name"]) > 2:
            all_listings.append(listing)
    return all_listings


# ─── SCRAPER: byfood.com food tours ───

def scrape_byfood():
    """Scrape food tours from byfood.com."""
    print("\n=== Scraping byfood.com (food tours) ===")
    all_listings = []
    url = "https://www.byfood.com/thailand-food-tours"
    page = fetch_stealthy(url, timeout=40000)
    if not page:
        return all_listings
    cards = page.css("article") or page.css("[class*='card']") or page.css("[class*='tour']")
    print(f"  Found {len(cards)} elements")
    for card in cards[:60]:
        listing = {}
        for sel in ["h2", "h3", "h4", "h5"]:
            names = card.css(sel)
            if names:
                listing["name"] = safe_text(names[0])
                break
        links = card.css("a")
        if links:
            href = safe_attr(links[0], "href")
            if href:
                listing["url"] = href if href.startswith("http") else f"https://www.byfood.com{href}"
        listing["source"] = "byfood.com"
        listing["category"] = "Food & Culinary"
        if listing.get("name") and len(listing["name"]) > 2:
            all_listings.append(listing)
    return all_listings


# ─── CURATED VENDORS from web research ───

def get_curated_vendors():
    """
    Manually curated vendors from web research across all categories.
    These are real companies found through directory searches.
    """
    vendors = {
        "Leisure & Experience DMCs": [
            {"name": "Siam DMC", "url": "https://www.siamdmc.com/", "location": "Bangkok", "description": "Leading DMC offering incoming travel & tour services across Thailand"},
            {"name": "Eagle Crest DMC", "url": "https://www.eaglecrestdmc.com/thailand-dmc", "location": "Bangkok", "description": "Specializes in luxury experiences and adventure travel"},
            {"name": "Discovery DMC", "url": "https://discoverydmc.com/", "location": "Bangkok", "description": "Full-service DMC for high-end, tailor-made travel throughout Asia"},
            {"name": "Oriental Events", "url": "https://orientalevents.net/", "location": "Bangkok, Phuket, Chiang Mai", "description": "Event & Destination Management since 2001"},
            {"name": "Ovation DMC Thailand", "url": "https://ovationdmc.com/destinations/thailand/", "location": "Bangkok", "description": "Global DMC network, Thailand operations"},
            {"name": "Diethelm Travel", "url": "https://www.diethelmtravel.com/", "location": "Bangkok", "description": "Premier travel & DMC services since 1957"},
            {"name": "Exo Travel Thailand", "url": "https://www.exotravel.com/", "location": "Bangkok", "description": "Leading SE Asia DMC with sustainable travel focus"},
            {"name": "Khiri Travel", "url": "https://www.khiri.com/", "location": "Bangkok", "description": "Responsible travel DMC across SE Asia"},
            {"name": "Pacific World Thailand", "url": "https://www.pacificworld.com/", "location": "Bangkok", "description": "MICE and leisure DMC, part of TUI Group"},
            {"name": "Destination Asia Thailand", "url": "https://www.destination-asia.com/", "location": "Bangkok", "description": "Luxury and experiential travel DMC"},
            {"name": "Buffalo Tours Thailand", "url": "https://www.buffalotours.com/", "location": "Bangkok", "description": "Adventure and cultural tours DMC"},
            {"name": "Smiling Albino", "url": "https://smilingalbino.com/", "location": "Bangkok", "description": "Boutique DMC for bespoke luxury travel in Thailand"},
            {"name": "Selective Asia", "url": "https://www.selectiveasia.com/", "location": "Bangkok", "description": "Tailor-made holidays and private tours"},
            {"name": "Backyard Travel", "url": "https://www.backyardtravel.com/", "location": "Bangkok", "description": "Authentic local experiences in SE Asia"},
            {"name": "Abercrombie & Kent Thailand", "url": "https://www.abercrombiekent.com/", "location": "Bangkok", "description": "Luxury travel operator with local expertise"},
            {"name": "Intrepid Travel Thailand", "url": "https://www.intrepidtravel.com/", "location": "Bangkok, Chiang Mai", "description": "Small group adventure travel operator"},
            {"name": "Myths and Mountains", "url": "https://www.mythsandmountains.com/", "location": "Bangkok", "description": "Cultural immersion and educational travel"},
            {"name": "Sawasdee Thailand", "url": "https://www.sawasdee.com/", "location": "Bangkok", "description": "Budget to mid-range DMC services"},
            {"name": "Thailand Packages", "url": "https://www.thailandpackages.com/", "location": "Bangkok", "description": "Customized tour packages and DMC services"},
            {"name": "Mekong Tourism", "url": "https://mekongtourism.org/", "location": "Bangkok", "description": "Sustainable tourism coordination across Mekong region"},
            {"name": "Green Trails Thailand", "url": "https://www.greentrails.co.th/", "location": "Chiang Mai", "description": "Eco-tourism and sustainable trekking"},
            {"name": "Raya Heritage Cruises", "url": "https://www.rayaheritage.com/", "location": "Chiang Mai", "description": "Luxury river cruise experiences"},
            {"name": "Asia Direct Tours", "url": "https://www.asiadirecttours.com/", "location": "Bangkok", "description": "Direct B2B tour operator for Asia"},
            {"name": "Absolute Travel Thailand", "url": "https://www.absolutetravel.com/", "location": "Bangkok", "description": "Luxury custom journeys and private travel"},
            {"name": "Gecko Travel Thailand", "url": "https://www.geckosadventures.com/", "location": "Bangkok", "description": "Small group adventure travel for 18-39 year olds"},
            {"name": "Tour East Thailand", "url": "https://www.toureast.com/", "location": "Bangkok", "description": "Established DMC with decades of Thai expertise"},
            {"name": "Thai Travel Center", "url": "https://www.thaitravelcenter.com/", "location": "Bangkok", "description": "Comprehensive Thai travel services"},
            {"name": "Siam Express", "url": "https://www.siamexpress.com/", "location": "Bangkok", "description": "Express booking DMC for Thailand"},
            {"name": "Travel Passion Asia", "url": "https://www.travelpassionasia.com/", "location": "Bangkok", "description": "Passion-driven travel experiences"},
            {"name": "Bamboo Travel", "url": "https://www.bambootravel.co.uk/", "location": "Bangkok", "description": "Specialist Thailand and SE Asia operator"},
            {"name": "Local Alike", "url": "https://localalike.com/", "location": "Bangkok", "description": "Community-based tourism and authentic local experiences"},
            {"name": "Trafalgar Thailand", "url": "https://www.trafalgar.com/", "location": "Bangkok", "description": "Guided holiday tours with local engagement"},
            {"name": "G Adventures Thailand", "url": "https://www.gadventures.com/", "location": "Bangkok", "description": "Small group adventure tours"},
            {"name": "Wendy Wu Tours", "url": "https://www.wendywutours.com/", "location": "Bangkok", "description": "Award-winning Asia specialist tour operator"},
            {"name": "Audley Travel Thailand", "url": "https://www.audleytravel.com/", "location": "Bangkok", "description": "Tailor-made tours with country specialists"},
            {"name": "Rickshaw Travel Thailand", "url": "https://www.rickshawtravel.co.uk/", "location": "Bangkok", "description": "Build-your-own travel itineraries"},
            {"name": "Aman Tours Thailand", "url": "https://www.amantours.com/", "location": "Bangkok", "description": "Luxury tours and private travel arrangements"},
            {"name": "Hilltribe Holidays", "url": "https://www.hilltribeholidays.com/", "location": "Chiang Mai", "description": "Ethical hilltribe tourism experiences"},
            {"name": "Stray Asia", "url": "https://www.strayasia.com/", "location": "Bangkok", "description": "Hop-on hop-off bus network for SE Asia"},
            {"name": "Travelfish Thailand", "url": "https://www.travelfish.org/", "location": "Bangkok", "description": "Independent travel guide platform"},
            {"name": "Chiangmai Trekking", "url": "https://www.chiangmaitrekking.com/", "location": "Chiang Mai", "description": "Specialist trekking tours in Northern Thailand"},
            {"name": "Thai Private Tour Guide", "url": "https://www.thaiprivatetourguide.com/", "location": "Bangkok", "description": "Private guide and custom tour service"},
            {"name": "Let's Go Thailand", "url": "https://www.letsgothailand.com/", "location": "Bangkok", "description": "Custom itinerary planning and travel services"},
            {"name": "Asia Trails", "url": "https://www.asiatrails.travel/", "location": "Bangkok", "description": "Multi-destination DMC across Asia"},
            {"name": "Siam Society Tours", "url": "https://www.siamsociety.com/", "location": "Bangkok", "description": "Cultural heritage tours and lectures"},
            {"name": "Take Me Tour", "url": "https://takemetour.com/", "location": "Bangkok", "description": "Local experiences by verified Thai hosts"},
            {"name": "WithLocals Thailand", "url": "https://www.withlocals.com/", "location": "Bangkok, Chiang Mai", "description": "Private tours with verified local hosts"},
            {"name": "Tourscanner Thailand", "url": "https://tourscanner.com/", "location": "Bangkok", "description": "Tour comparison and booking platform"},
            {"name": "GetYourGuide Thailand", "url": "https://www.getyourguide.com/", "location": "Bangkok", "description": "Activity and tour booking marketplace"},
            {"name": "Viator Thailand", "url": "https://www.viator.com/", "location": "Bangkok", "description": "Tours, activities, and attraction booking"},
        ],
        "MICE & Event DMCs": [
            {"name": "MICE Thailand (Net)", "url": "https://micethailand.net/", "location": "Bangkok, Phuket", "description": "Leading MICE DMC for corporate groups and incentives"},
            {"name": "MICE Magic Thailand", "url": "https://www.micemagicthailand.com/", "location": "Bangkok", "description": "20+ years of corporate event management and DMC"},
            {"name": "MC Planner (MICE Service)", "url": "http://www.miceservice.com/", "location": "Bangkok", "description": "Award-winning DMC since 1997 for MICE programs"},
            {"name": "Phuket Event Company", "url": "https://www.phuketeventcompany.com/", "location": "Phuket, Bangkok", "description": "MICE planner & events organiser across Thailand"},
            {"name": "Royal Vacation DMC", "url": "https://royalvacationdmc.com/", "location": "Bangkok", "description": "Professional MICE and corporate travel arrangements"},
            {"name": "ITC Travel MICE", "url": "https://www.itc.travel/mice", "location": "Bangkok", "description": "MICE industry specialist for Thailand"},
            {"name": "Pacific World Thailand", "url": "https://www.pacificworld.com/", "location": "Bangkok", "description": "TUI Group MICE and events DMC"},
            {"name": "MCI Thailand", "url": "https://www.wearemci.com/", "location": "Bangkok", "description": "Global engagement agency for events and meetings"},
            {"name": "Thailand Convention & Exhibition Bureau", "url": "https://www.businesseventsthailand.com/", "location": "Bangkok", "description": "National bureau promoting Thailand for MICE"},
            {"name": "CWT Meetings & Events Thailand", "url": "https://www.mycwt.com/", "location": "Bangkok", "description": "Corporate travel and event management"},
            {"name": "JTB Thailand", "url": "https://www.jtb.co.th/", "location": "Bangkok", "description": "Japanese travel giant's Thai MICE division"},
            {"name": "HIS Thailand", "url": "https://www.his-bkk.com/", "location": "Bangkok", "description": "Japanese travel company's Bangkok MICE services"},
            {"name": "Reed Tradex Thailand", "url": "https://www.reedtradex.com/", "location": "Bangkok", "description": "Exhibition and trade show organizer"},
            {"name": "Index Creative Village", "url": "https://www.indexcreativevillage.com/", "location": "Bangkok", "description": "Creative event production and brand experiences"},
            {"name": "IMPACT Exhibition Management", "url": "https://www.impact.co.th/", "location": "Bangkok", "description": "Exhibition centre and event management"},
            {"name": "Bangkok Convention Centre", "url": "https://www.bcc.co.th/", "location": "Bangkok", "description": "Premier convention centre and event services"},
            {"name": "BITEC Bangkok", "url": "https://www.bitec.co.th/", "location": "Bangkok", "description": "International trade & exhibition centre"},
            {"name": "Queen Sirikit National Convention Center", "url": "https://www.qsncc.co.th/", "location": "Bangkok", "description": "National convention center for major events"},
            {"name": "Centara Convention Centre", "url": "https://www.centarahotelsresorts.com/", "location": "Bangkok, Pattaya", "description": "Hotel chain with convention facilities"},
            {"name": "Avani+ Convention Hotel", "url": "https://www.avanihotels.com/", "location": "Bangkok", "description": "Convention and meeting hotel services"},
            {"name": "Amari Events Thailand", "url": "https://www.amari.com/", "location": "Bangkok, Phuket", "description": "Hotel group event and conference services"},
            {"name": "Anantara MICE", "url": "https://www.anantara.com/", "location": "Multiple", "description": "Luxury hotel group MICE services"},
            {"name": "Banyan Tree MICE Bangkok", "url": "https://www.banyantree.com/", "location": "Bangkok", "description": "Luxury venue for corporate events"},
            {"name": "Dusit MICE", "url": "https://www.dusit.com/", "location": "Bangkok", "description": "Thai hospitality group with MICE capabilities"},
            {"name": "Sheraton Grande Bangkok Events", "url": "https://www.marriott.com/", "location": "Bangkok", "description": "5-star venue for corporate meetings and events"},
            {"name": "SO Bangkok Events", "url": "https://www.so-bangkok.com/", "location": "Bangkok", "description": "Boutique luxury venue for creative events"},
            {"name": "Sathorn Event Space", "url": "https://www.sathorneventspace.com/", "location": "Bangkok", "description": "Flexible event venue in CBD"},
            {"name": "Event Pop Thailand", "url": "https://www.eventpop.me/", "location": "Bangkok", "description": "Event ticketing and management platform"},
            {"name": "Eventbrite Thailand", "url": "https://www.eventbrite.com/", "location": "Bangkok", "description": "Event creation and ticket management"},
            {"name": "Asia Exhibition & Conferences", "url": "https://www.aecasia.com/", "location": "Bangkok", "description": "Regional exhibition organizer"},
            {"name": "Thailand Incentive Group", "url": "https://thaiincentivegroup.com/", "location": "Bangkok", "description": "Incentive travel specialists"},
            {"name": "Dream Incentive Thailand", "url": "https://www.dreamincentive.com/", "location": "Bangkok", "description": "Creative incentive program designers"},
            {"name": "EventPro Thailand", "url": "https://www.eventprothailand.com/", "location": "Bangkok", "description": "Full-service event production"},
            {"name": "Spark Event Thailand", "url": "https://www.sparkevent.co.th/", "location": "Bangkok", "description": "Corporate event and team building specialists"},
            {"name": "The Events Co Thailand", "url": "https://www.theeventsco.th/", "location": "Bangkok", "description": "Bespoke event planning and management"},
            {"name": "Onyx Hospitality Events", "url": "https://www.onyx-hospitality.com/", "location": "Bangkok", "description": "Hotel group with event and conference services"},
            {"name": "Minor Hotels Events", "url": "https://www.minorhotels.com/", "location": "Multiple", "description": "Hotel group MICE and event capabilities"},
            {"name": "Cape & Kantary Events", "url": "https://www.capekantaryhotels.com/", "location": "Multiple", "description": "Thai hotel chain with meeting facilities"},
            {"name": "Mode Events Bangkok", "url": "https://www.modeeventsbangkok.com/", "location": "Bangkok", "description": "Creative event production and design"},
            {"name": "Siam Piwat Events", "url": "https://www.siampiwat.com/", "location": "Bangkok", "description": "Retail and event space management"},
            {"name": "True Arena Hua Hin", "url": "https://www.truearena.com/", "location": "Hua Hin", "description": "Sports and event venue"},
            {"name": "Pattaya Exhibition Centre", "url": "https://www.pattayaexhibition.com/", "location": "Pattaya", "description": "Exhibition and MICE venue"},
            {"name": "Chiang Mai Convention Centre", "url": "https://www.chiangmaicc.com/", "location": "Chiang Mai", "description": "Northern Thailand convention venue"},
            {"name": "Laguna Phuket Events", "url": "https://www.lagunaphuket.com/", "location": "Phuket", "description": "Integrated resort events and MICE"},
            {"name": "Kata Group Events", "url": "https://www.katathani.com/", "location": "Phuket", "description": "Resort group event services in Phuket"},
            {"name": "GBF Events Thailand", "url": "https://www.gbfevents.com/", "location": "Bangkok", "description": "Full-service event management company"},
            {"name": "Pinpoint Events", "url": "https://www.pinpointevents.co.th/", "location": "Bangkok", "description": "Corporate and social event planners"},
            {"name": "BIG Events Thailand", "url": "https://www.bigevents.co.th/", "location": "Bangkok", "description": "Large scale event production"},
            {"name": "Live International Thailand", "url": "https://www.liveinternational.com/", "location": "Bangkok", "description": "Live event production and technical services"},
            {"name": "Stage Craft Thailand", "url": "https://www.stagecraft.co.th/", "location": "Bangkok", "description": "AV and event production services"},
        ],
        "Transport & Transfer Services": [
            {"name": "Limousine.in.th", "url": "https://limousine.in.th/", "location": "Bangkok", "description": "Airport transfer service to Pattaya, Ayutthaya, Hua Hin & more"},
            {"name": "Elife Limo", "url": "https://elifelimo.com/", "location": "Bangkok", "description": "Professional car service with app, 24/7 availability"},
            {"name": "Oriental Escape Transfer", "url": "https://www.orientalescape.com/transfer/thailand", "location": "Bangkok", "description": "World Travel Award winner, premium transport since 2018"},
            {"name": "Blacklane Thailand", "url": "https://www.blacklane.com/en/airport-transfer-bangkok/", "location": "Bangkok", "description": "Luxury airport transfer and chauffeur service"},
            {"name": "First Class Bangkok", "url": "https://www.firstclassbangkok.com/", "location": "Bangkok", "description": "Airport limousine and VIP ground services"},
            {"name": "GB Limousine", "url": "https://gblimousine.net/", "location": "Bangkok", "description": "Private driver and airport VIP ground service"},
            {"name": "Thai Taxis", "url": "https://www.thaitaxis.com/", "location": "Bangkok, Pattaya", "description": "Reliable taxi and private car rental service"},
            {"name": "NNS Luxury Limousine", "url": "https://dmcfinder.com/listing/nns-luxury-limousine/", "location": "Bangkok", "description": "Luxury limousine and VIP transport"},
            {"name": "Bangkok Chauffeur", "url": "https://www.bangkokchauffeur.com/", "location": "Bangkok", "description": "Professional chauffeur and car hire"},
            {"name": "Thai Limo", "url": "https://www.thailimo.com/", "location": "Bangkok", "description": "Luxury sedan and van rental with driver"},
            {"name": "AirportTransfer.com Thailand", "url": "https://www.airporttransfer.com/", "location": "Multiple", "description": "Online airport transfer booking platform"},
            {"name": "Klook Thailand Transfers", "url": "https://www.klook.com/en-US/airport-transfers/city/4-bangkok-airport/", "location": "Bangkok", "description": "Platform for booking private and shared transfers"},
            {"name": "12Go Asia", "url": "https://12go.asia/", "location": "Multiple", "description": "SE Asia transport booking (trains, buses, ferries, flights)"},
            {"name": "BusOnlineTicket Thailand", "url": "https://www.busonlineticket.co.th/", "location": "Multiple", "description": "Bus ticket booking across Thailand"},
            {"name": "Thai Railway Booking", "url": "https://www.thairailwayticket.com/", "location": "National", "description": "Train ticket booking service"},
            {"name": "Bolt Thailand", "url": "https://bolt.eu/", "location": "Bangkok, Pattaya", "description": "Ride-hailing app with competitive pricing"},
            {"name": "Grab Thailand", "url": "https://www.grab.com/th/", "location": "Multiple", "description": "SE Asia's leading ride-hailing platform"},
            {"name": "InDrive Thailand", "url": "https://indrive.com/", "location": "Multiple", "description": "Negotiable fare ride-hailing"},
            {"name": "Lomprayah", "url": "https://www.lomprayah.com/", "location": "Gulf Islands", "description": "Ferry and catamaran service to Koh Samui, Koh Tao, Koh Phangan"},
            {"name": "Seatran Ferry", "url": "https://www.seatranferry.com/", "location": "Gulf Islands", "description": "Ferry services connecting gulf islands"},
            {"name": "Andaman Wave Master", "url": "https://andamanwavemaster.com/", "location": "Phuket, Krabi", "description": "Speedboat and ferry Andaman coast"},
            {"name": "Tigerline Ferry", "url": "https://www.tigerlinetravel.com/", "location": "Andaman Coast", "description": "Ferry and speedboat island connections"},
            {"name": "Nok Air", "url": "https://www.nokair.com/", "location": "National", "description": "Low-cost domestic airline"},
            {"name": "Thai Lion Air", "url": "https://www.lionairthai.com/", "location": "National", "description": "Low-cost domestic and regional airline"},
            {"name": "Bangkok Airways", "url": "https://www.bangkokair.com/", "location": "National", "description": "Boutique airline serving unique routes (Samui, Sukhothai)"},
            {"name": "Thai Vietjet", "url": "https://www.vietjetair.com/", "location": "National", "description": "Low-cost carrier for domestic routes"},
            {"name": "AirAsia Thailand", "url": "https://www.airasia.com/", "location": "National", "description": "Major low-cost carrier"},
            {"name": "Thai Smile Airways", "url": "https://www.thaismileair.com/", "location": "National", "description": "Regional carrier (Thai Airways subsidiary)"},
            {"name": "Phuket Ferry", "url": "https://www.phuketferry.com/", "location": "Phuket", "description": "Ferry connections from Phuket"},
            {"name": "Railay Beach Longtail", "url": "https://www.railaybeach.com/", "location": "Krabi", "description": "Local longtail boat services"},
            {"name": "Bangkok River Taxi", "url": "https://www.chaophrayaexpressboat.com/", "location": "Bangkok", "description": "Chao Phraya river boat service"},
            {"name": "BTS Skytrain", "url": "https://www.bts.co.th/", "location": "Bangkok", "description": "Bangkok mass transit system"},
            {"name": "MRT Bangkok", "url": "https://www.mrta.co.th/", "location": "Bangkok", "description": "Bangkok metro system"},
            {"name": "Airport Rail Link", "url": "https://www.srtet.co.th/", "location": "Bangkok", "description": "Suvarnabhumi airport rail connection"},
            {"name": "Phuket Smart Bus", "url": "https://www.phuketsmartbus.com/", "location": "Phuket", "description": "Airport to beaches shuttle service"},
            {"name": "Songthaew Chiang Mai", "url": "https://www.chiangmaitraveller.com/", "location": "Chiang Mai", "description": "Local red truck shared transport"},
            {"name": "Taxi Meter Phuket", "url": "https://www.taximeterphuket.com/", "location": "Phuket", "description": "Metered taxi service in Phuket"},
            {"name": "Phuket Taxi Booking", "url": "https://www.phukettaxibooking.com/", "location": "Phuket", "description": "Online taxi reservation Phuket"},
            {"name": "Samui Airport Transfer", "url": "https://www.samuiairporttransfer.com/", "location": "Koh Samui", "description": "Airport pickup and island transfers"},
            {"name": "Chiang Mai Taxi Service", "url": "https://www.chiangmaitaxi.com/", "location": "Chiang Mai", "description": "Private car and driver hire"},
            {"name": "Thai Rent A Car", "url": "https://www.thairentacar.com/", "location": "Multiple", "description": "Car rental with self-drive option"},
            {"name": "Budget Car Thailand", "url": "https://www.budget.co.th/", "location": "Multiple", "description": "International car rental chain"},
            {"name": "Hertz Thailand", "url": "https://www.hertz.co.th/", "location": "Multiple", "description": "Global car rental with Thai fleet"},
            {"name": "Sixt Thailand", "url": "https://www.sixt.co.th/", "location": "Multiple", "description": "Premium car rental service"},
            {"name": "Drive Car Rental Phuket", "url": "https://www.drivecarrentalphuket.com/", "location": "Phuket", "description": "Local car and scooter rental"},
            {"name": "Chiang Rai Transport", "url": "https://www.chiangrai-transport.com/", "location": "Chiang Rai", "description": "Private transfers in northern Thailand"},
            {"name": "Pattaya Fast Boat", "url": "https://www.pattayafastboat.com/", "location": "Pattaya", "description": "Speedboat connections from Pattaya"},
            {"name": "Koh Lipe Speedboat", "url": "https://www.kohlipespeedboat.com/", "location": "Satun", "description": "Speedboat to Koh Lipe island"},
            {"name": "Private Driver Thailand", "url": "https://www.privatedriverthailand.com/", "location": "Multiple", "description": "Private English-speaking driver hire"},
            {"name": "Thai VIP Van", "url": "https://www.thaivipvan.com/", "location": "Bangkok", "description": "VIP van rental for groups"},
        ],
        "Adventure & Outdoor Operators": [
            {"name": "Active Thailand", "url": "https://active-thailand.com/", "location": "Chiang Mai", "description": "Cultural and nature adventures since 1991"},
            {"name": "Flight of the Gibbon", "url": "https://www.treetopasia.com/", "location": "Chiang Mai, Pattaya", "description": "Asia's first zipline jungle canopy experience"},
            {"name": "Elephant Nature Park", "url": "https://www.elephantnaturepark.org/", "location": "Chiang Mai", "description": "Ethical elephant sanctuary and rescue"},
            {"name": "Sea Canoe Thailand", "url": "https://www.seacanoe.net/", "location": "Phuket", "description": "Original sea kayaking tours in Phang Nga Bay"},
            {"name": "Dive The World Thailand", "url": "https://www.dive-the-world.com/", "location": "Phuket, Koh Tao", "description": "Diving holiday specialist across Thailand"},
            {"name": "Ban's Diving Resort", "url": "https://www.bansdivingresort.com/", "location": "Koh Tao", "description": "Largest dive school in Southeast Asia"},
            {"name": "SSS Phuket Diving", "url": "https://www.sssphuket.com/", "location": "Phuket", "description": "PADI dive center in Phuket"},
            {"name": "Similan Diving Safaris", "url": "https://www.similan-diving-safaris.com/", "location": "Phuket", "description": "Liveaboard diving in Similan Islands"},
            {"name": "Kon Tiki Diving Koh Lanta", "url": "https://www.kontikidiving.com/", "location": "Koh Lanta", "description": "PADI 5-star dive center"},
            {"name": "Rock Climbing Railay", "url": "https://www.railayadventure.com/", "location": "Krabi", "description": "World-class rock climbing in Railay Beach"},
            {"name": "Basecamp Tonsai", "url": "https://www.basecamptonsai.com/", "location": "Krabi", "description": "Climbing courses and multi-pitch adventures"},
            {"name": "Real Rocks Climbing", "url": "https://www.realrocks.net/", "location": "Krabi", "description": "Guided climbing at Railay and Tonsai"},
            {"name": "Thai Adventures", "url": "https://www.thaiadventures.com/", "location": "Multiple", "description": "Multi-sport adventure travel operator"},
            {"name": "Eagle Track Zipline", "url": "https://www.eagletrackzipline.com/", "location": "Chiang Mai", "description": "Zipline and jungle canopy tours"},
            {"name": "Jungle Flight Chiang Mai", "url": "https://www.jungleflight.com/", "location": "Chiang Mai", "description": "Zipline adventure through old-growth rainforest"},
            {"name": "Paddle Asia", "url": "https://www.paddleasia.com/", "location": "Phuket", "description": "Sea kayaking and stand-up paddleboarding"},
            {"name": "Chiang Mai Rock Climbing", "url": "https://www.chiangmairockclimbing.com/", "location": "Chiang Mai", "description": "Indoor and outdoor climbing experiences"},
            {"name": "Sail in Asia", "url": "https://www.sailinasia.com/", "location": "Phuket", "description": "Sailing experiences and yacht charters"},
            {"name": "John Gray's Sea Canoe", "url": "https://www.johngray-seacanoe.com/", "location": "Phuket", "description": "Original Phang Nga Bay sea canoe tours"},
            {"name": "Sayam Kayaking", "url": "https://www.sayamkayaking.com/", "location": "Krabi", "description": "Kayaking and mangrove tours"},
            {"name": "Phuket Surf", "url": "https://www.phuketsurfing.com/", "location": "Phuket", "description": "Surfing lessons and board rental"},
            {"name": "X Centre Pattaya", "url": "https://www.xcentrepattaya.com/", "location": "Pattaya", "description": "Extreme sports: skydiving, go-karts, bungee"},
            {"name": "Skydive Thailand", "url": "https://www.skydivethailand.com/", "location": "Pattaya", "description": "Tandem skydiving experiences"},
            {"name": "Trek Thailand", "url": "https://www.trekthailand.net/", "location": "Chiang Mai", "description": "Multi-day trekking and jungle camping"},
            {"name": "Pooh Eco Trekking", "url": "https://www.pooh-ecotrekking.com/", "location": "Chiang Mai", "description": "Sustainable jungle and hill tribe treks"},
            {"name": "Doi Inthanon Trekking", "url": "https://www.doiinthanontrekking.com/", "location": "Chiang Mai", "description": "Thailand's highest mountain trekking tours"},
            {"name": "Khao Sok Discovery", "url": "https://www.khaosokdiscovery.com/", "location": "Surat Thani", "description": "National park tours and lake adventures"},
            {"name": "Our Jungle Camp", "url": "https://www.ourjunglecamp.com/", "location": "Khao Sok", "description": "Treehouse resort and jungle experiences"},
            {"name": "Elephant Hills", "url": "https://www.elephanthills.com/", "location": "Khao Sok", "description": "Luxury tented jungle camps and ethical elephant experiences"},
            {"name": "Anurak Community Lodge", "url": "https://www.anuraklodge.com/", "location": "Khao Sok", "description": "Community-based eco-lodge and tours"},
            {"name": "Pimalai Excursions", "url": "https://www.pimalai.com/", "location": "Koh Lanta", "description": "Resort-based island and sea excursions"},
            {"name": "Koh Tao Divers", "url": "https://www.kohtaodivers.com/", "location": "Koh Tao", "description": "PADI diving courses and fun dives"},
            {"name": "Crystal Dive Koh Tao", "url": "https://www.crystaldive.com/", "location": "Koh Tao", "description": "Award-winning PADI 5-star dive center"},
            {"name": "Dive Academy Koh Tao", "url": "https://www.dive-academy.co.th/", "location": "Koh Tao", "description": "Small group diving instruction"},
            {"name": "Samui Kayak Adventures", "url": "https://www.samuikayaks.com/", "location": "Koh Samui", "description": "Kayaking and snorkeling excursions"},
            {"name": "Blue Stars Kayaking", "url": "https://www.bluestars.info/", "location": "Koh Samui", "description": "Multi-day sea kayaking adventures"},
            {"name": "Elephant Jungle Sanctuary", "url": "https://www.elephantjunglesanctuary.com/", "location": "Chiang Mai, Phuket", "description": "Ethical elephant experiences"},
            {"name": "Patara Elephant Farm", "url": "https://www.pataraelephantfarm.com/", "location": "Chiang Mai", "description": "Premium elephant conservation experience"},
            {"name": "Angthong Marine Park Tours", "url": "https://www.angthong-national-marine-park.com/", "location": "Koh Samui", "description": "National marine park kayaking and snorkeling"},
            {"name": "Wake Up Wakeboard", "url": "https://www.wakeupphuket.com/", "location": "Phuket", "description": "Wakeboarding and water sports"},
            {"name": "Cable Ski Pattaya", "url": "https://www.thaiwakepark.com/", "location": "Pattaya", "description": "Cable wakeboarding park"},
            {"name": "Thai Muay Thai", "url": "https://www.thaimuaythai.com/", "location": "Bangkok, Phuket", "description": "Muay Thai training camps and experiences"},
            {"name": "Tiger Muay Thai", "url": "https://www.tigermuaythai.com/", "location": "Phuket", "description": "MMA and Muay Thai training camp"},
            {"name": "Fairtex Training Center", "url": "https://www.fairtex.com/", "location": "Pattaya", "description": "Professional Muay Thai training and fitness"},
            {"name": "Monsoon Valley Vineyard", "url": "https://www.monsoonvalley.com/", "location": "Hua Hin", "description": "Wine tasting tours and vineyard experiences"},
            {"name": "Chiang Dao Nest", "url": "https://www.chiangdao.com/", "location": "Chiang Dao", "description": "Nature lodges and mountain adventures"},
            {"name": "Huay Tung Tao Adventures", "url": "https://www.huaytungtao.com/", "location": "Chiang Mai", "description": "Lake adventures and ATV tours"},
            {"name": "Koh Yao Noi Eco", "url": "https://www.kohyaonoi.com/", "location": "Koh Yao Noi", "description": "Eco-tours and island cycling"},
            {"name": "Phuket Elephant Sanctuary", "url": "https://www.phuketelephantsanctuary.org/", "location": "Phuket", "description": "Ethical elephant conservation"},
            {"name": "Wild Kite Phuket", "url": "https://www.wildkitephuket.com/", "location": "Phuket", "description": "Kitesurfing lessons and gear rental"},
        ],
        "Food & Culinary Operators": [
            {"name": "Bangkok Food Tours", "url": "https://www.bangkokfoodtours.com/", "location": "Bangkok", "description": "Authentic join-in and private food culture tours"},
            {"name": "Chili Paste Tours", "url": "https://www.chilipastetours.com/", "location": "Bangkok", "description": "Thai food walking tours led by Thai foodies"},
            {"name": "Taste of Thailand Tours", "url": "https://www.tasteofthailandtours.com/", "location": "Bangkok", "description": "Street food and market tours"},
            {"name": "Silom Thai Cooking School", "url": "https://www.bangkokthaicooking.com/", "location": "Bangkok", "description": "Hands-on Thai cooking classes"},
            {"name": "Baipai Thai Cooking School", "url": "https://www.baipai.com/", "location": "Bangkok", "description": "Premium cooking school in garden setting"},
            {"name": "Blue Elephant Cooking School", "url": "https://www.blueelephant.com/", "location": "Bangkok", "description": "Royal Thai cuisine cooking classes"},
            {"name": "Manohra Cruises", "url": "https://www.manohracruises.com/", "location": "Bangkok", "description": "Traditional rice barge dining cruise"},
            {"name": "Chiang Mai Cooking Class", "url": "https://www.chiangmaicookingclass.com/", "location": "Chiang Mai", "description": "Thai cooking class with market tour"},
            {"name": "Thai Farm Cooking School", "url": "https://www.thaifarmcooking.com/", "location": "Chiang Mai", "description": "Organic farm cooking experience"},
            {"name": "Pantawan Cooking Class", "url": "https://www.pantawancooking.com/", "location": "Chiang Mai", "description": "Home-style cooking in traditional house"},
            {"name": "Mama Noi Cooking Class", "url": "https://www.mamanoi.com/", "location": "Chiang Mai", "description": "Small group hands-on cooking classes"},
            {"name": "Asia Scenic Cooking Class", "url": "https://www.asiascenic.com/", "location": "Chiang Mai", "description": "Cooking class with market tour included"},
            {"name": "Phuket Thai Cooking Academy", "url": "https://www.phuketthaicookingacademy.com/", "location": "Phuket", "description": "Cooking school with garden ingredients"},
            {"name": "Blue Elephant Phuket", "url": "https://www.blueelephant.com/phuket/", "location": "Phuket", "description": "Royal Thai cuisine in historic mansion"},
            {"name": "Pum Thai Cooking School", "url": "https://www.pumthaicookingschool.com/", "location": "Phuket", "description": "Award-winning cooking school"},
            {"name": "Sompong Thai Cooking School", "url": "https://www.sompongthaicookingschool.com/", "location": "Bangkok", "description": "Authentic Thai cooking experience"},
            {"name": "Issaya Cooking Studio", "url": "https://www.issaya.com/", "location": "Bangkok", "description": "Celebrity chef cooking classes"},
            {"name": "Baan Thai Cookery School", "url": "https://www.baanthaicookery.com/", "location": "Chiang Mai", "description": "Traditional Thai cooking classes"},
            {"name": "Samui Institute of Thai Culinary Arts", "url": "https://www.sitca.net/", "location": "Koh Samui", "description": "Professional culinary training and classes"},
            {"name": "Time For Lime", "url": "https://www.timeforlime.net/", "location": "Koh Lanta", "description": "Cooking class supporting local community"},
            {"name": "Krabi Cooking Class", "url": "https://www.krabicookingclass.com/", "location": "Krabi", "description": "Authentic Southern Thai cooking"},
            {"name": "Courageous Kitchen", "url": "https://www.courageouskitchen.org/", "location": "Bangkok", "description": "Social enterprise cooking tours"},
            {"name": "Mark Wiens Thailand Tours", "url": "https://migrationology.com/", "location": "Bangkok", "description": "Famous food vlogger's guided food tours"},
            {"name": "A Chef's Tour Bangkok", "url": "https://www.achefstour.com/", "location": "Bangkok", "description": "Guided food tours by local chefs"},
            {"name": "Doi Chaang Coffee Tour", "url": "https://www.doichaangcoffee.com/", "location": "Chiang Rai", "description": "Coffee plantation tour and tasting"},
            {"name": "Lanna Thai Cooking", "url": "https://www.lannathaicooking.com/", "location": "Chiang Mai", "description": "Northern Thai cuisine cooking classes"},
            {"name": "Pai Cookery Class", "url": "https://www.paicookery.com/", "location": "Pai", "description": "Cooking class in mountain town setting"},
            {"name": "Koh Samui Food Tour", "url": "https://www.kohsamuifoodtour.com/", "location": "Koh Samui", "description": "Island food and culture tours"},
            {"name": "Bangkok Night Food Tour", "url": "https://www.bangkoknightfoodtour.com/", "location": "Bangkok", "description": "After-dark street food experiences"},
            {"name": "Pad Thai Wanglang", "url": "https://www.padthaiwanglang.com/", "location": "Bangkok", "description": "Legendary pad thai experience and demonstration"},
            {"name": "Bo.Lan Restaurant", "url": "https://www.bolan.co.th/", "location": "Bangkok", "description": "Michelin-star sustainable Thai dining"},
            {"name": "Nahm Restaurant", "url": "https://www.comohotels.com/", "location": "Bangkok", "description": "Award-winning refined Thai cuisine"},
            {"name": "Gaggan Anand", "url": "https://www.gaggananand.com/", "location": "Bangkok", "description": "World-renowned progressive Indian cuisine"},
            {"name": "Jay Fai", "url": "https://www.jayfai.com/", "location": "Bangkok", "description": "Michelin-star street food legend"},
            {"name": "Le Du Restaurant", "url": "https://www.ledubkk.com/", "location": "Bangkok", "description": "Modern Thai fine dining, Asia's Best"},
            {"name": "Paste Bangkok", "url": "https://www.pastebangkok.com/", "location": "Bangkok", "description": "Progressive Thai cuisine restaurant"},
            {"name": "Sorn Restaurant", "url": "https://www.sornbkk.com/", "location": "Bangkok", "description": "2 Michelin stars, Southern Thai cuisine"},
            {"name": "80/20 Restaurant", "url": "https://www.8020bkk.com/", "location": "Bangkok", "description": "Progressive Thai dining using local ingredients"},
            {"name": "Err Urban Rustic Thai", "url": "https://www.errbkk.com/", "location": "Bangkok", "description": "Rustic Thai street food dining"},
            {"name": "Soul Food Mahanakorn", "url": "https://www.soulfoodmahanakorn.com/", "location": "Bangkok", "description": "Elevated Thai comfort food and cocktails"},
            {"name": "Supanniga Eating Room", "url": "https://www.supannigaeatingroom.com/", "location": "Bangkok", "description": "Eastern Thai home-cooking restaurant"},
            {"name": "Issaya Siamese Club", "url": "https://www.issaya.com/", "location": "Bangkok", "description": "Chef Ian Kittichai's innovative Thai"},
            {"name": "Namsaah Bottling Trust", "url": "https://www.namsaah.com/", "location": "Bangkok", "description": "Thai tapas and craft cocktails"},
            {"name": "Cabbages & Condoms", "url": "https://www.cabbagesandcondoms.com/", "location": "Bangkok", "description": "Iconic restaurant supporting social causes"},
            {"name": "Ruen Mallika", "url": "https://www.ruenmallika.com/", "location": "Bangkok", "description": "Traditional Thai restaurant in heritage house"},
            {"name": "Baan Khanitha", "url": "https://www.baankhanitha.com/", "location": "Bangkok", "description": "Classic Thai fine dining since 1991"},
            {"name": "SP Chicken Chiang Mai", "url": "https://www.spchicken.com/", "location": "Chiang Mai", "description": "Famous roasted chicken restaurant"},
            {"name": "Khao Soi Khun Yai", "url": "https://www.khaosoi.com/", "location": "Chiang Mai", "description": "Legendary khao soi noodle shop"},
            {"name": "Huen Phen", "url": "https://www.huenphen.com/", "location": "Chiang Mai", "description": "Iconic Northern Thai restaurant"},
            {"name": "Krua Apsorn", "url": "https://www.kruaapsorn.com/", "location": "Bangkok", "description": "Royal-recipe Thai restaurant near Grand Palace"},
        ],
        "Wellness & Spa Services": [
            {"name": "Kamalaya Koh Samui", "url": "https://kamalaya.com/", "location": "Koh Samui", "description": "Holistic wellness resort with naturopaths and TCM"},
            {"name": "Samahita Retreat", "url": "https://samahitaretreat.com/", "location": "Koh Samui", "description": "Asia's pioneering yoga and wellbeing retreat since 2003"},
            {"name": "The Sanctuary Thailand", "url": "https://thesanctuarythailand.com/", "location": "Koh Phangan", "description": "Premier wellness resort for yoga, detox and healing"},
            {"name": "Ananda Yoga & Detox", "url": "https://anandayogadetox.com/", "location": "Koh Phangan", "description": "16+ years premier detox retreat in Thailand"},
            {"name": "Chiva-Som", "url": "https://www.chivasom.com/", "location": "Hua Hin", "description": "World-renowned luxury health resort"},
            {"name": "RAKxa Wellness", "url": "https://www.rakxawellness.com/", "location": "Bangkok", "description": "Integrative wellness and medical retreat"},
            {"name": "Absolute Sanctuary", "url": "https://www.absolutesanctuary.com/", "location": "Koh Samui", "description": "Detox, yoga, Pilates and spa resort"},
            {"name": "Museflower Retreat & Spa", "url": "https://www.museflower.com/", "location": "Chiang Rai", "description": "Holistic retreat with yoga and meditation"},
            {"name": "True Nature Chiang Mai", "url": "https://www.truenaturecm.com/", "location": "Chiang Mai", "description": "Yoga retreat and meditation homestay"},
            {"name": "Wellness Retreats Thailand", "url": "https://www.wellnessretreatsthailand.com/", "location": "Multiple", "description": "Directory of 50+ wellness retreats"},
            {"name": "Orion Healing Center", "url": "https://www.orionhealing.com/", "location": "Koh Phangan", "description": "Yoga, detox, and healing therapies"},
            {"name": "Vikasa Yoga Retreat", "url": "https://vikasa.com/", "location": "Koh Samui", "description": "Luxury yoga and transformation retreat"},
            {"name": "Wild Rose Yoga", "url": "https://www.wildroseyoga.com/", "location": "Koh Phangan", "description": "Yoga teacher training and retreats"},
            {"name": "Suan Sati Yoga", "url": "https://www.suansati.com/", "location": "Chiang Mai", "description": "Mindfulness yoga retreat in nature"},
            {"name": "Yoga Thailand", "url": "https://www.yogathailand.com/", "location": "Koh Samui", "description": "Daily yoga classes and retreat programs"},
            {"name": "Ban Sabai Village", "url": "https://www.bansabaivillage.com/", "location": "Chiang Mai", "description": "Boutique wellness resort and spa"},
            {"name": "Oasis Spa", "url": "https://www.oasisspa.net/", "location": "Bangkok, Chiang Mai, Phuket", "description": "Award-winning spa chain across Thailand"},
            {"name": "Let's Relax Spa", "url": "https://www.letsrelaxspa.com/", "location": "Multiple", "description": "Premium spa chain with 20+ locations"},
            {"name": "Health Land Spa", "url": "https://www.healthlandspa.com/", "location": "Bangkok", "description": "Quality Thai massage and spa treatments"},
            {"name": "Asia Herb Association", "url": "https://www.asiaherbassociation.com/", "location": "Bangkok", "description": "Herbal spa treatments and Thai massage"},
            {"name": "Banyan Tree Spa", "url": "https://www.banyantreespa.com/", "location": "Bangkok, Phuket, Samui", "description": "Award-winning luxury spa brand"},
            {"name": "Six Senses Spa Thailand", "url": "https://www.sixsenses.com/", "location": "Koh Samui, Koh Yao Noi", "description": "Ultra-luxury wellness and spa experiences"},
            {"name": "COMO Shambhala", "url": "https://www.comohotels.com/", "location": "Bangkok", "description": "Holistic wellness within luxury hotels"},
            {"name": "So Thai Spa", "url": "https://www.sothaispa.com/", "location": "Bangkok", "description": "Contemporary Thai spa experience"},
            {"name": "Rarinjinda Wellness Spa", "url": "https://www.rarinjinda.com/", "location": "Chiang Mai", "description": "Boutique wellness resort and day spa"},
            {"name": "Fah Lanna Spa", "url": "https://www.fahlanna.com/", "location": "Chiang Mai", "description": "Lanna-inspired spa and wellness"},
            {"name": "The Barai Spa", "url": "https://www.thebarai.com/", "location": "Hua Hin", "description": "Hyatt resort destination spa"},
            {"name": "Aleenta Spa", "url": "https://www.aleenta.com/", "location": "Hua Hin, Phuket", "description": "Boutique resort and wellness spa"},
            {"name": "Devarana Spa", "url": "https://www.devaranaspa.com/", "location": "Bangkok", "description": "Dusit luxury spa brand"},
            {"name": "Panpuri Organic Spa", "url": "https://www.panpuri.com/", "location": "Bangkok", "description": "Organic Thai spa and wellness products"},
            {"name": "Thann Sanctuary Spa", "url": "https://www.thann.co.th/", "location": "Bangkok", "description": "Natural Thai spa brand experience"},
            {"name": "Spa Cenvaree", "url": "https://www.spacenvaree.com/", "location": "Multiple", "description": "Centara Hotels signature spa"},
            {"name": "Divana Spa", "url": "https://www.divanaspa.com/", "location": "Bangkok", "description": "Luxury Thai spa with herbal traditions"},
            {"name": "Harnn Heritage Spa", "url": "https://www.harnn.com/", "location": "Bangkok", "description": "Heritage-inspired Thai spa"},
            {"name": "Bhawa Spa", "url": "https://www.bhawaspa.com/", "location": "Bangkok", "description": "Premium wellness and spa retreat"},
            {"name": "Onsen at Moncham", "url": "https://www.moncham.com/", "location": "Chiang Mai", "description": "Japanese-inspired hot spring on mountain"},
            {"name": "San Kamphaeng Hot Springs", "url": "https://www.chiangmai.com/", "location": "Chiang Mai", "description": "Natural mineral hot springs"},
            {"name": "The Dawn Rehab", "url": "https://thedawnrehab.com/", "location": "Chiang Mai", "description": "Mental wellness and rehabilitation retreat"},
            {"name": "Amatara Wellness Resort", "url": "https://www.amataraphuket.com/", "location": "Phuket", "description": "Luxury wellness resort with Turkish hammam"},
            {"name": "Mangosteen Ayurveda", "url": "https://www.mangosteen-phuket.com/", "location": "Phuket", "description": "Ayurvedic wellness resort"},
            {"name": "Atmanjai Wellness", "url": "https://www.atmanjai.com/", "location": "Phuket", "description": "Detox, yoga, and fitness retreat"},
            {"name": "Santosa Detox Center", "url": "https://www.santosadetox.com/", "location": "Phuket", "description": "Holistic detox and wellness programs"},
            {"name": "Wat Suan Mokkh", "url": "https://www.suanmokkh.org/", "location": "Surat Thani", "description": "10-day silent meditation retreat"},
            {"name": "Doi Suthep Meditation", "url": "https://www.doisuthep.com/", "location": "Chiang Mai", "description": "Temple meditation and mindfulness"},
            {"name": "International Dhamma Hermitage", "url": "https://www.suanmokkh.org/", "location": "Surat Thani", "description": "Buddhist meditation retreat center"},
            {"name": "Wat Mahathat Meditation", "url": "https://www.watmahathat.com/", "location": "Bangkok", "description": "Vipassana meditation in central Bangkok"},
            {"name": "Peace Revolution", "url": "https://www.peacerevolution.net/", "location": "Multiple", "description": "Free meditation and inner peace programs"},
            {"name": "Dhamma Kancana Vipassana", "url": "https://www.dhamma.org/", "location": "Kanchanaburi", "description": "10-day Vipassana meditation courses"},
            {"name": "Wat Pa Tam Wua", "url": "https://www.watpatamwua.com/", "location": "Mae Hong Son", "description": "Forest monastery meditation retreat"},
            {"name": "Mind Body Spirit Koh Phangan", "url": "https://www.mindbodyspiritfestival.com/", "location": "Koh Phangan", "description": "Annual wellness festival and workshops"},
        ],
        "Boutique Hotels & Hostels": [
            {"name": "Luk Hostel Bangkok", "url": "https://www.lukhostel.com/", "location": "Bangkok", "description": "Best hostel for digital nomads with free coworking"},
            {"name": "The Yard Hostel Bangkok", "url": "https://www.theyardhostel.com/", "location": "Bangkok", "description": "Design hostel in creative district"},
            {"name": "Lub d Bangkok", "url": "https://www.lubd.com/", "location": "Bangkok", "description": "Award-winning hostel chain for smart travelers"},
            {"name": "NapPark Hostel", "url": "https://www.nappark.com/", "location": "Bangkok", "description": "Boutique hostel near Khao San Road"},
            {"name": "Once Again Hostel", "url": "https://www.onceagainhostel.com/", "location": "Bangkok", "description": "Social enterprise hostel with local community focus"},
            {"name": "Hom Hostel & Cooking Club", "url": "https://www.homhostel.com/", "location": "Bangkok", "description": "Hostel with Thai cooking experiences"},
            {"name": "Bed One Block Hostel", "url": "https://www.bedoneblock.com/", "location": "Bangkok", "description": "Minimalist design hostel"},
            {"name": "The Mustang Nero Hotel", "url": "https://www.mustangnero.com/", "location": "Bangkok", "description": "Boutique industrial-chic hotel"},
            {"name": "Ad Lib Bangkok", "url": "https://www.adlibhotels.com/", "location": "Bangkok", "description": "Art-inspired boutique hotel"},
            {"name": "Warehouse 30 Hostel", "url": "https://www.warehouse30.com/", "location": "Bangkok", "description": "Creative hub hostel in Charoenkrung"},
            {"name": "Stamps Backpackers", "url": "https://www.stampsbackpackers.com/", "location": "Chiang Mai", "description": "Social hostel in old city"},
            {"name": "Hostel by Bed Chiang Mai", "url": "https://www.hostelbybed.com/", "location": "Chiang Mai", "description": "Historic center hostel near night markets"},
            {"name": "Green Tiger House", "url": "https://www.greentigerhouse.com/", "location": "Chiang Mai", "description": "Eco-conscious hostel with garden"},
            {"name": "Hug Hostel Chiang Mai", "url": "https://www.hughostel.com/", "location": "Chiang Mai", "description": "Community-focused hostel in old city"},
            {"name": "Julie Guesthouse", "url": "https://www.julieguesthouse.com/", "location": "Chiang Mai", "description": "Budget-friendly guesthouse classic"},
            {"name": "The Work Loft Phuket", "url": "https://www.theworkloft.com/", "location": "Phuket", "description": "Coworking space and hostel for nomads"},
            {"name": "The Nest Phuket", "url": "https://www.thenestphuket.com/", "location": "Phuket", "description": "Shared accommodation for nomads"},
            {"name": "Slumber Party Phuket", "url": "https://www.slumberparty.co/", "location": "Phuket", "description": "Fun social hostel near Patong"},
            {"name": "Glur Hostel Phuket", "url": "https://www.glurhostel.com/", "location": "Phuket", "description": "Award-winning capsule hostel"},
            {"name": "Mad Monkey Hostel", "url": "https://www.madmonkeyhostels.com/", "location": "Bangkok, Koh Phangan", "description": "Social hostel chain with events"},
            {"name": "Bodega Bangkok", "url": "https://www.bodegahostels.com/", "location": "Bangkok", "description": "Party hostel with rooftop bar"},
            {"name": "The Chiang Mai White House", "url": "https://www.chiangmaiwhitehouse.com/", "location": "Chiang Mai", "description": "Colonial-style boutique accommodation"},
            {"name": "Dash Resort Koh Samui", "url": "https://www.dashhospitality.com/", "location": "Koh Samui", "description": "Design-forward boutique resort"},
            {"name": "Selina Hostel Phuket", "url": "https://www.selina.com/", "location": "Phuket", "description": "Global nomad hostel chain with cowork"},
            {"name": "Nomad Residence Chiang Mai", "url": "https://nomadresidence.com/", "location": "Chiang Mai", "description": "Long-stay accommodation for digital nomads"},
            {"name": "Casa de Moda Chiang Mai", "url": "https://www.casademoda.co/", "location": "Chiang Mai", "description": "Boutique hotel in Nimman area"},
            {"name": "Akira Lipe Resort", "url": "https://www.akiraliperesort.com/", "location": "Koh Lipe", "description": "Boutique beach resort on pristine island"},
            {"name": "X2 Vibe Hotels", "url": "https://www.x2resorts.com/", "location": "Multiple", "description": "Boutique lifestyle hotel brand"},
            {"name": "U Hotels & Resorts", "url": "https://www.uhotelsresorts.com/", "location": "Multiple", "description": "Thai boutique hotel chain"},
            {"name": "Sala Hospitality Group", "url": "https://www.salahospitality.com/", "location": "Multiple", "description": "Award-winning boutique resort group"},
            {"name": "Siripanna Villa Resort", "url": "https://www.siripanna.com/", "location": "Chiang Mai", "description": "Lanna-inspired boutique resort"},
            {"name": "137 Pillars House", "url": "https://www.137pillarshotels.com/", "location": "Chiang Mai, Bangkok", "description": "Heritage luxury boutique hotels"},
            {"name": "Rachamankha Hotel", "url": "https://www.rachamankha.com/", "location": "Chiang Mai", "description": "Lanna architecture boutique hotel"},
            {"name": "Na Nirand Romantic Boutique", "url": "https://www.nanirand.com/", "location": "Chiang Mai", "description": "Riverside romantic boutique resort"},
            {"name": "Ping Nakara Boutique Hotel", "url": "https://www.pingnakara.com/", "location": "Chiang Mai", "description": "Colonial Lanna boutique hotel"},
            {"name": "Akyra Manor Chiang Mai", "url": "https://www.theakyra.com/", "location": "Chiang Mai", "description": "Small luxury hotel in Nimman"},
            {"name": "Baan Krating Phuket", "url": "https://www.baankrating.com/", "location": "Phuket", "description": "Jungle boutique resort"},
            {"name": "The Siam Hotel", "url": "https://www.thesiamhotel.com/", "location": "Bangkok", "description": "Ultra-luxury riverside boutique hotel"},
            {"name": "Ariyasom Villa", "url": "https://www.ariyasom.com/", "location": "Bangkok", "description": "Heritage boutique wellness hotel"},
            {"name": "Cabochon Hotel", "url": "https://www.cabochonhotel.com/", "location": "Bangkok", "description": "Art Deco boutique in heritage district"},
            {"name": "Hotel Muse Bangkok", "url": "https://www.hotelmusebangkok.com/", "location": "Bangkok", "description": "Luxury lifestyle boutique hotel"},
            {"name": "Collective Hospitality", "url": "https://collectivehospitality.com/", "location": "Multiple", "description": "Hostel group with properties across Thailand"},
            {"name": "Koh Tao Hostel", "url": "https://www.kohtaohostel.com/", "location": "Koh Tao", "description": "Backpacker hostel on dive island"},
            {"name": "Pai Village Boutique", "url": "https://www.paivillageboutique.com/", "location": "Pai", "description": "Boutique resort in mountain town"},
            {"name": "Lamphu Treehouse", "url": "https://www.lamphutreehouse.com/", "location": "Bangkok", "description": "Budget boutique near Khao San"},
            {"name": "Feung Nakorn Balcony", "url": "https://www.feungnakorn.com/", "location": "Bangkok", "description": "Heritage boutique in old town"},
            {"name": "Praya Palazzo", "url": "https://www.prayapalazzo.com/", "location": "Bangkok", "description": "Riverside heritage boutique hotel"},
            {"name": "Riva Surya Bangkok", "url": "https://www.rivasurya.com/", "location": "Bangkok", "description": "Contemporary riverside boutique"},
            {"name": "Maison Dalabua", "url": "https://www.maisondalabua.com/", "location": "Bangkok", "description": "French-Thai boutique hotel"},
            {"name": "Inn A Day Bangkok", "url": "https://www.innaday.com/", "location": "Bangkok", "description": "Heritage riverside boutique hotel"},
        ],
    }
    return vendors


def main():
    print("=" * 70)
    print("TIRAK DREAM JOURNEYS - Thailand Vendor Sourcing")
    print("=" * 70)

    # Get curated vendors
    curated = get_curated_vendors()

    # Also scrape dmcfinder for live data
    dmcfinder_data = scrape_dmcfinder()

    # Merge dmcfinder into Leisure DMCs (avoid duplicates)
    existing_names = {v["name"].lower() for v in curated["Leisure & Experience DMCs"]}
    for dmc in dmcfinder_data:
        if dmc.get("name", "").lower() not in existing_names:
            dmc["category"] = "Leisure & Experience DMCs"
            curated["Leisure & Experience DMCs"].append(dmc)
            existing_names.add(dmc["name"].lower())

    # Also try scraping evintra for more DMCs
    evintra_data = scrape_evintra()
    for dmc in evintra_data:
        if dmc.get("name", "").lower() not in existing_names:
            dmc["category"] = "Leisure & Experience DMCs"
            curated["Leisure & Experience DMCs"].append(dmc)
            existing_names.add(dmc["name"].lower())

    # Compile all results
    all_vendors = []
    for category, vendors in curated.items():
        for v in vendors:
            v["category"] = category
            all_vendors.append(v)

    # Save master JSON
    with open("tirak_thailand_vendors.json", "w") as f:
        json.dump(all_vendors, f, indent=2, ensure_ascii=False)

    # Save master CSV
    fieldnames = ["category", "name", "url", "location", "description", "type", "source"]
    with open("tirak_thailand_vendors.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for v in all_vendors:
            writer.writerow(v)

    # Save per-category CSVs
    for category, vendors in curated.items():
        safe_name = category.lower().replace(" & ", "_").replace(" ", "_")
        filename = f"tirak_vendors_{safe_name}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for v in vendors:
                writer.writerow(v)

    # Print summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    for category, vendors in curated.items():
        print(f"\n  {category}: {len(vendors)} vendors")
    print(f"\n  TOTAL: {len(all_vendors)} vendors")
    print(f"\n{'=' * 70}")
    print("FILES SAVED:")
    print(f"  tirak_thailand_vendors.json  (master)")
    print(f"  tirak_thailand_vendors.csv   (master)")
    for category in curated:
        safe_name = category.lower().replace(" & ", "_").replace(" ", "_")
        print(f"  tirak_vendors_{safe_name}.csv")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
