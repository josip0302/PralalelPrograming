__kernel void jacobistep(__global float *psi, __global float *psinew, int m, int n,int length, int G)
{
	 __private uint gid = get_global_id(0);
    __private uint broj_dretvi = G;
    __private uint i;
      __private uint j;
__private uint d = (gid * broj_dretvi);

        __private uint d2=d+broj_dretvi;
        if( d2 > m){
            d2=m;
         }


	for(i=d;i<=d2;i++) {
		for(j=1;j<=n;j++) {
		psinew[i*(m+2)+j]=0.25*(psi[(i-1)*(m+2)+j]+psi[(i+1)*(m+2)+j]+psi[i*(m+2)+j-1]+psi[i*(m+2)+j+1]);
		}
	}
}

__kernel void deltasq(__global float *oldarr,__global float *newarr,__global float *dest, int m, int n,int length, int G)
{
	__private uint gid = get_global_id(0);
    __private uint broj_dretvi = G;
    __private uint i;
      __private uint j;
    __private uint d = (gid * broj_dretvi);
__private float tmp;
        __private uint d2=d+broj_dretvi;
        if( d2 >= m){
            d2=m;
         }

	for(i=d;i<=d2;i++)
	{
    __private float x=0.0;
		for(j=1;j<=n;j++){
		tmp = newarr[i*(m+2)+j]-oldarr[i*(m+2)+j];
		x += tmp*tmp;
		}
    dest[i]=x;
	}


}
__kernel void vratNazad(__global float *psinew, __global float *psi, int m, int n,int length, int G)
{
	 __private uint gid = get_global_id(0);
    __private uint broj_dretvi = G;
    __private uint i;
      __private uint j;
__private uint d = (gid * broj_dretvi);

    __private uint d2=d+broj_dretvi;
        if( d2 >= m){
            d2=m;
         }
    for(i=d;i<=d2;i++) {
			for(j=1;j<=n;j++) {
				psi[i*(m+2)+j]=psinew[i*(m+2)+j];
			}
		}

    }