'use client'

import { motion } from 'framer-motion'
import { Sparkles, ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function ArtifexCampusPage() {
  return (
    <div className="pt-32 pb-24 relative min-h-screen bg-[#08090C] flex items-center justify-center">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/10 blur-[120px] rounded-full pointer-events-none" />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="w-16 h-16 rounded-2xl bg-[#4F8BFF]/10 border border-[#4F8BFF]/20 flex items-center justify-center text-[#4F8BFF] mx-auto mb-6">
            <Sparkles className="w-8 h-8" />
          </div>
          
          <span className="inline-block px-4 py-2 rounded-full border border-white/10 text-gray-300 text-sm font-semibold tracking-wider mb-6 bg-white/5 backdrop-blur-sm">
            Çok Yakında
          </span>

          <h1 className="text-4xl md:text-6xl font-bold mb-6 tracking-tight text-white">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-[#4F8BFF]">[ÜRÜN 1 ADI]</span>
          </h1>
          
          <p className="text-gray-400 text-lg md:text-xl leading-relaxed mb-10 max-w-2xl mx-auto">
            İşletmenizi AI ile dönüştürecek hazır çözüm paketleri. Personel tasarrufu sağlayan, operasyonel yükü sıfıra indiren sonuç odaklı B2B yapay zeka otomasyonları.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
            {['Hazır Kurulum', 'Anında Başlama', '7/24 Operasyon', 'Ölçeklenebilir'].map((feature) => (
              <span key={feature} className="px-4 py-2 rounded-xl text-sm font-medium bg-[#4F8BFF]/10 border border-[#4F8BFF]/20 text-[#4F8BFF]">
                {feature}
              </span>
            ))}
          </div>

          <Link 
            href="/cozumler"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-white bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Çözümlere Dön
          </Link>
        </motion.div>
      </div>
    </div>
  )
}
