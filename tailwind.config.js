/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./pd/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        'alcher-bg': '#000000',
        'alcher-card': '#330426',
        'alcher-card-border': 'rgba(255, 255, 255, 0.2)',
        'alcher-input': '#5C1044',
        'alcher-placeholder': '#E8A2D7',
        'alcher-lime': '#C1FF00',
        'alcher-pink': '#FF3EBA',
        'alcher-pink-hover': '#E636A7',
        'alcher-border': '#4D0D39',
      },
      fontFamily: {
        sans: ['YDYoonche', 'yoona-yoonche', 'YoonA YoonChe', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        ydyoonche: ['YDYoonche', 'yoona-yoonche', 'YoonA YoonChe', 'sans-serif'],
        milker: ['Milker', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '1.25rem',
        '3xl': '1.75rem',
      }
    },
  },
  plugins: [],
}
