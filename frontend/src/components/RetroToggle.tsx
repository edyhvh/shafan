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
  className?: string
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
  className = '',
}: RetroToggleProps) {
  return (
    <button
      onClick={onToggle}
      className={`${position ? `fixed ${position} z-40` : ''} cursor-pointer group ${className}`}
      aria-label={ariaLabel}
      aria-pressed={enabled}
      title={title || ariaLabel}
    >
      {/* Neumorphic toggle track */}
      <div
        className={`
          relative flex items-center
          rounded-full
          bg-background
          transition-all duration-300 ease-out
          group-hover:scale-105
          ${enabled ? 'toggle-outer-pressed' : 'toggle-outer-raised'}
        `}
        style={{ width: '100px', height: '32px' }}
      >
        {/* Label text */}
        <span
          dir={textDirection}
          className={`
            absolute top-0 bottom-0 flex items-center
            ${labelFontClass} font-semibold text-sm
            transition-all duration-300 ease-out
            select-none
            ${
              enabled
                ? 'left-0 right-0 justify-start pl-2.5 text-secondary'
                : 'left-[42px] right-[8px] justify-end text-muted'
            }
          `}
        >
          {enabled ? labelLeft : labelRight}
        </span>

        {/* Neumorphic sliding knob */}
        <div
          className={`
            absolute top-[5px]
            w-[22px] h-[22px]
            rounded-full
            transition-all duration-300 ease-out
            group-hover:scale-110
            ${enabled ? 'right-[3px] bg-primary toggle-inner-dark' : 'left-[3px] bg-background toggle-inner-light'}
          `}
        />
      </div>
    </button>
  )
}
