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
      {/* Neumorphic toggle track */}
      <div
        className={`
          relative flex items-center
          rounded-full
          bg-background
          transition-all duration-300 ease-out
          group-hover:scale-105
          ${
            enabled
              ? 'shadow-[inset_4px_4px_8px_rgba(180,160,140,0.5),inset_-4px_-4px_8px_rgba(255,255,255,1)] group-hover:shadow-[inset_3px_3px_6px_rgba(180,160,140,0.4),inset_-3px_-3px_6px_rgba(255,255,255,0.95)]'
              : 'shadow-[6px_6px_12px_rgba(180,160,140,0.5),-6px_-6px_12px_rgba(255,255,255,1)] group-hover:shadow-[8px_8px_16px_rgba(180,160,140,0.6),-8px_-8px_16px_rgba(255,255,255,1)]'
          }
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
                ? 'left-0 right-0 justify-start pl-2.5 text-gray/80'
                : 'left-[42px] right-[8px] justify-end text-gray/60'
            }
          `}
        >
          {enabled ? labelLeft : labelRight}
        </span>

        {/* Neumorphic sliding knob */}
        <div
          className={`
            absolute top-[3px]
            w-[22px] h-[22px]
            rounded-full
            transition-all duration-300 ease-out
            group-hover:scale-110
            ${
              enabled
                ? 'right-[3px] bg-gray shadow-[inset_1px_1px_2px_rgba(0,0,0,0.3)] group-hover:shadow-[inset_1px_1px_3px_rgba(0,0,0,0.4)]'
                : 'left-[3px] bg-background shadow-[inset_2px_2px_4px_rgba(180,160,140,0.4),inset_-2px_-2px_4px_rgba(255,255,255,0.9)] group-hover:shadow-[inset_2px_2px_5px_rgba(180,160,140,0.5),inset_-2px_-2px_5px_rgba(255,255,255,1)]'
            }
          `}
        />
      </div>
    </button>
  )
}
