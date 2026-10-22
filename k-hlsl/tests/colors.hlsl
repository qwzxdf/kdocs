// 色付けの確認用(Viasfora 風: 制御フロー、可視性、エスケープ、書式指定子、レインボー括弧)
#define SCALE(x) ((x) * 2.0)
#define USE_FOG 1

struct Item
{
    float3 position;
    uint   id;
};

float Weight(int n)
{
	#if USE_FOG
    if (n > 0)
    {
        for (int i = 0; i < n; ++i)
        {
            if (i == 3) { continue; }
            printf("i=%d value=%5.2f\n\x41B 100%%", i, SCALE(1.5));
        }
    }
    else
    {
        return 0.0;
    }
	#else
		return SCALE(2.0);
	#endif

    switch (n)
    {
        case 1: break;
        default: discard;
    }
    while (n > 10) { n -= 10; }
  #  if defined(USE_FOG) && (USE_FOG > 0)
    return ((((1.0)))) + (n]);
  #  endif
}
