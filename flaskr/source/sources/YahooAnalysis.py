"""
Scrap five yar growth year from Yahoo Analysis website.

@note: It slows sourcing general data

@see Data: for data gathered

@see YahooAnalysis for source class
"""

from __future__ import annotations

from typing import Any, Optional
import re
from lxml import html
import logging

import flaskr.source.elements as src

logger = logging.getLogger("IsThisStockGood")


class Data(src.Data):
	"""
	Data class for Yahoo Analysis result
	
	@param five_year_growth_rate: Growth rate of five years
	@type five_year_growth_rate: Optional[int]
	"""
	
	def __init__(self):
		self.five_year_growth_rate: Optional[int] = None


class YahooAnalysis(src.Source):
	"""
	Source from MSNMoney

	@param data: Data fetched from source
	@type data: Data


	@param __url: Url to endpoint
	@type __url: str
	"""
	__url = "https://finance.yahoo.com/quote/{ticker}/analysis?p={ticker}"
	
	def __init__(self, symbol):
		"""
		Fetches value with given symbol.

		@param symbol: Symbol of asset
		@type symbol: str
		"""
		super().__init__(symbol)
		self.data = Data()
	
	async def fetch(self) -> YahooAnalysis:
		"""
		Asynchronous function for fetching data

		@return: Self for fluent style chaining
		"""
		self.response = await self._get(YahooAnalysis.__url.format(ticker=self.symbol))
		if not self.response.ok:
			self.error = (self.response.status_code, self.response.reason)
			return self
		
		text = self.response.text
		self.data.five_year_growth_rate = self.__parse_five_year_growth_rate(text)
		if not self.data.five_year_growth_rate:
			self.error = (404, "Could not parse five year growth rate")
			return self
		
		return self
	
	@staticmethod
	def __is_percentage(text: str) -> bool:
		"""
		Checks if text is percentage using regexp
		
		@param text: Text to check
		@type text: str
		
		@return: If text is percentage
		"""
		if not isinstance(text, str):
			return False
		match = re.match('(\d+(\.\d+)?%)', text)
		return match is not None
	
	def __parse_next_percentage(self, iterator: Any) -> Optional[str]:
		"""
		Get next percentage from iterator
		
		@param iterator: Iterator with text to iterate
		@type iterator: Any
		
		@return: Next percentage or None if there is no more percentages
		"""
		try:
			node = None
			while node is None or not self.__is_percentage(node.text):
				node = next(iterator)
			return node.text
		except StopIteration:  # End of iteration
			return None
	
	def __parse_five_year_growth_rate(self, content: str) -> bool | int:
		"""
		Scraps page for single piece of data
		
		@param content: Page to scrap
		@type content: str
		
		@return: Five year growth rate or None if not found
		"""
		tree = html.fromstring(bytes(content, encoding='utf8'))
		tree_iterator = tree.iter()
		five_year_growth_rate = None
		for element in tree_iterator:
			text = element.text
			if text == 'Next 5 Years (per annum)':
				percentage = self.__parse_next_percentage(tree_iterator)
				five_year_growth_rate = percentage.rstrip("%") if percentage else None
		return five_year_growth_rate if five_year_growth_rate else False
