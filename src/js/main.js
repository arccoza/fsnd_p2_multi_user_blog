// import {EditorState} from 'prosemirror-state';
// import {EditorView} from 'prosemirror-view';
// // import {schema} from 'prosemirror-schema-basic';
// import history from 'prosemirror-history';
// import {keymap} from 'prosemirror-keymap';
// import {schema, defaultMarkdownParser, defaultMarkdownSerializer} from 'prosemirror-markdown';
// // var {schema, defaultMarkdownParser, defaultMarkdownSerializer} = require('prosemirror-markdown');
// import 'unfetch/polyfill';
import delegate from 'delegate';
var print = console.log.bind(console);
// var ready = delegate.bind(document, document, 'DOMContentLoaded');
var ready = document.addEventListener.bind(document, 'DOMContentLoaded');
// var click = document.addEventListener.bind(document, 'click');



ready(ev => {
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

  delegate(document, '.faves', 'click', ev => {
    ev.preventDefault();
    
    print(ev);
    fetch(ev.delegateTarget.attributes.href.value, {
      method: 'POST',
      credentials: 'include'
    })
    .then(res => {
      return res.text();
      // alert(document.cookie.replace(/(?:(?:^|.*;\s*)session\s*\=\s*([^;]*).*$)|^.*$/, "$1"));
    })
    .then(res => {
      print(res);
      ev.delegateTarget.classList[res]('button-icon--active');
    })
    .catch(err => {
      print(err);
    });
    
    return false;
  });
});