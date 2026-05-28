'use client'

import { motion } from 'framer-motion'
import { useTranslation } from '@/i18n/i18n'
import Image from 'next/image'

function Reveal({ children, delay = 0, className = '' }: {
  children: React.ReactNode; delay?: number; className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay, ease: [0.25, 1, 0.5, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function HeroSectionElevate({ bgImage }: { bgImage: string }) {
  const { t } = useTranslation();

  return (
    <section
      className="relative min-h-screen flex flex-col justify-center bg-[#08090C] overflow-hidden"
      id="hero-elevate"
    >
      <Image
        src={bgImage}
        alt="[MARKA ADI] Hero"
        fill
        priority
        className="object-cover object-center absolute inset-0 z-0"
      />
      {/* darken + cool blue tint overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-[#08090C] via-[#08090C]/70 to-transparent opacity-95 z-0" />
      <div className="absolute inset-0 bg-[#0B0E1A]/35 mix-blend-multiply z-0" />
      {/* halftone watermark, echoes mark texture */}
      <div className="absolute inset-0 halftone-bg opacity-40 z-0" />

      {/* D11 Ash mark watermark — large faint disc bottom-left */}
      <div className="absolute -bottom-32 -left-40 w-[640px] h-[640px] opacity-[0.06] pointer-events-none z-0">
        <Image src="/images/logo.svg" alt="" fill className="object-contain" /> {/* TODO: kendi logonuz */}
      </div>

      {/* Ash drift particles — tiny dots scattering upward-left, echoes mark's "kül" trail */}
      <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
        <span className="ash-drift" style={{ left: '12%', top: '78%', width: '3px', height: '3px', animationDelay: '0s' }} />
        <span className="ash-drift" style={{ left: '8%', top: '64%', width: '2px', height: '2px', animationDelay: '1.2s' }} />
        <span className="ash-drift" style={{ left: '18%', top: '88%', width: '4px', height: '4px', animationDelay: '2.4s' }} />
        <span className="ash-drift" style={{ left: '6%', top: '52%', width: '2px', height: '2px', animationDelay: '3.6s' }} />
        <span className="ash-drift" style={{ left: '24%', top: '72%', width: '3px', height: '3px', animationDelay: '4.8s' }} />
        <span className="ash-drift" style={{ left: '14%', top: '60%', width: '2px', height: '2px', animationDelay: '6s' }} />
      </div>

      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-16 pt-24 pb-16">
        <div className="max-w-[42rem]">
          <Reveal delay={0.05}>
            <span className="mono-label text-[#4F8BFF] mb-5 inline-flex items-center gap-2">
              <span className="halftone-arc" aria-hidden />
              [MARKA ADI]
            </span>
          </Reveal>

          <Reveal delay={0.1}>
            <h1 className="font-display text-[clamp(2.6rem,5.2vw,5.2rem)] font-semibold tracking-[-0.035em] leading-[1.04] text-[#F4F2EC] mb-6">
              {t('hero.titleLine1')}
              <br />
              <span className="font-bold text-[#4F8BFF]">{t('hero.titleHighlight')}</span>
            </h1>
          </Reveal>

          <Reveal delay={0.25}>
            <p className="text-[#C9CCD4] text-lg sm:text-xl font-light leading-relaxed mb-10 max-w-lg">
              {t('hero.subtitle')}
            </p>
          </Reveal>

          <Reveal delay={0.4}>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-12 border-t border-white/10 w-full mt-4">
              {[
                { code: '01', title: t('hero.stat1Title'), desc: t('hero.stat1Desc') },
                { code: '02', title: t('hero.stat2Title'), desc: t('hero.stat2Desc') },
                { code: '03', title: t('hero.stat3Title'), desc: t('hero.stat3Desc') },
              ].map((stat) => (
                <div key={stat.code} className="bg-white/[0.04] backdrop-blur-sm border border-white/10 p-5 rounded-xl h-full flex flex-col hover:border-[#4F8BFF]/30 transition-colors duration-500">
                  <span className="font-mono text-[10px] tracking-[0.2em] text-[#4F8BFF]/80 mb-3">— {stat.code}</span>
                  <p className="text-[13px] lg:text-sm text-[#F4F2EC] font-semibold mb-2 tracking-tight">{stat.title}</p>
                  <div className="text-xs text-[#8A8E99] leading-relaxed">{stat.desc}</div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
