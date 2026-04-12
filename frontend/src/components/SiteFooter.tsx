import Link from 'next/link'
import { Locale } from '@/lib/locale'
import { t } from '@/lib/translations'

type Props = {
  locale: Locale
}

export default function SiteFooter({ locale }: Props) {
  const isRTL = locale === 'he'

  return (
    <footer className="w-full border-t border-black/10 mt-16">
      <div
        className={`mx-auto max-w-5xl px-4 py-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between ${isRTL ? 'text-right' : 'text-left'}`}
        dir={isRTL ? 'rtl' : 'ltr'}
      >
        <p
          className={`text-sm text-black/60 ${isRTL ? 'font-hebrew' : 'font-ui-latin'}`}
        >
          {t('legal', locale)}
        </p>

        <div className="flex items-center gap-4">
          <Link
            href={`/${locale}/terms`}
            className={`text-sm underline underline-offset-2 text-black/70 hover:text-black transition-colors ${isRTL ? 'font-hebrew' : 'font-ui-latin'}`}
          >
            {t('terms', locale)}
          </Link>
          <Link
            href={`/${locale}/privacy`}
            className={`text-sm underline underline-offset-2 text-black/70 hover:text-black transition-colors ${isRTL ? 'font-hebrew' : 'font-ui-latin'}`}
          >
            {t('privacy', locale)}
          </Link>
        </div>
      </div>
    </footer>
  )
}
