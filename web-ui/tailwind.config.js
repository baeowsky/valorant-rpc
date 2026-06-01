/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        themeAccent: '#bcb1e7',
        themeAccentSecondary: '#9a8fd1',
        themeBackground: '#060608',
      }
    },
  },
  plugins: [],
}
