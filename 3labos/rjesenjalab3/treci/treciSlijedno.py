import numpy as np, math, time, sys

np.set_printoptions(threshold=sys.maxsize)


def main():
    error, bnorm, tolerance, scalefactor, numiter, printfreq = 0, 0, 0, 0, 0, 1000
    bbase, hbase, wbase, mbase, nbase = 10, 15, 5, 32, 32
    irrotational, checkerr = 1, 0
    m, n, b, h, w, iter, i, j = 0, 0, 0, 0, 0, 0, 0, 0
    tstart, tstop, ttot, titer = 0, 0, 0, 0

    print("Usage: cfd <scale> <numiter>\n")

    scalefactor, numiter = 64, 10

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

    for iter in range(1, numiter + 1):

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                psitmp[i * (m + 2) + j] = 0.25 * (
                            psi[(i - 1) * (m + 2) + j] + psi[(i + 1) * (m + 2) + j] + psi[i * (m + 2) + j - 1] + psi[
                        i * (m + 2) + j + 1])
        if checkerr or iter == numiter:
            dsq = 0

            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    tmp = psitmp[i * (m + 2) + j] - psi[i * (m + 2) + j]
                    dsq += tmp * tmp
            error = dsq
            error = math.sqrt(error)
            error = error / bnorm

        if checkerr:
            if (error < tolerance):
                print("Converged on iteration {}\n".format(iter))
                break

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                psi[i * (m + 2) + j] = psitmp[i * (m + 2) + j]

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