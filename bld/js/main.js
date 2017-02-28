(function () {
'use strict';

var DOCUMENT_NODE_TYPE = 9;

/**
 * A polyfill for Element.matches()
 */
if (Element && !Element.prototype.matches) {
    var proto = Element.prototype;

    proto.matches = proto.matchesSelector ||
                    proto.mozMatchesSelector ||
                    proto.msMatchesSelector ||
                    proto.oMatchesSelector ||
                    proto.webkitMatchesSelector;
}

/**
 * Finds the closest parent that matches a selector.
 *
 * @param {Element} element
 * @param {String} selector
 * @return {Function}
 */
function closest$1 (element, selector) {
    while (element && element.nodeType !== DOCUMENT_NODE_TYPE) {
        if (element.matches(selector)) return element;
        element = element.parentNode;
    }
}

var closest_1 = closest$1;

var closest = closest_1;

/**
 * Delegates event to a selector.
 *
 * @param {Element} element
 * @param {String} selector
 * @param {String} type
 * @param {Function} callback
 * @param {Boolean} useCapture
 * @return {Object}
 */
function delegate(element, selector, type, callback, useCapture) {
    var listenerFn = listener.apply(this, arguments);

    element.addEventListener(type, listenerFn, useCapture);

    return {
        destroy: function() {
            element.removeEventListener(type, listenerFn, useCapture);
        }
    }
}

/**
 * Finds closest match and invokes callback.
 *
 * @param {Element} element
 * @param {String} selector
 * @param {String} type
 * @param {Function} callback
 * @return {Function}
 */
function listener(element, selector, type, callback) {
    return function(e) {
        e.delegateTarget = closest(e.target, selector);

        if (e.delegateTarget) {
            callback.call(element, e);
        }
    }
}

var delegate_1 = delegate;

// import {EditorState} from 'prosemirror-state';
// import {EditorView} from 'prosemirror-view';
// // import {schema} from 'prosemirror-schema-basic';
// import history from 'prosemirror-history';
// import {keymap} from 'prosemirror-keymap';
// import {schema, defaultMarkdownParser, defaultMarkdownSerializer} from 'prosemirror-markdown';
// // var {schema, defaultMarkdownParser, defaultMarkdownSerializer} = require('prosemirror-markdown');
var print = console.log.bind(console);
var ready = delegate_1.bind(document, document, 'DOMContentLoaded');
// var ready = document.addEventListener.bind(document, 'DOMContentLoaded');
// var click = document.addEventListener.bind(document, 'click');


ready(function () {
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

  delegate_1(document.body, '.faves', 'click', function (ev) {
    print(ev);
    ev.preventDefault();
  });
});

}());
