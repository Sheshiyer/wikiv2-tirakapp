import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Circle } from 'lucide-react';
import { cn } from '../lib/utils';

interface ChecklistItem {
  id: string;
  label: string;
  description: string;
}

const defaultItems: ChecklistItem[] = [
  { id: 'apply', label: 'Submit partner application', description: 'Fill out the form at tirak.app/partners' },
  { id: 'review', label: 'Application reviewed', description: 'Our team reviews within 24 hours' },
  { id: 'profile', label: 'Create your partner profile', description: 'Add business details, logo, and contact info' },
  { id: 'photos', label: 'Upload experience photos', description: 'High-quality images of your offerings' },
  { id: 'descriptions', label: 'Write experience descriptions', description: 'Compelling descriptions that attract travelers' },
  { id: 'pricing', label: 'Set your pricing', description: 'You have full control over your rates' },
  { id: 'availability', label: 'Configure availability', description: 'Set your calendar and blackout dates' },
  { id: 'live', label: 'Go live!', description: 'Your experiences are now visible to travelers' },
];

interface OnboardingChecklistProps {
  items?: ChecklistItem[];
}

export const OnboardingChecklist = ({ items = defaultItems }: OnboardingChecklistProps) => {
  const [checked, setChecked] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const progress = Math.round((checked.size / items.length) * 100);

  return (
    <div className="space-y-4">
      {/* Progress Bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-2 rounded-full bg-white/10 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-[#F5A6BF] to-[#9B8FD9] rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
        <span className="text-sm text-gray-400 whitespace-nowrap">{checked.size}/{items.length}</span>
      </div>

      {/* Checklist Items */}
      <div className="space-y-2">
        {items.map((item) => {
          const isChecked = checked.has(item.id);
          return (
            <motion.button
              key={item.id}
              onClick={() => toggle(item.id)}
              className={cn(
                'w-full flex items-start gap-3 p-4 rounded-xl border transition-all text-left',
                isChecked
                  ? 'bg-[#F5A6BF]/10 border-[#F5A6BF]/30'
                  : 'bg-white/5 border-white/10 hover:bg-white/10'
              )}
              whileTap={{ scale: 0.98 }}
            >
              <div className={cn(
                'h-6 w-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors',
                isChecked
                  ? 'bg-gradient-to-br from-[#F5A6BF] to-[#9B8FD9]'
                  : 'border-2 border-gray-600'
              )}>
                {isChecked ? <Check size={14} className="text-white" /> : <Circle size={14} className="text-transparent" />}
              </div>
              <div>
                <span className={cn(
                  'font-medium block',
                  isChecked ? 'text-[#F5A6BF] line-through' : 'text-white'
                )}>
                  {item.label}
                </span>
                <span className="text-gray-500 text-sm">{item.description}</span>
              </div>
            </motion.button>
          );
        })}
      </div>

      {progress === 100 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-xl bg-gradient-to-r from-[#F5A6BF]/20 to-[#9B8FD9]/20 border border-[#F5A6BF]/30 text-center"
        >
          <p className="text-[#F5A6BF] font-bold">🎉 You're all set! Welcome to Tirak!</p>
        </motion.div>
      )}
    </div>
  );
};
