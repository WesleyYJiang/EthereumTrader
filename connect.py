import bitstamp.client


class BitConnect:
        key = ""
        secret = ""
        customer_id = ""

        def __init__(self, key, secret, customer_id):
            self.key = key
            self.secret = secret
            self.customer_id = customer_id

        # Returns the private client  api access
        def get_private_client(self):
            trading_client = bitstamp.client.Trading(
                username=self.customer_id, key=self.key, secret=self.secret)
            return trading_client

        # Returns the public client api access
        def get_public_client(self):
            return bitstamp.client.Public()

        def get_account_balance(self, currency_type, quote):
            client = self.get_private_client()
            return client.account_balance(currency_type, quote)

        # Returns the value of the given currency
        def get_market_price(self, currency_type, quote):
            client = self.get_public_client()
            return client.ticker(currency_type, quote)["last"]

        # Returns the value of the given currency
        def get_percent_change(self, currency_type, quote):
            client = self.get_public_client()
            return (1 - float(client.ticker(currency_type, quote)["low"])
                    / float(client.ticker(currency_type, quote)["last"])) * 100

        # Perform a market buy
        def market_buy(self, amount, currency_type, quote):
            client = self.get_private_client()
            client.buy_market_order(amount, currency_type, quote)
            return "Market Buy Initiated on " + currency_type

        # Perform a market sell
        def market_sell(self, amount, currency_type, quote):
            client = self.get_private_client()
            client.sell_market_order(amount, currency_type, quote)
            return "Market Sell Initiated on " + currency_type

        # Perform a limit buy
        def limit_buy(self, amount, price, currency_type, quote):
            client = self.get_private_client()
            client.buy_limit_order(amount, price, currency_type, quote)
            return "Limit Buy Initiated on " + currency_type + "at " + price

        # Perform a market buy
        def limit_sell(self, amount, price, currency_type, quote):
            client = self.get_private_client()
            client.sell_limit_order(amount, price, currency_type, quote)
            return "Limit Sell Initiated on " + currency_type + "at " + price

        # Cancels all existing orders
        def cancel_orders(self):
            client = self.get_private_client()
            client.cancel_all_orders()
            return "Orders Cancelled"

        # Retrieve all user transactions
        def retrieve_transaction_history(self):
            client = self.get_private_client()
            client.user_transactions(0,100,True)



