import React from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, MapPin } from 'lucide-react';
import { cn } from '../lib/utils';

interface VendorDirectoryCardProps {
  name: string;
  category: string;
  location?: string;
  description?: string;
  url?: string;
  className?: string;
}

const categoryColors: Record<string, string> = {
  'Leisure & Experience DMCs': 'from-pink-500/20 to-purple-500/20 text-pink-300',
  'MICE & Event DMCs': 'from-blue-500/20 to-cyan-500/20 text-blue-300',
  'Transport & Transfer Services': 'from-green-500/20 to-emerald-500/20 text-green-300',
  'Adventure & Outdoor Operators': 'from-orange-500/20 to-amber-500/20 text-orange-300',
  'Food & Culinary Operators': 'from-red-500/20 to-rose-500/20 text-red-300',
  'Wellness & Spa Services': 'from-teal-500/20 to-cyan-500/20 text-teal-300',
  'Boutique Hotels & Hostels': 'from-indigo-500/20 to-violet-500/20 text-indigo-300',
  'Nightlife & Entertainment': 'from-fuchsia-500/20 to-pink-500/20 text-fuchsia-300',
  'Cinema & Entertainment': 'from-yellow-500/20 to-amber-500/20 text-yellow-300',
  'Lifestyle & Experiences': 'from-violet-500/20 to-purple-500/20 text-violet-300',
};

export const VendorDirectoryCard = ({
  name,
  category,
  location,
  description,
  url,
  className,
}: VendorDirectoryCardProps) => {
  const colorClass = categoryColors[category] || 'from-gray-500/20 to-gray-500/20 text-gray-300';

  return (
    <motion.div
      className={cn(
        'p-5 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 shadow-lg',
        className
      )}
      whileHover={{ scale: 1.02, y: -2 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-base font-bold text-white truncate pr-2">{name}</h3>
        {url && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-[#F5A6BF] transition-colors flex-shrink-0"
            aria-label={`Visit ${name} website`}
          >
            <ExternalLink size={16} />
          </a>
        )}
      </div>

      <span className={cn('inline-block px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r mb-3', colorClass)}>
        {category}
      </span>

      {description && (
        <p className="text-gray-400 text-sm mb-3 line-clamp-2">{description}</p>
      )}

      {location && (
        <div className="flex items-center gap-1 text-gray-500 text-xs">
          <MapPin size={12} />
          <span>{location}</span>
        </div>
      )}
    </motion.div>
  );
};
