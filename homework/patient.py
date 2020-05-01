import logging
import homework.log
import re
import datetime
import csv
from functools import partial, wraps
from itertools import islice


def check_name_value(name: str):
    # дефисы в имени ...
    if re.search(r'[^a-zA-Zа-яёА-ЯЁ\s]+', name):
        return False, name
    return True, name.capitalize()


def check_date_value(date: str):
    if re.match(r'\d{4}-\d{2}-\d{2}', re.sub(r'\s+', '', date)) is None:
        return False, date
    else:
        try:
            dt_date = datetime.date.fromisoformat(date)
        except ValueError:
            return False, date
        return True, dt_date.isoformat()


def check_phone_value(phone: str):
    if re.search(r'[^\d()\-+]', re.sub(r'\s+', '', phone)):
        return False, phone
    phone = ''.join(re.findall(r'\d+', phone))
    if len(phone) == 11:
        return True, '7' + phone[1:]
    else:
        return False, phone


def check_document_type_value(doc_type: str, possible_types: frozenset):
    if doc_type.lower() in possible_types:
        return True, doc_type.lower()
    else:
        return False, doc_type


def check_document_id_value(doc_id: str, doc_type: str):
    if re.search(r'[^\d/\-]', re.sub(r'\s+', '', doc_id)):
        return False, doc_id
    doc_id = ''.join(re.findall(r'\d', doc_id))
    if doc_type == 'заграничный паспорт' and len(doc_id) == 9:
        return True, doc_id
    elif doc_type in {'паспорт', 'водительское удостоверение'} and len(doc_id) == 10:
        return True, doc_id
    else:
        return False, doc_id


def set_method_logger(func):
    @wraps(func)
    def wrapper(self, instance, value, check_func, able_for_change=True):
        new_value = value
        try:
            func(self, instance, value, check_func, able_for_change)
            _, new_value = check_func(value)
        except TypeError:
            instance.error_logger.error(f'{value} must by string')
            raise TypeError
        except ValueError:
            instance.error_logger.error(f'Wrong format : {new_value}')
            raise ValueError
        except AttributeError:
            instance.error_logger.error(f'Try to set {self.atr_name} of {instance}')
            raise AttributeError
        else:
            # не  инициализация, а изменение
            if instance:
                instance.info_logger.info(f'For {instance} was set new {self.atr_name} = {new_value}')

    return wrapper


def file_method_logger(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except FileExistsError:
            self.error_logger.error(f'Raise FileExistsError in save() with {self}')
        except FileNotFoundError:
            self.error_logger.error(f'Raise FileNotFoundError in save() with {self}')
        except IsADirectoryError:
            self.error_logger.error(f'Raise IsADirectoryError in save() with {self}')
        except PermissionError:
            self.error_logger.error(f'Raise PermissionError in save() with {self}')
        else:
            self.info_logger.info(f'patient {self} was successfully added to file')

    return wrapper


class BaseDescriptor:
    def __init__(self, atr_name):
        self.atr_name = atr_name

    def __get__(self, instance, owner):
        value = instance.__dict__.get(self.atr_name)
        if value:
            return value
        else:
            # вроде не нарушает логику и нужно для hasattr()
            raise AttributeError

    @set_method_logger
    def _set(self, instance, value, check_func, able_for_change=True):
        if not able_for_change and hasattr(instance, self.atr_name):
            raise AttributeError
        if not isinstance(value, str):
            raise TypeError
        is_good, new_value = check_func(value)
        if is_good:
            instance.__dict__[self.atr_name] = new_value
        else:
            raise ValueError


class Name(BaseDescriptor):
    def __set__(self, instance, value):
        self._set(instance, value, check_name_value, False)


class BirthDate(BaseDescriptor):
    def __set__(self, instance, value):
        self._set(instance, value, check_date_value)


class Phone(BaseDescriptor):
    def __set__(self, instance, value):
        self._set(instance, value, check_phone_value)


class DocumentType(BaseDescriptor):
    possible_types = frozenset(('паспорт', 'заграничный паспорт', 'водительское удостоверение'))

    def __set__(self, instance, value):
        partial_check_func = partial(check_document_type_value, possible_types=self.possible_types)
        self._set(instance, value, partial_check_func)


class DocumentID(BaseDescriptor):
    def __set__(self, instance, value):
        partial_check_func = partial(check_document_id_value, doc_type=instance.document_type)
        self._set(instance, value, partial_check_func)


class Patient:
    # дескрипторы
    first_name = Name('first_name')
    last_name = Name('last_name')
    birth_date = BirthDate('birth_date')
    phone = Phone('phone')
    document_type = DocumentType('document_type')
    document_id = DocumentID('document_id')

    def __init__(self, first_name, last_name, birth_date, phone, document_type, document_id):
        self.info_logger = logging.getLogger('Info_Logger')
        self.error_logger = logging.getLogger('Error_Logger')
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.phone = phone
        self.document_type = document_type
        self.document_id = document_id
        self.info_logger.info(f'patient {self} was successfully created')

    @staticmethod
    def create(*args, **kwargs):
        return Patient(*args, **kwargs)

    @file_method_logger
    def save(self):
        with open("patients.csv", 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            patient = [self.first_name, self.last_name, self.birth_date, self.phone, self.document_type,
                       self.document_id]
            writer.writerow(patient)

    def __str__(self):
        return f'{self.first_name}, {self.last_name}, {self.birth_date}, {self.phone}, {self.document_type},' \
               f' {self.document_id}'

    def __bool__(self):
        # проверка на то все ли инициализированны
        attrs = filter(lambda atr: not atr.startswith('__'), dir(self))
        return all((hasattr(self, atr) for atr in attrs))


class PatientCollection:
    def __init__(self, path_to_file):
        self.path_to_csv_file = path_to_file

    def __iter__(self):
        with open(self.path_to_csv_file, 'rb', buffering=0) as file:
            while True:
                line = file.readline()
                if not line:
                    break
                yield Patient(*line.decode('utf-8').split(','))

    def limit(self, n):
        # наверно более красиво, очевидно и по питоняче
        return islice(self, n)
