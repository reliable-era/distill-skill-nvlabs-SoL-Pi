def total(prices, rebate_percent=0):
    if not 0 <= rebate_percent <= 100:
        raise ValueError("discount out of range")
    return sum(prices) * (1 - rebate_percent / 100)
