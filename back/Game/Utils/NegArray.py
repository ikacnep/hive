class NegArray:
    innerArr = [0, []]
    dimentions = 2
    count = []
    mod = []

    def __init__(self, dim = 2):
        self.innerArr = [0, []]
        self.dimentions = dim
        self.count = [0] * dim

    def Reset(self):
        self.innerArr = [0]

    def Dim(self):
        return self.dimentions

    def Count(self, dim):
        return self.count[dim - 1]

    def Get(self, pos):
        if (len(pos) != self.dimentions):
            raise IndexError("Wrong amount of items")

        cur = self.innerArr
        for i in range(0, len(pos)):
            curPos = pos[i] + cur[0]
            if (curPos >= len(cur[1]) or curPos < 0):
                return None
            cur = cur[1][curPos]

        return cur

    def Put(self, data, pos):
        if (len(pos) != self.dimentions):
            raise IndexError("Wrong amount of items")

        cur = self.innerArr
        curDat = None
        curPos = 1
        for i in range(0, len(pos)):
            curPos = pos[i] + cur[0]
            curDat = cur[1]
            if (curPos < 0):
                cur[0] -= curPos
                while (curPos < 0):
                    if (i < len(pos) - 1):
                        curDat.insert(0, [0, []])
                    else:
                        curDat.insert(0, None)
                    curPos += 1

            if (curPos >= len(curDat)):
                while (curPos >= len(cur[1])):
                    if (i < len(pos) - 1):
                        curDat.append([0, []])
                    else:
                        curDat.append(None)

            if (len(curDat) > self.count[i]):
                self.count[i] = len(curDat)

            cur = curDat[curPos]

        curDat[curPos] = data
