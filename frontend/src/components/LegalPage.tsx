import Link from 'next/link'
import { Fragment } from 'react'
import { Locale } from '@/lib/locale'
import { getLegalDoc, LegalKind } from '@/lib/legal-content'
import { t } from '@/lib/translations'

type Props = {
  locale: Locale
  kind: LegalKind
}

function renderInline(text: string) {
  const matches = text.matchAll(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g)
  const parts: Array<string | { href: string; label: string }> = []
  let last = 0

  for (const match of matches) {
    const full = match[0]
    const label = match[1]
    const href = match[2]
    const index = match.index ?? -1
    if (index < 0) continue

    if (index > last) {
      parts.push(text.slice(last, index))
    }

    parts.push({ href, label })
    last = index + full.length
  }

  if (last < text.length) {
    parts.push(text.slice(last))
  }

  return parts.map((part, index) => {
    if (typeof part === 'string') {
      return <Fragment key={index}>{part}</Fragment>
    }

    return (
      <a
        key={index}
        href={part.href}
        target="_blank"
        rel="noreferrer"
        className="underline underline-offset-2 hover:text-black"
      >
        {part.label}
      </a>
    )
  })
}

function renderMarkdownBlocks(body: string) {
  const lines = body.split('\n')
  const blocks: React.ReactNode[] = []

  let i = 0
  while (i < lines.length) {
    const raw = lines[i]
    const trimmed = raw.trim()

    if (!trimmed) {
      i += 1
      continue
    }

    if (trimmed.startsWith('## ')) {
      blocks.push(
        <h2
          key={`h2-${i}`}
          className="mt-8 mb-3 text-xl font-semibold text-black"
        >
          {trimmed.slice(3)}
        </h2>
      )
      i += 1
      continue
    }

    if (trimmed.startsWith('- ')) {
      const items: string[] = []
      while (i < lines.length && lines[i].trim().startsWith('- ')) {
        items.push(lines[i].trim().slice(2))
        i += 1
      }

      blocks.push(
        <ul
          key={`ul-${i}`}
          className="mb-4 list-disc ps-6 space-y-1 text-black/80"
        >
          {items.map((item, idx) => (
            <li key={`${idx}-${item.slice(0, 16)}`}>{renderInline(item)}</li>
          ))}
        </ul>
      )
      continue
    }

    const paragraphLines = [trimmed]
    i += 1
    while (i < lines.length) {
      const next = lines[i].trim()
      if (!next || next.startsWith('## ') || next.startsWith('- ')) break
      paragraphLines.push(next)
      i += 1
    }

    blocks.push(
      <p key={`p-${i}`} className="mb-4 leading-relaxed text-black/80">
        {renderInline(paragraphLines.join(' '))}
      </p>
    )
  }

  return blocks
}

export default function LegalPage({ locale, kind }: Props) {
  const isRTL = locale === 'he'
  const doc = getLegalDoc(kind, locale)

  return (
    <div className="max-w-3xl mx-auto px-4 pb-20">
      <section className={`mb-8 ${isRTL ? 'text-right' : 'text-left'}`}>
        <Link
          href={`/${locale}`}
          className="inline-flex rounded-full border border-black/20 px-4 py-1.5 text-xs uppercase tracking-[0.14em] text-black/70 hover:text-black hover:border-black/40 transition-colors"
        >
          {t('back_to_app', locale)}
        </Link>

        <h1
          className={`mt-4 text-3xl font-semibold text-black ${isRTL ? 'font-hebrew' : 'font-ui-latin'}`}
        >
          {doc.title}
        </h1>

        <div
          className={`mt-4 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs uppercase tracking-[0.12em] text-black/60 ${isRTL ? 'justify-end' : 'justify-start'}`}
        >
          {doc.effectiveDate && (
            <>
              <span>{t('legal_effective_date', locale)}</span>
              <span className="text-black/80">{doc.effectiveDate}</span>
            </>
          )}
          {doc.lastUpdated && (
            <>
              <span>{t('legal_last_updated', locale)}</span>
              <span className="text-black/80">{doc.lastUpdated}</span>
            </>
          )}
        </div>
      </section>

      <div className="h-px w-full bg-black/10 mb-8" />

      <section
        className={`${isRTL ? 'text-right' : 'text-left'}`}
        dir={isRTL ? 'rtl' : 'ltr'}
      >
        {renderMarkdownBlocks(doc.body)}
      </section>
    </div>
  )
}
