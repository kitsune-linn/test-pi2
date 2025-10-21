class inout:
    supported=["console", "file"]
    def read(src):
        if src in inout.supported:
            print("Read from", src)
        else:
            print("noy supported")
print(inout.supported)
inout.read("file")
inout.read("nono")
