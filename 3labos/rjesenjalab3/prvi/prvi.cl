__kernel void prim(__global int* a, __global int* b,int length, int G)
{
   __private uint gid = get_global_id(0);
    __private uint broj_dretvi = G;
    __private uint i;
      __private uint j;

       volatile __global int* broj = &b[0];
        __private uint d = (gid * broj_dretvi);

        __private uint d2=d+broj_dretvi;
        if( d2 > length){
            d2=length;
         }

        for( i = d; i < d2; i+=1) {

            __private uint num = a[i];

            __private uint var = 0;

            if (num > 1){

                for( j=2; j<num; j+=1 ){
                    if ((num % j) == 0){
                        var = 1;
                        break;
                    }
                }

                if (var == 0){
                   // b[0] += 1;
                    atomic_inc(broj);
                }

            }

        }
}