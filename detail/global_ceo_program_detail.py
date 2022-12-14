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


def extract_globle_ceo_detail(page):
    desc = get_globle_ceo_desc(page)
    version_list = get_globle_ceo_version_info(page)
    version_num = len(version_list)
    testimonials = get_globle_ceo_testimonials(page)
    takeaways = get_globle_ceo_takeaways(page)
    video_info = get_globle_ceo_video(page)
    who_attend_desc = get_globle_ceo_who_attend_desc(page)
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
            "duration_consecutive":True,
            "university_school":"2222_EUR",
            "type":"Onsite",
            "category_tags":[],
            'credential':''}


def get_globle_ceo_testimonials(page):
    testimonials = []
    try:
        slides = page.find('ul', attrs={"class": "slides"})
        testis = slides.find_all('li')
        for testi in testis:
            testimonial = globle_ceo_one_testi(testi)
            testimonials.append(testimonial)
    except:
        pass
    return testimonials


def globle_ceo_one_testi(testi):
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
        title_company = get_globle_ceo_title_company(name,other_text)
        title = title_company['title'].title()
        if 'Ceo' in title:
            title = title.replace('Ceo', 'CEO')
        company = title_company['company']
        testimonial['title'] = title
        testimonial['company'] = company.title()
    return testimonial


def get_globle_ceo_title_company(name,other_text):
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


def get_globle_ceo_takeaways(page):
    takeaways = ''
    url = page.find('a',text="What will you learn").get('href')
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


def get_globle_ceo_who_attend_desc(page):
    who_attend_desc = ''
    url = page.find('a',text="Who is right for this program").get('href')
    source = requests.get(url).content
    sub_page = bs4.BeautifulSoup(source, 'lxml')
    paras = sub_page.find('div',attrs={"class":"segment-content"}).find('div',attrs={"class":"eightcol"}).find_all('p')
    for para in paras:
        who_attend_desc += para.text + '\t'
    who_attend_desc = who_attend_desc.strip()
    return who_attend_desc


def get_globle_ceo_video(page):
    video_title = ''
    video_url = ''
    try:
        video_session = page.find('iframe',attrs={"allowfullscreen":"allowfullscreen"})
        video_url = video_session.get('src')
    except:
        pass

    return {"video_title":video_title,
            "video_url":video_url}


def get_globle_ceo_desc(page):
    desc = ''
    try:
        desc_div = page.find('div',attrs={'class':'tencol'}).find('p')
        desc = desc_div.text
    except:
        pass

    return desc


def get_globle_ceo_version_info(page):
    '''
    this function is for get distince locations with corresponding start date
    :param table_session:
    :return:
    '''
    version_list = []
    location = ['US - New York']
    origin_start_date = page.find('div',attrs={"class":"box-key two"}).find("div",
                                                                            attrs={"class":"key-content"}).find(
        'p').text
    start_date = deal_with_globle_ceo_start_date(origin_start_date)
    duration_info = get_duration_info(page)
    duration_type = "duration_" + duration_info['duration_type']
    end_date = calculate_globle_ceo_end_date(start_date,duration_info["duration_num"])
    price_info = get_price_info(page)
    version = {"location": location,
               "effective_start_date":start_date,
               'effective_end_date':end_date,
               'tuition_number':price_info['tuition'],
               'tuition_note':'',
               "currency":price_info['currency'],
               duration_type:duration_info['duration_num']}
    version_list.append(version)

    return version_list


def get_price_info(page):
    tuition = ''
    currency = ''
    title = page.find('div',attrs={"class":"box-key four"})
    price = title.find('div',attrs={"class":"key-content"}).find('p').text
    tuition = globle_ceo_tuition(price)
    currency = globle_ceo_currency(price)
    return {'tuition':tuition, "currency":currency}



def get_duration_info(page):
    duration_type = ''
    duration_num = ''
    duration_text = page.find('div',attrs={"class":"box-key one"}).find("div",
                                                                            attrs={"class":"key-content"}).find(
        'p').text
    duration_type = globle_ceo_duration_type(duration_text)
    duration_num = globle_ceo_duration_num(duration_text)
    return {"duration_type":duration_type,
            "duration_num":duration_num}


def calculate_globle_ceo_end_date(start_date,duration_num):
    date = datetime.strptime(start_date, "%Y-%m-%d")
    mm = int(duration_num)
    end_date = date + relativedelta(months=+mm)
    end_date = end_date.strftime("%Y-%m-%d")
    return end_date


def deal_with_globle_ceo_start_date(start_date):
    month = find_month(start_date)
    year = find_year(start_date)
    date = extract_en_globle_ceo_date_digit(start_date)
    start_date = f'{year}-{month}-{date}'
    return start_date


def extract_en_globle_ceo_date_digit(start_date):
    num_lst = re.findall('\d+', start_date)
    date = int(num_lst[0])
    if date < 10:
        date_str = '0' + str(date)
    else:
        date_str = str(date)
    if len(str(date)) == 4:
        date_str = '01'
    return date_str


def globle_ceo_duration_type(duration):
    duration_type = ''
    es_months = "meses"
    en_months = "months"
    duration = duration.lower()
    if es_months in duration or en_months in duration:
        duration_type = "months"
    return duration_type


def globle_ceo_duration_num(duration):
    num = ''
    num = re.findall('\d+',duration)[0]
    return num


def globle_ceo_currency(fee):
    currency = ''
    if 'S' or '$' in fee:
        currency = 'USD'
    if '???' in fee:
        currency = 'EUR'
    return currency


def globle_ceo_tuition(fee):
    tuition = ''
    num_lst = re.findall('\d+', fee)
    tuition = int(''.join(num_lst))
    return tuition


'''
global_ceo
'''

# global_ceo_url = "https://executiveeducation.iese.edu/csuite-senior-executives/global-ceo-program/"
# source = requests.get(global_ceo_url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_globle_ceo_detail(page)
# pprint(info)
# get_globle_ceo_version_info(page)
# get_globle_ceo_desc(page)
# get_globle_ceo_who_attend_desc(page)
# get_globle_ceo_takeaways(page)
# get_globle_ceo_video(page)
# get_globle_ceo_testimonials(page)
