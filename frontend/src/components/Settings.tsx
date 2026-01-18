'use client'

import { useState } from 'react'
import { getLocaleFromPath } from '@/lib/locale'
import { usePathname } from 'next/navigation'
import { t } from '@/lib/translations'
import { SettingsIcon, CloseIcon } from './icons'
import TextSourceToggle from './TextSourceToggle'
import MobileModal from './ui/MobileModal'
import NeumorphicToggle from './ui/NeumorphicToggle'
import ThemeToggleIcon from './ui/ThemeToggleIcon'
import { useTextSource } from '@/hooks/useTextSource'
import { useNikud } from '@/hooks/useNikud'
import { useSefer } from '@/hooks/useSefer'
import { useCantillation } from '@/hooks/useCantillation'
import { useTheme } from '@/hooks/useTheme'
import { isNewTestament } from '@/lib/books'
import { parseBookFromPath } from '@/lib/paths'

interface SettingsProps {
  className?: string
  isOpen?: boolean // Controlled open state
  onOpen?: () => void // Callback when settings opens
  onClose?: () => void // Callback when settings should close
}

export default function Settings({
  className,
  isOpen: controlledIsOpen,
  onOpen,
  onClose,
}: SettingsProps) {
  const [internalIsOpen, setInternalIsOpen] = useState(false)
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)

  // Use controlled state if provided, otherwise use internal state
  const isOpen =
    controlledIsOpen !== undefined ? controlledIsOpen : internalIsOpen

  const handleOpen = () => {
    if (controlledIsOpen === undefined) {
      setInternalIsOpen(true)
    }
    onOpen?.() // Notify parent to close other dropdowns
  }

  const handleClose = () => {
    if (controlledIsOpen === undefined) {
      setInternalIsOpen(false)
    } else {
      onClose?.()
    }
  }

  const { textSource, toggleTextSource } = useTextSource()
  const { nikudEnabled, toggleNikud } = useNikud()
  const { seferEnabled, toggleSefer } = useSefer()
  const { cantillationEnabled, toggleCantillation } = useCantillation()
  const { theme, toggleTheme } = useTheme()

  // Extract book from pathname to determine if we should show certain toggles
  const bookName = parseBookFromPath(pathname)
  const showTextSourceToggle = bookName && isNewTestament(bookName)
  const showCantillationToggle = bookName && !isNewTestament(bookName)

  const modalContent = (
    <div className="bg-background rounded-2xl shadow-2xl border border-black/10 p-6 w-full max-w-sm max-h-full overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-black">
          {t('settings_title', locale)}
        </h2>
        <button
          onClick={handleClose}
          className="p-2 text-black/60 hover:text-black transition-colors rounded-full hover:bg-black/5"
          aria-label="Close settings"
        >
          <CloseIcon />
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
          <NeumorphicToggle
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
          <NeumorphicToggle
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
            <NeumorphicToggle
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
          <NeumorphicToggle
            enabled={theme === 'light'}
            onClick={toggleTheme}
            ariaLabel="Toggle theme"
            iconRenderer={(isLight) => <ThemeToggleIcon isLight={isLight} />}
          />
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

      {/* Settings Modal/Panel */}
      <MobileModal isOpen={isOpen} onClose={handleClose}>
        {modalContent}
      </MobileModal>
    </>
  )
}
