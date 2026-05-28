import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Hizmetler',
  description: '[MARKA ADI] işletmelere yönelik profesyonel yapay zeka çözümleri ve hizmetleri.',
  openGraph: {
    title: 'Hizmetler | [MARKA ADI]',
    description: '[MARKA ADI] işletmelere yönelik profesyonel yapay zeka çözümleri ve hizmetleri.',
  }
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
