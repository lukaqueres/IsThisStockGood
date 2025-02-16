"""
A collection of functions to compute investing calculations from Rule #1.
"""

from __future__ import division
import math
from typing import Optional


def compound_annual_growth_rate(start_balance: int, end_balance: int, years: int) -> Optional[float]:
	"""
	Calculate the compound annual growth rate from raw data.

	Formula = (end/start)^(1/years) - 1
	
	@param start_balance: Start balance
	@param end_balance: Amount at end of timeframe
	@param years: Number of years in timespan
	
	@return: Compound annual growth rate from raw data.
	"""
	if start_balance is None or end_balance is None or years is None:
		return None
	if start_balance == 0 or years == 0:
		return None
	exponent = 1.0 / years
	# result = 0
	difference = end_balance / start_balance
	if difference > 0:  # The numbers are either both positive or both negative
		difference = end_balance / start_balance
		result = round((pow(difference, exponent) - 1.0) * 100, 2)
	else:  # One, and only one, of the numbers is negative
		# We can't really calculate a real growth rate for these cases, so let's double
		# an approximation to have something to show.
		if start_balance < end_balance:  # start_balance is negative
			difference = (end_balance - (2.0 * start_balance)) / (-1.0 * start_balance)
		else:  # end_balance is negative
			difference = ((-1 * end_balance) + start_balance) / start_balance
		result = round((pow(difference, exponent) - 1.0) * 100, 2)
	if end_balance < 0:
		result = -1 * result
	return result


def slope_of_best_fit_line_for_data(data: list):
	"""
	Returns the slope of the line of best fit for a set of data points.

	@param data: A list of data points to plot a best-fit line on.

	
	@return: Returns the slope of the best fit line.
	"""
	if not data or len(data) < 2:
		return None


#  m,b = np.polyfit(range(0, len(data)), data, 1)
#  return m


def max_position_size(share_price, trade_volume) -> (Optional[int], Optional[int]):
	"""
	Returns the limits for a position size for a given stock. These are the
	value to limit your position below to make sure you can buy in or sell out of
	a stock without causing an artificial price change.

	This boils down to 1% of the volume or 1% of the price of the volume.

	@param share_price: The share price of the stock.
	@param trade_volume: The average trade volume of the stock.
	
	@return Max position, Max shares
	"""
	if not share_price or not trade_volume:
		return None
	max_shares = math.floor(trade_volume * 0.01)  # 1%
	max_position = math.floor(share_price * max_shares)
	return max_position, max_shares


def payback_time(market_cap: int, net_income: int, estimated_growth_rate: int) -> int:
	"""
	Determine the amount of years to get your money back if you were to buy the
	entire company at the current market cap given the TTM net income and
	expected growth rate.

	For more details, read PaybackTime by Phil Town for information on this
	calculation. Basically it's the summation of each year future value (FV
	function on Excel).

	@param market_cap: The current market capitalization for the company.
	@param net_income: The trailing twelve month (TTM) net income for the company.
	@param estimated_growth_rate: A conservative estimated growth rate. (Typically the
		minimum of a professional growth estimate and the historical growth rate
		of equity/book-value-per-share.)

	
	@return: Returns the number of years (rounded up) for how many years are needed to
		receive a 100% return on your investment based on the company's income. If
		any of the inputs are invalid, returns -1.
		
	"""
	yearly_income = net_income
	total_payback = 0
	years = 0
	while total_payback < market_cap:
		if yearly_income <= 0 or estimated_growth_rate <= 0:
			years = -1
			break
	yearly_income += (yearly_income * estimated_growth_rate)
	total_payback += yearly_income
	years += 1
	
	return years


def margin_of_safety_price(current_eps: float, estimated_growth_rate: float,
                           historical_low_pe: float, historical_high_pe: float) -> (Optional[int], Optional[int]):
	"""
	Calculates the value a stock should be purchased at today to have a 50% margin
	of safety given a 10-year timeframe with a minimum projection of 15%-per-year
	earnings.

	@param current_eps: The current Earnings Per Share (EPS) value of the stock.
			Typically found from Yahoo Finance or Wall Street Journal page.
	@param estimated_growth_rate: A conservative estimated growth rate. (Typically the
		minimum of a professional growth estimate and the historical growth
		rate of equity/book-value-per-share.)
	@param historical_low_pe: The 5-year low for the price-to-earnings (PE) ratio.
		Usually found on MSN Money.
	@param historical_high_pe: The 5-year high for the price-to-earnings (PE) ratio.
		Usually found on MSN Money.

	@return:
		1. The maximum price to buy the stock for with a 50% margin of safety.
		2. The sticker price, which is the estimated fair-value price today. This
			value can be used to determine when is a good time to exit a position
			after a big run-up in price.
	
	"""
	if not current_eps or not estimated_growth_rate or not historical_low_pe or not historical_high_pe:
		return None, None
	future_eps = calculate_future_eps(current_eps, estimated_growth_rate)
	future_pe = calculate_future_pe(estimated_growth_rate, historical_low_pe,
	                                historical_high_pe)
	future_price = calculate_estimated_future_price(future_eps, future_pe)
	sticker_price = calculate_sticker_price(future_price)
	margin_of_safety = calculate_margin_of_safety(sticker_price)
	return margin_of_safety, sticker_price


def calculate_future_eps(current_eps: float, estimated_growth_rate: float, time_horizon: int = 10) -> Optional[float]:
	"""
	Calculates the estimated future earnings-per-share (EPS) value in 10 years.

	This implements the same underlying formula as the Excel "FV" (future value)
	function.

	@param current_eps: The current Earnings Per Share (EPS) value of the stock.
			Typically found from Yahoo Finance or Wall Street Journal page.
	@param estimated_growth_rate: A conservative estimated growth rate. (Typically the
			minimum of a professional growth estimate and the historical growth
			rate of equity/book-value-per-share.)
	@param time_horizon: The desired time horizon to calculate for. Defaults to 10.

	@return: The estimated future earnings-per-share value in 10 years time.
	"""
	# FV = C * (1 + r)^n
	# where C -> current_value, r -> rate, n -> years
	if not current_eps or not estimated_growth_rate:
		return None
	ten_year_growth_rate = math.pow(1.0 + estimated_growth_rate, time_horizon)
	future_eps_value = current_eps * ten_year_growth_rate
	return future_eps_value


def calculate_future_pe(estimated_growth_rate: float, historical_low_pe: float,
                        historical_high_pe: float) -> Optional[float]:
	"""
	Calculates the future price-to-earnings (PE) ratio value.

	@param estimated_growth_rate: A conservative estimated growth rate. (Typically the
			minimum of a professional growth estimate and the historical growth
			rate of equity/book-value-per-share.)
	@param historical_low_pe: The 5-year low for the price-to-earnings (PE) ratio.
			Usually found on MSN Money.
	@param historical_high_pe: The 5-year high for the price-to-earnings (PE) ratio.
			Usually found on MSN Money.

	@return: The estimated future price-to-earnings ratio.
	"""
	# To be conservative, we will take the smaller of these two: 1. the average
	# historical PE, 2. double the estimated growth rate.
	if not estimated_growth_rate or not historical_low_pe or not historical_high_pe:
		return None
	future_pe_one = (historical_low_pe + historical_high_pe) / 2.0
	# Multiply the growth rate by 100 to convert from a decimal to a percent.
	future_pe_two = 2.0 * (estimated_growth_rate * 100.0)
	conservative_future_pe = min(future_pe_one, future_pe_two)
	return conservative_future_pe


def calculate_estimated_future_price(future_eps, future_pe):
	"""
	Calculates the estimated future price of a stock.

	@param future_eps: A future earnings-per-share (EPS) value, typically on a
			10-year time horizon.
	@param future_pe: A future price-to-earnings (PE) value.

	@return: The estimated future price of a stock.
	"""
	if not future_eps or not future_pe:
		return None
	return future_eps * future_pe


def calculate_sticker_price(future_price: int, time_horizon: int = 10,
                            rate_of_return: float = 0.15) -> Optional[float]:
	"""
	Calculates the sticker price of a stock given its estimated future price and
	a desired rate of return.

	This implements the underlying formula as the Excel "PV" (present value)
	function.

	@param future_price: The estimated future price of a stock.
	@param time_horizon: The desired time horizon to calculate for. Defaults to 10.
	@param rate_of_return: The desired minimum rate of return.

	@return: The calculated sticker price.
	"""
	# PV = FV / (1 + r)^n
	# where r -> rate and n -> years
	if not future_price:
		return None
	target_growth_rate = math.pow(1.0 + rate_of_return, time_horizon)
	sticker_price = future_price / target_growth_rate
	return sticker_price


def calculate_margin_of_safety(sticker_price: float, margin_of_safety: int = 0.5) -> Optional[float]:
	"""
	Calculates a margin of safety price for a stock.

	@param sticker_price: The sticker price of a stock.
	@param margin_of_safety: The desired margin of safety as a percentage. Defaults to
		0.5 (i.e. 50%).

	@return: The margin of safety price.
	"""
	if not sticker_price:
		return None
	return sticker_price * (1 - margin_of_safety)


def calculate_roic(net_income: int, cash: int, long_term_debt: int, stockholder_equity: int) -> Optional[float]:
	"""
	Calculates roic
	
	@param net_income: Net income
	@param cash: Current cash
	@param long_term_debt: Long term debt
	@param stockholder_equity: Equity of stockholder
	@return: Roic
	"""
	if not net_income or not cash or not long_term_debt or not stockholder_equity:
		return None
	
	return (net_income / (stockholder_equity + long_term_debt - cash)) * 100
