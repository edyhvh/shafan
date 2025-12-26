import type { Metadata } from 'next'

// Root layout - redirects are handled by middleware
export const metadata: Metadata = {
  title: 'Shafan - ש',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <link rel="icon" type="image/x-icon" href="/favicon.ico" />
      <link rel="shortcut icon" href="/favicon.ico" />
      {children}
    </>
  )
}
