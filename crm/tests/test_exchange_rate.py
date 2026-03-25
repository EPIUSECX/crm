from unittest.mock import patch

import requests
from frappe.tests import UnitTestCase

from crm.api.exchange_rate import _fetch_from_frankfurter, get_exchange_rate


class TestExchangeRate(UnitTestCase):
	@patch("crm.api.exchange_rate.frappe.cache")
	@patch("crm.api.exchange_rate.frappe.log_error")
	@patch("crm.api.exchange_rate._fetch_exchange_rate")
	def test_get_exchange_rate_returns_none_when_throw_false_and_provider_fails(
		self, mock_fetch_exchange_rate, mock_log_error, mock_cache
	):
		mock_cache.return_value.get_value.return_value = None
		mock_fetch_exchange_rate.return_value = (None, "frankfurter")

		rate = get_exchange_rate("ZAR", "USD", throw=False)

		self.assertIsNone(rate)
		mock_log_error.assert_called_once()

	@patch("crm.api.exchange_rate.requests.get")
	def test_frankfurter_timeout_returns_none(self, mock_get):
		mock_get.side_effect = requests.exceptions.ReadTimeout()

		rate = _fetch_from_frankfurter("ZAR", "USD", "latest")

		self.assertIsNone(rate)
