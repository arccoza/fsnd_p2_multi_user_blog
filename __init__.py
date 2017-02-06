from flask import Flask, request, render_template, redirect, url_for


app = Flask(__name__, template_folder="views")


@app.route("/")
def root(req):
  return render_template('index.html', text=text)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
