import re
from pprint import pprint

import bs4
import requests

from detail.string_format import tackle_version_other_info, detect_language, get_start_date


def get_scroll_overview_info(page):
    info = {}
    info["desc"] = extract_overview(page)
    info["course_takeaways"] = extract_takeaways(page)
    if not info["course_takeaways"]:
        info["course_takeaways"] = get_course_takeaways(page)
    info["version_info_list"] = extract_version_info(page)
    info["who_attend_desc"] = extract_who_attend_desc(page)
    return info


def extract_who_attend_desc(page):
    who_attend_desc = ''
    try:
        who_attend_desc = page.find("div",attrs={"class":"toggle-label"},text="Is This Program Right for You?").find_next("div").text
    except:
        pass
    if not who_attend_desc:
        try:
            who_attend_desc = page.find("div",attrs={"class":"toggle-label"},text="Is this program for me?").find_next(
                "div").text
        except:
            pass

    if not who_attend_desc:
        try:
            who_attend_desc = page.find("div",attrs={"class":"toggle-label"},text="A quién va dirigido").find_next("div").text
        except:
            pass

    return who_attend_desc


def extract_overview(page):
    '''
    :param page:
    :return: overivew
    '''
    para = ''
    try:
        over_div = page.find('div',attrs={"class":"claim_inicial"})
        over_paras = over_div.find_all('p')
        for p in over_paras:
            para += p.text
    except:
        pass
    return para

def get_course_takeaways(page):
    takeaways = ''
    try:
        related_session = page.find('h2',text="Benefits")
        session = related_session.find_next('ul')
        li_sessions = session.find_all('li')
        for li in li_sessions:
            takeaways += li.text
        takeaways = takeaways.strip()
    except:
        pass
    return takeaways



def extract_takeaways(page):
    para = ''
    try:
        div = page.find('div',attrs={'class':'eightcol last'})
        lis = div.find_all('li')
        for li in lis:
            para += '*' + li.text
    except:
        pass
    return para


def is_blended(loc_session):
    blended = False
    try:
        if "Module" in loc_session.text:
            blended = True
        else:
            blended =  False
    except:
        pass
    return blended


def extract_version_info(page):
    version_info_list = []
    loc_session = page.find('div',attrs={"class":"segment clearfix cajita_datos"})
    blended_version = is_blended(loc_session)
    if blended_version:
        version = 1
        locations = get_blended_locations_en(loc_session)
        effective_start_date = get_blended_start_date(loc_session)
        version_info = {"version":version,
                        "locations":locations,
                        "effective_start_time":effective_start_date,
                        "type":"Blended-Onsite&Live-virtual"}
        version_info_list.append(version_info)
    else:
        version_info_list = get_unblended_version_info(page,loc_session)
        if len(version_info_list) == 0:
            version_info_list = extract_version_info_way2(page)
    return version_info_list


def extract_version_info_way2(page):
    versions_info = []
    try:
        loc_session = page.find('div',attrs={"class":"segment clearfix cajita_datos"})
        sessions = loc_session.find_all('p')
        version_num = len(sessions)
        tuition_info = extract_tuition_fee_info(page)
        if len(tuition_info) == 1 and len(tuition_info) < version_num:
            tuition_info = tuition_info * version_num
        for i,version in enumerate(sessions):
            location_session = version.find("strong")
            if location_session:
                 location = location_session.text
                 print(f'location: {location}')
                 left_info = version.text.replace(location, '').strip()
                 handled_left_info = tackle_version_other_info(left_info, location)
                 single_version_info = {"version": version_num,
                                        "location": location}
                 integrated_info = {**single_version_info, **handled_left_info}
                 versions_info.append(integrated_info)
    except:
        pass
    return versions_info


def get_unblended_version_info(page,loc_session):
    version_info = []
    try:
        sessions = loc_session.find_all('p')
        versions = len(sessions)
        tuition_info = extract_tuition_fee_info(page)
        if len(tuition_info) == 1 and len(tuition_info) < len(sessions):
            tuition_info = tuition_info * len(sessions)
        for i,session in enumerate(sessions):
            strong_text = ''
            location_object = session.find('strong')
            if location_object:
                strong_text = location_object.text
            else:
                location_object = session.find('b')
            if not location_object:
                location = ["Pamplona"]
            else:
                location = location_object.text
            left_info = session.text.replace(strong_text,'').strip()
            handled_left_info = tackle_version_other_info(left_info,location)
            single_version_info = {"version":versions,
                                   "location":location}
            integrated_info = {**single_version_info,**handled_left_info,**tuition_info[i]}
            version_info.append(integrated_info)
    except Exception as e:
        print(e)
    return version_info


def get_blended_locations_en(loc_session):
    location_list = []
    try:
        sessions = loc_session.find_all('p')
        for session in sessions:
            location = session.find('strong').text
            location_list.append(location)
    except:
        pass
    return location_list


def get_blended_start_date(loc_session):
    other_info = ''
    try:
        sessions = loc_session.find_all('p')
        for session in sessions:
            extract_strong = session.find('strong').extract()
            other_info = session.text
    except:
        pass
    return other_info


def extract_tuition_fee_info(page):
    try:
        fees_lst = ["Fees","fees",'Proceso de']
        toggle_labels = page.find_all("div",attrs={"class":"toggle-label"})
        fee_info_list = []
        for toggle in toggle_labels:
            text = toggle.text
            for fee in fees_lst:
                if fee in text:
                    fee_div = toggle.next_sibling
                    currency = get_currency(fee_div)
                    tuition = get_tuition(fee_div)
                    tuition_note = get_tuition_note(fee_div)
                    fee_info = {"currency":currency,
                                "tuition_number": tuition,
                                "tuition_note":tuition_note}
                    fee_info_list.append(fee_info)
    except:
        pass

    if len(fee_info_list) == 0:
        fee_info_list = [{"currency":'',
                          "tuition_number": '',
                          "tuition_note": ''}]
    return fee_info_list


def get_tuition(fee_div):
    tuition_num = ''
    try:
        general_fee = fee_div.find("ul").find_all('li')[0]
        general_fee_text = general_fee.text
        if "," in general_fee_text:
            general_fee_text = general_fee_text.replace(",",'')
            tuition_num_lst = re.findall('(\d+)', general_fee_text)
            tuition_num = tuition_num_lst[0]
        elif "." in general_fee_text:
            general_fee_text = general_fee_text.replace(".", '')
            tuition_num_lst = re.findall('(\d+)', general_fee_text)
            tuition_num = tuition_num_lst[0]
    except:
        pass
    return tuition_num


def get_currency(fee_div):
    currency = ''
    try:
        general_fee = fee_div.find("ul").find_all('li')[0]
        general_fee_text = general_fee.text
        if 'S' or '$' in general_fee_text:
            currency = 'USD'
        if '€' in general_fee_text:
            currency = 'EUR'
    except:
        pass
    return currency


def get_tuition_note(fee_div):
    tuition_note = ''
    try:
        fees = fee_div.find("ul").find_all('li')
        if len(fees) > 1:
            for fee_session in fees[1:]:
                tuition_note = "*" + fee_session.text
        if "\xa0" in tuition_note:
            tuition_note = tuition_note.replace("\xa0"," ")
    except:
        pass
    return tuition_note




# url = 'https://execedprograms.iese.edu/es/direccion-estrategica/proyectos-estrategicos/'
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_version_info(page)
# print(url)
# pprint(info)
#
# url = "https://execedprograms.iese.edu/es/direccion-estrategica/inteligencia-artificial"
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_version_info(page)
# print(url)
# pprint(info)
#
#
#
# url = 'https://execedprograms.iese.edu/leadership-people-management/high-performance-negotiator/'
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_version_info(page)
# print(url)
# pprint(info)
#
#
# url = 'https://execedprograms.iese.edu/es/direccion-estrategica/control-estrategia/'
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = extract_version_info(page)
# print(url)
# pprint(info)

# url = 'https://execedprograms.iese.edu/strategic-management/business-model-innovation-program/'
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = get_overview_info(page)
# pprint(info)