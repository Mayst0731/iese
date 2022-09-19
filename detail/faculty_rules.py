from pprint import pprint

import bs4
import requests

from download_parse import download_site


async def extract_faculties(page,session):
    faculty_list = []
    try:
        faculty_sessions = page.find_all('div', attrs={"class": "fitxa-faculty"})
        for faculty_session in faculty_sessions:
            fac_name = faculty_session.find_all('strong')[0].text
            fac_link = faculty_session.find('a')
            if fac_link:
                fac_url = faculty_session.find('a').get('href')
            else:
                fac_url = ''
            fac_img = faculty_session.find('img').get('src')
            fac_title = faculty_session.find_all('strong')[1].text.strip()
            if '\xa0' in fac_title:
                fac_title = fac_title.replace('\xa0','')
            fac = {'name':fac_name,
                   'pic_url':fac_img,
                   'faculty_url':fac_url,
                   'title':fac_title,
                   'university_school': '2222_EUR'}
            other_info = await extract_sub_url_info(fac_url,session)
            integrated_fac = {**fac,**other_info}
            del integrated_fac["faculty_url"]
            faculty_list.append(integrated_fac)
    except Exception as e:
        print (e)
    return faculty_list


async def extract_sub_url_info(url,session):
    intro_desc = ''
    pdf_url = ''
    if len(url) != '':
        page = await download_site(url, session)
        try:
            div_obj = page.find('div',attrs = {"class":"content"})
            intro_desc = div_obj.text
        except:
            pass
        try:
            pdf_url_link = page.find('a',attrs={"class":"website"})
            pdf_url = pdf_url_link.get('href')
        except:
            pass
    return {"intro_desc":intro_desc,
            "pdf_url":pdf_url}


# url = "https://execedprograms.iese.edu/strategic-management/getting-things-done/"
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_faculties(page)
# pprint(info)
#
# url = "https://execedprograms.iese.edu/es/liderazgo-direccion-personas/comunicar-eficacia-persuasion/"
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_faculties(page)
# pprint(info)
#
# url = "https://execedprograms.iese.edu/strategic-management/artificial-intelligence/"
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_faculties(page)
# pprint(info)