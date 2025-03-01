import pyopencl as cl
import numpy
import time
import os
import math
os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
class CL:
    def __init__(self,G,L):
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        self.G=numpy.int32(G)
        self.G2=G
        self.L = numpy.int32(L)

    def loadProgram(self, filename):
        #read in the OpenCL source file as a string
        f = open(filename, 'r')
        fstr = "".join(f.readlines())

        #create the program
        self.program = cl.Program(self.ctx, fstr).build()

    def execute(self,polje,h):
        mf = cl.mem_flags

        #initialize client side (CPU) arrays
        self.a = polje

        #create OpenCL buffers
        self.a_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.a)
        c = numpy.empty_like(self.a,dtype=numpy.float32)
        self.dest_buf = cl.Buffer(self.ctx, mf.READ_WRITE, c.nbytes)

        self.program.pi(self.queue, (self.G,),(self.L,), self.a_buf, self.dest_buf,numpy.int32(len(polje)),numpy.int32(1+(int(len(polje)/self.G))))
        cl._enqueue_read_buffer(self.queue, self.dest_buf, c).wait()
        return c

if __name__ == "__main__":

    N = 50000000
    PI = 3.141592653589793238462643;
    h = 1.0 / (N * 1.0)
    suma = 0.0
    ulazno_polje=numpy.array(range(1,N+1))

    start_time = time.time()


    G=1000000
    L=64

    example = CL(G,L)
    example.loadProgram("drugi.cl")
    rjesnje=numpy.array(example.execute(ulazno_polje,h))

    mojPi=sum(rjesnje)*h


    print("Pi je približno "+ str(mojPi)+" s pogreškom od "+str(abs(PI-mojPi)))
    end_time = time.time()

# Calculate elapsed time
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time)