'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ChevronDown } from '@/components/icons'

interface DropdownItem {
  id: string
  label: string
  href?: string
  isCurrent?: boolean
  onClick?: () => void
}

interface SearchableDropdownProps {
  triggerLabel: string
  triggerClassName: string
  triggerAriaLabel: string
  isOpen: boolean
  onToggle: () => void
  searchQuery: string
  onSearchChange: (query: string) => void
  searchPlaceholder: string
  items: DropdownItem[]
  emptyMessage: string
  gridCols?: number
  dropdownClassName?: string
}

/**
 * Reusable searchable dropdown component
 */
export default function SearchableDropdown({
  triggerLabel,
  triggerClassName,
  triggerAriaLabel,
  isOpen,
  onToggle,
  searchQuery,
  onSearchChange,
  searchPlaceholder,
  items,
  emptyMessage,
  gridCols = 1,
  dropdownClassName = 'dropdown-panel',
}: SearchableDropdownProps) {
  const [searchInputRef, setSearchInputRef] = useState<HTMLInputElement | null>(
    null
  )

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && searchInputRef) {
      setTimeout(() => searchInputRef.focus(), 100)
    } else if (!isOpen) {
      onSearchChange('') // Clear search when closing
    }
  }, [isOpen, searchInputRef, onSearchChange])

  const renderItems = () => {
    if (gridCols > 1) {
      return (
        <div className={`grid grid-cols-${gridCols} gap-1 p-2`}>
          {items.length > 0 ? (
            items.map((item) => (
              <Link
                key={item.id}
                href={item.href || '#'}
                onClick={item.onClick}
                className={`flex items-center justify-center p-2 text-sm font-semibold rounded-lg transition-all duration-200 cursor-pointer ${
                  item.isCurrent
                    ? 'bg-primary text-white'
                    : 'text-primary bg-black/[0.04] hover:bg-black/[0.08] hover:shadow-sm'
                }`}
              >
                {item.label}
              </Link>
            ))
          ) : (
            <div className="col-span-full px-4 py-3 text-sm text-muted text-center">
              {emptyMessage}
            </div>
          )}
        </div>
      )
    }

    return (
      <div className="py-1 max-h-[300px] overflow-y-auto">
        {items.length > 0 ? (
          items.map((item) => (
            <Link
              key={item.id}
              href={item.href || '#'}
              onClick={item.onClick}
              className={`block px-4 py-2 text-sm font-semibold transition-all duration-200 cursor-pointer ${
                item.isCurrent
                  ? 'bg-primary text-white'
                  : 'text-primary hover:bg-black/[0.08] hover:shadow-sm'
              }`}
            >
              {item.label}
            </Link>
          ))
        ) : (
          <div className="px-4 py-3 text-sm text-muted text-center">
            {emptyMessage}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="relative inline-block">
      <button
        onClick={onToggle}
        className={`${triggerClassName} ${isOpen ? 'active' : ''} text-secondary`}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-label={triggerAriaLabel}
      >
        <span>{triggerLabel}</span>
        <ChevronDown
          className={`ml-1 transition-transform duration-200 text-secondary ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div
          className={`absolute left-1/2 -translate-x-1/2 top-full mt-2 overflow-hidden z-50 min-w-[200px] max-h-[400px] overflow-y-auto ${dropdownClassName}`}
        >
          {/* Search */}
          <div className="p-2 border-b border-black/5">
            <div className="relative">
              <svg
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <input
                ref={setSearchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                placeholder={searchPlaceholder}
                className="w-full pl-10 pr-4 py-2 text-sm font-ui-latin text-primary neumorphism-inset outline-none placeholder:text-muted rounded-lg"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          </div>
          {renderItems()}
        </div>
      )}
    </div>
  )
}
