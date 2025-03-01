import time

N=50000000
PI = 3.141592653589793238462643;
h=1.0/(N*1.0)
sum=0.0
start_time = time.time()
for i in range(1,N+1):
    x=h*(i-0.5)
    sum+=4/(1.0+x*x)
mojPi=h*sum

print("Pi je približno "+ str(mojPi)+" s pogreškom od "+str(abs(PI-mojPi)))

end_time = time.time()


elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time)