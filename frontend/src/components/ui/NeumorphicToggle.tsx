'use client'

import { ReactNode } from 'react'

interface NeumorphicToggleProps {
  enabled: boolean
  onClick: () => void
  label?: string
  ariaLabel: string
  icon?: ReactNode
  iconRenderer?: (enabled: boolean) => ReactNode
  size?: 'sm' | 'md'
}

export default function NeumorphicToggle({
  enabled,
  onClick,
  label,
  ariaLabel,
  icon,
  iconRenderer,
  size = 'md',
}: NeumorphicToggleProps) {
  const sizeClasses = {
    sm: {
      container: 'w-[32px] h-[32px]',
      inner: 'w-[12px] h-[12px]',
    },
    md: {
      container: 'w-[40px] h-[40px]',
      inner: 'w-[16px] h-[16px]',
    },
  }

  const currentSize = sizeClasses[size]

  return (
    <div className="flex flex-col items-center gap-1">
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
            ${currentSize.container}
            rounded-full
            transition-all duration-300 ease-out
            bg-background
            group-hover:scale-105
            ${enabled ? 'toggle-outer-pressed' : 'toggle-outer-raised'}
          `}
        >
          {/* Inner content - either custom icon renderer, single icon, or circle */}
          <div className="absolute inset-0 flex items-center justify-center">
            {iconRenderer ? (
              // Custom icon renderer (for complex cases like theme toggle)
              iconRenderer(enabled)
            ) : icon ? (
              // Single icon toggle
              <div className="transition-all duration-300">{icon}</div>
            ) : (
              // Simple toggle with circle
              <div
                className={`
                  ${currentSize.inner}
                  rounded-full
                  transition-all duration-300 ease-out
                  group-hover:scale-110
                  ${enabled ? 'bg-primary toggle-inner-dark' : 'bg-background toggle-inner-light'}
                `}
              />
            )}
          </div>
        </div>
      </button>
      {/* Label below button */}
      {label && (
        <span className="text-[10px] font-ui-hebrew font-bold text-secondary select-none">
          {label}
        </span>
      )}
    </div>
  )
}
