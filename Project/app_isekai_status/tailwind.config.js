/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'game': ['"Noto Sans JP"', 'sans-serif'],
      },
      animation: {
        'bar-fill': 'barFill 1s ease-out forwards',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-in': 'slideIn 0.4s ease-out forwards',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'star-twinkle': 'starTwinkle 1.5s ease-in-out infinite',
      },
      keyframes: {
        barFill: {
          '0%': { width: '0%' },
          '100%': { width: 'var(--bar-width)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(251, 191, 36, 0.3)' },
          '50%': { boxShadow: '0 0 25px rgba(251, 191, 36, 0.8)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        starTwinkle: {
          '0%, 100%': { opacity: '0.3' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
