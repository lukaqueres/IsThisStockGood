from __future__ import annotations

import asyncio
import random
import logging
import typing

from requests_futures.sessions import FuturesSession
from requests.models import Response

logger = logging.getLogger("IsThisStockGood")


class Data:
	def __init__(self, ticker: str):
		if not ticker:
			return
		self.__ticker = ticker
		
		
class MSNMoney(Data):
	def __init__(self, ticker):
		super().__init__(ticker)
		self.stock_id: int = 0
		self.pe_ratios: dict = {}

		
class YahooFinance(Data):
	URL: dict = {
		"quote_summary": "https://query1.finance.yahoo.com/v6/finance/quote?symbols={ticker}",
		"finance_quote": "https://query1.finance.yahoo.com/v6/finance/quote?symbols={ticker}",
		"finance_analysis": "https://finance.yahoo.com/quote/{ticker}/analysis?p={ticker}",
	}
	
	def __init__(self, ticker):
		super().__init__(ticker)
		self.quote_summary: dict = {}
		self.finance_quote: dict = {}
		self.finance_analysis: dict = {}
		
	async def get(self):
		self.quote_summary = await Fetch().url(YahooFinance.URL.get("quote_summary"), **{"ticker": self.__ticker})


class Company(Data):
	def __init__(self, ticker):
		super().__init__(ticker)
		self.market: str = ""
		self.industry: str = ""
		self.displayName: str = ""
		self.shortName: str = ""
		self.symbol: str = ""
		self.__MSN_data: MSNMoney = MSNMoney(ticker)
		self.__Yahoo_data: YahooFinance = YahooFinance(ticker)
		
	async def fetch(self):
		self.__Yahoo_data = Fetch().url().request()


class Fetch:
	
	USER_AGENT_LIST = [
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
	]
	
	def __init__(self):
		self.__url: str = ""
		self.__hooks: dict = {}
		self.__response: typing.Optional[Response] = None
		self.__handler: typing.Optional[typing.Callable] = None
		self.__future: typing.Optional[Response] = None
		self.__result: dict = {}
	
	@staticmethod
	def __get_session() -> FuturesSession:
		session = FuturesSession()
		session.headers.update({
			'User-Agent': random.choice(Fetch.USER_AGENT_LIST)
		})
		return session
	
	def receiver(self, response, *args, **kwargs) -> typing.Optional[dict]:
		if response.status_code != 200:
			logger.warning(
				f"Request to {response.url} returned with code {response.status_code} because of {response.reason}")
			return None
		logger.debug(f"Request to {response.url}  returned with code {response.status_code}")
		self.__response = response
		result = response.text
		logger.debug(f"Request to {response.url} returned : {result}")
		self.__result = result
	
	def url(self, url: str, **kwargs) -> Fetch:
		if kwargs:
			url = url.format(kwargs)
		self.__url = url
		return self
	
	def hooks(self, **kwargs) -> Fetch:
		self.__hooks.update(kwargs)
		return self
	
	def handler(self, handler: typing.Callable) -> Fetch:
		self.__handler = handler
		return self
	
	async def request(self) -> dict:
		session: FuturesSession = self.__get_session()
		self.__future = session.get(self.__url, allow_redirects=True, hooks={
			'response': self.receiver,
		}.update(self.__hooks))
		if self.__response:
			return self.__handler(self.__result)
		return self.__result
