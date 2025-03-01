from  mpi4py import MPI

comm = MPI.COMM_WORLD
worker =comm.Get_rank()
size = comm.Get_size()

if worker==0:
    data=[{"data for "+ str(i):i}for i in range(0,size)]
    print(data)
else:
    data=None
data= comm.scatter(data,root=0)
print(worker,data)