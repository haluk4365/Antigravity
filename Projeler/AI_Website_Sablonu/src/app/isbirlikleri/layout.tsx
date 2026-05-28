import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Marka İşbirlikleri & Sponsorluklar | [MARKA ADI]',
  description: 'Yapay zeka ürünleriniz, SaaS uygulamalarınız veya teknoloji servisleriniz için 500.000+ izlenmeli video içerik üretimi ve B2B marka sponsorluk paketleri.',
  openGraph: {
    title: 'Marka İşbirlikleri & Sponsorluklar | [MARKA ADI]',
    description: 'Yapay zeka ürünleriniz, SaaS uygulamalarınız veya teknoloji servisleriniz için video içerik üretimi ve B2B marka sponsorluk dosyası.',
    url: `${process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'}/isbirlikleri`,
  }
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
