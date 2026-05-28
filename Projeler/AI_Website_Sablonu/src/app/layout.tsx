import type { Metadata } from 'next'
import { Inter_Tight, JetBrains_Mono } from 'next/font/google'
import { LanguageProvider } from '@/i18n/i18n'
import { Navbar } from '@/components/layout/Navbar'
import dynamic from 'next/dynamic'
import './globals.css'

const Footer = dynamic(() => import('@/components/layout/Footer').then(mod => mod.Footer))

const interTight = Inter_Tight({
  subsets: ['latin', 'latin-ext'],
  variable: '--font-inter-tight',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700', '800'],
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin', 'latin-ext'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
  weight: ['400', '500', '600'],
})

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'),
  title: {
    default: '[MARKA ADI] — [KISA TANIM]',
    template: '%s | [MARKA ADI]',
  },
  description: '[SITE ACIKLAMASI]',
  keywords: ['[ANAHTAR KELIME 1]', '[ANAHTAR KELIME 2]', '[ANAHTAR KELIME 3]'],
  authors: [{ name: '[MARKA ADI]' }],
  creator: '[MARKA ADI]',
  openGraph: {
    type: 'website',
    locale: 'tr_TR',
    url: process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com',
    siteName: '[MARKA ADI]',
    title: '[MARKA ADI] — [KISA TANIM]',
    description: '[SITE ACIKLAMASI]',
    images: [
      {
        url: '/images/og-image.png',
        width: 1200,
        height: 630,
        alt: '[MARKA ADI] — [KISA TANIM]',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: '[MARKA ADI] — [KISA TANIM]',
    description: '[SITE ACIKLAMASI]',
    images: ['/images/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="tr" className={`${interTight.variable} ${jetbrainsMono.variable}`} suppressHydrationWarning>
      <head>
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
      </head>
      <body className="min-h-screen bg-[#08090C] text-[#F4F2EC] font-sans selection:bg-[#4F8BFF]/35">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Organization',
              name: '[MARKA ADI]',
              url: process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com',
              logo: '/favicon.svg',
              founder: {
                '@type': 'Person',
                name: '[MARKA SAHIBI ADI]',
                jobTitle: '[UNVAN]',
              },
              sameAs: [
                'https://instagram.com/[KULLANICI_HANDLE]',
                'https://youtube.com/@[KULLANICI_HANDLE]',
                'https://tiktok.com/@[KULLANICI_HANDLE]',
              ],
              description: '[SITE ACIKLAMASI]',
            }),
          }}
        />
        <LanguageProvider>
          <Navbar />
          <main className="pt-20">
            {children}
          </main>
          <Footer />
        </LanguageProvider>
      </body>
    </html>
  )
}
