import requests
import aiohttp
from bs4 import BeautifulSoup
from time import perf_counter

def scrape_intro_paragraphs(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.content, "html.parser")

  paragraphs = soup.find_all('p')

  return [paragraph.text for paragraph in paragraphs[:3]]

async def async_scrape_intro_paragraphs(url):
  async with aiohttp.ClientSession() as session:
    async with session.get('http://python.org') as response:
  
  response = requests.get(url)
  soup = BeautifulSoup(response.content, "html.parser")

  paragraphs = soup.find_all('p')

  return [paragraph.text for paragraph in paragraphs[:3]]


urls = [
  "https://en.wikipedia.org/wiki/Goldendoodle",
  "https://en.wikipedia.org/wiki/Golden_Retriever",
  "https://en.wikipedia.org/wiki/Poodle"
]

# without concurrency

start_time = perf_counter()

for url in urls:
  scrape_first_three_paragraphs(url)

end_time = perf_counter()

print(f"Without concurrency: {(end_time - start_time)*1000:.2f} ms")

# asynchronously

tart_time = perf_counter()

for url in urls:
  scrape_first_three_paragraphs(url)

end_time = perf_counter()

print(f"Asynchronously: {(end_time - start_time)*1000:.2f} ms")


# print table to compare async vs multithread


