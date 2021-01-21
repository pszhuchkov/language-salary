import os
import sys
import time

import requests

from dotenv import load_dotenv
from itertools import count
from requests.exceptions import ConnectionError, HTTPError
from terminaltables import AsciiTable


HH_API_URL = 'https://api.hh.ru/vacancies/'
SJ_API_URL = 'https://api.superjob.ru/2.0/vacancies/'

PROGRAMMING_LANGUAGES = [
    'JavaScript', 'Java', 'Python', 'Ruby',
    'PHP', 'C++', 'C#', 'C', 'Go', 'Scala'
]

MOSCOW_ID_HH = 1
MOSCOW_ID_SJ = 4
PROGRAMMING_CATALOG_SJ = 48
SEARCH_IN_VACANCY_NAME_SJ = 1


def get_language_average_salary_hh(language):
    vacancy_name = f'программист {language}'
    params = {
        'text': vacancy_name, 'search_field': 'name', 'area': MOSCOW_ID_HH
    }
    vacancies_found, vacancies = 0, []
    for page in count(0):
        params['page'] = page
        page_response = requests.get(HH_API_URL, params=params)
        page_response.raise_for_status()
        page_with_vacancies = page_response.json()
        vacancies.extend(page_with_vacancies['items'])
        if page >= page_with_vacancies['pages'] - 1:
            vacancies_found = page_with_vacancies['found']
            break
    vacancies_processed, average_salary = get_language_average_salary(
        vacancies, 'HeadHunter'
    )
    return {
        language:
            {
                'vacancies_found': vacancies_found,
                'vacancies_processed': vacancies_processed,
                'average_salary': average_salary
            }
    }


def get_language_average_salary_sj(language, superjob_key):
    params = {
        'town': MOSCOW_ID_SJ,
        'catalogues': PROGRAMMING_CATALOG_SJ,
        'keywords[0][keys]': 'программист',
        'keywords[0][srws]': SEARCH_IN_VACANCY_NAME_SJ,
        'keywords[0][skwc]': 'and',
        'keywords[1][keys]': language,
        'keywords[1][srws]': SEARCH_IN_VACANCY_NAME_SJ,
        'keywords[1][skwc]': 'particular'
    }
    headers = {'X-Api-App-Id': superjob_key}
    vacancies_found, vacancies = 0, []
    for page in count(0):
        params['page'] = page
        page_response = requests.get(SJ_API_URL, headers=headers,
                                     params=params)
        page_response.raise_for_status()
        page_with_vacancies = page_response.json()
        vacancies.extend(page_with_vacancies['objects'])
        if not page_with_vacancies['more']:
            vacancies_found = page_with_vacancies['total']
            break
    vacancies_processed, average_salary = get_language_average_salary(
        vacancies, 'SuperJob'
    )
    return {
        language:
            {
                'vacancies_found': vacancies_found,
                'vacancies_processed': vacancies_processed,
                'average_salary': average_salary
            }
    }


def get_language_average_salary(vacancies, service):
    predicted_salaries = []
    for vacancy in vacancies:
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


def generate_average_salaries_table(service, languages_average_salaries):
    table_average_salaries = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    ]
    table_average_salaries.extend([
        [
            language,
            vacancies_stats['vacancies_found'],
            vacancies_stats['vacancies_processed'],
            vacancies_stats['average_salary']
        ]
        for language, vacancies_stats in languages_average_salaries.items()
    ])
    table_instance = AsciiTable(table_average_salaries, service)
    return table_instance.table


def main():
    load_dotenv()
    superjob_key = os.getenv('SUPERJOB_KEY')
    languages_average_salaries_hh = {}
    languages_average_salaries_sj = {}
    try:
        for language in PROGRAMMING_LANGUAGES:
            languages_average_salaries_hh.update(
                get_language_average_salary_hh(language)
            )
            languages_average_salaries_sj.update(
                get_language_average_salary_sj(language, superjob_key)
            )
        print(generate_average_salaries_table('HeadHunter',
                                              languages_average_salaries_hh))
        print()
        print(generate_average_salaries_table('SuperJob',
                                              languages_average_salaries_sj))
    except ConnectionError as conn_err:
        print(conn_err, file=sys.stderr)
        time.sleep(3)
    except HTTPError as http_err:
        print(http_err, file=sys.stderr)
        sys.exit()


if __name__ == '__main__':
    main()
