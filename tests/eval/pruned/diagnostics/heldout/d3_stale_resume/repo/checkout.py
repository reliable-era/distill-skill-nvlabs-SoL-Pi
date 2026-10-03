def total(prices, rebate_percent=0):
    subtotal = sum(prices)
    return subtotal * (1 - rebate_percent)
