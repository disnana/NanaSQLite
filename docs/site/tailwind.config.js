/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./.vitepress/**/*.{js,ts,vue,mts}",
        "./**/*.md",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    light: '#6366f1',
                    DEFAULT: '#4f46e5',
                    dark: '#3730a3',
                }
            }
        },
    },
    plugins: [],
}
