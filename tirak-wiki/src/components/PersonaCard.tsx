import React from 'react';
import { GlassCard } from './GlassCard';
import { cn } from '../lib/utils';
import { User, Quote, Star, MapPin, Briefcase } from 'lucide-react';

interface PersonaCardProps {
  name: string;
  role: string;
  age: string | number;
  location: string;
  quote: string;
  traits: string[];
  bio: string;
  type: 'companion' | 'traveler';
  image?: string;
}

export const PersonaCard = ({
  name,
  role,
  age,
  location,
  quote,
  traits,
  bio,
  type,
  image
}: PersonaCardProps) => {
  const isCompanion = type === 'companion';
  const accentColor = isCompanion ? 'text-tirak-pink' : 'text-tirak-purple';
  const bgColor = isCompanion ? 'bg-tirak-pink/10' : 'bg-tirak-purple/10';

  return (
    <GlassCard className="max-w-2xl mx-auto overflow-hidden">
      <div className="flex flex-col md:flex-row gap-6">
        {/* Left Column: Avatar & Quick Stats */}
        <div className="flex-shrink-0 flex flex-col items-center space-y-4">
          <div className={cn("w-32 h-32 rounded-full flex items-center justify-center text-4xl font-bold border-4 border-white/20 shadow-inner overflow-hidden", bgColor, accentColor)}>
            {image ? (
              <img src={image} alt={name} className="w-full h-full object-cover" />
            ) : (
              name.charAt(0)
            )}
          </div>
          <div className="text-center">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">{name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-300">{age} years old</p>
          </div>

          <div className="flex flex-col space-y-2 w-full text-sm">
            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
              <Briefcase size={16} />
              <span>{role}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
              <MapPin size={16} />
              <span>{location}</span>
            </div>
          </div>
        </div>

        {/* Right Column: Bio & Details */}
        <div className="flex-grow space-y-4">
          <div className="relative p-4 rounded-lg bg-white/5 border border-white/10 italic text-gray-700 dark:text-gray-200">
            <Quote size={20} className={cn("absolute -top-2 -left-2 fill-current opacity-50", accentColor)} />
            "{quote}"
          </div>

          <div>
            <h4 className="font-semibold text-sm uppercase tracking-wider text-gray-500 mb-2">Bio</h4>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{bio}</p>
          </div>

          <div>
            <h4 className="font-semibold text-sm uppercase tracking-wider text-gray-500 mb-2">Key Traits</h4>
            <div className="flex flex-wrap gap-2">
              {traits.map((trait, index) => (
                <span
                  key={index}
                  className={cn("px-3 py-1 rounded-full text-xs font-medium border border-white/10", bgColor, accentColor)}
                >
                  {trait}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </GlassCard>
  );
};
