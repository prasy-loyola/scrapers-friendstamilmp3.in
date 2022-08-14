# %%
import json
from email import contentmanager
import os
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://friendstamilmp3.in/"


def songs_from_movie(movie_page):
    print("processing .. " + movie_page)
    page = requests.get(BASE_URL + movie_page).text
    content = BeautifulSoup(page, features="html.parser")

    song_elements = content.find_all("a", {"title": "Download this song"})

    songs  = { s["download"]: s["href"] for s in song_elements}

    return songs


def get_movies(base_page):

    page_url = BASE_URL + base_page
    print("processing  " + page_url)
    content = requests.get(page_url).text
    page = BeautifulSoup(content, features="html.parser")
    movies = page.find_all("span", {"class": "folder"})
    movies += page.find_all("span", {"class": "folder1"})
    if movies is None:
        return []

    movie_links = list(
        filter(lambda m: m["name"] != '',
            map(lambda x: 
                {"name": x.find("a").text,
                "link": x.find("a")["href"],
                 "songs": songs_from_movie(x.find("a")["href"])
                 },movies
            )
        )
    )

    return movie_links


def get_movies_A_Z(page):
    movies = []
    for cpage in range(ord("A"), ord("Z")+1):
        movies += get_movies("index.php?page=" + page + "&cpage=" + chr(cpage))
    return movies


# %%


pages = ["Old%20Collections",
         "Old%20Hits%20(Singers)"]
a_z_pages =[ "M.S.Viswanathan%20Hits"]
collection = {}
for page in pages:
    collection[page] = get_movies("index.php?page=" + page)

for page in a_z_pages:
    collection[page] = get_movies_A_Z( page)

#%%

with open("songs.json","w") as file:
    file.write(json.dumps(collection))

#%%
print(os.curdir)
#%%
for collection in json.load(open("songs.json","r")).items():
    collection_dir =  os.curdir +"/" +  collection[0]
    os.makedirs(collection_dir, exist_ok=True)

    for movie in collection[1]:
        movie_dir  = collection_dir + "/" + movie["name"]
        os.makedirs(movie_dir, exist_ok=True)

        for song in movie["songs"].items():
            with open(movie_dir + "/" + song[0] ,"wb") as file:
                file.write( requests.get(song[1]).content)
