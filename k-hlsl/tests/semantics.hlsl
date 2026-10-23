// 自分で決めたセマンティクス(JOINTS など)にも色が付くかを確かめるサンプル
struct VS_IN
{
    float4 position : POSITION;
    float4 normal : NORMAL;
    uint4 joints : JOINTS;
    float4 weights : WEIGHTS;
    uint4 joints1 : JOINTS1;
    float4 weights1 : WEIGHTS1;
};

cbuffer BlurConstants : register(b0)
{
    int2 blur_direction;
    uint in_color_slot;
    uint out_blurred_slot;
};

float4 main(VS_IN i) : SV_Target
{
    return i.position + i.weights;
}
