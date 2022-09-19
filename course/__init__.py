from download_parse import download_site


async def extract_courses(url,session,cate_list):
    print('hello course')
    page = await download_site(url, session)
    course_list = []
    for cate in cate_list:
        if cate['category'] == "C-SUITE & SENIOR EXECUTIVES" or cate['category'] == 'FUNCTIONAL DIRECTORS':
            cate_name = cate['category'].upper()
            first_two_cate_courses = get_first_two_category_course(page,cate_name,cate)
            course_list += first_two_cate_courses
        else:
            page = await download_site(cate['url'], session)
            other_courses = get_other_courses(page,cate)
            course_list += other_courses
    filtered_courses = filter_courses(course_list)
    return filtered_courses


def get_first_two_category_course(page,cate_name,cate):
    lst = []
    first_single_category_element = page.find('a', text=cate_name)
    first_category_elements = first_single_category_element.find_next_sibling('ul')
    first_category_course_elements = first_category_elements.find_all('li')

    for course_element in first_category_course_elements:
        try:
            course_name = course_element.text
            course_a_tag = course_element.find('a')
            course_url = course_a_tag['href']
            course = {
               'name':course_name,
               'url':course_url,
                'category': [cate['category']],
                'category_url': [cate['url']]
            }
            lst.append(course)
        except Exception as e:
            print(e)
    return lst


def get_other_courses(page,cate):
    lst = []
    course_url_element = page.find('ul',attrs={'class':'listado_programas_home'})
    course_elements = course_url_element.find_all('li')
    for course_element in course_elements:
        course_ele = course_element.find('a')
        course_url = course_ele['href']
        course_name = course_ele.find('h5').text
        course = {"name":course_name,
                  "url":course_url,
                  "category": [cate['category']],
                  "category_url": [cate['url']]
                  }
        lst.append(course)
    return lst


def filter_courses(course_list):
    name_course_mapping = dict()
    for course in course_list:
        if course['name'] not in name_course_mapping:
            name_course_mapping[course['name']] = course
        else:
            if course['category'][0] not in name_course_mapping[course['name']]['category']:
                name_course_mapping[course['name']]['category'] += course['category']
                name_course_mapping[course['name']]['category_url'] += course['category_url']
    new_list = []
    for key, course in name_course_mapping.items():
        new_list.append(course)
    return new_list