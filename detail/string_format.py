import re
import datetime
from langdetect import detect


def tackle_version_other_info(other_info,location):
    start_date = ''
    end_date  =''
    start_date = get_start_date(other_info,location)
    duration_type = get_duration_type(other_info)
    duration_num = get_duration_num(other_info)
    end_date = get_end_date(other_info,start_date,duration_type,duration_num)
    if end_date == '':
        return {"effective_start_date": start_date,
            "effective_end_date": end_date}
    if duration_type == '':
        duration_type = 'days'
        duration_num = calculate_duration_num(start_date,end_date)
    duration_type = "duration_"+duration_type
    return {"effective_start_date": start_date,
            "effective_end_date": end_date,
            duration_type :duration_num}


def no_start_and_no_end(start_date,end_date):
    start_dd = start_date.split("-")[-1]

    return


def calculate_duration_num(start_date,end_date):
    start = start_date.split('-')[-1]
    end = end_date.split('-')[-1]
    diff = int(end) - int(start)
    return diff


def get_start_date(info_str,location_text):
    month = find_month(info_str)
    if month == '':
        month = find_month(location_text)
    year = find_year(info_str)
    date = find_start_date(info_str)
    if date == 'de':
        date = '01'
    start_date = f'{year}-{month}-{date}'
    return start_date


def get_end_date(other_info,start_date,duration_type,duration_num):
    year,month,date = '','',''
    if "|" in other_info:
        date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        if duration_type == "weeks":
            weeks = datetime.timedelta(weeks=int(duration_num))
            end_date = (date+weeks).date()
            end_date = end_date.strftime("%Y-%m-%d")
            return end_date
        elif duration_type == "days":
            days = datetime.timedelta(days=int(duration_num))
            end_date = (date + days).date()
            end_date = end_date.strftime("%Y-%m-%d")
            return end_date
    elif '-' in other_info:
        year = find_year(other_info)
        month = find_month(other_info)
        date = extract_end_date(other_info)
        end_date = f'{year}-{month}-{date}'
    elif '-' not in other_info and ':' not in other_info:
        year = find_year(other_info)
        month = find_month(other_info)
        date = extract_end_date(other_info)
        end_date = f'{year}-{month}-{date}'
    return end_date if date != '' else ''


def get_duration_type(info_str):
    duration_type = ""
    if "weeks" in info_str or "semanas":
        duration_type = "weeks"
    elif "months" in info_str or "meses" in info_str:
        duration_type = "months"
    elif "days" in info_str:
        duration_type = "days"
    return duration_type


def get_duration_num(other_info):
    duration_num = ''
    if "|" in other_info:
        info_lst = other_info.split("|")
        duration_info = info_lst[-1]
        duration_num_lst = re.findall('\d+', duration_info)
        duration_num = duration_num_lst[0]
    else:
        duration_num = re.findall('d{1,2}',other_info)[0]
    return duration_num


def find_month(info_str):
    en_months_check = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12',
        }
    for key in en_months_check.keys():
        if key in info_str or key.lower() in info_str or key.upper() in info_str:
            return en_months_check[key]
    es_months_check = {
    "Enero": '01',
    'Febrero': '02',
    'Marzo':'03',
    'Abril':'04',
    'Mayo':'05',
    'Junio':'06',
    'Julio':'07',
    'Agosto':'08',
    'Septiembre':'09',
    'Octubre':'10',
    'Noviembre':'11',
    'Diciembre':'12'
    }
    for key in es_months_check.keys():
        if key in info_str or key.lower() in info_str:
            return es_months_check[key]
    return ""


def find_year(info_str):
    year = re.findall('\d{4}', info_str)
    return year[0]


def find_start_date(info_str):
    date_str = ''
    try:
        if ":" in info_str:
            date_info = ' '.join(info_str.split(":")[1:])
            date_str = date_info.split(" ")[2]
            if ',' in date_str:
                date_str = date_str.strip()[:-1]
                date_str = date_dic(date_str)
        elif ":" not in info_str and "-" in info_str:
            date_lst = info_str.split("-")
            date_str = extract_date_digit(date_lst[0])
            date_str = date_dic(date_str)
        elif ":" not in info_str and "-" not in info_str and "," in info_str:
            date_str = extract_start_date(info_str)
            date_str = date_dic(date_str)
        if date_str == '':
            date_str = '01'
    except:
        pass
    if '-' in date_str:
        date_str = re.findall('\d{1,2}',info_str)[0]
        date_str = date_dic(date_str)
    return date_str


def extract_date_digit(str):
    num_lst=re.findall('\d+', str)
    return num_lst[0]


def extract_start_date(str):
    num_lst = re.findall('(\d{1,2})', str)
    start_date = min(num_lst)
    return start_date


def extract_end_date(str):
    find_year = re.findall('\d{4}', str)[0]
    if find_year:
        year_idx = str.index(find_year)
        str = str[:year_idx]
    num_lst = re.findall('\d{1,2}', str)
    if len(num_lst) > 0:
        end_date = max(num_lst)
        if int(end_date) < 10:
            end_date = '0'+end_date
    else:
        end_date = ''
    return end_date


def date_dic(date_str):
    if int(date_str) < 10:
        date_str = '0'+date_str
    return date_str

def detect_language(course_name):
    lang = detect(course_name)
    return lang

# info_str = "Start date: February 3, 2021 | 5 weeks"
# info = tackle_version_other_info(info_str,'')
# print(info)
#
#
# info_str = "June 1-4, 2021"
# info = tackle_version_other_info(info_str,'')
# print(info)
#
# info_str = '12, 19, May 10, 17, 2021'
# info = tackle_version_other_info(info_str,'')
# print(info)
#
# info_str = 'October 2021 (dates after confirmation)'
# info = tackle_version_other_info(info_str,'')
# print(info)
#
# info_str = 'Octubre de 2021 (fechas ptes. confirmación)'
# info = tackle_version_other_info(info_str,'')
# print(info)