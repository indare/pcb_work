#!/usr/bin/env python3
"""Rail detector threshold bands (v2.1 daughter). All DS numbers are cited in rail_detect.md.

Topology (recommended):
  + rail : R1 (V+ -> nA), R2 (nA -> GND), R3 (nA -> FB_P).   FB_P = buffered "good" (VH when good, VL when not)
           TPS3701 INA: OUTA low when nA < VIT-(INA); released when nA > VIT+(INA)
  - rail : Rt (VREF -> nB), Rb (nB -> V-), Rg (nB -> GND), Rh (nB -> FB_N).  FB_N = inverted "good" (VH when NOT good, VL when good)
           TPS3701 INB: OUTB low when nB > VIT+(INB); released when nB < VIT-(INB)
"""
import itertools

E96 = [1.00,1.02,1.05,1.07,1.10,1.13,1.15,1.18,1.21,1.24,1.27,1.30,1.33,1.37,1.40,1.43,1.47,1.50,1.54,1.58,1.62,1.65,1.69,1.74,1.78,1.82,1.87,1.91,1.96,2.00,2.05,2.10,2.15,2.21,2.26,2.32,2.37,2.43,2.49,2.55,2.61,2.67,2.74,2.80,2.87,2.94,3.01,3.09,3.16,3.24,3.32,3.40,3.48,3.57,3.65,3.74,3.83,3.92,4.02,4.12,4.22,4.32,4.42,4.53,4.64,4.75,4.87,4.99,5.11,5.23,5.36,5.49,5.62,5.76,5.90,6.04,6.19,6.34,6.49,6.65,6.81,6.98,7.15,7.32,7.50,7.68,7.87,8.06,8.25,8.45,8.66,8.87,9.09,9.31,9.53,9.76]

def e96(x):
    import math
    d = 10 ** math.floor(math.log10(x))
    m = x / d
    best = min(E96 + [10.0], key=lambda v: abs(v - m))
    return best * d

# ---------------- DS values (TPS3701, SBVS240C p5) ----------------
VITm_A = (0.397, 0.400, 0.403)   # INA negative-going (fault) threshold  min/typ/max
VITp_A = (0.400, 0.4055, 0.413)  # INA positive-going (release)
VITp_B = (0.397, 0.400, 0.403)   # INB positive-going (fault)
VITm_B = (0.387, 0.3945, 0.400)  # INB negative-going (release)
IIN = 25e-9                      # |IIN| max at 6.5 V (15 nA at 0.1 V) -> use 25 nA both
# TPS3700 (SBVS187G p6) for comparison: VIT+ 396/400/404 (both), VIT- 387/394.5/400 (both)
T3700 = dict(VITm_A=(0.387,0.3945,0.400), VITp_A=(0.396,0.400,0.404),
             VITp_B=(0.396,0.400,0.404), VITm_B=(0.387,0.3945,0.400))
# LM4040-N 2.5 V, B grade (SNOS633N 5.8): +-5 mV @25C, +-21 mV over -40..85C; C grade +-12 / +-29 mV
VREF_NOM = 2.5
# CMOS feedback source levels (SN74LVC1G14, VOH >= VCC-0.1, VOL <= 0.1 at 100 uA)
# VCC (Pico 3V3) range is NOT in any DS we hold -> assumption: 2.90 .. 3.40 V
#   lower end = TPS3808G30 rising threshold worst (2.79*1.015 + 2.5%*2.79 = 2.90 V): below it RGd is held low anyway
VCC_RANGE = (2.90, 3.30, 3.40)

def pos_thresholds(R1, R2, R3, vitm, vitp, vh, vl, ib):
    g = 1/R1 + 1/R2 + 1/R3
    # falling (good -> not good): FB = vh
    vf = R1 * (vitm * g - vh / R3) + ib * R1    # ib into node (+) lowers node -> sign handled by corners
    # rising (not good -> good): FB = vl
    vr = R1 * (vitp * g - vl / R3) + ib * R1
    return vf, vr

def neg_thresholds(Rt, Rb, Rg, Rh, vref, vitp, vitm, vh, vl, ib):
    gt, gb, gg, gh = 1/Rt, 1/Rb, 1/Rg, 1/Rh
    G = gt + gb + gg + gh
    # falling magnitude (good -> not good): node > VIT+(INB), FB_N = vl (good state)
    vf = (vitp * G - vref * gt - vl * gh + ib) / gb
    # rising magnitude (not good -> good): node < VIT-(INB), FB_N = vh
    vr = (vitm * G - vref * gt - vh * gh + ib) / gb
    return vf, vr

def design_pos(vrise=12.0, vfall=10.5, vh=3.3, R1=1.0e6, part=None):
    vitp = (part or {}).get('VITp_A', VITp_A)[1]
    vitm = (part or {}).get('VITm_A', VITm_A)[1]
    s = vrise / vitp               # 1 + a + b
    b = (vitm * s - vfall) / vh
    a = s - 1 - b
    return R1, R1 / a, R1 / b

def design_neg(vrise=-12.0, vfall=-10.5, vh=3.3, vref=2.5, gt_over_gb=7.0, Rb=1.0e6, part=None):
    vitp = (part or {}).get('VITp_B', VITp_B)[1]
    vitm = (part or {}).get('VITm_B', VITm_B)[1]
    gb = 1 / Rb
    gt = gt_over_gb * gb
    G = (vref * gt + vfall * gb) / vitp          # from falling eq (vl=0)
    gh = (vitm * G - vref * gt - vrise * gb) / vh
    gg = G - gt - gb - gh
    return 1/gt, Rb, 1/gg, 1/gh

def corners_pos(R, tol, part=None, vref_unused=None):
    R1, R2, R3 = R
    p = part or {}
    vA_m = p.get('VITm_A', VITm_A); vA_p = p.get('VITp_A', VITp_A)
    fall, rise = [], []
    for s1, s2, s3 in itertools.product((-1, 1), repeat=3):
        r1, r2, r3 = R1*(1+s1*tol), R2*(1+s2*tol), R3*(1+s3*tol)
        for vm in (vA_m[0], vA_m[2]):
            for vp in (vA_p[0], vA_p[2]):
                for vh in (VCC_RANGE[0]-0.1, VCC_RANGE[2]):
                    for vl in (0.0, 0.1):
                        for ib in (-IIN, IIN):
                            f, r = pos_thresholds(r1, r2, r3, vm, vp, vh, vl, ib)
                            fall.append(f); rise.append(r)
    return (min(fall), max(fall)), (min(rise), max(rise))

def corners_neg(R, tol, vref_tol, part=None):
    Rt, Rb, Rg, Rh = R
    p = part or {}
    vB_p = p.get('VITp_B', VITp_B); vB_m = p.get('VITm_B', VITm_B)
    fall, rise = [], []
    for ss in itertools.product((-1, 1), repeat=4):
        rt, rb, rg, rh = [x*(1+s*tol) for x, s in zip(R, ss)]
        for vref in (VREF_NOM - vref_tol, VREF_NOM + vref_tol):
            for vp in (vB_p[0], vB_p[2]):
                for vm in (vB_m[0], vB_m[2]):
                    for vh in (VCC_RANGE[0]-0.1, VCC_RANGE[2]):
                        for vl in (0.0, 0.1):
                            for ib in (-IIN, IIN):
                                f, r = neg_thresholds(rt, rb, rg, rh, vref, vp, vm, vh, vl, ib)
                                fall.append(f); rise.append(r)
    return (min(fall), max(fall)), (min(rise), max(rise))

def node_neg(R, vref, vneg, fb):
    Rt, Rb, Rg, Rh = R
    gt, gb, gg, gh = 1/Rt, 1/Rb, 1/Rg, 1/Rh
    return (vref*gt + vneg*gb + fb*gh) / (gt+gb+gg+gh)

def main():
    print("=== ideal design (typ thresholds, VH=3.3 V, VREF=2.5 V) ===")
    Rp = design_pos()
    print("pos ideal R1,R2,R3 =", ["%.4g" % x for x in Rp])
    Rp_e = tuple(e96(x) for x in Rp)
    print("pos E96  R1,R2,R3 =", ["%.4g" % x for x in Rp_e])
    f, r = pos_thresholds(*Rp_e, VITm_A[1], VITp_A[1], 3.3, 0.0, 0.0)
    print("pos E96 nominal: fall %.3f V  rise %.3f V" % (f, r))
    Rn = design_neg()
    print("neg ideal Rt,Rb,Rg,Rh =", ["%.4g" % x for x in Rn])
    Rn_e = tuple(e96(x) for x in Rn)
    print("neg E96  Rt,Rb,Rg,Rh =", ["%.4g" % x for x in Rn_e])
    f, r = neg_thresholds(*Rn_e, 2.5, VITp_B[1], VITm_B[1], 3.3, 0.0, 0.0)
    print("neg E96 nominal: fall %.3f V  rise %.3f V" % (f, r))
    for v in (-15.0, -15.75, -16.5):
        print("  node B at V-=%.2f (good, FB_N=0): %.3f V" % (v, node_neg(Rn_e, 2.5 - 0.021, v, 0.0)))
    print("  node B at V-=0 (not good, FB_N=3.3): %.3f V" % node_neg(Rn_e, 2.5, 0.0, 3.3))
    # divider currents
    print("  I(R1) at 15 V: %.1f uA ; I(Rb) at -15 V: %.1f uA ; I(Rt) from VREF: %.1f uA" % (
        (15-0.4)/Rp_e[0]*1e6, (15+0.4)/Rn_e[1]*1e6, (2.5-0.4)/Rn_e[0]*1e6))
    print("  Thevenin pos node %.1f k, neg node %.1f k" % (
        1/(1/Rp_e[0]+1/Rp_e[1]+1/Rp_e[2])/1e3, 1/sum(1/x for x in Rn_e)/1e3))

    print()
    print("=== worst-case bands (TPS3701 / TLV6710) ===")
    print("assumed VCC (feedback VH) %.2f..%.2f V, VOL 0..0.1 V, |IIN| 25 nA" % (VCC_RANGE[0]-0.1, VCC_RANGE[2]))
    rows = []
    for tol_name, tol in (("0.1%", 0.001), ("0.1%+TCR25ppm*35K", 0.001+25e-6*35), ("1%", 0.01), ("1%+TCR100ppm*35K", 0.01+100e-6*35)):
        pf, pr = corners_pos(Rp_e, tol)
        for vr_name, vrt in (("LM4040B full-T +-21mV", 0.021), ("LM4040C full-T +-29mV", 0.029)):
            nf, nr = corners_neg(Rn_e, tol, vrt)
            rows.append((tol_name, vr_name, pf, pr, nf, nr))
            print("R %-18s | +fall %.3f..%.3f  +rise %.3f..%.3f | %s: -fall %.3f..%.3f  -rise %.3f..%.3f" % (
                tol_name, pf[0], pf[1], pr[0], pr[1], vr_name, nf[0], nf[1], nr[0], nr[1]))

    print()
    print("=== same resistors with TPS3700 / TLV6700 thresholds (redesigned for its typ) ===")
    Rp7 = tuple(e96(x) for x in design_pos(part=T3700))
    Rn7 = tuple(e96(x) for x in design_neg(part=T3700))
    print("pos E96", ["%.4g" % x for x in Rp7], " neg E96", ["%.4g" % x for x in Rn7])
    for tol_name, tol in (("0.1%", 0.001), ("1%", 0.01)):
        pf, pr = corners_pos(Rp7, tol, part=T3700)
        nf, nr = corners_neg(Rn7, tol, 0.021, part=T3700)
        print("R %-5s | +fall %.3f..%.3f  +rise %.3f..%.3f | -fall %.3f..%.3f  -rise %.3f..%.3f" % (
            tol_name, pf[0], pf[1], pr[0], pr[1], nf[0], nf[1], nr[0], nr[1]))

    print()
    print("=== negative divider referenced to raw 3V3 (no LM4040), 2 resistors + Rh, for comparison ===")
    # node = (3.3*gt + V-*gb + fb*gh)/G ; choose gt so node>=0 at -16.5 V -> gt >= 5 gb
    for v33_tol in (0.01, 0.03, 0.05):
        Rn3 = tuple(e96(x) for x in design_neg(vref=3.3, gt_over_gb=5.3))
        global VREF_NOM
        old = VREF_NOM; VREF_NOM = 3.3
        nf, nr = corners_neg(Rn3, 0.001, 3.3*v33_tol)
        VREF_NOM = old
        print("3V3 +-%d%%, R 0.1%%: -fall %.3f..%.3f  -rise %.3f..%.3f  (R=%s)" % (
            v33_tol*100, nf[0], nf[1], nr[0], nr[1], ["%.3g" % x for x in Rn3]))

    print()
    print("=== sensitivities (neg channel, E96 design) ===")
    Rt, Rb, Rg, Rh = Rn_e
    gt, gb, gg, gh = 1/Rt, 1/Rb, 1/Rg, 1/Rh
    G = gt+gb+gg+gh
    print("dVfall/dVIT+ = G/gb = %.2f ; dVfall/dVREF = -gt/gb = %.2f ; dVrise/dVH = -gh/gb = %.3f" % (G/gb, -gt/gb, -gh/gb))
    R1, R2, R3 = Rp_e
    s = 1 + R1/R2 + R1/R3
    print("pos: dV/dVIT = %.2f ; dVfall/dVH = -R1/R3 = %.3f" % (s, -R1/R3))

    print()
    print("=== time from falling threshold to 9.45 V (board rail after 22 ohm, contact opened) ===")
    for C in (4.6e-6, 22.7e-6, 40.3e-6):
        for I in (23.9e-3, 2.9e-3):
            for vf in (10.2, 10.5, 12.0, 13.0):
                t = C * (vf - 9.45) / I
                print("C %5.1f uF I %5.1f mA Vfall %5.2f -> %6.2f ms" % (C*1e6, I*1e3, vf, t*1e3))
    print()
    print("=== TPS3808 CT for delay: tD(s) = CT(nF)/175 + 0.5e-3 ===")
    for ct in (1.5, 2.2, 2.7, 3.3):
        td = ct/175 + 0.5e-3
        print("CT %.1f nF -> typ %.1f ms ; x0.6..x1.4 (spread of DS CT rows) %.1f..%.1f ms" % (ct, td*1e3, td*0.6e3, td*1.4e3))
    print()
    print("=== LVC1G123 pulse: tw ~ K*Rext*Cext, K 1.0..1.1 (DS table 10k/0.1uF: 1.0..1.1 ms) ===")
    for R, C in ((100e3, 0.33e-6), (100e3, 0.47e-6), (200e3, 0.22e-6)):
        for ctol in (0.05, 0.10):
            lo = 1.0*R*(1-0.01)*C*(1-ctol)
            hi = 1.1*R*(1+0.01)*C*(1+ctol)
            print("R %3.0fk C %.2fuF ctol %2d%% -> %.1f..%.1f ms (nom %.1f)" % (R/1e3, C*1e6, ctol*100, lo*1e3, hi*1e3, R*C*1e3))
    print()
    print("=== coil current worst (reviews): 5.25 V / (125 ohm * 0.9) ===")
    i = 5.25/(125*0.9)
    print("per coil %.1f mA; auto reset (2 audio coils) %.1f mA; 4 boards simultaneously %.1f mA" % (i*1e3, 2*i*1e3, 8*i*1e3))

if __name__ == "__main__":
    main()
