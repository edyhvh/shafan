import { redirect } from 'next/navigation'

interface PageProps {
  params: Promise<{
    locale: string
  }>
}

export default async function HomePage({ params }: PageProps) {
  const resolvedParams = await params
  const { locale } = resolvedParams

  // Redirect to John chapter 1
  redirect(`/${locale}/book/john/chapter/1`)
}
