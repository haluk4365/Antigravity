'use client'

import { motion } from 'framer-motion'
import { Instagram, Linkedin, Twitter, Youtube, Mail } from 'lucide-react'
import { useTranslation } from '@/i18n/i18n'
import Link from 'next/link'
import Image from 'next/image'

export function Footer() {
  const currentYear = new Date().getFullYear();
  const { t } = useTranslation();

  // TODO: kendi sosyal medya linklerinizi ve e-postanızı girin
  const socialLinks = [
    { icon: <Linkedin className="w-5 h-5" />, href: "https://linkedin.com/in/[KULLANICI_HANDLE]", label: "LinkedIn" },
    { icon: <Instagram className="w-5 h-5" />, href: "https://instagram.com/[KULLANICI_HANDLE]", label: "Instagram" },
    { icon: <Youtube className="w-5 h-5" />, href: "https://youtube.com/@[KULLANICI_HANDLE]", label: "YouTube" },
    { icon: <Twitter className="w-5 h-5" />, href: "https://x.com/[KULLANICI_HANDLE]", label: "X" },
    { icon: <Mail className="w-5 h-5" />, href: `mailto:${process.env.NEXT_PUBLIC_CONTACT_EMAIL || "info@example.com"}`, label: "Email" },
  ];

  return (
    <footer className="border-t border-white/5 bg-[#08090C] relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-2xl h-[200px] bg-[#4F8BFF]/8 blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative z-10">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8 md:gap-12">

          <div className="flex flex-col items-center md:items-start text-center md:text-left gap-4">
            <Link href="/" className="flex items-center gap-3 text-2xl font-semibold tracking-tight text-[#F4F2EC] group">
              <Image src="/images/logo.svg" alt="" width={36} height={36} className="h-9 w-9" />
              <span>[MARKA<span className="text-[#4F8BFF]"> ADI]</span></span>
            </Link>
            <p className="text-[#8A8E99] text-sm max-w-xs">{t('footer.description')}</p>
            <div className="mt-2 flex gap-4">
              {socialLinks.map((link, i) => (
                <a
                  key={i}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={link.label}
                  className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 hover:border-white/20 hover:-translate-y-1 transition-all duration-300"
                >
                  {link.icon}
                </a>
              ))}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-6 sm:gap-12 text-center sm:text-left text-sm text-gray-400">
            <div className="flex flex-col gap-3">
              <span className="text-white font-semibold mb-1">Kurumsal</span>

              <Link href="/sozlesmeler/mesafeli-satis" className="hover:text-white transition-colors">Mesafeli Satış Sözleşmesi</Link>
              <Link href="/sozlesmeler/kvkk" className="hover:text-white transition-colors">Gizlilik ve KVKK Politikası</Link>
            </div>
          </div>

        </div>

        <div className="mt-16">
          <div className="halftone-divider max-w-md mx-auto mb-6" />
          <div className="flex flex-col items-center justify-center text-[#8A8E99] text-sm">
            <p>© {currentYear} [MARKA ADI]. {t('footer.rights')}</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
