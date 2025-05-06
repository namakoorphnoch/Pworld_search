from flask import Flask, render_template_string, request
import requests
from bs4 import BeautifulSoup
import urllib.parse
import unicodedata

app = Flask(__name__)

HTML = """
<!doctype html>
<title>P-WORLD 機種名検索</title>
<h2>型式名から機種名を検索</h2>
<form method="post">
  <textarea name="keywords" rows="10" cols="60" placeholder="型式名を1行ずつ入力してください">{{ request.form.keywords or '' }}</textarea><br><br>
  <input type="submit" value="検索">
</form>
{% if results %}
  <h3>検索結果：</h3>
  <ul>
  {% for row in results %}
    <li>{{ row }}</li>
  {% endfor %}
  </ul>
{% endif %}
"""

def normalize(text):
    return unicodedata.normalize("NFKC", text).replace(" ", "").replace("　", "").strip()

def search_machine_name(keyword):
    base_url = "https://www.p-world.co.jp/_machine/t_machine.cgi?key="
    encoded = urllib.parse.quote(keyword)
    url = base_url + encoded
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.text.strip()
            return title.replace(" | P-WORLD", "")
    except Exception as e:
        return f"[エラー: {e}]"
    return "-"

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        raw = request.form["keywords"]
        lines = [normalize(line) for line in raw.splitlines() if line.strip()]
        for line in lines:
            name = search_machine_name(line)
            results.append(f"{line} → {name}")
    return render_template_string(HTML, results=results)

if __name__ == "__main__":
    app.run()
