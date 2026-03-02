'use client'

import { useEffect, useRef, useState } from 'react'
import { DONATION_CONFIG } from '@/lib/config'

declare global {
  interface Window {
    kofiWidgetOverlay?: {
      draw: (
        username: string,
        options: Record<string, string>,
        containerId?: string
      ) => void
    }
  }
}

export default function KoFiButton() {
  const drawnRef = useRef(false)
  const [loadFailed, setLoadFailed] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    let isActive = true
    let retryTimer: number | null = null
    let retries = 0
    const maxRetries = 20

    const drawFloatingChat = () => {
      if (!window.kofiWidgetOverlay || drawnRef.current || !isActive) {
        return false
      }

      try {
        window.kofiWidgetOverlay.draw(
          DONATION_CONFIG.kofiUsername,
          {
            type: 'floating-chat',
            'floating-chat.donateButton.text': 'Support me',
            'floating-chat.donateButton.background-color': '#00b9fe',
            'floating-chat.donateButton.text-color': '#fff',
          },
          'kofi-inline-container'
        )

        drawnRef.current = true
        setLoadFailed(false)
        return true
      } catch {
        return false
      }
    }

    const scheduleRetry = () => {
      if (!isActive || drawnRef.current) {
        return
      }

      if (retries >= maxRetries) {
        setLoadFailed(true)
        return
      }

      retries += 1
      retryTimer = window.setTimeout(() => {
        if (drawFloatingChat()) {
          return
        }
        scheduleRetry()
      }, 150)
    }

    const handleLoad = () => {
      if (drawFloatingChat()) {
        return
      }
      scheduleRetry()
    }

    const handleError = () => {
      if (!drawnRef.current) {
        setLoadFailed(true)
      }
    }

    if (window.kofiWidgetOverlay && drawFloatingChat()) {
      return () => {
        isActive = false
        if (retryTimer !== null) {
          window.clearTimeout(retryTimer)
        }
      }
    }

    let script = document.getElementById(
      'kofi-overlay-widget-script'
    ) as HTMLScriptElement | null

    if (!script) {
      script = document.createElement('script')
      script.id = 'kofi-overlay-widget-script'
      script.src = 'https://storage.ko-fi.com/cdn/scripts/overlay-widget.js'
      script.type = 'text/javascript'
      script.async = true
      document.head.appendChild(script)
    }

    script.addEventListener('load', handleLoad)
    script.addEventListener('error', handleError)

    if (script.getAttribute('data-loaded') === 'true') {
      handleLoad()
    }

    const markLoaded = () => {
      script?.setAttribute('data-loaded', 'true')
    }

    script.addEventListener('load', markLoaded)

    return () => {
      isActive = false
      script?.removeEventListener('load', handleLoad)
      script?.removeEventListener('load', markLoaded)
      script?.removeEventListener('error', handleError)
      if (retryTimer !== null) {
        window.clearTimeout(retryTimer)
      }
    }
  }, [])

  return (
    <>
      <div id="kofi-inline-container" className="flex justify-center" />
      {loadFailed && (
        <a
          href={`https://ko-fi.com/${DONATION_CONFIG.kofiUsername}`}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 inline-block text-sm text-gray/70 underline underline-offset-2 hover:text-black transition-colors"
        >
          Open Ko-fi donation page
        </a>
      )}
      <style jsx global>{`
        #kofi-inline-container .floatingchat-container-wrap,
        #kofi-inline-container .floatingchat-container-wrap-mobi {
          position: static !important;
          left: auto !important;
          right: auto !important;
          bottom: auto !important;
          width: 220px !important;
          height: 65px !important;
          margin: 0 auto !important;
          opacity: 1 !important;
          overflow: visible !important;
          transform: none !important;
          z-index: auto !important;
        }

        #kofi-inline-container .floatingchat-container,
        #kofi-inline-container .floatingchat-container-mobi {
          position: static !important;
          width: 220px !important;
          height: 65px !important;
          opacity: 1 !important;
          overflow: visible !important;
          transform: none !important;
        }
      `}</style>
    </>
  )
}
