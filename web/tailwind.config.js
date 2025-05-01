/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: '#fcd34d',       // Yellow
        glass: '#60a5fa',       // Blue
        metal: '#9ca3af',       // Gray
        others: '#a3e635',      // Green
      },
    },
  },
  plugins: [],
} 