import type { Metadata } from 'next'
import { BRAND_CONFIG } from '@/lib/config'

const BRAND_NAME = BRAND_CONFIG.name
const BRAND_TITLE = `${BRAND_NAME} – Pure Hebrew for Scripture Study`
const SEO_TITLE = 'Shafan | Read the Hebrew Bible'
const SOCIAL_IMAGE_URL = BRAND_CONFIG.socialImageUrl

// Root layout - locale detection and redirects are handled by middleware.ts
export const metadata: Metadata = {
  title: SEO_TITLE,
  description:
    'Read the Hebrew Bible (Tanakh) and Besorah in Hebrew. Fast, clean, distraction-free study with Nikud controls and trusted texts. Start reading now.',
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
  openGraph: {
    title: BRAND_TITLE,
    description:
      'Read the Hebrew Bible (Tanakh) and Besorah in Hebrew. Fast, clean, distraction-free study with Nikud controls and trusted texts. Start reading now.',
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
      'Read the Hebrew Bible (Tanakh) and Besorah in Hebrew. Fast, clean, distraction-free study with Nikud controls and trusted texts. Start reading now.',
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
  return children
}
