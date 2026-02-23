/** @type {import("tailwindcss").Config} */
export default {
  content: ["./src/**/*.{html,js,svelte,ts}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        surface: {
          0: '#0a0a0b',
          1: '#111113',
          2: '#1a1a1e',
          3: '#232329',
        },
        border: {
          DEFAULT: '#2a2a32',
          hover: '#3a3a44',
        },
        accent: {
          DEFAULT: '#6366f1',
          hover: '#818cf8',
          dim: '#6366f120',
        },
      },
    },
  },
  plugins: [],
};
