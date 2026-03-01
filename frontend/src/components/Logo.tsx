import Image from 'next/image'

interface LogoProps {
  className?: string
  size?: 'default' | 'compact'
}

export default function Logo({ className = '', size = 'default' }: LogoProps) {
  const isCompact = size === 'compact'

  const width = isCompact ? 28 : 120
  const height = isCompact ? 28 : 120
  const sizeClass = isCompact ? 'w-7 h-7' : 'w-[120px] h-[120px]'

  return (
    <div className={`flex items-center ${className}`}>
      <Image
        src="/logo.png"
        alt="shafan"
        width={width}
        height={height}
        priority={isCompact}
        className={`${sizeClass} object-contain`}
      />
    </div>
  )
}
