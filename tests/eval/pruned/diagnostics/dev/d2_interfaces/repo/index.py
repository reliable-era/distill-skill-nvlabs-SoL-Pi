from normalization import key
def build(rows):
    return {key(name):value for name,value in rows}
