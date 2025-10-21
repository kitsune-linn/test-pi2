# def caculate(n1, n2):
#     print(n1+n2)
#     return n1+n2
# value=caculate(2, 3)+caculate(3, 5)
# print(value)
def plustomax(n1, n2):
    sum=0
    for i in range(n1, n2+1):
        sum+=i
    print(sum)
    return sum
value=plustomax(1, 16526)+plustomax(254, 3841)
print(value)