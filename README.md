# fsnd_p2_multi_user_blog

Project #2 of FSND

A multi-user blog built for GAE using Flask and Gulp.

All css and js source files are in src. All css and js built files are in bld.

All development and testing was done on Linux (elementary OS 0.4 / Ubuntu 16.04) and Node.js v6.9.2, running the project under Windows was not tested, but it should run.

A modern browser (IE 11 / Edge, current versions of Chrome / Firefox / Safari) that supports current flexbox is required to view the site.

An internet connection is required to access online resources.

## View

To view the site, visit this link: [https://fsnd-mublog.appspot.com/](https://fsnd-mublog.appspot.com/)

## Download and Setup

### Download
To download this project either:
- Clone this repo with `git clone git@github.com:arccoza/fsnd_p2_multi_user_blog.git`
- Or download it as an archive from [here](https://github.com/arccoza/fsnd_p2_multi_user_blog/archive/master.zip) and unzip.

### Setup

GAE gcloud dev server, Node.js >= v6, Python 2.7, and Gulp are required to build and run the project on a local dev machine.

GAE gcloud and a GAE account are required to publish the project online.

## Building and Running
To build the project and run it locally do:

1. From the project folder at a terminal type `npm install`.
2. Then `gulp build` to prepare the js and css.
3. Then `dev_appserver.py app.yaml` to run the local dev server.
4. View the site on `http://localhost:8080/`.

## Usage
To add and edit content on the site signin or register by clicking on the icons in the top right of the site.
Once registered and/or signed-in there will be an file+ icon at the top left of the content area, click this to add new posts.
Alongside each post, both in the index and when viewing individual posts, there are icons to favourite, edit, and delete posts.
You can comment on a post using the form at the end of the article, you must be signed-in.

Markdown is accepted in posts and comments.

## Notes

- Custom `Security`, `Token`, and `Session` classes were created to manage auth and sessions in the app.
- Authenticaion and sessions are handled using JSON Web Tokens.
- Models use the Security object for route access control through decorators.
- Passlib is used for password encryption and verification.
- GAE does not allow you to access much information from python's `os` module, the `cuid` module requires `os.getpid` so a version for GAE was modified and placed in `utils`.
- PEP8 was followed for all python code, except for the use of 2 space indentation; personal preference.