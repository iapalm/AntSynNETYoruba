import random

ants = []
syns = []

word_files = ['dataset/noun-pairs.test', 'dataset/noun-pairs.train', 'dataset/noun-pairs.val']

for wf in word_files:
    with open(wf, 'r') as f:
        for line in f:
            w1, w2, state = line.split("\t")
            state = int(state)
            
            if state == 1:
                ants.append((w1, w2))
            else:
                syns.append((w1, w2))
    
content = ""            
for (syn1, syn2) in syns:
    content += "A {} is like a {}.  ".format(syn1, syn2)
    if random.random() > 0.8:
        content += "\n"
for (ant1, ant2) in ants:
    content += "There is both {} and {}.  ".format(ant1, ant2)
    if random.random() > 0.8:
        content += "\n"
    
with open('test-corpus/test-corpus.txt', 'w+') as f:
    f.write(content)