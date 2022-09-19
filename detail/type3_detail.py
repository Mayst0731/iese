import re
from pprint import pprint

import bs4
import requests

from detail.string_format import get_start_date, get_duration_type


def get_type3_detail(page):
    faculties = []
    testimonials = []
    start_date = get_type3_start_date(page)
    end_date = ''
    credential = 'Certificate'
    type = 'Online-Self-paced'
    duration_info = get_type3_duration(page)
    faculties = get_type3_faculies(page)
    testimonials = get_type3_testis(page)
    price_info = get_type3_price(page)
    overview = get_type3_overview(page)
    takeaways = get_type3_takeaways(page)
    who_attend_desc = get_type3_who_attend_desc(page)
    overview = {"desc":overview,
                "video_url":'',
                "video_title":""}
    info = {"desc":overview,
            "effective_start_date":start_date,
            "effective_end_date":end_date,
            "who_attend_desc":who_attend_desc,
            "course_takeaways":takeaways,
            "credential":credential,
            "type":type,
            "course_faculties":faculties,
            "testimonials":testimonials,
            "languages": "es",
            "exec_ed_inquiry_cc_emails":"",
            "version":1}
    info.update(price_info)
    info.update(duration_info)
    return info


def get_type3_start_date(page):
    start_date = ''
    try:
        date_related_session = page.find('h3',text="COMIENZA EL")
        date_session = date_related_session.find_next("p")
        start_date = date_session.text
        start_date = get_start_date(start_date,'')
    except Exception as e:
        print(e)
    return start_date


def get_type3_duration(page):
    duration_type = ''
    duration_num = ''
    try:
        duration_related_session = page.find('h3',text="DURACIÓN")
        duration_session = duration_related_session.find_next("p")
        duration_text = duration_session.text
        duration_type = get_duration_type(duration_text)
        duration_num = get_type3_duration_num(duration_text)
        duration_type = "duration_"+duration_type
        print(duration_type)
    except:
        pass

    return {duration_type:duration_num}


def get_type3_duration_num(text):
    num = re.findall('\d{1,2}',text)[0]
    return num


def get_type3_price(page):
    tuition = ''
    currency = ''
    tuition_note = ''
    try:
        price_related_session = page.find('h3', text="COSTO")
        price_session = price_related_session.find_next("p")
        price_text = price_session.text
        currency = get_type3_currency(price_text)
        tuition = ''.join(re.findall('(\d+)',price_text))
    except:
        pass

    return {"tuition_number":tuition,
            "currency":currency,
            "tuition_note":tuition_note,
            "location":'Online'}


def get_type3_currency(text):
    currency = ''
    if 'S' or '$' in text:
        currency = 'USD'
    if '€' in text:
        currency = 'EUR'
    return currency


def get_type3_overview(page):
    overview = ''
    try:
        overview = page.find("section",attrs={"data-section-type":"generic"}).text
        overview = re.sub('\s\s+', ' ', overview)
    except Exception as e:
        print(e)
    return overview


def get_type3_takeaways(page):
    takeaways = ''
    try:
        takeaways = page.find("section",attrs={"data-section-type":"program_experiences"}).text
        takeaways = re.sub('\s\s+', ' ', takeaways)
    except:
        pass
    return takeaways


def get_type3_who_attend_desc(page):
    who_attend = ''
    try:
        who_attend = page.find("section",attrs={"data-section-type":"key_takeaways"}).text
        who_attend = re.sub('\s\s+', ' ', who_attend)
    except:
        pass
    return who_attend


def get_type3_faculies(page):
    faculties = []
    try:
        fac_sessions = page.find("section",attrs={"data-section-type":"faculty_members"}).find_all("div",
                                                                                                   attrs={"class":"slider__item"})
        for fac_session in fac_sessions:
            name = ''
            title = ''
            pic_url = ''
            pdf_url = ''
            intro_desc = ''
            university_school = '2222_EUR'
            pic_url = fac_session.picture.img.get('src')
            name = fac_session.h4.text.title()
            name = re.sub('\s\s+', ' ', name)
            title_sec = fac_session.h4.find_next("p")
            if title_sec:
                title = title_sec.text
                title = re.sub('\s\s+', ' ', title)
                intro_desc = title_sec.find_next('p').text
                intro_desc = re.sub('\s\s+', ' ', intro_desc)
            fac = {'name':name,
                   "title":title,
                   "pic_url":pic_url,
                   "pdf_url":pdf_url,
                   "intro_desc":intro_desc,
                   "university_school":university_school}
            faculties.append(fac)
    except:
        pass
    return faculties

def get_type3_testis(page):
    testis = []
    try:
        testi_sessions = page.find("section",attrs={"data-section-type":"testimonials"}).find_all("div",
                                                                                                   attrs={"class":"slider__item"})

        for testi_sec in testi_sessions:
            name = ''
            title = ''
            company = ''
            testimonial_statement = ''
            picture_url =''
            visual_url = ''
            name = testi_sec.h4.text.strip()
            name = name.replace('—','').strip()
            name_lst = name.split(',')
            name = name_lst[0].strip()
            title = name_lst[1].strip()
            testimonial_statement = testi_sec.p.text.strip()
            picture_url = testi_sec.img.get("src")
            info = {"name":name,
                    "title":title,
                    "company":company,
                    "testimonial_statement":testimonial_statement,
                    "picture_url":picture_url,
                    "active":True,
                    "publish":100}
            testis.append(info)
    except:
        pass
    return testis



# url = "https://online-em.iese.edu/desarrolla-talento-digital"
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = get_type3_testis(page)
# pprint(info)
#
# url = 'https://online-em.iese.edu/impulsa-innovacion-idea-lanzamiento'
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = get_type3_testis(page)
# pprint(info)
#
# url = 'https://online-em.iese.edu/mindset-digital'
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = get_type3_testis(page)
# pprint(info)
#
# url = 'https://online-em.iese.edu/mujer-y-liderazgo'
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = get_type3_testis(page)
# pprint(info)