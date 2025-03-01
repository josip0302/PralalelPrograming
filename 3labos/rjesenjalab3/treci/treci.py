import pyopencl as cl
import numpy as np, math, time, sys

np.set_printoptions(threshold=sys.maxsize)


class CL:
    def __init__(self,G,L):
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        self.G=np.int32(G)
        self.G2=G
        self.L = np.int32(L)

    def loadProgram(self, filename):
        #read in the OpenCL source file as a string
        f = open(filename, 'r')
        fstr = "".join(f.readlines())

        #create the program
        self.program = cl.Program(self.ctx, fstr).build()

    def executeJ(self,polje1,polje2,m,n):
        mf = cl.mem_flags

        #initialize client side (CPU) arrays
        self.a = polje1
        self.b=polje2
        #create OpenCL buffers
        self.a_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.a)
        self.b_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.b)


        self.program.jacobistep(self.queue, (self.G,), (self.L,), self.a_buf, self.b_buf,np.int32(m),np.int32(n),np.int32(len(polje1)),np.int32(1+(int(len(polje1)/self.G))))
        cl._enqueue_read_buffer(self.queue, self.b_buf, polje2).wait()

    def executeError(self,polje1,polje2,m,n):
        mf = cl.mem_flags

        #initialize client side (CPU) arrays
        self.a = polje1
        self.b=polje2
        #create OpenCL buffers
        self.a_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.a)
        self.b_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.b)
        c = np.empty_like(self.a)
        self.dest_buf = cl.Buffer(self.ctx, mf.READ_WRITE, c.nbytes)

        self.program.deltasq(self.queue, (self.G,), (self.L,), self.a_buf, self.b_buf,self.dest_buf,np.int32(m),np.int32(n),np.int32(len(polje1)),np.int32(1+(int(len(polje1)/self.G))))
        cl._enqueue_read_buffer(self.queue, self.dest_buf, c).wait()
        return c
    def executeCopy(self,polje1,polje2,m,n):
        mf = cl.mem_flags

        #initialize client side (CPU) arrays
        self.a = polje1
        self.b=polje2
        #create OpenCL buffers
        self.a_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.a)
        self.b_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.b)


        self.program.vratNazad(self.queue, (self.G,), (self.L,), self.a_buf, self.b_buf,np.int32(m),np.int32(n),np.int32(len(polje1)),np.int32(1+(int(len(polje1)/self.G))))
        cl._enqueue_read_buffer(self.queue, self.b_buf, polje2).wait()

def main():
    error, bnorm, tolerance, scalefactor, numiter, printfreq = 0, 0, 0, 0, 0, 1000
    bbase, hbase, wbase, mbase, nbase = 10, 15, 5, 32, 32
    irrotational, checkerr = 1, 0
    m, n, b, h, w, iter, i, j = 0, 0, 0, 0, 0, 0, 0, 0
    tstart, tstop, ttot, titer = 0, 0, 0, 0

    print("Usage: cfd <scale> <numiter>\n")

    scalefactor, numiter = 64, 1000

    print("Scale Factor = {}, iterations = {}\n".format(scalefactor, numiter))

    b = bbase * scalefactor
    h = hbase * scalefactor
    w = wbase * scalefactor
    m = mbase * scalefactor
    n = nbase * scalefactor

    print("Running CFD on {} x {} grid in serial\n".format(m, n))

    psi = np.zeros(((m + 2) * (n + 2)), dtype=np.float32)
    psitmp = np.zeros(((m + 2) * (n + 2)), dtype=np.float32)
    i, j = 0, 0

    for i in range(b + 1, b + w):
        psi[i * (m + 2) + 0] = i - b

    for i in range(b + w, m + 1):
        psi[i * (m + 2) + 0] = w

    for j in range(1, h + 1):
        psi[(m + 1) * (m + 2) + j] = w

    for j in range(h + 1, h + w):
        psi[(m + 1) * (m + 2) + j] = w - j + h

    bnorm = 0.0
    for i in range(0, m + 2):
        for j in range(0, n + 2):
            bnorm += psi[i * (m + 2) + j] * psi[i * (m + 2) + j]

    bnorm = math.sqrt(bnorm)

    print("\nStarting main loop...\n\n")
    tstart = time.time()
    example = CL(10000000, 64)
    example.loadProgram("treci.cl")
    for iter in range(1, numiter + 1):
        #prva paralelizacia
        #jacobistep
        example.executeJ(psi,psitmp,m,n)

        if checkerr or iter == numiter:

            #deltasq
            dsq=sum(example.executeError(psi,psitmp,m,n))
            error = dsq
            error = math.sqrt(error)
            error = error / bnorm

        if checkerr:
            if (error < tolerance):
                print("Converged on iteration {}\n".format(iter))
                break
        #copy back
        example.executeCopy(psitmp, psi, m, n)


        if (iter % printfreq == 0):
            if not checkerr:
                print("Completed iteration {}\n".format(iter))
            else:
                print("Completed iteration {}, error = {}\n".format(iter, error))

    if iter > numiter:
        iter = numiter

    tstop = time.time()

    ttot = tstop - tstart
    titer = ttot / iter

    print("\n... finished\n")
    print("After {} iterations, the error is {}\n".format(iter, error))
    print("Time for {} iterations was {} seconds\n".format(iter, ttot))
    print("Each iteration took {} seconds\n".format(titer))
    print("... finished\n")


if __name__ == '__main__':
    main()