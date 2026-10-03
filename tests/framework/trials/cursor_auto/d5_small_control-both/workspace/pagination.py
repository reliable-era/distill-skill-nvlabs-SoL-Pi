def page_count(count,size):
    if count == 0:
        return 0
    return (count + size - 1) // size
