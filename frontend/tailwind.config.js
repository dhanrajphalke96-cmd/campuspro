import forms from '@tailwindcss/forms';

export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#050714',
        panel: 'rgba(8, 16, 34, 0.88)',
        border: 'rgba(255, 255, 255, 0.1)',
        accent: '#61dafb',
        muted: '#8a99b8',
        highlight: '#7c3aed',
      },
      boxShadow: {
        glass: '0 20px 60px rgba(0, 0, 0, 0.28)',
      },
    },
  },
  plugins: [forms],
};
