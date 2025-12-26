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
        px-4 py-2 rounded-sm
        text-base font-medium
        transition-all duration-200
        border
        cursor-pointer
        hover:scale-105 hover:shadow-md
        active:scale-95
        ${
          enabled
            ? 'bg-black text-white border-black hover:bg-gray-900'
            : 'bg-gray/10 text-gray/50 border-gray/15 hover:bg-gray/20 hover:text-gray/70'
        }
      `}
      style={enabled ? {
        boxShadow: '0 0 10px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
      } : undefined}
      aria-label="Toggle nikud"
      title="Toggle nikud"
    >
      <span className="font-ui-hebrew font-bold relative z-10 text-lg">{label}</span>
    </button>
  )
}
