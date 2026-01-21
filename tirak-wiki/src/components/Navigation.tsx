import React, { useState } from 'react';
import { Menu, X, Home, Book, Users, Megaphone, FolderOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const navItems = [
  { name: 'Introduction', href: '/docs/01-introduction/welcome', icon: Home },
  { name: 'Foundation', href: '/docs/02-foundation/positioning', icon: Book },
  { name: 'Audiences', href: '/docs/03-audience/companion-persona', icon: Users },
  { name: 'Campaigns', href: '/docs/04-campaign/pre-launch-ads', icon: Megaphone },
  { name: 'Resources', href: '/docs/05-resources/faq', icon: FolderOpen },
];

export const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-4 py-3 border-b border-white/10 bg-[#0f0f13]/80 backdrop-blur-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <a href="/" className="flex items-center gap-2 group">
           {/* Tirak Logo Placeholder */}
           <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#F5A6BF] to-[#9B8FD9] group-hover:scale-110 transition-transform duration-300" />
           <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#F5A6BF] to-[#9B8FD9]">
             Tirak
           </span>
        </a>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-6">
          {navItems.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="text-gray-300 hover:text-white transition-colors text-sm font-medium flex items-center gap-2 group"
            >
              <item.icon size={16} className="group-hover:text-[#F5A6BF] transition-colors" />
              {item.name}
            </a>
          ))}
        </div>

        {/* Mobile Toggle */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden p-2 text-gray-300 hover:text-white"
          aria-label="Toggle menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden overflow-hidden bg-[#0f0f13] border-b border-white/10"
          >
            <div className="px-4 py-6 space-y-4">
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="block text-gray-300 hover:text-[#F5A6BF] text-lg font-medium flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  <item.icon size={20} className="text-[#9B8FD9]" />
                  {item.name}
                </a>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};
