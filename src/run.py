import datetime
import time
from bcolors import ConsoleColors
from src.connect import BitConnect
import json


# Class to encapsulate the different trading algorithms
# Includes a function that simulates the Ethereum market price (not accurately) and tests
# the algorithm on that
class EthereumAlgorithms:
    interval = 0
    interval_bound_change = 0
    connect = ()
    api_calls = 0
    total_gained = 0

    def __init__(self, interval, interval_bound_change, key, secret, customer_id):
        self.interval = interval
        self.interval_bound_change = interval_bound_change
        self.connect = BitConnect(key, secret, customer_id)
        self.api_calls = 0
        self.total_gained = 0

    # Full working algorithm. Actually trades money in real time
    def full_wrench(self, currency_type):
        # Runs the script until program quits
        t_data = self.connect.retrieve_transaction_history()
        current_value = float(self.connect.get_market_price(currency_type, 'usd'))
        try:
            switch_bound = float(t_data[0]["eth_usd"])
        except:
            switch_bound = current_value

        try:
            eth_balance = round(
                float(self.connect.get_account_balance(currency_type, 'usd')[currency_type + '_balance']), 6)
            self.api_calls += 1
        except:
            eth_balance = round(
                float(input("Authorization Failed. Enter Your Current " + currency_type + " Balance Manually:")), 6)

        try:
            usd_balance = round(float(self.connect.get_account_balance(currency_type, 'usd')['usd_balance']), 6)
            self.api_calls += 1
        except:
            usd_balance = round(float(input("Authorization Failed. Enter Your Current USD Balance Manually:")), 6)

        # Ethereum eth_balance that will be moved with this algorithm (in ETH)

        # Determines if you are currently holding any eth
        if eth_balance > 0:
            moving_balance = eth_balance
            holding = True
        else:
            moving_balance = usd_balance / current_value
            holding = False

        starting_value = switch_bound
        starting_time = time.time()
        new_file = open("log-" + str(time.time()) + ".txt", "w+")
        last_bound = switch_bound
        cross_count = 0
        hold_balance = False
        starting_moving_balance = moving_balance
        self.total_gained = \
            round((moving_balance * current_value)
                  - (starting_moving_balance *
                     float(t_data[0][currency_type + '_usd'])), 2)
        while True:

            # For preventing api oversure
            time_elapsed = round((time.time() - starting_time) / 60, 2)
            if time_elapsed >= 10:
                self.api_calls = 0
                starting_time = time.time()

            if self.api_calls > 590:
                return
            time.sleep(1.5)

            # Current value of eth
            try:
                current_value = float(self.connect.get_market_price(currency_type, 'usd'))
                self.api_calls += 1
            except:
                current_value = current_value

            percent_change = (1 - starting_value / current_value) * 100

            if holding:
                self.total_gained = \
                    round((moving_balance * current_value)
                          - (starting_moving_balance * float(
                        self.connect.retrieve_transaction_history()[0][currency_type + '_usd'])), 2)

            # Print Info
            print(ConsoleColors.OKBLUE
                  + str(datetime.datetime.utcnow())
                  + "\t|| %^:" + str(round(percent_change))
                  + "\t|| CV:" + str(round(current_value, 2))
                  + "\t|| SB:" + str(round(switch_bound, 2))
                  + "\t|| B:" + str(round(eth_balance, 2))
                  + "\t|| USD:" + str(round(usd_balance, 2))
                  + "\t|| MB:" + str(round(moving_balance, 2))
                  + "\t|| TG: $" + str(self.total_gained)
                  # + "\t|| API Calls:" + str(self.api_calls)
                  + "\t|| H:" + str(holding) + ConsoleColors.ENDC)

            # Log Info
            log_object = {
                "time": str(datetime.datetime.utcnow()),
                "percent_change": str(round(percent_change)),
                "eth_value": str(current_value),
                "switch_bound": str(switch_bound),
                currency_type + '_balance': str(eth_balance),
                "usd_balance": str(usd_balance),
                "holding": str(holding),
                "api_calls": str(self.api_calls),
                "moving_balance": str(moving_balance)}

            new_file.write(json.dumps(log_object) + "\n")

            if cross_count >= 3:
                hold_balance = True

            # If the current value reaches the switch_bound and you are holding money
            if current_value <= switch_bound and holding and not hold_balance:
                # Cancel existing orders and then sell
                self.connect.cancel_orders()

                self.api_calls += 1
                print(ConsoleColors.WARNING + "Switch Bound Reached, Selling Moving Balance" + ConsoleColors.ENDC)

                # sell_data = json.dumps(self.connect.market_sell(round(moving_balance, 6), currency_type, 'usd'))
                # print(ConsoleColors.WARNING + json.dumps(sell_data) + ConsoleColors.ENDC)
                # self.api_calls += 1

                try:
                    fee = float(self.connect.retrieve_transaction_history()[0]["fee"])
                except:
                    fee = .000625 * moving_balance
                moving_balance -= fee
                self.api_calls += 1

                holding = False
                # Update USD and ETH Balance
                eth_balance -= moving_balance
                usd_balance += moving_balance * current_value
                moving_balance = usd_balance / current_value
                # Make sure you don't get stuck ina trade loop  when the current value doesn't change
                if switch_bound == last_bound:
                    cross_count += 1
                switch_bound += switch_bound * .00001

            # If the current value reaches the  switch_bound and you are not holding money
            elif current_value >= switch_bound and not holding and not hold_balance:
                # Cancel existing orders and then buy
                self.connect.cancel_orders()
                self.api_calls += 1

                print("Switch Bound Reached, Buying Moving Balance")
                moving_balance = usd_balance / current_value

                # buy_data = self.connect.market_buy(round(moving_balance, 6), currency_type, 'usd')
                # print(ConsoleColors.WARNING + json.dumps(buy_data) + ConsoleColors.ENDC)
                # self.api_calls += 1

                try:
                    fee = float(self.connect.retrieve_transaction_history()[0]["fee"])
                except:
                    fee = .000625 * moving_balance
                moving_balance -= fee
                self.api_calls += 1

                holding = True
                # Update USD and Ethereum Balance

                eth_balance += moving_balance
                usd_balance -= moving_balance * current_value
                # Make sure you don't get stuck in a trade loop when the current value doesn't change
                if switch_bound == last_bound:
                    cross_count += 1
                switch_bound -= switch_bound * .00001

            # If percent change increases to > interval then increase the Switch Bound by the price increase * ibc
            if percent_change > self.interval:
                new_bound = switch_bound + (switch_bound * ((percent_change / 100) * self.interval_bound_change))
                print(ConsoleColors.WARNING \
                      + "Raising Switch Bound by " + str((percent_change * self.interval_bound_change)) \
                      + " % from " + str(switch_bound) \
                      + " to " + str(new_bound) + ConsoleColors.ENDC)
                switch_bound = new_bound
                starting_value = switch_bound
                last_bound = switch_bound
                cross_count = 0

            # If the percent change decreases to < interval then decrease the Switch Bound by the price increase * ibc
            elif percent_change < (self.interval * -1):
                new_bound = switch_bound + (switch_bound * ((percent_change / 100) * self.interval_bound_change))
                print (ConsoleColors.WARNING + (
                    "Lowering Switch Bound by " + str(
                        (percent_change * self.interval_bound_change)) + "% from "
                    + str(switch_bound) + " to " + str(new_bound)) + ConsoleColors.ENDC)
                switch_bound = new_bound
                starting_value = switch_bound
                last_bound = switch_bound
                cross_count = 0


if __name__ == '__main__':
    algo = EthereumAlgorithms(1, 1, key, secret, customer_id)
    algo.full_wrench('eth')
