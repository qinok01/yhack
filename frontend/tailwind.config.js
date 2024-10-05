module.exports = {

  content: [
    './index.html',
    './src/**/*.{html,js,jsx,ts,tsx}', // Adjust the paths according to your project structure

  ],

  theme: {
    extend: {
      colors: {
        customLightGray: '#F3F3FD', // Your custom color
        customeBlue: "#1678F2", // Your custom color
        
      },
      fontFamily: {
        afacad: ['Afacad', 'sans-serif'], // Add custom font family  
        roboto: ['Roboto', 'sans-serif'], // Add custom font family
      },
      maxWidth: {
        '1400': '1400px', // Add custom max-width for 1400px
      },
      backgroundImage: {
        'custom-radial': 'radial-gradient(linear, rgba(58,142,246,1) 0%, rgba(111,58,250,1) 100%)',
        'custom-linear': 'linear-gradient(90deg, rgba(58,142,246,1) 0%, rgba(111,58,250,1) 100%)',
      },

    },
  },

  plugins: [],

}
