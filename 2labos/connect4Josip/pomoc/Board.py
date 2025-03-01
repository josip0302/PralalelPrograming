import copy


class Igrac:
    Racunalo = 1
    Covjek = 2


class Rezultat:
    def __init__(self, odigranStupac, rezultat, prvaDva=False):
        self.stupac = odigranStupac
        self.rezultat = rezultat
        self.prvaDva = prvaDva


class RezultatPosao:
    def __init__(self, prviStupac, drugiStupac):
        self.prviStupac = prviStupac
        self.drugiStupac = drugiStupac

    def __repr__(self):
        return "[" + str(self.prviStupac) + "," + str(self.drugiStupac) + "]"


class Board:
    def __init__(self, visina, sirina):
        self.visina = visina
        self.sirina = sirina
        self.potez = Igrac.Covjek
        self.zadnjiIgrao = -1
        self.zadnjeIgranaKolona = -1,
        self.zadnjeIgranRed = -1
        self.ploca = [[0 for i in range(sirina)] for j in range(visina)]
        self.visinaStupca = [0 for i in range(sirina)]

    def __repr__(self):
        return "\n".join([str(row) for row in reversed(self.ploca)]).replace("[", "").replace("]", "").replace(",", "")

    def imaMjesta(self, i):
        return any([x[i] == 0 for x in self.ploca])

    def ubaciZeton(self, igrac, col):
        if not self.imaMjesta(col) or self.potez != igrac:
            print(
                f"Illegalni potez igraca:{igrac},stupac:{col}", flush=True)
            return
        for row in range(self.visina):
            if self.ploca[row][col] == 0:
                self.ploca[row][col] = igrac
                self.prebaciPotez()
                self.zadnjeIgranaKolona = col
                self.visinaStupca[col] += 1
                return

    def ZadnjiIgrao(self):
        return Igrac.Covjek if self.potez == Igrac.Racunalo else Igrac.Racunalo

    def prebaciPotez(self):
        self.potez = Igrac.Covjek if self.potez == Igrac.Racunalo else Igrac.Racunalo

    def duplicirajPlocu(self):
        novaPloca = Board(self.visina, self.sirina)
        novaPloca.ploca = copy.deepcopy(self.ploca)
        novaPloca.potez = self.potez
        novaPloca.zadnjeIgranaKolona = self.zadnjeIgranaKolona
        novaPloca.visinaStupca = copy.deepcopy(self.visinaStupca)
        return novaPloca

    def ukloniZeton(self, i):
        for k in reversed(self.ploca):
            if k[i] != 0:
                k[i] = 0
                self.visinaStupca[i] -= 1
                self.prebaciPotez()
                return

    def provjera(self):
        seq = 1
        col = self.zadnjeIgranaKolona
        row = self.visinaStupca[col] - 1
        igrac = self.ploca[row][col]

        # uspravno
        if row < 0:
            return False
        r = row - 1
        while r >= 0 and self.ploca[r][col] == igrac:
            seq += 1
            r -= 1
        if seq > 3:
            return True

        # vodoravno
        seq = 0
        c = col
        while (c - 1) >= 0 and self.ploca[row][c - 1] == igrac:
            c -= 1
        while c < self.sirina and self.ploca[row][c] == igrac:
            seq += 1
            c += 1
        if seq > 3:
            return True

        # lijevo na desno
        seq = 0
        r = row
        c = col
        while (c - 1) >= 0 and (r - 1) >= 0 and self.ploca[r - 1][c - 1] == igrac:
            c -= 1
            r -= 1
        while c < self.sirina and r < self.visina and self.ploca[r][c] == igrac:
            c += 1
            r += 1
            seq += 1
        if seq > 3:
            return True

        # desno na lijevo
        seq = 0
        r = row
        c = col
        while (c - 1) >= 0 and (r + 1) < self.visina and self.ploca[r + 1][c - 1] == igrac:
            c -= 1
            r += 1
        while c < self.sirina and r >= 0 and self.ploca[r][c] == igrac:
            c += 1
            r -= 1
            seq += 1
        return seq > 3
