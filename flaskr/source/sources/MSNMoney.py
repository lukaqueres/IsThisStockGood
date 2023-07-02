"""
Get data about company, along with couple values.

@see Data: for data gathered

@see MSNMoney for source class
"""

from __future__ import annotations

from typing import Optional, Tuple
import json
import asyncio
import logging
import traceback

import flaskr.source.elements as src

logger = logging.getLogger("IsThisStockGood")


class Data(src.Data):
	"""
	Data class for MSNMoney result

	@param displayName: Display name of asset
	@type displayName: Optional[str]
	
	@param shortName: Short name of asset
	@type shortName: Optional[str]
	
	@param industry: Industry of asset
	@type industry: Optional[str]
	
	@param market: Market of sector
	@type market: Optional[str]
	
	@param pe_high: Highest price-to-earnings ratio
	@type pe_high: Optional[int]
	
	@param pe_low: Lowest price-to-earnings ratio
	@type pe_low: Optional[int]
	"""
	
	def __init__(self):
		super().__init__()
		
		self.displayName: Optional[str] = None
		self.shortName: Optional[str] = None
		self.industry: Optional[str] = None
		self.market: Optional[str] = None
		self.pe_high: Optional[int] = None
		self.pe_low: Optional[int] = None


class MSNMoney(src.Source):
	"""
	Source from MSNMoney
	
	@param data: Data fetched from source
	@type data: Data
	
	@param __id: Id of asset
	@type __id: Optional[str]
	
	@param url_id: Url for id of asset
	@type url_id: str
	
	@param url_ratios: Url for data about asset
	@type url_ratios: str
	
	@param __KEY_RATIOS_YEAR_SPAN: Years of ratios span
	@type __KEY_RATIOS_YEAR_SPAN: int
	"""
	url_id = "https://services.bingapis.com/contentservices-finance.csautosuggest/api/v1/Query?query={ticker}&market=en-us"
	url_ratios = "https://services.bingapis.com/contentservices-finance.financedataservice/api/v1/KeyRatios?stockId={id}"
	
	__KEY_RATIOS_YEAR_SPAN = 5
	
	def __init__(self, symbol: str):
		"""
		Fetches data about company with given symbol.
		First, id is acquired, and then used to fetch data.
		
		@param symbol: Symbol of asset
		@type symbol: str
		"""
		super().__init__(symbol)
		self.data = Data()
		self.__id: Optional[str] = None
		
	@classmethod
	async def setup(cls, symbol):
		self = MSNMoney(symbol)
		self.__id = await self.__stock_id()
		return self
		
	async def set_id(self):
		self.__id: Optional[str] = await self.__stock_id()
		
	async def fetch(self) -> MSNMoney:
		"""
		Asynchronous function for fetching data
		
		@return: Self for fluent style chaining
		"""
		if self.__id:
			self.response = await self._get(MSNMoney.url_ratios.format(id=self.__id))
		else:
			if not self.error:
				self.error = (404, "Ticker not found")
			self.response = None
			return self
		if not self.response.ok:
			self.error = (self.response.status, self.response.reason)
			return self
		self.data.pe_low, self.data.pe_high = await self.__pe_ratios()
		
		try:
			data = await self.response.json()
			
			self.data.displayName = data.get("displayName", None)
			self.data.industry = data.get("industry", None)
			self.data.market = data.get("market", None)
			self.data.shortName = data.get("shortName", None)
			self.data.symbol = data.get("symbol", None)
		
		except Exception as e:
			logger.error(e)
			logging.error(traceback.format_exc())
			self.error = (424, "Data could not be processed")
		return self
		
	async def __stock_id(self) -> Optional[str]:
		"""
		Collects id from url and ticker

		@return: Id if found, otherwise None
		"""
		response = await self._get(MSNMoney.url_id.format(ticker=self.symbol))
		if not response.ok:
			self.error = (response.status, response.reason)
			return None
		content = await response.text()
		try:
			content = json.loads(content)
			for data in content.get('data', {}).get('stocks', []):
				data = json.loads(data)
				if data.get('RT00S', '').upper() == self.symbol.upper():
					return data.get('SecId', '')
		except Exception as e:
			logger.error(e)
			logger.debug(content)
			self.error = (424, "Data could not be processed")
			return None
		
	async def __pe_ratios(self) -> Tuple[Optional[int], Optional[int]]:
		"""
		Returns lowest, and highest price-to-earnings ratio, None if there was some problem ( or no data )

		@return: lowest pe-ratios, highest pe-ratios
		"""
		json_result = await self.response.json()
		recent_pe_ratios = [
			                   year.get('priceToEarningsRatio', None)
			                   for year in json_result.get('companyMetrics', [])
			                   if year.get('fiscalPeriodType', '') == 'Annual' and 'priceToEarningsRatio' in year
		][-self.__KEY_RATIOS_YEAR_SPAN:]
		if len(recent_pe_ratios) != self.__KEY_RATIOS_YEAR_SPAN:
			return None, None
		try:
			pe_high = max(recent_pe_ratios)
			pe_low = min(recent_pe_ratios)
		except ValueError:
			return None, None
		return pe_low, pe_high
		