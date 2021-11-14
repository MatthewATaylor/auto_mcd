def str_is_num(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def str_is_dollar_amt(s):
    return len(s) > 1 and s[0] == "$" and str_is_num(s[1:])


def str_is_cal_count(s):
    return " Cal." in s


def str_is_limit(s):
    return "Limit of " in s and s.removeprefix("Limit of ").isnumeric()
