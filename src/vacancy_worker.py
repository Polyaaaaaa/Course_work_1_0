class Vacancies:
    def __init__(
        self,
        name: str,
        link: str,
        salary: int = 0,
        description: str = "",
        id: str = None,
    ):
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
            salary = 0
            if vacancy.get("salary"):
                salary = vacancy.get("salary").get("from", 0)

            obj = cls(
                name=vacancy.get("name"),
                link=vacancy.get("alternate_url"),
                salary=salary,
                description=vacancy.get("snippet", {}).get("requirement", ""),
                id=vacancy.get("id"),
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
