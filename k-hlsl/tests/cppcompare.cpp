// HLSL の cbuffer と比べるサンプル(tests/cppcompare.hlsl と対)
#include <DirectXMath.h>

// lightDir(float3)が、HLSL では 96 から始まる。C++ は 88 に置くので、ずれる
struct PerObject {
  DirectX::XMFLOAT4X4 world;
  DirectX::XMFLOAT3 tint;
  float alpha;
  DirectX::XMFLOAT2 uv_scale;
  DirectX::XMFLOAT3 light_dir;
  float intensity;
  float shine;
};
