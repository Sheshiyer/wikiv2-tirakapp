import React from 'react';
import { GlassCard } from './GlassCard';
import { cn } from '../lib/utils';
import { Megaphone, ArrowRight, Image as ImageIcon } from 'lucide-react';

interface AdAsset {
  headline: string;
  body: string;
  cta: string;
  format: 'feed' | 'story' | 'carousel';
}

interface AdAssetGridProps {
  assets: AdAsset[];
}

export const AdAssetGrid = ({ assets }: AdAssetGridProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 my-8">
      {assets.map((asset, index) => (
        <GlassCard key={index} className="flex flex-col h-full relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-2 opacity-50">
            {asset.format === 'story' ? <div className="h-8 w-4 border-2 rounded-sm" /> : <div className="h-6 w-8 border-2 rounded-sm" />}
          </div>
          
          <div className="mb-4 flex items-center gap-2 text-tirak-pink font-semibold text-xs uppercase tracking-widest">
            <Megaphone size={14} />
            <span>{asset.format} Ad</span>
          </div>

          {/* Visual Placeholder */}
          <div className="w-full aspect-video bg-gray-100 dark:bg-white/5 rounded-lg mb-4 flex items-center justify-center border border-white/10 group-hover:bg-gray-200 dark:group-hover:bg-white/10 transition-colors">
            <ImageIcon className="text-gray-400" />
          </div>

          <div className="flex-grow space-y-3">
            <h3 className="font-bold text-lg leading-tight text-gray-900 dark:text-white">
              {asset.headline}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-4">
              {asset.body}
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10">
            <button className="w-full py-2 px-4 rounded-lg bg-gradient-to-r from-tirak-pink to-tirak-purple text-white font-medium text-sm flex items-center justify-center gap-2 shadow-lg hover:opacity-90 transition-opacity">
              {asset.cta}
              <ArrowRight size={16} />
            </button>
          </div>
        </GlassCard>
      ))}
    </div>
  );
};
