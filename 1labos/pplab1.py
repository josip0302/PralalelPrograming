from  mpi4py import MPI
import random
import time

def getLeft(i,s):
    if(i==0):
        return s-1
    else:
        return i-1
def getRight(i,s):
    if (i == s-1):
        return 0
    else:
        return i+1
def jedi(t):
    print(t + "jedem", flush=True)
    time.sleep(3)

comm = MPI.COMM_WORLD
worker =comm.Get_rank()
size = comm.Get_size()

if worker ==0:
    vilice = [True,True]
    p=2
elif worker == size-1:
    vilice = [False, False]
    p=0
else:
    vilice = [False, True]
    p=1
c=0

zahtjevi=[100,100]
tabs=""
desno=getRight(worker,size)
lijevo=getLeft(worker,size)
for i in range(0,worker):
    tabs+="    "
#Proces(i)
while True :
    #misli (slucajan broj sekundi);
    # i 'istovremeno' odgovaraj na zahtjeve!
    duljinaMisli=random.randint(1,8)
    print(tabs + "mislim", flush=True)
    for y in range(0, duljinaMisli):
        time.sleep(1)

        if comm.iprobe(source=desno):
           zahtjev=comm.recv(source=desno)
           print(tabs+"stigao zatjev od:" + str(desno),flush=True)
           if vilice[1] and p  > 0:

               p -= 1

               vilice[1] = False
               comm.send(zahtjev, dest=desno)
        if comm.iprobe(source=lijevo):
           zahtjev=comm.recv(source=lijevo)
           print(tabs + "stigao zatjev od:" + str(lijevo), flush=True)
           if vilice[0] and p  > 0:
               p -= 1

               vilice[0] = False
               comm.send(zahtjev, dest=lijevo)
    #dok (nemam obje vilice) {
    while (p+c<2):
        #posalji zahtjev za vilicom;
        strana=100
        pinjur=3
        imamVilicu = True
        if not vilice[0]:
            strana=getLeft(worker,size)
            pinjur="daj lijevu"
            imamVilicu = False
        elif not vilice[1]:
            strana=getRight(worker,size)
            pinjur="daj desnu"
            imamVilicu = False
        print(tabs +"tražim vilicu("+str(strana)+")", flush=True)

        comm.send(worker,dest=strana)

        # ponavljaj {
        while not imamVilicu:
        # cekaj poruku (bilo koju!);
            poruka=comm.recv()
        # ako je poruka odgovor na zahtjev // dobio vilicu
        # azuriraj vilice;
        # inace ako je poruka zahtjev // drugi traze moju vilicu
        # obradi zahtjev (odobri ili zabiljezi);
            if pinjur == "daj lijevu" and poruka == worker:
                vilice[0] = True
                c += 1
                print(tabs + "dobio vilicu", flush=True)
                imamVilicu = True
            elif pinjur == "daj desnu" and poruka == worker:
                vilice[1] = True
                c += 1
                print(tabs + "dobio vilicu", flush=True)
                imamVilicu=True
            elif poruka == desno:

                if vilice[1] and p > 0:
                    p -= 1
                    vilice[1] = False
                    comm.send(desno, dest=desno)
                else:
                    print(tabs + "drugi traze moju vilicu", flush=True)
                    zahtjevi[1] = desno
            elif poruka == lijevo:
                if vilice[0] and p > 0:
                    p -= 1
                    vilice[0] = False
                    comm.send(lijevo, dest=lijevo)
                else:
                    print(tabs + "drugi traze moju vilicu", flush=True)
                    zahtjevi[0] = lijevo


        #} dok ne dobijes trazenu vilicu;

    #jedi;
    print(tabs + "jedem("+str(worker)+")", flush=True)
    time.sleep(3)
    p=2
    c=0
    #odgovori na postojeće zahtjeve;
    if zahtjevi[1] != 100:
        if vilice[1] and p > 0:
            p -= 1
            vilice[1] = False
            comm.send(desno, dest=desno)

    if zahtjevi[0] != 100:
        if vilice[0] and p > 0:
            p -= 1
            vilice[0] = False
            comm.send(lijevo, dest=lijevo)
