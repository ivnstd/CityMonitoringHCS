import asyncio
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

from .scheme import Message
from .logger import logger


SITE_URL = 'https://www.kvs-saratov.ru'
START_URL = 'https://www.kvs-saratov.ru/news/operativnyy-monitoring/'
PAGE_URL = 'https://www.kvs-saratov.ru/news/operativnyy-monitoring/18443?PAGEN_1='



async def fetch_html(url, client):
    """ Получение HTML-кода страницы по заданному URL """
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.content
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка HTTP при получении {url}: {e}")


async def get_page(url, client):
    """ Извлечение контента со страницы """
    html = await fetch_html(url, client)
    return BeautifulSoup(html, 'html.parser')


async def parse_page(url, last_message_id, client):
    """ Парсинг одной страницы """
    page = await get_page(url, client)

    news_items = page.find_all('div', {'class': 'news_item'})
    messages_info_list = []

    for item in news_items:
        id = int(item.find('a')['href'].split('/')[-2])
        # Если сообщение новое, парсим его
        if id > last_message_id:
            location = item.find('h3').get_text('', True)
            date_str = item.find('span').get_text()
            date = datetime.strptime(date_str + " 00:00:00", "%d.%m.%Y %H:%M:%S")
            messages_info_list.append(Message(
                id=id,
                source="kvs",
                date=date,
                from_user="ООО «Концессии водоснабжения — Саратов»",
                text=location,
                image=None
            ))
            logger.info(f"Сообщение KVS:{id}")


    # Если все спаршенные сообщения были новыми, парсинг нужно продолжить
    is_parsing_continue = len(messages_info_list) == len(news_items)

    return messages_info_list, is_parsing_continue


async def get_last_page_number(url, client):
    """ Получение номера последней страницы с данными """
    page = await get_page(url, client)
    last_url_block = page.find('a', string='Конец')
    last_page = int(last_url_block['href'].split('=')[-1])
    return last_page


async def async_range(start, stop):
    """ Асинхронный вариант range """
    for i in range(start, stop):
        yield i
        await asyncio.sleep(0)


async def get_messages(last_message_id=32350):
    async with httpx.AsyncClient() as client:
        max_page_number = await get_last_page_number(START_URL, client)

        messages = []
        async for page_number in async_range(1, max_page_number + 1):
            url = f'{PAGE_URL}{page_number}'
            (messages_info_list, is_parsing_continue) = await parse_page(url, last_message_id, client)
            messages.extend(messages_info_list)
            if not is_parsing_continue:
                break
        return messages
