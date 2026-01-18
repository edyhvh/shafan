'use client'

import { SunIcon } from '../icons'
import { MoonIcon } from '../icons'

interface ThemeToggleIconProps {
  isLight: boolean
}

export default function ThemeToggleIcon({ isLight }: ThemeToggleIconProps) {
  return (
    <>
      {/* Sun icon - visible when light theme is enabled */}
      <div
        className={`transition-all duration-300 ${
          isLight ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
        }`}
      >
        <SunIcon />
      </div>

      {/* Moon icon - visible when dark theme is enabled */}
      <div
        className={`absolute inset-0 transition-all duration-300 ${
          !isLight ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
        }`}
      >
        <MoonIcon />
      </div>
    </>
  )
}
