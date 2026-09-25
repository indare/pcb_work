# Pico ratiometric scheme: threshold error at 10.5 V for 3V3 error e, plus other terms
V=10.5
for e in (0.01,0.02,0.03):
    print("3V3 %+.0f%% uncalibrated -> +/- threshold error %.3f V (both rails, ratiometric offset)"%(e*100, V*e))
# with LM4040B ratio (+-0.85% full T) -> 
print("LM4040B ratio-cal: %.3f V"%(V*0.0085))
# ADC LSB referred to rail: divider 15.9 V -> 3.0 V max
k=3.0/16.5
print("1 LSB (3.3/4096) at rail: %.1f mV; ENOB 9 noise ~ %.0f mV (1/2^9 FS)"%(3.3/4096/k*1e3, 3.3/512/k*1e3))
# diode-OR VF uncertainty (Si small signal, 20..60 C, ~2 mV/K) and part spread +-50 mV
print("diode VF spread +-0.05 V + TC 2mV/K*40K/2 = +-%.2f V at rail"%(0.05+0.002*20))
# sudden-loss timing: lo corner C=4.6uF
C=4.6e-6
for I,lab in ((23.9e-3,"EN not yet cut"),(2.9e-3,"EN cut")):
    print("dV/dt %s: %.2f V/ms -> 10.5->9.45 V in %.2f ms"%(lab,I/C*1e-3,C*1.05/I*1e3))
# I2C 100 kbit/s single MCP23017 register write: S+addr+reg+data+P ~ 29 bit
t=29/100e3
print("I2C write %.2f ms; waiting for one in-flight 8-byte transaction ~%.2f ms"%(t*1e3,(9*10)/100e3*1e3))
# TPS3808 delay with CT C0G 5%
for ct in (2.2,2.7):
    td=ct/175+0.5e-3
    print("CT %.1f nF: typ %.1f ms, +-40%% & C +-5%%: %.1f..%.1f ms"%(ct,td*1e3,(ct*0.95/175+0.5e-3)*0.6e3,(ct*1.05/175+0.5e-3)*1.4e3))
# LVC1G123 with K 0.97(typ fig)..1.1, R1%, C5%
print("LVC1G123 100k/0.33u: %.1f..%.1f ms"%(0.97*99e3*0.33e-6*0.95*1e3,1.1*101e3*0.33e-6*1.05*1e3))
# 22 ohm on NO side: pole-pole short
I=31.8/44; print("pole-pole short via 2x22: %.2f A, %.1f W each; RS6 OLP 0.3 A -> %.1f W each"%(I,I*I*22,0.09*22))
