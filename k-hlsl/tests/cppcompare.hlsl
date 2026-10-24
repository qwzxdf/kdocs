// C++ の構造体と比べるサンプル(tests/cppcompare.cpp と対)
cbuffer PerObject : register(b1)
{
    float4x4 world;
    float3 tint;
    float alpha;
    float2 uvScale;
    float3 lightDir;
    float intensity;
    float shine;
};

float4 main() : SV_Target
{
    return world[0] + tint.x + alpha + uvScale.x + lightDir.x + intensity + shine;
}
