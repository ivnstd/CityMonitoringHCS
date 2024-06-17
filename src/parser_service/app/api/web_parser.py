import asyncio
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

from .scheme import Message
from .logger import logger


URL = 'https://www.kvs-saratov.ru/news/operativnyy-monitoring/18443?PAGEN_1='
URL2 = 'https://saratovvodokanal.ru/news/?PAGEN_1='
MESSAGE_COUNT = 100
LAST_ID = 32422     # локальный идентификатор последней записи на старом сайте
ID_DELTA = 57       # разница локальных идентификаторов на сайтах

SITE_ATTR = {
    URL: {
        'class': 'news_item',
        'item': 'h3',
        'date': 'span',
        'date_padding': " 00:00:00"
    },
    URL2: {
        'class': 'text_box',
        'item': 'h4',
        'date': 'time',
        'date_padding': ":00"
    }
}

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


async def parse_page(site_url, url, last_message_id, client, is_new, count=MESSAGE_COUNT):
    """ Парсинг одной страницы """
    page = await get_page(url, client)
    site_attr = SITE_ATTR[site_url]
    news_items = page.find_all('div', {'class': site_attr['class']})
    messages_info_list = []

    for item in news_items:
        try:
            if len(item.attrs.get('class', [])) > 1:
                continue

            id = int(item.find('a')['href'].split('/')[-2])
            # Если сообщение новое, парсим его
            if (not is_new and last_message_id - count <= id < last_message_id or
                    is_new and last_message_id < id <= last_message_id + count):

                id = id + ID_DELTA * int(site_url == URL2)
                location = item.find(site_attr['item']).get_text('', True)
                date_str = item.find(site_attr['date']).get_text()
                date = datetime.strptime(date_str + site_attr['date_padding'], "%d.%m.%Y %H:%M:%S")
                messages_info_list.append(Message(
                    id=id,
                    source="kvs",
                    date=date,
                    from_user="ООО «Концессии водоснабжения — Саратов»",
                    text=location,
                    image=None
                ))
                logger.info(f"Сообщение KVS:{id}")
        except Exception as e:
            logger.error(f"Ошибка при чтении: {e}")

    return messages_info_list


async def get_last_page_number(url, client):
    """ Получение номера последней страницы с данными """
    page = await get_page(url, client)
    last_url_block = page.find('a', string='Конец')
    last_page = int(last_url_block['href'].split('=')[-1])
    return last_page


async def get_last_message_id(client):
    """ Определение идентификатора последнего сообщения на сайте """
    page = await get_page(URL, client)

    news_item = page.find('div', {'class': 'news_item'})
    last_message_id = int(news_item.find('a')['href'].split('/')[-2])

    return last_message_id


async def async_range(start, stop):
    """ Асинхронный вариант range """
    for i in range(start, stop):
        yield i
        await asyncio.sleep(0)


def new_site_fix(last_message_id):
    url = URL
    if last_message_id >= LAST_ID:
        url = URL2
        last_message_id -= ID_DELTA
    return url, last_message_id


async def get_messages(last_message_id, is_new):
    async with httpx.AsyncClient() as client:
        if last_message_id == 0:
            # Если последнее id не определено или равно 0, то чтобы не пришлось парсить абсолютно всё
            # (что может быть опасно и не нужно), будем отталкиваться от последнего сообщения на сайте
            # и парсить определенное количесвто сообщений перед ним / после него
            last_message_id = await get_last_message_id(client)
            if is_new:
                last_message_id -= MESSAGE_COUNT

        url, last_message_id = new_site_fix(last_message_id)

        max_page_number = await get_last_page_number(url, client)
        messages = []

        async for page_number in async_range(1, max_page_number + 1):
            messages_count = len(messages)

            page_url = f'{url}{page_number}'
            messages_info_list = await parse_page(url, page_url, last_message_id, client, is_new)
            messages.extend(messages_info_list)

            if messages_count == len(messages) and messages_count > 0:
                break
        return messages


async def get_new_messages(last_message_id):
    return await get_messages(last_message_id, is_new=True)


async def get_old_messages(last_message_id):
    return await get_messages(last_message_id, is_new=False)
