'use client';

import { motion } from 'framer-motion';
import { useRef } from 'react';
import type { MouseEvent } from 'react';
import {
  Users, GraduationCap, ArrowUpRight, Sparkles, TrendingUp, ExternalLink
} from 'lucide-react';
import { ServicesSection } from '@/components/sections/ServicesSection';
import { useTranslation } from '@/i18n/i18n';

function SkoolIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

const fadeUp = {
  hidden: { opacity: 0, y: 50, filter: 'blur(4px)' },
  visible: (i: number) => ({
    opacity: 1, y: 0, filter: 'blur(0px)',
    transition: { duration: 0.7, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }
  })
};

function BentoCard({ children, className = '', custom = 0 }: { children: React.ReactNode; className?: string; custom?: number }) {
  const cardRef = useRef<HTMLDivElement>(null);
  const handleMouse = (e: MouseEvent) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    cardRef.current.style.setProperty('--mouse-x', `${x}%`);
    cardRef.current.style.setProperty('--mouse-y', `${y}%`);
  };

  return (
    <motion.div
      ref={cardRef}
      variants={fadeUp}
      custom={custom}
      onMouseMove={handleMouse}
      className={`bento-card relative overflow-hidden ${className}`}
    >
      {children}
    </motion.div>
  );
}

export default function SolutionsPage() {
  const { t } = useTranslation();

  const readySolutions = [
    {
      title: t('solutions.readyItemTitle'),
      description: t('solutions.readyItemDesc'),
      features: [t('solutions.readyItemFeature1'), t('solutions.readyItemFeature2'), t('solutions.readyItemFeature3'), t('solutions.readyItemFeature4')],
      href: '/cozumler/artifex-campus',
      accentColor: '#4F8BFF',
      icon: <Sparkles className="w-6 h-6" />,
      external: false,
    },
  ];

  const customSolutions = [
    {
      title: t('solutions.customItemTitle'),
      description: t('solutions.customItemDesc'),
      features: [t('solutions.customItemFeature1'), t('solutions.customItemFeature2'), t('solutions.customItemFeature3'), t('solutions.customItemFeature4')],
      href: '/cozumler/hizmetler',
      accentColor: '#4F8BFF',
      icon: <TrendingUp className="w-6 h-6" />,
      external: false,
    },
  ];

  const educations = [
    {
      title: t('solutions.aiFactoryTitle'),
      subtitle: t('solutions.aiFactorySubtitle'),
      description: t('solutions.aiFactoryDesc'),
      href: process.env.NEXT_PUBLIC_COMMUNITY_URL || '#', // TODO: topluluk linkinizi env'e koyun
      icon: <SkoolIcon className="w-7 h-7" />,
      gradient: 'from-blue-400 to-blue-600',
      bgGlow: 'rgba(52, 211, 153, 0.1)',
      members: t('solutions.aiFactoryMembers'),
      badge: t('solutions.aiFactoryBadge'),
    },
    {
      title: t('solutions.udemyTitle'),
      subtitle: t('solutions.udemySubtitle'),
      description: t('solutions.udemyDesc'),
      href: process.env.NEXT_PUBLIC_TRAINING_URL || '#', // TODO: egitim linkinizi env'e koyun
      icon: <GraduationCap className="w-7 h-7" />,
      gradient: 'from-blue-500 to-blue-700',
      bgGlow: 'rgba(139, 92, 246, 0.1)',
      members: t('solutions.udemyMembers'),
      badge: t('solutions.udemyBadge'),
    },
  ];

  return (
    <div className="pt-24 pb-12">
      {/* ÇÖZÜMLER */}
      <section className="py-12 relative" id="solutions">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="text-center max-w-3xl mx-auto mb-16"
          >
            <motion.span variants={fadeUp} custom={0} className="inline-flex items-center gap-2 text-[#4F8BFF] text-sm font-semibold tracking-[0.2em] uppercase mb-4"><span className="halftone-arc" aria-hidden />{t('solutions.badge')}</motion.span>
            <motion.h2 variants={fadeUp} custom={1} className="text-3xl md:text-5xl font-bold mb-5 tracking-tight">
              {t('solutions.title')}{' '}
              <span className="text-gradient-accent">{t('solutions.titleHighlight')}</span>
            </motion.h2>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch">
            <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} className="flex flex-col h-full">
              <motion.h3 variants={fadeUp} custom={0} className="text-sm font-semibold text-gray-500 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                <div className="w-5 h-[1px] bg-[#4F8BFF]" />
                {t('solutions.readyTitle')}
              </motion.h3>
              <div className="flex-1 flex flex-col gap-6">
                {readySolutions.map((solution, i) => (
                  <BentoCard key={solution.title} custom={i + 1} className="!rounded-3xl relative flex-1 flex flex-col group p-6 border border-white/5 bg-white/5 backdrop-blur-sm">
                    <div className="absolute -top-px left-[15%] right-[15%] h-[1px] bg-gradient-to-r from-transparent via-[#4F8BFF]/50 to-transparent opacity-50 group-hover:opacity-100 transition-opacity" />
                    <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-[200px] h-[200px] rounded-full blur-[80px] opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" style={{ background: 'rgba(79, 139, 255, 0.08)' }} />
                    <div className="relative z-10 flex flex-col h-full">
                      <div className="flex-1">
                        <div className="w-12 h-12 rounded-2xl bg-[#4F8BFF]/10 border border-[#4F8BFF]/20 flex items-center justify-center text-[#4F8BFF] mb-5 group-hover:scale-110 transition-transform duration-500">
                          {solution.icon}
                        </div>
                        <h4 className="text-2xl font-bold text-white mb-3">{solution.title}</h4>
                        <p className="text-gray-400 text-sm leading-relaxed mb-6">{solution.description}</p>
                        <div className="flex flex-wrap gap-2 mb-6">
                          {solution.features.map((f) => (
                            <span key={f} className="px-3 py-1 rounded-lg text-xs font-medium bg-[#4F8BFF]/10 border border-[#4F8BFF]/20 text-[#4F8BFF]">{f}</span>
                          ))}
                        </div>
                      </div>
                      <div className="mt-auto">
                        <a href={solution.href} className="inline-flex items-center gap-2 text-sm font-semibold text-white hover:text-[#4F8BFF] transition-colors">
                          {t('solutions.exploreBtn')} <ArrowUpRight className="w-4 h-4" />
                        </a>
                      </div>
                    </div>
                  </BentoCard>
                ))}
              </div>
            </motion.div>

            <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} className="flex flex-col h-full">
              <motion.h3 variants={fadeUp} custom={0} className="text-sm font-semibold text-gray-500 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                <div className="w-5 h-[1px] bg-[#4F8BFF]" />
                {t('solutions.customTitle')}
              </motion.h3>
              <div className="flex-1 flex flex-col gap-6">
                {customSolutions.map((solution, i) => (
                  <BentoCard key={solution.title} custom={i + 1} className="!rounded-3xl relative flex-1 flex flex-col group p-6 border border-white/5 bg-white/5 backdrop-blur-sm">
                    <div className="absolute -top-px left-[15%] right-[15%] h-[1px] bg-gradient-to-r from-transparent via-[#4F8BFF]/50 to-transparent opacity-50 group-hover:opacity-100 transition-opacity" />
                    <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-[200px] h-[200px] rounded-full blur-[80px] opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" style={{ background: 'rgba(79, 139, 255, 0.08)' }} />
                    <div className="relative z-10 flex flex-col h-full">
                      <div className="flex-1">
                        <div className="w-12 h-12 rounded-2xl bg-[#4F8BFF]/10 border border-[#4F8BFF]/20 flex items-center justify-center text-[#4F8BFF] mb-5 group-hover:scale-110 transition-transform duration-500">
                          {solution.icon}
                        </div>
                        <h4 className="text-2xl font-bold text-white mb-3">{solution.title}</h4>
                        <p className="text-gray-400 text-sm leading-relaxed mb-6">{solution.description}</p>
                        <div className="flex flex-wrap gap-2 mb-6">
                          {solution.features.map((f) => (
                            <span key={f} className="px-3 py-1 rounded-lg text-xs font-medium bg-[#4F8BFF]/10 border border-[#4F8BFF]/20 text-[#4F8BFF]">{f}</span>
                          ))}
                        </div>
                      </div>
                      <div className="mt-auto">
                        <a href={solution.href} className="inline-flex items-center gap-2 text-sm font-semibold text-white hover:text-[#4F8BFF] transition-colors">
                          {t('solutions.reviewBtn')} <ArrowUpRight className="w-4 h-4" />
                        </a>
                      </div>
                    </div>
                  </BentoCard>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* EĞİTİMLER */}
      <section className="py-24 relative" id="educations">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="text-center max-w-3xl mx-auto mb-16"
          >
            <motion.span variants={fadeUp} custom={0} className="inline-block text-blue-400 text-sm font-semibold tracking-[0.2em] uppercase mb-4">
              {t('solutions.eduBadge')}
            </motion.span>
            <motion.h2 variants={fadeUp} custom={1} className="text-3xl md:text-5xl font-bold mb-5 tracking-tight">
              {t('solutions.eduTitle')}{' '}
              <span className="text-gradient-accent">{t('solutions.eduTitleHighlight')}</span>
            </motion.h2>
            <motion.p variants={fadeUp} custom={2} className="text-gray-400 text-lg leading-relaxed">
              {t('solutions.eduDesc')}
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {educations.map((edu, i) => (
              <BentoCard key={edu.title} custom={i} className="!rounded-3xl relative group overflow-hidden p-6 border border-white/5 bg-white/5 backdrop-blur-sm">
                <div
                  className="absolute -top-px left-[15%] right-[15%] h-[1px] opacity-40 group-hover:opacity-100 transition-opacity duration-500"
                  style={{ background: `linear-gradient(90deg, transparent, ${edu.bgGlow.replace('0.1', '0.8')}, transparent)` }}
                />
                <div className="absolute -top-20 right-0 w-[200px] h-[200px] rounded-full blur-[80px] opacity-0 group-hover:opacity-60 transition-opacity duration-700 pointer-events-none" style={{ background: edu.bgGlow }} />

                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-6">
                    <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${edu.gradient} flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform duration-500`}>
                      {edu.icon}
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r ${edu.gradient} text-white`}>
                      {edu.badge}
                    </span>
                  </div>

                  <h3 className="text-2xl font-bold text-white mb-2">{edu.title}</h3>
                  <p className="text-sm font-medium text-gray-300 mb-3">{edu.subtitle}</p>
                  <p className="text-gray-400 text-sm leading-relaxed mb-6">{edu.description}</p>

                  <div className="flex items-center justify-between mt-auto">
                    <span className="flex items-center gap-2 text-xs text-gray-500">
                      <Users className="w-3.5 h-3.5" />
                      {edu.members}
                    </span>
                    <a
                      href={edu.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-white/[0.05] border border-white/[0.08] hover:bg-white/[0.08] hover:border-white/[0.15] text-white transition-all duration-300"
                    >
                      {t('solutions.joinBtn')} <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              </BentoCard>
            ))}
          </motion.div>
        </div>
      </section>

      {/* HİZMETLER — Referanslar dahil */}
      <ServicesSection />
    </div>
  );
}
