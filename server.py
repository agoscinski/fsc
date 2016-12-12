from tarfile import _section
import quickfix as fix
import quickfix42 as fix42
import re
import time
import datetime
import yahoo_finance
import MySQLdb
from enum import Enum
import matching_algorithm
import TradingClass
from TradingClass import MarketDataResponse
from TradingClass import NewSingleOrder
from TradingClass import OrderCancelRequest
from TradingClass import Order
from TradingClass import OrderCancelReject
from TradingClass import ExecutionReport
from TradingClass import FIXDateTimeUTC


class ServerRespond(Enum):
    AUTHENTICATION_FAILED = 0
    AUTHENTICATION_SUCCESS = 1


class ServerFIXApplication(fix.Application):

    def __init__(self, server_fix_handler):
        self.server_fix_handler = server_fix_handler
        super(ServerFIXApplication, self).__init__()

    def onCreate(self, session_id):
        self.sessionID = session_id
        return

    def onLogon(self, session_id):
        return

    def onLogout(self, session_id):
        return

    def toAdmin(self, message, session_id):
        return

    def fromAdmin(self, message, session_id):
        """React to admin level messages

        This function is invoked when administrative message is received. For example: Logon, Logout, Heartbeat.
        TODO what is a administrative message?

        Args:
            message (Swig Object of type 'FIX::Message *'): The received message
            session_id (Swig Object of type 'FIX::SessionID *'): The received message

        Returns:
            None
        """

        # begin_string = message.getHeader().getField(fix.BeginString())  # returns 'FIX::FieldBase *'
        msg_type = message.getHeader().getField(fix.MsgType())
        if msg_type.getString() == fix.MsgType_Logon:
            self.server_fix_handler.handle_logon_request(message)
        else:
            # TODO send error: MsgType not understand
            pass

        return

    def toApp(self, message, session_id):
        return

    def fromApp(self, message, session_id):
        """React to application level messages

        This function is invoked when a application level request is received.
        TODO What is a application level request?

        Args:
            message (Swig Object of type 'FIX::Message *'): The received message
            session_id (Swig Object of type 'FIX::SessionID *'): The received message

        Returns:
            None
        """
        # beginString = message.getHeader().getField(fix.BeginString())
        msg_Type = message.getHeader().getField(fix.MsgType())
        if msg_Type.getString() == fix.MsgType_MarketDataRequest:
            print '''IN MarketDataRequest'''
            self.server_fix_handler.handle_market_data_request(message)
        elif msg_Type.getString() == fix.MsgType_NewOrderSingle:
            print '''IN NewSingleOrder'''
            self.server_fix_handler.handle_order_request(message)
        elif msg_Type.getString() == fix.MsgType_OrderCancelRequest:
            print '''IN OrderCancelRequest'''
            self.server_fix_handler.handle_order_cancel_request(message)

class ServerFIXHandler:
    def __init__(self, server_logic, server_config_file_name):
        self.server_logic = server_logic
        self.server_config_file_name = server_config_file_name
        self.fix_application = None
        self.socket_acceptor = None

    def start(self):
        self.init_fix_settings()
        self.socket_acceptor.start()

    def stop(self):
        self.socket_acceptor.stop()

    def init_fix_settings(self):
        settings = fix.SessionSettings(self.server_config_file_name)
        self.fix_application = ServerFIXApplication(self)
        self.storeFactory = fix.FileStoreFactory(settings)
        #self.logFactory = fix.FileLogFactory(settings)
        self.logFactory = fix.ScreenLogFactory(settings)
        self.socket_acceptor = fix.SocketAcceptor(self.fix_application, self.storeFactory, settings, self.logFactory)

    def handle_logon_request(self, message):
        password = message.getField(fix.RawData())
        user_id = message.getHeader().getField(fix.SenderSubID())
        logon_respond = self.server_logic.process_logon(user_id, password)
        if logon_respond == ServerRespond.AUTHENTICATION_FAILED:
            # TODO reject client AUTHENTICATION_FAILED
            pass

        return

    def handle_market_data_request(self, message):
        """Process market data request

    		Args:
    			message (fix message): market data request message

    		Returns:
    			None
    		"""
        market_data_request = TradingClass.MarketDataRequest.from_fix_message(message)

        # Market data Object sent to server logic to be processed
        self.server_logic.process_market_data_request(market_data_request)
        return

    # return_to_gui: current_price, day_high, day_low : json_string;
    # time_stamp, price, quantity : json_string; orderstuff : json

    def send_market_data_respond(self, market_data):
        """Send market data respond

            Args:
                market_data MarketDataResponse Object

            Returns:
                None
            """

        # Create Market Data Response Fix Message from market_data
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_MarketDataSnapshotFullRefresh))
        header.setField(fix.MsgSeqNum(1))
        header.setField(fix.SendingTime())
        message.setField(fix.MDReqID(market_data.md_req_id))
        message.setField(fix.NoMDEntries(market_data.no_md_entry_types))
        message.setField(fix.Symbol(market_data.symbol))
        message.setField(fix.TotalVolumeTraded(market_data.md_total_volume_traded))

        group_md_entry = fix42.MarketDataSnapshotFullRefresh.NoMDEntries()
        md_entry_type = market_data.md_entry_type_list
        md_entry_px = market_data.md_entry_px_list
        md_entry_size = market_data.md_entry_size_list
        md_entry_date = market_data.md_entry_date_list
        md_entry_time = market_data.md_entry_time_list
        entry_date_fix = fix.MDEntryDate()
        entry_time_fix = fix.MDEntryTime()
        for md_index in range(market_data.no_md_entry_types):
            entry_date_fix.setString(md_entry_date[md_index].__str__())
            # TODO time should not be here i think
            # entry_time_fix.setString(md_entry_time[md_index].__str__())
            group_md_entry.setField(fix.MDEntryType(md_entry_type[md_index]))
            group_md_entry.setField(fix.MDEntryPx(md_entry_px[md_index]))
            group_md_entry.setField(fix.MDEntrySize(md_entry_size[md_index]))
            group_md_entry.setField(entry_date_fix)
            group_md_entry.setField(entry_time_fix)
            message.addGroup(group_md_entry)

        # Send the message to client
        fix.Session.sendToTarget(message, self.fix_application.sessionID)

        return

    def handle_order_request(self, fix_message):
        """Process order request from a client

            Args:
                fix_message (quickfix.Message): order fix message received from client

            Returns:
                None
        """
        fix_order = NewSingleOrder.from_fix_message(fix_message)
        self.server_logic.process_new_single_order_request(fix_order)
        return

    def handle_order_cancel_request(self, message):
        #TODO documentation
        order_cancel_request = OrderCancelRequest.from_fix_message(message)
        self.server_logic.process_order_cancel_request(order_cancel_request)

    def send_execution_report_respond(self, execution_report):
        """Sends an execution report respond

            Args:
                execution_report (TradingClass.ExecutionReport): the report which will be sent

            Returns:
                None
            """
        fix_message = execution_report.create_fix_message()
        fix.Session.sendToTarget(fix_message, self.fix_application.sessionID)
        return

    def send_reject_order_execution_respond(self, execution_report):
        """Send order reject execution respond

            Args:
                execution_report (TradingClass.ExecutionReport):

            Returns:
                None
            """
        fix_message = execution_report.create_fix_message()
        fix.Session.sendToTarget(fix_message, self.fix_application.sessionID)
        return

    def send_order_cancel_execution_respond(self, order_cancel_execution):
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_ExecutionReport))
        header.setField(fix.SendingTime())

        message.setField(fix.OrderID(order_cancel_execution.order_id))
        message.setField(fix.ClOrdID(order_cancel_execution.client_order_id))
        if order_cancel_execution.original_client_order_id is not None:
            message.setField(fix.OrigClOrdID(order_cancel_execution.original_client_order_id))
        if order_cancel_execution.price is not None:
            message.setField(fix.Price(order_cancel_execution.price))
        message.setField(fix.ExecID(order_cancel_execution.execution_id))
        message.setField(fix.ExecTransType(order_cancel_execution.execution_transaction_type))
        message.setField(fix.ExecType(order_cancel_execution.execution_type))
        message.setField(fix.OrdStatus(order_cancel_execution.order_status))
        message.setField(fix.Symbol(order_cancel_execution.symbol))
        message.setField(fix.Side(order_cancel_execution.side))
        message.setField(fix.LeavesQty(order_cancel_execution.left_quantity))
        message.setField(fix.CumQty(order_cancel_execution.cumulative_quantity))
        message.setField(fix.AvgPx(order_cancel_execution.average_price))

        fix.Session.sendToTarget(message, self.fix_application.sessionID)

    def send_order_cancel_reject_respond(self, order_cancel_reject):
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_OrderCancelReject))

        message.setField(fix.OrderID(order_cancel_reject.order_id))
        message.setField(fix.ClOrdID(order_cancel_reject.cl_ord_id))
        message.setField(fix.OrigClOrdID(order_cancel_reject.orig_cl_ord_id))
        message.setField(fix.OrdStatus(order_cancel_reject.ord_status))
        message.setField(fix.CxlRejResponseTo(order_cancel_reject.cxl_rej_response_to))
        if order_cancel_reject.cxl_rej_reason is not None:
            message.setField(fix.CxlRejReason(order_cancel_reject.cxl_rej_reason))

        fix.Session.sendToTarget(message, self.fix_application.sessionID)
        return


class ServerLogic:
    exec_id = 0
    order_id = 0
    cancel_order_id = 0

    def __init__(self, server_config_file_name, server_database_handler=None):
        self.server_fix_handler = ServerFIXHandler(self, server_config_file_name)
        self.server_database_handler = ServerDatabaseHandler() if server_database_handler == None else server_database_handler
        self.market_simulation_handler = MarketSimulationHandler()
        self.initialize_new_database = False

    def start_server(self):
        if self.initialize_new_database:
            self.server_database_handler.create_database()
            self.market_simulation_handler.init_market()
        self.server_fix_handler.start()
        while 1: time.sleep(1)
        self.stop_server()

    def stop_server(self):
        self.server_fix_handler.stop()

    def gen_exec_id(self):
        self.exec_id = self.exec_id + 1
        return self.exec_id

    def gen_order_id(self):
        self.order_id = self.order_id + 1
        return self.order_id

    def gen_order_cancel_id(self):
        self.cancel_order_id = self.cancel_order_id + 1
        return self.cancel_order_id

    def authenticate_user(self, user_id, password):
        """Authenticates user

        Checks if user with the given id and password exists in database

        Args:
            user_id (string): The user id
            password (string): The password

        Returns:
            success (ServerRespond): success of authentication
        """
        # TODO #29 add authentication
        return ServerRespond.AUTHENTICATION_SUCCESS

    def process_logon(self, user_id, password):
        respond = self.authenticate_user(user_id, password)
        return respond

    def process_market_data_request(self, md_request):
        """Process market data request

		Args:
			md_request : MarketDataRequest Object

		Returns:
			bool: The return value. True for success, False otherwise.
		"""

        # Subscribe means will be sent periodically, so for now we use snapshot
        if md_request.subscription_request_type == 0:
            print("0 = Snapshot")
        elif md_request.subscription_request_type == 1:
            print("1 = Snapshot + Updates (Subscribe)")
        elif md_request.subscription_request_type == 2:
            print("2 = Disable previous Snapshot + Update Request (Un-subscribe)")

        # Now we wll only support Top of Book (only best prices quoted), Full of Book means all the traded data.
        if md_request.market_depth == 0:
            print("Full Book")
        elif md_request.market_depth == 1:
            print("Top of Book")

        md_req_id = md_request.md_req_id
        no_md_entries = md_request.no_md_entry_types
        symbol = md_request.symbol_list[0]
        md_entry_type_list = md_request.md_entry_type_list

        pending_stock_orders = self.server_database_handler.fetch_pending_order_with_cumulative_quantity_by_stock_ticker(symbol)
        stock_information = self.server_database_handler.fetch_stock_information(symbol)
        market_data_response = self.pack_into_fix_market_data_response(md_req_id, md_entry_type_list, symbol,
                                                                       pending_stock_orders, stock_information)

        self.server_fix_handler.send_market_data_respond(market_data_response)

        pass

    def process_order_request(self, requested_fix_order):
        """Process an order request from the FIX Handler

        Args:
            requested_fix_order (NewSingleOrder): NewSingleOrder Object from fix handler

        Returns:
            None
        """

        requested_order = TradingClass.Order.from_new_single_order(requested_fix_order)
        order_is_valid = self.check_if_order_is_valid(requested_order)
        if order_is_valid:
            self.process_valid_order_request(requested_order)
        else:
            self.process_invalid_order_request(requested_order)

    def process_valid_order_request(self, requested_order):
        """
        Args:
            requested_order (TradingClass.Order):
        """
        self.server_database_handler.insert_order(requested_order)
        acknowledge_execution_report = self.create_execution_report_for_new_order(requested_order)
        self.server_fix_handler.send_execution_report_respond(acknowledge_execution_report)
        orders = self.server_database_handler.fetch_pending_order_with_cumulative_quantity_by_stock_ticker(requested_order.symbol)
        order_executions = matching_algorithm.match(orders)
        for order_execution in order_executions:
            order_execution.execution_id = self.server_database_handler.insert_order_execution(order_execution)
            execution_report_of_buy_order, execution_report_of_sell_order = self.create_execution_report_for_order_execution(
                order_execution)
            self.server_fix_handler.send_execution_report_respond(execution_report_of_buy_order)
            self.server_fix_handler.send_execution_report_respond(execution_report_of_sell_order)
        return None

    def process_invalid_order_request(self, requested_order):
        order_id = str(self.gen_order_id())
        exec_id = str(self.gen_exec_id())
        cl_ord_id = requested_order.client_order_id
        receiver_comp_id = requested_order.account_company_id
        exec_trans_type = TradingClass.FIXHandlerUtils.ExecutionTransactionType.NEW
        exec_type = TradingClass.FIXHandlerUtils.ExecutionType.REJECTED
        ord_status = TradingClass.FIXHandlerUtils.OrderStatus.REJECTED
        symbol = requested_order.stock_ticker
        side = requested_order.side
        price = requested_order.price
        stop_px = None
        leaves_qty = 0
        cum_qty = 0
        avg_px = 0

        # Encapsulate result of processing into execution report
        reject_order_execution = TradingClass.ExecutionReport(order_id, cl_ord_id, exec_id, exec_trans_type, exec_type,
                                                              ord_status
                                                              , symbol, side, leaves_qty, cum_qty, avg_px, price,
                                                              stop_px, receiver_comp_id)
        self.server_fix_handler.send_reject_order_execution_respond(reject_order_execution)

    def check_if_order_is_valid(self, requested_order):

        if(self.current_server_time>=self.end_time or self.current_server_time<=self.start_time):
            return False

        stock_total_volume = self.server_database_handler.fetch_stock_total_volume(requested_order.stock_ticker)
        stock_information = self.server_database_handler.fetch_stock_information(requested_order.stock_ticker)
        current_price = stock_information.current_price

        price_difference = requested_order.price - current_price
        traded_value_difference = requested_order.price * requested_order.order_quantity - stock_total_volume * current_price

        is_valid = (0.1 >= price_difference >= -0.1 and 0.2 >= traded_value_difference >= -0.2)
        return is_valid

    def process_invalid_order_cancel_request(self, requested_order_cancel):
        """Process an invalid order cancel request and create OrderCancelReject Fix object to be sent through FixHandler

        Args:
            requested_order_cancel (OrderCancel): OrderCancel Object created from OrderCancelRequest Fix object

        Returns:
            None
        """
        order_id = str(self.gen_order_cancel_id())
        cl_ord_id = requested_order_cancel.order_cancel_id
        orig_cl_ord_id = requested_order_cancel.client_order_id
        receiver_comp_id = requested_order_cancel.account_company_id
        ord_status = '8'
        cxl_rej_response_to = '1'
        cxl_rej_reason = None
        order_cancel_reject = OrderCancelReject(orig_cl_ord_id, cl_ord_id, order_id, ord_status, cxl_rej_response_to,
                                                receiver_comp_id, cxl_rej_reason)
        self.server_fix_handler.send_order_cancel_reject_respond(order_cancel_reject)

    def process_order_cancel_request(self, order_cancel_request):
        """Process an invalid order cancel request from Fix Handler

        Args:
            order_cancel_request (OrderCancelRequest): OrderCancelRequest Object from fix handler

        Returns:
            None
        """
        requested_order_cancel = TradingClass.OrderCancel.from_order_cancel_request(order_cancel_request)
        order = self.server_database_handler.fetch_latest_order_by_client_information(
            requested_order_cancel.client_order_id, requested_order_cancel.account_company_id)
        requested_order_cancel.order_received_date = order.received_date
        order_cancel_is_valid = self.check_if_order_cancel_is_valid(order)
        if order_cancel_is_valid:
            self.process_valid_order_cancel_request(requested_order_cancel, order)
        else:
            self.process_invalid_order_cancel_request(requested_order_cancel)

    def check_if_order_cancel_is_valid(self, order):
        """Check whether an order cancel request is valid or not valid based on status of Order Object

        Args:
            order (Order): Order object created based on OrderCancel object

        Returns:
            True or False
        """
        if order is None:
            return False
        elif (order.last_status == TradingClass.DatabaseHandlerUtils.LastStatus.DONE or
                      order.last_status == TradingClass.DatabaseHandlerUtils.LastStatus.CANCELED
            or order.last_status == TradingClass.DatabaseHandlerUtils.LastStatus.EXPIRED):
            return False
        else:
            return True

    def process_valid_order_cancel_request(self, requested_order_cancel, order):
        """Process a valid order cancel request and create ExecutionReport Fix object to be sent through FixHandler

        Args:
            requested_order_cancel (OrderCancel): OrderCancel object created based on OrderCancelRequest Fix object
            order (Order): Order object based on OrderCancel object

        Returns:
            None
        """
        self.server_database_handler.update_order_status(order, TradingClass.DatabaseHandlerUtils.LastStatus.CANCELED)
        cumulative_quantity, average_price = self.server_database_handler.fetch_cumulative_quantity_and_average_price_by_order_id(
            order.client_order_id, order.account_company_id, order.received_date)
        requested_order_cancel.cancel_quantity = order.price-cumulative_quantity
        requested_order_cancel.last_status = TradingClass.DatabaseHandlerUtils.LastStatus.CANCELED
        requested_order_cancel.msg_seq_num = self.gen_order_cancel_id()

        self.server_database_handler.insert_order_cancel(requested_order_cancel)
        # self.server_database_handler.update_order_cancel_success(requested_order_cancel.client_order_id,
        #        requested_order_cancel.account_company_id, OrderCancelStatus.CANCELED, cumulative_quantity, executed_time)

        order_id = str(self.gen_order_cancel_id())
        orig_cl_ord_id = requested_order_cancel.client_order_id
        cl_ord_id = requested_order_cancel.order_cancel_id
        exec_id = str(self.gen_exec_id())
        receiver_comp_id = requested_order_cancel.account_company_id
        exec_trans_type =  TradingClass.FIXHandlerUtils.ExecutionTransactionType.NEW
        exec_type = TradingClass.FIXHandlerUtils.ExecutionType.CANCELED
        ord_status = TradingClass.FIXHandlerUtils.OrderStatus.CANCELED
        symbol = requested_order_cancel.stock_ticker
        side = requested_order_cancel.side
        price = None
        leaves_qty = 0  # could also be filled order quantity-cum_quantity

        order_cancel_execution = ExecutionReport(order_id, cl_ord_id, exec_id, exec_trans_type, exec_type,
                        ord_status, symbol, side, leaves_qty, cumulative_quantity, average_price, price, receiver_comp_id, orig_cl_ord_id)
        self.server_fix_handler.send_order_cancel_execution_respond(order_cancel_execution)

    def create_execution_report_for_new_order(self, new_order):
        """Used to create a execution report for a new order
        Args:
            new_order (TradingClass.Order):

        Returns:
            execution_report (TradingClass.ExecutionReport)
        """
        left_quantity = new_order.order_quantity
        cumulative_quantity = 0
        average_price = 0
        execution_report = TradingClass.ExecutionReport.from_order(new_order, TradingClass.FIXHandlerUtils.ExecutionTransactionType.NEW,
                                                                   TradingClass.FIXHandlerUtils.ExecutionType.NEW,
                                                                   TradingClass.FIXHandlerUtils.OrderStatus.NEW, left_quantity,
                                                                   cumulative_quantity, average_price)
        execution_report.execution_id = self.server_database_handler.insert_execution_report(execution_report)
        return execution_report

    def create_execution_report_for_order_execution(self, order_execution):
        """Creates two execution report for the two matched orders in an order execution

        Args:
            order_execution (TradingClass.OrderExecution): The order execution matching the two orders
             for which an execution report will be created

        Returns:
            execution_report_of_buy_order (a tuple of TradingClass.ExecutionReport): The  execution report referring to
             the buy order of the two matched orders in the order execution.
            execution_report_of_sell_order (a tuple of TradingClass.ExecutionReport): The  execution report referring to
             the buy order of the two matched orders in the order execution.
        """
        execution_report_of_buy_order = self.create_execution_report_for_executed_order(
            order_execution.buyer_client_order_id, order_execution.buyer_company_id,
            order_execution.buyer_received_date, order_execution)
        execution_report_of_sell_order = self.create_execution_report_for_executed_order(
            order_execution.seller_client_order_id, order_execution.seller_company_id,
            order_execution.seller_received_date, order_execution)
        return execution_report_of_buy_order, execution_report_of_sell_order

    def create_execution_report_for_executed_order(self, client_order_id, account_company_id, received_date,
                                                   order_execution):
        """Creates an execution report for the order with the order id (client_order_id, account_company_id,
         received_date).

        Args:
            client_order_id (string): first part of order id
            account_company_id (string: second part of order id
            received_date (TradingClass.FIXDate): third part of order id
            order_execution (TradingClass.OrderExecution): The order execution to be inserted

        Returns:
            execution_report (a tuple of TradingClass.ExecutionReport): The two execution reports resulting from the
             inserted order execution. One for buy side, one for sell side.
        """
        cumulative_quantity, average_price = self.server_database_handler.fetch_cumulative_quantity_and_average_price_by_order_id(
            client_order_id, account_company_id, received_date)
        order = self.server_database_handler.fetch_order_by_order_id(client_order_id, account_company_id,
                                                                     received_date)
        left_quantity = order.order_quantity - cumulative_quantity
        is_order_filled = left_quantity == 0.

        if is_order_filled:
            execution_transaction_type = TradingClass.ExecutionTransactionType.FILL
            execution_type = TradingClass.FIXHandlerUtils.ExecutionType.FILL
            order_status = TradingClass.FIXHandlerUtils.OrderStatus.FILLED
        else:
            execution_transaction_type = TradingClass.FIXHandlerUtils.ExecutionTransactionType.PARTIAL_FILL
            execution_type = TradingClass.FIXHandlerUtils.ExecutionType.PARTIAL_FILL
            order_status = TradingClass.FIXHandlerUtils.OrderStatus.PARTIALLY_FILLED

        order_id = TradingClass.Order.create_order_id(client_order_id, account_company_id, received_date)

        execution_report = TradingClass.ExecutionReport(order_id=order_id, client_order_id=client_order_id,
                                                        execution_id=order_execution.execution_id,
                                                        execution_transaction_type=execution_transaction_type,
                                                        execution_type=execution_type, order_status=order_status,
                                                        symbol=order.symbol,
                                                        side=order.side, price=order.price, left_quantity=left_quantity,
                                                        cumulative_quantity=cumulative_quantity,
                                                        average_price=average_price)
        return execution_report

    def pack_into_fix_market_data_response(self, market_data_required_id, market_data_entry_types, symbol,
                                           pending_stock_orders, stock_information):
        """
        Args
            pending_stock_orders (list of TradingClass.Order)
            stock_information (TradingClass.DatabaseStockInformation)
            market_data_entry_types (list of strings): the types of orders which should be included
        Returns:

        """
        market_data_entry_type_list = []
        market_data_entry_price_list = []
        market_data_entry_size_list = []
        market_data_entry_date_list = []
        market_date_entry_time_list = []

        for pending_order in pending_stock_orders:
            # TODO make this more beautiful
            order_entry_type = 0
            if pending_order.side == 1:
                order_entry_type = 0
            elif pending_order.side == 2:
                order_entry_type = 1

            if order_entry_type in market_data_entry_types:
                # TODO show how with property this can be done better
                pending_order_date_time = pending_order.received_date.date
                pending_order_fix_date = TradingClass.FIXDate.from_year_month_day(pending_order_date_time.year,
                                                                                  pending_order_date_time.month,
                                                                                  pending_order_date_time.day)
                # TODO there should be not time anymore isn it?
                # pending_order_fix_time = TradingClass.TimeFix(pending_order_date_time.hour, pending_order_date_time.minute,
                #                                           pending_order_date_time.second)

                market_data_entry_type_list.append(str(order_entry_type))
                market_data_entry_price_list.append(pending_order.price)
                market_data_entry_size_list.append(pending_order.order_quantity)
                market_data_entry_date_list.append(pending_order_fix_date)
                # market_date_entry_time_list.append(pending_order_fix_time)

        current_date_time = datetime.datetime.now()
        current_fix_date = TradingClass.FIXDate.from_year_month_day(current_date_time.year, current_date_time.month,
                                                                    current_date_time.day)
        current_fix_time = TradingClass.FIXTime(current_date_time.hour, current_date_time.minute,
                                                current_date_time.second)
        if TradingClass.FIXHandlerUtils.MarketDataEntryType.TRADE in market_data_entry_types:
            market_data_entry_type_list.append(TradingClass.FIXHandlerUtils.MarketDataEntryType.TRADE)
            market_data_entry_price_list.append(stock_information.current_price)
            market_data_entry_size_list.append(0)
            market_data_entry_date_list.append(current_fix_date)
            market_date_entry_time_list.append(current_fix_time)

        # TODO Not Finished! Filled with dummy only to not cause error in client side
        # if TradingClass.FIXHandler.MarketDataEntryType.OPENING in market_data_entry_types_integer:
        # if 5 in market_data_entry_types_integer:
        # if 7 in market_data_entry_types_integer:
        # if 8 in market_data_entry_types_integer:

        if TradingClass.FIXHandlerUtils.MarketDataEntryType.OPENING in market_data_entry_types:
            market_data_entry_type_list.append(TradingClass.FIXHandlerUtils.MarketDataEntryType.OPENING)
            market_data_entry_price_list.append(20)
            market_data_entry_size_list.append(0)
            market_data_entry_date_list.append(current_fix_date)
            market_date_entry_time_list.append(current_fix_time)

        if TradingClass.FIXHandlerUtils.MarketDataEntryType.CLOSING in market_data_entry_types:
            market_data_entry_type_list.append(TradingClass.FIXHandlerUtils.MarketDataEntryType.CLOSING)
            market_data_entry_price_list.append(20)
            market_data_entry_size_list.append(0)
            market_data_entry_date_list.append(current_fix_date)
            market_date_entry_time_list.append(current_fix_time)

        if TradingClass.FIXHandlerUtils.MarketDataEntryType.SESSION_HIGH in market_data_entry_types:
            market_data_entry_type_list.append(TradingClass.FIXHandlerUtils.MarketDataEntryType.SESSION_HIGH)
            market_data_entry_price_list.append(20)
            market_data_entry_size_list.append(0)
            market_data_entry_date_list.append(current_fix_date)
            market_date_entry_time_list.append(current_fix_time)

        if TradingClass.FIXHandlerUtils.MarketDataEntryType.SESSION_LOW in market_data_entry_types:
            market_data_entry_type_list.append(TradingClass.FIXHandlerUtils.MarketDataEntryType.SESSION_LOW)
            market_data_entry_price_list.append(stock_information.current_price)
            market_data_entry_size_list.append(20)
            market_data_entry_date_list.append(current_fix_date)
            market_date_entry_time_list.append(current_fix_time)

        # TODO Add Total Volume Traded but not readed from database yet!
        market_data = MarketDataResponse(market_data_required_id, len(market_data_entry_type_list), symbol,
                                         market_data_entry_type_list, market_data_entry_price_list,
                                         market_data_entry_size_list, market_data_entry_date_list,
                                         market_date_entry_time_list,
                                         stock_information.current_volume)
        return market_data


class ServerDatabaseHandler(TradingClass.DatabaseHandler):

    def insert_execution_report(self, execution_report):
        # MAYBETODO
        return 0

    def insert_order_execution(self, order_execution):
        """Inserts an order execution and returns this order execution with an added execution ID

        Args:
            order_execution (TradingClass.OrderExecution): The order execution to be inserted

        Returns:
            order_execution_id (int): The ID of the order execution when inserted

        """
        # TODO use the execute_responsive_insert_sql_command function for this, this function is similar to insert_order

        command = (
            "INSERT INTO OrderExecution(OrderExecutionQuantity, OrderExecutionPrice, ExecutionTime, Order_BuyClientOrderID,"
            "Order_BuyCompanyID, Order_BuyReceivedDate, Order_SellClientOrderID, Order_SellCompanyID, Order_SellReceivedDate)"
            " VALUES('%s','%s','%s', '%s','%s','%s', '%s','%s','%s')"
            % (str(order_execution.quantity), str(order_execution.price), order_execution.execution_time.mysql_date_stamp_string,
               order_execution.buyer_client_order_id,
               order_execution.buyer_company_id, order_execution.buyer_received_date.mysql_date_stamp_string,
               order_execution.seller_client_order_id, order_execution.seller_company_id,
               order_execution.seller_received_date.mysql_date_stamp_string))
        order_execution_id = self.execute_responsive_insert_sql_command(command)
        return order_execution_id

    def fetch_cumulative_quantity_and_average_price_by_order_id(self, client_order_id, account_company_id,
                                                                received_date):
        """Fetches the cumulative quantity and average price of the order with the order id (client_order_id,
         account_company_id, received_date).

        Args:
            client_order_id (string): first part of order id
            account_company_id (string: second part of order id
            received_date (TradingClass.FIXDate): third part of order id
        Returns:
            cumulative_quantity (float): total number of shares filled of an order with the given order id
            average_price (float): the average price of all filled shares
        """
        sql_command = ("select CumulativeQuantity, AveragePrice from `OrderWithCumulativeQuantityAndAveragePrice` "
                       "where ClientOrderID='%s' and Account_CompanyID='%s' and ReceivedDate = '%s'") % (
                          client_order_id, account_company_id, received_date)

        sql_command_result = self.execute_select_sql_command(sql_command)
        if len(sql_command_result) < 1: return None
        cumulative_quantity, average_price = float(sql_command_result[0][0]), float(sql_command_result[0][1])
        return cumulative_quantity, average_price

    def fetch_order_by_order_id(self, client_order_id, account_company_id, received_date):
        """Fetches the order data of the order with the order id (client_order_id, account_company_id, received_date)
         and packs it into an order object.

        Args:
            client_order_id (string): first part of order id
            account_company_id (string: second part of order id
            received_date (TradingClass.FIXDate): third part of order id
        Returns:
            order quantity (TradingClass.Order): the order object
        """
        command=("select ClientOrderID, Account_CompanyID, ReceivedDate, HandlingInstruction, Stock_Ticker, Side,"
                 " MaturityDate,OrderType,OrderQuantity,Price,LastStatus from `Order` "
                 "where ClientOrderID='%s' and Account_CompanyID="
                    "'%s' and ReceivedDate='%s'" %(client_order_id,account_company_id,received_date))
        order_rows = self.execute_select_sql_command(command)
        first_row = order_rows[0] if len(order_rows) == 1 else None
        order_fetched = Order(client_order_id=first_row[0], account_company_id=first_row[1],
                              received_date=TradingClass.FIXDate(first_row[2]), handling_instruction=first_row[3],
                              stock_ticker=first_row[4], side=first_row[5],
                              maturity_date=TradingClass.FIXDate(first_row[6]), order_type=first_row[7],
                              order_quantity=first_row[8], price=first_row[9], last_status=first_row[10])
        return order_fetched

    def fetch_latest_order_by_client_information(self, client_order_id, account_company_id):
        """Fetches the order data of the latest order with the client information (client_order_id, account_company_id)
         and packs it into an order object.

        Args:
            client_order_id (string): first part of client_information
            account_company_id (string: second part of client_information
        Returns:
            order quantity (TradingClass.Order): the order object
        """
        sql_command = ("select ClientOrderID,Account_CompanyID, ReceivedDate, HandlingInstruction, Stock_Ticker,"
                       "Side, MaturityDate, OrderType, OrderQuantity, Price, LastStatus, MsgSeqNum, OnBehalfOfCompanyID, SenderSubID,"
                       "CashOrderQuantity from `Order` where ClientOrderID='%s' and Account_CompanyID='%s' "
                       "ORDER BY ReceivedDate DESC LIMIT 1") % (client_order_id, account_company_id)
        order_arguments_rows = self.execute_select_sql_command(sql_command)
        if len(order_arguments_rows) < 1: return None
        order_argument_row = list(order_arguments_rows[0])
        order = Order(*order_argument_row)
        return order

    def insert_order(self, order):
        """Inserts a TradingClass.Order into the database

        Args:
            order (TradingClass.Order): The order to be inserted
        Returns:
            None
        """
        command = (
            "INSERT INTO `Order`(ClientOrderID, Account_CompanyID, ReceivedDate, HandlingInstruction, Stock_Ticker,"
            "Side, MaturityDate, OrderType, OrderQuantity, Price, LastStatus, MsgSeqNum) VALUES('%s','%s','%s','%s','%s','%s',"
            "'%s','%s','%s','%s','%s', '%s')"
            % (order.client_order_id, order.account_company_id, order.received_date.mysql_date_stamp_string,
               order.handling_instruction, order.stock_ticker, str(order.side),
               str(order.maturity_date), order.order_type, str(order.order_quantity),
               str(order.price), str(order.last_status), str(order.msg_seq_num)))
        self.execute_nonresponsive_sql_command(command)
        return



    def insert_order_cancel(self, requested_order_cancel):
        """Inserts a TradingClass.OrderCancel into the database

        Args:
            requested_order_cancel (TradingClass.OrderCancel): The order cancel to be inserted
        Returns:
            None
        """
        last_status=0
        executed_time = FIXDateTimeUTC.create_for_current_time()
        sql_command = ("INSERT INTO OrderCancel(Order_ClientOrderID, OrderCancelID, Order_Account_CompanyID, " \
                      "Order_ReceivedDate, LastStatus, ReceivedTime, MsgSeqNum, CancelQuantity, ExecutionTime) " \
                      "VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(requested_order_cancel.client_order_id,
            requested_order_cancel.order_cancel_id,requested_order_cancel.account_company_id,
            requested_order_cancel.order_received_date, last_status, requested_order_cancel.received_time.date_time,
            requested_order_cancel.msg_seq_num,requested_order_cancel.cancel_quantity, executed_time.date_time))
        self.execute_nonresponsive_sql_command(sql_command)

    def update_order_status(self, order, order_status):
        """Update TradingClass.Order status into database

        Args:
            order (TradingClass.Order): The order to be updated in status
            order_status (TradingClass.DatabaseHandlerUtils.LastStatus) : status of order to be updated
        Returns:
            None
        """
        sql_command = ("UPDATE `Order` SET LastStatus ='%s' where ClientOrderID='%s' AND Account_CompanyID='%s' "
                       "AND ReceivedDate ='%s'"
                       % (order_status, order.client_order_id, order.account_company_id, order.received_date))
        self.execute_nonresponsive_sql_command(sql_command)

    def fetch_pending_order_with_cumulative_quantity_by_stock_ticker(self, symbol):
        """Fetches all orders from the database with status pending and returns them in a list of orders

        Args:
            symbol (string): The ticker symbol for which orders are fetched

        Returns:
            pending_orders (list of TradingClass.Order): pending orders
        """
        sql_command = ("select ClientOrderID, Account_CompanyID, ReceivedDate, HandlingInstruction, Stock_Ticker,"
                       "Side, MaturityDate, OrderType, OrderQuantity, Price, LastStatus, MsgSeqNum, OnBehalfOfCompanyID,"
                       " SenderSubID, CashOrderQuantity, CumulativeQuantity from "
                       "`OrderWithCumulativeQuantityAndAveragePrice` where LastStatus=1 and Stock_Ticker='%s'") % (
                          symbol)

        pending_orders_arguments_as_list = self.execute_select_sql_command(sql_command)  # list of tuples
        pending_orders = []
        for pending_order_arguments in pending_orders_arguments_as_list:
            pending_order_arguments_as_list = list(pending_order_arguments)  # ClientOrderID
            #pending_order_arguments_as_list[0] = pending_order_arguments_as_list[0]  # ClientOrderID
            #pending_order_arguments_as_list[1] = pending_order_arguments_as_list[1]  # Account_CompanyID
            pending_order_arguments_as_list[2] = TradingClass.FIXDate(pending_order_arguments_as_list[2])  # ReceivedDate
            #pending_order_arguments_as_list[3] = pending_order_arguments_as_list[3]  # HandlingInstruction
            #pending_order_arguments_as_list[4] = pending_order_arguments_as_list[4]  # Stock_Ticker
            # pending_order_arguments_as_list[5] = pending_order_arguments_as_list[5]  # Side
            pending_order_arguments_as_list[6] = TradingClass.FIXDate(pending_order_arguments_as_list[6])  # MaturityDate
            #pending_order_arguments_as_list[7] = int(pending_order_arguments_as_list[7])  # OrderType
            #pending_order_arguments_as_list[8] = float(pending_order_arguments_as_list[8])  # OrderQuantity
            #pending_order_arguments_as_list[9] = float(pending_order_arguments_as_list[9])  # Price
            #pending_order_arguments_as_list[10] = int(pending_order_arguments_as_list[10])  # LastStatus
            #pending_order_arguments_as_list[11] = pending_order_arguments_as_list[11]  # MsgSeqNum
            #pending_order_arguments_as_list[12] = pending_order_arguments_as_list[12]  # OnBehalfOfCompanyID
            #pending_order_arguments_as_list[13] = pending_order_arguments_as_list[13]  # SenderSubID
            #pending_order_arguments_as_list[14] = pending_order_arguments_as_list[14]  # CashOrderQuantity
            pending_order_arguments_as_list[15] = float(pending_order_arguments_as_list[15])  # OrderWithCumulativeQuantityAndAveragePrice
            order = Order(*pending_order_arguments_as_list)
            pending_orders.append(order)
        return pending_orders

    def delete_all_stock_data(self):
        command = "delete from Stock"
        self.execute_nonresponsive_sql_command(command)

    def delete_stock_data(self, stock):
        command = ("delete from Stock where Ticker = '%s' limit 1" % stock.ticker)
        self.execute_nonresponsive_sql_command(command)

    def insert_stock_data(self, stock):
        command = (
            "insert into Stock(Ticker, CompanyName, LotSize, TickSize, TotalVolume) values( '%s', '%s', '%s', '%s')" % (
                stock.ticker, stock.company_name, stock.lot_size, stock.tick_size, stock.total_volume))
        self.execute_nonresponsive_sql_command(command)

    def fetch_stock_information(self, stock_ticker_symbol):
        """Retrieves stock information from database

        Args:
            stock_ticker_symbol (string): The stock's ticker symbol

        Returns:
             TradingClass.DatabaseStockInformation object"""
        sql_command = (
            "SELECT CurrentPrice.CurrentPrice, PendingOrderCurrentQuantity.CurrentQuantity "
            "FROM PendingOrderCurrentQuantity INNER JOIN CurrentPrice "
            "ON PendingOrderCurrentQuantity.Ticker = CurrentPrice.Stock_Ticker")
        order_arguments_rows = self.execute_select_sql_command(sql_command)
        order_arguments_row_list = list(order_arguments_rows[0])
        order_arguments_row_list[0] = int(order_arguments_row_list[0])
        order_arguments_row_list[1] = int(order_arguments_row_list[1])
        database_stock_information = TradingClass.DatabaseStockInformation(*order_arguments_row_list)
        return database_stock_information

    def fetch_stock_total_volume(self, stock_ticker_symbol):
        """Retrieves stock total volume from database

        Args:
            stock_ticker_symbol (string): The stock's ticker symbol

        Returns:
             Stock Total Volume (float)"""
        sql_command = ("SELECT TotalVolume FROM Stock where Ticker='%s'" % stock_ticker_symbol)
        stock_arguments_rows = self.execute_select_sql_command(sql_command)
        stock_total_volume = stock_arguments_rows[0][0]

        return stock_total_volume

    def fetch_orders_of_type(self, order):
        """Returns all orders for the same stock as the given order


        Args:
            order (string): The user id
            password (string): The password

        Returns:
            success (ServerRespond): success of authentication
        """
        pass


class MarketSimulationHandler:
    def __init__(self):
        self.stock_list_file_name = "stock_list.cfg"
        self.stock_list = read_file_values(self.stock_list_file_name)

    def init_market(self):
        pass
        # ServerDatabaseHandler().load_sql_file("./database/account_insert.sql")
        # ServerDatabaseHandler().load_sql_file("./database/stock_insert.sql")
        # ServerDatabaseHandler().load_sql_file("./database/order_insert.sql")
        # ServerDatabaseHandler().load_sql_file("./database/order_execution_insert.sql")

        # self.load_market_data_into_database()

    def load_market_data_into_database(self):
        """Loads market data for initialization

		Used for server initialization to fetch data from a finance server

		Returns:
		    None
		"""
        for stock in self.stock_list:
            share = yahoo_finance.Share(stock)
            new_stock = Stock(share.data_set["symbol"], share.data_set["Name"], share.data_set["LastTradePriceOnly"],
                              share.data_set["Volume"])
            ServerDatabaseHandler().insert_stock_data(new_stock)


class Stock:
    def __init__(self, ticker, company_name=None, lot_size=None, tick_size=None, total_volume=None):
        self.ticker = ticker
        self.company_name = company_name
        self.lot_size = lot_size
        self.tick_size = tick_size
        self.total_volume = total_volume

    def get_ticker(self):
        return self.ticker

    def get_company_name(self):
        return self.company_name

    def get_lot_size(self):
        return self.lot_size

    def get_tick_size(self):
        return self.tick_size

    def get_total_volume(self):
        return self.total_volume


def read_file(file_name):
    """Produces a string without \n

    Args:
        file_name (string): name of the file

    Returns:
        list (string): A list of stock names
    """
    with open(file_name, 'r') as file:
        content = file.read()
    return content


def read_file_values(file_name):
    """Produces a list out of a file, each line represents one value

    Args:
        file_name (string): name of the file

    Returns:
        list (string): A list of stock names
    """
    with open(file_name, 'r') as file:
        list = file.read().splitlines()
    return list
