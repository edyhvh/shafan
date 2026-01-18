import { SunIcon } from './icons'

interface ThemeToggleProps {
  enabled: boolean
  onClick: () => void
  ariaLabel?: string
}

export default function ThemeToggle({
  enabled,
  onClick,
  ariaLabel,
}: ThemeToggleProps) {
  return (
    <button
      onClick={onClick}
      className="cursor-pointer group relative"
      aria-label={ariaLabel}
    >
      <div className="relative">
        {/* Sun icon - visible when light theme is enabled */}
        <div
          className={`transition-all duration-300 ${
            enabled ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
          }`}
        >
          <SunIcon />
        </div>

        {/* Moon icon - visible when dark theme is enabled */}
        <div
          className={`absolute inset-0 transition-all duration-300 ${
            !enabled ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
          }`}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
        </div>
      </div>
    </button>
  )
}
