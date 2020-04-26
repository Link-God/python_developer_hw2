import os

import pytest

from homework.config import PASSPORT_TYPE, CSV_PATH
from homework.patient import PatientCollection, Patient
from tests.constants import PATIENT_FIELDS

GOOD_PARAMS = (
    ("Кондрат", "Рюрик", "1971-01-11", "79160000000", PASSPORT_TYPE, "0228 000000"),
    ("Евпатий", "Коловрат", "1972-01-11", "79160000001", PASSPORT_TYPE, "0228 000001"),
    ("Ада", "Лавлейс", "1978-01-21", "79160000002", PASSPORT_TYPE, "0228 000002"),
    ("Миртл", "Плакса", "1880-01-11", "79160000003", PASSPORT_TYPE, "0228 000003"),
    ("Евлампия", "Фамилия", "1999-01-21", "79160000004", PASSPORT_TYPE, "0228 000004"),
    ("Кузя", "Кузьмин", "2000-01-21", "79160000005", PASSPORT_TYPE, "0228 000005"),
    ("Гарри", "Поттер", "2020-01-11", "79160000006", PASSPORT_TYPE, "0228 000006"),
    ("Рон", "Уизли", "1900-04-20", "79160000007", PASSPORT_TYPE, "0228 000007"),
    ("Билл", "Гейтс", "1978-12-31", "79160000008", PASSPORT_TYPE, "0228 000008"),
    ("Владимир", "Джугашвили", "1912-01-31", "79160000009", PASSPORT_TYPE, "0228 000009"),
    ("Вован", "ДеМорт", "1978-11-30", "79160000010", PASSPORT_TYPE, "0228 000010"),
    ("Гопник", "Районный", "1978-01-25", "79160000011", PASSPORT_TYPE, "0228 000011"),
    ("Фёдор", "Достоевский", "1978-01-05", "79160000012", PASSPORT_TYPE, "0228 000012"),
)


@pytest.fixture()
def prepare():
    with open(CSV_PATH, 'w', encoding='utf-8') as f:
        f.write('')
    for params in GOOD_PARAMS:
        Patient(*params).save()
    yield
    os.remove(CSV_PATH)


@pytest.mark.usefixtures('prepare')
def test_collection_iteration():
    collection = PatientCollection(CSV_PATH)
    for i, patient in enumerate(collection):
        true_patient = Patient(*GOOD_PARAMS[i])
        for field in PATIENT_FIELDS:
            assert getattr(patient, field) == getattr(true_patient, field), f"Wrong attr {field} for {GOOD_PARAMS[i]}"


@pytest.mark.usefixtures('prepare')
def test_limit_usual():
    collection = PatientCollection(CSV_PATH)
    try:
        len(collection.limit(8))
        assert False, "Iterator should not have __len__ method"
    except (TypeError, AttributeError):
        assert True
    for i, patient in enumerate(collection.limit(8)):
        true_patient = Patient(*GOOD_PARAMS[i])
        for field in PATIENT_FIELDS:
            assert getattr(patient, field) == getattr(true_patient,
                                                      field), f"Wrong attr {field} for {GOOD_PARAMS[i]} in limit"


@pytest.mark.usefixtures('prepare')
def test_limit_add_record():
    collection = PatientCollection(CSV_PATH)
    limit = collection.limit(len(GOOD_PARAMS) + 10)
    for _ in range(len(GOOD_PARAMS)):
        next(limit)
    new_patient = Patient("Митрофан", "Космодемьянский", "1999-10-15", "79030000000", PASSPORT_TYPE, "4510 000444")
    new_patient.save()
    last_patient = next(limit)
    for field in PATIENT_FIELDS:
        assert getattr(new_patient, field) == getattr(last_patient, field), f"Wrong attr {field} for changed limit"


@pytest.mark.usefixtures('prepare')
def test_limit_remove_records():
    collection = PatientCollection(CSV_PATH)
    limit = collection.limit(4)
    with open(CSV_PATH, 'w', encoding='utf-8') as f:
        f.write('')
    assert len([_ for _ in limit]) == 0, "Limit works wrong for empty file"
