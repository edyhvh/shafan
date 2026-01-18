'use client'

import RetroToggle from './RetroToggle'

interface TextSourceToggleProps {
  enabled: boolean
  onToggle: () => void
  position?: string
  className?: string
}

export default function TextSourceToggle({
  enabled,
  onToggle,
  position,
  className,
}: TextSourceToggleProps) {
  // If position is empty string, pass undefined to disable fixed positioning
  const togglePosition =
    position === '' ? undefined : (position ?? 'top-[88px] right-5')

  return (
    <RetroToggle
      enabled={enabled}
      onToggle={onToggle}
      labelLeft="Delitzsch"
      labelRight="Hutter"
      position={togglePosition}
      ariaLabel="Toggle text source between Hutter and Delitzsch"
      title="Toggle text source"
      labelFontClass="font-ui-latin"
      textDirection="ltr"
      className={className}
    />
  )
}
