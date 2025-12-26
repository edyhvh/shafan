interface ChevronDownProps {
  className?: string
}

export default function ChevronDown({ className = '' }: ChevronDownProps) {
  return (
    <svg
      className={`w-3 h-3 ${className}`}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M19 9l-7 7-7-7"
      />
    </svg>
  )
}
