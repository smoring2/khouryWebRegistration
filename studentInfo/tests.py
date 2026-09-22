from django.test import SimpleTestCase

from .student_views import timeConversion
from .validation import (coerce_float, coerce_int, collect_ints, get_int,
                         get_text, invalid_parameters_message)


class CoerceIntTests(SimpleTestCase):
    def test_missing_and_malformed_values_return_default(self):
        for value in (None, '', '   ', 'abc', '1.5', [], {}):
            self.assertIsNone(coerce_int(value))
        self.assertEqual(coerce_int('abc', 0), 0)

    def test_valid_values(self):
        self.assertEqual(coerce_int('42'), 42)
        self.assertEqual(coerce_int(' 42 '), 42)
        self.assertEqual(coerce_int(42), 42)


class CoerceFloatTests(SimpleTestCase):
    def test_missing_and_malformed_values_return_default(self):
        for value in (None, '', 'abc'):
            self.assertIsNone(coerce_float(value))

    def test_valid_values(self):
        self.assertEqual(coerce_float('3.5'), 3.5)
        self.assertEqual(coerce_float('4'), 4.0)


class ParamHelperTests(SimpleTestCase):
    def test_collect_ints_reports_invalid_names(self):
        values, invalid = collect_ints({'nuid': '1', 'hours': 'x'}, 'nuid', 'hours', 'advisor_id')
        self.assertEqual(values, {'nuid': 1})
        self.assertEqual(invalid, ['hours', 'advisor_id'])

    def test_get_int_and_get_text(self):
        self.assertEqual(get_int({'a': '7'}, 'a'), 7)
        self.assertIsNone(get_int({}, 'a'))
        self.assertEqual(get_text({'a': '  b '}, 'a'), 'b')
        self.assertEqual(get_text({}, 'a'), '')

    def test_invalid_parameters_message_names_fields_only(self):
        self.assertEqual(invalid_parameters_message(['nuid', 'hours']),
                         'Invalid or missing parameter(s): nuid, hours')


class TimeConversionTests(SimpleTestCase):
    def test_unmapped_or_malformed_input_returns_none(self):
        for date, time in (('None', '10:00:00'), (None, '10:00:00'), ('X', '10:00:00'),
                           ('M', None), ('M', ''), ('M', 'ab:cd')):
            self.assertIsNone(timeConversion(date, time))

    def test_known_days(self):
        self.assertEqual(timeConversion('M', '10:30:00'), 10 * 60 + 30)
        self.assertEqual(timeConversion('W', '09:05:00'), 2 * 24 * 60 + 9 * 60 + 5)
