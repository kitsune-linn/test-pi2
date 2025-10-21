import cmath
import math
magnitude=400
radian=math.acos(0.95)
#degree=math.degrees(radian)
Is=cmath.rect(magnitude, radian)
Is=Is.conjugate()
Vsp=345000/(3**0.5)
Vs=345000
Y=0.00000422j*130
Z=(0.036+0.3j)*130
A=1+Y*Z/2
B=-Z
C=-Y*(1+Y*Z/4)
D=1+Y*Z/2
Vrp=A*Vsp+B*Is
Ir=C*Vsp+D*Is
Vr=Vrp*(3**0.5)
Sr=3*Vrp*(Ir.conjugate())
Ss=3*Vsp*(Is.conjugate())
eta=100*(Sr.real/Ss.real)
Vr=abs(Vr)
Vm=100*(Vs-Vr)/Vr
theta=cmath.phase(Ir)
pf=math.cos(theta)
print("受電端電壓=", "{:.3f}".format(Vr))
print("受電端電流=", "{:.3f}".format(abs(Ir)), ",", "pf=", "{:.6f}".format(pf)) 
print("功率=", "{:.3f}".format(eta), "%")
print("電壓調整率=", "{:.3f}".format(Vm), "%")