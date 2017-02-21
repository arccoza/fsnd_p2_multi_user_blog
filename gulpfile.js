var gulp = require('gulp')
// var rename = require('gulp-rename')
var rollup = require('gulp-better-rollup')
var babel = require('rollup-plugin-babel')
var nodeResolve = require('rollup-plugin-node-resolve');
var commonjs = require('rollup-plugin-commonjs');
var json = require('rollup-plugin-json');
var postcss = require('gulp-postcss');
var autoprefixer = require('autoprefixer');
var cssnano = require('cssnano');
var atImport = require("postcss-import");
var aseColors = require('postcss-ase-colors');
var colorFunction = require("postcss-color-function")
var print = console.log.bind(console);

 
gulp.task('build:js', () => {
  gulp.src('src/js/main.js')
    // .pipe(sourcemaps.init())
    .pipe(rollup({
      // notice there is no `entry` option as rollup integrates into gulp pipeline 
      plugins: [
        nodeResolve({ jsnext: true, main: true, browser: true, preferBuiltins: false }),
        commonjs({ include: 'node_modules/**' }),
        json(),
        babel({
          exclude: [
            'node_modules/**',
            '*.json'
          ],
        })
      ]
    }, {
      // also rollups `sourceMap` option is replaced by gulp-sourcemaps plugin 
      format: 'iife',
    }))
    // inlining the sourcemap into the exported .js file 
    // .pipe(sourcemaps.write())
    .pipe(gulp.dest('bld/js'))
});


gulp.task('build:css', function () {
  var processors = [
    atImport(),
    aseColors({file: 'node_modules/colors.css/assets/colors-css.ase'}),
    colorFunction(),
    autoprefixer(),
    // cssnano()
  ]

  return gulp.src('src/css/main.css')
    .pipe(postcss(processors))
    .pipe(gulp.dest('bld/css'));
});


gulp.task('watch', function() {
  gulp.watch('src/**/*.js', ['build:js']);
  gulp.watch('src/**/*.css', ['build:css']);
});