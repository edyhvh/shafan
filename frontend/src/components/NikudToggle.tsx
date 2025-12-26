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
        px-3 py-1.5 rounded-md
        text-sm font-medium
        transition-all duration-200
        border
        cursor-pointer
        hover:scale-105 hover:shadow-md
        active:scale-95
        ${
          enabled
            ? 'bg-gray text-white border-gray hover:bg-gray/90'
            : 'bg-gray/10 text-gray/50 border-gray/15 hover:bg-gray/20 hover:text-gray/70'
        }
      `}
      style={{
        backgroundImage: enabled
          ? `
            linear-gradient(45deg, rgba(255,255,255,0.08) 25%, transparent 25%),
            linear-gradient(-45deg, rgba(255,255,255,0.08) 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, rgba(255,255,255,0.08) 75%),
            linear-gradient(-45deg, transparent 75%, rgba(255,255,255,0.08) 75%)
          `
          : `
            linear-gradient(45deg, rgba(51,51,51,0.06) 25%, transparent 25%),
            linear-gradient(-45deg, rgba(51,51,51,0.06) 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, rgba(51,51,51,0.06) 75%),
            linear-gradient(-45deg, transparent 75%, rgba(51,51,51,0.06) 75%)
          `,
        backgroundSize: '4px 4px',
        backgroundPosition: '0 0, 0 2px, 2px -2px, -2px 0px',
      }}
      aria-label="Toggle nikud"
      title="Toggle nikud"
    >
      <span className="font-ui-hebrew font-bold relative z-10">{label}</span>
    </button>
  )
}
