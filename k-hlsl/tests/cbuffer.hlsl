// 定数バッファのレイアウトを確かめるサンプル。tests/lsp_cbuffer.py が使う。
struct Light
{
    float3 pos;
    float range;
    float3 color;
};

cbuffer PerFrame : register(b0)
{
    float4x4 viewProj;
    float3 eye;
    float time;
    float2 a;
    float3 b;
    float c[3];
    Light lights[2];
    bool flag;
    float3x3 m33;
    float d;
};

// 並べ替えると小さくなる例
cbuffer Wasteful : register(b1)
{
    float3 a;
    float4 b;
    float c;
    float4x4 m;
    float d;
    float2 e;
};

struct Data
{
    float4x4 world;
    float3 tint;
    float alpha;
    uint flags;
};
ConstantBuffer<Data> gData : register(b2);

float4 main() : SV_Target
{
    return viewProj[0] + eye.x + gData.alpha + a.x + b.x;
}
