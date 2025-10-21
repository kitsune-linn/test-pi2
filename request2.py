import urllib.request as req
src="https://www.ntu.edu.tw/"
with req.urlopen(src) as response:
    data=response.read().decode("utf-8")
print(data)