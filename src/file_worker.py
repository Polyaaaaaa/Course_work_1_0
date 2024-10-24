import json
import os
from abc import ABC, abstractmethod


class AbstractVacancyConnector(ABC):
    @abstractmethod
    def add_vacancy(self, vacancy_data):
        """Добавить вакансию."""
        pass

    @abstractmethod
    def get_vacancies(self, criteria):
        """Получить вакансии по указанным критериям."""
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy_id):
        """Удалить вакансию"""
        pass


class JSONSaver(AbstractVacancyConnector):
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump([], file)  # Создаем пустой файл

    def add_vacancy(self, vacancy_data):
        vacancy_dict = {
            "name": vacancy_data.name,
            "link": vacancy_data.link,
            "salary": vacancy_data.salary,
            "description": vacancy_data.description,
            "id": vacancy_data.id,  # Добавляем id
        }
        with open(self.filename, "r+", encoding="utf-8") as file:
            vacancies = json.load(file)
            vacancies.append(vacancy_dict)
            file.seek(0)
            json.dump(vacancies, file)
            file.truncate()

    def get_vacancies(self, criteria):
        with open(self.filename, "r", encoding="utf-8") as file:
            vacancies = json.load(file)
            result = []

            for vacancy in vacancies:
                matches = True  # Флаг для отслеживания соответствия
                for key, value in criteria.items():
                    if (
                        vacancy.get(key) != value
                    ):  # Если хоть одно значение не совпадает
                        matches = False
                        break  # Выходим из цикла, если не совпало

                if matches:
                    result.append(vacancy)

            return result

    def delete_vacancy(self, vacancy_id):
        with open(self.filename, "r+", encoding="utf-8") as file:
            vacancies = json.load(file)

            not_suitable = []

            for vacancy in vacancies:
                if vacancy.get("id") == None:
                    vacancy.get("id", "Нет айди")
                elif vacancy.get("id") != vacancy_id:
                    not_suitable.append(vacancy)

            # Перемещаем указатель файла в начало
            file.seek(0)

            # Очищаем файл
            file.truncate()

            # Записываем обновленный список вакансий в файл
            json.dump(not_suitable, file)
