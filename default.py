# def divide(n1, n2):
#     print(n1/n2)
# divide(4, 2)
# def power(base, exp=0):
#     return base**exp
# value=power(2)
# print(value)
# def avg(*numbers):
#     sum=0
#     count=0
#     for number in numbers:
#         sum+=number
#         count+=1
#     sum=sum/count
#     print(sum)
# avg(1, 3, 5)
def avg(*numbers):
    sum=0
    for number in numbers:
        sum+=number
    sum=sum/len(numbers)
    print(sum)
avg(1, 3, 5)
