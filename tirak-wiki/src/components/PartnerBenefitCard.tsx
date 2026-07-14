import React from 'react';
import { motion } from 'framer-motion';
import { DollarSign, Clock, Users, Shield, TrendingUp, Globe, Star, Zap, Heart, Banknote, CameraOff, CalendarClock, ShieldCheck, MessageCircleHeart } from 'lucide-react';
import { cn } from '../lib/utils';

const iconMap: Record<string, React.ComponentType<{ className?: string; size?: number }>> = {
  'dollar-sign': DollarSign,
  'clock': Clock,
  'users': Users,
  'shield': Shield,
  'trending-up': TrendingUp,
  'globe': Globe,
  'star': Star,
  'zap': Zap,
  'heart': Heart,
  'banknote': Banknote,
  'camera-off': CameraOff,
  'calendar-clock': CalendarClock,
  'shield-check': ShieldCheck,
  'message-circle-heart': MessageCircleHeart,
};

interface PartnerBenefitCardProps {
  iconName?: string;
  iconColor?: string;
  icon?: React.ReactNode;
  headline: string;
  description: string;
  stat?: string;
  statLabel?: string;
  className?: string;
}

export const PartnerBenefitCard = ({
  iconName,
  iconColor = 'text-[#F5A6BF]',
  icon,
  headline,
  description,
  stat,
  statLabel,
  className,
}: PartnerBenefitCardProps) => {
  const IconComponent = iconName ? iconMap[iconName] : null;

  return (
    <motion.div
      className={cn(
        'p-6 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 shadow-lg text-center',
        className
      )}
      whileHover={{ scale: 1.02, y: -2 }}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4 }}
    >
      <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-[#F5A6BF]/20 to-[#9B8FD9]/20 flex items-center justify-center mx-auto mb-4">
        {IconComponent ? <IconComponent className={iconColor} size={28} /> : icon}
      </div>

      {stat && (
        <div className="mb-2">
          <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#F5A6BF] to-[#9B8FD9]">
            {stat}
          </span>
          {statLabel && (
            <span className="block text-xs text-gray-500 mt-1">{statLabel}</span>
          )}
        </div>
      )}

      <h3 className="text-lg font-bold text-white mb-2">{headline}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
    </motion.div>
  );
};
