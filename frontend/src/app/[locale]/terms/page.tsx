import type { Metadata } from 'next'
import LegalPage from '@/components/LegalPage'
import { Locale } from '@/lib/locale'
import { BRAND_CONFIG } from '@/lib/config'
import { getLegalTitle, getLegalDescription } from '@/lib/legal-content'

const SOCIAL_IMAGE_URL = BRAND_CONFIG.socialImageUrl

interface PageProps {
  params: Promise<{
    locale: string
  }>
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { locale } = await params
  const loc = locale as Locale
  const canonicalUrl = `https://shafan.xyz/${loc}/terms`
  const title = getLegalTitle('terms', loc)
  const description = getLegalDescription('terms', loc)

  return {
    title,
    description,
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      title,
      description,
      type: 'website',
      url: canonicalUrl,
      siteName: 'Shafan',
      images: [
        {
          url: SOCIAL_IMAGE_URL,
          alt: title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [SOCIAL_IMAGE_URL],
    },
  }
}

export default async function TermsPage({ params }: PageProps) {
  const { locale } = await params
  const loc = locale as Locale

  return <LegalPage locale={loc} kind="terms" />
}
