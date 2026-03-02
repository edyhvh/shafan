'use client'

import { useEffect } from 'react'

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
  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    const drawFloatingChat = () => {
      if (!window.kofiWidgetOverlay) {
        return
      }

      window.kofiWidgetOverlay.draw(
        'edyhvh',
        {
          type: 'floating-chat',
          'floating-chat.donateButton.text': 'Support me',
          'floating-chat.donateButton.background-color': '#00b9fe',
          'floating-chat.donateButton.text-color': '#fff',
        },
        'kofi-inline-container'
      )
    }

    if (window.kofiWidgetOverlay) {
      drawFloatingChat()
    } else {
      const overlayScript = document.getElementById(
        'kofi-overlay-widget-script'
      ) as HTMLScriptElement | null

      if (!overlayScript) {
        const script = document.createElement('script')
        script.id = 'kofi-overlay-widget-script'
        script.src = 'https://storage.ko-fi.com/cdn/scripts/overlay-widget.js'
        script.type = 'text/javascript'
        script.onload = drawFloatingChat
        document.head.appendChild(script)
      } else {
        overlayScript.addEventListener('load', drawFloatingChat, { once: true })
      }
    }
  }, [])

  return (
    <>
      <div id="kofi-inline-container" className="flex justify-center" />
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
