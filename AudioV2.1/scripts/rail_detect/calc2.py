import math, itertools
from calc import *
import calc
E192=[1.00,1.01,1.02,1.04,1.05,1.06,1.07,1.09,1.10,1.11,1.13,1.14,1.15,1.17,1.18,1.20,1.21,1.23,1.24,1.26,1.27,1.29,1.30,1.32,1.33,1.35,1.37,1.38,1.40,1.42,1.43,1.45,1.47,1.49,1.50,1.52,1.54,1.56,1.58,1.60,1.62,1.64,1.65,1.67,1.69,1.72,1.74,1.76,1.78,1.80,1.82,1.84,1.87,1.89,1.91,1.93,1.96,1.98,2.00,2.03,2.05,2.08,2.10,2.13,2.15,2.18,2.21,2.23,2.26,2.29,2.32,2.34,2.37,2.40,2.43,2.46,2.49,2.52,2.55,2.58,2.61,2.64,2.67,2.71,2.74,2.77,2.80,2.84,2.87,2.91,2.94,2.98,3.01,3.05,3.09,3.12,3.16,3.20,3.24,3.28,3.32,3.36,3.40,3.44,3.48,3.52,3.57,3.61,3.65,3.70,3.74,3.79,3.83,3.88,3.92,3.97,4.02,4.07,4.12,4.17,4.22,4.27,4.32,4.37,4.42,4.48,4.53,4.59,4.64,4.70,4.75,4.81,4.87,4.93,4.99,5.05,5.11,5.17,5.23,5.30,5.36,5.42,5.49,5.56,5.62,5.69,5.76,5.83,5.90,5.97,6.04,6.12,6.19,6.26,6.34,6.42,6.49,6.57,6.65,6.73,6.81,6.90,6.98,7.06,7.15,7.23,7.32,7.41,7.50,7.59,7.68,7.77,7.87,7.96,8.06,8.16,8.25,8.35,8.45,8.56,8.66,8.76,8.87,8.98,9.09,9.20,9.31,9.42,9.53,9.65,9.76,9.88]
def e192(x):
    d=10**math.floor(math.log10(x)); m=x/d
    return min(E192+[10.0],key=lambda v:abs(v-m))*d

def corners_pos_mixed(R, tols):
    R1,R2,R3=R; fall=[];rise=[]
    for ss in itertools.product((-1,1),repeat=3):
        r=[x*(1+s*t) for x,s,t in zip(R,ss,tols)]
        for vm in (VITm_A[0],VITm_A[2]):
          for vp in (VITp_A[0],VITp_A[2]):
            for vh in (VCC_RANGE[0]-0.1,VCC_RANGE[2]):
              for vl in (0,0.1):
                for ib in (-IIN,IIN):
                  f,rr=pos_thresholds(*r,vm,vp,vh,vl,ib); fall.append(f); rise.append(rr)
    return (min(fall),max(fall)),(min(rise),max(rise))
def corners_neg_mixed(R, tols, vrt):
    fall=[];rise=[]
    for ss in itertools.product((-1,1),repeat=4):
        r=[x*(1+s*t) for x,s,t in zip(R,ss,tols)]
        for vref in (2.5-vrt,2.5+vrt):
          for vp in (VITp_B[0],VITp_B[2]):
            for vm in (VITm_B[0],VITm_B[2]):
              for vh in (VCC_RANGE[0]-0.1,VCC_RANGE[2]):
                for vl in (0,0.1):
                  for ib in (-IIN,IIN):
                    f,rr=neg_thresholds(*r,vref,vp,vm,vh,vl,ib); fall.append(f); rise.append(rr)
    return (min(fall),max(fall)),(min(rise),max(rise))

Rp=tuple(e192(x) for x in design_pos())
Rn=tuple(e192(x) for x in design_neg())
print("pos E192",["%.4g"%x for x in Rp], "nominal fall/rise %.3f/%.3f"%pos_thresholds(*Rp,VITm_A[1],VITp_A[1],3.3,0,0))
print("neg E192",["%.4g"%x for x in Rn], "nominal fall/rise %.3f/%.3f"%neg_thresholds(*Rn,2.5,VITp_B[1],VITm_B[1],3.3,0,0))
print("node at -16.5 good (VREF-21mV): %.3f V"%node_neg(Rn,2.479,-16.5,0))
T1=0.001+25e-6*35; T2=0.01+100e-6*35
for name,tp,tn in (("all 0.1%%+TCR",(T1,T1,T1),(T1,T1,T1,T1)),
                   ("divider 0.1%%, hyst R (R3,Rh) 1%%",(T1,T1,T2),(T1,T1,T1,T2)),
                   ("all 1%%+TCR",(T2,T2,T2),(T2,T2,T2,T2))):
    pf,pr=corners_pos_mixed(Rp,tp); nf,nr=corners_neg_mixed(Rn,tn,0.021)
    print("%-34s +fall %.3f..%.3f +rise %.3f..%.3f | -fall %.3f..%.3f -rise %.3f..%.3f"%(name,*pf,*pr,*nf,*nr))

# error budget (falling thresholds), one contributor at a time around nominal
def pf(R1=Rp[0],R2=Rp[1],R3=Rp[2],vm=VITm_A[1],vh=3.3,ib=0): return pos_thresholds(R1,R2,R3,vm,0.4055,vh,0,ib)[0]
base=pf()
print("\n+ fall budget (nominal %.3f):"%base)
print("  VIT-(INA) 397..403 mV : %+.3f / %+.3f"%(pf(vm=0.397)-base,pf(vm=0.403)-base))
print("  VH 2.8..3.4 V         : %+.3f / %+.3f"%(pf(vh=2.8)-base,pf(vh=3.4)-base))
print("  IIN +-25 nA           : %+.3f / %+.3f"%(pf(ib=-25e-9)-base,pf(ib=25e-9)-base))
for t,n in ((T1,"0.1%+TCR"),(T2,"1%+TCR")):
    d=[pf(R1=Rp[0]*(1+t))-base,pf(R2=Rp[1]*(1+t))-base,pf(R3=Rp[2]*(1+t))-base]
    print("  R1/R2/R3 +%s     : %+.3f %+.3f %+.3f"%(n,*d))
def nf(Rt=Rn[0],Rb=Rn[1],Rg=Rn[2],Rh=Rn[3],vref=2.5,vp=0.400,ib=0): return neg_thresholds(Rt,Rb,Rg,Rh,vref,vp,0.3945,3.3,0,ib)[0]
base=nf()
print("\n- fall budget (nominal %.3f):"%base)
print("  VIT+(INB) 397..403 mV : %+.3f / %+.3f"%(nf(vp=0.397)-base,nf(vp=0.403)-base))
print("  VREF +-21 mV (B)      : %+.3f / %+.3f"%(nf(vref=2.479)-base,nf(vref=2.521)-base))
print("  VREF +-5 mV (B,25C)   : %+.3f / %+.3f"%(nf(vref=2.495)-base,nf(vref=2.505)-base))
print("  IIN +-25 nA           : %+.3f / %+.3f"%(nf(ib=-25e-9)-base,nf(ib=25e-9)-base))
for t,n in ((T1,"0.1%+TCR"),(T2,"1%+TCR")):
    d=[nf(Rt=Rn[0]*(1+t))-base,nf(Rb=Rn[1]*(1+t))-base,nf(Rg=Rn[2]*(1+t))-base,nf(Rh=Rn[3]*(1+t))-base]
    print("  Rt/Rb/Rg/Rh +%s  : %+.3f %+.3f %+.3f %+.3f"%(n,*d))
# LM4040 current budget
print("\nLM4040 feed: IRMIN 65uA(full T) + divider %.1f uA"%((2.5-0.4)/Rn[0]*1e6))
for vcc in (2.9,3.3):
    for vf in (0.24,0.32):
        R=(vcc-vf-2.5)/(65e-6+(2.5-0.4)/Rn[0])
        print("  from 3V3=%.2f via BAT54 VF %.2f: R <= %.1f k"%(vcc,vf,R/1e3))
for vp in (10.0,13.6,15.9):
    R=(vp-0.32-2.5)/(65e-6+(2.5-0.4)/Rn[0])
    print("  from V+=%.1f: R <= %.0f k"%(vp,R/1e3))
