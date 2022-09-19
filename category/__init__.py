import requests

from download_parse import download_site
import urllib
from pprint import pprint


async def extract_categories(url,session):
    print('hello cate')
    page = await download_site(url,session)
    nav_bar_cates = get_nav_bar_cates(page,url)
    list_cates = get_list_cates(page,url)
    cate_list = nav_bar_cates + list_cates
    return cate_list


def get_nav_bar_cates(page,url):
    cate_list = []
    first_single_category_element = page.find('a', text='C-SUITE & SENIOR EXECUTIVES')
    first_single_category_name = first_single_category_element.text
    first_single_category_url = first_single_category_element['href']

    cate = integory_into_dict(first_single_category_name,first_single_category_url,url)
    cate_list.append(cate)

    second_single_category_element = page.find('a', text='FUNCTIONAL DIRECTORS')
    second_single_category_name = second_single_category_element.text
    second_single_category_url = second_single_category_element['href']
    cate = integory_into_dict(second_single_category_name, second_single_category_url, url)
    cate_list.append(cate)
    return cate_list


def get_list_cates(page,url):
    cate_list = []

    other_category_link_elements = page.select(
        '#filtros_programas > li.filtro.filtro_1.filtro_select_programas > select')
    other_category_elements = other_category_link_elements[0].find_all('option')

    for element in other_category_elements:
        if len(element['value']) != 0:
            category_name = element.text
            category_url = get_category_url(category_name)
            cate = integory_into_dict(category_name,category_url,url)
            cate_list.append(cate)
    return cate_list


def get_category_url(name):
    name_lst = name.lower().split()
    name_str = '-'.join(name_lst)
    pre_str = 'https://execedprograms.iese.edu/?manda&filter_1='
    post_str = '&filter_2&filter_3#aqui'
    url = pre_str+name_str+post_str
    return url


def integory_into_dict(category,url,parent_url):
    dict = {'category':category,
            'url':url,
            'parent_url':parent_url}
    return dict




