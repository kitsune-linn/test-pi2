# with open("data.txt", mode="w", encoding="utf-8") as writeread:
#     writeread.write("hello world\n你好世界")
# with open("data.txt", mode="r", encoding="utf-8") as writeread:
#     data=writeread.read()
# print(data)

with open("data.txt", mode="w", encoding="utf-8") as writeread:
    writeread.write("11\n1\n1\n1\n2\n2\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n1\n")
sum=0
with open("data.txt", mode="r", encoding="utf-8") as writeread:
    for i in writeread:
        sum+=int(i)
print(sum)
