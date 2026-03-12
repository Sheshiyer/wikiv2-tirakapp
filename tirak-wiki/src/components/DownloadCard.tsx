import React from 'react';
import { motion } from 'framer-motion';
import { FileDown } from 'lucide-react';
import { cn } from '../lib/utils';

interface DownloadCardProps {
  title: string;
  description: string;
  fileName: string;
  fileSize: string;
  href: string;
  icon?: React.ReactNode;
  className?: string;
}

export const DownloadCard = ({
  title,
  description,
  fileName,
  fileSize,
  href,
  icon,
  className,
}: DownloadCardProps) => {
  return (
    <motion.div
      className={cn(
        'p-6 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 shadow-lg',
        className
      )}
      whileHover={{ scale: 1.02, y: -2 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex items-start gap-4">
        <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-[#F5A6BF]/20 to-[#9B8FD9]/20 flex items-center justify-center flex-shrink-0">
          {icon || <FileDown className="text-[#F5A6BF]" size={24} />}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-bold text-white mb-1">{title}</h3>
          <p className="text-gray-400 text-sm mb-3">{description}</p>
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">{fileName} · {fileSize}</span>
            <a
              href={href}
              download
              aria-label={`Download ${title} (${fileName}, ${fileSize})`}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-[#F5A6BF] to-[#9B8FD9] text-white text-sm font-semibold hover:opacity-90 transition-opacity"
            >
              <FileDown size={14} aria-hidden="true" />
              Download
            </a>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
