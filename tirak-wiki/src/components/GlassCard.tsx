import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
}

export const GlassCard = ({ children, className, hoverEffect = true }: GlassCardProps) => {
  return (
    <motion.div
      className={cn(
        "glass-card p-6 rounded-xl transition-all duration-300",
        "bg-white/10 backdrop-blur-md border border-white/20 shadow-lg",
        className
      )}
      whileHover={hoverEffect ? { scale: 1.02, y: -2 } : undefined}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {children}
    </motion.div>
  );
};
