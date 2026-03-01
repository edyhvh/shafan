import type { Metadata } from 'next'
import { BRAND_CONFIG } from '@/lib/config'

const BRAND_NAME = BRAND_CONFIG.name
const BRAND_TITLE = `${BRAND_NAME} – Pure Hebrew for Scripture Study`
const SOCIAL_IMAGE_URL = BRAND_CONFIG.socialImageUrl

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
    siteName: 'Shafan',
    images: [
      {
        url: SOCIAL_IMAGE_URL,
        width: 1200,
        height: 630,
        alt: BRAND_TITLE,
        type: 'image/png',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: BRAND_TITLE,
    description:
      'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
    images: [SOCIAL_IMAGE_URL],
    site: '@shafanxyz',
    creator: '@shafanxyz',
  },
  icons: {
    icon: '/icon.png?v=2',
    shortcut: '/icon.png?v=2',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <link rel="icon" type="image/png" href="/icon.png?v=2" />
      <link rel="shortcut icon" href="/icon.png?v=2" />
      {children}
    </>
  )
}
