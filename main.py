import os
import anthropic
import asyncio
import requests
import aiohttp
import random
from bs4 import BeautifulSoup
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from tabulate import tabulate
import matplotlib.pyplot as plt

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
    async with asyncio.TaskGroup() as tg:
      tasks = [tg.create_task(async_parse_page(session, url)) for url in urls]

  return [task.result() for task in tasks]


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

print(f"Number of processes: {os.cpu_count()}\n")

# sets up anthropic
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# runs the performance tests
url_counts = [3, 6, 10]

sequential_performance = []
asynchronous_performance = []
multithreaded_performance = []
multiprocessing_performance = []

for n in url_counts:
  urls = random.sample(all_urls, n)

  print('* ' * 10 + f"{n} URLs " + '* ' * 10)
  [print(f"* {url}") for url in urls]
  print('\n')
  
  # sequentially
  start_time = perf_counter()
  results = [scrape_intro_paragraphs(url) for url in urls]
  end_time = perf_counter()
  
  sequential_time_ms = (end_time - start_time) * 1000
  sequential_performance.append(sequential_time_ms)
  print(f"Sequential summary: {summarize_paragraphs(client, results)} \n")
  
  # asynchronously
  start_time = perf_counter()
  results = asyncio.run(async_scrape_intro_paragraphs(urls))
  end_time = perf_counter()
  
  asynchronous_time_ms = (end_time - start_time) * 1000
  asynchronous_performance.append(asynchronous_time_ms)
  print(f"Asynchronous summary: {summarize_paragraphs(client, results)} \n")
  
  # multithreaded
  start_time = perf_counter()
  with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(scrape_intro_paragraphs, urls))
  end_time = perf_counter()
  
  multithreaded_time_ms = (end_time - start_time) * 1000
  multithreaded_performance.append(multithreaded_time_ms)
  print(f"Multithreaded summary: {summarize_paragraphs(client, results)} \n")

  # multiprocess
  start_time = perf_counter()
  with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(scrape_intro_paragraphs, urls))
  end_time = perf_counter()
  
  multiprocessing_time_ms = (end_time - start_time) * 1000
  multiprocessing_performance.append(multiprocessing_time_ms)
  print(f"Multiprocessing summary: {summarize_paragraphs(client, results)} \n")
  

# visualize results (table)
table_data = [
  ["Sequential"] + [f"{time:2f} ms" for time in sequential_performance], 
  ["Asynchronous"] + [f"{time:2f} ms" for time in asynchronous_performance], 
  ["Multithreaded"] + [f"{time:2f} ms" for time in multithreaded_performance],
  ["Multiprocess"] + [f"{time:2f} ms" for time in multiprocessing_performance]
]

print("\nPerformance Comparison:")
headers = ["Method"] + [f"{n} URLs" for n in url_counts]
print(tabulate(table_data, headers=headers, tablefmt='grid'))

# visualize results (graph)

plt.figure(figsize=(10, 6))
plt.plot(url_counts, sequential_performance, marker='o', label='Sequential')
plt.plot(url_counts, asynchronous_performance, marker='s', label='Asynchronous')
plt.plot(url_counts, multithreaded_performance, marker='^', label='Multithreaded')
plt.plot(url_counts, multithreaded_performance, marker='^', label='Multiprocess')

plt.xlabel('Number of URLs')
plt.ylabel('Time (milliseconds)')
plt.title('Performance Comparison of Different Methods')
plt.legend()
plt.grid(True)
plt.savefig('performance_comparison.png')
plt.close()
