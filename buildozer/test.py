import re

f=open("pubspec.json")
print (f)
txt=f.read().replace('\n', '')
print (txt)
print ()

mg = re.search('versionCode[:"\s]+(\d+)',txt)
print (mg.group(1))

ng = re.search('versionName[:"\s]+([\d.]+)',txt)
print (ng.group(1))
