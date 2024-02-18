from bs4 import BeautifulSoup
import httpx
import asyncio
import datetime

SITE_URL = 'https://www.kvs-saratov.ru'
START_URL = 'https://www.kvs-saratov.ru/news/operativnyy-monitoring/'
PAGE_URL = 'https://www.kvs-saratov.ru/news/operativnyy-monitoring/18443?PAGEN_1='


async def fetch_html(url, client):
    """ Получение HTML-кода страницы по заданному URL """
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.content
    except httpx.HTTPStatusError as exc:
        print(f"HTTP error occurred while fetching {url}: {exc}")

async def get_page(url, client):
    """ Извлечение контента со страницы """
    html = await fetch_html(url, client)
    return BeautifulSoup(html, 'html.parser')


async def parse_page(url, client):
    page = await get_page(url, client)

    news_items = page.find_all('div', {'class': 'news_item'})
    for item in news_items:
        id = item.find('a')['href'].split('/')[-2]
        loc = item.find('h3').get_text('', True)
        date_str = item.find('span').get_text()
        date = datetime.datetime.strptime(date_str, "%d.%m.%Y").date()
        print(id, date, loc)


async def get_last_page_number(url, client):
    """ Получение номера последней страницы с данными """
    page = await get_page(url, client)
    last_url_block = page.find('a', string='Конец')
    last_page = int(last_url_block['href'].split('=')[-1])
    return last_page


async def async_range(start, stop):
    for i in range(start, stop):
        yield i
        await asyncio.sleep(0)


async def main():
    async with httpx.AsyncClient() as client:
        # max_page_number = await get_last_page_number(START_URL, client)
        max_page_number = 3

        async for page_number in async_range(1, max_page_number + 1):
            url = f'{PAGE_URL}{page_number}'
            await parse_page(url, client)


if __name__ == "__main__":
    asyncio.run(main())
