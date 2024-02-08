const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/index.html' 
    })
  ],
  entry: './src/index.js', // Replace with the path to your main entry file
  output: {
    filename: 'bundle.js', // Replace with the desired output filename
    path: path.resolve(__dirname, 'dist'), // Replace with the desired output directory
    publicPath: '/static/', // This ensures that all the assets are served from the /static/ path
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
};
