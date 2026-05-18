import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, X } from 'lucide-react';
import { WikiAssistant } from './WikiAssistant';

type ContactButtonsProps = {
  docSlug: string;
  docTitle: string;
};

export const ContactButtons = ({ docSlug, docTitle }: ContactButtonsProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm" onClick={() => setIsOpen(false)}>
          <div className="absolute inset-0 flex items-center justify-center px-3 py-3 sm:px-6 sm:py-6">
            <div
              className="relative h-full max-h-[min(92vh,980px)] w-full max-w-6xl overflow-hidden rounded-[2rem] border border-white/10 bg-[#0e0d13]/92 shadow-[0_40px_120px_rgba(0,0,0,0.55)]"
              onClick={(event) => event.stopPropagation()}
            >
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="absolute right-4 top-4 z-10 inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-[#17171d]/90 text-gray-300 transition hover:border-white/20 hover:text-white"
                aria-label="Close assistant"
              >
                <X size={18} />
              </button>
              <WikiAssistant docSlug={docSlug} docTitle={docTitle} />
            </div>
          </div>
        </div>
      )}

      <div className="fixed bottom-6 right-6 z-40 flex flex-col gap-3">
        <motion.button
          type="button"
          onClick={() => setIsOpen((open) => !open)}
          className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-[#F5A6BF] to-[#9B8FD9] text-[#0f0f13] shadow-lg transition-transform hover:scale-110"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1 }}
          aria-label={isOpen ? 'Close wiki assistant' : 'Open wiki assistant'}
      >
          <MessageCircle size={24} />
        </motion.button>
      </div>
    </>
  );
};
