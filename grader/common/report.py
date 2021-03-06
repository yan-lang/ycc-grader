from abc import ABC, abstractmethod


class BaseReport(ABC):
    TOTAL_GRADE = 100

    @property
    @abstractmethod
    def report_name(self):
        pass

    @property
    @abstractmethod
    def total_grade(self):
        pass

    @property
    @abstractmethod
    def grade(self):
        pass

    @property
    @abstractmethod
    def detail(self):
        pass


class ErrorReport(BaseReport):

    def __init__(self, report_name, total_grade, error_msg):
        self._report_name = report_name
        self._error_msg = error_msg
        self._total_grade = total_grade

    @property
    def report_name(self):
        return self._report_name

    @property
    def total_grade(self):
        return self._total_grade

    @property
    def grade(self):
        return 0

    @property
    def detail(self):
        return self._error_msg
