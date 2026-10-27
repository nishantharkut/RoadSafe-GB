/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#F8FAFC", // Light mode page background
        card: "#FFFFFF",
        primaryText: "#0F172A",
        secondaryText: "#475569",
        borderSubtle: "#E2E8F0",
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        severity: {
          fatal: '#DC2626',
          serious: '#EA580C',
          slight: '#0D9488'
        }
      }
    },
  },
  plugins: [],
}
