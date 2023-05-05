
def len_list(list_):
    if list_:
        list_ = [x for x in list_ if x != '']
        # if list_ is not None:
        return len(list(list_))


def update_dict(dict1, dict2):
    if dict2:
        return dict1.update(dict2)


filters = [len_list, update_dict]
