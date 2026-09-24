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
        bgBase: '#05070D',
        panelBase: '#0B1226',
        panelBorder: 'rgba(255, 255, 255, 0.08)',
        accentTeal: '#14B8A6',
        accentAmber: '#F59E0B',
        accentRose: '#F43F5E',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Space Grotesk', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-teal': 'glowTeal 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glowTeal: {
          '0%': { boxShadow: '0 0 10px rgba(20, 184, 166, 0.2)' },
          '100%': { boxShadow: '0 0 25px rgba(20, 184, 166, 0.6)' },
        }
      }
    },
  },
  plugins: [],
}
