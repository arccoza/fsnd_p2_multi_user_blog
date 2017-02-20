var gulp = require('gulp')
// var rename = require('gulp-rename')
var rollup = require('gulp-better-rollup')
var babel = require('rollup-plugin-babel')
var nodeResolve = require('rollup-plugin-node-resolve');
var commonjs = require('rollup-plugin-commonjs');

 
gulp.task('build:js', () => {
  gulp.src('src/js/main.js')
    // .pipe(sourcemaps.init())
    .pipe(rollup({
      // notice there is no `entry` option as rollup integrates into gulp pipeline 
      plugins: [
        nodeResolve({ jsnext: true, main: true, browser: true }),
        commonjs({ include: 'node_modules/**' }),
        babel({
          "exclude": 'node_modules/**'
        })
      ]
    }, {
      // also rollups `sourceMap` option is replaced by gulp-sourcemaps plugin 
      format: 'iife',
    }))
    // inlining the sourcemap into the exported .js file 
    // .pipe(sourcemaps.write())
    .pipe(gulp.dest('bld/js'))
})