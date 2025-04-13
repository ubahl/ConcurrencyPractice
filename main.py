import os
import anthropic
import asyncio
import requests
import aiohttp
from bs4 import BeautifulSoup
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor


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


urls = [
    "https://en.wikipedia.org/wiki/Goldendoodle",
    "https://en.wikipedia.org/wiki/Golden_Retriever",
    "https://en.wikipedia.org/wiki/Poodle"
]

# set up anthropic

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# sequentially

start_time = perf_counter()

results = [scrape_intro_paragraphs(url) for url in urls]

end_time = perf_counter()

print(f"Summary: {summarize_paragraphs(client, results)}")

print(f"Sequentially: {(end_time - start_time)*1000:.2f} ms")

# asynchronously

print()

start_time = perf_counter()

results = asyncio.run(async_scrape_intro_paragraphs(urls))

end_time = perf_counter()

print(f"Summary: {summarize_paragraphs(client, results)}")

print(f"Asynchronously: {(end_time - start_time)*1000:.2f} ms")

# multithreaded

print()

start_time = perf_counter()

with ThreadPoolExecutor() as executor:
  results = list(executor.map(scrape_intro_paragraphs, urls))

end_time = perf_counter()

print(f"Summary: {summarize_paragraphs(client, results)}")

print(f"Multithreaded: {(end_time - start_time)*1000:.2f} ms")

# todo: print table / graph to compare
# todo: add more urls
