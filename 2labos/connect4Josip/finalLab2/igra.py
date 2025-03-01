from ploca import Ploca 
import random 
from copy import copy, deepcopy
import time
from mpi4py import MPI
import math
import sys 

dubinaDijeljenja=int(sys.argv[1])
B=Ploca(6,7)
dubina = 7
taskList=[]
movesList=[0.0 for _ in range(7)]
resultList=[0.0 for _ in range(7)]
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()  

def EvaluateParalel(Current,LastMover,iLastCol,iDepth):
    dTotal=0.0
    bAllLose = True
    bAllWin = True
    iMoves=1
    if(Current.gotovo(iLastCol)):
        if(LastMover==2):
            return 1.0
        
        else:
            return -1.0
    if(iDepth==0):
        return 0.0
    iDepth-=1
    if(LastMover==2):
        NewMover = 1
    else:
        NewMover = 2
    for iCol in range(Current.columns):
        if(Current.moveLegal(iCol)):
            
            Current.Move(iCol,NewMover)
            if(dubinaDijeljenja==2):
               
                iMoves+=1
                dResult ={'col':iLastCol,'Current':Current.copy(), 'LastMover':NewMover,'iLastCol':iCol,'iDepth':iDepth}
                taskList.append(dResult)
            elif(dubinaDijeljenja==3):
                

                for jCol in range(Current.columns):
                    if(Current.moveLegal(jCol)):
                        
                        iMoves+=1
                        if(NewMover==2):
                            NewerMover = 1
                        else:
                            NewerMover = 2
                        Current.Move(jCol,NewerMover)
                        dResult ={'col':iLastCol,'Current':Current.copy(), 'LastMover':NewerMover,'iLastCol':jCol,'iDepth':iDepth-1}
                        taskList.append(dResult)
                        Current.unodMove(jCol)
            Current.unodMove(iCol)
    movesList[iLastCol]=iMoves
def Evaluate(Current,LastMover,iLastCol,iDepth):
    
    dTotal=0.0
    bAllLose = True
    bAllWin = True
    iMoves=0
    if(Current.gotovo(iLastCol)):
        if(LastMover==2):
            return 1.0
        
        else:
            return -1.0
    if(iDepth==0):
        return 0.0
    iDepth-=1
    if(LastMover==2):
        NewMover = 1
    else:
        NewMover = 2
    for iCol in range(Current.columns):
        if(Current.moveLegal(iCol)):
            iMoves+=1
            Current.Move(iCol,NewMover)
            dResult = Evaluate(Current.copy(),NewMover, iCol, iDepth)
            Current.unodMove(iCol)
            if(dResult > -1.0):
                bAllLose = False
            if dResult != 1.0 :
                bAllWin = False
            if(dResult == 1.0 and NewMover == 2):
                return 1.0;	
            if(dResult == -1.0  and NewMover == 1):
                return -1.0;	
            dTotal += dResult
    if(bAllWin == True):	
        return 1
    if(bAllLose == True):
        return -1
    dTotal /= iMoves
    return dTotal
if(rank==0):
    B.print()
    print("Dijelimo na dubini " +str(dubinaDijeljenja))
    print(size)
    print("Dobro došli u connect 4")
    igrase=True
    while igrase:
        print("Vaš potez")
        x = int(input())
        if(1<=x<=B.columns):
            B.Move(x-1,1)
          
        B.print()
     
        if(B.gotovo(x-1)):
            B.print()
            print("Čestitam pobjedili ste")
            break
        iDepth = dubina
        start_time = time.time()
        while True:
            print("Dubina: " + str(iDepth))
            dBest = -1.0
            iBestCol = -1.0
            for iCol in range(B.columns):
                if(B.moveLegal(iCol)):
                    if iBestCol == -1:
                        iBestCol=iCol
                    if(dubinaDijeljenja==3):
                        movesList[iCol]=1.0
                    B.Move(iCol,2)
                    if(size>1):
                        if(dubinaDijeljenja==1):
                            movesList[iCol]=1.0
                           
                            dResult ={'col':iCol,'Current':B.copy(), 'LastMover':2,'iLastCol':iCol,'iDepth':iDepth-1}
                            taskList.append(dResult)
                        else:
                            
                            EvaluateParalel(B.copy(), 2, iCol, iDepth-1)
                        B.unodMove(iCol)
                    else:
                        dResult = Evaluate(B.copy(), 2, iCol, iDepth-1)
                        B.unodMove(iCol)
                        if dResult>dBest or (dBest == dResult and random.randint(0,2)==0):
                            dBest= dResult
                            iBestCol=iCol
                        print("Stupac:"+ str(iCol))
                        print("vrijednost: " + str(dBest))
            
            if(size>1):
                for i in range(0,len(taskList),size-1):
                    for a in range(1,size):
                        
                        if(i+a-1)<len(taskList):
                            #print(a)
                            print(i+a-1)
                            comm.send(taskList[i+a-1], dest=a)
                    for a in range(1,size):
                        
                        if(i+a-1)<len(taskList):
                            data=comm.recv(source=a)
                            resultList[data["col"]]+=data["rez"]
                iBestCol=resultList.index(max(resultList))
                if(movesList[iBestCol]!=0.0):
                    dBest=max(resultList)/movesList[iBestCol]
                else:
                    for i in range(len(movesList)):
                        if(movesList[i]==0.0):
                            resultList[i]=-1000
                    iBestCol=resultList.index(max(resultList))
                    if(movesList[iBestCol]==0.0):
                        dBest=0.0
                        print(movesList)
                    else:
                        dBest=max(resultList)/movesList[iBestCol]
                taskList=[]
                movesList=[0.0 for _ in range(7)]
                resultList=[0.0 for _ in range(7)]
            iDepth=round(iDepth/2)
            if dBest!=-1.0 or iDepth<=0:

                break
        print("Najbolji redak je:"+ str(iBestCol+1)+", sa vrijednosti:"+ str(dBest) )
        B.Move(iBestCol, 2)
        B.print()
        end_time = time.time()  
        elapsed_time = end_time - start_time
        print("Elapsed time: ", elapsed_time) 
        if(B.gotovo(iBestCol)):
            B.print()
            print("Igra zavrsena! (pobjeda racunala)")
            break
                   
if rank!=0:
    while True:
        data = comm.recv(source=0)
        rez=Evaluate(data["Current"],data["LastMover"],data["iLastCol"],data["iDepth"])
        col=data["col"]
        comm.send({"col":col,"rez":rez},dest=0)
                   