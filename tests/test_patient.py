import functools
import os
from datetime import datetime
import itertools

import pytest

from homework.config import GOOD_LOG_FILE, ERROR_LOG_FILE, CSV_PATH, PHONE_FORMAT, PASSPORT_TYPE, PASSPORT_FORMAT, \
    INTERNATIONAL_PASSPORT_FORMAT, INTERNATIONAL_PASSPORT_TYPE, DRIVER_LICENSE_TYPE, DRIVER_LICENSE_FORMAT
from homework.patient import Patient
from tests.constants import GOOD_PARAMS, OTHER_GOOD_PARAMS, WRONG_PARAMS, PATIENT_FIELDS


def get_len(file):
    with open(file, encoding='utf-8') as f:
        return len(f.readlines())


def check_log_size(log, increased=False):
    def deco(func):
        log_map = {"error": ERROR_LOG_FILE, "good": GOOD_LOG_FILE, "csv": CSV_PATH}
        log_path = log_map.get(log, log)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_len = get_len(log_path)
            result = func(*args, **kwargs)
            new_len = get_len(log_path)
            assert new_len > log_len if increased else new_len == log_len, f"Wrong {log} file length"
            return result
        return wrapper
    return deco


def setup_module(__main__):
    for file in [GOOD_LOG_FILE, ERROR_LOG_FILE, CSV_PATH]:
        with open(file, 'w', encoding='utf-8') as f:
            f.write('')


def teardown_module(__name__):
    for file in [GOOD_LOG_FILE, ERROR_LOG_FILE, CSV_PATH]:
        os.remove(file)


@check_log_size("error")
@check_log_size("good", increased=True)
def test_creation_all_good_params():
    patient = Patient("Кондрат", "Коловрат", "1978-01-31", PHONE_FORMAT, PASSPORT_TYPE, PASSPORT_FORMAT)
    assert patient.first_name == "Кондрат", "Wrong attribute first_name"
    assert patient.last_name == "Коловрат", "Wrong attribute last_name"
    assert patient.birth_date == "1978-01-31" or patient.birth_date == datetime(1978, 1, 31), \
        "Wrong attribute birth_date"
    assert patient.phone == PHONE_FORMAT, "Wrong attribute phone"
    assert patient.document_type == PASSPORT_TYPE, "Wrong attribute document_type"
    assert patient.document_id == PASSPORT_FORMAT, "Wrong attribute document_id"

    patient = Patient("Кондрат", "Коловрат", "1978-01-31", PHONE_FORMAT, INTERNATIONAL_PASSPORT_TYPE,
                      INTERNATIONAL_PASSPORT_FORMAT)
    assert patient.document_type == INTERNATIONAL_PASSPORT_TYPE, "Wrong attribute document_type"
    assert patient.document_id == INTERNATIONAL_PASSPORT_FORMAT, "Wrong attribute document_id"

    patient = Patient("Кондрат", "Коловрат", "1978-01-31", PHONE_FORMAT, DRIVER_LICENSE_TYPE, DRIVER_LICENSE_FORMAT)
    assert patient.document_type == DRIVER_LICENSE_TYPE, "Wrong attribute document_type"
    assert patient.document_id == DRIVER_LICENSE_FORMAT, "Wrong attribute document_id"


@pytest.mark.parametrize('default,new', itertools.permutations(["(916)", "916", "-916-"], 2))
@check_log_size("error")
@check_log_size("good", increased=True)
def test_creation_acceptable_phone(default, new):
    patient = Patient("Кондрат", "Коловрат", "1978-01-31", PHONE_FORMAT.replace(default, new),
                      PASSPORT_TYPE, PASSPORT_FORMAT)
    assert patient.phone == PHONE_FORMAT, "Wrong attribute phone"


@pytest.mark.parametrize('passport', ("00 00 000 000", "0000-000000", "0 0 0 0 0 0 0 0 0 0", "0000/000-000"))
@check_log_size("error")
@check_log_size("good", increased=True)
def test_creation_acceptable_passport(passport):
    patient = Patient("Кондрат", "Коловрат", "1978-01-31", PHONE_FORMAT, PASSPORT_TYPE, passport)
    assert patient.document_id == PASSPORT_FORMAT, "Wrong attribute document_id"


@pytest.mark.parametrize('passport', ("00 0000000", "00-0000000", "0 0 0 0 0 0 0 0 0", "00/000-0000"))
@check_log_size("error")
@check_log_size("good", increased=True)
def test_creation_acceptable_international_passport(passport):
    patient = Patient("Кондрат", "Коловрат", "1978-01-31", PHONE_FORMAT, INTERNATIONAL_PASSPORT_TYPE, passport)
    assert patient.document_id == INTERNATIONAL_PASSPORT_FORMAT, "Wrong attribute document_id"


@pytest.mark.parametrize('driver_license', ("00 00 000 000", "0000-000000", "0 0 0 0 0 0 0 0 0 0", "0000/000000"))
@check_log_size("error")
@check_log_size("good", increased=True)
def test_creation_acceptable_driver_license(driver_license):
    patient = Patient("Кондрат", "Коловрат", "1978-01-31", PHONE_FORMAT, DRIVER_LICENSE_TYPE, driver_license)
    assert patient.document_id == DRIVER_LICENSE_FORMAT, "Wrong attribute document_id"


# неверный тип
@pytest.mark.parametrize("i", list(range(len(GOOD_PARAMS))))
@check_log_size("error", increased=True)
@check_log_size("good")
def test_creation_wrong_type_params(i):
        try:
            Patient(*GOOD_PARAMS[:i], 1.8, *GOOD_PARAMS[i+1:])
            assert False, f"TypeError for {PATIENT_FIELDS[i]} not invoked"
        except TypeError:
            assert True


# неверные значения
@pytest.mark.parametrize("i", list(range(len(GOOD_PARAMS))))
@check_log_size("error", increased=True)
@check_log_size("good")
def test_creation_wrong_params(i):
    try:
        Patient(*GOOD_PARAMS[:i], WRONG_PARAMS[i], *GOOD_PARAMS[i+1:])
        assert False, f"ValueError for {PATIENT_FIELDS[i]} not invoked"
    except ValueError:
        assert True


# метод create
@check_log_size("error")
@check_log_size("good", increased=True)
def test_create_method_good_params():
    patient = Patient.create(*GOOD_PARAMS)
    for param, field in zip(GOOD_PARAMS, PATIENT_FIELDS):
        assert getattr(patient, field) in (param, datetime(1978, 1, 31)), f"Wrong attribute {field}"


# обновление параметров
@pytest.mark.parametrize("patient,field,param", zip(
    [Patient(*OTHER_GOOD_PARAMS)] * len(PATIENT_FIELDS[:2]),
    PATIENT_FIELDS[:2],
    GOOD_PARAMS[:2]
))
@check_log_size("error", increased=True)
@check_log_size("good")
def test_names_assignment(patient, field, param):
    try:
        setattr(patient, field, param)
        assert False, f"Attribute error should be invoked for {field} changing"
    except AttributeError:
        assert True


@pytest.mark.parametrize("patient,field,param", zip(
    [Patient(*OTHER_GOOD_PARAMS)] * len(PATIENT_FIELDS[2:]),
    PATIENT_FIELDS[2:],
    GOOD_PARAMS[2:]
))
@check_log_size("error")
@check_log_size("good", increased=True)
def test_good_params_assignment(patient, field, param):
    setattr(patient, field, param)
    assert getattr(patient, field) == param, f"Attribute {field} did not change"


@pytest.mark.parametrize("patient,field,param", zip(
    [Patient(*OTHER_GOOD_PARAMS)] * len(PATIENT_FIELDS[2:]),
    PATIENT_FIELDS[2:],
    [1.4] * len(PATIENT_FIELDS[2:])
))
@check_log_size("error", increased=True)
@check_log_size("good")
def test_wrong_type_assignment(patient, field, param):
    try:
        setattr(patient, field, param)
        assert False, f"TypeError for {field} assignment not invoked"
    except TypeError:
        assert True


@pytest.mark.parametrize("patient,field,param", zip(
    [Patient(*OTHER_GOOD_PARAMS)] * len(PATIENT_FIELDS[2:]),
    PATIENT_FIELDS[2:],
    WRONG_PARAMS[2:]
))
@check_log_size("error", increased=True)
@check_log_size("good")
def test_wrong_value_assignment(patient, field, param):
    try:
        setattr(patient, field, param)
        assert False, f"ValueError for {field} assignment not invoked"
    except ValueError:
        assert True


# метод save
@check_log_size("csv", increased=True)
def test_save():
    patient = Patient(*GOOD_PARAMS)
    patient.save()
