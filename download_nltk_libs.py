import nltk

with open('nltk.txt') as f:
    content = f.readlines()
content = [x.strip() for x in content]

print("Going to download %s NLTK packages: %s"%(len(content), content))

for item in content:
    nltk.download(item)
