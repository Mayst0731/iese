import time

from category import extract_categories
from course import *
import aiohttp
import asyncio

from detail import extract_details
from final_arrangement import final_run
from test import final_cities_test
from write_to_json import write_to_json


async def start_crawl(base_url):
    session = aiohttp.ClientSession()
    category_list = await extract_categories(base_url, session)
    write_to_json(category_list, 'category/outputfiles/category_2222_EUR_XW_0226.json')
    course_list = await extract_courses(base_url,session,category_list)
    print(f'total {len(course_list)} courses')
    write_to_json(course_list, 'course/outputfiles/course_2222_EUR_XW_0226.json')
    details = await extract_details(course_list,session)
    write_to_json(details, './detail/outputfiles/comprehensive_details.json')
    final_run()
    final_cities_test()
    await session.close()
    return

if __name__ == '__main__':
    start_time = time.time()
    BASE_URL = "https://execedprograms.iese.edu/"
    asyncio.run(start_crawl(BASE_URL))
    duration = time.time() - start_time
    minutes = duration // 60
    print(f"Crawled {duration} seconds, {minutes} mins")



