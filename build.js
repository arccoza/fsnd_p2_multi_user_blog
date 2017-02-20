// import { rollup } from 'rollup';
// import nodeResolve from 'rollup-plugin-node-resolve';
// import commonjs from 'rollup-plugin-commonjs';
var rollup = require('rollup').rollup;
var nodeResolve = require('rollup-plugin-node-resolve');
var commonjs = require('rollup-plugin-commonjs');
var babel = require('rollup-plugin-babel');
var json = require('rollup-plugin-json');
var print = console.log.bind(console);


rollup({
  entry: './src/js/main.js',
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
})
.then(function(bundle) {
  bundle.write({
    format: 'iife',
    moduleName: 'library',
    dest: './bld/js/main.js',
    sourceMap: true
  });
})
.catch(function(err) {
  print(err);
})