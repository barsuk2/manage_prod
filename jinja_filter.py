def len_list(list_):
    if list_:
        list_ = [x for x in list_ if x != '']
    # if list_ is not None:
        return len(list(list_))
