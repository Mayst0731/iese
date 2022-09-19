import copy
import json
import re
from pprint import pprint

import bs4
import requests

from detail.overview_rules import extract_tuition_fee_info
from detail.string_format import detect_language, find_month, get_duration_type
from detail.transformación_digital_program import get_trans_desc
from write_to_json import write_to_json


def final_format_detail(details):
    for detail in details:
        detail["category_tags"] = ''
        if "languages" in detail:
            detail["languages"] = language_map(detail["languages"])
        else:
            detail["languages"] = detect_language(detail["name"])
        if detail["exec_ed_inquiry_cc_emails"].startswith("mailto:"):
            detail["exec_ed_inquiry_cc_emails"] = detail["exec_ed_inquiry_cc_emails"].replace("mailto:",'')
        if "course_takeaways" not in detail:
            print(detail["url"])
        detail["credential"] = ''
        # print(f'{detail["url"]}')
        # pprint(detail["overview"])
    return details


def language_map(language):
    language = language.strip()
    language_dict = {"es":"Spanish",
                     "en":'English',
                     "it": "Italian",
                     "English":"English"}
    mapped_lang = language_dict.get(language,'English')
    return mapped_lang


def location_map(locations):
    lang = ''
    if type(locations):
        pass
    return lang


def check_attrs(details):
    detail_attrs = {'name': '',
                    'url':'',
                   'university_school': '',
                   'category': '',
                   'desc':'',
                   'active':'',
                   'type':'',
                   'category_tags':'',
                   'priority': 0,
                   'publish': 100,
                   'version': '',
                   'location': '',
                   'currency': '',
                   'tuition_number': '',
                   'tuition_note': '',
                   'Repeatable': 'Y',
                   'effective_date_start': '',
                   'effective_date_end': '',
                   'duration_consecutive': '',
                   'languages': '',
                   'credential': '',
                   'course_takeaways': '',
                   'course_faculties': [],
                   'who_attend_desc': '',
                   'overview': '',
                   'testimonials': [],
                   'exec_ed_inquiry_cc_emails':'',
                   'schedule':[]
                   }
    final_details = []
    re_scrape_course_detail = []
    for detail in details:
        rescrape_urls = ["https://execedprograms.iese.edu/strategic-management/getting-things-done/",
                          "https://execedprograms.iese.edu/strategic-management/artificial-intelligence/",
                          "https://execedprograms.iese.edu/leadership-people-management/communication-skills/"]
        if detail["url"] in rescrape_urls:
            rescrape_course = copy.deepcopy(detail)
            re_scrape_course_detail.append(rescrape_course)
            del detail
            continue
        if detail['url'] == 'https://execedprograms.iese.edu/leadership-people-management/high-performance-negotiator':
            detail['version'] = 1
            detail['location'] = 'Barcelona, ----, Spanish'
            detail['type'] = 'Onsite'
            detail["effective_date_start"] = '2021-06-05'
            detail["schedule"] = [[detail["effective_date_start"],
                                   "",
                                   "",
                                   "formal"]]
        if detail["url"] == "https://execedprograms.iese.edu/strategic-management/value-creation-effective-boards/":
            detail['version'] = 1
            detail['location'] = 'Barcelona, ----, Spanish'
            detail['type'] = 'Onsite'
            detail["effective_date_start"] = '2021-05-24'
            detail["schedule"] = [[detail["effective_date_start"],
                                   "",
                                   "",
                                   "formal"]]
        if detail["url"] == "https://execedprograms.iese.edu/leadership-people-management/positive-leader/":
            detail['version'] = 1
            detail['location'] = 'Barcelona, ----, Spanish'
            detail['type'] = 'Onsite'
            detail["effective_date_start"] = '2021-10-25'
            detail["schedule"] = [[detail["effective_date_start"],
                                   "",
                                   "",
                                   "formal"]]
        if 'tuition_note' not in detail:
            detail['tuition_note'] = ''
        duration_number = get_duration_number(detail)
        if 'tuition' in detail:
            detail['tuition_number'] = detail['tuition']
        schedule = [[
                     detail.get("effective_start_date",''),
                     detail.get("effective_end_date",''),
                     duration_number,
                     'formal'
                        ]]
        detail['effective_date_start'] = detail.get('effective_start_date','')
        detail['effective_date_end'] = detail.get('effective_end_date','')
        detail["schedule"] = schedule
        if 'overview' not in detail:
            detail["overview"] = {'desc':detail['desc'],
                                  'video_url':detail.get('video_url',''),
                                  'video_title':detail.get('video_title','')}
        if 'languages' not in detail:
            detail['languages'] = detect_language(detail["name"])

        location = detail.get('location','')
        formatted_location = format_location(location,detail["url"])
        detail["location"] = formatted_location
        # print(f'location {formatted_location}')
        type = detail.get('type','')
        formatted_type = format_type(type,location,detail['url'])
        detail['type'] = formatted_type
        if 'desc' not in detail and detail['url'] == \
                'https://executiveeducation.iese.edu/es/consejeros-directivos-seniors/transformacion-digital/':
            source = requests.get(detail['url']).content
            page = bs4.BeautifulSoup(source, 'lxml')
            detail["desc"] = get_trans_desc(page).strip()
        if 'currency' not in detail and 'tuition_number' not in detail:
            source = requests.get(detail['url']).content
            page = bs4.BeautifulSoup(source,'lxml')
            info = extract_tuition_fee_info(page)[0]
            detail['currency'] = info['currency']
            detail['tuition_number'] = info['tuition_number']
            detail['tuition_note'] = info['tuition_note']
        if 'effective_start_date' in detail:
            detail["effective_date_start"] = detail.pop('effective_start_date')
        if 'effective_end_date' in detail:
            detail["effective_date_end"] = detail.pop('effective_end_date')
        if 'mailto:' in detail["exec_ed_inquiry_cc_emails"]:
            detail["exec_ed_inquiry_cc_emails"] = detail["exec_ed_inquiry_cc_emails"].replace('mailto:','').strip()
        final_details.append(detail)

    for detail in re_scrape_course_detail:
        url = detail['url']
        source = requests.get(url).content
        page=bs4.BeautifulSoup(source,'lxml')
        ver1 = onsite_version_detail(page)
        ver2 = online_version_detail(page)
        info1 = {**detail,**ver1}
        info2 = {**detail, **ver2}
        final_details.append(info1)
        final_details.append(info2)
    course_set = set()
    for detail in final_details:
        for k in detail_attrs.keys():
            if k not in detail:
                course_set.add(detail["url"])
                print(f'{detail["url"]} no {k}')
            if 'version_info_list' in detail:
                del detail["version_info_list"]
    print(len(final_details))
    return final_details


def onsite_version_detail(page):
    location = ''
    version = 2
    effective_date_start = ''
    tuition_number = ''
    currency = ''
    tuition_note = ''
    credential = ''
    type = 'Onsite'
    effective_date_end = ''
    schedule = [["", "", "", "formal"]]
    languages = 'English'
    try:
        location = page.find('div',attrs={"class":"fourcol last"}).find('div',attrs={"class":"segment clearfix cajita_datos"}).strong.text
        location = format_location(location,'')
    except Exception as e:
        print(e)
    try:
        page.find('div', attrs={"class": "fourcol last"}).find('div', attrs={"class": "segment clearfix cajita_datos"}).strong.extract()
        start_date = page.find('div',attrs={"class":"fourcol last"}).find('div',attrs={"class":"segment clearfix cajita_datos"}).p.text

        year = re.findall('\d{4}',start_date)[0]
        date = re.findall('\d{1,2}',start_date)[0]
        if len(date) < 2:
            date = '0'+date
        month = find_month(start_date)
        effective_date_start = f'{year}-{month}-{date}'
    except Exception as e:
        print(e)
    try:
        price_related_session = page.find('div',attrs={"class":"toggle-label"},text="On-Campus Edition Admission "
                                                                                  "Process & "
                                                                             "Fees")
        price_session = price_related_session.find_next('div').find('strong',text='General fee').find_parent('li').text
        tuition_number = get_tuition_number(price_session)
        currency = get_currency_type(price_session)
        tuition_note = price_related_session.find_next('div').find('ul').text
        if 'Certificate' in tuition_note:
            credential = 'Certificate'
    except:
        pass
    try:
        schedule[0][0] = effective_date_start
        schedule[0][1] = effective_date_end
        schedule[0][2] = ''
    except:
        pass
    return {'location':location,
            'version':version,
            'tuition_number':tuition_number,
            'currency':currency,
            'tuition_note':tuition_note,
            'credential':credential,
            'effective_date_start':effective_date_start,
            'effective_date_end': effective_date_end,
            'type':type,
            'schedule':schedule,
            'languages':languages}


def online_version_detail(page):
    location = ''
    version = 2
    effective_date_start = ''
    effective_date_end = ''
    tuition_number = ''
    currency = ''
    tuition_note = ''
    credential = ''
    type = 'Online-Virtual'
    duration_type = ''
    duration_num = ''
    schedule = [["","","","formal"]]
    languages = 'English'
    try:
        location = page.find('div', attrs={"class": "fourcol last"}).find('div', attrs={"class": "segment clearfix cajita_datos"}).find_all('p')[1].strong.text
        location = format_location(location, '')
    except:
        pass
    try:
        page.find('div', attrs={"class": "fourcol last"}).find('div', attrs={"class": "segment clearfix cajita_datos"}).find_all('p')[1].strong.extract()
        start_date = page.find('div',attrs={"class":"fourcol last"}).find('div',attrs={"class":"segment clearfix cajita_datos"}).find_all('p')[1].text

        year = re.findall('\d{4}',start_date)[0]
        date = re.findall('\d{1,2}',start_date)[0]
        if len(date) < 2:
            date = '0'+date
        month = find_month(start_date)
        effective_date_start = f'{year}-{month}-{date}'
    except Exception as e:
        print(e)
    date_info = ''
    try:
        date_info = page.find('div', attrs={"class": "fourcol last"}).find('div', attrs={"class": "segment clearfix cajita_datos"}).find_all('p')[1].text
        duration_type = get_duration_type(date_info)
        duration_type = 'duration_'+duration_type
        duration_num = re.findall('\d{1}',date_info)[-1]
    except Exception as e:
        print(e)
    try:
        price_related_session = page.find('div',attrs={"class":"toggle-label"},text="Live Online Edition Admission "
                                                                                    "Process & Fees")
        price_session = price_related_session.find_next('div').find('strong',text='General fee').find_parent('li').text
        tuition_number = get_tuition_number(price_session)
        currency = get_currency_type(price_session)
        tuition_note = price_related_session.find_next('div').find('ul').text
        if 'Certificate' in tuition_note:
            credential = 'Certificate'
    except:
        pass
    try:
        schedule[0][0] = effective_date_start
        schedule[0][1] = effective_date_end
        schedule[0][2] = str(duration_num)
    except:
        pass

    info =  {'location': location,
            'version': version,
            'tuition_number': tuition_number,
            'currency': currency,
            'tuition_note': tuition_note,
            'credential': credential,
            'effective_date_start': effective_date_start,
            'effective_date_end': effective_date_end,
            'type':type,
            'schedule':schedule,
            'languages':languages}
    if 'weeks' in date_info:
        duration_info = {duration_type:duration_num}
        info.update(duration_info)
    return info


def get_tuition_number(txt):
    tuition_number = 0
    try:
        tuition_number = int(''.join(re.findall('\d+',txt)))
    except:
        pass
    return tuition_number


def get_currency_type(txt):
    currency = ''
    if 'S' or '$' in txt:
        currency = 'USD'
    if '€' in txt:
        currency = 'EUR'
    return currency


def format_type(origin_type,location,url):
    if url == 'https://execedprograms.iese.edu/leadership-people-management/communication-skills/':
        type = 'Onsite'
        return type
    if url == "https://execedprograms.iese.edu/strategic-management/value-creation-effective-boards/":
        type = "Onsite"
        return type
    type = ''
    if origin_type == "Onsite" or origin_type == "Blended-Onsite&Self-paced":
        return origin_type
    elif origin_type == "Blended - Onsite & Live Virtual" or origin_type == "Blended-Onsite&Live-virtual":
        type = 'Blended-Onsite&Virtual'
        return type
    elif origin_type == '' and 'Live online' in location:
        type = 'Online-Virtual'
    elif origin_type == '' and 'campus' in location and 'online' in location:
        type = 'Blended-Onsite&Self-paced'
    elif origin_type == '' and 'online' in location and '&' in location:
        type = 'Blended-Onsite&Self-paced'
    elif origin_type == '' and location == '':
        type = 'Blended-Onsite&Virtual'
    elif origin_type == '':
        type = 'Onsite'
    return type


def get_duration_number(detail):
    number = ''
    if 'duration_days' in detail:
        number = detail["duration_days"]
    elif 'duration_weeks' in detail:
        number = detail["duration_weeks"]
    elif 'duration_months' in detail:
        number = detail["duration_months"]
    number = str(number)
    return number


def format_location(locations,url):
    if url == 'https://execedprograms.iese.edu/leadership-people-management/communication-skills/':
        loc = "Barcelona, ----, Spain"
        return loc
    if url == "https://execedprograms.iese.edu/strategic-management/value-creation-effective-boards/":
        loc = "Barcelona, ----, Spain"
        return loc
    formatted_locations = 'Barcelona, ----, Spain'
    if locations == '':
        return "Barcelona, ----, Spain"
    location_dict = {"US - New York": "New York, NY, United States",
                     "BARCELONA": "Barcelona, ----, Spain",
                     "Madrid": "Madrid, ----, Spain",
                     "online & en campus": "Barcelona, ----, Spain",
                     "Sao Paulo": "Sao Paulo, ----, Brazil",
                     "IESE MUNICH": "Munich, ----, Germany",
                     "Zaragoza": "Zaragoza, ----, Spain",
                     "Aula virtual": "Barcelona, ----, Spain",
                     "Valencia": "Valencia, ----, Spain",
                     "Bilbao": "BILBAO, ----, Spain",
                     "Live Online": "Barcelona, ----, Spain",
                     "Online": "Barcelona, ----, Spain"}
    if type(locations) is str:
        for loc in location_dict.keys():
            if loc.title() in locations or loc in locations:
                formatted_location = location_dict[loc]
                return formatted_location
    if type(locations) is list:
        formatted_locations = []
        for location in locations:
            for loc in location_dict.keys():
                if loc.title() in location or loc in location:
                    formatted_locations.append(location_dict[loc])

    return formatted_locations


def filter_out_faculties(details):
    for detail in details:
        if len(detail['course_faculties'])>0:
            for fac in detail['course_faculties']:
                if "Academic director" in fac["name"]:
                        fac["name"] = fac["name"].replace("Academic director",'').strip()
                if "Director académico" in fac["name"]:
                        fac["name"] = fac["name"].replace("Director académico", '').strip()
                if "(Ed. Live Online)" in fac["name"]:
                    fac["name"] = fac["name"].replace("(Ed. Live Online)",'').strip()
                fac["name"] = fac["name"].strip()
                fac["intro_desc"] = fac["intro_desc"].strip()
        else:
            detail['course_faculties'] = []
    faculties = []
    faculty_set = set()
    for detail in details:
        if len(detail['course_faculties']) > 0:
            for fac in detail['course_faculties']:
                if fac["name"] not in faculty_set:
                    faculty_set.add(fac["name"])
                    faculties.append(fac)
    return faculties


def modify_faculty_in_detail(details):
    for detail in details:
        course_faculties = []
        if len(detail['course_faculties'])>0:
            for fac in detail['course_faculties']:
                course_faculties.append(fac["name"])
        detail["course_faculties"] = course_faculties
        print(f'before: {detail["languages"]}')
        detail["languages"] = language_map(detail["languages"])
        print(f'after: {detail["languages"]}')
    return details


def type_convert(type):
    type_map = {"Blended-Onsite&Virtual":"blended-ov",
                "Online-Virtual":"online-virtual",
                "Onsite":"onsite",
                "Blended-Onsite&Self-paced":"blended-os"}
    new_type = type_map.get(type,"onsite")
    return new_type


# FINAL RUN
def final_run():
    with open('./detail/outputfiles/comprehensive_details.json') as f:
        d = json.load(f)

    print(len(d))
    new_details = check_attrs(d)
    faculties = filter_out_faculties(new_details)
    final_details = modify_faculty_in_detail(new_details)
    for detail in final_details:
        if "version" not in detail:
            detail["version"] = 1
        if isinstance(detail["location"],list) and len(detail["location"]) == 0:
            detail["location"] = "Barcelona, ----, Spain"
        if isinstance(detail["location"], str) and len(detail["location"]) == 0:
            detail["location"] = "Barcelona, ----, Spain"
        if isinstance(detail["location"], str):
            detail["location"] = [detail["location"]]
        if "locations" in detail:
            del detail["locations"]
        detail["type"] = type_convert(detail["type"])
    write_to_json(faculties, 'detail/outputfiles/faculty_2222_EUR_XW_0316.json')
    write_to_json(final_details,'./detail/outputfiles/detail_2222_EUR_XW_0226.json')


final_run()

with open('./detail/outputfiles/detail_2222_EUR_XW_0226.json') as f:
    d = json.load(f)

loc_set = set()
for detail in d:
    locs = detail["location"]
    if "locations" in detail:
        print("name: ",detail["name"])
        print("locations: ", detail["locations"])
        print("location: ", detail["location"])
    if len(locs) == 0:
        print('no locs')
    if isinstance(locs, list):
        for loc in locs:
            loc_set.add(loc)
    else:
        loc_set.add(locs)
pprint(loc_set)










# info = final_format_detail(d)









