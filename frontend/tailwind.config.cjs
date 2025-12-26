/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        black: '#000000',
        gray: '#333333',
        background: '#FAF6F0',
        white: '#FFFFFF',
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '32px',
        xl: '64px',
      },
      borderRadius: {
        none: '0',
      },
      fontFamily: {
        'logo-latin': ['Libre Bodoni', 'serif'],
        'logo-hebrew': ['Suez One', 'serif'],
        'bible-hebrew': ['Cardo', 'serif'],
        'ui-latin': ['Inter', 'sans-serif'],
        'ui-hebrew': ['Assistant', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'logo-latin-desktop': '48px',
        'logo-latin-mobile': '36px',
        'logo-hebrew-desktop': '52px',
        'logo-hebrew-mobile': '38px',
        'bible-hebrew-desktop': '28px',
        'bible-hebrew-mobile': '24px',
        'ui-base': '16px',
      },
      lineHeight: {
        logo: '1.1',
        bible: '1.85',
        ui: '1.5',
      },
      letterSpacing: {
        bible: '0.01em',
      },
    },
  },
  plugins: [],
}
