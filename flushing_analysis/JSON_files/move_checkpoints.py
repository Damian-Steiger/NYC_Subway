import os

dir = os.getcwd()

files = os.listdir(dir)
files.sort()

for f in files:
  if f.endswith("checkpoint.json"):
    os.rename(dir+"/"+f, dir+"/checkpoint/"+f)

print("done")
