import sys, time; sys.path.insert(0,'.')
from core import *
from figures import *
from PIL import Image
bg = np.zeros((H,W,3),np.float32); bg[:] = rgb(0.75,0.68,0.62)
surf, ctx = new_surface()
def place(x,y,h,fn,*a,**k):
    ctx.save(); ctx.translate(x,y); ctx.scale(h,h); fn(ctx,*a,**k); ctx.restore()
place(200,900,700,draw_A_back,1.0,0.7)
place(520,900,650,draw_B_back,1.0,0.7)
place(800,900,700,draw_side_figure,'A',1.0,0.7)
place(1000,900,650,draw_side_figure,'B',1.0,0.7)
place(1400,350,400,draw_A_profile,1.0,0.7,0.0)
place(1750,750,500,draw_hand,0.0,0.0,1.0)
place(1750,850,500,draw_hand,1.0,0.0,1.0)
pm,a = surface_to_np(surf)
pm = light_layer(pm,a,(0.4,-1),4*S,rgb(1.0,0.72,0.42),1.2)
img = over_pm(bg,pm,a)
out = post(img,0,{})
Image.fromarray(out).save('tests/chars_%d.png'%int(time.time()))
