"""
Classes for sourcing, and parsing results.

"""

from typing import Any, Optional, Tuple, Type

import requests
import random
import logging
import json

logger = logging.getLogger("IsThisStockGood")


class Data:
	"""
	Class with data from source
	
	It is here to ease potential future changes
	"""
	pass


class Source:
	"""
	Source parent class. Has essential attributes.
	It is inherited in the source classes
	
	
	@param symbol: Ticker symbol of company
	@type symbol: str
	@param error: Tuple with error code and reason. None if there was no error
	@type error: Optional[Tuple[int, str]]
	@param data: Class with data fetched from the source. May contain values calculated from acquired data
	@type data: Type[Data] | Data
	@param response: Response from request call
	@type response: Optional[requests.Response]
	
	@param _USER_AGENTS: List of 5 user agents for requests calls
	@type _USER_AGENTS: Tuple[str, str, str, str, str]
	"""
	
	_USER_AGENTS = (
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 "
		"Safari/605.1.15",
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 "
		"Safari/537.36",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
	)
	
	def __init__(self, symbol: str):
		"""
			@param symbol: Ticker symbol of company
			@type symbol: str
		"""
		self.symbol: str = symbol
		self.error: Optional[Tuple[int, str]] = None
		self.data: Type[Data] | Data = Data()
		self.response: Optional[requests.Response] = None

	async def _get(self, url: str, *args, **kwargs) -> requests.Response:
		"""
		Asynchronous method for get calls with user agent in session

		@param url: url for C{get} call
		@type url: str
		@param args: arguments that are passed to C{session.get()} call
		@type args: tuple
		@param kwargs: kwargs for C{session.get()} call
		@type kwargs: dict
		
		@return: response from url
		"""
		
		session = requests.Session()
		session.headers.update({
			'User-Agent': random.choice(self._USER_AGENTS)
		})
		response = session.get(*args, url=url, **kwargs)
		if not response.ok:
			logger.warning(f"{response.url} returned code {response.status_code} : {response.reason}")
			return response
		logger.debug(f"{response.url} returned: {response.content}")
		return response


class Color:
	"""
	Color values for data
	
	@param green: Green color hex
	@type green: str
	@param orange: Orange color hex
	@type orange: str
	@param red: Red color hex
	@type red: str
	@param white: White color hex
	@type white: str
	@param yellow: Yellow color hex
	@type yellow: str
	@param grey: Grey color
	@type grey: str
	"""
	
	green: str = "#89e051"
	orange: str = "#f7523f"
	red: str = "#701516"
	white: str = "#ffffff"
	yellow: str = "#f1e05a"
	grey: str = "grey"
	
	@staticmethod
	def zero_based_range(value: int, range_list: list[int] | tuple[int]) -> str:
		"""
		Assign color to value based on zero based range
		
		@param value: Value of element
		@param range_list: range
		@return: Color string
		
		@raise AttributeError: Invalid range list
		"""
		if len(range_list) != 3:
			raise AttributeError("Invalid Range. Pass 3 values")
		if value is None:
			return Color.grey
		color = Color.green
		if value >= range_list[2]:
			color = Color.red
		elif value >= range_list[1]:
			color = Color.orange
		elif value >= range_list[0]:
			color = Color.yellow
		
		return color
	
	@staticmethod
	def range(value: int, range_list: list[int] | tuple[int]) -> str:
		"""
		Assign color to value based on range

		@param value: Value of element
		@param range_list: range
		@return: Color string

		@raise AttributeError: Invalid range list
		"""
		if len(range_list) != 3:
			raise AttributeError("Invalid Range. Pass 3 values")
		if value is None:
			return Color.grey
		color = Color.red
		if value >= range_list[2]:
			color = Color.green
		elif value >= range_list[1]:
			color = Color.yellow
		elif value >= range_list[0]:
			color = Color.orange
		
		return color


class Property:
	"""
	Property has value and color
	
	@param color: Color hex or name
	@type color: str
	@param value: Value of property
	@type value: Any
	"""
	def __init__(self, value: Any):
		"""
		
		@param value: Value for property
		"""
		self.color: str = Color.grey
		self.value: Any = value or None
	
	def range_color(self, range_list: list):
		"""
		Get color by range
		
		@param range_list: Range list for range of color
		@return: Hex or name
		"""
		self.color = Color.range(self.value, range_list)
	
	def zero_based_range_color(self, range_list: list):
		"""
		Get color by zero based range

		@param range_list: Range list for range of color
		@return: Hex or name
		"""
		self.color = Color.zero_based_range(self.value, range_list)
	
	def to_json(self) -> str:
		"""
		Converts class to json string
		
		@return: json string of property's value and color
		"""
		return json.dumps(self, default=lambda o: o.__dict__)
	
	
class Result:
	"""
	# TODO: Finish docstring
	"""
	def __init__(self):
		self.ticker: Optional[str] = None
		self.name: Optional[str] = None
		self.shortName: Optional[str] = None
		self.address: Optional[str] = None
		self.industry: Optional[str] = None
		self.profile: Optional[object] = None
		
		self.roic: list[Property] = [Property(None) for p in range(4)]
		self.equity: list[Property] = [Property(None) for p in range(4)]
		self.eps: list[Property] = [Property(None) for p in range(4)]
		self.sales: list[Property] = [Property(None) for p in range(4)]
		self.cash: list[Property] = [Property(None) for p in range(4)]
		
		self.total_debt: Property = Property(None)
		self.free_cash_flow: Property = Property(None)
		self.debt_payoff_time: Property = Property(None)
		self.debt_equity_ratio: Property = Property(None)
		self.margin_of_safety_price: Property = Property(None)
		self.current_price: Property = Property(None)
		self.sticker_price: Property = Property(None)
		self.payback_time: Property = Property(None)
		self.average_volume: Property = Property(None)
		self.shares_to_hold: Property = Property(None)
		
		self.error: Optional[tuple[int, str]] = None
	
	def colour(self) -> None:
		"""
		Apply colors to properties based on values
		"""
		lists_range = [0, 5, 10]
		
		lists = ["roic", "eps", "sales", "equity", "cash"]
		
		for attr in lists:
			if getattr(self, attr) is not None:
				for elem in getattr(self, attr):
					elem.range_color(lists_range)
		
		margin_o_safety = self.margin_of_safety_price.value
		
		zero_based_range = {"debt_equity_ratio": [1, 2, 3], "debt_payoff_time": [2, 3, 4], "payback_time": [6, 8, 10],
		                    "current_price": [margin_o_safety or 0, margin_o_safety or 0 * 1.25,
		                                      margin_o_safety or 0 * 1.5]}
		
		for zero_based, zero_range in zero_based_range.items():
			if getattr(self, zero_based) is not None:
				getattr(self, zero_based).zero_based_range_color(zero_range)
		
		if self.free_cash_flow.value is not None and self.free_cash_flow.value < 0:
			self.debt_payoff_time.color = Color.red
		
		if not self.margin_of_safety_price.value:
			self.current_price.color = Color.grey
		
		if not self.payback_time.value:
			self.payback_time.color = Color.grey
			
		if not self.average_volume.value:
			self.average_volume.color = Color.grey
		
		if self.average_volume.value is not None and self.current_price.value is not None:
			average_volume = self.average_volume.value or 0
			min_volume = 1000000 if self.current_price.value <= 1.0 else 500000
			self.average_volume.color = Color.green if average_volume >= min_volume else Color.red
		
		nones = ["margin_of_safety_price", "sticker_price", "total_debt", "free_cash_flow"]
		
		for item in nones:
			getattr(self, item).color = None
	
	def to_json(self) -> str:
		"""
		Json representation of result
		
		@return: JSON string
		"""
		return json.dumps(self, default=lambda o: o.__dict__)
