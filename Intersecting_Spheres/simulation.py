import numpy as np

N, M = 100000, 100000
rng = np.random.default_rng(42)

vols = []
for d in rng.uniform(0, 2, N):
    p = rng.uniform(-1, 1, (M, 3))
    in_a = (p**2).sum(1) <= 1
    in_b = ((p - [d, 0, 0]) ** 2).sum(1) <= 1
    vols.append((in_a & in_b).mean() * 8)

print(np.mean(vols))
