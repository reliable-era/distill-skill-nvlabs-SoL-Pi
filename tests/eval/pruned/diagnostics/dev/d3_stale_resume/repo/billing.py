def total(prices, discount_percent=0):
    subtotal = sum(prices)
    return subtotal * (1 - discount_percent)
