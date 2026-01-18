// Standalone Back Arrow icon - left-pointing arrow
export default function BackArrowIcon({ className }: { className?: string }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      className={className}
    >
      <path d="M19 12H5M12 19l-7-7 7-7" />
    </svg>
  )
}
