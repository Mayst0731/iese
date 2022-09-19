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


def extract_pmd_detail(page):
    desc = get_pmd_desc(page)
    version_list = get_pmd_version_info(page)
    version_num = len(version_list)
    testimonials = get_pmd_testimonials(page)
    takeaways = get_pmd_takeaways(page)
    video_info = get_pmd_video(page)
    who_attend_desc = get_pmd_who_attend_desc(page)
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
            "credential":"",
            "duration_consecutive":True}


def get_pmd_testimonials(page):
    testimonials = []
    slides = page.find('ul', attrs={"class": "slides"})
    testis = slides.find_all('li')
    for testi in testis:
        testimonial = pmd_one_testi(testi)
        testimonials.append(testimonial)

    return testimonials


def pmd_one_testi(testi):
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
        title_company = get_pmd_title_company(name,other_text)
        title = title_company['title'].title()
        if 'Ceo' in title:
            title = title.replace('Ceo', 'CEO')
        company = title_company['company']
        testimonial['title'] = title
        testimonial['company'] = company.title()
    return testimonial


def get_pmd_title_company(name,other_text):
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


def get_pmd_takeaways(page):
    takeaways = ''
    url = page.find('div', attrs={"class": "menu-pmd-container"}).find('ul', attrs={"class": "sub-menu"}).find_all(
        'li')[
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


def get_pmd_who_attend_desc(page):
    who_attend_desc = ''
    url = page.find('a',text="Who is right for this program?").get('href')
    source = requests.get(url).content
    sub_page = bs4.BeautifulSoup(source, 'lxml')
    paras = sub_page.find('div',attrs={"class":"segment-content"}).find('div',attrs={"class":"eightcol"}).find_all('p')
    for para in paras:
        who_attend_desc += para.text + '\t'
    who_attend_desc = who_attend_desc.strip()
    return who_attend_desc


def get_pmd_video(page):
    video_title = ''
    video_url = ''
    try:
        video_session = page.find('iframe',attrs={"allowfullscreen":"allowfullscreen"})
        video_url = video_session.get('src')
    except:
        pass
    return {"video_title":video_title,
            "video_url":video_url}


def get_pmd_desc(page):
    desc = ''
    try:
        desc_div = page.find('div',attrs={'class':'tencol'}).find('p')
        desc = desc_div.text
    except:
        pass
    return desc



def get_pmd_version_info(page):
    '''
    this function is for get distince locations with corresponding start date
    :param table_session:
    :return:
    '''
    version_list = []
    ba_link = page.find('a',text="• Barcelona")
    two_loc_link = page.find('a',text="• Sao Paulo-Barcelona")
    ba_url = ba_link.get('href')
    two_loc_url = two_loc_link.get('href')
    ba_version_info = ba_version(ba_url)
    two_loc_version_info = two_loc_version(two_loc_url)
    version_list.append(ba_version_info)
    version_list.append(two_loc_version_info)

    return version_list


def ba_version(url):
    source = requests.get(url).content
    page = bs4.BeautifulSoup(source, 'lxml')
    start_date = extract_start_date(page)
    duration_info = extract_duration(page)
    location = ['Barcelona']
    duration_type = 'duration_' + duration_info["duration_type"]
    duration_num = duration_info['duration_num']
    price_info = extract_tuition_currency(page)
    currency = price_info["currency"]
    tuition = price_info["tuition"]
    end_date = calculate_pmd_end_date(start_date,duration_num)
    return {"effective_start_date":start_date,
            "effective_end_date":end_date,
            duration_type:duration_num,
            "currency":currency,
            "tuition_number":tuition,
            "tuition_note":"",
            "location":location,
            "type":"Blended-Onsite&Self-paced"}


def two_loc_version(url):
    source = requests.get(url).content
    page = bs4.BeautifulSoup(source, 'lxml')
    start_date = extract_start_date(page)
    start_date = start_date[:-4] + '01'
    duration_info = extract_duration(page)
    location = ['Barcelona','Sao Paulo']
    duration_type = 'duration_'+duration_info["duration_type"]
    duration_num = duration_info['duration_num']
    price_info = extract_tuition_currency(page)
    currency = price_info["currency"]
    tuition = price_info["tuition"]
    end_date = calculate_pmd_end_date(start_date,duration_num)
    return {"effective_start_date":start_date,
            "effective_end_date":end_date,
            duration_type:duration_num,
            "currency":currency,
            "tuition":tuition,
            "location":location}


def extract_start_date(page):
    processed_start_date = ''
    start_session_text = page.find('div',attrs={"class":"box-key three"}).find('div',
                                                                               attrs={"class":"key-content"}).find(
        'p').text
    processed_start_date = deal_with_pmd_start_date(start_session_text)
    return processed_start_date


def extract_duration(page):

    duration_session_text = page.find('div',attrs={"class":"box-key one"}).find('div',
                                                                               attrs={"class":"key-content"}).find(
        'p').text
    duration_type = pmd_duration_type(duration_session_text)
    duration_num = pmd_duration_num(duration_session_text)
    return {"duration_type":duration_type,
            "duration_num":duration_num}


def extract_tuition_currency(page):
    price_session_text = page.find('div',attrs={"class":"box-key four"}).find('div',
                                                                               attrs={"class":"key-content"}).find(
        'p').text

    currency = pmd_currency(price_session_text)
    tuition = pmd_tuition(price_session_text)
    return {"currency":currency,
            "tuition":tuition}


def calculate_pmd_end_date(start_date,duration_num):
    date = datetime.strptime(start_date, "%Y-%m-%d")
    mm = int(duration_num)
    end_date = date + relativedelta(months=+mm)
    end_date = end_date.strftime("%Y-%m-%d")
    return end_date


def deal_with_pmd_start_date(start_date):
    month = find_month(start_date)
    year = find_year(start_date)
    date = extract_es_pmd_date_digit(start_date)
    start_date = f'{year}-{month}-{date}'
    return start_date


def extract_es_pmd_date_digit(start_date):
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
        duration_type = "duration_" + pmd_duration_type(duration)
        duration_num = pmd_duration_num(duration)
        currency = pmd_currency(price)
        tuition = pmd_tuition(price)
        _map[location] = {duration_type:duration_num,
                         'currency':currency,
                         'tuition':tuition}
    return _map


def find_corresponding_other_info(location,_map):
    for loc in _map.keys():
        if location in loc:
            other_info = _map[loc]
    return other_info



def pmd_duration_type(duration):
    duration_type = ''
    es_months = "meses"
    es_months = "months"
    duration = duration.lower()
    if es_months in duration:
        duration_type = "months"
    elif es_months in duration:
        duration_type = "months"
    return duration_type


def pmd_duration_num(duration):
    num = ''
    num = re.findall('\d+',duration)[0]
    return num


def pmd_currency(fee):
    currency = ''
    if 'S' or '$' in fee:
        currency = 'USD'
    if '€' in fee:
        currency = 'EUR'
    return currency


def pmd_tuition(fee):
    tuition = ''
    num_lst = re.findall('\d+', fee)
    tuition = int(''.join(num_lst))
    return tuition


'''
PMD
'''

# PMD_URL = "https://executiveeducation.iese.edu/functional-directors/program-management-development/"
# source = requests.get(PMD_URL).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_pmd_detail(page)
# pprint(info)
# get_pmd_version_info(page)
# get_pmd_desc(page)
# get_pmd_who_attend_desc(page)
# get_pmd_takeaways(page)
# get_pmd_video(page)
# get_pmd_testimonials(page)
