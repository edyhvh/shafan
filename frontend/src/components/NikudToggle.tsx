'use client'

interface NikudToggleProps {
  enabled: boolean
  onToggle: () => void
}

// Hebrew word "nikud" - displayed in the toggle
const NIKUD_LABEL = 'נקוד'

export default function NikudToggle({ enabled, onToggle }: NikudToggleProps) {
  return (
    <button
      onClick={onToggle}
      className="fixed top-6 right-5 z-40 cursor-pointer group"
      aria-label="Toggle nikud"
      aria-pressed={enabled}
      title="Toggle nikud"
    >
      {/* Retro toggle track */}
      <div
        className={`
          relative flex items-center
          w-[72px] h-[32px]
          rounded-full
          border-2
          transition-all duration-300 ease-out
          ${
            enabled
              ? 'bg-gray border-gray'
              : 'bg-white border-gray/30 group-hover:border-gray/50'
          }
        `}
      >
        {/* Label text */}
        <span
          className={`
            absolute inset-0 flex items-center
            font-ui-hebrew font-semibold text-sm
            transition-all duration-300 ease-out
            select-none
            ${enabled ? 'justify-start pl-2.5 text-white/90' : 'justify-end pr-2.5 text-gray/60'}
          `}
        >
          {NIKUD_LABEL}
        </span>

        {/* Sliding knob */}
        <div
          className={`
            absolute top-[3px]
            w-[22px] h-[22px]
            rounded-full
            transition-all duration-300 ease-out
            shadow-[0_1px_3px_rgba(0,0,0,0.2)]
            ${
              enabled
                ? 'right-[3px] bg-white'
                : 'left-[3px] bg-gray/40 group-hover:bg-gray/60'
            }
          `}
        />
      </div>
    </button>
  )
}
