'use client'

import Image from 'next/image'
import { useTheme } from '@/hooks/useTheme'

interface LogoProps {
  className?: string
  size?: 'default' | 'compact'
}

export default function Logo({ className = '', size = 'default' }: LogoProps) {
  const { theme, isLoaded } = useTheme()
  const isCompact = size === 'compact'

  const width = isCompact ? 28 : 120
  const height = isCompact ? 28 : 120
  const sizeClass = isCompact ? 'w-7 h-auto' : 'w-[120px] h-auto'
  const src =
    !isLoaded || theme === 'light' ? '/logo_light.svg' : '/logo_dark.svg'

  return (
    <div className={`flex items-center ${className}`}>
      <Image
        src={src}
        alt="shafan"
        width={width}
        height={height}
        priority={isCompact}
        unoptimized
        className={`${sizeClass} object-contain`}
      />
    </div>
  )
}
