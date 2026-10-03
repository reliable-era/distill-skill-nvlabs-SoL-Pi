from canonical import key

def get(catalog, name):
    return catalog.get(key(name))
