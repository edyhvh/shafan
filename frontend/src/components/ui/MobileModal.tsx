'use client'

import { createPortal } from 'react-dom'
import { useEffect, useState } from 'react'

interface MobileModalProps {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
  topOffset?: string // default "top-24"
}

export default function MobileModal({
  isOpen,
  onClose,
  children,
  topOffset = 'top-24',
}: MobileModalProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted || !isOpen) return null

  return createPortal(
    <div
      className={`fixed ${topOffset} left-0 right-0 bottom-0 z-[1000]`}
      onClick={(e) => {
        // Close if clicking the backdrop (not the modal content)
        if (e.target === e.currentTarget) {
          onClose()
        }
      }}
    >
      {/* Backdrop - covers the entire modal area */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in duration-300" />

      {/* Modal Content - centered in the modal area */}
      <div
        className="relative z-10 flex justify-center items-start pt-4 px-4 h-full animate-in fade-in slide-in-from-top-4 duration-300 ease-out"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>,
    document.body
  )
}
