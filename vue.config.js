module.exports = {
  css: {
    loaderOptions: {
      postcss: {
        plugins: [
          require('postcss-import')(),
          require('postcss-cssnext')({ browsers: ['>0.5%'] })]
      }
    }
  },
  outputDir: 'docs'
}

