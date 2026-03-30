'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import type { TTHFootnote } from '@/lib/types'

interface FootnoteTooltipProps {
  footnote: TTHFootnote
}

const SUPERSCRIPT_DIGIT_MAP: Record<string, string> = {
  '⁰': '0',
  '¹': '1',
  '²': '2',
  '³': '3',
  '⁴': '4',
  '⁵': '5',
  '⁶': '6',
  '⁷': '7',
  '⁸': '8',
  '⁹': '9',
}

function normalizeMarker(marker: string): string {
  return marker.replace(
    /[⁰¹²³⁴⁵⁶⁷⁸⁹]/g,
    (digit) => SUPERSCRIPT_DIGIT_MAP[digit] ?? digit
  )
}

export default function FootnoteTooltip({ footnote }: FootnoteTooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const tooltipRef = useRef<HTMLSpanElement>(null)
  const displayMarker = normalizeMarker(footnote.marker)

  const hide = useCallback(() => setIsVisible(false), [])

  // Close on click outside
  useEffect(() => {
    if (!isVisible) return
    const handleClickOutside = (e: MouseEvent) => {
      if (
        triggerRef.current &&
        !triggerRef.current.contains(e.target as Node) &&
        tooltipRef.current &&
        !tooltipRef.current.contains(e.target as Node)
      ) {
        hide()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isVisible, hide])

  // Close on Escape
  useEffect(() => {
    if (!isVisible) return
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') hide()
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isVisible, hide])

  return (
    <span className="relative inline">
      <button
        ref={triggerRef}
        onClick={() => setIsVisible(!isVisible)}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        className="cursor-pointer text-[0.55em] align-super text-[#4a7c59] dark:text-[#6b9b7a] font-bold tabular-nums hover:text-[#3d6b4a] transition-colors duration-150 leading-none"
        aria-label={`Footnote ${footnote.number}: ${footnote.word}`}
        type="button"
      >
        {displayMarker}
      </button>
      {isVisible && (
        <span
          ref={tooltipRef}
          role="tooltip"
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 block w-64 max-w-[85vw] p-3 rounded-lg bg-background border border-black/10 shadow-lg text-sm text-primary"
          onMouseEnter={() => setIsVisible(true)}
          onMouseLeave={() => setIsVisible(false)}
        >
          <span className="mb-1 block font-semibold text-xs text-secondary">
            {footnote.word}
          </span>
          <span className="block text-xs leading-relaxed">
            {footnote.explanation}
          </span>
          {/* Tooltip arrow */}
          <span
            className="absolute top-full left-1/2 block h-0 w-0 -translate-x-1/2 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[6px] border-t-black/10"
            aria-hidden="true"
          />
        </span>
      )}
    </span>
  )
}
