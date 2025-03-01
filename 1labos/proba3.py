from  mpi4py import MPI

comm = MPI.COMM_WORLD
worker =comm.Get_rank()
size = comm.Get_size()

if worker==1:
    data="Pozdrav domovini"
    print(data)
else:
    data=None
data= comm.bcast(data,root=1)
print(worker,data)