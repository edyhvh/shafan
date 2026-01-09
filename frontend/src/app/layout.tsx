import type { Metadata } from 'next'

// Root layout - locale detection and redirects are handled by middleware.ts
export const metadata: Metadata = {
  title: 'Shafan',
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
