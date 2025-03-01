import pyopencl as cl
import numpy
import time

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

    def execute(self,polje):
        mf = cl.mem_flags

        #initialize client side (CPU) arrays
        self.a = polje

        #create OpenCL buffers
        self.a_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.a)
        c = numpy.empty_like(self.a)
        self.dest_buf = cl.Buffer(self.ctx, mf.READ_WRITE, c.nbytes)

        self.program.prim(self.queue, (self.G,), (self.L,), self.a_buf, self.dest_buf,numpy.int32(len(polje)),numpy.int32(1+(int(len(polje)/self.G))))
        cl._enqueue_read_buffer(self.queue, self.dest_buf, c).wait()
        return c[0]

if __name__ == "__main__":
    N=19
    ulazno_polje=numpy.array(range(1,2**N))
    start_time = time.time()
    count=0

    G=240000
    L=64

    example = CL(G,L)
    example.loadProgram("prvi.cl")
    count=example.execute(ulazno_polje)


    print("Broj primarnih brojeva u ulaznom nizu je:"+str(count))
    end_time = time.time()

# Calculate elapsed time
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time)