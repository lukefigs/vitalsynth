
import numpy as np

def apply_edge_cases(sample, afib=False, motion=False, dropout=False):
    noisy = sample.copy()

    if motion:
        jitter = np.random.normal(0, 0.3, noisy.shape)
        noisy += jitter

    if dropout:
        start = np.random.randint(100, noisy.shape[0] - 200)
        noisy[start:start+100, :] = 0

    if afib:
        ppg_distort = np.sin(np.linspace(0, 12*np.pi, noisy.shape[0])) * 0.4
        noisy[:, 1] += ppg_distort

    return noisy
