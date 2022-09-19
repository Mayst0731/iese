from pprint import pprint
import bs4
import requests

from detail.faculty_rules import extract_sub_url_info
from download_parse import download_site


async def get_general_faculties(url,session):
    page = await download_site(url,session)
    faculty_list = []
    faculty_sessions = page.find_all('div', attrs={"class": "impacto"})
    for faculty_session in faculty_sessions:
        fac_name = faculty_session.find('p',attrs={"class":"titol"}).text
        fac_url = faculty_session.find('p',attrs={"class":"titol"}).a.get('href')
        fac_img = faculty_session.find('div',attrs={"class":"foto"}).find('img').get('src')
        fac_title_text = faculty_session.find('div',attrs={"class":"texto"}).text
        pre_title,mid_title,post_title = fac_title_text.partition("or")
        title = pre_title + mid_title
        sub_url_info = await extract_sub_url_info(url,session)
        fac = {'name':fac_name,
                'pic_url':fac_img,
                'faculty_url':fac_url,
                'title':title.strip(),
                "intro_desc":"",
                'university_school': '2222_EUR'}
        fac["intro_desc"] = sub_url_info['intro_desc']
        fac["pdf_url"] = sub_url_info["pdf_url"]
        del fac["faculty_url"]
        faculty_list.append(fac)
    return faculty_list

