import { BRAND_CONFIG } from '@/lib/config'
import { Locale } from '@/lib/locale'
import { t } from '@/lib/translations'

interface HeadProps {
  params: Promise<{
    locale: string
  }>
}

export default async function Head({ params }: HeadProps) {
  const { locale } = await params
  const loc = locale as Locale
  const pageUrl = `${BRAND_CONFIG.siteUrl}/${loc}/info`

  const faqJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    inLanguage: loc,
    mainEntity: [
      {
        '@type': 'Question',
        name: t('info_hutter_title', loc),
        acceptedAnswer: {
          '@type': 'Answer',
          text: t('info_hutter_text', loc),
        },
      },
      {
        '@type': 'Question',
        name: t('info_delitzsch_title', loc),
        acceptedAnswer: {
          '@type': 'Answer',
          text: t('info_delitzsch_text', loc),
        },
      },
      {
        '@type': 'Question',
        name: t('info_polyglot_title', loc),
        acceptedAnswer: {
          '@type': 'Answer',
          text: t('info_polyglot_text', loc),
        },
      },
      {
        '@type': 'Question',
        name: t('info_besorah_title', loc),
        acceptedAnswer: {
          '@type': 'Answer',
          text: t('info_besorah_text', loc),
        },
      },
      {
        '@type': 'Question',
        name: t('info_tanaj_title', loc),
        acceptedAnswer: {
          '@type': 'Answer',
          text: t('info_tanaj_text', loc),
        },
      },
    ],
  }

  const pageJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: t('info_title', loc),
    description: t('site_meta_description', loc),
    url: pageUrl,
    inLanguage: loc,
    isPartOf: {
      '@type': 'WebSite',
      name: 'Shafan',
      url: BRAND_CONFIG.siteUrl,
    },
  }

  return (
    <>
      <script
        id={`jsonld-faq-info-${loc}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <script
        id={`jsonld-webpage-info-${loc}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(pageJsonLd) }}
      />
    </>
  )
}
