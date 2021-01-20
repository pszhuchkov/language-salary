import os
import sys
import time

import requests

from dotenv import load_dotenv
from itertools import count
from requests.exceptions import ConnectionError, HTTPError
from terminaltables import AsciiTable


SERVICES_API = {
    'HeadHunter': 'https://api.hh.ru/vacancies/',
    'SuperJob': 'https://api.superjob.ru/2.0/vacancies/'
}


PROGRAMMING_LANGUAGES = [
    'JavaScript', 'Java', 'Python', 'Ruby',
    'PHP', 'C++', 'C#', 'C', 'Go', 'Scala'
]


def get_language_average_salary_hh(language, service='HeadHunter'):
    vacancy_name = f'программист {language}'
    params = {'text': vacancy_name, 'search_field': 'name', 'area': '1'}
    vacancies_found, vacancies_list = 0, []
    for page in count(0):
        params['page'] = page
        try:
            page_response = requests.get(SERVICES_API[service], params=params)
            page_response.raise_for_status()
            page_data = page_response.json()
            vacancies_list.extend(page_data['items'])
            if page == page_data['pages'] - 1:
                vacancies_found = page_data['found']
                break
        except ConnectionError as conn_err:
            print(conn_err, file=sys.stderr)
            time.sleep(5)
        except HTTPError as http_err:
            print(http_err, file=sys.stderr)
            sys.exit()
    vacancies_processed, average_salary = get_language_average_salary(
        service, vacancies_list
    )
    return {
        language:
            {
                'vacancies_found': vacancies_found,
                'vacancies_processed': vacancies_processed,
                'average_salary': average_salary
            }
    }


def get_language_average_salary_sj(language, service='SuperJob'):
    params = {
        'town': '4',
        'catalogues': '48',
        'keywords[0][keys]': 'программист',
        'keywords[0][srws]': '1',
        'keywords[0][skwc]': 'and',
        'keywords[1][keys]': language,
        'keywords[1][srws]': '1',
        'keywords[1][skwc]': 'particular'
    }
    headers = {'X-Api-App-Id': os.getenv('SUPERJOB_KEY')}
    vacancies_found, vacancies_list = 0, []
    for page in count(0):
        params['page'] = page
        try:
            page_response = requests.get(SERVICES_API[service],
                                         headers=headers, params=params)
            page_response.raise_for_status()
            page_data = page_response.json()
            vacancies_list.extend(page_data['objects'])
            if not page_data['more']:
                vacancies_found = page_data['total']
                break
        except ConnectionError as conn_err:
            print(conn_err, file=sys.stderr)
            time.sleep(5)
        except HTTPError as http_err:
            print(http_err, file=sys.stderr)
            sys.exit()
    vacancies_processed, average_salary = get_language_average_salary(
        service, vacancies_list
    )
    return {
        language:
            {
                'vacancies_found': vacancies_found,
                'vacancies_processed': vacancies_processed,
                'average_salary': average_salary
            }
    }


def get_language_average_salary(service, vacancies_list):
    predicted_salaries = []
    for vacancy in vacancies_list:
        if service == 'HeadHunter':
            predicted_salary = predict_rub_salary_hh(vacancy)
        else:
            predicted_salary = predict_rub_salary_sj(vacancy)
        if predicted_salary:
            predicted_salaries.append(predicted_salary)
    if predicted_salaries:
        vacancies_processed = len(predicted_salaries)
        average_salary = int(sum(predicted_salaries) / vacancies_processed)
        return vacancies_processed, average_salary
    return 0, None


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        return predict_salary(
            vacancy['payment_from'], vacancy['payment_to']
        )


def predict_rub_salary_hh(vacancy):
    salary_data = vacancy['salary']
    if salary_data and salary_data['currency'] == 'RUR':
        return predict_salary(
            salary_data['from'], salary_data['to']
        )


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        predicted_salary = (salary_from + salary_to) / 2
    elif salary_from:
        predicted_salary = salary_from * 1.2
    elif salary_to:
        predicted_salary = salary_to * 0.8
    else:
        return None
    return int(predicted_salary)


def print_average_salaries_table(service, average_salaries_data):
    table_data = [['Язык программирования', 'Вакансий найдено',
                   'Вакансий обработано', 'Средняя зарплата']]
    table_data.extend([
        [language, average_salaries_data[language]['vacancies_found'],
         average_salaries_data[language]['vacancies_processed'],
         average_salaries_data[language]['average_salary']]
        for language in average_salaries_data.keys()
    ])
    table_instance = AsciiTable(table_data, service)
    return table_instance.table


def main():
    load_dotenv()
    languages_average_salaries_hh = {}
    languages_average_salaries_sj = {}
    for language in PROGRAMMING_LANGUAGES:
        languages_average_salaries_hh.update(
            get_language_average_salary_hh(language)
        )
        languages_average_salaries_sj.update(
            get_language_average_salary_sj(language)
        )
    print(print_average_salaries_table('HeadHunter',
                                       languages_average_salaries_hh))
    print()
    print(print_average_salaries_table('SuperJob',
                                       languages_average_salaries_sj))


if __name__ == '__main__':
    main()
