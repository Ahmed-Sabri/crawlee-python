import asyncio
import os
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext

# Ensure the directory exists
output_dir = os.path.join(os.getcwd(), 'output-folder')
os.makedirs(output_dir, exist_ok=True)

async def main() -> None:
    crawler = PlaywrightCrawler(
        max_requests_per_crawl=500,
    )

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f'Processing {context.request.url}')
        
        # Extract the content of the page
        content = await context.page.content()
        
        # Generate a valid filename from the URL
        filename = context.request.url.replace('https://', '').replace('/', '_') + '.html'
        filepath = os.path.join(output_dir, filename)
        
        # Save the content to a file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        
        context.log.info(f'Saved {context.request.url} to {filepath}')
        
        # Find and enqueue links to other pages within the documentation
        await context.enqueue_links(
            selector='a',  # Adjust the selector as needed to target all relevant links
            label='DETAIL',
        )

    await crawler.run(['https://example.com/'])

if __name__ == '__main__':
    asyncio.run(main())
