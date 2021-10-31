from math import modf, fabs, floor


def get_binary_repr(f):
    frac, fint = modf(fabs(f))  # split on fractional, integer parts
    n, d = frac.as_integer_ratio()  # frac = numerator / denominator
    return f'{floor(fint):b}.{n:0{d.bit_length() - 1}b}'
