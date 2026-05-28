import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Hakkımda & Ekibimiz | [MARKA ADI]',
  description: '[MARKA HAKKINDA ACIKLAMA]',
  openGraph: {
    title: 'Hakkımda & Ekibimiz | [MARKA ADI]',
    description: '[MARKA HAKKINDA ACIKLAMA]',
    url: `${process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'}/hakkimizda`,
  }
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
