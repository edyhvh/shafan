import type { Metadata } from 'next'
import LegalPage from '@/components/LegalPage'
import { Locale } from '@/lib/locale'
import { BRAND_CONFIG } from '@/lib/config'

const SOCIAL_IMAGE_URL = BRAND_CONFIG.socialImageUrl

interface PageProps {
  params: Promise<{
    locale: string
  }>
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { locale } = await params
  const loc = locale as Locale
  const canonicalUrl = `https://shafan.xyz/${loc}/terms`

  return {
    title: 'Terms of Service of Shafan',
    description: 'Read the Terms of Service for Shafan.',
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      title: 'Terms of Service of Shafan',
      description: 'Read the Terms of Service for Shafan.',
      type: 'website',
      url: canonicalUrl,
      images: [
        {
          url: SOCIAL_IMAGE_URL,
          alt: 'Terms of Service of Shafan',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: 'Terms of Service of Shafan',
      description: 'Read the Terms of Service for Shafan.',
      images: [SOCIAL_IMAGE_URL],
    },
  }
}

export default async function TermsPage({ params }: PageProps) {
  const { locale } = await params
  const loc = locale as Locale

  return <LegalPage locale={loc} kind="terms" />
}
