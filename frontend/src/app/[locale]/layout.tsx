import type { Metadata } from 'next'
import {
  Inter,
  Libre_Bodoni,
  Suez_One,
  Cardo,
  Assistant,
} from 'next/font/google'
import '../globals.css'
import Navbar from '@/components/Navbar'
import CorrectionWarning from '@/components/CorrectionWarning'
import SiteFooter from '@/components/SiteFooter'
import InitialPreferencesSync from '../../components/InitialPreferencesSync'
import { Locale } from '@/lib/locale'
import { t } from '@/lib/translations'
import { BRAND_CONFIG } from '@/lib/config'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  weight: ['400', '500', '600'],
})

const libreBodoni = Libre_Bodoni({
  subsets: ['latin'],
  variable: '--font-libre-bodoni',
  weight: ['700'],
})

const suezOne = Suez_One({
  subsets: ['hebrew'],
  variable: '--font-suez-one',
  weight: ['400'],
})

const cardo = Cardo({
  subsets: ['latin', 'greek'],
  variable: '--font-cardo',
  weight: ['400', '700'],
})

const assistant = Assistant({
  subsets: ['hebrew'],
  variable: '--font-assistant',
  weight: ['400', '600'],
})

const SOCIAL_IMAGE_URL = BRAND_CONFIG.socialImageUrl

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>
}): Promise<Metadata> {
  const brandName = 'Shafan | Read the Hebrew Bible'
  const { locale } = await params
  const loc = (locale || 'he') as Locale
  const description = t('site_meta_description', loc)
  const canonicalUrl = `https://shafan.xyz/${loc}`
  const openGraphLocaleMap: Record<Locale, string> = {
    en: 'en_US',
    es: 'es_ES',
    he: 'he_IL',
  }

  return {
    title: brandName,
    description,
    metadataBase: new URL('https://shafan.xyz'),
    keywords: [
      'hebrew bible',
      'hebrew bible study',
      'tanakh hebrew text',
      'tanaj hebreo',
      'hebrew tanakh online',
      'besorah hebrew',
      'besorah hebreo',
      'hebrew new testament',
      'delitzsch hebrew translation',
      'hutter hebrew new testament',
    ],
    robots: {
      index: true,
      follow: true,
    },
    alternates: {
      canonical: canonicalUrl,
      languages: {
        en: 'https://shafan.xyz/en',
        es: 'https://shafan.xyz/es',
        he: 'https://shafan.xyz/he',
      },
    },
    authors: [{ name: BRAND_CONFIG.authorName, url: BRAND_CONFIG.authorUrl }],
    creator: BRAND_CONFIG.authorName,
    publisher: 'Shafan',
    openGraph: {
      title: brandName,
      description,
      type: 'website',
      url: canonicalUrl,
      siteName: 'Shafan',
      locale: openGraphLocaleMap[loc],
      images: [
        {
          url: SOCIAL_IMAGE_URL,
          width: 1200,
          height: 630,
          alt: brandName,
          type: 'image/png',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: brandName,
      description,
      images: [SOCIAL_IMAGE_URL],
      site: '@shafanxyz',
      creator: '@shafanxyz',
    },
  }
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}) {
  const resolvedParams = await params
  const locale = resolvedParams.locale || 'he'
  const dir = locale === 'he' ? 'rtl' : 'ltr'
  const websiteJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'Shafan',
    url: BRAND_CONFIG.siteUrl,
    inLanguage: locale,
  }
  const organizationJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'Shafan',
    url: BRAND_CONFIG.siteUrl,
    logo: BRAND_CONFIG.logoUrl,
    sameAs: [
      `https://x.com/${BRAND_CONFIG.twitterHandle.replace('@', '')}`,
      BRAND_CONFIG.githubUrl,
      BRAND_CONFIG.youtubeUrl,
    ],
  }
  const personJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: BRAND_CONFIG.authorName,
    url: BRAND_CONFIG.authorUrl,
    sameAs: [
      BRAND_CONFIG.authorUrl,
      `https://x.com/${BRAND_CONFIG.twitterHandle.replace('@', '')}`,
      BRAND_CONFIG.youtubeUrl,
    ],
  }

  return (
    <html
      lang={locale}
      dir={dir}
      data-scroll-behavior="smooth"
      data-nikud="true"
      data-cantillation="false"
      data-text-source="delitzsch"
      data-sefer="true"
      data-tth="false"
      data-theme="light"
      suppressHydrationWarning
    >
      <head>
        <script
          id={`jsonld-website-${locale}`}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd) }}
        />
        <script
          id={`jsonld-organization-${locale}`}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(organizationJsonLd),
          }}
        />
        <script
          id={`jsonld-person-${locale}`}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(personJsonLd) }}
        />
      </head>
      <body
        className={`${inter.variable} ${libreBodoni.variable} ${suezOne.variable} ${cardo.variable} ${assistant.variable} font-ui-latin antialiased`}
      >
        <InitialPreferencesSync />
        <div className="min-h-screen bg-background">
          {/* Floating Navbar */}
          <Navbar />

          {/* Correction Warning - Desktop: floating left, Mobile: below navbar */}
          <div className="fixed top-4 left-4 z-30 hidden md:block">
            <CorrectionWarning />
          </div>
          <div className="fixed top-24 left-4 right-4 z-30 md:hidden">
            <CorrectionWarning />
          </div>

          {/* Main content with top padding for floating navbar */}
          <main className="w-full pt-32 pb-16">{children}</main>

          <SiteFooter locale={locale as Locale} />
        </div>
      </body>
    </html>
  )
}
