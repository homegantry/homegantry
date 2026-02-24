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
          0: '#18181b',
          1: '#1f1f23',
          2: '#27272a',
          3: '#323238',
        },
        border: {
          DEFAULT: '#3f3f46',
          hover: '#52525b',
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
