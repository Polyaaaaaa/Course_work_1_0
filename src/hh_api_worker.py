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
        self.url = "https://api.hh.ru/vacancies"
        self.headers = {"User-Agent": "HH-User-Agent"}
        self.params = {"text": "", "page": 0, "per_page": 100}
        self.vacancies = []
        super().__init__(file_worker)

    def load_vacancies(self, keyword):
        self.params["text"] = keyword
        while self.params["page"] < 20:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            if response.status_code != 200:
                print(f"Ошибка при запросе: {response.status_code}")
                return []  # Возвращаем пустой список в случае ошибки

            vacancies = response.json().get("items", [])
            if not vacancies:
                break
            self.vacancies.extend(vacancies)
            self.params["page"] += 1
        return self.vacancies
