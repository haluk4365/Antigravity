import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Çözümler — İşletmeler ve Girişimciler İçin Yapay Zeka',
  description: '[MARKA ADI] çözümleriyle iş süreçlerinizi otomatikleştirin. Hazır AI araçları ve şirkete özel otonom sistem kurulum hizmetleri.',
  openGraph: {
    title: 'Çözümler | [MARKA ADI]',
    description: '[MARKA ADI] çözümleriyle iş süreçlerinizi otomatikleştirin. Hazır AI araçları ve şirkete özel otonom sistem kurulum hizmetleri.',
    url: `${process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'}/cozumler`,
  }
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
