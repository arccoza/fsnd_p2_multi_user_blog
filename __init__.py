from sanic import Sanic
from sanic.response import json, html, text
from jinja2 import Environment, FileSystemLoader, select_autoescape


views = Environment(
  loader=FileSystemLoader('views'),
  autoescape=select_autoescape(['html', 'xml'])
)

app = Sanic()


@app.route("/")
async def test(req):
  tmpl = views.get_template('index.html')
  return html(tmpl.render(n=20, test=req.args.get('test')))

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
