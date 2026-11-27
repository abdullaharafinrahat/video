import sys, time; sys.path.insert(0,'.')
from core import *
import shots
from PIL import Image
ts = [float(x) for x in sys.argv[1:]]
cache = {}
for tg in ts:
    cls = shots.shot_for(tg)
    if cls not in cache:
        cache.clear(); import gc; gc.collect()
        t0=time.time(); cache[cls]=cls(); print(cls.__name__,'init',round(time.time()-t0,2))
    sh = cache[cls]
    t0=time.time()
    img, gr = sh.frame(tg-cls.T0, tg, int(tg*24))
    out = post(img, int(tg*24), gr) if img is not None else np.zeros((H,W,3),np.uint8)
    print(tg, 'frame', round(time.time()-t0,2))
    Image.fromarray(out).resize((960,540), Image.LANCZOS).save('tests/f_%05.2f_%d.png'%(tg, int(time.time())))
