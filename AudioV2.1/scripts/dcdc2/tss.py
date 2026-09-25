base=101.8
cases={("ii",1):(61.8,0.5),("ii",2):(74.1,1.0),("ii",4):(98.8,1.9),("i",1):(61.8,21.5),("i",2):(63.0,42.0),("i",4):(65.5,82.9),
       ("i-direct",1):(50.8,20.5),("i-direct",2):(52.1,41.0),("i-direct",4):(54.8,81.9)}
conv={"RS6":200,"TMR9":300,"TMR10WI":333,"REC20K":667}
for k,(C,bl) in cases.items():
    s=f"{k[0]:9s} n={k[1]} "
    for c,ia in conv.items():
        for lim in (0.8,1.0):
            room=lim*ia-base-bl
            s+=f"{c}@{int(lim*100)}%: "+(f"{C*15/room:5.1f}ms " if room>0 else "  不可  ")
    print(s)
# socket short
for c,ia in conv.items():
    lo=80.7+220; hi=101.8+500; hic=hi+25.5
    print(c, f"{100*lo/ia:.0f}-{100*hi/ia:.0f}% (HP clip {100*hic/ia:.0f}%)")
# preloads to reach 25% (and 10% REC20K) on -15V
m={"ii typ":52.5,"ii typ n4":53.5,"ii light":47.2,"i n2 typ":58.8,"i n4 typ":71.5,"i n4 light":57.6,"noboard typ":45.7}
for c,ia in conv.items():
    for tgt in ((0.25,0.10) if c=="REC20K" else (0.25,)):
        for k,v in m.items():
            need=tgt*ia-v
            if need>0: print(c,int(tgt*100),k,f"need {need:.1f} mA -> {15/need:.2f} kΩ {15*need/1000:.2f} W")
            else: print(c,int(tgt*100),k,"ok")
