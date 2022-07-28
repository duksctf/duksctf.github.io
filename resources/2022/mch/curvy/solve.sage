from sympy import discrete_log

def SmartAttack(P,Q,p):
    E = P.curve()
    Eqp = EllipticCurve(Qp(p, 2), [ ZZ(t) + randint(0,p)*p for t in E.a_invariants() ])

    P_Qps = Eqp.lift_x(ZZ(P.xy()[0]), all=True)
    for P_Qp in P_Qps:
        if GF(p)(P_Qp.xy()[1]) == P.xy()[1]:
            break

    Q_Qps = Eqp.lift_x(ZZ(Q.xy()[0]), all=True)
    for Q_Qp in Q_Qps:
        if GF(p)(Q_Qp.xy()[1]) == Q.xy()[1]:
            break

    p_times_P = p*P_Qp
    p_times_Q = p*Q_Qp

    x_P,y_P = p_times_P.xy()
    x_Q,y_Q = p_times_Q.xy()

    phi_P = -(x_P/y_P)
    phi_Q = -(x_Q/y_Q)
    k = phi_Q/phi_P
    return ZZ(k)

# Point from the curve
x1 = 1
x2 = 10246385595908412093322394614482812
x3 = 39363994084598900187252501570838981
x4 = 21407548750102312410625794491436912
x5 = 32685866221368843545964725685301333

# From the binary search
p = 0xa745e606518ab2a7a4c4cbd0243ff
F = GF(p)
R = Zmod(p)

# Recover a and b
var('a,b')
eqn = [ 4*(a+b+x1)*(x2+2) == (3+a)^2, 
        4*(x2^3 + a*x2+b)*(x4+2*x2) == (3*x2^2+a)^2]
s = solve(eqn,a,b)

a = eval(re.sub("([0-9]+)", r"F(\1)",str(s[0][0].right())))
b = eval(re.sub("([0-9]+)", r"F(\1)",str(s[0][1].right())))

#a = 49850651047495986645822557378918223
#b = 21049438014429831351540675253466229

E = EllipticCurve(GF(p),[a,b])
G = E(1,-sqrt(F(a+ b+1)))
Q = E(1337,-sqrt(F(a*1337+ b+1337^3)))
if Q[0] == x4:
    print("Done")

print(Q)
print(SmartAttack(G,Q,p))
print(G*4189812079514248908161689197409449 == Q)