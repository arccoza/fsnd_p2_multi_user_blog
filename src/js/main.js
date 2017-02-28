// import {EditorState} from 'prosemirror-state';
// import {EditorView} from 'prosemirror-view';
// // import {schema} from 'prosemirror-schema-basic';
// import history from 'prosemirror-history';
// import {keymap} from 'prosemirror-keymap';
// import {schema, defaultMarkdownParser, defaultMarkdownSerializer} from 'prosemirror-markdown';
// // var {schema, defaultMarkdownParser, defaultMarkdownSerializer} = require('prosemirror-markdown');
import delegate from 'delegate';
var print = console.log.bind(console);
var ready = delegate.bind(document, document, 'DOMContentLoaded');
// var ready = document.addEventListener.bind(document, 'DOMContentLoaded');
// var click = document.addEventListener.bind(document, 'click');



ready(() => {
//   var view = new EditorView(document.body, {
//     state: EditorState.create({
//       doc: defaultMarkdownParser.parse('content'),
//       plugins: [history.history(), keymap({
//         "Mod-z": history.undo,
//         "Mod-Shift-z": history.redo
//       })],
//       selectionChange: ev => {
//         print(ev);
//       }
//     })
//   });

//   print(view);
  
  delegate(document.body, '.faves', 'click', ev => {
    print(ev);
    ev.preventDefault();
  });
});