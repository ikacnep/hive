def ReallyEqual(a, b):
    if (not isinstance(a, list)):
        if (not isinstance(b, list)):
            return a == b
        return False

    if (len(a) != len(b)):
        return False

    for i in range(0, len(a)):
        if (not ReallyEqual(a[i], b[i])):
            return False

    return True

def Intersect(a, b):
    rv = []
    for i in range (0, len(a)):
        cur = a[i]
        for j in range (0, len(b)):
            if (ReallyEqual(cur, b[j])):
                rv.append(cur)
                break
    return rv

def Except(a, b):
    rv = []
    for i in range (0, len(a)):
        cur = a[i]
        isPresent = False
        for j in range(0, len(b)):
            if (ReallyEqual(cur, b[j])):
                isPresent = True
                break
        if (not isPresent):
            rv.append(cur)
    return rv

def Union(a, b):
    rv = []
    for cur in a:
        rv.append(cur)
    for cur in b:
        exists = False
        for test in a:
            if (ReallyEqual(test, cur)):
                exists = True
                break
        if (not exists):
            rv.append(cur)

    return rv



def CellsNearby(pos):
    i = pos[0]
    j = pos[1]
    return [(i , j - 1), (i - 1, j), (i - 1, j + 1), (i, j + 1), (i + 1, j), (i + 1, j - 1)]