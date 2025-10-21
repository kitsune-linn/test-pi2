import cmath
import math

# Given parameters
magnitude = 400
radian = math.acos(0.95)
Is = cmath.rect(magnitude, radian).conjugate()
Vsp = 345000 / (3**0.5)
Vs = 345000
Y = 0.00000422j * 130
Z = (0.036 + 0.3j) * 130

# Correct ABCD parameters
A = 1 + Y * Z / 2
B = -Z
C = -Y * (1 + Y * Z / 4)
D = 1 + Y * Z / 2

# Print ABCD parameters for debugging
print("A =", A)
print("B =", B)
print("C =", C)
print("D =", D)

# Calculating Vrp and Ir
Vrp = A * Vsp + B * Is
Ir = C * Vsp + D * Is

# Print intermediate values for debugging
print("Vsp =", Vsp)
print("Is =", Is)
print("Vrp =", Vrp)
print("Ir (before magnitude calculation) =", Ir)

# Converting Vrp to line-to-line voltage Vr
Vr = Vrp * (3**0.5)

# Power calculations
Sr = 3 * Vrp * (Ir.conjugate())
Ss = 3 * Vsp * (Is.conjugate())

# Print power calculations for debugging
print("Sr =", Sr)
print("Ss =", Ss)

# Efficiency calculation
eta = 100 * (Sr.real / Ss.real)

# Print efficiency calculation for debugging
print("Efficiency (eta) =", eta)

# Voltage regulation calculation
Vr_magnitude = abs(Vr)
Vm = 100 * (Vs - Vr_magnitude) / Vr_magnitude

# Output results
print("受電端電壓 =", "{:.2f}".format(Vr_magnitude))
print("受電端電流 =", "{:.2f}".format(abs(Ir)))
print("功率 =", "{:.2f}".format(eta), "%")
print("電壓調整率 =", "{:.2f}".format(Vm), "%")