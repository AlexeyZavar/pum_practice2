from math import modf, copysign, fabs, floor


def get_binary(f):
    sign = '-' * (copysign(1.0, f) < 0)
    frac, fint = modf(fabs(f))  # split on fractional, integer parts
    n, d = frac.as_integer_ratio()  # frac = numerator / denominator
    return f'{sign}{floor(fint):b}.{n:0{d.bit_length() - 1}b}'
