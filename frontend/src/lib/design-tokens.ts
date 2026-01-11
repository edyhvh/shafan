/**
 * Design tokens for Shafan project
 * Based on design system specification
 */

export const colors = {
  black: '#000000',
  gray: '#333333',
  background: '#FAF6F0',
  white: '#FFFFFF',
  // Dark theme colors
  dark: {
    background: '#3c3836',
    hebrew: '#d5c4a1',
    ui: '#bdae93',
  },
} as const

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '32px',
  xl: '64px',
} as const

export const radius = {
  none: '0',
} as const

export const typography = {
  logo: {
    latin: {
      family: "'Libre Bodoni', serif",
      weight: 700,
      sizeDesktop: '48px',
      sizeMobile: '36px',
      lineHeight: 1.1,
    },
    hebrew: {
      family: "'Suez One', serif",
      weight: 400,
      sizeDesktop: '52px',
      sizeMobile: '38px',
      lineHeight: 1.1,
    },
  },
  bible: {
    hebrew: {
      family: "'Cardo', serif",
      weights: {
        regular: 400,
        bold: 700,
      },
      sizeDesktop: '28px',
      sizeMobile: '24px',
      lineHeight: 1.85,
      letterSpacing: '0.01em',
    },
  },
  ui: {
    latin: {
      family: "'Inter', sans-serif",
      weights: {
        regular: 400,
        medium: 500,
        semibold: 600,
      },
      sizeBase: '16px',
      lineHeight: 1.5,
    },
    hebrew: {
      family: "'Assistant', sans-serif",
      weights: {
        regular: 400,
        semibold: 600,
      },
    },
  },
} as const

export const fonts = {
  googleFontsUrl:
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Libre+Bodoni:wght@700&family=Suez+One&family=Cardo:wght@400;700&family=Assistant:wght@400;600&display=swap',
} as const

export type Colors = typeof colors
export type Spacing = typeof spacing
export type Typography = typeof typography
