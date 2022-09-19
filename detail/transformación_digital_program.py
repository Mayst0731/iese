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


def extract_trans_detail(page):
    desc = get_trans_desc(page)
    version_list = get_trans_version_info(page)
    version_num = len(version_list)
    testimonials = get_trans_testimonials(page)
    takeaways = get_trans_takeaways(page)
    video_info = get_trans_video(page)
    who_attend_desc = get_trans_who_attend_desc(page)
    language = detect_language(desc)
    overview = {"desc": desc,
                "video_title": video_info["video_title"],
                "video_url": video_info["video_url"]}

    for version in version_list:
        version["version"] = version_num
    return {"overview": overview,
            "version_info_list": version_list,
            "testimonials": testimonials,
            "course_takeaways": takeaways,
            "who_attend_desc": who_attend_desc,
            "languages": language}


def get_trans_testimonials(page):
    testimonials = []
    try:
        slides = page.find('ul', attrs={"class": "slides"})
        testis = slides.find_all('li')
        for testi in testis:
            testimonial = trans_one_testi(testi)
            testimonials.append(testimonial)
    except:
        pass

    return testimonials


def trans_one_testi(testi):
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
        title_company = get_trans_title_company(name,other_text)
        title = title_company['title'].title()
        if 'Ceo' in title:
            title = title.replace('Ceo', 'CEO')
        company = title_company['company']
        testimonial['title'] = title
        testimonial['company'] = company.title()
    return testimonial


def get_trans_title_company(name,other_text):
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


def get_trans_takeaways(page):
    takeaways = ''
    url = page.find('a',text="¿Qué aprenderé?").get('href')
    source = requests.get(url).content
    sub_page = bs4.BeautifulSoup(source, 'lxml')
    sub_page = bs4.BeautifulSoup(source, 'lxml')
    paras = sub_page.find('div', attrs={"class": "segment-content"}).find('div', attrs={"class": "eightcol "
                                                                                                 "last"}).find_all(
        'p')
    for para in paras:
        takeaways += para.text + '\t'
    takeaways= takeaways.strip()
    return takeaways


def get_trans_who_attend_desc(page):
    who_attend_desc = ''
    url = page.find('a',text="¿Es para mi?").get('href')
    source = requests.get(url).content
    sub_page = bs4.BeautifulSoup(source, 'lxml')
    paras = sub_page.find('div',attrs={"class":"segment-content"}).find('div',attrs={"class":"eightcol"}).find_all('p')
    for para in paras:
        who_attend_desc += para.text + '\t'
    who_attend_desc = who_attend_desc.strip()
    return who_attend_desc


def get_trans_video(page):
    video_title = ''
    video_url = ''
    try:
        video_session = page.find('iframe',attrs={"allowfullscreen":"allowfullscreen"})
        video_url = video_session.get('src')
    except:
        pass

    return {"video_title":video_title,
            "video_url":video_url}


def get_trans_desc(page):
    desc = ''
    try:
        desc_div = page.find('div',attrs={"class":"tencol"})
        desc = desc_div.text
    except:
        pass
    return desc


def get_trans_version_info(page):
    '''
    this function is for get distince locations with corresponding start date
    :param table_session:
    :return:
    '''
    version_list = []
    location = ['BARCELONA','MADRID']
    dates_info = pickup_start_end_date(page)
    start_date = dates_info['start_date']
    end_date = dates_info['end_date']
    duration_info = calculate_trans_duration_info(start_date,end_date)
    price_info = get_tuition_info(page)
    duration_num = duration_info['duration_num']
    duration_type = "duration_"+duration_info['duration_type']
    version = {"location": location,
                    "effective_start_date":start_date,
                    'effective_end_date':end_date,
                    'tuition':price_info['tuition'],
                    "currency":price_info['currency'],
                    "tuition_note":price_info['tuition_note'],
                    duration_type:duration_info['duration_num'],
                    "type":"Blended - Onsite & Live Virtual"}
    version_list.append(version)

    return version_list

def pickup_start_end_date(page):
    start_date = ''
    end_date = ''
    origin_date_text = page.find('div', attrs={"class": "box-key one"}).text
    dates_text = origin_date_text.split("|")
    dates = []
    for date_text in dates_text:
        date_text = date_text.strip()
        dates.append(date_text)
    dates = dates[1:]
    start_date = deal_with_trans_start_date(dates[0])
    end_date = deal_with_trans_start_date(dates[-1])

    return {"start_date":start_date,
            "end_date":end_date}



def deal_with_trans_start_date(start_date):
    month = find_month(start_date)
    year = find_year(start_date)
    date = extract_es_trans_date_digit(start_date)
    start_date = f'{year}-{month}-{date}'
    return start_date


def extract_es_trans_date_digit(start_date):
    num_lst = re.findall('\d+', start_date)
    date = int(num_lst[0])
    if date < 10:
        date_str = '0' + str(date)
    else:
        date_str = str(date)
    return date_str


def calculate_trans_duration_info(start_date,end_date):
    duration_type = 'months'
    duration_num = ''
    s = datetime.strptime(start_date, '%Y-%m-%d')
    e = datetime.strptime(end_date, '%Y-%m-%d')
    diff = relativedelta(e, s)
    duration_num = diff.months
    return {"duration_type":duration_type,
            "duration_num":duration_num}


def get_tuition_info(page):
    origin_price_text = page.find('div', attrs={"class": "box-key three"}).text
    tuition_list = origin_price_text.split('\n')
    currency = trans_currency(tuition_list[3])
    tuition = trans_tuition(tuition_list[3])
    tuition_note = ' '.join(tuition_list[4:])
    return {"tuition":tuition,
            "currency":currency,
            "tuition_note":tuition_note.strip()}


def trans_currency(fee):
    currency = ''
    if 'S' or '$' in fee:
        currency = 'USD'
    if '€' in fee:
        currency = 'EUR'
    return currency


def trans_tuition(fee):
    tuition = ''
    num_lst = re.findall('\d+', fee)
    tuition = int(''.join(num_lst))
    return tuition



# trans_URL = "https://executiveeducation.iese.edu/es/consejeros-directivos-seniors/transformacion-digital/"
# source = requests.get(trans_URL).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_trans_detail(page)
# pprint(info)
# get_trans_version_info(page)
# get_trans_desc(page)
# get_trans_who_attend_desc(page)
# get_trans_takeaways(page)
# get_trans_video(page)
# get_trans_testimonials(page)
