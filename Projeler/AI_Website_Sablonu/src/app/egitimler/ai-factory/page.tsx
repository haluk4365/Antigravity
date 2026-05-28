'use client'

import { motion } from 'framer-motion'
import { ArrowUpRight } from 'lucide-react'
import { useTranslation } from '@/i18n/i18n'

export default function AIFactoryPage() {
  const { t } = useTranslation();

  return (
    <div className="pt-32 pb-24 relative min-h-screen flex flex-col items-center justify-center">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 text-blue-400 text-sm font-semibold tracking-[0.2em] uppercase mb-4"><span className="halftone-arc" aria-hidden />{t('aiFactory.badge')}</span>
          <h1 className="text-4xl md:text-6xl font-bold mb-6 tracking-tight text-white">
            {t('aiFactory.title')}{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-blue-600">{t('aiFactory.titleHighlight')}</span>
          </h1>
          <p className="text-gray-400 text-lg md:text-xl leading-relaxed mb-10 max-w-2xl mx-auto">
            {t('aiFactory.desc')}
          </p>
          <a 
            href={process.env.NEXT_PUBLIC_COMMUNITY_URL || "#"} /* TODO: topluluk linkinizi env'e koyun */
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-lg font-bold text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-400 hover:to-blue-500 transition-all duration-300 shadow-lg shadow-blue-500/25"
          >
            {t('aiFactory.btn')} <ArrowUpRight className="w-5 h-5" />
          </a>
        </motion.div>
      </div>
    </div>
  )
}
