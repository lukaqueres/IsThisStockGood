"""
Get values from Yahoo Quote Summary, like profile and other data

@see Profile: For profile data

@see Data: for data gathered

@see YahooQuoteSummary for source class
"""

from __future__ import annotations

import asyncio
from typing import Any, List, Optional
import logging
import traceback
from enum import Enum

import flaskr.source.elements as src

import flaskr.source.RuleOneCalcs as RuleOne

logger = logging.getLogger("IsThisStockGood")


class Profile:
	"""
	Profile details about symbol owner
	
	@param address1: The street where the headquarters is located
	@type address1: Optional[str]
	
	@param city: The city in which the headquarters is located
	@type city: Optional[str]
	
	@param state: The state in which the headquarters is located
	@type state: Optional[str]
	
	@param country: The country in which the headquarters is located
	@type country: Optional[str]
	
	@param website: Website of company
	@type website: Optional[str]
	
	@param industryDisp: Company industry in nice string
	@type industryDisp: Optional[str]
	
	@param sector: Company sector
	@type sector: Optional[str]
	
	@param longBusinessSummary: Mostly I{really} long business summary
 	@type longBusinessSummary: Optional[str]
	
	@param fullTimeEmployees: Number of full time employees working at company
	@type fullTimeEmployees: Optional[int]
	
	@param companyOfficers: List of details about company officers
	@type companyOfficers: Optional[list]
	"""
	
	def __init__(self):
		"""
		Prepare fields for profile details
		"""
		self.address1: Optional[str] = None
		self.city: Optional[str] = None
		self.state: Optional[str] = None
		self.country: Optional[str] = None
		self.website: Optional[str] = None
		self.industryDisp: Optional[str] = None
		self.sector: Optional[str] = None
		self.longBusinessSummary: Optional[str] = None
		self.fullTimeEmployees: Optional[int] = None
		self.companyOfficers: Optional[list] = None
	
	def fill(self, attributes: list[str], data: dict) -> None:
		"""
		Copy values from dictionary to class attributes
		
		@param attributes: Attributes to copy
		@type attributes: list[str]
		
		@param data: Dictionary with values
		@type data: dict
		
		@return: None
		"""
		for attr_name in attributes:
			attr = None
			if attr_name in data.keys():
				attr = data[attr_name]
			setattr(self, attr_name, attr)


class Data(src.Data):
	"""
	Data class for Yahoo Quote Summary result

	@param profile: Profile data about company
	@type profile: Profile
	
	@param roic_history: History of roic
	@type roic_history: Optional[list]
	
	@param roic_average_3: Roic average for 3 years
	@type roic_average_3: Optional[int]
	
	@param roic_average_1: Roic average for 1 year
	@type roic_average_1: Optional[int]
	
	@param currentPrice: Current price
	@type currentPrice: Optional[int]
	
	@param totalDebt: Total debt of company
	@type totalDebt: Optional[int]
	
	@param debtToEquity: Debt to equity ratio
	@type debtToEquity: Optional[int]
	
	@param trailingEps: Trailing Eps
	@type trailingEps: Optional[int]
	"""
	
	def __init__(self):
		self.profile: Profile = Profile()
		self.roic_history: Optional[list] = None
		self.roic_average_3: Optional[int] = None
		self.roic_average_1: Optional[int] = None
		
		self.currentPrice: Optional[int] = None
		self.totalDebt: Optional[int] = None
		self.debtToEquity: Optional[int] = None
		self.trailingEps: Optional[int] = None


# TODO: This may be deleted?
class YahooFinanceQuoteSummaryModule(Enum):
	"""
	Enum class with Module
	"""
	assetProfile = 1
	incomeStatementHistory = 2
	incomeStatementHistoryQuarterly = 3
	balanceSheetHistory = 4
	balanceSheetHistoryQuarterly = 5
	cashFlowStatementHistory = 6
	cashFlowStatementHistoryQuarterly = 7
	defaultKeyStatistics = 8
	financialData = 9
	calendarEvents = 10
	secFilings = 11
	recommendationTrend = 12
	upgradeDowngradeHistory = 13
	institutionOwnership = 14
	fundOwnership = 15
	majorDirectHolders = 16
	majorHoldersBreakdown = 17
	insiderTransactions = 18
	insiderHolders = 19
	netSharePurchaseActivity = 20
	earnings = 21
	earningsHistory = 22
	earningsTrend = 23
	industryTrend = 24
	indexTrend = 26
	sectorTrend = 27


class YahooQuoteSummary(src.Source):
	"""
	Source from Yahoo Quote Summary

	@param data: Data fetched from source
	@type data: Data


	@param __url: Url to endpoint
	@type __url: str
	
	@param __MODULES: Modules available during fetch
	@type __MODULES: List[str]
	
	@param modules: Modules available during fetch
	@type modules: str
	"""
	__url = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules={modules}"
	
	__MODULES = [
		"assetProfile",  # Company info/background
		"incomeStatementHistory",
		"incomeStatementHistoryQuarterly",
		"balanceSheetHistory",  # Current cash/equivalents
		"balanceSheetHistoryQuarterly",
		"cashFlowStatementHistory",
		"cashFlowStatementHistoryQuarterly",
		"defaultKeyStatistics",
		"financialData",
		"calendarEvents",  # Contains ex-dividend date
		"secFilings",  # SEC filing links
		"recommendationTrend",
		"upgradeDowngradeHistory",
		"institutionOwnership",
		"fundOwnership",
		"majorDirectHolders",
		"majorHoldersBreakdown",
		"insiderTransactions",
		"insiderHolders",
		"netSharePurchaseActivity",
		"earnings",
		"earningsHistory",
		"earningsTrend",
		"industryTrend",
		"indexTrend",
		"sectorTrend"
	]
	
	def __init__(self, ticker: str, modules: Optional[List[str]]):
		"""
		Prepare essentials
		
		@param ticker: Ticker symbol of company
		
		@param modules: List of modules to get
		"""
		super().__init__(ticker)
		self.modules = ",".join([module for module in modules if module in self.__MODULES])
		self.data: Data = Data()
	
	@property
	async def values(self) -> Any:
		"""
		Allows for easier access to response values
		
		@return: Better accessible dictionary
		"""
		if not self.response:
			return None
		result = await self.response.json()
		return result["quoteSummary"]["result"][0]
	
	async def fetch(self) -> YahooQuoteSummary:
		"""
		Asynchronous function for fetching data

		@return: Self for fluent style chaining
		"""
		self.response = await self._get(self.__url.format(ticker=self.symbol, modules=self.modules))
		
		if not self.response.ok:
			self.error = (self.response.status, self.response.reason)
			return self
		
		values = await self.values
		self.data.profile.fill(["address1", "city", "state", "country", "website", "industryDisp",
		                        "sector", "longBusinessSummary", "fullTimeEmployees", "companyOfficers"],
		                       values["assetProfile"])
	
		financial_data = values.get("financialData", {})
		self.data.currentPrice = financial_data.get("currentPrice", {}).get("raw", None)
		self.data.totalDebt = financial_data.get("totalDebt", {}).get("raw", None)
		self.data.debtToEquity = financial_data.get("debtToEquity", {}).get("raw", None)
		
		self.data.trailingEps = values.get("defaultKeyStatistics", {}).get("trailingEps", {}).get("raw", None)
		
		self.data.roic_history = await self.__roic_history()
		
		if not self.data.roic_history:
			self.error = (424, "Could not parse roic history")
			return self
		try:
			self.data.roic_average_1 = self.__roic_average(1)
			self.data.roic_average_3 = self.__roic_average(3)
		except Exception as e:
			logger.error(e)
			logging.error(traceback.format_exc())
			self.error = (424, "Could not parse roic average")
			return self
		
		return self
		
	async def __roic_history(self) -> list:
		"""
		Calculates roic history
		
		@return: roic history list
		"""
		net_income_history = await self.__income_statement_history('netIncome')
		cash_history = await self.__balance_sheet_history('cash')
		long_term_debt_history = await self.__balance_sheet_history('longTermDebt')
		stockholder_equity_history = await self.__balance_sheet_history('totalStockholderEquity')
		roic_history = []
		for i in range(0, len(net_income_history)):
			roic_history.append(
				RuleOne.calculate_roic(
					net_income_history[i], cash_history[i],
					long_term_debt_history[i], stockholder_equity_history[i]
				)
			)
		return roic_history
	
	def __roic_average(self, years: int) -> Optional[int]:
		"""
		Calculates roic average for given amount of years
		
		@param years: Year span of data
		@return: roic average for given years
		
		
		@raise AttributeError
		"""
		if not self.data.roic_history:
			return None
		history = self.data.roic_history
		for h in history:
			if h is None:
				return None
		if len(history[0:years]) < years:
			raise AttributeError("Too few years in ROIC history")
		return round(sum(history[0:years]) / years, 2)
	
	async def __income_statement_history(self, key: str) -> list:
		"""
		Returns company income statement history

		@param key: Value for history
		@return: Income statement history
		"""
		history = []
		values = await self.values
		for stmt in values.get('incomeStatementHistory', {}).get('incomeStatementHistory', []):
			history.append(stmt.get(key).get('raw'))
		return history
	
	async def __balance_sheet_history(self, key: str) -> list:
		"""
		Returns company balance sheet history
		
		@param key: Value for history
		@return: Balance sheet history
		"""
		history = []
		values = await self.values
		for stmt in values.get('balanceSheetHistory', {}).get('balanceSheetStatements', []):
			history.append(stmt.get(key, {}).get('raw'))
		return history
