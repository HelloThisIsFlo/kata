import pytest
from schema import Schema, Optional, SchemaError

from kata.domain.exceptions import InvalidConfig


def test_simple_nested_dict():
    schema = Schema({'KataGRepo': {'User': str,
                                   'Repo': str}})

    assert not schema.is_valid({})
    assert not schema.is_valid({'KataGRepo': {}})
    assert not schema.is_valid({'KataGRepo': {'User': 'frank'}})
    assert not schema.is_valid({'KataGRepo': {'User': 22,
                                              'Repo': 'test'}})

    assert schema.is_valid({'KataGRepo': {'User': 'frank',
                                          'Repo': 'test'}})


def test_unlimited_keys_in_sub_dict():
    schema = Schema({'MyKey': {str: int}})

    assert not schema.is_valid({'MyKey': {}})
    assert not schema.is_valid({'MyKey': {'test': 'not a int'}})

    assert schema.is_valid({'MyKey': {'test': 24}})
    assert schema.is_valid({'MyKey': {'test': 24,
                                      'other': 4,
                                      'last': 11}})


def test_optional():
    schema = Schema({'MyKey': {Optional(str): int}})

    assert schema.is_valid({'MyKey': {}})
    assert schema.is_valid({'MyKey': {'test1': 4444,
                                      'test2': 2222}})


def test_extract_info_of_reason_why_invalid():
    def function_under_test(data_to_validate):
        try:
            schema.validate(data_to_validate)
        except SchemaError as e:
            raise InvalidConfig(e)

    def assert_domain_exception_is_raised_matching_msg(invalid_data, *regexes_to_match_in_exception_msg):
        domain_exception = InvalidConfig
        with pytest.raises(domain_exception) as raised:
            function_under_test(invalid_data)
        for regex in regexes_to_match_in_exception_msg:
            raised.match(regex)

    schema = Schema({'KataGRepo': {'User': str,
                                   'Repo': str},
                     'OtherKey': bool})

    missing_katagrepo_entry = {'OtherKey': False}
    invalid_type_for_user = {'KataGRepo': {'User': 37,
                                           'Repo': 'test'},
                             'OtherKey': True}
    missing_both_user_and_repo = {'KataGRepo': {},
                                  'OtherKey': True}

    assert_domain_exception_is_raised_matching_msg(missing_katagrepo_entry, r'KataGRepo', r'Missing')
    assert_domain_exception_is_raised_matching_msg(invalid_type_for_user, r'User')
    assert_domain_exception_is_raised_matching_msg(missing_both_user_and_repo, r'User', r'Repo')
