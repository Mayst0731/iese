from pprint import pprint

import bs4
import requests

from detail.amp_detail import extract_amp_detail, get_amp_testimonials
from detail.bap_detail import extract_bap_detail
from detail.coaching_program_detail import extract_coaching_detail
from detail.faculty_rules import extract_faculties
from detail.general_faculty_detail import get_general_faculties
from detail.global_ceo_program_detail import extract_globle_ceo_detail
from detail.overview_rules import get_scroll_overview_info
from detail.pdd_detail import extract_pdd_detail
from detail.pdg_detail import extract_pdg_detail
from detail.pmd_detail import extract_pmd_detail
from detail.testimonial_rules import get_testimonials
from detail.transformación_digital_program import extract_trans_detail
from detail.type3_detail import get_type3_detail
from download_parse import download_site


async def extract_details(course_list,session):
    courses = []
    type3_urls = ["https://online-em.iese.edu/desarrolla-talento-digital",
                  'https://online-em.iese.edu/impulsa-innovacion-idea-lanzamiento',
                  'https://online-em.iese.edu/mindset-digital',
                  'https://online-em.iese.edu/mujer-y-liderazgo']
    other_info = {"priority": 0,
                  "publish": 100,
                  "active": True,
                  "Repeatable": "Y",
                  "is_advanced_management_program": False,
                  "who_attend_params": '{"working experience": "","background knowledge": ""}'}
    course_url_set = set()
    count = 0
    for course in course_list:
        if course["url"] in course_url_set:
            continue

        elif course['url'] not in course_url_set and course['url'] == "https://execedprograms.iese.edu/strategic-management/business-model-innovation-program/":
            detail = await extract_scroll_course(course, session)
            detail.update(other_info)
            pprint(detail)
            courses.append(detail)
            course_url_set.add(course["url"])
        elif course['url'] not in course_url_set and course['url'] in type3_urls:
            print(course['url'])
            page = await download_site(course["url"],session)
            detail = get_type3_detail(page)
            detail.update(other_info)
            detail.update(course)
            courses.append(detail)
            course_url_set.add(course["url"])
        elif course["url"] not in course_url_set and course["url"] == "https://executiveeducation.iese.edu/es/consejeros-directivos-seniors/transformacion-digital/":
            print(course['url'])
            detail = await extract_nav_course(course,session)
            detail.update(other_info)
            courses.append(detail)
            course_url_set.add(course["url"])
        elif course["url"] not in course_url_set and course["url"] == "https://executiveeducation.iese.edu/csuite-senior-executives/coaching-program/":
            print(course['url'])
            detail = await extract_nav_course(course, session)
            detail.update(other_info)
            courses.append(detail)
            course_url_set.add(course["url"])
        elif course["url"] not in course_url_set and "C-Suite & Senior Executives" in course["category"] or "FUNCTIONAL DIRECTORS" in course["category"]:
            print(course['url'])
            detail = await extract_nav_course(course,session)
            detail.update(other_info)
            courses.append(detail)
            course_url_set.add(course["url"])
        elif course["url"] not in course_url_set:
            count += 1
            print(f"{count}. scroll course: {course['url']}")
            detail = await extract_scroll_course(course,session)
            detail.update(other_info)
            pprint(detail)
            courses.append(detail)
            course_url_set.add(course["url"])
    final_courses = []
    for course in courses:
        if 'university_school' not in course:
            course["university_school"] = '2222_EUR'
        if 'credential' not in course:
            course['credential'] = ''
        if 'duration_consecutive' not in course:
            course['duration_consecutive'] = True
        if 'category_tags' not in course:
            course['category_tags'] = []
        if "version_info_list" in course and len(course["version_info_list"]) > 0:
            all_version_info = course["version_info_list"]
            for version in all_version_info:
                new_course = {**course,**version}
                del new_course["version_info_list"]
                final_courses.append(new_course)
        else:
            final_courses.append(course)

    return final_courses


async def extract_nav_course(course,session):
    faculties = await get_general_faculties("https://executiveeducation.iese.edu/csuite-senior-executives/learning-experience/", session)
    amp_url = 'https://executiveeducation.iese.edu/csuite-senior-executives/advanced-management-program/'
    amp_page = await download_site(amp_url,session)

    bap_url = 'https://executiveeducation.iese.edu/functional-directors/business-acceleration-program-munich/'
    bap_page = await download_site(bap_url,session)

    pdd_url = 'https://executiveeducation.iese.edu/es/directores-funcionales/pdd/'
    pdd_page = await download_site(pdd_url,session)

    coaching_url = 'https://executiveeducation.iese.edu/csuite-senior-executives/coaching-program/'
    coaching_page = await download_site(coaching_url,session)

    global_ceo_url = 'https://executiveeducation.iese.edu/csuite-senior-executives/global-ceo-program/'
    global_ceo_page = await download_site(global_ceo_url,session)

    pdg_url = 'https://executiveeducation.iese.edu/es/consejeros-directivos-seniors/pdg/'
    pdg_page = await download_site(pdg_url,session)

    pade_url = "https://executiveeducation.iese.edu/es/consejeros-directivos-seniors/pade/"
    pade_page = await download_site(pade_url,session)

    pmd_url = 'https://executiveeducation.iese.edu/functional-directors/program-management-development/'
    pmd_page = await download_site(pmd_url,session)

    trans_url = 'https://executiveeducation.iese.edu/es/consejeros-directivos-seniors/transformacion-digital/'
    trans_page = await download_site(trans_url,session)

    amp_detail = extract_amp_detail(amp_page)
    amp_contact = get_nav_email(amp_page)
    amp_detail["exec_ed_inquiry_cc_emails"] = amp_contact

    bap_detail = extract_bap_detail(bap_page)
    bap_contact = get_nav_email(bap_page)
    bap_detail["exec_ed_inquiry_cc_emails"] = bap_contact

    coaching_detail = extract_coaching_detail(coaching_page)
    coaching_contact = get_nav_email(coaching_page)
    coaching_detail["exec_ed_inquiry_cc_emails"] = coaching_contact

    global_ceo_detail = extract_globle_ceo_detail(global_ceo_page)
    global_contact = get_nav_email(global_ceo_page)
    global_ceo_detail["exec_ed_inquiry_cc_emails"] = global_contact

    pdd_detail = extract_pdd_detail(pdd_page)
    pdd_contact = get_nav_email(pdd_page)
    pdd_detail["exec_ed_inquiry_cc_emails"] = pdd_contact

    pdg_detail = extract_pdg_detail(pdg_page)
    pdg_contact = get_nav_email(pdg_page)
    pdg_detail["exec_ed_inquiry_cc_emails"] = pdg_contact


    pade_detail = extract_pdg_detail(pade_page)
    pade_contact = get_nav_email(pade_page)
    pade_detail["exec_ed_inquiry_cc_emails"] = pade_contact


    pmd_detail = extract_pmd_detail(pmd_page)
    pmd_contact = get_nav_email(pmd_page)
    pmd_detail["exec_ed_inquiry_cc_emails"] = pmd_contact

    trans_detail = extract_trans_detail(trans_page)
    trans_contact = get_nav_email(trans_page)
    trans_detail["exec_ed_inquiry_cc_emails"] = trans_contact

    url_detail_map = {amp_url:amp_detail,
                      bap_url:bap_detail,
                      coaching_url:coaching_detail,
                      global_ceo_url:global_ceo_detail,
                      pdd_url:pdd_detail,
                      pdg_url:pdg_detail,
                      pade_url:pade_detail,
                      pmd_url:pmd_detail,
                      trans_url:trans_detail}
    if course['url'] in url_detail_map:
        detail = url_detail_map.get(course['url'])
        detail.update(course)
        detail["course_faculties"] = faculties
        return detail
    else:
        detail = await extract_scroll_course(course,session)
        return detail


async def extract_scroll_course(course,session):
    url = course['url']
    page = await download_site(url, session)
    contact_email = get_scroll_email(page)
    overview_page_info = get_scroll_overview_info(page)
    testimonials = get_testimonials(page)
    faculties = await extract_faculties(page,session)

    desc = overview_page_info["desc"]
    overview = {"desc": desc,
                "video_title": '',
                "video_url": ''}

    info =  {"overview": overview,
             "exec_ed_inquiry_cc_emails":contact_email,
             "testimonials": testimonials,
             "course_faculties": faculties}
    info.update(course)
    info.update(overview_page_info)
    return info


def get_scroll_email(page):
    email = ''
    try:
        email = page.find('a',text="Email").get('href')
    except:
        pass
    return email


def get_nav_email(page):
    email = ''
    try:
        links = page.find_all('a')
        for link in links:
            if '@' in link.text and '.' in link.text:
                email = link.get('href')
    except:
        pass
    return email

# url = 'https://executiveeducation.iese.edu/csuite-senior-executives/advanced-management-program/'
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = get_nav_email(page)
# print(info)
#
#
# url = 'https://execedprograms.iese.edu/es/direccion-estrategica/inteligencia-artificial/'
# source = requests.get(url).content
# page = bs4.BeautifulSoup(source,'lxml')
# info = get_scroll_email(page)
# print(info)






