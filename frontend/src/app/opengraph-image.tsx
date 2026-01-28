import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const alt = 'Shafan – Pure Hebrew for Scripture Study'
export const size = {
  width: 1200,
  height: 630,
}
export const contentType = 'image/png'

export default async function Image() {
  return new ImageResponse(
    <div
      style={{
        fontSize: 60,
        background: 'linear-gradient(to bottom, #1e293b, #0f172a)',
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontFamily: 'system-ui',
      }}
    >
      <div
        style={{
          fontSize: 120,
          fontWeight: 'bold',
          marginBottom: 20,
        }}
      >
        shafan
      </div>
      <div
        style={{
          fontSize: 40,
          opacity: 0.9,
          textAlign: 'center',
          maxWidth: 900,
        }}
      >
        Pure Hebrew for Scripture Study
      </div>
      <div
        style={{
          fontSize: 32,
          opacity: 0.7,
          marginTop: 40,
        }}
      >
        Tanakh • Besorah • Delitzsch • Hutter
      </div>
    </div>,
    {
      ...size,
    }
  )
}
