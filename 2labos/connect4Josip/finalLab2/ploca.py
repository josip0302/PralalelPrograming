
from copy import deepcopy


class Ploca:
  #inicijalizacija
  def __init__(self, rows,columns):
     self.rows = rows
     self.columns = columns
     self.mat=[[0 for _ in range(columns)] for _ in range(rows)]
     self.height=[0 for _ in range(columns)]

  #ispis ploče
  def print(self):
    print("  ",end=" ")
    for i in range(self.columns):
        print(" "+str(i+1)+" ",end=" ")
    print("")
    print("  ",end=" ")
    for i in range(self.columns):
        print("----",end="")
        
    print("")
    for i in range(self.rows):
        print(str(i+1)+" ",end="|")
        for j in range(self.columns):
          print(" "+str(self.mat[i][j])+" ",end=" ")
        print("",end="|")
        print("")

    print("  ",end=" ")
    for i in range(self.columns):
       print("----",end="")
    print("")


  def moveLegal(self,col):
       if(self.height[col]<self.rows):
         return True
       else:
          return False
       

  def Move(self,col,player):
     if(self.moveLegal(col)):
        a=self.rows-self.height[col]-1
        self.mat[a][col]=player
        self.height[col]+=1
        return a
     else:
        return -1
     
  def unodMove(self,col):
     if self.height[col]==0:
        return False  
     
     self.mat[self.rows-self.height[col]][col]=0
     self.height[col]-=1
     return True
     
  def gotovo(self,lastcol):
     col=lastcol
     row=self.rows - self.height[lastcol]
     if(row<0):
        return False
     player = self.mat[row][col]
     
     # uspravno
     seq=1
     r= row+1
     
     while(r<self.rows and self.mat[r][col]==player):
       
        seq+=1
        r+=1
     if seq>3:
        return True
     
     #vodoravno
     seq=0
     c=col
     while c-1>=0 and self.mat[row][c-1]==player:
        c-=1
     while c<self.columns and self.mat[row][c]==player:
        seq+=1
        c+=1
     if seq>3:
        return True
     

     #koso s lijeva na desno
     seq=0
     c=col
     r=row
     while c-1>=0 and r-1>=0 and self.mat[r-1][c-1]==player:
         c-=1
         r-=1
     while c<self.columns and r < self.rows and self.mat[r][c]==player:
         c+=1
         r+=1
         seq+=1
     if seq > 3:
        return True
     
     # koso s desna na lijevo
     seq=0
     c=col
     r=row
     while c-1>=0 and r+1<self.rows and self.mat[r+1][c-1]==player:
         c-=1
         r+=1
     while c<self.columns and r >= 0 and self.mat[r][c]==player:
         c+=1
         r-=1
         seq+=1
     if seq > 3:
        return True
     return False
  
  def copy(self):
     return deepcopy(self)