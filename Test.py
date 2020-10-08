SPO2 = 'sssssss'

def test():

    global SPO2

    print(SPO2)
    d = 'hello'
    globals()['SPO2'] = d
    print(SPO2)
    print(d)
    d = 'asdsad'
    print(d)
    print(SPO2)

test()