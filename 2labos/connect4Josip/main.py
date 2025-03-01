import random 
from copy import copy, deepcopy
import time
from mpi4py import MPI
import math


nRows=6
nColumns=7
constDubina=6
mat = [[0 for _ in range(nColumns)] for _ in range(nRows)]



comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()  


def printPloca(ploca):
    print("  ",end=" ")
    for i in range(nColumns):
        print(" "+str(i+1)+" ",end=" ")
    print("")
    print("  ",end=" ")
    for i in range(nColumns):
        print("----",end="")
        
    print("")
    for i in range(nRows):
        print(str(i+1)+" ",end="|")
        for j in range(nColumns):
          print(" "+str(ploca[i][j])+" ",end=" ")
        print("",end="|")
        print("")

    print("  ",end=" ")
    for i in range(nColumns):
       print("----",end="")
    print("")

def unesi(ploca,a,t):
    b=-1
    for i in range(nRows):
        if(ploca[i][a-1]==0 and (i+1==nRows or ploca[i+1][a-1]!=0 )):
            ploca[i][a-1]=t
            b=i
            return b
    
    
def ukloni(ploca,a,t):
    b=-1
    for i in range(nRows):
        if(ploca[i][a-1]==t and (i+1==nRows or ploca[i+1][a-1]!=0 )):
            ploca[i][a-1]=0



def legalno(ploca,a):
    for i in range(nRows):
        if(ploca[i][a-1]==0 and (i+1==nRows or ploca[i+1][a-1]!=0 )):
            return True
    return False



def provjeri(ploca,a,b,t):
    
    startV=b-3 if b-3>0 else 0
    endV=startV+3 if startV+3<nRows-3 else nRows-3
    for i in range(startV,endV):
       if(ploca[i][a]==ploca[i+1][a]==ploca[i+2][a]==ploca[i+3][a]==t):
          return True
    
    startH=a-3 if a-3>0 else 0
    endH=startH+3 if startH+3<nColumns-3 else nColumns-3
    for i in range(startH,endH):
       if(ploca[b][i]==ploca[b][i+1]==ploca[b][i+2]==ploca[b][i+3]==t):
          return True
      
    if a-3<0 or b-3<0:
       if a>=b:
          startA=a-b
          startB=0
       else:
          startA=0
          startB=b-a
    else:  
     startA=a-3
     startB=b-3 
    for i in range(0,4):
       if(startB+i+3<nRows and startA+i+3<nColumns):
        ''' print(mat[startB+i][startA+i],end=" ")
        print(mat[startB+i+1][startA+i+1],end=" ")
        print(mat[startB+i+2][startA+i+2],end=" ")
        print(mat[startB+i+3][startA+i+3])'''
        if(ploca[startB+i][startA+i]==ploca[startB+i+1][startA+i+1]==ploca[startB+i+2][startA+i+2]==ploca[startB+i+3][startA+i+3]==t):
          return True
    
    if a-3<0 or b+3>=nRows:
       if a>=(nRows-b):
          startA=(nRows-b)-1
          startB=nRows-1
       else:
          startA=0
          startB=b-a
    else:  
     startA=a-3
     startB=b+3     
    for i in range(0,4):
       if(startB-i-3>=0 and startA+i+3<nColumns):
        ''' print(mat[startB-i][startA+i],end=" ")
        print(mat[startB-i-1][startA+i+1],end=" ")
        print(mat[startB-i-2][startA+i+2],end=" ")
        print(mat[startB-i-3][startA+i+3])
        '''
        if(ploca[startB-i][startA+i]==ploca[startB-i-1][startA+i+1]==ploca[startB-i-2][startA+i+2]==ploca[startB-i-3][startA+i+3]==t):
          return True
    return False

def Evaluate(ploca,t,a,b,dubina):
   novaPloca=deepcopy(ploca)
   bAllLose = True
   bAllWin = True
   dResult=0.0 
   dTotal=0.0
   if(provjeri(novaPloca,a,b,t)):
      if(t==2):
         return -1
      else:
         return 1
   
   if(dubina<=0):
     
      return 0
  
   if(t==1):
      NewMover=2
   else:
      NewMover=1
   
   dTotal=0
   iMoves=0
   destCount=0
   for i in range(nColumns):
      if legalno(novaPloca,i):
         iMoves+=1
         b=unesi(novaPloca,i,NewMover)
         if(rank==0 and size>1 and dubina<=2):
          destCount+=1
          dest = random.randint(1,size-1)
          data = {'novaPloca':novaPloca, 'NewMover':NewMover,'i':i,'b':b,'dubina':dubina-1}
          comm.send(data, dest=dest)
          ukloni(novaPloca,i,NewMover)
         else:
          dResult=Evaluate(novaPloca,NewMover,i,b,dubina-1)
          ukloni(novaPloca,i,NewMover)
          if dResult>-1:
             bAllLose=False
          if dResult != 1:
             bAllWin=False
          if dResult == 1 and NewMover == 2:
             return -1
          if dResult == -1 and NewMover==1:
             return 1
          dTotal+= dResult
   for i in range(destCount):
         data=comm.recv(source=MPI.ANY_SOURCE)
         dResult=data["dResult"]
         col=data["col"]
         if dResult>-1:
             bAllLose=False
         if dResult != 1:
             bAllWin=False
         if dResult == 1 and NewMover == 2:
             return -1
         if dResult == -1 and NewMover==1:
             return 1
         dTotal+= dResult
   if bAllWin:
      return 1
   if bAllLose:
      return -1
   dTotal /=iMoves
   return dTotal


def genereateCPU(ploca,dubina):
   nDubina = deepcopy(dubina)
   novaPloca=deepcopy(ploca)
  
   while True:
      dBest=1
      iBestCol=-1
      destCount=0
      for i in range(nColumns):
         if(legalno(novaPloca,i)):
            if(iBestCol==-1):
               iBestCol=i
            b=unesi(novaPloca,i,2)
            if(rank==0 and size>1 and nDubina<=2):
             print(nDubina)
             destCount+=1
             dest = random.randint(1,size-1)
             data = {'novaPloca':novaPloca, 'NewMover':2,'i':i,'b':b,'dubina':dubina-1}
             comm.send(data, dest=dest)
             ukloni(novaPloca,i,2)
           
            else:
             dResult=Evaluate(novaPloca,2,i,b,nDubina)
             ukloni(novaPloca,i,2)
             if(dResult>dBest or (dResult==dBest and random.randint(0,2)==0)):
               dBest=dResult
               iBestCol=i
      for i in range(destCount):
         data=comm.recv(source=MPI.ANY_SOURCE)
         dResult=data["dResult"]
         col=data["col"]
         if(dResult<dBest or (dResult==dBest and random.randint(0,2)==0)):
               dBest=dResult
               iBestCol=col
      nDubina=round(nDubina/2)
     
      if dBest!=1 and nDubina<=0:
         break
   return iBestCol
  

#start_time = time.time()
if(rank==0):
 print("Dobro došli u connect 4")
 printPloca(mat)
 igrase=True
 while igrase:
    print("Vaš potez")
    x = input()
    if(1<=int(x)<=nColumns):
     
     red=unesi(mat,int(x),1)
     gotovo=provjeri(mat,int(x)-1,red,1)
    # print(Evaluate(mat,1,int(x)-1,red,constDubina))
     if(gotovo):
        printPloca(mat)
        print("Čestitam pobjedili ste")
        print(constDubina)
        igrase=False
        break
     start_time = time.time()
     y = genereateCPU(mat,constDubina)
     #y=random.randint(1,nColumns)
     
     red=unesi(mat,y,2)
     gotovo=provjeri(mat,y,red,2)
     printPloca(mat)
     end_time = time.time()  
     elapsed_time = end_time - start_time
     print("Elapsed time: ", elapsed_time) 
     if(gotovo):
        print("Nažalost izgubili ste")
        igrase=False
        break
     
    else:
     print("Unesite novi broj između 1 i "+str(nColumns))
     
if rank!=0:
    while True:
     data = comm.recv(source=0)
     rez=Evaluate(data["novaPloca"],data["NewMover"],data["i"],data["b"],data["dubina"])
     comm.send({"dResult":rez,"col":data["i"]},dest=0)

