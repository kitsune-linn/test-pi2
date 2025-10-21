import cmath
import math
magnitude=270000000
radian=math.acos(0.8)
Sr=cmath.rect(magnitude, radian)
Vrp=325000/(3**0.5)
Vr=325000
Ir=Sr/(3*Vrp)
Ir=Ir.conjugate()
Y=2*60*math.pi*0.0000000112j*130
Z=(0.036+2*60*math.pi*0.0008j)*130
A=1+Y*Z/2
B=Z
C=Y*(1+Y*Z/4)
D=1+Y*Z/2
Vsp=A*Vrp+B*Ir
Is=C*Vrp+D*Ir
Vs=Vsp*(3**0.5)
Sr=3*Vrp*(Ir.conjugate())
Ss=3*Vsp*(Is.conjugate())
eta=100*(Sr.real/Ss.real)
Vs=abs(Vs)
Vm=100*(Vs-Vr)/Vr
theta=cmath.phase(Is)
pf=math.cos(theta)
print("送電端電壓=", "{:.3f}".format(Vs))
print("送電端電流=", "{:.3f}".format(abs(Is)), "pf=", "{:.6f}".format(pf))
print("功率=", "{:.3f}".format(eta), "%")
print("電壓調整率=", "{:.3f}".format(Vm), "%")