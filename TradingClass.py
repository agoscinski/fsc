import MySQLdb
import numpy as np
import re
import datetime
import quickfix as fix
import quickfix42 as fix42
import abc

##################
## Time classes ##
##################

class FIXYearMonth(object):
    def __init__(self, date_object):
        self.date = date_object

    @classmethod
    def from_year_month(cls, year, month):
        """Constructor of YearMonthFix
        Args:
            year (int)
            month (int)
        """
        date_object = datetime.date(year, month, 1)
        return cls(date_object)

    @classmethod
    def from_date_stamp_string(cls, date_stamp_string):
        """Constructor from date stamp strings

        Args:
            date_stamp_string (string): string in format YYYYMM
        Returns:
            (FIXYearMonth object)
        """
        date_object = datetime.datetime.strptime(date_stamp_string, "%Y%m").date()
        return cls(date_object)

    @property
    def year(self):
        return self.date.year

    @year.setter
    def year(self, year):
        self.date.year = year

    @property
    def month(self):
        return self.date.month

    @month.setter
    def month(self, month):
        self.date.month = month

    def __str__(self):
        return self.date.strftime("%Y%m")


class FIXDate(object):
    """The FixDate object encapsulates a date object

    Attributes:
        date (datetime.date): the date
    """

    def __init__(self, date_object):
        self.date = date_object

    @classmethod
    def from_fix_date_stamp_string(cls, date_stamp_string):
        """Constructor for mysql date stamp strings

        Args:
            date_stamp_string (string): string in format YYYYMMDD
        Returns:
            (FIXDate object)
        """
        date_object = datetime.datetime.strptime(date_stamp_string, "%Y%m%d").date()
        return cls(date_object)

    @classmethod
    def from_mysql_date_stamp_string(cls, date_stamp_string):
        """Constructor for mysql date stamp strings

        Args:
            date_stamp_string (string): string in format YYYY-MM-DD
        Returns:
            (FIXDate object)
        """
        date_object = datetime.datetime.strptime(date_stamp_string, "%Y-%m-%d").date()
        return cls(date_object)

    @classmethod
    def from_year_month_day(cls, year, month, day):
        """Constructor from date stamp strings

        Args:
            year (int): an integer representing the year
            month (int): an integer representing the month
            day (int): an integer representing the day
        Returns:
            (FIXDate object)
        """
        date_object = datetime.date(year, month, day)
        return cls(date_object)

    def __eq__(self, other):
        return self.date.year == other.date.year and self.date.month == other.date.month and self.date.day == other.date.day

    def __ne__(self, other):
        return not __eq__(self, other)

    def __str__(self):
        return self.date.strftime("%Y%m%d")

    @property
    def mysql_date_stamp_string(self):
        return self.date.strftime("%Y-%m-%d")

    @mysql_date_stamp_string.setter
    def year(self, date_stamp_string):
        self.date = datetime.datetime.strptime(date_stamp_string, "%Y-%m-%d").date()

    @property
    def year(self):
        return self.date.year

    @year.setter
    def year(self, year):
        self.date.year = year

    @property
    def month(self):
        return self.date.month

    @month.setter
    def month(self, month):
        self.date.month = month

    @property
    def day(self):
        return self.date.day

    @day.setter
    def day(self, day):
        self.date.day = day

    # TODO remove
    def set_date_from_year_month_day(self, year, month, date):
        self.date = datetime.date(year, month, date)

    def set_date_from_date_stamp_string(self, string):
        self.date = datetime.datetime.strptime(string, "%Y-%m-%d").date()

    def set_date_today(self):
        self.date = datetime.date.today()


class FIXTime(object):
    """Constructor of FIXTime
        @Parameter:
            hour : hour in int
            minute : minutes in int
            second : second in int
    """

    def __init__(self, hour, minute, second):
        self.time = datetime.time(hour, minute, second, 0)

    # TODO remove
    def get_time(self):
        return self.time

    def __str__(self):
        return self.time.strftime("%H:%M:%S")

    # TODO remove
    def set_time(self, hour, minute, second):
        self.time = datetime.time(hour, minute, second, 0)

    def set_time_string(self, string):
        self.time = datetime.datetime.strptime(string, "%H:%M:%S").time()

    def set_time_value(self, time):
        self.time = time


class FIXDateTimeUTC(object):
    def __init__(self, datetime_object):
        """Constructor of FIXDateTimeUTC from
        Args:
            datetime_object (datetime.datetime object)
        """
        self.date_time = datetime_object

    @classmethod
    def from_year_month_date_hour_minute_second(cls, year, month, date, hour, minute, second):
        """Constructor of FIXDateTimeUTC
        Args
            year (int): year
            month (int): month
            date (int): date
            hour (int): hour
            minute (int): minutes
            second (int): second
        """
        datetime_object = datetime.datetime(year, month, date, hour, minute, second, 0)
        return cls(datetime_object)

    @classmethod
    def create_for_current_time(cls):
        current_time_datetime_object = datetime.datetime.utcnow()
        return cls(current_time_datetime_object)

    @classmethod
    def from_date_fix_time_stamp_string(cls, date_time_stamp_string):
        """Constructor from date stamp strings
    @staticmethod
    def parse_file_names_from_init_script(init_script_file_path):
        file_names = []
        pattern_for_line_with_file = re.compile("(?<=source ).+")
        for line in open(init_script_file_path):
            for match in re.finditer(pattern_for_line_with_file, line):
                file_name = match.group(0)
                file_names.append(file_name)
        return file_names

        Args:
            date_time_stamp_string (string): string in format YYYYMMDD-HH:MM:SS
        Returns:
            (FIXDate object)
        """
        date_object = datetime.datetime.strptime(date_time_stamp_string, "%Y%m%d-%H:%M:%S").date()
        return cls(date_object)

    def __str__(self):
        return self.date_time.strftime("%Y%m%d-%H:%M:%S")

    @property
    def mysql_date_stamp_string(self):
        return self.date_time.strftime("%Y-%m-%d %H:%M:%S")

    @mysql_date_stamp_string.setter
    def year(self, date_stamp_string):
        self.date = datetime.datetime.strptime(date_stamp_string, "%Y-%m-%d %H:%M:%S").date()

    # TODO clean
    def get_date_time(self):
        return self.date_time

    def set_date_time(self, year, month, date, hour, minute, second):
        self.date_time = datetime.datetime(year, month, date, hour, minute, second, 0)

    def set_date_time_string(self, string):
        self.date_time = datetime.datetime.strptime(string, "%Y%m%d-%H:%M:%S").date()

    def set_date_time_default_string(self, string):
        self.date_time = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S").date()

    def set_date_time_value(self, date_time):
        self.date_time = date_time


###################################
## Server/Client related classes ##
###################################

class ServerFIXHandlerScheme(abc.ABCMeta):

    @abc.abstractmethod
    def handle_order_cancel_request(self, message):
        pass

    @abc.abstractmethod
    def handle_order_request(self, message):
        pass

class DummyServerFIXHandler(ServerFIXHandlerScheme):
    def handle_order_cancel_request(self, message):
        pass

    def handle_order_request(self, message):
        pass

class FIXHandlerUtils:

    class MarketDataEntryType:
        OFFER = 0
        BID = 1
        CURRENT_PRICE = 2
        OPENING_PRICE = 4
        CLOSING_PRICE = 5
        DAY_HIGH = 7
        DAY_LOW = 8

    class Side:
        BUY = fix.Side_BUY
        SELL = fix.Side_SELL

    class OrderType:
        MARKET = fix.TriggerOrderType_MARKET
        LIMIT = fix.TriggerOrderType_LIMIT

    class OrderStatus:
        NEW = '0'
        PARTIALLY_FILLED = '1'
        FILLED = '2'
        CANCELED = '4'
        REPLACED = '5'
        PENDING_CANCEL = '6'
        REJECTED = '8'
        EXPIRED = 'C'
        PENDING_REPLACE = 'E'

    class ExecutionType:
        NEW = '0'
        PARTIAL_FILL = '1'
        FILL = '2'
        CANCELED = '4'
        REJECTED = '8'

    class ExecutionTransactionType:
        NEW = '0'
        CANCEL = '1'
        CORRECT = '2'
        STATUS = '3'
        """
        NEW = '0'
        PARTIAL_FILL = '1'
        FILL = '2'
        CANCELED = '4'
        REPLACE = '5'
        REJECTED = '8'
        EXPIRED = 'C'
        """
    class HandlingInstruction:
        AUTOMATED_EXECUTION_ORDER_PRIVATE_NO_BROKER_INTERVENTION = fix.HandlInst_AUTOMATED_EXECUTION_ORDER_PRIVATE_NO_BROKER_INTERVENTION

    @staticmethod
    def get_field_value(fix_object, message):
        if message.isSetField(fix_object.getField()):
            message.getField(fix_object)
            return fix_object.getValue()
        else:
            return None

    @staticmethod
    def get_field_string(fix_object, message):
        if message.isSetField(fix_object.getField()):
            message.getField(fix_object)
            return fix_object.getString()
        else:
            return None

    @staticmethod
    def get_header_field_value(fix_object, message):
        if message.getHeader().isSetField(fix_object.getField()):
            message.getHeader().getField(fix_object)
            return fix_object.getValue()
        else:
            return None

    @staticmethod
    def get_header_field_string(fix_object, message):
        if message.getHeader().isSetField(fix_object.getField()):
            message.getHeader().getField(fix_object)
            return fix_object.getString()
        else:
            return None

class DatabaseHandlerUtils:
    # Enums
    class OrderType:
        MARKET = 1
        LIMIT = 2

    class Side:
        BUY = 1
        SELL = 2

    class LastStatus:
        DONE = 0
        PENDING = 1
        CANCELED = 2
        EXPIRED = 3

    class HandlingInstruction:
        AUTOMATED_EXECUTION_ORDER_PRIVATE_NO_BROKER_INTERVENTION = 1

    @staticmethod
    def parse_file_names_from_init_script(init_script_file_path):
        file_names = []
        pattern_for_line_with_file = re.compile("(?<=source ).+")
        for line in open(init_script_file_path):
            for match in re.finditer(pattern_for_line_with_file, line):
                file_name = match.group(0)
                file_names.append(file_name)
        return file_names

    @staticmethod
    def parse_sql_commands_from_sql_file(sql_file_file_path):
        """Parses a sql file and extracts the sql commands of it
        Args:
            sql_file_file_path (string): the file path of the sql file

        Returns:
            sql_commands (list of string): each element is one sql command to be executed
        """
        with open(sql_file_file_path) as sql_file:
            sql_file_content = sql_file.read().replace("\n", " ").split(";")

        sql_commands = []
        pattern_for_sql_command = re.compile("(CREATE|INSERT|SET ..|UPDATE|DELETE).+")
        for block in sql_file_content:
            match = re.search(pattern_for_sql_command, block)
            if match is not None:
                sql_command = match.group(0)
                sql_commands.append(sql_command)
        return sql_commands


class DatabaseHandler:

    def __init__(self, user_name="root", user_password="root", database_name="FSCDatabase", database_port=3306,
                 init_database_script_path="./database/init_fsc_database.sql"):
        """
        Args:
            user_name (string)
            user_password (string)
            database_name (string)
            database_port (int)
            init_database_script_path (string)
        """
        self.user_name = user_name
        self.user_password = user_password
        self.database_name = database_name
        self.database_port = database_port
        self.init_database_script_path = init_database_script_path

    def init_database(self):
        """This function initializes a new database, by first dropping the database with self.database_name and the creating
         a new one with the same name. It then load all sql files saved in the init script file located in self.init_database_script_path,
         see database documentation for file format of the init script
        """
        self.drop_schema()
        self.create_schema()
        self.load_init_script()
        return

    def teardown_database(self):
        self.drop_schema()

    def create_schema(self):
        sql_command = "CREATE SCHEMA IF NOT EXISTS `" + self.database_name + "` DEFAULT CHARACTER SET utf8 ;"
        try:
            connection = MySQLdb.connect(host='localhost', user=self.user_name, passwd=self.user_password)
            cursor = connection.cursor()
            cursor.execute(sql_command)
            connection.commit()
            connection.close()
            return
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        return

    def drop_schema(self):
        """This function drops the database with self.database_name"""
        sql_command = "DROP SCHEMA IF EXISTS `" + self.database_name + "` ;"
        self.execute_nonresponsive_sql_command(sql_command)

    def load_init_script(self):
        file_names = DatabaseHandlerUtils.parse_file_names_from_init_script(self.init_database_script_path)
        for file_name in file_names:
            self.load_sql_file(file_name)
        return

    def load_sql_file(self, file_path):
        sql_commands = DatabaseHandlerUtils.parse_sql_commands_from_sql_file(file_path)
        for sql_command in sql_commands:
            self.execute_nonresponsive_sql_command(sql_command)

    def execute_select_sql_command(self, sql_command):
        """Used to execute SELECT commands which return a table
        Args:
            sql_command (string): the sql command to be executed
        Returns:
            fetched_database_rows (list of tuples): the each entry is a row of the select statement #TODO do not know if this is correct
        """
        fetched_database_rows = []
        try:
            connection = MySQLdb.connect(host='localhost', user=self.user_name, passwd=self.user_password,
                                         db=self.database_name, port=self.database_port)
            cursor = connection.cursor()
            execution = (sql_command)
            cursor.execute(execution)
            fetched_database_rows = cursor.fetchall()
            connection.close()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

        return fetched_database_rows

    def execute_nonresponsive_sql_command(self, sql_command):
        """Used to execute commands CREATE, UPDATE, DELETE which returns nothing
        Args:
            sql_command (string): the sql command to be executed
        Returns:
            None
        """
        try:
            connection = MySQLdb.connect(host='localhost', user=self.user_name, passwd=self.user_password,
                                         db=self.database_name, port=self.database_port)
            cursor = connection.cursor()
            cursor.execute(sql_command)
            connection.commit()
            connection.close()
            return
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def execute_responsive_insert_sql_command(self, insert_sql_command):
        """Used to execute commands INSERT which returns the produced ID from database server
        Args:
            insert_sql_command (string): the sql command to be executed
        Returns:
            id_of_inserted_row (ID type in database): the ID of the object inserted
        """
        try:
            connection = MySQLdb.connect(host='localhost', user=self.user_name, passwd=self.user_password,
                                         db=self.database_name, port=self.database_port)
            cursor = connection.cursor()
            cursor.execute(insert_sql_command)
            connection.commit()
            id_of_inserted_row = cursor.lastrowid
            connection.close()
            return id_of_inserted_row
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])


class DatabaseHandlerUtils:
    # Enums
    class OrderType:
        MARKET = 1
        LIMIT = 2

    class Side:
        BUY = 1
        SELL = 2

    class LastStatus:
        DONE = 0
        PENDING = 1
        CANCELED = 2
        EXPIRED = 3

    class HandlingInstruction:
        AUTOMATED_EXECUTION_ORDER_PRIVATE_NO_BROKER_INTERVENTION = 1

    @staticmethod
    def parse_file_names_from_init_script(init_script_file_path):
        file_names = []
        pattern_for_line_with_file = re.compile("(?<=source ).+")
        for line in open(init_script_file_path):
            for match in re.finditer(pattern_for_line_with_file, line):
                file_name = match.group(0)
                file_names.append(file_name)
        return file_names

    @staticmethod
    def parse_sql_commands_from_sql_file(sql_file_file_path):
        """Parses a sql file and extracts the sql commands of it
        Args:
            sql_file_file_path (string): the file path of the sql file

        Returns:
            sql_commands (list of string): each element is one sql command to be executed
        """
        with open(sql_file_file_path) as sql_file:
            sql_file_content = sql_file.read().replace("\n", " ").split(";")

        sql_commands = []
        pattern_for_sql_command = re.compile("(CREATE|INSERT|SET ..|UPDATE|DELETE).+")
        for block in sql_file_content:
            match = re.search(pattern_for_sql_command, block)
            if match is not None:
                sql_command = match.group(0)
                sql_commands.append(sql_command)
        return sql_commands


class ClientLogicUtils:

    @staticmethod
    def extract_offers_price_quantity(market_data_entry_types, market_data_entry_prices,
                                      market_data_entry_quantity):
        prices = market_data_entry_prices[market_data_entry_types == FIXHandlerUtils.OrderEntryType.OFFER]
        quantity = market_data_entry_quantity[market_data_entry_types == FIXHandlerUtils.OrderEntryType.OFFER]
        return prices, quantity

    @staticmethod
    def extract_bid_price_quantity(market_data_entry_types, market_data_entry_prices,
                                   market_data_entry_quantity):
        prices = market_data_entry_prices[market_data_entry_types == FIXHandlerUtils.MarketDataEntryType.BID]
        quantity = market_data_entry_quantity[market_data_entry_types == FIXHandlerUtils.MarketDataEntryType.BID]
        return prices, quantity

    @staticmethod
    def extract_current_price(market_data_entry_types, market_data_entry_prices):
        current_price = ClientLogicUtils.get_value_for_id(
            market_data_entry_prices, market_data_entry_types, FIXHandlerUtils.MarketDataEntryType.CURRENT_PRICE)
        return current_price

    @staticmethod
    def extract_opening_price(market_data_entry_types, market_data_entry_prices):
        opening_price = ClientLogicUtils.get_value_for_id(
            market_data_entry_prices, market_data_entry_types, FIXHandlerUtils.MarketDataEntryType.OPENING_PRICE)
        return opening_price

    @staticmethod
    def extract_closing_price(market_data_entry_types, market_data_entry_prices):
        closing_price = ClientLogicUtils.get_value_for_id(
            market_data_entry_prices, market_data_entry_types, FIXHandlerUtils.MarketDataEntryType.CLOSING_PRICE)
        return closing_price

    @staticmethod
    def extract_day_high(market_data_entry_types, market_data_entry_prices):
        session_high = ClientLogicUtils.get_value_for_id(
            market_data_entry_prices, market_data_entry_types, FIXHandlerUtils.MarketDataEntryType.DAY_HIGH)
        return session_high

    @staticmethod
    def extract_day_low(market_data_entry_types, market_data_entry_prices):
        session_low = ClientLogicUtils.get_value_for_id(
            market_data_entry_prices, market_data_entry_types, FIXHandlerUtils.MarketDataEntryType.DAY_LOW)
        return session_low

    @staticmethod
    def extract_market_data_information(market_data):
        market_data_entry_types = np.array(market_data.get_md_entry_type_list())
        market_data_entry_prices = np.array(market_data.get_md_entry_px_list())
        market_data_entry_quantity = np.array(market_data.get_md_entry_size_list())

        offers_price, offers_quantity = ClientLogicUtils.extract_offers_price_quantity(market_data_entry_types,
                                                                                       market_data_entry_prices,
                                                                                       market_data_entry_quantity)
        bids_price, bids_quantity = ClientLogicUtils.extract_bid_price_quantity(market_data_entry_types,
                                                                                market_data_entry_prices,
                                                                                market_data_entry_quantity)
        current_price = ClientLogicUtils.extract_current_price(market_data_entry_types, market_data_entry_prices)
        current_quantity = market_data.get_md_total_volume_traded()
        opening_price = ClientLogicUtils.extract_opening_price(market_data_entry_types)
        closing_price = ClientLogicUtils.extract_closing_price(market_data_entry_types)
        day_high = ClientLogicUtils.extract_day_high(market_data_entry_types)
        day_low = ClientLogicUtils.extract_low_low(market_data_entry_types)

        offers_price, offers_quantity, bids_price, bids_quantity, current_price, current_quantity, opening_price, \
        closing_price, day_high, day_low = \
            ClientLogicUtils.transform_numpy_array_to_list(offers_price, offers_quantity, bids_price, bids_quantity,
                                                           current_price,
                                                           current_quantity, opening_price, closing_price, day_high,
                                                           day_low)
        return offers_price, offers_quantity, bids_price, bids_quantity, current_price, current_quantity, opening_price, \
               closing_price, day_high, day_low

    @staticmethod
    def extract_five_smallest_offers(offers_price, offers_quantity):
        five_smallest_offers_indices = ClientLogicUtils.extract_n_smallest_indices(offers_price, 5)
        five_smallest_offers_price, five_smallest_offers_quantity = \
            ClientLogicUtils.get_values_from_lists_for_certain_indices(five_smallest_offers_indices, offers_price,
                                                                       offers_quantity)
        return five_smallest_offers_price, five_smallest_offers_quantity

    @staticmethod
    def extract_five_biggest_bids(bids_price, bids_quantity):
        five_biggest_bids_indices = ClientLogicUtils.extract_n_biggest_indices(bids_price)
        five_biggest_bids_price, five_biggest_bids_quantity = ClientLogicUtils.get_values_from_lists_for_certain_indices(
            five_biggest_bids_indices, bids_price, bids_quantity)
        return five_biggest_bids_price, five_biggest_bids_quantity

    @staticmethod
    def get_index_of_first_occurring_value(numpy_array, value):
        indices_of_occurrences = numpy_array[numpy_array == value]
        index = indices_of_occurrences[0] if len(indices_of_occurrences) > 0 else None
        return index

    @staticmethod
    def get_value_for_id(values, ids, id):
        """Gets the value of the entry in the numpy array values with the index of the id in the numpy array ids
        Args:
            values (numpy.array of float64): collection of values
            ids (numpy.array of int64): collection of different ids
            id (int): the id for which the index is determined in ids
        """
        index_of_first_occurring_value = ClientLogicUtils.get_index_of_first_occurring_value(ids, id)
        value = None if index_of_first_occurring_value is None else values[index_of_first_occurring_value]
        return value

    @staticmethod
    def extract_n_smallest_indices(integer_list, n, order="ascending"):
        n_smallest_indices = np.argsort(integer_list)[:n]
        if order == "descending":
            n_smallest_indices = n_smallest_indices[::-1]

        return n_smallest_indices

    @staticmethod
    def extract_n_biggest_indices(integer_list, n, order="ascending"):
        n_biggest_indices = np.argsort(integer_list)[-n:]
        if order == "descending":
            n_biggest_indices = n_biggest_indices[::-1]
        return n_biggest_indices

    @staticmethod
    def get_values_from_lists_for_certain_indices(certain_indices, *lists):
        values_of_lists = []
        for list_ in lists:
            values_of_lists.append(list(np.array(list_)[certain_indices]))
        return values_of_lists

    @staticmethod
    def transform_numpy_array_to_list(*numpy_arrays):
        lists = []
        for numpy_array in numpy_arrays:
            lists.append(list(numpy_array))
        return lists

    @staticmethod
    def get_value_for_id(values, ids, id):
        """Gets the value of the entry in the numpy array values with the index of the id in the numpy array ids
        Args:
            values (numpy.array of float64): collection of values
            ids (numpy.array of int64): collection of different ids
            id (int): the id for which the index is determined in ids
        """
        index_of_first_occurring_value = ClientLogicUtils.get_index_of_first_occurring_value(ids, id)
        value = None if index_of_first_occurring_value is None else values[index_of_first_occurring_value]
        return value

#################################
## FIX message related classes ##
#################################

class MarketDataRequest(object):
    """Constructor of class MarketDataRequest:
    Args:
        md_req_id (string): market data request ID
        subscription_request_type : Type of subscription of market data request (char)
        market_depth : market depth of market data request (int)
        no_md_entry_types (int) : number of market data entry requested
        md_entry_type_list (list of int): market data entries
        no_related_sym : number of symbols requested (int)
        symbol_list : list of ticker symbol (list of string)
    """

    def __init__(self, md_req_id, subscription_request_type, market_depth, no_md_entry_types, md_entry_type_list,
                 no_related_sym, symbol_list):
        self.md_req_id = md_req_id
        self.subscription_request_type = subscription_request_type
        self.market_depth = market_depth
        self.no_md_entry_types = no_md_entry_types
        self.md_entry_type_list = md_entry_type_list
        self.no_related_sym = no_related_sym
        self.symbol_list = symbol_list

    @classmethod
    def from_fix_message(cls, fix_message):
        """Constructor from a quickfix.Message"""
        message_fields = [fix.MDReqID(), fix.SubscriptionRequestType(), fix.MarketDepth(), fix.NoMDEntryTypes(),
                          fix.NoRelatedSym()]
        market_data_required_id, subscription_request_type, market_depth, no_market_data_entry_types, no_related_symbols = get_values_from_fix_message_fields(
            fix_message, message_fields)

        market_data_entry_types = get_fix_group_field(fix_message, fix42.MarketDataRequest().NoMDEntryTypes(),
                                                      fix.MDEntryType(), no_market_data_entry_types,
                                                      transform_group_element=int)
        related_symbols = get_fix_group_field(fix_message, fix42.MarketDataRequest().NoRelatedSym(), fix.Symbol(),
                                              no_related_symbols)

        market_data_request = cls(market_data_required_id, subscription_request_type, market_depth,
                                  no_market_data_entry_types, market_data_entry_types, no_related_symbols,
                                  related_symbols)
        return market_data_request


# TODO Move this functions to FIXHandler
def get_values_from_fix_message_fields(fix_message, message_field_types):
    """Gets the values of the message fields in the message
    Args:
        fix_message (quickfix.Message)
        message_field_types (list of quickfix field types)
    Returns:
        values (list of different types)"""
    values = []
    for i in range(len(message_field_types)):
        fix_field = message_field_types[i]
        fix_message.getField(fix_field)
        values[i] = fix_field.getValue()
    return values


def get_fix_group_field(fix_message, fix_group, fix_field_type, no_group_elements,
                        transform_group_element=None):
    """
    Args:
        fix_message (quickfix.Message):
        fix_group (FIX::Group *)
        fix_field_type (quickfix field type)
        no_group_elements (int)
        transform_group_element (function): This function is applied on each group entry after the value is
            retrieved
    Returns:
        group_elements (list of different types): list of group elements
    """
    group_elements = []
    for i in range(no_group_elements):
        fix_message.getGroup(i + 1, fix_group)
        fix_group.getField(fix_field_type)
        group_element = fix_field_type.getValue() if transform_group_element is None else transform_group_element(
            fix_field_type.getValue())
        group_elements.append(group_element)
    return group_elements


class MarketDataResponse(object):
    """Constructor of class MarketDataResponse:
        @Parameter:
            md_req_id : market data response ID related to market data request ID (string)
            no_md_entry_types = no_md_entry_types (int)
            symbol = symbol (string)
            md_entry_type_list = md entry type list (list of int)
            md_entry_px_list = md entry price list (list of float)
            md_entry_size_list = md entry size list (list of float)
            md_entry_date_list = md entry date list (list of DateFix Object=> datetime UTC Date YYYYMMDD)
            md_entry_time_list = md entry time list (list of TimeFix Object=> datetime UTC Time HH:MM:SS)
    """

    def __init__(self, md_req_id, no_md_entry_types, symbol, md_entry_type_list, md_entry_px_list,
                 md_entry_size_list, md_entry_date_list, md_entry_time_list, md_total_volume_traded=None):
        self.md_req_id = md_req_id
        self.no_md_entry_types = no_md_entry_types
        self.symbol = symbol
        self.md_entry_type_list = md_entry_type_list
        self.md_entry_px_list = md_entry_px_list
        self.md_entry_size_list = md_entry_size_list
        self.md_entry_date_list = md_entry_date_list
        self.md_entry_time_list = md_entry_time_list
        self.md_total_volume_traded = md_total_volume_traded


class OrderCancelRequest(object):
    """Constructor of class OrderCancelRequest:
        @Parameter:
        orig_cl_ord_id = original client order id to be cancelled (String)
        cl_ord_id = cancellation client order id (String)
        symbol = symbol (String)
        side = side (char)
        transact_time = transaction time (DateTimeFix Object=> DateTime datetime UTC YYYYMMDD-HH:MM:SS)
        order_qty = order quantity (float)
        sender_comp_id = sender company id (String)
        sending_time = Sending Time of the message (DateTimeFix Object=> DateTime datetime UTC YYYYMMDD-HH:MM:SS)
        on_behalf_of_comp_id = company on behalf of sender company id (String)
        sender_sub_id = identifier created by sender_comp_id (String)
    """

    def __init__(self, orig_cl_ord_id, cl_ord_id, symbol, side, transact_time, order_qty, sender_comp_id=None,
                 sending_time=None, on_behalf_of_comp_id=None, sender_sub_id=None):
        self.orig_cl_ord_id = orig_cl_ord_id
        self.cl_ord_id = cl_ord_id
        self.symbol = symbol
        self.side = side
        self.transact_time = transact_time
        self.order_qty = order_qty
        self.sender_comp_id = sender_comp_id
        if sending_time is not None:
            self.sending_time = sending_time
        if sender_comp_id is not None:
            self.sender_comp_id = sender_comp_id
        if on_behalf_of_comp_id is not None:
            self.on_behalf_of_comp_id = on_behalf_of_comp_id
        if sender_sub_id is not None:
            self.sender_sub_id = sender_sub_id

    @classmethod
    def from_fix_message(cls, fix_message):
        """Constructor from a quickfix.Message
        Args:
           fix_message (quickfix.Message)
        Returns:
            OrderCancelRequest
        """
        orig_cl_ord_id = FIXHandlerUtils.get_field_value(fix.OrigClOrdID(), fix_message)
        cl_ord_id = FIXHandlerUtils.get_field_value(fix.ClOrdID(), fix_message)
        symbol = FIXHandlerUtils.get_field_value(fix.Symbol(), fix_message)
        side = FIXHandlerUtils.get_field_value(fix.Side(), fix_message)
        transaction_time = FIXHandlerUtils.get_field_string(fix.TransactTime(), fix_message)
        order_quantity = FIXHandlerUtils.get_field_value(fix.OrderQty(), fix_message)
        sender_company_id = FIXHandlerUtils.get_header_field_value(fix.SenderCompID(), fix_message)
        sending_time = FIXHandlerUtils.get_header_field_string(fix.SendingTime(), fix_message)
        on_behalf_of_comp_id = FIXHandlerUtils.get_header_field_value(fix.OnBehalfOfCompID(), fix_message)
        sender_sub_id = FIXHandlerUtils.get_header_field_value(fix.SenderSubID(), fix_message)

        return cls(orig_cl_ord_id, cl_ord_id, symbol, side, transaction_time, order_quantity, sender_company_id, sending_time,
                   on_behalf_of_comp_id, sender_sub_id)

class OrderCancelReject(object):
    """Constructor of class OrderCancelReject represents a quickfix order cancel reject (message type 9):
    Args:
        orig_cl_ord_id=original client order id to be cancelled (String)
        cl_ord_id= cancellation client order id (String)
        order_id= Execution Order Cancel ID  (String)
        ord_status= status of rejected order cancel =8 (Char)
        cxl_rej_response_to= type of transaction requested=> OrderCancelRequest =1 (Char)
        receiver_comp_id= receiver company ID (String)

    """

    def __init__(self, orig_cl_ord_id, cl_ord_id, order_id, ord_status, cxl_rej_response_to, receiver_comp_id,
                 cxl_rej_reason=None):
        self.orig_cl_ord_id = orig_cl_ord_id
        self.cl_ord_id = cl_ord_id
        self.order_id = order_id
        self.ord_status = ord_status
        self.cxl_rej_response_to = cxl_rej_response_to
        self.receiver_comp_id = receiver_comp_id
        if cxl_rej_reason is not None:
            self.cxl_rej_reason = cxl_rej_reason
        else:
            self.cxl_rej_reason = None

    @classmethod
    def from_fix_message(cls, fix_message):
        """Constructor from a quickfix.Message
        Args:
           fix_message (quickfix.Message)
        Returns:
            OrderCancelReject
        """
        orig_cl_ord_id = FIXHandlerUtils.get_field_value(fix.OrigClOrdID(), fix_message)
        cl_ord_id = FIXHandlerUtils.get_field_value(fix.ClOrdID(), fix_message)
        order_id = FIXHandlerUtils.get_field_value(fix.OrderID(), fix_message)
        ord_status = FIXHandlerUtils.get_field_value(fix.OrdStatus(), fix_message)
        receiver_comp_id = FIXHandlerUtils.get_header_field_value(fix.TargetCompID(), fix_message)
        cxl_rej_reason = FIXHandlerUtils.get_field_value(fix.CxlRejReason(), fix_message)

        return cls(orig_cl_ord_id, cl_ord_id, order_id, ord_status, receiver_comp_id, cxl_rej_reason)

class NewSingleOrder(object):
    """A New single order is designed after the FIX message of type D "Order - Single" and is used to
     encapsulate a message into an object

    Args:
        client_order_id (string)
        handling_instruction (char/FIXHandlerUtils.HandlingInstruction)
        symbol (string)
        side (char/FIXHandlerUtils.Side)
        maturity_month_year (FIXYearMonth)
        maturity_day (int): between 1-31
        transaction_time (FIXDateTimeUTC)
        order_quantity (float)
        order_type (char/FIXHandlerUtils.OrderType)
        price (float)
        stop_price (float)
    """

    def __init__(self, client_order_id, handling_instruction, symbol, maturity_month_year,
                 maturity_day, side, transaction_time, order_quantity, order_type, price, stop_price=None,
                 sender_company_id=None, sending_time=None, on_behalf_of_comp_id=None, sender_sub_id=None):
        self.client_order_id = client_order_id
        self.handling_instruction = handling_instruction
        self.symbol = symbol
        self.maturity_month_year = maturity_month_year
        self.maturity_day = maturity_day
        self.side = side
        self.transaction_time = transaction_time
        self.order_quantity = order_quantity
        self.order_type = order_type
        self.price = price
        self.stop_price = stop_price
        self.sender_company_id = sender_company_id
        self.sending_time = sending_time
        self.on_behalf_of_comp_id = on_behalf_of_comp_id
        self.sender_sub_id = sender_sub_id

    @classmethod
    def create_dummy_new_single_order(cls, client_order_id="client", handling_instruction="1",
                                      symbol="TSLA", maturity_month_year=FIXYearMonth.from_year_month(2000, 1),
                                      maturity_day=2, side=FIXHandlerUtils.Side.BUY,
                                      transaction_time=FIXDateTimeUTC.from_date_fix_time_stamp_string("20000101-10:00:00"),
                                      order_quantity=10., order_type=FIXHandlerUtils.OrderType.LIMIT, price=100.,
                                      stop_price=None, sender_company_id=None, sending_time=None,
                                      on_behalf_of_company_id=None, sender_sub_id=None):
        """For testing"""
        dummy_new_single_order = cls(client_order_id, handling_instruction,
                                     symbol, maturity_month_year, maturity_day, side,
                                     transaction_time, order_quantity, order_type, price,
                                     stop_price, sender_company_id, sending_time,
                                     on_behalf_of_company_id, sender_sub_id)
        return dummy_new_single_order

    @classmethod
    def from_fix_message(cls, fix_message):
        """Constructor from a quickfix.Message
        Args:
           fix_message (quickfix.Message)
        Returns:
            NewSingleOrder
        """
        client_order_id = FIXHandlerUtils.get_field_value(fix.ClOrdID(), fix_message)
        handling_instruction = FIXHandlerUtils.get_field_value(fix.HandlInst(), fix_message)
        execution_instruction = FIXHandlerUtils.get_field_value(fix.ExecInst(), fix_message)
        symbol = FIXHandlerUtils.get_field_value(fix.Symbol(), fix_message)
        maturity_month_year = FIXHandlerUtils.get_field_value(fix.MaturityMonthYear(), fix_message)
        maturity_day = FIXHandlerUtils.get_field_value(fix.MaturityDay(), fix_message)
        side = FIXHandlerUtils.get_field_value(fix.Side(), fix_message)
        transact_time = FIXHandlerUtils.get_field_string(fix.TransactTime(), fix_message)
        order_quantity = FIXHandlerUtils.get_field_value(fix.OrderQty(), fix_message)
        order_type = FIXHandlerUtils.get_field_value(fix.OrdType(), fix_message)
        price = FIXHandlerUtils.get_field_value(fix.Price(), fix_message)
        stop_price = FIXHandlerUtils.get_field_value(fix.StopPx(), fix_message)
        sender_company_id = FIXHandlerUtils.get_header_field_value(fix.SenderCompID(), fix_message)
        sending_time = FIXHandlerUtils.get_header_field_string(fix.SendingTime(), fix_message)
        on_behalf_of_comp_id = FIXHandlerUtils.get_header_field_value(fix.OnBehalfOfCompID(), fix_message)
        sender_sub_id = FIXHandlerUtils.get_header_field_value(fix.SenderSubID(), fix_message)
        return cls(client_order_id, handling_instruction, execution_instruction, symbol, maturity_month_year,
                   maturity_day, side,
                   transact_time, order_quantity, order_type, price, stop_price, sender_company_id,
                   sending_time, on_behalf_of_comp_id, sender_sub_id)

    def to_fix_message(self):
        """Creates from a new single order object a fix message
        Returns:
            message (quickfix.Message"""
        message = fix.Message()
        header = message.getHeader()
        if self.sender_company_id is not None: header.setField(fix.SenderCompID(self.sender_company_id()))
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        header.setField(fix.SendingTime())

        # Set Fix Message fix_order object
        maturity_month_year_fix = fix.MaturityMonthYear()
        maturity_month_year_fix.setString(str(self.maturity_month_year))
        transact_time_fix = fix.TransactTime()
        transact_time_fix.setString(str(self.transaction_time))

        message.setField(fix.ClOrdID(self.client_order_id))
        message.setField(fix.HandlInst(self.handling_instruction))
        message.setField(fix.Symbol(self.symbol))
        message.setField(maturity_month_year_fix)
        message.setField(fix.MaturityDay(str(self.maturity_day)))
        message.setField(fix.Side(self.side))
        message.setField(transact_time_fix)
        message.setField(fix.OrderQty(self.order_quantity))
        message.setField(fix.OrdType(self.order_type))
        message.setField(fix.Price(self.price))
        if self.stop_price is not None: message.setField(fix.StopPx(self.stop_price))


class ExecutionReport(object):
    """Constructor
    Args:
        order_id (string): order id
        client_order_id (string): client order id (if it's cancellation response it will be client cancel order id)
        execution_id (string): execution id
        execution_transaction_type (char): execution transaction type
        execution_type (char): execution type
        order_status (char):
        symbol (String): ticker symbol of the stock
        side (char):
        left_quantity (float): amount of shares open for further execution
        cumulative_quantity (float): total number of shares filled
        average_price (float): calculated average price of all fills on this order
        price (float): price of order if it's an order execution response
        receiver_comp_id (String): receiver of company id
        original_client_order_id : client order id in case of cancellation response returned
    """

    def __init__(self, order_id, client_order_id, execution_id, execution_transaction_type, execution_type,
                 order_status, symbol, side, left_quantity, cumulative_quantity, average_price, price,
                 receiver_comp_id=None, original_client_order_id=None):
        self.order_id = order_id
        self.client_order_id = client_order_id
        self.execution_id = execution_id
        self.execution_transaction_type = execution_transaction_type
        self.execution_type = execution_type
        self.order_status = order_status
        self.symbol = symbol
        self.side = side
        self.left_quantity = left_quantity
        self.cumulative_quantity = cumulative_quantity
        self.average_price = average_price
        self.price = price
        self.receiver_comp_id = receiver_comp_id
        if original_client_order_id is not None:
            self.original_client_order_id = original_client_order_id
        else:
            self.original_client_order_id = None


    @classmethod
    def from_order(cls, order, execution_transaction_type, execution_type, order_status, left_quantity,
                   cumulative_quantity, average_price):
        """
        Args:
            order (TradingClass.Order)
            execution_transaction_type (char)
            execution_type (int)
            order_status (int)
            left_quantity (float): amount of shares open for further execution
            cumulative_quantity (float): total number of shares filled
            average_price (float): calculated average price of all fills on this order
        """
        order_id = order.order_id
        client_order_id = order.client_order_id
        execution_id = None
        # execution_transaction_type
        # str(execution_type)
        # str(order_status)
        symbol = order.stock_ticker
        side = order.side
        # left_quantity
        # cumulative_quantity
        # average_price
        price = order.price
        execution_report = cls(order_id, client_order_id, execution_id, execution_transaction_type, str(execution_type),
                               str(order_status), symbol, side, left_quantity, cumulative_quantity, average_price,
                               price)
        return execution_report

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def create_fix_message(self):
        """Creates from an execution report a fix message"""
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_ExecutionReport))
        header.setField(fix.SendingTime())

        message.setField(fix.OrderID(self.order_id))
        message.setField(fix.ClOrdID(self.client_order_id))
        message.setField(fix.ExecID(self.execution_id))
        message.setField(fix.ExecTransType(self.execution_transaction_type))
        message.setField(fix.ExecType(self.execution_type))
        message.setField(fix.OrdStatus(self.order_status))
        message.setField(fix.Symbol(self.symbol))
        message.setField(fix.Side(self.side))
        message.setField(fix.LeavesQty(self.left_quantity))
        message.setField(fix.CumQty(self.cumulative_quantity))
        message.setField(fix.AvgPx(self.average_price))
        message.setField(fix.Price(self.price))
        return message


class Order(object):
    """Constructor of class Order, it is designed after the Order table from the database
    Args:
        client_order_id (string): The order ID from the client side
        account_company_id (string): account company id related to the order
        received_date (FIXDate object): received_date
        handling_instruction (int/DatabaseHandlerUtils.HandlingInstruction): handling instruction
        stock_ticker (string): ticker symbol of the stock referring in the order
        side (int/DatabaseHandlerUtils.Side): type of order
        maturity_date (FIXDate object): the date when order will mature
        order_type (int/DatabaseHandlerUtils.OrderType): the type of order, see Side for different types
        order_quantity (float): order quantity
        price (float): price of the stock
        last_status (int/DatabaseHandlerUtils.LastStatus): last status
        msg_seq_num (int): message sequence number
        on_behalf_of_company_id (string): original sender who sends order
        sender_sub_id (string): sub identifier of sender
        cash_order_quantity (float): amount of order requested
        msg_seq_num (int)
        cumulative_order_quantity (float): the remaining amount of shares of the order able to be sold/bought
        average_price (float): the average price of the sold, bought shares

    """

    def __init__(self, client_order_id, account_company_id, received_date, handling_instruction, stock_ticker, side,
                 maturity_date,
                 order_type, order_quantity, price, last_status, msg_seq_num=None, on_behalf_of_company_id=None,
                 sender_sub_id=None, cash_order_quantity=None, cumulative_order_quantity=None, average_price=None):
        self.client_order_id = client_order_id
        self.account_company_id = account_company_id
        self.received_date = received_date
        self.handling_instruction = handling_instruction
        self.stock_ticker = stock_ticker
        self.side = side
        self.maturity_date = maturity_date
        self.order_type = order_type
        self.order_quantity = order_quantity
        self.price = price
        self.last_status = last_status
        self.msg_seq_num = msg_seq_num
        self.on_behalf_of_company_id = on_behalf_of_company_id
        self.sender_sub_id = sender_sub_id
        self.cash_order_quantity = cash_order_quantity
        self.cumulative_order_quantity = cumulative_order_quantity
        self.average_price = average_price

    @classmethod
    def create_dummy_order(cls, client_order_id="20161120-001", account_company_id="client",
                           received_date=FIXDate.from_fix_date_stamp_string("20161120"), handling_instruction=1,
                           stock_ticker="TSLA", side=DatabaseHandlerUtils.Side.BUY,
                           maturity_date=FIXDate.from_fix_date_stamp_string("20161125"),
                           order_type=DatabaseHandlerUtils.OrderType.MARKET, order_quantity=100.00, price=10.00,
                           last_status=DatabaseHandlerUtils.LastStatus.PENDING, msg_seq_num=0,
                           cumulative_order_quantity=50., average_price=12.):
        """For testing"""
        dummy_order = cls(client_order_id=client_order_id, account_company_id=account_company_id,
                          received_date=received_date, handling_instruction=handling_instruction,
                          stock_ticker=stock_ticker, side=side, maturity_date=maturity_date, order_type=order_type,
                          order_quantity=order_quantity, price=price, last_status=last_status, msg_seq_num=msg_seq_num,
                          cumulative_order_quantity=cumulative_order_quantity, average_price=average_price)
        return dummy_order

    @classmethod
    def from_new_single_order(cls, new_single_order):
        """Creates a order from a TradingClass.NewSingleOrder
        Args:
            new_single_order (TradingClass.NewSingleOrder):
        Returns:
            order (TradingClass.Order): The order object
        """

        client_order_id = new_single_order.client_order_id
        account_company_id = new_single_order.sender_company_id
        received_time = FIXDateTimeUTC.create_for_current_time()
        handling_instruction = new_single_order.handling_instruction
        stock_ticker = new_single_order.symbol
        side = new_single_order.side
        maturity_date = FIXDate.from_year_month_day(new_single_order.maturity_month_year.year,
                                                    new_single_order.maturity_month_year.month,
                                                    new_single_order.maturity_day)
        order_type = new_single_order.order_type
        order_quantity = new_single_order.order_quantity
        price = new_single_order.price
        last_status = DatabaseHandlerUtils.LastStatus.PENDING
        message_sequence_number = 0
        on_behalf_of_company_id = None
        sender_sub_id = None
        cash_order_quantity = None

        order = cls(client_order_id, account_company_id, received_time, handling_instruction, stock_ticker,
                    side, maturity_date, order_type, order_quantity, price, last_status, message_sequence_number,
                    on_behalf_of_company_id, sender_sub_id, cash_order_quantity)
        return order

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(self, other)

    @property
    def order_id(self):
        """
        Returns:
             order_id (string):
        """
        return Order.create_order_id(self.client_order_id, self.account_company_id, self.received_date)

    @staticmethod
    def create_order_id(client_order_id, account_company_id, received_date):
        """Creates an order id from the components. Use this method if you want
         to create an order id

        Args:
            client_order_id (string)
            account_company_id (string)
            received_date (TradingClass.FIXDate)
        Returns:
             order_id (string):
        """
        return client_order_id + "_" + account_company_id + "_" + str(received_date)

################################
### Database related classes ###
################################


class DatabaseStockInformation:
    def __init__(self, current_price=None, current_volume=None, opening_price=None, closing_price=None,
                 day_high=None,
                 day_low=None):
        self.current_price = current_price
        self.current_volume = current_volume
        self.opening_price = opening_price
        self.closing_price = closing_price
        self.day_high = day_high
        self.day_low = day_low


class OrderExecution:
    def __init__(self, execution_id, quantity, price, execution_time, buyer_client_order_id,
                 buyer_company_id, buyer_received_date, seller_client_order_id, seller_company_id,
                 seller_received_date):
        """
        Args:
            execution_id (int)
            quantity (float): quantity of the order execution
            price (float): price of the order execution (the price on which both parties execute order)
            execution_time (TradingClass.FIXDateTimeUTC): date and time of execution
            buyer_client_order_id (string)
            buyer_company_id (string)
            buyer_received_date (TradingClass.FIXDate)
            seller_client_order_id (string)
            seller_company_id (string)
            seller_received_date (string)
        """
        self.execution_id = execution_id
        self.quantity = quantity
        self.price = price
        self.execution_time = execution_time
        self.buyer_client_order_id = buyer_client_order_id
        self.buyer_company_id = buyer_company_id
        self.buyer_received_date = buyer_received_date
        self.seller_client_order_id = seller_client_order_id
        self.seller_company_id = seller_company_id
        self.seller_received_date = seller_received_date

    @classmethod
    def from_buy_and_sell_order(cls, executed_quantity, executed_price, buy_order, sell_order,
                                execution_time):
        """
        Args:
            executed_quantity (float): quantity of the order execution
            executed_price (float): the price on which both parties execute order
            buy_order (TradingClass.Order):
            sell_order (TradingClass.Order):
            execution_time (TradingClass.FIXDateTimeUTC)
        """
        order_execution = cls(execution_id=None, quantity=executed_quantity, price=executed_price,
                              execution_time=execution_time,
                              buyer_client_order_id=buy_order.client_order_id,
                              buyer_company_id=buy_order.account_company_id,
                              buyer_received_date=buy_order.received_date,
                              seller_client_order_id=sell_order.client_order_id,
                              seller_company_id=sell_order.account_company_id,
                              seller_received_date=sell_order.received_date)
        return order_execution

    @classmethod
    def create_dummy_order_execution(cls, execution_id=0, quantity=100., price=50.,
                                     execution_time=FIXDateTimeUTC.from_date_fix_time_stamp_string(
                                         "20111111-11:11:11"),
                                     buyer_client_order_id="0",
                                     buyer_company_id="GS",
                                     buyer_received_date=FIXDate.from_fix_date_stamp_string("20161109"),
                                     seller_client_order_id="1",
                                     seller_company_id="MS",
                                     seller_received_date=FIXDate.from_fix_date_stamp_string("20161108")):
        """
        Args:
            executed_quantity (float): quantity of the order execution
            executed_price (float): the price on which both parties execute order
            buy_order (TradingClass.Order):
            sell_order (TradingClass.Order):
            execution_time (TradingClass.FIXDateTimeUTC)
        """
        dummy_order_execution = cls(execution_id, quantity, price, execution_time, buyer_client_order_id,
                                    buyer_company_id, buyer_received_date, seller_client_order_id,
                                    seller_company_id, seller_received_date)
        return dummy_order_execution

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(self, other)

    @property
    def buyer_order_id(self):
        """
        Returns:
             buyer_order_id (string):
        """
        return Order.create_order_id(self.buyer_client_order_id, self.buyer_company_id,
                                     self.buyer_received_date)

    @property
    def seller_order_id(self):
        """
        Returns:
             seller_order_id (string):
        """
        return Order.create_order_id(self.seller_client_order_id, self.seller_company_id,
                                     self.seller_received_date)


class OrderCancel(object):
    """Constructor of class OrderCancel, it is designed after the OrderCancel table from the database
    Args:
        client_order_id (String): original order ID
        order_cancel_id (String): cancelled order ID from the client side
        account_company_id (String): account company id related to the order
        order_received_date (FixDate): order received date
        stock_ticker (String): ticker symbol of the stock referring in the order
        side (int): side
        order_quantity (int): order quantity
        last_status (int): last status
        msg_seq_num (int): message sequence number
        on_behalf_of_company_id (String): original sender who sends order
        sender_sub_id (String): sub identifier of sender
        cancel_quantity (float): otal order quantity cancelled
        execution_time (FixDateTimeUTC): execution time of cancelling the order
    """

    def __init__(self, client_order_id, order_cancel_id, account_company_id, order_received_date, stock_ticker,
                 side,
                 order_quantity, last_status, received_time, msg_seq_num=None , cancel_quantity=None,
                 execution_time=None, on_behalf_of_company_id=None, sender_sub_id=None):
        self.client_order_id = client_order_id
        self.order_cancel_id = order_cancel_id
        self.account_company_id = account_company_id
        self.order_received_date = order_received_date
        self.stock_ticker = stock_ticker
        self.side = side
        self.order_quantity = order_quantity
        self.last_status = last_status
        self.received_time = received_time
        self.msg_seq_num = msg_seq_num
        self.cancel_quantity = cancel_quantity
        self.execution_time = execution_time
        self.on_behalf_of_company_id = on_behalf_of_company_id
        self.sender_sub_id = sender_sub_id

    @classmethod
    def from_order_cancel_request(cls, order_cancel_request):
        """Creates a order from a TradingClass.OrderCancelRequest
        Args:
            order_cancel_request (TradingClass.OrderCancelRequest):
        Returns:
            order_cancel (TradingClass.OrderCancel): The order cancel object
        """

        client_order_id = order_cancel_request.orig_cl_ord_id
        order_cancel_id = order_cancel_request.cl_ord_id
        account_company_id = order_cancel_request.sender_comp_id
        order_received_date = None
        received_time = FIXDateTimeUTC.create_for_current_time()
        stock_ticker = order_cancel_request.symbol
        side = order_cancel_request.side
        order_quantity = order_cancel_request.order_qty
        last_status = DatabaseHandlerUtils.LastStatus.PENDING
        message_sequence_number = None
        on_behalf_of_company_id = None
        sender_sub_id = None
        cancel_quantity = None
        execution_time = None
        order_cancel = cls(client_order_id, order_cancel_id, account_company_id, order_received_date, stock_ticker,
                           side, order_quantity, last_status, received_time, message_sequence_number, cancel_quantity,
                           execution_time, on_behalf_of_company_id, sender_sub_id)
        return order_cancel

    @classmethod
    def create_dummy_order_cancel(cls, client_order_id = '0', order_cancel_id = '1', account_company_id = 'MS',
        order_received_date = FIXDate.from_year_month_day(2016,11,8), stock_ticker = "TSLA",
        side = 2, order_quantity = 100, last_status = DatabaseHandlerUtils.LastStatus.CANCELED,
        received_time = FIXDateTimeUTC.create_for_current_time(), msg_seq_num = 1, cancel_quantity=10,
                                  execution_time=FIXDateTimeUTC.create_for_current_time()):
        """For testing"""
        dummy_order_cancel = cls(client_order_id, order_cancel_id, account_company_id, order_received_date,
                                 stock_ticker, side, order_quantity, last_status, received_time, msg_seq_num,
                                 cancel_quantity,execution_time)

        return dummy_order_cancel
###########################
### GUI related classes ###
###########################

class StockInformation():
    def __init__(self, p_price, p_high, p_low):
        self.price = p_price
        self.high = p_high
        self.low = p_low


class StockHistory():
    def __init__(self, p_time, p_price, p_quantity):
        """ A stock history object to be represented

        Args:
            p_time (list of string):  YYYY-MM-DD-HH-MM
            p_price (list of float):
            p_quantity (list of int): quantities
        """
        self.time = p_time
        self.price = p_price
        self.quantity = p_quantity


class OrderBookBuy():
    def __init__(self, p_price, p_quantity):
        # price,quantity are list type, with length of 5
        self.price = p_price
        self.quantity = p_quantity


class OrderBookSell():
    def __init__(self, p_price, p_quantity):
        # price,quantity are list type, with length of 5
        self.price = p_price
        self.quantity = p_quantity


class MarketData():
    def __init__(self, p_stock_information, p_stock_history, p_order_book_buy, p_order_book_sell):
        # type of parameters:
        # stock_information -> StockInformation
        # stock_history -> StockHistory
        # order_book_buy -> OrderBookBuy
        # order_book_sell -> OrderBookSell
        self.stock_information = p_stock_information
        self.stock_history = p_stock_history
        self.order_book_buy = p_order_book_buy
        self.order_book_sell = p_order_book_sell


class TradingTransaction():
    def __init__(self, p_time, p_price, p_quantity, p_side):
        # side: True means buy, False means sell
        self.time = p_time
        self.price = p_price
        self.quantity = p_quantity
        self.side = p_side
