"""
Get quite large amount of values from StockRow

@see Profile: For profile data

@see Data: for data gathered

@see StockRow for source class
"""

from __future__ import annotations

from typing import Optional
import traceback
import logging

import flaskr.source.elements as src
import flaskr.source.RuleOneCalcs as RuleOne

logger = logging.getLogger("IsThisStockGood")


class Data(src.Data):
	"""
	Data class for StockRow result
	
	@param roic: Roic
	@type roic: Optional[int]
	
	@param roic_averages: List of roic averages
	@type roic_averages: Optional[list]
	
	@param revenue_growth_rates: List of revenue growth rates
	@type revenue_growth_rates: Optional[list]
	
	@param eps_growth_rates: List of Earnings/Sh rates
	@type eps_growth_rates: Optional[list]
	
	@param debt_equity_ratio: Debt to equity ratio
	@type debt_equity_ratio: Optional[int]
	
	@param total_debt: Total debt of company
	@type total_debt: Optional[int]
	
	@param debt_payoff_time: Time to payoff debt from total_debt
	@type debt_payoff_time: Optional[int]
	
	@param equity: Equity ( Book Value/Sh )
	@type equity: Optional[int]
	
	@param equity_growth_rates: List of equity ( Book Value/Sh ) rates
	@type equity_growth_rates: Optional[list]
	
	@param free_cash_flow: Free cash flow
	@type free_cash_flow: Optional[int]
	
	@param free_cash_flow_growth_rates: List of last cash flow growth rates
	@type free_cash_flow_growth_rates: Optional[list]
	
	@param recent_free_cash_flow: Free cash flow for last year
	@type recent_free_cash_flow: Optional[int]
	
	@param last_year_net_income: Last year's net income
	@type last_year_net_income: Optional[int]

	"""
	
	def __init__(self):
		super().__init__()
		
		self.roic: Optional[int] = None
		self.roic_averages: Optional[list] = None
		self.revenue_growth_rates: Optional[list] = None
		self.eps_growth_rates: Optional[list] = None
		
		self.debt_equity_ratio: Optional[int] = None
		self.total_debt: Optional[int] = None
		self.debt_payoff_time: Optional[int] = None
		
		self.equity: Optional[list] = None
		self.equity_growth_rates: Optional[list] = None
		self.free_cash_flow: Optional[int] = None
		self.free_cash_flow_growth_rates: Optional[list] = None
		self.recent_free_cash_flow: Optional[int] = None
		self.last_year_net_income: Optional[int] = None


class StockRow(src.Source):
	"""
	Source from MSNMoney

	@param data: Data fetched from source
	@type data: Data
	
	
	@param __url: Url to endpoint
	@type __url: str
	"""
	
	__url = "https://stockrow.com/api/companies/{ticker}/new_key_stats.json"
	
	def __init__(self, symbol: str):
		"""
		Fetches data about company with given symbol.

		@param symbol: Symbol of asset
		@type symbol: str
		"""
		super().__init__(self.__temporary_ticker_mapping(symbol))
		self.data = Data()
		
	async def fetch(self) -> StockRow:
		"""
		Asynchronous function for fetching data

		@return: Self for fluent style chaining
		"""
		
		self.response = await self._get(self.__url.format(ticker=self.symbol))
		if not self.response.ok:
			self.error = (self.response.status_code, self.response.reason)
			return self
		if not self.__parse():
			self.error = (424, "Data could not be processed")
			return self
		return self
	
	@staticmethod
	def __temporary_ticker_mapping(symbol: str) -> str:
		"""
		Temporary ticker mapping

		@param symbol: Ticker
		@type symbol: str
		
		@return: Symbol, may be result of mapping
		"""
		mapping = {
			'META': 'FB'
		}
		return mapping.get(symbol.upper(), symbol)
	
	def __parse(self) -> bool:
		"""
		Parses data from result.
		
		@return: if parsing was successful
		"""
		try:
			data_dict = {}
			data = self.response.json()
			
			rows = data.get("fundamentals", {}).get("rows", [])
			_add_list_of_dicts_to_dict(rows, data_dict, "label")
			
			capital_structures = data.get("capital_structure", {})
			singles = capital_structures.get("singles", [])
			_add_list_of_dicts_to_dict(singles, data_dict, "label")
			
			sparklines = capital_structures.get("sparklines", [])
			_add_list_of_dicts_to_dict(sparklines, data_dict, "label")
			
			self.data.roic = _get_nested_values_for_key(data_dict, "ROIC")
			# Convert from decimal to percent
			self.data.roic = [self.data.roic[i] * 100 for i in range(0, len(self.data.roic))]
			self.data.roic_averages = _compute_averages_for_data(self.data.roic)
			if not self.data.roic_averages:
				logging.error('Failed to parse ROIC')
			
			revenue = _get_nested_values_for_key(data_dict, "Revenue")
			self.data.revenue_growth_rates = compute_growth_rates_for_data(revenue)
			if not self.data.revenue_growth_rates:
				logging.error('Failed to parse Revenue growth rates')
			
			eps = _get_nested_values_for_key(data_dict, "Earnings/Sh")
			self.data.eps_growth_rates = compute_growth_rates_for_data(eps)
			if not self.data.eps_growth_rates:
				logging.error('Failed to parse EPS growth rates')
			
			debt_equity = _get_nested_value_for_key(data_dict, "Debt to Equity (Q)")
			if not debt_equity:
				logging.error('Failed to parse Debt-to-Equity ratio.')
			else:
				self.data.debt_equity_ratio = debt_equity
			
			self.data.equity = _get_nested_values_for_key(data_dict, "Book Value/Sh")
			self.data.equity_growth_rates = compute_growth_rates_for_data(self.data.equity)
			if not self.data.equity:
				logging.error('Failed to parse Book Value/Sh.')
			
			self.data.free_cash_flow = _get_nested_values_for_key(data_dict, "FCF")
			self.data.free_cash_flow_growth_rates = compute_growth_rates_for_data(self.data.free_cash_flow)
			if not self.data.free_cash_flow:
				logging.error('Failed to parse Free Cash Flow.')
			else:
				self.data.recent_free_cash_flow = self.data.free_cash_flow[-1]  # Data already in USD millions
			
			net_income = _get_nested_values_for_key(data_dict, "Net Income")
			if net_income and len(net_income):
				self.data.last_year_net_income = net_income[-1]
			
			total_debts = _get_nested_values_for_key(data_dict, "Total Debt")  # Already in USD millions
			self.__calculate_total_debt(total_debts)
		
		except Exception as e:
			logger.warning(e)
			logging.error(traceback.format_exc())
			return False
		return True
	
	def __calculate_total_debt(self, total_debts):
		"""
		Calculate total debt
		
		@param total_debts:
		"""
		if not len(total_debts) > 0 or not self.data.recent_free_cash_flow:
			self.data.total_debt = 0
			logging.error('Failed to parse Long Term Debt')
			self.data.debt_payoff_time = 0
		else:
			self.data.total_debt = total_debts[-1]  # Data already in USD millions
			self.data.debt_payoff_time = self.data.total_debt / self.data.recent_free_cash_flow


def _add_list_of_dicts_to_dict(list_of_dicts: list, target_dict: dict, key_name):
	"""
	Adds key from dictionaries in list to target dictionary
	
	@param list_of_dicts: List of source dictionaries
	@param target_dict: Target dictionary
	@param key_name: Key
	"""
	for i in range(0, len(list_of_dicts)):
		value = list_of_dicts[i]
		key = value.get(key_name, "")
		if not key:
			continue
		target_dict[key] = value


def _get_nested_values_for_key(dictionary: dict, key: str) -> list:
	"""
	Returns nested values
	
	@param dictionary: Dictionary
	@param key: Key for values
	
	@return: List of nested values
	"""
	elements = dictionary.get(key, {}).get("values", [])
	return [x for x in elements if isinstance(x, (int, float, complex))]


def _get_nested_value_for_key(dictionary: dict, key: str) -> int | float | complex:
	"""
	Return nested value from key
	
	@param dictionary: Nested dict
	@param key:
	@return: Value
	"""
	value = dictionary.get(key, {}).get("value", None)
	return value if isinstance(value, (int, float, complex)) else None


def compute_growth_rates_for_data(data: list) -> Optional[list]:
	"""
	Calculates growth rates for given data
	
	@param data: List of values
	@return: Growth rates
	"""
	if data is None or len(data) < 2:
		return None
	results = []
	year_over_year = RuleOne.compound_annual_growth_rate(data[-2], data[-1], 1)
	results.append(year_over_year)
	if len(data) > 3:
		average_3 = RuleOne.compound_annual_growth_rate(data[-4], data[-1], 3)
		results.append(average_3)
	if len(data) > 5:
		average_5 = RuleOne.compound_annual_growth_rate(data[-6], data[-1], 5)
		results.append(average_5)
	if len(data) > 6:
		last_index = len(data) - 1
		max_val = RuleOne.compound_annual_growth_rate(data[0], data[-1], last_index)
		results.append(max_val)
	return [x for x in results if x is not None]


def _average(array: list) -> int:
	"""
	Average value in list
	
	@param array: Values
	
	@return: Average value
	"""
	return round(sum(array) / len(array), 2)


def _compute_averages_for_data(data: list) -> Optional[list]:
	"""
	Calculates yearly averages from a set of yearly data. Assumes no TTM entry at the end.
	
	@param data: Data for averages
	@type data: list
	
	@return Average values for given data
	"""
	
	if data is None or len(data) < 2:
		return None
	results = [round(data[-1], 2)]
	if len(data) >= 3:
		three_year = _average(data[-3:])
		results.append(three_year)
	if len(data) >= 5:
		five_year = _average(data[-5:])
		results.append(five_year)
	if len(data) >= 6:
		max_val = _average(data)
		results.append(max_val)
	return [x for x in results if x is not None]
