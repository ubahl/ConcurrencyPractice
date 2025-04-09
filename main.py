import requests
from bs4 import BeautifulSoup

url = "https://en.wikipedia.org/wiki/Goldendoodle"

response = requests.get(url)

soup = BeautifulSoup(response.content, "html.parser")

content_div = soup.find()