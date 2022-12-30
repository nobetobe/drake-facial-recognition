import asyncio
import aiofiles
import shutil
import os
import aiohttp
from tqdm import tqdm
from bs4 import BeautifulSoup


def main():
    urls = asyncio.run(get_img_urls())
    asyncio.run(download_imgs(urls))


async def get_page(sess, url):
    async with sess.get(url) as response:
        if response.status != 200:
            return []
        
        html_text = await response.text()
    soup = BeautifulSoup(html_text, 'html.parser')
    imgs = soup.findAll('img', attrs={'src': True, 'gi-icon': False})
    return [img['src'] for img in imgs if not img['src'].startswith('/')]


async def get_img_urls():
    main_url = r'https://www.gettyimages.com/photos/drake?assettype=image&sort=mostpopular&phrase=drake&license=rf,rm&page='  # source of images
    urls = []
    print('Getting urls...')
    async with aiohttp.ClientSession() as sess:
        for i in range(20):  # first 20 pages of image source
            url = main_url+str(i)
            urls += await get_page(sess, url)
    print('Done')
    return urls


async def download_img(sess, url, num):
    async with sess.get(url) as response:
        if response.status != 200:
            return False
        async with aiofiles.open(f'drake-images/drake{num}.png', mode='wb') as img:
            await img.write(await response.read())
            await img.close()


async def download_imgs(urls):
    if os.path.exists('drake-images'):
        shutil.rmtree('drake-images')
    os.mkdir('drake-images')
    print('Downloading images...')
    async with aiohttp.ClientSession() as sess:
        for num, url in tqdm(enumerate(urls)):
            await download_img(sess, url, num)
    print('Done')


if __name__ == '__main__':
    main()
