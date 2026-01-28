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
import { Locale } from '@/lib/locale'
import { t } from '@/lib/translations'

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

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>
}): Promise<Metadata> {
  const brandName = 'shafan'
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
      'hebrew tanakh online',
      'besorah hebrew hutter',
      'nikud toggle',
      'hebrew bible study',
      'tanakh hebrew text',
      'besorah hebrew',
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
    openGraph: {
      title: brandName,
      description,
      type: 'website',
      url: canonicalUrl,
      siteName: 'Shafan',
      locale: openGraphLocaleMap[loc],
      images: [
        {
          url: 'https://shafan.xyz/og-image.png',
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
      images: ['https://shafan.xyz/og-image.png'],
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

  return (
    <html
      lang={locale}
      dir={dir}
      data-nikud="true"
      data-cantillation="false"
      data-text-source="delitzsch"
      data-sefer="true"
      data-theme="light"
      suppressHydrationWarning
    >
      <head>
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="shortcut icon" href="/icon.svg" />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var nikud = localStorage.getItem('shafan-nikud-enabled');
                  if (nikud !== null) {
                    document.documentElement.setAttribute('data-nikud', nikud);
                  }
                  var cantillation = localStorage.getItem('shafan-cantillation-enabled');
                  if (cantillation !== null) {
                    document.documentElement.setAttribute('data-cantillation', cantillation);
                  }
                  var textSource = localStorage.getItem('shafan-text-source');
                  if (textSource !== null) {
                    document.documentElement.setAttribute('data-text-source', textSource);
                  }
                  var sefer = localStorage.getItem('shafan-sefer-enabled');
                  if (sefer !== null) {
                    document.documentElement.setAttribute('data-sefer', sefer);
                  }
                  var theme = localStorage.getItem('shafan-theme');
                  if (theme !== null) {
                    document.documentElement.setAttribute('data-theme', theme);
                  }
                } catch(e) {}
              })();
            `,
          }}
        />
      </head>
      <body
        className={`${inter.variable} ${libreBodoni.variable} ${suezOne.variable} ${cardo.variable} ${assistant.variable} font-ui-latin antialiased`}
      >
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
        </div>
      </body>
    </html>
  )
}
