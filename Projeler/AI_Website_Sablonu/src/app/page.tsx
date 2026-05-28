import dynamic from 'next/dynamic'
import { HeroSectionElevate } from '@/components/sections/HeroSectionElevate'

const ProductsSection = dynamic(() => import('@/components/sections/ProductsSection').then(mod => mod.ProductsSection))

export default function Home() {
  return (
    <>
      <HeroSectionElevate bgImage="/hero_bg/hero_Elevate_New_V1.webp" />
      <ProductsSection />
    </>
  )
}
