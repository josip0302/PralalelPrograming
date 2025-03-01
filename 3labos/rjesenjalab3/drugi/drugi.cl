
__kernel void pi(__global int* a, __global float* b,int length, int G)
{
   __private uint gid = get_global_id(0);
    __private uint broj_dretvi = G;
    __private uint i;

        __private uint d = (gid * broj_dretvi);

        __private uint d2=d+broj_dretvi;

        if( d2 > length){
            d2=length;
         }
__private float h=0.0;

         h= 1.0 / length;

        for( i = d; i < d2; i+=1) {

            __private uint num = a[i];
             __private float x=0.0;
              x=h*((float)num - (float)0.5 );

                b[i]=4.0 / ( (float)1.0 + x*x );


            }


}