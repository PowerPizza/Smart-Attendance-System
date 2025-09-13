import numpy as np

arr1 = np.array([1.2, 12.8, 3.5, 7.9])
arr2 = np.array([1.2, 12.8, 1.5, 2.2])

print(np.linalg.norm(arr1 - arr2))