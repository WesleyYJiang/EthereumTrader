from connect import Bit_Connect
import time


connect = Bit_Connect(key, secret, customer_id)

# First buy in
# Set lower bound at buy in price
# Continue holding
# If price increases by 10%
# move lower bound up by %5
# if price reaches lower bound, sell
# If price decreases by 10%, move lower bound down by 5%
# If price reaches lower bound and you own no currency, buy in

# price = 260  buy in
# price increases to 300, increase lower bound to 280
# if price decreases to 280, sell
# if price continues to decrease to 220 (-10%), decrease lower bound to 240
# if price increases back to 240, buy in


def run_script():
    log = ""
    eth_lower_bound = 260
    holding = False

    while True:
        time.sleep(2)
        current_value = connect.get_market_price('eth', 'usd')
        moving_balance = connect.get_account_balance('eth', 'usd')['eth_balance'] / 10

        if current_value == eth_lower_bound and holding:
            connect.cancel_orders()
            log += "Lower Bound Reached, Selling Moving Balance" + '\n'
            print("Lower Bound Reached, Selling Moving Balance" + '\n')
            connect.limit_sell(moving_balance, eth_lower_bound, 'eth', 'usd')
            holding = False

        if current_value == eth_lower_bound and not holding:
            connect.cancel_orders()
            log += "Lower Bound Reached, Buying Moving Balance" + '\n'
            print("Lower Bound Reached, Buying Moving Balance" + '\n')
            connect.limit_buy(moving_balance, eth_lower_bound, 'eth', 'usd')
            holding = True

        if connect.get_percent_change('eth', 'usd') > 10:
            new_bound = eth_lower_bound + eth_lower_bound * .5
            log += "Raising ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n'
            log += "Current Value is at " + str(current_value)
            print("Raising ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n')
            print("Current Value is at " + str(current_value))
            eth_lower_bound = new_bound

        if connect.get_percent_change('eth', 'usd') < -10:
            new_bound = eth_lower_bound - eth_lower_bound * .5
            log += "Lowering ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n'
            log += "Current ETH Value is at " + str(current_value)
            print("Lowering ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n')
            print("Current ETH Value is at " + str(current_value))
            eth_lower_bound = new_bound

if __name__ == '__main__':
    run_script()











