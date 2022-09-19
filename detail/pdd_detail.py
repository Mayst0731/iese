import re
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from langdetect import detect

from detail.string_format import detect_language
from detail.string_format import find_month, find_year, find_start_date, extract_date_digit

from download_parse import download_site
from pprint import pprint

import bs4
import requests


def extract_pdd_detail(page):
    desc = get_pdd_desc(page)
    version_list = get_pdd_version_info(page)
    version_num = len(version_list)
    testimonials = get_pdd_testimonials(page)
    takeaways = get_pdd_takeaways(page)
    video_info = get_pdd_video(page)
    who_attend_desc = get_pdd_who_attend_desc(page)
    language = detect_language(desc)
    overview = {"desc": desc,
                "video_title": video_info["video_title"],
                "video_url": video_info["video_url"]}

    for version in version_list:
        version["version"] = version_num
    return {"desc": overview,
            "version_info_list": version_list,
            "testimonials": testimonials,
            "course_takeaways": takeaways,
            "who_attend_desc": who_attend_desc,
            "languages": language,
            "type":"Blended-Onsite&Self-paced",
            "credential":"",
            "duration_consecutive":True}


def get_pdd_testimonials(page):
    testimonials = []
    slides = page.find('ul', attrs={"class": "slides"})
    testis = slides.find_all('li')
    for testi in testis:
        testimonial = pdd_one_testi(testi)
        testimonials.append(testimonial)
    return testimonials


def pdd_one_testi(testi):
    testimonial = {
        "publish": 100,
        "active": True,
        "name": "Anonymous",
        "title": "",
        "company": "",
        "testimonial_statement": '',
        "picture_url": "",
        "visual_url": ""
    }

    picture_img = testi.find('img')
    if picture_img:
        picture_url = picture_img.get('src')
        testimonial['picture_url'] = picture_url
    name_obj = testi.find('h3',attrs={"class":"title"})
    if name_obj:
        name = name_obj.text
        testimonial['name'] = name.title().strip()
    quote_obj = testi.find('blockquote')
    if quote_obj:
        quote = quote_obj.text
        testimonial['testimonial_statement'] = quote.strip()
    other_text_obj = testi.find('cite')
    if other_text_obj:
        other_text = other_text_obj.text
        title_company = get_pdd_title_company(name,other_text)
        title = title_company['title'].title()
        if 'Ceo' in title:
            title = title.replace('Ceo', 'CEO')
        company = title_company['company']
        testimonial['title'] = title
        testimonial['company'] = company.title()
    return testimonial


def get_pdd_title_company(name,other_text):
    title = ''
    company = ''
    if ',' in other_text:
        other_text_lst = other_text.split(',')
        title = other_text_lst[0].title()
        company = ''.join(other_text[1:])
    else:
        title = other_text
    name = name.title()
    if name in title:
        title = title.replace(name,'')

    return {"title":title,
            "company":company}


def get_pdd_takeaways(page):
    takeaways = ''
    url = page.find('div', attrs={"class": "menu-pdd-container"}).find('ul', attrs={"class": "sub-menu"}).find_all('li')[
        1].find('a').get('href')
    source = requests.get(url).content
    sub_page = bs4.BeautifulSoup(source, 'lxml')
    sub_page = bs4.BeautifulSoup(source, 'lxml')
    paras = sub_page.find('div', attrs={"class": "segment-content"}).find('div', attrs={"class": "eightcol "
                                                                                                 "last"}).find_all(
        'p')
    for para in paras:
        takeaways += para.text + '\t'
    takeaways = takeaways.strip()
    return takeaways


def get_pdd_who_attend_desc(page):
    who_attend_desc = ''
    url = page.find('a',text="¿Es para mi?").get('href')
    source = requests.get(url).content
    sub_page = bs4.BeautifulSoup(source, 'lxml')
    paras = sub_page.find('div',attrs={"class":"segment-content"}).find('div',attrs={"class":"eightcol"}).find_all('p')
    for para in paras:
        who_attend_desc += para.text + '\t'
    who_attend_desc = who_attend_desc.strip()
    return who_attend_desc


def get_pdd_video(page):
    video_title = ''
    video_url = ''
    video_session = page.find('iframe',attrs={"allowfullscreen":"allowfullscreen"})
    video_url = video_session.get('src')

    return {"video_title":video_title,
            "video_url":video_url}


def get_pdd_desc(page):
    desc = ''
    try:
        desc_div = page.find('div',attrs={'class':'tencol'}).find('p')
        desc = desc_div.text
    except:
        pass

    return desc



def get_pdd_version_info(page):
    '''
    this function is for get distince locations with corresponding start date
    :param table_session:
    :return:
    '''
    version_list = []
    location_set = set()
    location_other_info_map = mapping_location_duration_price(page)
    table_session = page.find("table")
    t_body = table_session.find('tbody')
    all_info = t_body.find_all('tr')
    for info in all_info:
        location = info.find('td',attrs={"class":"column-2"}).text.strip()
        if "(" in location:
            parenthesis_idx = location.index("(")
            location = location[:parenthesis_idx].strip()
        if location not in location_set:
            location_set.add(location)
            start_date = info.find('td',attrs={"class":"column-1"}).text
            start_date = deal_with_pdd_start_date(start_date)
            other_info = find_corresponding_other_info(location,location_other_info_map)

            loc_start_date = {"location":[location],
                              "effective_start_date":start_date}
            integrate_location_other_info = {**loc_start_date,**other_info}
            # end_date = calculate_pdd_end_date(start_date, integrate_location_other_info.get("duration_months",''))
            integrate_location_other_info["effective_end_date"] = ""
            version_list.append(integrate_location_other_info)

    return version_list


def calculate_pdd_end_date(start_date,duration_num):
    date = datetime.strptime(start_date, "%Y-%m-%d")
    mm = int(duration_num)
    end_date = date + relativedelta(months=+mm)
    end_date = end_date.strftime("%Y-%m-%d")
    return end_date


def deal_with_pdd_start_date(start_date):
    month = find_month(start_date)
    year = find_year(start_date)
    date = extract_es_pdd_date_digit(start_date)
    start_date = f'{year}-{month}-{date}'
    return start_date


def extract_es_pdd_date_digit(start_date):
    num_lst = re.findall('\d+', start_date)
    date = int(num_lst[0])
    if date < 10:
        date_str = '0' + str(date)
    else:
        date_str = str(date)
    return date_str

def mapping_location_duration_price(page):
    _map = dict()
    boxes_for_locations = page.find_all("div",attrs={"class":"box-key two"})
    for location_box in boxes_for_locations:
        location = location_box.strong.text
        duration_box = location_box.parent.next_sibling.next_sibling.next_sibling
        price_box = duration_box.next_sibling
        duration = duration_box.find('p',attrs={"class":"text"}).text
        price = price_box.find('p',attrs={"class":"text"}).text
        duration_type = "duration_" + pdd_duration_type(duration)
        duration_num = pdd_duration_num(duration)
        currency = pdd_currency(price)
        tuition = pdd_tuition(price)
        _map[location] = {duration_type:duration_num,
                         'currency':currency,
                         'tuition_number':tuition,
                         'tuition_note':''}
    return _map


def find_corresponding_other_info(location,_map):
    other_info = {}
    for loc in _map.keys():
        if location in loc:
            other_info = _map[loc]
    return other_info


def pdd_duration_type(duration):
    duration_type = ''
    es_months = "meses"
    duration = duration.lower()
    if es_months in duration:
        duration_type = "months"
    return duration_type


def pdd_duration_num(duration):
    num = ''
    num = re.findall('\d+',duration)[0]
    return num


def pdd_currency(fee):
    currency = ''
    if 'S' or '$' in fee:
        currency = 'USD'
    if '€' in fee:
        currency = 'EUR'
    return currency


def pdd_tuition(fee):
    tuition = ''
    num_lst = re.findall('\d+', fee)
    tuition = int(''.join(num_lst))
    return tuition


'''
PDD
'''

# PDD_URL = "https://executiveeducation.iese.edu/es/directores-funcionales/pdd/"
# source = requests.get(PDD_URL).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_pdd_detail(page)
# pprint(info)
# get_pdd_version_info(page)
# get_pdd_desc(page)
# get_pdd_who_attend_desc(page)
# get_pdd_takeaways(page)
# get_pdd_video(page)
# get_pdd_testimonials(page)
