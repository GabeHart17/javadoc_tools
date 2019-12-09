import sys


if len(sys.argv) < 2:
    print("correct usage is:\npython3 dedocumentator.py file.java")
    sys.exit()

ext = sys.argv[1].split('.')[-1]
name = sys.argv[1][:-len(ext) - 1]

with open(sys.argv[1], 'r') as f:
    text = f.read()

chunks = [i.split("*/") for i in text.split("/*")]
flat_chunks = []
for i in chunks:
    for j in i:
        flat_chunks.append(j)

out = open(name + "_dedocumentated." + ext, 'a')

state = True
for c in flat_chunks:
    if state:
        out.write(c)
    state = not state

out.close()
