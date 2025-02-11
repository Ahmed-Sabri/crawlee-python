#pip install 'crawlee[curl-impersonate]' 'crawlee[playwright]' curl_cffi crawlee 'crawlee[all]' 
import asyncio
import os
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlsplit
import bleach
import markdown

async def main() -> None:
    # Prompt the user to enter the website they need to crawl and scrape
    website = input("Enter the website you want to crawl and scrape: ")

    # Create a folder with the name of the website
    folder_name = website.split("//")[-1].split("/")[0]
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Create separate folders for HTML and Markdown files
    html_folder = os.path.join(folder_name, "html")
    markdown_folder = os.path.join(folder_name, "markdown")
    if not os.path.exists(html_folder):
        os.makedirs(html_folder)
    if not os.path.exists(markdown_folder):
        os.makedirs(markdown_folder)

    # BeautifulSoupCrawler crawls the web using HTTP requests and parses HTML using the BeautifulSoup library.
    crawler = BeautifulSoupCrawler(max_requests_per_crawl=50000)

    # Define a request handler to process each crawled page and attach it to the crawler using a decorator.
    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
        context.log.info(f'Processing {context.request.url} ...')
        # Extract relevant data from the page context.
        data = {
            'url': context.request.url,
            'title': context.soup.title.string if context.soup.title else None,
        }
        # Store the extracted data.
        await context.push_data(data)
        # Extract links from the current page and add them to the crawling queue.
        await context.enqueue_links()

        # Download the crawled HTML file
        response = requests.get(context.request.url)
        html_file = os.path.join(html_folder, f"{urlsplit(context.request.url).path.split('/')[-1]}.html")
        with open(html_file, "w") as file:
            file.write(response.text)

        # Convert the HTML file to Markdown
        html_file = os.path.join(html_folder, f"{urlsplit(context.request.url).path.split('/')[-1]}.html")
        markdown_file = os.path.join(markdown_folder, f"{urlsplit(context.request.url).path.split('/')[-1]}.md")
        with open(html_file, "r") as file:
            html = file.read()
        markdown_text = bleach.clean(html, tags=[], strip=True)
        markdown_text = markdown.markdown(markdown_text)
        with open(markdown_file, "w") as file:
            file.write(markdown_text)

    # Add first URL to the queue and start the crawl.
    await crawler.run([website])

if __name__ == '__main__':
    asyncio.run(main())
