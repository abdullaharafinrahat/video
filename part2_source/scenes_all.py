from scenes1 import *
try:
    from scenes2 import *
except ImportError:
    pass
try:
    from scenes3 import *
except ImportError:
    pass

START = 189.5
TIMES = {19: (189.5, 201.7), 20: (201.7, 210.0), 21: (210.0, 219.5), 22: (219.5, 232.3), 23: (232.3, 240.6),
         24: (240.6, 244.6), 25: (244.6, 248.2), 26: (248.2, 259.6), 27: (259.6, 274.6), 28: (274.6, 281.8),
         29: (281.8, 288.4), 30: (288.4, 309.6), 31: (309.6, 341.2), 32: (341.2, 364.3)}
CLASSES = {}
for _n in range(19, 33):
    c = globals().get('S%d' % _n)
    if c:
        CLASSES[_n] = c


def build_scenes(only=None):
    out = {}
    for n, c in CLASSES.items():
        if only and n not in only:
            continue
        out[n] = c(*TIMES[n])
    return out
