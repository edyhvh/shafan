'use client'

import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { useNikud } from '@/hooks/useNikud'
import { useCantillation } from '@/hooks/useCantillation'
import { useTextSource } from '@/hooks/useTextSource'
import { useSefer } from '@/hooks/useSefer'
import { useTheme } from '@/hooks/useTheme'
import { usePathname } from 'next/navigation'
import { isNewTestament, AVAILABLE_BOOKS, type BookName } from '@/lib/books'
import { useScrollState } from '@/hooks/useScrollState'
import TextSourceToggle from './TextSourceToggle'
import SunIcon from './icons/SunIcon'

interface ToggleButtonProps {
  enabled: boolean
  onClick: () => void
  label: string
  ariaLabel: string
  topPosition: string
  animationDelay?: string
}

/**
 * Reusable toggle button component for reading controls
 */
function ToggleButton({
  enabled,
  onClick,
  label,
  ariaLabel,
  topPosition,
  animationDelay = '0ms',
}: ToggleButtonProps) {
  return (
    <div
      className={`!fixed right-5 z-40 flex flex-col items-center gap-1 transition-all duration-300 ease-out animate-in fade-in slide-in-from-right-4`}
      style={{ top: topPosition, animationDelay }}
    >
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

/**
 * Theme toggle button component - uses sun icon instead of circle
 */
function ThemeToggle({
  enabled,
  onClick,
  ariaLabel,
  topPosition,
  animationDelay = '0ms',
}: Omit<ToggleButtonProps, 'label'>) {
  return (
    <div
      className={`!fixed right-5 z-40 flex flex-col items-center transition-all duration-300 ease-out animate-in fade-in slide-in-from-right-4`}
      style={{ top: topPosition, animationDelay }}
    >
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
          {/* Sun icon - adapts to theme */}
          <div className="absolute inset-0 flex items-center justify-center">
            <SunIcon
              className="
                transition-all duration-300 ease-out
                group-hover:scale-110
                text-primary
              "
            />
          </div>
        </div>
      </button>
    </div>
  )
}

/**
 * Component for reading controls (nikud and text source toggles)
 * Positioned as fixed controls at the top, always visible
 */
export default function ReadingControls() {
  const { nikudEnabled, toggleNikud } = useNikud()
  const { cantillationEnabled, toggleCantillation } = useCantillation()
  const { textSource, toggleTextSource } = useTextSource()
  const { seferEnabled, toggleSefer } = useSefer()
  const { theme, toggleTheme } = useTheme()
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)

  // Import scroll state hook
  const { shouldHideForContent } = useScrollState()

  // Extract bookId from pathname to check if it's New Testament
  const pathParts = pathname.split('/')
  const bookIndex = pathParts.indexOf('book')
  const bookId =
    bookIndex !== -1 && pathParts[bookIndex + 1]
      ? pathParts[bookIndex + 1]
      : null
  const bookName =
    bookId && AVAILABLE_BOOKS.includes(bookId as BookName)
      ? (bookId as BookName)
      : null
  const showTextSourceToggle = bookName && isNewTestament(bookName)
  const showCantillationToggle = bookName && !isNewTestament(bookName)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Hide controls when scrolled down (like navbar)
  if (shouldHideForContent) {
    return null
  }

  const controlsContent = (
    <>
      {/* Text Source Toggle (Hutter/Delitzsch) - Only for New Testament */}
      {showTextSourceToggle && (
        <TextSourceToggle
          enabled={textSource === 'delitzsch'}
          onToggle={toggleTextSource}
          position="top-6 right-5"
          className="transition-all duration-300 ease-out animate-in fade-in slide-in-from-right-4"
        />
      )}

      {/* Nikud Button - Always shown, positioned below text source toggle if both are visible */}
      {/* Text source ends at 56px, so Nikud starts at 72px with 16px gap */}
      <ToggleButton
        enabled={nikudEnabled}
        onClick={toggleNikud}
        label="נקוד"
        ariaLabel="Toggle nikud (vowel points)"
        topPosition={showTextSourceToggle ? '72px' : '24px'}
        animationDelay="50ms"
      />

      {/* Sefer Button - Always shown, positioned below nikud button */}
      {/* Each button component is ~56px tall (40px button + 4px gap + 12px label) */}
      {/* Using 64px spacing between button tops for consistent visual separation */}
      <ToggleButton
        enabled={seferEnabled}
        onClick={toggleSefer}
        label="ספר"
        ariaLabel="Toggle sefer (continuous paragraph) display"
        topPosition={showTextSourceToggle ? '136px' : '88px'}
        animationDelay="100ms"
      />

      {/* Cantillation Button - Only shown for Tanaj books, positioned below sefer button */}
      {showCantillationToggle && (
        <ToggleButton
          enabled={cantillationEnabled}
          onClick={toggleCantillation}
          label="טעמים"
          ariaLabel="Toggle cantillation marks"
          topPosition={showTextSourceToggle ? '200px' : '152px'}
          animationDelay="150ms"
        />
      )}

      {/* Theme Toggle Button - Always shown, positioned below the last button */}
      <ThemeToggle
        enabled={theme === 'light'}
        onClick={toggleTheme}
        ariaLabel="Toggle theme (light/dark)"
        topPosition={
          showCantillationToggle
            ? showTextSourceToggle
              ? '264px'
              : '216px'
            : showTextSourceToggle
              ? '200px'
              : '152px'
        }
        animationDelay="200ms"
      />
    </>
  )

  // Use portal to render controls directly in body, outside any scrollable containers
  if (!mounted) return null

  // Hide floating controls on mobile - they're now in the settings panel
  // Use a more reliable mobile detection
  if (typeof window !== 'undefined') {
    const isMobile =
      window.innerWidth < 768 || window.matchMedia('(max-width: 767px)').matches
    if (isMobile) return null
  }

  return createPortal(controlsContent, document.body)
}
