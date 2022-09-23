from __future__ import print_function, division
import math
# import random
import sys
from operator import itemgetter

# # Python 2.x and 3.x compatibility
if sys.version_info.major == 2:
    range = xrange
    from future_builtins import map, zip


CHAR_LOOKUP_SYMBOLS = [(0, ' '), # Should be sorted
                      (1, '*'),
                      (2, ':'),
                      #(3, '!'),
                      (4, '|'),
                      #(8, '+'),
                      (float("inf"), '#')]

def charlookup(num_chars):
    """ Character for the given amount of elements in the bin """
    return next(ch for num, ch in CHAR_LOOKUP_SYMBOLS if num_chars <= num)


def bin_generator(data, bin_ends):
    """ Yields a list for each bin """
    max_idx_end = len(bin_ends) - 1
    iends = enumerate(bin_ends)

    idx_end, value_end = next(iends)
    bin_data = []
    for el in sorted(data):
        while el >= value_end and idx_end != max_idx_end:
            yield bin_data
            bin_data = []
            idx_end, value_end = next(iends)
        bin_data.append(el)

    # Finish
    for unused in iends:
        yield bin_data
        bin_data = []
    yield bin_data


def enumerated_reversed(seq):
    """ A version of reversed(enumerate(seq)) that actually works """
    return zip(range(len(seq) - 1, -1, -1), reversed(seq))
    
def merge(a, b):
    ret = []
    for i in range(0, len(a)):
        if a[i] == '*' or b[i] == '*':
            ret.append('*')
        else:
            ret.append(' ')
    return ret


def plot(y_vals, x_vals=None, num_x_chars=70, num_y_chars=15):
    """
    Plots the values given by y_vals. The x_vals values are the y indexes, by
    default, unless explicitly given. Pairs (x, y) are matched by the x_vals
    and y_vals indexes, so these must have the same length.

    The num_x_chars and num_y_chars inputs are respectively the width and
    height for the output plot to be printed, given in characters.
    """
    y_vals = list(y_vals)
    x_vals = list(x_vals) if x_vals else list(range(len(y_vals)))
    if len(x_vals) != len(y_vals):
        raise ValueError("x_vals and y_vals must have the same length")

    ymin = min(y_vals)
    ymax = max(y_vals)
    xmin = min(x_vals)
    xmax = max(x_vals)

    xbinwidth = (xmax - xmin) / num_x_chars
    y_bin_width = (ymax - ymin) / num_y_chars

    x_bin_ends = [(xmin + (i+1) * xbinwidth, 0) for i in range(num_x_chars)]
    y_bin_ends = [ymin + (i+1) * y_bin_width for i in range(num_y_chars)]

    columns_pairs = bin_generator(zip(x_vals, y_vals), x_bin_ends)
    yloop = lambda *args: [charlookup(len(el)) for el in bin_generator(*args)]
    ygetter = lambda iterable: map(itemgetter(1), iterable)
    columns = (yloop(ygetter(pairs), y_bin_ends) for pairs in columns_pairs)
    rows = list(zip(*columns))
    
    pr = [];
    for idx, row in enumerated_reversed(rows):
        if not pr:
            pr = row
        else:
            pr = merge(row, pr)
        y_bin_mid = y_bin_ends[idx] - y_bin_width / 2
        print("".join(pr))
        # print(y_bin_mid, '\t', "".join(pr))
