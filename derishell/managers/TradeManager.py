import time
import collections

from terminaltables import AsciiTable

from derishell.util.deribit_api import RestClient

from derishell.util.Util import Util
from derishell.util.ColorText import ColorText
from derishell.managers.ConfigManager import ConfigManager
from derishell.managers.DatabaseManager import DatabaseManager

class TradeManager:

    stopLossTriggered = False

    @staticmethod
    def create_new_buy_order(price, amount):
        Util.get_logger().info("Placing Buy Order for " + str(amount) + " contracts at " + str(price))
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)
        order = client.buy(ConfigManager.get_config().tradeInsturment, amount, price, False, "")
        return order

    @staticmethod
    def create_new_sell_order(price, amount):
        Util.get_logger().info("Placing Sell Order for " + str(amount) + " contracts at " + str(price))
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)
        order = client.sell(ConfigManager.get_config().tradeInsturment, amount, price, True, "")
        return order

    @staticmethod
    def create_sl_sell_order(price, amount):
        Util.get_logger().info("Placing SL Sell Order for " + str(amount) + " contracts at " + str(price))
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)
        order = client.sell_stop_market_order(ConfigManager.get_config().tradeInsturment, amount, price)
        return order        

    @staticmethod
    def setup_inital_ladder():
        Util.get_logger().info("Setup initial ladder")

        for x in range(ConfigManager.get_config().numOfOrders):
            DatabaseManager.create_order_entry("", (ConfigManager.get_config().basePrice - ConfigManager.get_config().priceDistance) - (ConfigManager.get_config().priceDistance * x), ConfigManager.get_config().contractSize, "buy")


        TradeManager.update_pending_orders()

        # Create the stop loss order
        order = TradeManager.create_sl_sell_order(ConfigManager.get_config().stopLossPrice, ConfigManager.get_config().numOfOrders * ConfigManager.get_config().contractSize)
        DatabaseManager.create_sl_order_entry(order['order']['orderId'], ConfigManager.get_config().stopLossPrice, ConfigManager.get_config().numOfOrders * ConfigManager.get_config().contractSize)


    @staticmethod
    def cancel_all_current_orders():

        orders = DatabaseManager.get_all_open_orders()
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)

        for order in orders:
            client.cancel(order.orderId)
            DatabaseManager.update_order_entry(order.orderId, "cancelled")
            Util.get_logger().info("Cancelled order: " + str(order.orderId))


    @staticmethod
    def close_all_positions():
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)
        positions = client.positions()

        for x in positions:
            if x['direction'] == 'buy':
                client.sell(ConfigManager.get_config().tradeInsturment, x['size'], 1, False, "")
            else:
                client.buy(ConfigManager.get_config().tradeInsturment, x['size'], 99999, False, "")

    @staticmethod
    def update_pending_orders():

        orders = DatabaseManager.get_all_pending_orders()

        for order in orders:

            if order.direction == 'buy':
                #if currentPrice > order.price:
                newOrder = TradeManager.create_new_buy_order(order.price, order.contractSize)
                DatabaseManager.update_new_order_entry(order, newOrder['order']['orderId'], "open")

            else:
                newOrder = TradeManager.create_new_sell_order(order.price, order.contractSize)
                DatabaseManager.update_new_order_entry(order, newOrder['order']['orderId'], "open")


    @staticmethod
    def update_order_status():

        if TradeManager.stopLossTriggered == False:
            orders = DatabaseManager.get_all_open_orders()

            client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)

            for order in orders:

                try:
                    
                    updatedOrder = client.getorderstate(order.orderId)

                    DatabaseManager.update_order_entry(order.orderId, updatedOrder['state'])

                    if updatedOrder['state'] == "filled":

                        if "SLMS" in order.orderId:
                            # Stop loss fired
                            Util.get_logger().info("STOP LOSS FIRED - CANCELLING ALL ORDERS")
                            TradeManager.cancel_all_current_orders()

                            TradeManager.stopLossTriggered = True


                        else:
                            if updatedOrder['direction'] == "buy":

                                if ConfigManager.get_config().fcbMode:
                                    #Create new one
                                    DatabaseManager.create_order_entry("", order.price + ConfigManager.get_config().priceDistance, ConfigManager.get_config().contractSize, "sell")

                                else:
                                    sellPriceOffset = ConfigManager.get_config().basePrice - order.price
                                    DatabaseManager.create_order_entry("", ConfigManager.get_config().basePrice + sellPriceOffset, ConfigManager.get_config().contractSize, "sell")

                            else:

                                if ConfigManager.get_config().fcbMode:
                                    DatabaseManager.create_order_entry("", order.price - ConfigManager.get_config().priceDistance, ConfigManager.get_config().contractSize, "buy")
                                else:
                                    # put in buy order
                                    buyPriceOffset = order.price - ConfigManager.get_config().basePrice
                                    DatabaseManager.create_order_entry("",ConfigManager.get_config().basePrice + buyPriceOffset , ConfigManager.get_config().contractSize, "buy")
                except:
                    pass
        else:
            #We no longer update our queue until user resets
            pass


    @staticmethod
    def update_all():
        TradeManager.update_order_status()
        TradeManager.update_pending_orders()


    @staticmethod
    def show_sells_table(orders):

        sortedDict = {}

        for order in orders:
            sortedDict[order.price] = order

        sortedDict = collections.OrderedDict(sorted(sortedDict.items()))

        table_data = [
            ['#', 'OrderId', 'Price', 'Contract Size', 'Status', 'Direction'],
        ]

        for order in list(sortedDict.values())[::-1]:
            if order.direction == "sell":
                table_data.append([order.id, order.orderId, order.price, order.contractSize, order.status, ColorText.red(order.direction)])

        table = AsciiTable(table_data, "Current Open Sell Orders")
        print(table.table)

    @staticmethod
    def show_buys_table(orders):

        sortedDict = {}

        for order in orders:
            sortedDict[order.price] = order

        sortedDict = collections.OrderedDict(sorted(sortedDict.items()))

        table_data = [
            ['#', 'OrderId', 'Price', 'Contract Size', 'Status', 'Direction'],
        ]

        for order in list(sortedDict.values())[::-1]:
            if order.direction == "buy":
                table_data.append([order.id, order.orderId, order.price, order.contractSize, ColorText.yellow(order.status) if order.status=="pending" else order.status, ColorText.green(order.direction)])

        table = AsciiTable(table_data, "Current Open Buy Orders")
        print(table.table)    

    @staticmethod
    def show_current_orders():

        openOrders = DatabaseManager.get_all_open_orders() + DatabaseManager.get_all_pending_orders()

        print()

        table_data = []

        table_data.append([ColorText.yellow(ConfigManager.get_config().basePrice)])
        table = AsciiTable(table_data, "Base")
        print(table.table)

        print()

        TradeManager.show_sells_table(openOrders)

        print()

        TradeManager.show_buys_table(openOrders)

        print()
