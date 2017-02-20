from flask import Flask, request, render_template, redirect, url_for


app = Flask(__name__, template_folder="views", static_folder='bld', static_url_path='/static')
app.debug = True


@app.route("/")
def root():
  return render_template('index.html', page=None)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
