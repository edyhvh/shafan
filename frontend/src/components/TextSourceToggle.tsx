'use client'

import RetroToggle from './RetroToggle'

interface TextSourceToggleProps {
  enabled: boolean
  onToggle: () => void
  position?: string
}

export default function TextSourceToggle({
  enabled,
  onToggle,
  position,
}: TextSourceToggleProps) {
  return (
    <RetroToggle
      enabled={enabled}
      onToggle={onToggle}
      labelLeft="Hutter"
      labelRight="Delitzsch"
      position={position || 'top-[88px] right-5'}
      ariaLabel="Toggle text source between Hutter and Delitzsch"
      title="Toggle text source"
      labelFontClass="font-ui-latin"
      textDirection="ltr"
    />
  )
}
