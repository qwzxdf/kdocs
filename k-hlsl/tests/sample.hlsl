// K-HLSL のスモーク テスト用。ResourceDescriptorHeap などの SM 6.6 以降の構文を含む。
#include "common.hlsli"

struct Light
{
    float3 position;
    float  range;
};

cbuffer Frame : register(b0, space0)
{
    float4x4 gViewProj;
    uint     gTexIndex;
};

Texture2D<float4>       gTex  : register(t0);
RWStructuredBuffer<Light> gLights : register(u0);
SamplerState            gSamp : register(s0);

float3 Lighting(float3 n, float3 l)
{
    return saturate(dot(n, l)) * lerp(0.2, 1.0, n.y);
}

[numthreads(8, 8, 1)]
void CSMain(uint3 id : SV_DispatchThreadID)
{
    Texture2D<float4> t = ResourceDescriptorHeap[gTexIndex];
    SamplerState s = SamplerDescriptorHeap[0];
    float4 c = t.SampleLevel(s, float2(id.xy) / 256.0, 0);
    float sum = WaveActiveSum(c.x);
    gLights[id.x].range = sum;
    //COMPLETE_DOT
}
