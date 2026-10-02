def total(prices, discount_percent=0):
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount out of range")
    return sum(prices) * (1 - discount_percent / 100)
