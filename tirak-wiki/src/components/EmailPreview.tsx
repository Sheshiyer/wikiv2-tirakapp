import React from 'react';
import { GlassCard } from './GlassCard';
import { cn } from '../lib/utils';
import { Mail, Paperclip, Clock, MoreHorizontal } from 'lucide-react';

interface EmailPreviewProps {
  subject: string;
  from: string;
  to: string;
  previewText?: string;
  children: React.ReactNode;
}

export const EmailPreview = ({ subject, from, to, previewText, children }: EmailPreviewProps) => {
  return (
    <div className="max-w-3xl mx-auto my-8 font-sans">
      <GlassCard className="p-0 overflow-hidden border-0">
        {/* Header (Mac Mail Style) */}
        <div className="bg-gray-100 dark:bg-gray-800/50 border-b border-gray-200 dark:border-white/10 p-4">
          <div className="flex items-start justify-between mb-4">
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-400" />
              <div className="w-3 h-3 rounded-full bg-yellow-400" />
              <div className="w-3 h-3 rounded-full bg-green-400" />
            </div>
            <div className="text-gray-400">
              <Clock size={16} />
            </div>
          </div>
          
          <div className="space-y-1 text-sm">
            <div className="flex gap-2">
              <span className="text-gray-500 w-12 text-right">From:</span>
              <span className="font-medium text-gray-900 dark:text-white">{from}</span>
            </div>
            <div className="flex gap-2">
              <span className="text-gray-500 w-12 text-right">To:</span>
              <span className="text-gray-700 dark:text-gray-300">{to}</span>
            </div>
            <div className="flex gap-2 mt-2 pt-2 border-t border-gray-200 dark:border-white/5">
              <span className="text-gray-500 w-12 text-right">Subj:</span>
              <span className="font-bold text-gray-900 dark:text-white">{subject}</span>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="p-8 bg-white dark:bg-gray-900/50 min-h-[300px]">
          <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
            {children}
          </div>
          
          {/* Footer Signature Mockup */}
          <div className="mt-8 pt-8 border-t border-gray-200 dark:border-white/10 flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-tirak-pink to-tirak-purple flex items-center justify-center text-white font-bold text-xs">
              T
            </div>
            <div className="text-xs text-gray-500">
              <p className="font-bold text-gray-900 dark:text-white">Tirak Team</p>
              <p>Community Manager</p>
              <p className="text-tirak-pink">tirak.co.th</p>
            </div>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
