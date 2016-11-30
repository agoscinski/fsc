# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 13:13:40 2016

@author: Emely
"""

import numpy as np
import TradingClass


def pro_rata(buy, sell):
    """Matching algorithm using pro rata algorithm

    Require: buy and sell orders shall not been matured yet

    Args:
        buy (list of TradingClass.Order):
        sell (list of TradingClass.Order):
    Returns:
        return trade matrix with traded shares
        set buy and sell shares to new amount"""

    if (len(buy) == 0):
        return 0

    if (len(sell) == 0):
        return 0

    lb = len(buy)
    ls = len(sell)

    "get total volume of buy"
    volbuy = 0
    for i in range(lb):
        volbuy += buy[i].get_order_qty()

    "get total volume of sell"
    volsell = 0
    for i in range(ls):
        volsell += sell[i].get_order_qty()

    "compare volumes"
    if (volsell > volbuy):
        dif = volsell - volbuy - 1
        while (dif > 0):
            dif = dif - sell[ls - 1].get_order_qty()
            ls = ls - 1

    summ = 0

    for i in range(ls):
        summ += buy[i].get_order_qty() * (i + 1)

    "list of transactions, line is seller(i), row is buyer(j)"
    trade = np.zeros(shape=(len(sell), len(buy)))

    "time pro rata algorithm"
    p = []
    for i in range(lb):
        p.append((buy[i].get_order_qty() * buy[i].get_price() * (i + 1)) / summ)

    P = []
    for i in range(lb):
        comp = [buy[i].get_order_qty() * buy[i].get_price(), np.floor(p[i] * len(sell))]
        P.append(np.min(comp))

    for i in range(ls):
        while (sell[i].get_order_qty() > 0):
            for j in range(lb):
                if P[j] > 0:
                    P[j] -= 1
                    buy[j].set_order_qty(buy[j].get_order_qty() - 1)
                    sell[i].set_order_qty(sell[i].get_order_qty() - 1)
                    trade[[i], [j]] += 1
                    if (sell[i].get_order_qty() == 0):
                        break

    return trade


def match(orders):
    """This function takes a list of orders and returns the execution

    Args:
        orders (list of TradingClass.Order): These are the are orders the algorithm received

    Returns:
        order_executions (list of TradingClass.ExecutionReport)
    """
    buy_orders, sell_orders = extract_buy_and_sell_orders(orders)
    trading_matrix = pro_rata(buy_orders, sell_orders)
    order_executions = extract_order_executions_out_of_trading_matrix(trading_matrix)
    return order_executions


def extract_buy_and_sell_orders(orders):
    """This function takes a list of orders and returns one list with all buy orders, and one with all sell orders

    Args:
        orders (list of TradingClass.Order): These are the are orders the algorithm received

    Returns:
        buy_orders (list of TradingClass.ExecutionReport): Orders from type buy/bid
        sell_orders (list of TradingClass.ExecutionReport): Orders from type sell/offer
    """
    buy_orders = []
    sell_orders = []
    for order in orders:
        if order.side == TradingClass.OrderSideType.BUY:
            buy_orders.append(order)
        elif order.side == TradingClass.OrderSideType.SELL:
            sell_orders.append(order)
    return buy_orders, sell_orders


def extract_order_executions_out_of_trading_matrix(trading_matrix, buy_orders, sell_orders):
    """Transforms a trading matrix to a list of buy and sell orders

    Function requires number of rows trading_matrix is the same as the length of sell_orders
    and number of columns trading_matrix is the same as the length of buy_orders.
    Function requires only buy orders are in the buy_orders list and only sell orders are in the
    sell_orders list

    Args:
        trading_matrix (numpy.array): An array where in each row represents a sell order
            and each column represents one buy order
        buy_orders (list of TradingClass.Order): A list of buy orders related to the trading_matrix
        sell_orders (list of TradingClass.Order): A list of sell orders related to the trading_matrix

    Returns:
        order_executions (list of TradingClass.OrderExecution)
    """
    execution_orders = []
    current_timestamp = TradingClass.FIXDateTimeUTC.create_for_current_time()
    for i in trading_matrix.shape[0]:
        for j in trading_matrix.shape[1]:
            execution_order = create_order_execution_from_trading_matrix_entry(trading_matrix[i, j], buy_orders[j],
                                                                               sell_orders[i], current_timestamp)
            execution_orders.append(execution_order)

    return execution_orders


class MatchingError(object):
    pass


def create_order_execution_from_trading_matrix_entry(trading_matrix_entry, buy_order, sell_order, timestamp):
    """Creates an order execution from an entry in a trading matrix

    Args:
        trading_matrix_entry (float): An array where in each row represents a sell order
            and each column represents one buy order
        buy_order (TradingClass.Order): order from type buy/bid
        sell_order (TradingClass.Order): order from type sell/offer
        timestamp (TradingClass.FIXDateTimeUTC): timestamp for the order execution

    Returns:
        order_execution (TradingClass.OrderExecution)
    """
    matched_price = determine_price_for_match(buy_order, sell_order)
    execution_order = TradingClass.OrderExecution.from_buy_and_sell_order(executed_quantity=trading_matrix_entry,
                                                                          executed_price=matched_price,
                                                                          buy_order=buy_order,
                                                                          sell_order=sell_order,
                                                                          execution_time=timestamp)
    return execution_order


#TODO two market orders should be matched on current market price, otherwise it only makes sense create exetreme high prices for market orders, to get higher value
def determine_price_for_match(buy_order, sell_order):
    """Determines the price between a buy and sell order which has been matched

    If between a sell and buy order price is an intersection they can agree on, then the price in the middle will be
    determined. If there is no intersection but both orders are market order then still the price in the middle will
    be determined. If there is no intersection and only one order is a limit order, then the price of the limit order
    determines the price. If there is not intersection and both order are limite order, then an error will be outputted

    Args:
        buy_order (TradingClass.Order): order from type buy/bid
        sell_order (TradingClass.Order): order from type sell/offer

    Returns:
        matched_price (float): the price on which buyer and seller will agree on
    """

    is_intersection = buy_order.price >= sell_order.price
    if is_intersection:
        return sell_order.price + (buy_order.price - sell_order.price) / 2.
    elif buy_order.order_type == TradingClass.OrderType.MARKET and sell_order.order_type == TradingClass.OrderType.MARKET:
        return buy_order.price + (sell_order.price - buy_order.price) / 2.
    elif buy_order.order_type == TradingClass.OrderType.LIMIT and sell_order.order_type == TradingClass.OrderType.LIMIT:
        raise MatchingError("Matched orders have no intersection in price and are both limit orders.")
    else:
        # the state is only one order is a limit order
        limit_order = buy_order if buy_order.order_id == TradingClass.OrderType.LIMIT else sell_order
        return limit_order.price
