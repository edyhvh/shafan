import type { Metadata } from 'next'

const BRAND_NAME = 'shafan'
const BRAND_TITLE = `${BRAND_NAME} – Pure Hebrew for Scripture Study`

// Root layout - locale detection and redirects are handled by middleware.ts
export const metadata: Metadata = {
  title: BRAND_NAME,
  description:
    'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
  metadataBase: new URL('https://shafan.xyz'),
  keywords: [
    'hebrew tanakh online',
    'nuevo testamento hebreo',
    'besorah hebreo',
    'brith hadashah',
    'besorah hebrew hutter',
    'hebrew delitzsch',
    'hebrew bible',
    'biblia hebrea',
    'torah',
    'tora',
    'hebrew bible study',
    'biblia estudio hebreo',
    'shafan',
    'tanaj hebreo',
    'traduccion nuevo testamento hebreo',
    'hutter',
    'delitzsch',
    'tanakh hebrew text',
    'besorah hebrew',
  ],
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    title: BRAND_TITLE,
    description:
      'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
    type: 'website',
    url: 'https://shafan.xyz',
    images: [
      {
        url: '/og-image.png',
        alt: BRAND_TITLE,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: BRAND_TITLE,
    description:
      'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
    images: ['/og-image.png'],
  },
  icons: {
    icon: '/icon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <link rel="icon" type="image/svg+xml" href="/icon.svg" />
      <link rel="shortcut icon" href="/icon.svg" />
      {children}
    </>
  )
}
