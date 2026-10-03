from labels import display
def row(first,last):
    text=display(first,last)
    return "name=" + text.split(" ")[0]
