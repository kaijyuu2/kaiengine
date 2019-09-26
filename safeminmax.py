def dmax(iter, default=0):
    try:
        return max(iter)
    except ValueError:
        return default

def dmin(iter, default=999):
    try:
        return min(iter)
    except ValueError:
        return default
