interface LogoProps {
  className?: string
  size?: 'default' | 'compact'
}

export default function Logo({ className = '', size = 'default' }: LogoProps) {
  const isCompact = size === 'compact'

  const hebrewSize = isCompact
    ? 'text-[24px] md:text-[28px]'
    : 'text-[52px] md:text-[52px]'

  const latinSize = isCompact
    ? 'text-[22px] md:text-[26px]'
    : 'text-[48px] md:text-[48px]'

  const gap = isCompact ? 'gap-1.5' : 'gap-3'

  return (
    <div className={`flex items-baseline ${gap} ${className}`}>
      <span
        className={`font-logo-hebrew ${hebrewSize} leading-[1.1] text-black`}
      >
        שפן
      </span>
      <span className={`font-logo-latin ${latinSize} leading-[1.1] text-black`}>
        shafan
      </span>
    </div>
  )
}
