'use client'

import { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { getLocaleFromPath } from '@/lib/locale'
import { usePathname } from 'next/navigation'
import { t } from '@/lib/translations'
import { SettingsIcon } from './icons'
import TextSourceToggle from './TextSourceToggle'
import { useTextSource } from '@/hooks/useTextSource'
import { useNikud } from '@/hooks/useNikud'
import { useSefer } from '@/hooks/useSefer'
import { useCantillation } from '@/hooks/useCantillation'
import { useTheme } from '@/hooks/useTheme'
import { isNewTestament, AVAILABLE_BOOKS, type BookName } from '@/lib/books'

interface SettingsProps {
  className?: string
  onOpen?: () => void // Callback when settings opens
  closeTrigger?: number // When this changes, close settings
}

// Inline toggle button matching desktop ToggleButton style
function InlineToggleButton({
  enabled,
  onClick,
  label,
  ariaLabel,
}: {
  enabled: boolean
  onClick: () => void
  label: string
  ariaLabel: string
}) {
  return (
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={onClick}
        className="cursor-pointer group relative"
        aria-label={ariaLabel}
        aria-pressed={enabled}
        title={ariaLabel}
      >
        {/* Neumorphic outer ring */}
        <div
          className={`
            w-[40px] h-[40px]
            rounded-full
            transition-all duration-300 ease-out
            bg-background
            group-hover:scale-105
            ${enabled ? 'toggle-outer-pressed' : 'toggle-outer-raised'}
          `}
        >
          {/* Inner circle - black when ON */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className={`
                w-[16px] h-[16px]
                rounded-full
                transition-all duration-300 ease-out
                group-hover:scale-110
                ${enabled ? 'bg-primary toggle-inner-dark' : 'bg-background toggle-inner-light'}
              `}
            />
          </div>
        </div>
      </button>
      {/* Label below button */}
      <span className="text-[10px] font-ui-hebrew font-bold text-secondary select-none">
        {label}
      </span>
    </div>
  )
}

// Inline theme toggle matching desktop ThemeToggle style
function InlineThemeToggle({
  enabled,
  onClick,
  ariaLabel,
}: {
  enabled: boolean
  onClick: () => void
  ariaLabel: string
}) {
  return (
    <div className="flex flex-col items-center">
      <button
        onClick={onClick}
        className="cursor-pointer group relative"
        aria-label={ariaLabel}
        aria-pressed={enabled}
        title={ariaLabel}
      >
        {/* Neumorphic outer ring */}
        <div
          className={`
            w-[40px] h-[40px]
            rounded-full
            transition-all duration-300 ease-out
            bg-background
            group-hover:scale-105
            ${enabled ? 'toggle-outer-pressed' : 'toggle-outer-raised'}
          `}
        >
          {/* Sun icon - visible when light theme is enabled */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className={`transition-all duration-300 ${
                enabled ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
              }`}
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-primary"
              >
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
              </svg>
            </div>

            {/* Moon icon - visible when dark theme is enabled */}
            <div
              className={`absolute inset-0 flex items-center justify-center transition-all duration-300 ${
                !enabled ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
              }`}
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-primary"
              >
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
              </svg>
            </div>
          </div>
        </div>
      </button>
    </div>
  )
}

export default function Settings({
  className,
  onOpen,
  closeTrigger,
}: SettingsProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)
  const prevCloseTriggerRef = useRef<number | undefined>(undefined)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleOpen = () => {
    setIsOpen(true)
    onOpen?.() // Notify parent to close other dropdowns
  }

  // Close settings when closeTrigger changes (increments)
  useEffect(() => {
    if (
      closeTrigger !== undefined &&
      closeTrigger !== prevCloseTriggerRef.current &&
      isOpen
    ) {
      setIsOpen(false)
    }
    if (closeTrigger !== undefined) {
      prevCloseTriggerRef.current = closeTrigger
    }
  }, [closeTrigger, isOpen])

  const { textSource, toggleTextSource } = useTextSource()
  const { nikudEnabled, toggleNikud } = useNikud()
  const { seferEnabled, toggleSefer } = useSefer()
  const { cantillationEnabled, toggleCantillation } = useCantillation()
  const { theme, toggleTheme } = useTheme()

  // Extract book from pathname to determine if we should show certain toggles
  const bookMatch = pathname.match(/\/book\/([^/]+)/)
  const bookId = bookMatch ? bookMatch[1] : null
  const bookName =
    bookId && AVAILABLE_BOOKS.includes(bookId as BookName)
      ? (bookId as BookName)
      : null
  const showTextSourceToggle = bookName && isNewTestament(bookName)
  const showCantillationToggle = bookName && !isNewTestament(bookName)

  const modalContent = (
    <div
      className="fixed top-24 left-0 right-0 bottom-0 z-[1000]"
      onClick={(e) => {
        // Close if clicking the backdrop (not the modal content)
        if (e.target === e.currentTarget) {
          setIsOpen(false)
        }
      }}
    >
      {/* Backdrop - covers the entire modal area */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in duration-300" />

      {/* Modal Content - centered in the modal area */}
      <div className="relative z-10 flex justify-center items-start pt-4 px-4 h-full animate-in fade-in slide-in-from-top-4 duration-300 ease-out">
        <div
          className="bg-background rounded-2xl shadow-2xl border border-black/10 p-6 w-full max-w-sm max-h-full overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-black">
              {t('settings_title', locale)}
            </h2>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 text-black/60 hover:text-black transition-colors rounded-full hover:bg-black/5"
              aria-label="Close settings"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          <div className="space-y-4">
            {/* Text Source Toggle - Only for New Testament */}
            {showTextSourceToggle && (
              <div className="flex items-center justify-between py-2">
                <label className="text-sm font-medium text-black/80">
                  {locale === 'he' ? 'מקור הטקסט' : 'Text Source'}
                </label>
                <TextSourceToggle
                  enabled={textSource === 'delitzsch'}
                  onToggle={toggleTextSource}
                  position=""
                />
              </div>
            )}

            {/* Nikud Toggle */}
            <div className="flex items-center justify-between py-2">
              <label className="text-sm font-medium text-black/80">
                {t('nikud', locale)}
              </label>
              <InlineToggleButton
                enabled={nikudEnabled}
                onClick={toggleNikud}
                label="נקוד"
                ariaLabel="Toggle nikud (vowel points)"
              />
            </div>

            {/* Sefer Toggle */}
            <div className="flex items-center justify-between py-2">
              <label className="text-sm font-medium text-black/80">
                {locale === 'he' ? 'ספר' : 'Sefer'}
              </label>
              <InlineToggleButton
                enabled={seferEnabled}
                onClick={toggleSefer}
                label="ספר"
                ariaLabel="Toggle sefer (continuous paragraph) display"
              />
            </div>

            {/* Cantillation Toggle - Only for Tanaj */}
            {showCantillationToggle && (
              <div className="flex items-center justify-between py-2">
                <label className="text-sm font-medium text-black/80">
                  {locale === 'he' ? 'טעמים' : 'Cantillation'}
                </label>
                <InlineToggleButton
                  enabled={cantillationEnabled}
                  onClick={toggleCantillation}
                  label="טעמים"
                  ariaLabel="Toggle cantillation marks"
                />
              </div>
            )}

            {/* Theme Toggle */}
            <div className="flex items-center justify-between py-2">
              <label className="text-sm font-medium text-black/80">
                {locale === 'he' ? 'ערכת נושא' : 'Theme'}
              </label>
              <InlineThemeToggle
                enabled={theme === 'light'}
                onClick={toggleTheme}
                ariaLabel="Toggle theme"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Settings Button */}
      <button
        onClick={handleOpen}
        className={`p-2.5 text-black/70 hover:text-black transition-all duration-200 rounded-full hover:bg-black/5 ${className}`}
        aria-label="Open settings"
      >
        <SettingsIcon />
      </button>

      {/* Settings Modal/Panel - Rendered in portal */}
      {mounted && isOpen && createPortal(modalContent, document.body)}
    </>
  )
}
