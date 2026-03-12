import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

interface OnboardingStepProps {
  stepNumber: number;
  title: string;
  description: string;
  icon?: React.ReactNode;
  isLast?: boolean;
  className?: string;
}

export const OnboardingStep = ({
  stepNumber,
  title,
  description,
  icon,
  isLast = false,
  className,
}: OnboardingStepProps) => {
  return (
    <motion.div
      className={cn('flex gap-4', className)}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: stepNumber * 0.1 }}
    >
      {/* Timeline */}
      <div className="flex flex-col items-center">
        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-[#F5A6BF] to-[#9B8FD9] flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
          {icon || stepNumber}
        </div>
        {!isLast && (
          <div className="w-px flex-1 bg-gradient-to-b from-[#9B8FD9]/50 to-transparent min-h-[40px]" />
        )}
      </div>

      {/* Content */}
      <div className="pb-8">
        <h3 className="text-lg font-bold text-white mb-1">{title}</h3>
        <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
};
