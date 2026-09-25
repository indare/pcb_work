from calc2 import *
T1=0.001+25e-6*35; T2=0.01+100e-6*35
Rp=tuple(e192(x) for x in design_pos(R1=499e3))
Rn=tuple(e192(x) for x in design_neg(Rb=499e3))
print("scaled pos",["%.4g"%x for x in Rp],"nom fall/rise %.3f/%.3f"%pos_thresholds(*Rp,VITm_A[1],VITp_A[1],3.3,0,0))
print("scaled neg",["%.4g"%x for x in Rn],"nom fall/rise %.3f/%.3f"%neg_thresholds(*Rn,2.5,VITp_B[1],VITm_B[1],3.3,0,0))
a,b=corners_pos_mixed(Rp,(T1,T1,T2)); c,d=corners_neg_mixed(Rn,(T1,T1,T1,T2),0.021)
print("div 0.1%%+TCR, hyst 1%%+TCR: +fall %.3f..%.3f +rise %.3f..%.3f | -fall %.3f..%.3f -rise %.3f..%.3f"%(*a,*b,-c[1],-c[0],-d[1],-d[0]))
a,b=corners_pos_mixed(Rp,(T2,T2,T2)); c,d=corners_neg_mixed(Rn,(T2,T2,T2,T2),0.021)
print("all 1%%+TCR:               +fall %.3f..%.3f +rise %.3f..%.3f | -fall %.3f..%.3f -rise %.3f..%.3f"%(*a,*b,-c[1],-c[0],-d[1],-d[0]))
print("node B @-16.5 good, VREF-21mV: %.3f V; @0 V not good: %.3f V"%(node_neg(Rn,2.479,-16.5,0),node_neg(Rn,2.5,0,3.3)))
print("node A @15.9 V good FB 3.4: %.3f V"%((15.9/Rp[0]+3.4/Rp[2])/(1/Rp[0]+1/Rp[1]+1/Rp[2])))
print("I from V+ %.1f uA, from V- %.1f uA, from VREF %.1f uA"%((15-0.4)/Rp[0]*1e6,(15+0.4)/Rn[1]*1e6,(2.5-0.4)/Rn[0]*1e6))
# LM4040 feed from stack +15 via 82k
for vp in (10.0,13.6,14.25,15.9):
    print("  LM4040 IR with 82k from stack +%.2f: %.0f uA (divider draw %.1f)"%(vp,((vp-2.5)/82e3-(2.5-0.4)/Rn[0])*1e6,(2.5-0.4)/Rn[0]*1e6))
# condition for node >= -0.3 V when VREF collapses
Rt,Rb,Rg,Rh=Rn; G=1/Rt+1/Rb+1/Rg+1/Rh
print("  node >= -0.3 V needs |V-| <= VREF*Rb/Rt + 0.3*G*Rb = %.2f*VREF + %.2f"%(Rb/Rt,0.3*G*Rb))
