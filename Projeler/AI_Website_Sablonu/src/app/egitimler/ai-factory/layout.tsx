import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '[ÜRÜN 2 ADI]: Girişimci Yapay Zeka Eğitimi | [MARKA ADI]',
  description: 'Girişimciler ve profesyoneller için sıfırdan yapay zeka otomasyonu, pasif gelir ve ürün çıkarma topluluğu. Skool üzerinden ulaşıma açık.',
  openGraph: {
    title: '[ÜRÜN 2 ADI] Topluluğu | [MARKA ADI]',
    description: 'Girişimciler ve profesyoneller için sıfırdan yapay zeka otomasyonu, pasif gelir ve ürün çıkarma topluluğu.',
    url: `${process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'}/egitimler/ai-factory`,
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
            '@type': 'Course',
            name: '[ÜRÜN 2 ADI] Topluluğu ve Eğitimi',
            description: 'Girişimciler ve profesyoneller için sıfırdan yapay zeka otomasyonu, pasif gelir ve AI ürün geliştirme kursu.',
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
