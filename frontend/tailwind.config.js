/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          ink: "#0F172A",
          sky: "#0EA5E9",
          mist: "#E2E8F0",
          sand: "#F8FAFC",
        },
      },
    },
  },
  plugins: [],
};
