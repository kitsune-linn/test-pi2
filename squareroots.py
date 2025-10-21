n=int(input("請輸入一個正整數:"))
for i in range(n):
    if i*i==n:
        print(i)
        break
    i+=1
else:
    print("error")

