"""
Get data from every source with one call

@see ticker: This function returns data
"""
import logging
import asyncio
import json
import re
from typing import Optional

from flaskr.source.sources import *
import flaskr.source.elements as elements
import flaskr.source.RuleOneCalcs as RuleOne

logger = logging.getLogger("IsThisStockGood")


def ticker(symbol: str) -> (dict, int):
	"""
	Fetch data for company with provided ticker / symbol
	
	After data is fetched for all sources, is checked for errors and parsed to class & returned
	
	@param symbol: Ticker / Symbol of company
	
	@return: dictionary with data, and code for http response
	"""
	msn_money = asyncio.run(MSNMoney(symbol).fetch())
	stock_row = asyncio.run(StockRow(symbol).fetch())
	yahoo_analysis = asyncio.run(YahooAnalysis(symbol).fetch())
	yahoo_quote_summary = asyncio.run(YahooQuoteSummary(symbol,
	                                                    ["assetProfile", "incomeStatementHistory",
	                                                     "balanceSheetHistory", "financialData",
	                                                     "balanceSheetHistory", "earnings",
	                                                     "defaultKeyStatistics"]
	                                                    ).fetch())
	
	result = elements.Result()
	result.ticker = symbol
	
	code = 200
	error: Optional[str] = None
	
	if msn_money.error:
		logger.warning(f"Msn Money Error: {msn_money.error}")
	if stock_row.error:
		logger.warning(f"StockRow Error: {stock_row.error}")
	if yahoo_analysis.error:
		logger.warning(f"Yahoo Analysis Error: {yahoo_analysis.error}")
	if yahoo_quote_summary.error:
		logger.warning(f"Yahoo Quote Summary Error: {yahoo_quote_summary.error}")
	
	if msn_money.error and stock_row.error and yahoo_analysis.error and yahoo_quote_summary.error:
		if msn_money.error[0] == stock_row.error[0] == yahoo_quote_summary.error[0] == yahoo_analysis.error[0] == 404:
			code = 404
			error = "Ticker not found"
			
		result.error = error
		return json.loads(result.to_json()), code
	
	margin_of_safety_price, sticker_price = _calculate_margin_of_safety_price(
		stock_row.data.equity_growth_rates,
		msn_money.data.pe_low,
		msn_money.data.pe_high,
		yahoo_quote_summary.data.trailingEps,
		yahoo_analysis.data.five_year_growth_rate)
	
	roic_list = _get_roic_averages(
		yahoo_quote_summary.data.roic_average_1,
		yahoo_quote_summary.data.roic_average_3,
		stock_row.data.roic_averages)
	
	profile = yahoo_quote_summary.data.profile
	result.address = f"{profile.country} {profile.city} - {profile.address1}"
	result.profile = profile
	result.industry = msn_money.data.industry if msn_money.data.industry else yahoo_quote_summary.data.profile.industryDisp
	result.shortName = msn_money.data.shortName
	result.name = msn_money.data.displayName
	result.total_debt.value = stock_row.data.total_debt
	result.current_price.value = yahoo_quote_summary.data.currentPrice
	
	if roic_list is not None:
		result.roic = [elements.Property(elem) for elem in roic_list]
	if stock_row.data.eps_growth_rates is not None:
		result.eps = [elements.Property(elem) for elem in stock_row.data.eps_growth_rates]
	if stock_row.data.revenue_growth_rates is not None:
		result.sales = [elements.Property(elem) for elem in stock_row.data.revenue_growth_rates]
	if stock_row.data.equity_growth_rates is not None:
		result.equity = [elements.Property(elem) for elem in stock_row.data.equity_growth_rates]
		
	if stock_row.data.free_cash_flow_growth_rates is not None:
		result.cash = [elements.Property(elem) for elem in stock_row.data.free_cash_flow_growth_rates]
	
	"""
	result.roic.reverse()
	result.eps.reverse()
	result.sales.reverse()
	result.equity.reverse()
	result.cash.reverse()"""
	
	result.free_cash_flow.value = stock_row.data.recent_free_cash_flow
	result.debt_payoff_time.value = stock_row.data.debt_payoff_time
	result.debt_equity_ratio.value = stock_row.data.debt_equity_ratio
	
	result.sticker_price.value = sticker_price
	result.margin_of_safety_price.value = margin_of_safety_price
	
	result.error = error
	
	result.colour()
	
	return json.loads(result.to_json()), code


def check(symbol: str) -> bool:
	"""
	Check if symbol is correct
	
	@param symbol: Symbol
	@return: If symbol is correct
	"""
	pattern = re.compile(r"[A-Za-z,.\-]+")
	
	if len(symbol) > 6 or not pattern.match(symbol):
		return False
	return True


def _calculate_margin_of_safety_price(equity_growth_rates: list, pe_low: int, pe_high: int, ttm_eps: int,
                                      five_year_growth_rate: int) -> (Optional[int], Optional[int]):
	"""
	
	@param equity_growth_rates: Equity growth rates
	@param pe_low: Lowest Pe Ratio
	@param pe_high: Highest Pe Ratio
	@param ttm_eps: Trailing Twelve Months of Eps
	@param five_year_growth_rate: Five year growth rate
	
	@return: Margin of Safety price, Sticker price
	"""
	
	if not equity_growth_rates or not pe_low or not pe_high or not five_year_growth_rate:
		return None, None
	
	if not five_year_growth_rate or not equity_growth_rates:
		return None, None
	growth_rate = min(float(five_year_growth_rate),
	                  float(equity_growth_rates[-1]))
	# Divide the growth rate by 100 to convert from percent to decimal.
	growth_rate = growth_rate / 100.0
	
	if not ttm_eps or not pe_low or not pe_high:
		return None, None
	margin_of_safety_price, sticker_price = \
		RuleOne.margin_of_safety_price(float(ttm_eps), growth_rate,
		                               float(pe_low), float(pe_high))
	return margin_of_safety_price, sticker_price


def _get_roic_averages(one_year_avg: int, three_year_avg: int, roic_avg: list) -> Optional[list]:
	"""
	Calculate ROIC averages for 1,3,5 and Max years
	StockRow averages aren't accurate, so we're getting avg for 1y and 3y from Yahoo
	by calculating these by ourselves. The rest is from StockRow to at least have some (even
	a bit of inaccurate values), cause Yahoo has data for 4 years only.
	
	@param one_year_avg: Roic average for 1 year
	@param three_year_avg: Roic average from 3 years
	@param roic_avg: List of roic averages
	
	@return List of roic averages
	"""
	if roic_avg is None:
		return None
	f_roic_avg = []
	try:
		if one_year_avg is not None:
			f_roic_avg.append(one_year_avg)
		else:
			raise AttributeError
	except AttributeError:
		try:
			f_roic_avg.append(roic_avg[0])
		except IndexError:
			return []
		
	try:
		if three_year_avg is not None:
			f_roic_avg.append(three_year_avg)
		else:
			raise AttributeError
	except AttributeError:
		try:
			f_roic_avg.append(roic_avg[1])
		except IndexError:
			return f_roic_avg
	try:
		f_roic_avg.append(roic_avg[2])
		f_roic_avg.append(roic_avg[3])
	except IndexError:
		pass
	return f_roic_avg
