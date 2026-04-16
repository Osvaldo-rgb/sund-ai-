/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./**/*.{html,js}"
  ],
  darkMode: 'class', // permite dark mode com a classe "dark"
  theme: {
    extend: {
      colors: {
        sund: {
          // Verde Principal - Saúde e Confiança
          green: '#10b981',
          'green-soft': '#34d399',
          'green-light': '#6ee7b7',

          // Azul - Inteligência e Calma
          blue: '#3b82f6',
          'blue-soft': '#60a5fa',
          'blue-light': '#93c5fd',

          // Neutros
          light: '#f8fafc',
          'light-2': '#f1f5f9',
          gray: '#e2e8f0',
          'gray-dark': '#64748b',

          // Dark Mode
          dark: '#0f172a',
          'dark-2': '#1e2937',
          'dark-3': '#334155'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
}