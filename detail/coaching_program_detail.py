import re
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from langdetect import detect
from pip._vendor.msgpack import Timestamp

from detail.string_format import detect_language
from detail.string_format import find_month, find_year, find_start_date, extract_date_digit

from download_parse import download_site
from pprint import pprint

import bs4
import requests


def extract_coaching_detail(page):
    desc = get_coaching_desc(page)
    version_list = get_coaching_version_info(page)
    version_num = len(version_list)
    testimonials = get_coaching_testimonials(page)
    takeaways = get_coaching_takeaways(page)
    video_info = get_coaching_video(page)
    who_attend_desc = get_coaching_who_attend_desc(page)
    language = detect_language(desc)
    faculty = get_coaching_faculty(page)
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
            "university_school":"2222_EUR",
            "credential":"",
            "duration_consecutive":''}



def get_coaching_testimonials(page):
    testimonials = []
    slides = page.find('ul', attrs={"class": "slides"})
    testis = slides.find_all('li')
    for testi in testis:
        testimonial = coaching_one_testi(testi)
        testimonials.append(testimonial)

    return testimonials


def coaching_one_testi(testi):
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
        title_company = get_coaching_title_company(name,other_text)
        title = title_company['title'].title()
        if 'Ceo' in title:
            title = title.replace('Ceo', 'CEO')
        company = title_company['company']
        testimonial['title'] = title
        testimonial['company'] = company.title()
    return testimonial


def get_coaching_title_company(name,other_text):
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


def get_coaching_takeaways(page):
    takeaways = ''
    try:
        takeaways_session_person = page.find('div',attrs={"class":"sixcol"}).find_all('li')
        takeaways_session_company = page.find('div', attrs={"class": "sixcol last"}).find_all('li')
        takeaways_sessions = takeaways_session_person + takeaways_session_company
        for takeaways_session in takeaways_sessions:
            takeaways += takeaways_session.text
    except:
        pass

    return takeaways


def get_coaching_who_attend_desc(page):
    who_attend_desc = ''
    try:
        url = page.find('div',text="Who is right for this program?").get('href')
        source = requests.get(url).content
        sub_page = bs4.BeautifulSoup(source, 'lxml')
        paras = sub_page.find('div',attrs={"class":"segment-content"}).find('div',attrs={"class":"eightcol"}).find_all('p')
        for para in paras:
            who_attend_desc += para.text + '\t'
    except:
        pass

    return who_attend_desc


def get_coaching_video(page):
    video_title = ''
    video_url = ''
    try:
        video_session = page.find('iframe',attrs={"allowfullscreen":"allowfullscreen"})
        video_url = video_session.get('src')
    except:
        pass

    return {"video_title":video_title,
            "video_url":video_url}


def get_coaching_desc(page):
    desc = ''
    try:
        desc_div = page.find('div',attrs={'class':'segment-content'}).find('p')
        desc = desc_div.text
    except:
        pass
    return desc


def get_coaching_version_info(page):
    '''
    this function is for get distince locations with corresponding start date
    :param table_session:
    :return:
    '''
    version_list = []
    start_date = extract_coaching_start_date(page)
    end_date = extract_coaching_end_date(page)
    price_info = extract_tuition_currency(page)
    currency = price_info['currency']
    tuition = price_info['tuition']
    location = get_location(page)
    version_info = {"effective_start_date": start_date,
                     "effective_end_date": end_date,
                     "duration_weeks": 8,
                     "currency": currency,
                     "tuition_number": tuition,
                     "tuition_note":"",
                     "location":location,
                    "type":"Blended - Onsite & Live Virtual"}
    version_list.append(version_info)

    return version_list


def get_location(page):
    location = ''
    try:
        loc_session_text = page.find('div', attrs={"class": "locale"}).find("p",attrs={"class":"city"}).text
        location = loc_session_text
    except:
        return []
    return [location]


def extract_coaching_start_date(page):
    start_date = ''
    try:
        start_date_text = page.find('div',attrs={"class":"flip-container"}).find("div",attrs={"class":"front"}).find("p",
                                                                                                                 attrs={"class":"info"}).text
        month = find_month(start_date_text)
        year = find_year(start_date_text)
        date = find_coaching_start_date(start_date_text)
        start_date = f'{year}-{month}-{date}'
    except:
        pass
    return start_date


def find_coaching_start_date(start_date_text):
    num_lst = re.findall('(\d{1,2})', start_date_text)
    start_date = min(num_lst)
    return start_date


def extract_coaching_end_date(page):
    end_date = ''
    try:
        end_date_text = page.find_all('div',attrs={"class":"flip-container"})[2].find("div",attrs={"class":"front"}).find(
        "p",attrs={"class":"info"}).text
        month = find_month(end_date_text)
        year = find_year(end_date_text)
        date = find_coaching_end_date(end_date_text)
        end_date = f'{year}-{month}-{date}'
    except:
        pass
    return end_date


def find_coaching_end_date(end_date_text):
    num_lst = re.findall('(\d{1,2})', end_date_text)
    end_date = max(num_lst)
    return end_date


def extract_tuition_currency(page):
    currency = "EUR"
    tuition = 0
    try:
        price_session_text = page.find('div',attrs={"class":"box-key four"}).find('div', attrs={"class":"key-content"}).find('p').text

        currency = coaching_currency(price_session_text)
        tuition = coaching_tuition(price_session_text)
    except:
        pass
    return {"currency":currency,
            "tuition":tuition}


def deal_with_coaching_start_date(start_date):
    month = find_month(start_date)
    year = find_year(start_date)
    date = extract_en_coaching_date_digit(start_date)
    start_date = f'{year}-{month}-{date}'
    return start_date


def extract_en_coaching_date_digit(start_date):
    num_lst = re.findall('\d+', start_date)
    date = int(num_lst[0])
    if date < 10:
        date_str = '0' + str(date)
    else:
        date_str = str(date)
    return date_str



def coaching_currency(fee):
    currency = ''
    if 'S' or '$' in fee:
        currency = 'USD'
    if '€' in fee:
        currency = 'EUR'
    return currency


def coaching_tuition(fee):
    tuition = ''
    num_lst = re.findall('\d+', fee)
    tuition = int(''.join(num_lst))
    return tuition


def get_coaching_faculty(page):
    faculty_list = []
    faculty_sessions = page.find_all("div",attrs={"class":"segment-content"})[6].find_all("div",
                                                                                          attrs={"class":"fourcol"})
    faculty_sessions += page.find_all("div",attrs={"class":"segment-content"})[6].find_all("div",
                                                                                          attrs={"class":"fourcol "
                                                                                                         "last"})
    for faculty_session in faculty_sessions:
        faculty = extract_faculty_info(faculty_session)
        if faculty:
            faculty_list.append(faculty)
    return faculty_list


def extract_faculty_info(faculty_session):
    try:
        name = faculty_session.find_all('p')[0].strong.text.strip()
    except:
        return
    try:
        faculty_session.find_all('p')[0].strong.extract
        text = faculty_session.find_all('p')[0].text
        title, ending_words, company = text.partition("or")
    except:
        title,company = '',''
    if name in title:
        title = title.replace(name,"").strip()
    pic_url = faculty_session.find('img').get("src")
    faculty = {"name": name, "title": title + "or", "intro_desc": "", "pic_url": "", "university_school": "2222_EUR",
               'pic_url': pic_url}
    return faculty

'''
Coaching programm
'''

# coaching_prog_url = "https://executiveeducation.iese.edu/csuite-senior-executives/coaching-program/"
# source = requests.get(coaching_prog_url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_coaching_detail(page)
# pprint(info)
# get_coaching_version_info(page)
# get_coaching_desc(page)
# get_coaching_who_attend_desc(page)
# get_coaching_takeaways(page)
# get_coaching_video(page)
# get_coaching_testimonials(page)
# get_coaching_faculty(page)

