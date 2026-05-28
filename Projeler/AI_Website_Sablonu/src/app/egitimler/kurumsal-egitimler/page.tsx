'use client'

import { motion } from 'framer-motion'
import { useRef, useState } from 'react'
import type { MouseEvent } from 'react'
import Image from 'next/image'
import { GraduationCap, Building, Target, Presentation, Briefcase, Zap, CheckCircle2 } from 'lucide-react'
import { useTranslation } from '@/i18n/i18n'

const fadeUp = {
  hidden: { opacity: 0, y: 50, filter: 'blur(4px)' },
  visible: (i: number) => ({
    opacity: 1, y: 0, filter: 'blur(0px)',
    transition: { duration: 0.7, delay: i * 0.12, ease: [0.16, 1, 0.3, 1] }
  })
}

function RefCard({ client, index }: { client: any; index: number }) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [imgError, setImgError] = useState(false)

  const handleMouse = (e: MouseEvent) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100
    cardRef.current.style.setProperty('--mouse-x', `${x}%`)
    cardRef.current.style.setProperty('--mouse-y', `${y}%`)
  }

  return (
    <motion.div
      ref={cardRef}
      variants={fadeUp}
      custom={index}
      onMouseMove={handleMouse}
      className="bento-card !rounded-3xl group relative overflow-hidden p-8 border border-white/5 bg-[#0a0a0f] hover:border-white/10"
    >
      {/* Top accent */}
      <div
        className="absolute -top-px left-[15%] right-[15%] h-[1px] opacity-40 group-hover:opacity-100 transition-opacity duration-500"
        style={{ background: `linear-gradient(90deg, transparent, ${client.bgGlow.replace('0.12', '0.9')}, transparent)` }}
      />
      {/* Background glow on hover */}
      <div
        className="absolute -top-10 -right-10 w-[180px] h-[180px] rounded-full blur-[80px] opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"
        style={{ background: client.bgGlow }}
      />

      <div className="relative z-10">
        {/* Icon + Name */}
        <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${client.gradient} flex items-center justify-center text-white shadow-lg mb-5 group-hover:scale-110 transition-transform duration-500 overflow-hidden relative`}>
          {client.logo ? (
            <Image 
              src={client.logo} 
              alt={`${client.name} logo`}
              fill
              className="object-contain bg-white p-2"
            />
          ) : !imgError && client.logoDomain ? (
            <Image 
              src={`https://www.google.com/s2/favicons?domain=${client.logoDomain}&sz=128`} 
              alt={`${client.name} logo`} 
              width={128}
              height={128}
              className="w-full h-full object-cover bg-white p-1.5"
              onError={() => setImgError(true)}
              unoptimized
            />
          ) : (
            <GraduationCap className="w-6 h-6" />
          )}
        </div>
        <h4 className="text-xl font-bold text-white mb-3">{client.name}</h4>
        <p className="text-gray-400 text-base leading-relaxed">{client.desc}</p>
      </div>
    </motion.div>
  )
}

export default function CorporateTrainingsPage() {
  const { t } = useTranslation();

  const educationClients = [
    {
      name: t('corporateTrainings.client1Name'),
      desc: t('corporateTrainings.client1Desc'),
      gradient: 'from-blue-500 to-blue-600',
      bgGlow: 'rgba(52, 211, 153, 0.12)',
      logoDomain: 'example.com',
      logo: '/images/logos/logo.png'
    },
    {
      name: t('corporateTrainings.client2Name'),
      desc: t('corporateTrainings.client2Desc'),
      gradient: 'from-slate-400 to-slate-600',
      bgGlow: 'rgba(148, 163, 184, 0.12)',
      logoDomain: 'example.com'
    },
    {
      name: t('corporateTrainings.client3Name'),
      desc: t('corporateTrainings.client3Desc'),
      gradient: 'from-stone-500 to-stone-600',
      bgGlow: 'rgba(239, 68, 68, 0.12)',
      logoDomain: 'example.com'
    },
    {
      name: t('corporateTrainings.client4Name'),
      desc: t('corporateTrainings.client4Desc'),
      gradient: 'from-blue-500 to-blue-700',
      bgGlow: 'rgba(139, 92, 246, 0.12)',
      logoDomain: 'example.com',
      logo: '/images/logos/logo.png'
    },
    {
      name: t('corporateTrainings.client5Name'),
      desc: t('corporateTrainings.client5Desc'),
      gradient: 'from-stone-500 to-stone-600',
      bgGlow: 'rgba(249, 115, 22, 0.12)',
      logoDomain: 'example.com',
      logo: '/images/logos/logo.png'
    },
    {
      name: t('corporateTrainings.client6Name'),
      desc: t('corporateTrainings.client6Desc'),
      gradient: 'from-stone-600 to-stone-500',
      bgGlow: 'rgba(234, 88, 12, 0.12)',
      logoDomain: 'example.com'
    },
  ];

  const benefits = [
    t('corporateTrainings.benefit1'),
    t('corporateTrainings.benefit2'),
    t('corporateTrainings.benefit3'),
    t('corporateTrainings.benefit4'),
  ]

  const features = [
    {
      icon: <Building className="w-8 h-8 text-[#4F8BFF]" />,
      title: t('corporateTrainings.feat1Title'),
      desc: t('corporateTrainings.feat1Desc')
    },
    {
      icon: <Target className="w-8 h-8 text-[#EDEAE3]" />,
      title: t('corporateTrainings.feat2Title'),
      desc: t('corporateTrainings.feat2Desc')
    },
    {
      icon: <Presentation className="w-8 h-8 text-[#4F8BFF]" />,
      title: t('corporateTrainings.feat3Title'),
      desc: t('corporateTrainings.feat3Desc')
    }
  ]

  return (
    <div className="pt-32 pb-24 relative min-h-screen bg-[#08090C] overflow-hidden">
      {/* Background Header Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-[#4F8BFF]/5 blur-[120px] rounded-[100%] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Hero Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center mb-32">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="inline-block px-4 py-2 rounded-full bg-[#4F8BFF]/10 border border-[#4F8BFF]/20 text-[#4F8BFF] text-sm font-bold tracking-wider mb-6 uppercase">
              {t('corporateTrainings.badge')}
            </span>
            <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-8 leading-[1.1]">
              {t('corporateTrainings.titleLine1')} <span className="text-gradient-accent">{t('corporateTrainings.titleHighlight')}</span> <br />
              {t('corporateTrainings.titleLine2')}
            </h1>
            <p className="text-gray-400 text-lg md:text-xl leading-relaxed mb-10">
              {t('corporateTrainings.desc')}
            </p>
            
            <ul className="space-y-4 mb-12">
              {benefits.map((benefit, i) => (
                <li key={i} className="flex items-center gap-3 text-gray-300">
                  <div className="w-6 h-6 rounded-full bg-white/5 flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-4 h-4 text-[#4F8BFF]" />
                  </div>
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
            
            <a 
              href={`mailto:${process.env.NEXT_PUBLIC_CONTACT_EMAIL || "info@example.com"}`}
              className="inline-flex items-center justify-center px-8 py-4 text-base font-bold text-white bg-gradient-to-r from-[#4F8BFF] to-[#4F8BFF] hover:from-[#7AA8FF] hover:to-[#4F8BFF] border border-transparent rounded-2xl transition-all hover:scale-105 active:scale-95 shadow-[0_0_30px_rgba(79, 139, 255, 0.3)] hover:shadow-[0_0_50px_rgba(79, 139, 255, 0.5)]"
            >
              {t('corporateTrainings.ctaBtn')}
            </a>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.9, filter: 'blur(10px)' }}
            animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
            transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="relative"
          >
            <div className="relative aspect-square w-full max-w-[500px] mx-auto rounded-[3rem] overflow-hidden border border-white/10 shadow-[0_0_60px_rgba(79, 139, 255, 0.15)] bg-[#0E0F14]">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-900/40 to-blue-900/40 opacity-80 mix-blend-luminosity" />
              
              <div className="absolute inset-0 bg-[url('/images/egitimler/egitim2.webp')] bg-cover bg-center opacity-70 hover:opacity-90 transition-all duration-1000" />
              <div className="absolute inset-0 bg-gradient-to-t from-[#08090C] via-[#08090C]/40 to-[#08090C]/20" />
              
              <div className="absolute bottom-10 left-10 right-10 flex flex-col items-center p-6 rounded-2xl bg-black/60 backdrop-blur-md border border-white/10">
                <div className="flex -space-x-4 mb-3">
                  <div className="w-12 h-12 rounded-full border-2 border-black bg-gradient-to-br from-[#4F8BFF] to-[#4F8BFF] flex items-center justify-center text-white"><Briefcase size={20} /></div>
                  <div className="w-12 h-12 rounded-full border-2 border-black bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white"><Zap size={20} /></div>
                  <div className="w-12 h-12 rounded-full border-2 border-black bg-gradient-to-br from-stone-400 to-stone-500 flex items-center justify-center text-white"><Target size={20} /></div>
                </div>
                <p className="text-white text-sm font-semibold text-center">{t('corporateTrainings.heroImgDesc')}</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Kurumlar Grid */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="mb-32"
        >
          <motion.div variants={fadeUp} custom={0} className="text-center max-w-3xl mx-auto mb-14">
            <div className="flex items-center gap-3 justify-center mb-4">
              <GraduationCap className="w-5 h-5 text-[#4F8BFF]" />
              <span className="text-sm font-semibold text-gray-500 uppercase tracking-[0.2em]">{t('corporateTrainings.refsBadge')}</span>
            </div>
            <motion.h3 variants={fadeUp} custom={1} className="text-3xl md:text-5xl font-bold tracking-tight mb-6 text-white">
              {t('corporateTrainings.refsTitle')}{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#4F8BFF] to-[#4F8BFF]">{t('corporateTrainings.refsTitleHighlight')}</span>
            </motion.h3>
            <motion.p variants={fadeUp} custom={2} className="text-gray-400 text-lg leading-relaxed">
              {t('corporateTrainings.refsDesc')}
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {educationClients.map((client, i) => (
              <RefCard key={client.name} client={client} index={i} />
            ))}
          </motion.div>
        </motion.div>

        {/* Eğitimlerimizden Kareler (Gallery) */}
        <div className="mb-32 relative">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center max-w-3xl mx-auto mb-14"
          >
             <h3 className="text-3xl font-bold text-white mb-4">{t('corporateTrainings.galleryTitle')}</h3>
             <p className="text-gray-400 text-lg">{t('corporateTrainings.galleryDesc')}</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
             <motion.div 
               initial={{ opacity: 0, x: -30 }} 
               whileInView={{ opacity: 1, x: 0 }} 
               viewport={{ once: true }}
               className="relative h-64 md:h-full rounded-3xl overflow-hidden border border-white/10 group"
             >
               <Image src="/images/egitimler/egitim1.webp" alt="Kurumsal Eğitim" fill className="object-cover opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all duration-700" />
               <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-6">
                 <span className="text-white font-medium">{t('corporateTrainings.galleryImg1')}</span>
               </div>
             </motion.div>
             <div className="grid grid-cols-1 gap-6">
               <motion.div 
                 initial={{ opacity: 0, x: 30 }} 
                 whileInView={{ opacity: 1, x: 0 }} 
                 viewport={{ once: true }}
                 transition={{ delay: 0.2 }}
                 className="relative h-64 rounded-3xl overflow-hidden border border-white/10 group"
               >
                 <Image src="/images/egitimler/egitim2.webp" alt="Kurumsal Eğitim" fill className="object-cover opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all duration-700" style={{ objectPosition: 'center 65%' }} />
                 <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-6">
                   <span className="text-white font-medium">{t('corporateTrainings.galleryImg2')}</span>
                 </div>
               </motion.div>
               <motion.div 
                 initial={{ opacity: 0, x: 30 }} 
                 whileInView={{ opacity: 1, x: 0 }} 
                 viewport={{ once: true }}
                 transition={{ delay: 0.4 }}
                 className="relative h-64 rounded-3xl overflow-hidden border border-white/10 group bg-white/[0.02]"
               >
                 <Image src="/images/egitimler/egitim3.webp" alt="Kurumsal Eğitim" fill className="object-cover opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all duration-700" style={{ objectPosition: 'center 75%' }} />
                 <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-6">
                   <span className="text-white font-medium">{t('corporateTrainings.galleryImg3')}</span>
                 </div>
               </motion.div>
             </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mb-20">
          <motion.h3 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center text-3xl font-bold text-white mb-16"
          >
            {t('corporateTrainings.featTitle')}
          </motion.h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.15, ease: [0.16, 1, 0.3, 1] }}
                className="bento-card group"
              >
                <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-500">
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold text-white mb-4 tracking-tight">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed text-sm">
                  {feature.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}
