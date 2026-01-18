'use client'

interface NikudToggleProps {
  enabled: boolean
  onToggle: () => void
  position?: string
  className?: string
}

// Hebrew word "nikud" - displayed in the toggle
const NIKUD_LABEL = 'נקוד'

export default function NikudToggle({
  enabled,
  onToggle,
  position,
  className = '',
}: NikudToggleProps) {
  return (
    <button
      onClick={onToggle}
      className={`${position ? `fixed ${position} z-40` : ''} cursor-pointer group ${className}`}
      aria-label="Toggle nikud"
      aria-pressed={enabled}
      title="Toggle nikud"
    >
      {/* Neumorphic toggle track */}
      <div
        className={`
          relative flex items-center
          rounded-full
          bg-background
          ${enabled ? 'toggle-outer-pressed' : 'toggle-outer-raised'}
        `}
        style={{ width: '100px', height: '32px' }}
      >
        {/* Label text */}
        <span
          dir="rtl"
          className={`
            absolute top-0 bottom-0 flex items-center
            font-ui-hebrew font-semibold text-sm
            select-none pointer-events-none
            ${
              enabled
                ? 'left-0 right-0 justify-start pl-2.5 text-secondary'
                : 'left-[30px] right-[8px] justify-end text-muted'
            }
          `}
        >
          {NIKUD_LABEL}
        </span>

        {/* Sliding knob - smooth animation */}
        <div
          className={`
            absolute top-[5px]
            w-[22px] h-[22px]
            rounded-full
            transition-[left,right] duration-500 ease-[cubic-bezier(0.4,0,0.2,1)]
            ${enabled ? 'right-[3px] left-auto bg-primary toggle-inner-dark' : 'left-[3px] right-auto bg-background toggle-inner-light'}
          `}
        />
      </div>
    </button>
  )
}
