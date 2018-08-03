import nltk


prop_dict = {
        'RAM': ['memory', 'ram'],
        'Disk': ['disk', 'ssd', 'storage', 'hdd'],
        'Traffic': ['traffic', 'bandwidth', 'bw', 'transfer'],
        }


def get_property(prop:str, key_words: [str], st: nltk.tree.Tree):
    s = str(st.flatten()).lower()
    # print(s)
    found_key_word = False
    for kw in key_words:
        if kw in s:
            found_key_word = True

    if not found_key_word:
        return False, None, None

    found_count = False
    for leaf in st.leaves():
        if leaf[1] == 'CD':
            count = leaf[0]
            found_count = True
        elif leaf[1] == 'NNP' and found_count:
            count += leaf[0]
            break
    print(prop, count)
    return True, prop, count


def get_price(st: nltk.tree.Tree):
    s = str(st.flatten()).lower()
    key_words = ['/m', 'mo',  'month', 'year']
    key_word = None
    found_key_word = False
    for kw in key_words:
        if kw in s:
            key_word = kw
            found_key_word = True

    if not found_key_word:
        return False, None, None

    unit = None
    count = ''
    c = 0
    for leaf in st.leaves():
        if c == 2:
            break
        if leaf[1] == 'CD':
            s = leaf[0].split('/')[0]
            if key_word == 'year':
                count += str(float(s)/12)
            else:
                count += s
            c += 1
        elif leaf[1] == '$':
            count += '$'
            c += 1

    print('Price', count)
    return True, 'Price', count
