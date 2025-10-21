# class point:
#     def __init__(self):
#         self.x=3
#         self.y=4
# p1=point()
# print(p1.x, p1.y)

# class fullname:
#     def __init__(self, firstname, lastname):
#         self.firstname=firstname
#         self.lastname=lastname
# name1=fullname("C.C", "Lin")
# print(name1.firstname, name1.lastname)

class file:
    def __init__(self, name):
        self.name=name
        self.file=None
    def open(self):
        self.file=open(self.name, mode="r", encoding="utf-8")
    def read(self):
        return self.file.read()
f1=file("data1.txt")
f1.open()
data=f1.read()
print(data)