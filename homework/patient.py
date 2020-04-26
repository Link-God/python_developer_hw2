from homework.log import info_logger, error_logger
import re
import datetime
import csv


def check_name_value(name: str):
    # дефисы в имени ...
    if re.search(r'[^\w\s]+', name):
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


class BaseDescriptor:
    def __init__(self, atr_name):
        self.atr_name = atr_name

    def __get__(self, instance, owner):
        return instance.__dict__[self.atr_name]


class Name(BaseDescriptor):
    def __set__(self, instance, value):
        if not instance.__dict__.get(self.atr_name):
            if not isinstance(value, str):
                error_logger.error(f'{value} must by string')
                raise TypeError
            is_good, name = check_name_value(value)
            if is_good:
                instance.__dict__[self.atr_name] = name
            else:
                error_logger.error(f'Wrong format : {name}')
                raise ValueError(f'smt wrong in {name}')
        else:
            error_logger.error(f'Try to set name of {instance}')
            raise AttributeError()


class BirthDate(BaseDescriptor):
    def __set__(self, instance, value):
        if not isinstance(value, str):
            error_logger.error(f'{value} must by string')
            raise TypeError
        is_good, date = check_date_value(value)
        if is_good:
            if instance.__dict__.get(self.atr_name):
                info_logger.info(f'For {instance} was set new birth_date = {value}')
            instance.__dict__[self.atr_name] = date
        else:
            error_logger.error(f'Wrong format : {date}')
            raise ValueError(f'smt wrong in {date}')


class Phone(BaseDescriptor):
    def __set__(self, instance, value):
        if not isinstance(value, str):
            error_logger.error(f'{value} must by string')
            raise TypeError
        is_good, phone = check_phone_value(value)
        if is_good:
            if instance.__dict__.get(self.atr_name):
                info_logger.info(f'For {instance} was set new phone = {value}')
            instance.__dict__[self.atr_name] = phone
        else:
            error_logger.error(f'Wrong format : {phone}')
            raise ValueError(f'smt wrong in {phone}')


class DocumentType(BaseDescriptor):
    possible_types = frozenset(('паспорт', 'заграничный паспорт', 'водительское удостоверение'))

    def __set__(self, instance, value):
        if not isinstance(value, str):
            error_logger.error(f'{value} must by string')
            raise TypeError
        is_good, doc_type = check_document_type_value(value, self.possible_types)
        if is_good:
            if instance.__dict__.get(self.atr_name):
                info_logger.info(f'For {instance} was set new doc_type = {value}')
            instance.__dict__[self.atr_name] = doc_type
        else:
            error_logger.error(f'Wrong format : {doc_type}')
            raise ValueError(f'smt wrong in {doc_type}')


class DocumentID(BaseDescriptor):
    def __set__(self, instance, value):
        if not isinstance(value, str):
            error_logger.error(f'{value} must by string')
            raise TypeError
        is_good, doc_id = check_document_id_value(value, instance.document_type)
        if is_good:
            if instance.__dict__.get(self.atr_name):
                info_logger.info(f'For {instance} was set new doc_id = {value}')
            instance.__dict__[self.atr_name] = doc_id
        else:
            error_logger.error(f'Wrong format : {doc_id}')
            raise ValueError(f'smt wrong in {doc_id}')


class Patient:
    # дескрипторы
    first_name = Name('first_name')
    last_name = Name('last_name')
    birth_date = BirthDate('birth_date')
    phone = Phone('phone')
    document_type = DocumentType('document_type')
    document_id = DocumentID('document_id')

    def __init__(self, first_name, last_name, birth_date, phone, document_type, document_id):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.phone = phone
        self.document_type = document_type
        self.document_id = document_id
        info_logger.info(f'patient {self} was successfully created')

    @staticmethod
    def create(*args, **kwargs):
        return Patient(*args, **kwargs)

    def save(self):
        try:
            with open("patients.csv", 'a', encoding='utf-8', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                patient = [self.first_name, self.last_name, self.birth_date, self.phone, self.document_type,
                           self.document_id]
                writer.writerow(patient)
        except FileExistsError:
            error_logger.error(f'Raise FileExistsError in save() with {self}')
        except FileNotFoundError:
            error_logger.error(f'Raise FileNotFoundError in save() with {self}')
        except IsADirectoryError:
            error_logger.error(f'Raise IsADirectoryError in save() with {self}')
        except PermissionError:
            error_logger.error(f'Raise PermissionError in save() with {self}')
        else:
            info_logger.info(f'patient {self} was successfully added to file')

    def __str__(self):
        return f'{self.first_name}, {self.last_name}, {self.birth_date}, {self.phone}, {self.document_type},' \
               f' {self.document_id}'


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
        counter = 0
        with open(self.path_to_csv_file, 'rb', buffering=0) as file:
            while True:
                line = file.readline()
                if not line or counter == n:
                    break
                yield Patient(*line.decode('utf-8').split(','))
                counter += 1
