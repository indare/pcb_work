from calc2 import *
T1=0.001+25e-6*35; T2=0.01+100e-6*35
for vf,vr in ((10.5,12.0),(10.8,12.2),(11.0,12.3)):
    Rp=tuple(e192(x) for x in design_pos(vrise=vr,vfall=vf))
    Rn=tuple(e192(x) for x in design_neg(vrise=-vr,vfall=-vf))
    for name,t in (("0.1%+TCR",T1),("1%+TCR",T2)):
        a,b=corners_pos_mixed(Rp,(t,t,t)); c,d=corners_neg_mixed(Rn,(t,t,t,t),0.021)
        print("nom fall %.1f rise %.1f R %-9s: +fall %.2f..%.2f +rise %.2f..%.2f | -fall %.2f..%.2f -rise %.2f..%.2f  Rp=%s Rn=%s"%(vf,vr,name,*a,*b,-c[1],-c[0],-d[1],-d[0],["%.3g"%x for x in Rp],["%.3g"%x for x in Rn]))
