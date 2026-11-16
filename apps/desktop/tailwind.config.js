/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        surface: {
          DEFAULT: '#0f172a',
          elevated: '#1e293b',
          muted: '#131b2e',
        },
        border: {
          DEFAULT: '#1e293b',
          focused: '#334155',
        },
        primary: {
          DEFAULT: '#2563eb',
          hover: '#1d4ed8',
          light: '#3b82f6',
        },
        cyan: {
          DEFAULT: '#06b6d4',
          hover: '#0891b2',
        },
      },
    },
  },
  plugins: [],
};
