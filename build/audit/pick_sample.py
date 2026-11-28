import os, sys, random, collections, json
root, n = sys.argv[1], int(sys.argv[2])
random.seed(7)
by = collections.defaultdict(list); hubs = []
for d, ds, fs in os.walk(root):
    r = os.path.relpath(d, root)
    if r.split(os.sep)[0] in ('assets', '.git', 'widget', 'embed'): continue
    for f in fs:
        if not f.endswith('.html') or f == '404.html': continue
        p = '/' + os.path.relpath(os.path.join(d, f), root).replace(os.sep, '/')
        (hubs if f == 'index.html' else by[os.path.dirname(p)]).append(p)
pick = hubs[:150]
for k in sorted(by):
    pick += random.sample(by[k], min(3, len(by[k])))
random.shuffle(pick)
pick = list(dict.fromkeys(hubs[:150] + pick))[:n]
print('\n'.join(pick))
