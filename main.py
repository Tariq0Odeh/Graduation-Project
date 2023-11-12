import numpy as np

N = 5
K = 2


class Traffic:
    def __init__(self):
        self.data = np.random.randint(1, 10, N)

    def __str__(self):
        return f"Traffic: {self.data}"


class Resources:
    def __init__(self):
        self.data = np.random.uniform(1.0, 10.0, K)

    def __str__(self):
        return f"Resources: {self.data}"


class Qos:
    def __init__(self):
        self.data = np.random.uniform(1.0, 10.0, N)

    def __str__(self):
        return f"Qos: {self.data}"


class Slice:
    def __init__(self, t):
        self.t = t
        self.x = [Traffic() for _ in range(t)]
        self.r = [Resources() for _ in range(t)]
        self.q = [Qos() for _ in range(t)]

    def __str__(self):
        return f"\n".join([f"\tDTI {i + 1}: {x}\n\t\t   {r}\n\t\t   {q}" for i, (x, r, q) in enumerate(zip(self.x, self.r, self.q))])


def print_traffic_and_resource_matrices(slices, n_ttis):
    i = 1
    for slice in slices:
        print(f"Slice - {i}")
        print(slice)
        i = i+1


if __name__ == '__main__':
    M = 4
    t = 3

    slices = [Slice(t) for _ in range(M)]

    print_traffic_and_resource_matrices(slices, t)
