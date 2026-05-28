import { MetadataRoute } from 'next'

export const dynamic = 'force-static'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/r/', '/r'],
    },
    sitemap: `${process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'}/sitemap.xml`,
  }
}
