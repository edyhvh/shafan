'use client'

interface NikudToggleProps {
  enabled: boolean
  onToggle: () => void
}

// Hebrew word "nikud" with and without vowel points
const NIKUD_WITH_POINTS = 'נִקּוּד'
const NIKUD_WITHOUT_POINTS = 'נקוד'

export default function NikudToggle({ enabled, onToggle }: NikudToggleProps) {
  const label = enabled ? NIKUD_WITH_POINTS : NIKUD_WITHOUT_POINTS

  return (
    <button
      onClick={onToggle}
      className={`
        fixed top-7 right-6 z-40
        px-4 py-2 rounded-lg
        text-base font-medium
        transition-all duration-200
        cursor-pointer
        ${enabled ? 'liquid-glass-dark' : 'liquid-glass-dark-inactive'}
        text-white
        font-semibold
      `}
      aria-label="Toggle nikud"
      title="Toggle nikud"
    >
      <span className="font-ui-hebrew font-bold relative z-10 text-lg">
        {label}
      </span>
    </button>
  )
}
