import numpy as np



# 10 samples. 2ls, 2 rs
# avg across left and right
arr2 = np.arange(40).reshape([40//4,2,2])
print(arr2,"\n\n")
# the shared axis is computed for mean...
print(arr2.mean(axis=1)) # axis to 'collapse'