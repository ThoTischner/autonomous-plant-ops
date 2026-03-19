/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'plant-bg': '#0a0e17',
        'plant-card': '#111827',
        'plant-border': '#1e293b',
        'plant-accent': '#3b82f6',
        'plant-success': '#10b981',
        'plant-warning': '#f59e0b',
        'plant-danger': '#ef4444',
      },
    },
  },
  plugins: [],
}
