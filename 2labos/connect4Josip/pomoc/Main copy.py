import random
import time

from mpi4py import MPI
from pomoc.Board import Board
from pomoc.Board import Igrac
from pomoc.Board import Rezultat
from pomoc.Board import RezultatPosao
from collections import defaultdict

TAGS = {'Board': 0, 'Request': 1, 'Job': 2, 'Result': 3, 'Done': 4}
DEPTH = 7


def izracunajRez(ploca, depth):
    win = True
    lose = True
    potezi = 0
    total = 0
    if ploca.provjera():
        if ploca.ZadnjiIgrao() == Igrac.Racunalo:
            return 1
        else:
            return -1
    if depth == 0:
        return 0

    potez = ploca.potez
    for i in range(ploca.sirina):
        if ploca.imaMjesta(i):
            potezi += 1
            ploca.ubaciZeton(potez, i)
            rezultat = izracunajRez(ploca, depth - 1)
            ploca.ukloniZeton(i)
            if rezultat != 1:
                win = False
            if rezultat > -1:
                lose = False
            if rezultat == 1 and potez == Igrac.Racunalo:
                return 1
            if rezultat == -1 and potez == Igrac.Covjek:
                return -1
            total += rezultat
    if win:
        return 1
    if lose:
        return -1
    return total / potezi


def seq():
    print(f'Seq')
    while True:
        print(f'Trenutno stanje:\n{ploca}')
        x = int(input(f'Unesite broj stupca: '))
        if x <= 0 or x >= 8:
            print("Unijeli ste broj van dimenzija ploce")
            continue
        ploca.ubaciZeton(Igrac.Covjek, x - 1)

        if ploca.provjera():
            print("Pobjeda!")
            break
        rezultati = {}
        start = time.perf_counter()
        for k in range(ploca.sirina):
            if ploca.imaMjesta(k):
                ploca.ubaciZeton(Igrac.Racunalo, k)
                rezultati[k] = izracunajRez(ploca, DEPTH - 1)
                ploca.ukloniZeton(k)
        end = time.perf_counter()
        print(f"Proteklo vremena: {end - start:0.4f}")
        max_v = max(rezultati.values())
        print(rezultati)
        print(max_v)
        m = [k for k, v in rezultati.items() if v == max_v]

        print(m)
        if len(m) > 1:
            m = m[random.randint(0, len(m) - 1)]
        else:
            m = m[0]
        ploca.ubaciZeton(Igrac.Racunalo, m)
        if ploca.provjera():
            print("Poraženi ste!")
            break


if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    status = MPI.Status()
    col = 7
    row = 6
    if size == 1:
        ploca = Board(row, col)
        seq()
    elif rank == 0:
        ploca = Board(row, col)
        while True:
            print(f'Stanje: \n {ploca}')
            x = int(input(f'Unesite broj stupca: '))
            if x <= 0 or x >= 8:
                print("Unijeli ste broj van dimenzija ploce")
                continue
            ploca.ubaciZeton(Igrac.Covjek, x - 1)
            if ploca.potez != Igrac.Racunalo:
                print("Pokusajte ponovo")
                continue
            if ploca.provjera():
                print(ploca)
                print("Cestitam pobjedio si.")
                for k in range(1, size):
                    comm.send("Done", dest=k, tag=TAGS['Done'])
                break
            for k in range(1, size):
                comm.send(ploca, dest=k, tag=TAGS['Board'])

            jobs = []
            kopija = ploca.duplicirajPlocu()
            for k in range(ploca.sirina):
                for j in range(ploca.sirina):
                    if kopija.imaMjesta(k):
                        kopija.ubaciZeton(Igrac.Racunalo, k)
                        if kopija.imaMjesta(j):
                            jobs.append(RezultatPosao(k, j))
                        kopija.ukloniZeton(k)

            rezultati = defaultdict(lambda: 0)
            locked = {}
            for k in range(ploca.sirina):
                locked[k] = False
            num_jobs = len(jobs)
            poslovi = 0
            start = time.perf_counter()
            while len(jobs) > 0:
                poruka = comm.recv(status=status)
                if status.tag == TAGS['Request']:
                    comm.send(jobs.pop(), dest=status.source, tag=TAGS['Job'])
                elif status.tag == TAGS['Result']:
                    if poruka.prvaDva:
                        rezultati[poruka.stupac] = poruka.rezultat
                        locked[poruka.stupac] = True
                    if not locked[poruka.stupac]:
                        rezultati[poruka.stupac] += poruka.rezultat / \
                            ploca.sirina
                    poslovi += 1

            while num_jobs != poslovi:
                poruka = comm.recv(status=status)
                if status.tag == TAGS['Result']:
                    if poruka.prvaDva:
                        rezultati[poruka.stupac] = poruka.rezultat
                        locked[poruka.stupac] = True
                    if not locked[poruka.stupac]:
                        rezultati[poruka.stupac] += poruka.rezultat / \
                            ploca.sirina
                    poslovi += 1

            for k in range(1, size):
                comm.send("Done", dest=k, tag=TAGS['Done'])
            end = time.perf_counter()
            print(f"Proteklo vremena: {end - start:0.4f}")
            print(rezultati)
            maks = max(rezultati.values())
            m = [k for k, v in rezultati.items() if v == maks]

            print(m)
            if len(m) > 1:
                m = m[random.randint(0, len(m) - 1)]
            else:
                m = m[0]
            ploca.ubaciZeton(Igrac.Racunalo, m)
            if ploca.provjera():
                print(ploca)
                print("Poraženi ste!")
                for k in range(1, size):
                    comm.send("Done", dest=k, tag=TAGS['Done'])
                break
        print("Kraj igre.")

    else:
        while True:
            poruka = comm.recv(source=0, status=status)
            if status.tag == TAGS['Board']:
                kopija = poruka
            elif status.tag == TAGS['Done']:
                break

            while True:
                comm.send("Request", dest=0, tag=TAGS['Request'])
                poruka = comm.recv(source=0, status=status)
                ploca = kopija.duplicirajPlocu()
                if status.tag == TAGS['Done']:
                    break

                if status.tag == TAGS['Job']:
                    ploca.ubaciZeton(Igrac.Racunalo, poruka.prviStupac)
                    if ploca.provjera():
                        comm.send(Rezultat(poruka.prviStupac, 1, True),
                                  dest=0, tag=TAGS['Result'])
                        continue
                    ploca.ubaciZeton(Igrac.Covjek, poruka.drugiStupac)
                    if ploca.provjera():
                        comm.send(Rezultat(poruka.prviStupac, -1,
                                  True), dest=0, tag=TAGS['Result'])
                    else:
                        result = izracunajRez(ploca, DEPTH - 2)
                        comm.send(Rezultat(poruka.prviStupac, result),
                                  dest=0, tag=TAGS['Result'])
