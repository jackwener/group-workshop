/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', '"Noto Sans SC"', 'system-ui', 'sans-serif'],
        serif: ['"Playfair Display"', 'serif'],
      },
      colors: {
        brand: {
          50: '#fef9ec',
          100: '#fdf0c8',
          200: '#fbe08c',
          300: '#f9cc50',
          400: '#f7bc28',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
        },
        navy: {
          800: '#1e293b',
          900: '#0f172a',
        }
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0,0,0,0.04), 0 1px 2px -1px rgba(0,0,0,0.06)',
        'card-hover': '0 4px 12px 0 rgba(0,0,0,0.08), 0 2px 4px -2px rgba(0,0,0,0.06)',
        'glow': '0 0 20px rgba(245,158,11,0.15)',
      }
    },
  },
  plugins: [],
}
