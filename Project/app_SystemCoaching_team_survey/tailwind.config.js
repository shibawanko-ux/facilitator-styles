/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#ffcc00',
          light: '#fffef0',
          dark: '#e6b800',
        },
        ad: {
          gray: '#666666',
          dark: '#333333',
          border: '#e8e8e8',
          bg: '#fafafa',
        },
      },
      fontFamily: {
        sans: ['Poppins', 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
