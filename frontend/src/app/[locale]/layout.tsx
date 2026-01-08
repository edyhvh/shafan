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
  params: _params,
}: {
  params: Promise<{ locale: string }>
}): Promise<Metadata> {
  return {
    title: 'Shafan',
    description: "Read Elias Hutter's Hebrew Besorah Translation",
    keywords: [
      'Hebrew',
      'New Testament',
      'Bible',
      'Elias Hutter',
      'Shafan',
      'Besorah',
      'בשורה',
      'Yeshua',
      'Mashiaj',
      'Mashiach',
      'Tanaj',
      'Tanakh',
      'משיח',
      'ישוע',
      'ישועה',
    ],
    openGraph: {
      title: 'Shafan',
      description: "Read Elias Hutter's Hebrew Besorah Translation",
      type: 'website',
    },
    twitter: {
      card: 'summary',
      title: 'Shafan',
      description: "Read Elias Hutter's Hebrew Besorah Translation",
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
      data-text-source="hutter"
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
                  var textSource = localStorage.getItem('shafan-text-source');
                  if (textSource !== null) {
                    document.documentElement.setAttribute('data-text-source', textSource);
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

          {/* Correction Warning */}
          <CorrectionWarning />

          {/* Main content with top padding for floating navbar */}
          <main className="w-full pt-32 pb-16">{children}</main>
        </div>
      </body>
    </html>
  )
}
