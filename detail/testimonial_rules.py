from pprint import pprint

import bs4
import requests

from detail.pdd_detail import get_pdd_title_company


def get_testimonials(page):
    testimonials  = []
    try:
        slides = page.find('ul', attrs={"class": "slides"})
        testis = slides.find_all('li')
        for testi in testis:
            testimonial = one_testi(testi)
            if testimonial['testimonial_statement'] != '':
                testimonials.append(testimonial)
    except:
        testimonials = []
    return testimonials


def one_testi(testi):
    testimonial = {
        "publish": "public",
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
    name_obj = testi.find('h3', attrs={"class": "title"})
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
        title_company = get_pdd_title_company(name, other_text)
        title = title_company['title'].title()
        if 'Ceo' in title:
            title = title.replace('Ceo', 'CEO')
        company = title_company['company']
        testimonial['title'] = title
        testimonial['company'] = company.title()
    return testimonial


def get_title_company(name,other_text):
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


