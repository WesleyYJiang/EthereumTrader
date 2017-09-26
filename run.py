from connect import Bit_Connect
import time

connect = Bit_Connect(key, secret, customer_id)


def run_script():
    # Runs the script until program quits
    log = ""
    eth_lower_bound = 260
    holding = False

    while True:
        # Make the system sleep to prevent API overuse
        time.sleep(2)
        # Current value of eth
        current_value = connect.get_market_price('eth', 'usd')
        # Ethereum balance that will be moved with this algorithm
        moving_balance = connect.get_account_balance('eth', 'usd')['eth_balance'] / 10

        # If the current value reaches the lower bound and you are holding money
        if current_value == eth_lower_bound and holding:
            connect.cancel_orders()
            log += "Lower Bound Reached, Selling Moving Balance" + '\n'
            print("Lower Bound Reached, Selling Moving Balance" + '\n')
            connect.limit_sell(moving_balance, eth_lower_bound, 'eth', 'usd')
            holding = False

        # If the current value reaches the lower bound and you are not holding money
        if current_value == eth_lower_bound and not holding:
            connect.cancel_orders()
            log += "Lower Bound Reached, Buying Moving Balance" + '\n'
            print("Lower Bound Reached, Buying Moving Balance" + '\n')
            connect.limit_buy(moving_balance, eth_lower_bound, 'eth', 'usd')
            holding = True

        # If the percent change increases by more than 10% then increase the lower bound by 5%
        if connect.get_percent_change('eth', 'usd') > 10:
            new_bound = eth_lower_bound + eth_lower_bound * .5
            log += "Raising ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n'
            log += "Current Value is at " + str(current_value)
            print("Raising ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n')
            print("Current Value is at " + str(current_value))
            eth_lower_bound = new_bound

        # If the percent change increases by more than 10% then decrease the lower bound by 5%
        if connect.get_percent_change('eth', 'usd') < -10:
            new_bound = eth_lower_bound - eth_lower_bound * .5
            log += "Lowering ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n'
            log += "Current ETH Value is at " + str(current_value)
            print("Lowering ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n')
            print("Current ETH Value is at " + str(current_value))
            eth_lower_bound = new_bound

if __name__ == '__main__':
    run_script()











