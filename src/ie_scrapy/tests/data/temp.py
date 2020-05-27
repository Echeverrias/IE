
def foo():
    with open('temps.txt' 'r') as f:
        l = f.readlines()
    import pickle
    with open('company_links.list', 'wb') as f:
        pickle.dump(l, f)
    return l
