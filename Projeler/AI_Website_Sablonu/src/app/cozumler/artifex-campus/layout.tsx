import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '[ÜRÜN 1 ADI] & Otonom Sistem Kurulumu | [MARKA ADI]',
  description: 'İşletmeler ve startup\'lar için A\'dan Z\'ye özel yapay zeka ajanları, otonom pazarlama sistemleri ve mimari danışmanlık hizmetleri.',
  openGraph: {
    title: '[ÜRÜN 1 ADI] — Kurumsal AI Danışmanlık | [MARKA ADI]',
    description: 'İşletmeler ve startup\'lar için A\'dan Z\'ye özel yapay zeka ajanları, otonom pazarlama sistemleri ve mimari danışmanlık hizmetleri.',
    url: `${process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'}/cozumler/artifex-campus`,
  }
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Service',
            name: '[ÜRÜN 1 ADI] & Otonom AI Sistem Kurulumu',
            description: 'İşletmeler ve startup\'lar için A\'dan Z\'ye özel yapay zeka ajanları, otonom pazarlama sistemleri ve AI mimari danışmanlık hizmetleri.',
            provider: {
              '@type': 'Organization',
              name: '[MARKA ADI]',
              sameAs: process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'
            }
          })
        }}
      />
      {children}
    </>
  )
}
