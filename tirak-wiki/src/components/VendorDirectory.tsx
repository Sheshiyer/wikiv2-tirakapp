import React, { useState, useMemo } from 'react';
import { Search, Filter } from 'lucide-react';
import { VendorDirectoryCard } from './VendorDirectoryCard';
import { cn } from '../lib/utils';

interface Vendor {
  name: string;
  url?: string;
  location?: string;
  description?: string;
  category: string;
  phone?: string;
  email?: string;
}

interface VendorDirectoryProps {
  vendors: Vendor[];
  categories: string[];
}

export const VendorDirectory = ({ vendors, categories }: VendorDirectoryProps) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = useMemo(() => {
    let result = vendors;
    if (selectedCategory !== 'all') {
      result = result.filter((v) => v.category === selectedCategory);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (v) =>
          v.name.toLowerCase().includes(q) ||
          (v.location && v.location.toLowerCase().includes(q)) ||
          (v.description && v.description.toLowerCase().includes(q))
      );
    }
    return result;
  }, [vendors, selectedCategory, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Search and Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <label htmlFor="vendor-search" className="sr-only">Search partners</label>
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
          <input
            id="vendor-search"
            type="text"
            placeholder="Search partners by name, location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search partners"
            className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 text-white placeholder-gray-500 focus:outline-none focus:border-[#F5A6BF]/50 transition-colors"
          />
        </div>
        <div className="relative">
          <label htmlFor="vendor-category-filter" className="sr-only">Filter by category</label>
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
          <select
            id="vendor-category-filter"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            aria-label="Filter by category"
            className="pl-10 pr-8 py-3 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 text-white appearance-none cursor-pointer focus:outline-none focus:border-[#F5A6BF]/50 transition-colors"
          >
            <option value="all" className="bg-[#0f0f13]">All Categories ({vendors.length})</option>
            {categories.map((cat) => {
              const count = vendors.filter((v) => v.category === cat).length;
              return (
                <option key={cat} value={cat} className="bg-[#0f0f13]">
                  {cat} ({count})
                </option>
              );
            })}
          </select>
        </div>
      </div>

      {/* Results Count */}
      <p className="text-gray-400 text-sm">
        Showing <span className="text-white font-semibold">{filtered.length}</span> of{' '}
        <span className="text-white font-semibold">{vendors.length}</span> partners
        {selectedCategory !== 'all' && (
          <span>
            {' '}in <span className="text-[#F5A6BF]">{selectedCategory}</span>
          </span>
        )}
      </p>

      {/* Vendor Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.slice(0, 60).map((vendor, i) => (
          <VendorDirectoryCard
            key={`${vendor.name}-${i}`}
            name={vendor.name}
            category={vendor.category}
            location={vendor.location}
            description={vendor.description}
            url={vendor.url}
          />
        ))}
      </div>

      {filtered.length > 60 && (
        <p className="text-center text-gray-500 text-sm">
          Showing first 60 of {filtered.length} results. Use search or filters to narrow down.
        </p>
      )}

      {filtered.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400">No partners found matching your criteria.</p>
          <button
            onClick={() => { setSearchQuery(''); setSelectedCategory('all'); }}
            className="mt-3 text-[#F5A6BF] hover:underline text-sm"
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
};
