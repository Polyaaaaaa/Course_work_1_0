import json
import os

import requests
from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, file_worker):
        self.file_worker = file_worker

    @abstractmethod
    def load_vacancies(self, keyword):
        pass


class HeadHunterAPI(Parser):
    """
    Класс для работы с API HeadHunter
    Класс Parser является родительским классом, который вам необходимо реализовать
    """

    def __init__(self, file_worker):
        self.url = 'https://api.hh.ru/vacancies'
        self.headers = {'User-Agent': 'HH-User-Agent'}
        self.params = {'text': '', 'page': 0, 'per_page': 100}
        self.vacancies = []
        super().__init__(file_worker)

    def load_vacancies(self, keyword):
        self.params['text'] = keyword
        while self.params['page'] < 20:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            if response.status_code != 200:
                print(f"Ошибка при запросе: {response.status_code}")
                return []  # Возвращаем пустой список в случае ошибки

            vacancies = response.json().get('items', [])
            if not vacancies:
                break
            self.vacancies.extend(vacancies)
            self.params['page'] += 1
        return self.vacancies


class Vacancies:
    def __init__(self, name: str, link: str, salary: int = 0, description: str = "", id: str = None):
        self.name = name
        self.link = link
        self.salary = self.validation_data(salary)
        self.description = description
        self.id = id

    def validation_data(self, salary):
        if salary is None or salary == "":
            return "Зарплата не указана"
        if not isinstance(salary, (int, float)):
            raise ValueError("Зарплата должна быть числом")
        if salary < 0:
            raise ValueError("Зарплата не может быть отрицательной")
        return salary

    @classmethod
    def cast_to_object_list(cls, vacancies_list):
        """Преобразует список вакансий в список объектов Vacancies."""
        object_list = []
        for vacancy in vacancies_list:
            obj = cls(
                name=vacancy.get("name"),
                link=vacancy.get("link"),
                salary=vacancy.get("salary", 0),
                description=vacancy.get("description", ""),
                id=vacancy.get("id")
            )
            object_list.append(obj)
        return object_list

    def __lt__(self, other):
        if not isinstance(other, Vacancies):
            return NotImplemented
        return self.salary < other.salary

    def __le__(self, other):
        if not isinstance(other, Vacancies):
            return NotImplemented
        return self.salary <= other.salary

    def __eq__(self, other):
        if not isinstance(other, Vacancies):
            return NotImplemented
        return self.salary == other.salary

    def __ne__(self, other):
        if not isinstance(other, Vacancies):
            return NotImplemented
        return self.salary != other.salary

    def __gt__(self, other):
        if not isinstance(other, Vacancies):
            return NotImplemented
        return self.salary > other.salary

    def __ge__(self, other):
        if not isinstance(other, Vacancies):
            return NotImplemented
        return self.salary >= other.salary

    def __repr__(self):
        return f"Vacancies(name={self.name}, link={self.link}, salary={self.salary}, description={self.description})"


class AbstractVacancyConnector(ABC):
    @abstractmethod
    def add_vacancy(self, vacancy_data):
        """Добавить вакансию."""
        pass

    @abstractmethod
    def get_vacancy(self, criteria):
        """Получить вакансии по указанным критериям."""
        pass

    @abstractmethod
    def del_vacancy(self, vacancy_id):
        """Удалить вакансию"""
        pass


class JSONSaver(AbstractVacancyConnector):
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as file:
                json.dump([], file) # Создаем пустой файл

    def add_vacancy(self, vacancy_data):
        vacancy_dict = {
            'name': vacancy_data.name,
            'link': vacancy_data.link,
            'salary': vacancy_data.salary,
            'description': vacancy_data.description,
            'id': vacancy_data.id  # Добавляем id
        }
        with open(self.filename, "r+") as file:
            vacancies = json.load(file)
            vacancies.append(vacancy_dict)
            file.seek(0)
            json.dump(vacancies, file)
            file.truncate()

    def get_vacancies(self, criteria):
        with open(self.filename, "r") as file:
            vacancies = json.load(file)
            result = []

            for vacancy in vacancies:
                matches = True # Флаг для отслеживания соответствия
                for key, value in criteria.items():
                    if vacancy.get(key) != value: # Если хоть одно значение не совпадает
                        matches = False
                        break # Выходим из цикла, если не совпало

                if matches:
                    result.append(vacancy)

            return result

    def delete_vacancy(self, vacancy_id):
        with open(self.filename, "r+") as file:
            vacancies = json.load(file)

            not_suitable = []

            for vacancy in vacancies:
                if vacancy.get("id") != vacancy_id:
                    not_suitable.append(vacancy)

            # Перемещаем указатель файла в начало
            file.seek(0)

            # Очищаем файл
            file.truncate()

            # Записываем обновленный список вакансий в файл
            json.dump(not_suitable, file)


# Создание экземпляра класса для работы с API сайтов с вакансиями
hh_api = HeadHunterAPI(os.path.join("src", "vacancies.json"))

# Получение вакансий с hh.ru в формате JSON
hh_vacancies = hh_api.load_vacancies("Python")

# Преобразование набора данных из JSON в список объектов
vacancies_list = Vacancies.cast_to_object_list(hh_vacancies)

# Пример работы контструктора класса с одной вакансией
vacancy = Vacancies("Python Developer", "<https://hh.ru/vacancy/123456>", 100000150000, "Требования: опыт работы от 3 лет...")

# Сохранение информации о вакансиях в файл
json_saver = JSONSaver()
json_saver.add_vacancy(vacancy)
json_saver.delete_vacancy(vacancy)


def user_interaction():
    def filter_vacancies(vacancies, filter_words):
        """Фильтрует вакансии по ключевым словам в описании."""
        filtered = []
        for vacancy in vacancies:
            if any(word.lower() in vacancy.get("description", "").lower() for word in filter_words):
                filtered.append(vacancy)
        return filtered

    def get_vacancies_by_salary(vacancies, salary_range):
        """Возвращает вакансии в заданном диапазоне зарплат."""
        if not salary_range:
            return vacancies

        min_salary, max_salary = map(int, salary_range.split('-'))
        ranged_vacancies = []

        for vacancy in vacancies:
            salary = vacancy.get("salary")
            if isinstance(salary, int) and min_salary <= salary <= max_salary:
                ranged_vacancies.append(vacancy)

        return ranged_vacancies

    def sort_vacancies(vacancies):
        """Сортирует вакансии по зарплате по убыванию."""
        return sorted(vacancies, key=lambda v: v.get("salary", 0), reverse=True)

    def get_top_vacancies(vacancies, top_n):
        """Возвращает топ N вакансий по зарплате."""
        return vacancies[:top_n]  # Возвращает первые N вакансий из отсортированного списка

    def print_vacancies(vacancies):
        """Выводит список вакансий в удобном формате."""
        if not vacancies:
            print("Вакансии не найдены.")
            return

        for vacancy in vacancies:
            print(f"Название: {vacancy.get('name')}")
            print(f"Ссылка: {vacancy.get('link')}")
            print(f"Зарплата: {vacancy.get('salary', 'Не указана')}")
            print(f"Описание: {vacancy.get('description', 'Нет описания')}")
            print("-" * 40)  # Разделитель между вакансиями

    print("Добро пожаловать в систему поиска вакансий!")

    search_query = input("Введите поисковый запрос: ")

    while True:
        try:
            top_n = int(input("Введите количество вакансий для вывода в топ N: "))
            if top_n <= 0:
                raise ValueError("Количество вакансий должно быть положительным.")
            break
        except ValueError as e:
            print(e)

    filter_words = input("Введите ключевые слова для фильтрации вакансий (через пробел): ").split()
    salary_range = input("Введите диапазон зарплат (например, 100000 - 150000): ")

    print("\nПолучение вакансий...")
    json_saver = JSONSaver(os.path.join("src", "vacancies.json"))
    vacancies_list = json_saver.get_vacancies({'text': search_query})

    filtered_vacancies = filter_vacancies(vacancies_list, filter_words)
    ranged_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)
    sorted_vacancies = sort_vacancies(ranged_vacancies)
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n)


    if top_vacancies:
        print("\nТоп вакансий по зарплате:")
        print_vacancies(top_vacancies)
    else:
        print("Вакансии не найдены по заданным критериям.")
