'use client'

interface RetroToggleProps {
  enabled: boolean
  onToggle: () => void
  labelLeft: string
  labelRight: string
  position: string
  ariaLabel: string
  title?: string
  labelFontClass?: string
  textDirection?: 'ltr' | 'rtl' | 'auto'
}

/**
 * Reusable retro-style toggle component
 * Can be used for any binary preference toggle
 */
export default function RetroToggle({
  enabled,
  onToggle,
  labelLeft,
  labelRight,
  position,
  ariaLabel,
  title,
  labelFontClass = 'font-ui-latin',
  textDirection = 'auto',
}: RetroToggleProps) {
  return (
    <button
      onClick={onToggle}
      className={`${position ? `fixed ${position} z-40` : ''} cursor-pointer group`}
      aria-label={ariaLabel}
      aria-pressed={enabled}
      title={title || ariaLabel}
    >
      {/* Retro toggle track */}
      <div
        className={`
          relative flex items-center
          rounded-full
          border-2
          transition-all duration-300 ease-out
          ${
            enabled
              ? 'bg-gray border-gray'
              : 'bg-white border-gray/30 group-hover:border-gray/50'
          }
        `}
        style={{ width: '100px', height: '32px' }}
      >
        {/* Label text */}
        <span
          dir={textDirection}
          className={`
            absolute inset-0 flex items-center
            ${labelFontClass} font-semibold text-sm
            transition-all duration-300 ease-out
            select-none
            ${enabled ? 'justify-start pl-2.5 text-white/90' : 'justify-end pr-2.5 text-gray/60'}
          `}
        >
          {enabled ? labelLeft : labelRight}
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
