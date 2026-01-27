import { DONATION_CONFIG } from '@/lib/config'
import { Locale } from '@/lib/locale'
import { t } from '@/lib/translations'
import type { Metadata } from 'next'

// Pre-render this page for all locales at build time
export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'es' }, { locale: 'he' }]
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>
}): Promise<Metadata> {
  const { locale } = await params
  const loc = locale as Locale
  const title = t('donate_meta_title', loc)
  const description = t('donate_meta_description', loc)
  const canonicalUrl = `https://shafan.xyz/${loc}/donate`

  return {
    title,
    description,
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      title,
      description,
      type: 'website',
      url: canonicalUrl,
      images: [
        {
          url: '/og-image.png',
          alt: title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: ['/og-image.png'],
    },
  }
}

// Inline SVG icons - rendered on server, no client JS needed

const GithubSponsorsIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 16 16" fill="currentColor">
    <path
      fillRule="evenodd"
      d="M4.25 2.5c-1.336 0-2.75 1.164-2.75 3 0 2.15 1.58 4.144 3.365 5.682A20.565 20.565 0 008 13.393a20.561 20.561 0 003.135-2.211C12.92 9.644 14.5 7.65 14.5 5.5c0-1.836-1.414-3-2.75-3-1.373 0-2.609.986-3.029 2.456a.75.75 0 01-1.442 0C6.859 3.486 5.623 2.5 4.25 2.5zM8 14.25l-.345.666-.002-.001-.006-.003-.018-.01a7.643 7.643 0 01-.31-.17 22.075 22.075 0 01-3.434-2.414C2.045 10.731 0 8.35 0 5.5 0 2.836 2.086 1 4.25 1 5.797 1 7.153 1.802 8 3.02 8.847 1.802 10.203 1 11.75 1 13.914 1 16 2.836 16 5.5c0 2.85-2.045 5.231-3.885 6.818a22.08 22.08 0 01-3.744 2.584l-.018.01-.006.003h-.002L8 14.25zm0 0l.345.666a.752.752 0 01-.69 0L8 14.25z"
    />
  </svg>
)

const CreditCardIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 16 16" fill="currentColor">
    <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v1h14V4a1 1 0 0 0-1-1H2zm13 4H1v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V7z" />
    <path d="M2 10a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-1z" />
  </svg>
)

const TelegramIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="currentColor"
    aria-hidden="true"
  >
    <path d="M9.993 15.43 9.66 20.06c.506 0 .726-.217.99-.478l2.37-2.28 4.91 3.595c.902.498 1.54.235 1.76-.832l3.2-15.02c.293-1.326-.48-1.845-1.33-1.53L2.1 9.18c-1.29.49-1.27 1.19-.22 1.51l4.86 1.52 11.28-7.12c.53-.35 1.01-.16.61.19L9.993 15.43z" />
  </svg>
)

interface PageProps {
  params: Promise<{
    locale: string
  }>
}

export default async function DonatePage({ params }: PageProps) {
  const { locale } = await params
  const loc = locale as Locale
  const isRTL = loc === 'he'

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div
          className={`space-y-6 text-gray ${isRTL ? 'font-hebrew' : 'font-ui-latin'}`}
        >
          {/* GitHub Sponsor */}
          <div className="flex items-center justify-center gap-3 text-lg">
            <div className="flex items-center gap-1">
              <GithubSponsorsIcon className="w-6 h-6" />
              <CreditCardIcon className="w-5 h-5" />
            </div>
            <span className="font-medium">Github Sponsor</span>
            <a
              href={DONATION_CONFIG.githubSponsor}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray/70 hover:text-black underline underline-offset-2 transition-colors"
            >
              @edyhvh
            </a>
          </div>
          <p className="text-sm text-gray/70">
            {t('donate_contact_prefix', loc)}{' '}
            <span className="inline-flex items-center gap-2">
              <span className="inline-flex items-center gap-1 font-medium text-gray">
                <TelegramIcon className="w-4 h-4" />
                {t('donate_telegram_label', loc)}
              </span>
              <a
                href="https://t.me/edyhvh"
                target="_blank"
                rel="noopener noreferrer"
                className="underline underline-offset-2 hover:text-black transition-colors"
              >
                @edyhvh
              </a>
            </span>
          </p>
        </div>
      </div>
    </div>
  )
}
