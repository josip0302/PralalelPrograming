import numpy
import time

N=16
ulazno_polje=numpy.array(range(1,2**N))
start_time = time.time()
count=0

for i in ulazno_polje:
    prim = True
    if i > 1:
        for j in range(2, i):
            if i % j == 0:
                prim = False
                break
        if (prim):
            count += 1
print("Broj primarnih brojeva u ulaznom nizu je:"+str(count))
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time)