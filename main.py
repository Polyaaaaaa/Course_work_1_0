
import os

from src.file_worker import JSONSaver
from src.hh_api_worker import HeadHunterAPI
from src.vacancy_worker import Vacancies


# Создание экземпляра класса для работы с API сайтов с вакансиями
hh_api = HeadHunterAPI(os.path.join("src", "vacancies.json"))

# Получение вакансий с hh.ru в формате JSON
hh_vacancies = hh_api.load_vacancies("Python")

# Преобразование набора данных из JSON в список объектов
vacancies_list = Vacancies.cast_to_object_list(hh_vacancies)

# Пример работы контструктора класса с одной вакансией
vacancy = Vacancies(
    "Python Developer",
    "<https://hh.ru/vacancy/123456>",
    100000150000,
    "Требования: опыт работы от 3 лет...",
)

# Сохранение информации о вакансиях в файл
json_saver = JSONSaver(os.path.join("vacancies.json"))
json_saver.add_vacancy(vacancy)
json_saver.delete_vacancy(vacancy.id)


def user_interaction():
    def filter_vacancies(vacancies, filter_words):
        """Фильтрует вакансии по ключевым словам в описании."""
        filtered = []
        for vacancy in vacancies:
            if any(
                word.lower() in vacancy.description.lower() for word in filter_words
            ):
                filtered.append(vacancy)
        return filtered

    def get_vacancies_by_salary(vacancies, salary_range):
        """Возвращает вакансии в заданном диапазоне зарплат."""
        if not salary_range:
            return vacancies

        min_salary, max_salary = map(int, salary_range.split("-"))
        ranged_vacancies = []

        for vacancy in vacancies:
            salary = vacancy.salary
            if isinstance(salary, int) and min_salary <= salary <= max_salary:
                ranged_vacancies.append(vacancy)

        return ranged_vacancies

    def sort_vacancies(vacancies):
        """Сортирует вакансии по зарплате по убыванию."""
        return sorted(vacancies, key=lambda v: v.salary, reverse=True)

    def get_top_vacancies(vacancies, top_n):
        """Возвращает топ N вакансий по зарплате."""
        return vacancies[
            :top_n
        ]  # Возвращает первые N вакансий из отсортированного списка

    def print_vacancies(vacancies):
        """Выводит список вакансий в удобном формате."""
        if not vacancies:
            print("Вакансии не найдены.")
            return

        for vacancy in vacancies:
            print(f"Название: {vacancy.name}")
            print(f"Ссылка: {vacancy.link}")
            print(
                f"Зарплата: {vacancy.salary if isinstance(vacancy.salary, int) else 'Не указана'}"
            )
            print(
                f"Описание: {vacancy.description if vacancy.description else 'Нет описания'}"
            )
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

    filter_words = input(
        "Введите ключевые слова для фильтрации вакансий (через пробел): "
    ).split()
    salary_range = input("Введите диапазон зарплат (например, 100000 - 150000): ")

    print("\nПолучение вакансий...")
    json_saver = JSONSaver(os.path.join("vacancies.json"))
    vacancies_list = json_saver.get_vacancies({"text": search_query})

    if vacancies_list is None:
        vacancies_list = []

    filtered_vacancies = filter_vacancies(vacancies_list, filter_words)
    ranged_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)
    sorted_vacancies = sort_vacancies(ranged_vacancies)
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n)

    if top_vacancies:
        print("\nТоп вакансий по зарплате:")
        print_vacancies(top_vacancies)
    else:
        print("Вакансии не найдены по заданным критериям.")


# Запуск взаимодействия с пользователем
user_interaction()
