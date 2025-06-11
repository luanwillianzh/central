from fastapi import FastAPI
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from bs4 import BeautifulSoup
import urllib.parse
app = FastAPI()

@app.get("/novel/{novel}")
def get_novel_info(novel):
    response = requests.get(f"https://centralnovel.com/series/{novel}/", verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    name = soup.select_one("h1[itemprop=name]").text.strip()
    desc = soup.select_one(".entry-content p").text.strip()
    cover = soup.select_one("div.thumb img")["src"]
    lista = soup.select("div.bixbox.bxcl.epcheck a")[::-1][:-2]
    chapters = [ (" - ".join([ i.text for i in a.select("div")[:2] ]), a['href'].split('/')[-2]) for a in lista ]
    genres = [ [a["href"].split("/")[-2], a.text] for a in soup.select(".genxed a")]
    return {"nome": name, "desc": desc, "cover": cover, "chapters": chapters, "genres": genres}

@app.get("/chapter/{chapter}")
def get_chapter(chapter):
    response = requests.get(f"https://centralnovel.com/{chapter}/", verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.select_one("h1.entry-title").text.strip()
    subtitle = soup.select_one("div.cat-series").text.strip()
    content = str(soup.select_one("div.epcontent.entry-content"))
    return {"title": title, "subtitle": subtitle, "content": content}

@app.get("/search/{text}")
def search(text):
    url = "https://centralnovel.com/wp-admin/admin-ajax.php"
    headers = {"Accept": "*/*", "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3", "TE": "trailers", "Content-Type": "application/x-www-form-urlencoded"}
    query = urllib.parse.quote_plus(text)
    data = "action=ts_ac_do_search&ts_ac_query={}".format(query)
    resp = requests.post(url, headers=headers, data=data, verify=False).json()
    lista = resp['series'][0]['all']
    return {"sucesso": True, "resultado": [ {"nome": a['post_title'], "url": a['post_link'].split("/")[-2], "cover": a['post_image']} for a in lista ]}
