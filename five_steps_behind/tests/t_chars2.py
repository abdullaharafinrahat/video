import sys, time; sys.path.insert(0,'.')
from core import *
from figures import *
from PIL import Image
bg = np.zeros((H,W,3),np.float32); bg[:] = rgb(0.75,0.68,0.62)
surf, ctx = new_surface()
def place(x,y,h,fn,*a,**k):
    ctx.save(); ctx.translate(x,y); ctx.scale(h,h); fn(ctx,*a,**k); ctx.restore()
place(150,950,700,draw_A_back,1.0,0.7)
place(700,450,600,draw_A_profile,1.0,0.7,0.0)
place(1250,450,600,draw_A_profile,1.0,0.7,1.0)
ctx.save(); ctx.translate(1650,300); draw_hand(ctx,0.1,0.0,1.0,scale=350); ctx.restore()
ctx.save(); ctx.translate(1650,750); draw_hand(ctx,1.0,0.0,1.0,scale=350); ctx.restore()
pm,a = surface_to_np(surf)
pm = light_layer(pm,a,(1,-0.3),4*S,rgb(1.0,0.72,0.42),1.2)
img = over_pm(bg,pm,a)
out = post(img,0,{})
Image.fromarray(out).save('tests/chars_%d.png'%int(time.time()))
