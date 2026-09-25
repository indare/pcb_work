import itertools, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from calc2 import *
Rp=(499e3,17.8e3,1.23e6); Rn=(71.5e3,499e3,54.9e3,1.17e6)
T=lambda p,tcr: p+tcr*35
def per_unit(Rp,Rn,tp,tn):
    hp=[];hn=[]
    for ss in itertools.product((-1,1),repeat=3):
        r=[x*(1+s*t) for x,s,t in zip(Rp,ss,tp)]
        for vm,vp in ((0.397,0.400),(0.403,0.403+0.002),(0.397,0.397+0.002)):  # hysteresis min 2 mV
          if vp<0.400: vp=0.400
          for vh in (2.8,3.4):
            for vl in (0,0.1):
              for ib in (-25e-9,25e-9):
                f,rr=pos_thresholds(*r,vm,vp,vh,vl,ib); hp.append(rr-f)
    for ss in itertools.product((-1,1),repeat=4):
        r=[x*(1+s*t) for x,s,t in zip(Rn,ss,tn)]
        for vref in (2.479,2.521):
          for vp,vm in ((0.397,0.395),(0.403,0.400),(0.400,0.398)):
            for vh in (2.8,3.4):
              for vl in (0,0.1):
                for ib in (-25e-9,25e-9):
                  f,rr=neg_thresholds(*r,vref,vp,vm,vh,vl,ib); hn.append(-(rr-f))
    return min(hp),max(hp),min(hn),max(hn)
print("per-unit hysteresis (rise-fall, same parts):")
for n,tp,tn in (("0.1%div/1%hyst",(T(.001,25e-6),)*2+(T(.01,1e-4),),(T(.001,25e-6),)*3+(T(.01,1e-4),)),
                ("all 1%",(T(.01,1e-4),)*3,(T(.01,1e-4),)*4)):
    print(" ",n,"+ %.3f..%.3f V  - %.3f..%.3f V"%per_unit(Rp,Rn,tp,tn))
# 0.5% variant
t5=T(.005,50e-6); t1=T(.01,1e-4)
a,b=corners_pos_mixed(Rp,(t5,t5,t1)); c,d=corners_neg_mixed(Rn,(t5,t5,t5,t1),0.021)
print("0.5%%+50ppm div, 1%% hyst: +fall %.3f..%.3f +rise %.3f..%.3f | -fall %.3f..%.3f -rise %.3f..%.3f"%(*a,*b,-c[1],-c[0],-d[1],-d[0]))
# LM4040 current with 68k
G=sum(1/x for x in Rn)
for vs in (8.9,10.0,13.6,15.9):
    for node in (0.046,0.4,1.08):
        pass
    idiv_max=(2.5-0.0)/Rn[0]
    print("stack %.1f V: I(68k)=%.0f uA, LM4040 IR min=%.0f uA (divider draw <= %.1f uA)"%(vs,(vs-2.5)/68e3*1e6,((vs-2.521)/68e3-(2.521-0.03)/Rn[0])*1e6,(2.521-0.03)/Rn[0]*1e6))
# INB node with VREF collapsed
for vref in (0,1.0,1.61,2.5):
  for vneg in (-15.0,-15.9,-16.5):
    for fb in (0,3.3):
      nd=(vref/Rn[0]+vneg/Rn[1]+fb/Rn[3])/G
      if vneg==-16.5 or vref==0: print("VREF %.2f V- %.1f FB %.1f -> node %.3f V (Thevenin %.1f k)"%(vref,vneg,fb,nd,1/G/1e3))
# BAT54 clamp error, scaled x0.1
for scale,ir in ((1,2e-6),(1,0.2e-6),(0.1,2e-6),(0.1,0.2e-6)):
    Rth=1/G*scale
    print("scale %.1f, IR %.1f uA: node err %.1f mV -> threshold err %.3f V"%(scale,ir*1e6,ir*Rth*1e3,ir*Rth*G*Rn[1]))
