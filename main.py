import os
import anthropic
import asyncio
import requests
import aiohttp
import random
from bs4 import BeautifulSoup
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
from tabulate import tabulate


def scrape_intro_paragraphs(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.content, "html.parser")

  paragraphs = soup.find_all('p')

  return " ".join([paragraph.text for paragraph in paragraphs[:3]])


async def async_fetch_page(session, url):
  async with session.get(url) as response:
    return await response.text()


async def async_parse_page(session, url):
  page = await async_fetch_page(session, url)
  soup = BeautifulSoup(page, "html.parser")
  paragraphs = soup.find_all('p')
  return " ".join([paragraph.text for paragraph in paragraphs[:3]])


async def async_scrape_intro_paragraphs(urls):
  async with aiohttp.ClientSession() as session:
    tasks = [async_parse_page(session, url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results


def summarize_paragraphs(client, paragraphs):
  prompt = f"""
    Summarize the following paragraphs: 
    
    {" ".join(paragraphs)}
  """

  message = client.messages.create(
      model="claude-3-7-sonnet-20250219",
      max_tokens=1000,
      temperature=1,
      system=
      "You are a wikipedia summarizer. Respond with a summary, maximum one sentence.",
      messages=[{
          "role": "user",
          "content": [{
              "type": "text",
              "text": prompt
          }]
      }])
  return message.content[0].text


all_urls = [
    "https://en.wikipedia.org/wiki/Goldendoodle",
    "https://en.wikipedia.org/wiki/Golden_Retriever",
    "https://en.wikipedia.org/wiki/Poodle",
    "https://en.wikipedia.org/wiki/German_Shepherd",
    "https://en.wikipedia.org/wiki/Labrador_Retriever",
    "https://en.wikipedia.org/wiki/Husky",
    "https://en.wikipedia.org/wiki/Beagle",
    "https://en.wikipedia.org/wiki/Pomeranian_dog",
    "https://en.wikipedia.org/wiki/Chihuahua_(dog_breed)",
    "https://en.wikipedia.org/wiki/Dachshund",
    "https://en.wikipedia.org/wiki/Bernese_Mountain_Dog"
]

# sets up anthropic
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# runs the performance tests
url_counts = [3, 6, 10]

sequential_performance = [ "Sequential" ]
asynchronous_performance = [ "Asynchronous" ]
multithreaded_performance = [ "Multithreaded" ]

for n in url_counts:
  urls = random.sample(all_urls, n)

  print('* ' * 10 + f"{n} URLs " + '* ' * 10)
  
  # sequentially
  start_time = perf_counter()
  results = [scrape_intro_paragraphs(url) for url in urls]
  end_time = perf_counter()
  
  sequential_time_ms = (end_time - start_time) * 1000
  sequential_performance.append(f"{sequential_time_ms:.2f} ms")
  print(f"Sequential summary: {summarize_paragraphs(client, results)} \n")
  
  # asynchronously
  start_time = perf_counter()
  results = asyncio.run(async_scrape_intro_paragraphs(urls))
  end_time = perf_counter()
  
  asynchronous_time_ms = (end_time - start_time) * 1000
  asynchronous_performance.append(f"{asynchronous_time_ms:.2f} ms")
  print(f"Asynchronous summary: {summarize_paragraphs(client, results)} \n")
  
  # multithreaded
  start_time = perf_counter()
  with ThreadPoolExecutor() as executor:
    results = list(executor.map(scrape_intro_paragraphs, urls))
  end_time = perf_counter()
  
  multithreaded_time_ms = (end_time - start_time) * 1000
  multithreaded_performance.append(f"{multithreaded_time_ms:.2f} ms")
  print(f"Multithreaded summary: {summarize_paragraphs(client, results)} \n")

# visualize results
table_data = [sequential_performance, asynchronous_performance, multithreaded_performance]

print("\nPerformance Comparison:")
headers = ["Method"] + [f"{n} URLs" for n in url_counts]
print(tabulate(table_data, headers=headers, tablefmt='grid'))

# todo: print graph to compare
# summaries into a txt file
# todo: add more urls
