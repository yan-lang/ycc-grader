from abc import ABC, abstractmethod


class AbstractReport(ABC):

    @property
    @abstractmethod
    def submitted_file_name(self):
        pass

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


class ErrorReport(AbstractReport):

    def __init__(self, submitted_file, report_name, total_grade, error_msg):
        self._submitted_file = submitted_file
        self._report_name = report_name
        self._error_msg = error_msg
        self._total_grade = total_grade

    @property
    def submitted_file_name(self):
        return self._submitted_file

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
