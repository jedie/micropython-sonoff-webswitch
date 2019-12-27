import gc

_HEX = '0123456789ABCDEF'


def unquote(string):
    string = string.replace('+', ' ')
    if '%' not in string:
        return string

    bits = string.split('%')
    if len(bits) == 1:
        return string

    res = [bits[0]]
    for item in bits[1:]:
        if len(item) >= 2:
            a, b = item[:2].upper()
            if a in _HEX and b in _HEX:
                res.append(chr(int(a + b, 16)))
                res.append(item[2:])
                continue

        res.append('%')
        res.append(item)

    return ''.join(res)


def parse_qsl(qs):
    if qs is None:
        return ()
    qs = str(qs)
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    res = []
    for name_value in pairs:
        try:
            name, value = name_value.split('=', 1)
        except ValueError:
            res.append((unquote(name_value), ''))
        else:
            res.append((unquote(name), unquote(value)))
    return res


def request_query2dict(qs):
    query_dict = dict(parse_qsl(qs))
    gc.collect()
    return query_dict
