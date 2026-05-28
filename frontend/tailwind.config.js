import forms from '@tailwindcss/forms';

export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#051617',
        panel: 'rgba(10, 34, 30, 0.94)',
        border: 'rgba(255, 255, 255, 0.08)',
        accent: '#14b8a6',
        muted: '#a3b8a0',
        highlight: '#fae8c4',
        surfaceLight: '#0d2d27',
      },
      boxShadow: {
        glass: '0 24px 80px rgba(0, 0, 0, 0.32)',
      },
    },
  },
  plugins: [forms],
};
