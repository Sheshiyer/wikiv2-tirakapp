import vendorJson from '../../vendor-pipeline/data/tirak_thailand_vendors.json';

export interface Vendor {
  name: string;
  url?: string;
  location?: string;
  description?: string;
  category: string;
  phone?: string;
  email?: string;
}

const vendors: Vendor[] = vendorJson as Vendor[];

export const VENDOR_CATEGORIES = [
  'Leisure & Experience DMCs',
  'MICE & Event DMCs',
  'Transport & Transfer Services',
  'Adventure & Outdoor Operators',
  'Food & Culinary Operators',
  'Wellness & Spa Services',
  'Boutique Hotels & Hostels',
  'Nightlife & Entertainment',
  'Cinema & Entertainment',
  'Lifestyle & Experiences',
] as const;

export type VendorCategory = (typeof VENDOR_CATEGORIES)[number];

export function getVendorsByCategory(category: string): Vendor[] {
  return vendors.filter((v) => v.category === category);
}

export function getAllVendors(): Vendor[] {
  return vendors;
}

export function getVendorStats() {
  const byCategory = VENDOR_CATEGORIES.map((cat) => ({
    category: cat,
    count: vendors.filter((v) => v.category === cat).length,
  }));

  return {
    total: vendors.length,
    categories: byCategory,
    categoryCount: VENDOR_CATEGORIES.length,
  };
}

export function searchVendors(query: string): Vendor[] {
  const q = query.toLowerCase();
  return vendors.filter(
    (v) =>
      v.name.toLowerCase().includes(q) ||
      v.category.toLowerCase().includes(q) ||
      (v.location && v.location.toLowerCase().includes(q)) ||
      (v.description && v.description.toLowerCase().includes(q))
  );
}
