---
title: Instancing
tags:
  - 描画
---

# Instancing

<strong>草は、同じメッシュを何十万個も描きます</strong>。<strong>インスタンシングは、1 回の描画命令で、同じメッシュを、位置を変えて、大量に描く</strong>方法で、描画命令の数を減らせます。このページでは、インスタンシングを説明します。

!!! tip "ポイント"
    - 1 回の DrawIndexedInstanced で、大量に描く。
    - 位置・向き・大きさは、インスタンス バッファに。
    - GPU 駆動なら、カリングも GPU で行える。
    - 描画命令の数が、減る。

## インスタンシング
<strong>同じメッシュを位置・向き・大きさだけ変えて、大量に描く</strong>のが<strong>インスタンシング</strong>です。

インスタンシングの方式です。`DrawIndexedInstanced` は、インスタンス数を指定して描き、インスタンスごとのデータは頂点バッファか StructuredBuffer に置きます。`DrawIndexedInstancedIndirect` は、インスタンス数を GPU が決める方式で、カリング結果をそのまま使え、CPU 待ちがありません。インスタンス データは、位置（float3）・回転（1 つの角度）・スケール・色の個体差などで、16〜32 バイトに収めます。

```hlsl
struct GrassInstance {
  float3 position;
  float rotation;
  float scale;
  float color_variation;
  float2 padding;
};

StructuredBuffer<GrassInstance> instances : register(t0);

VSOutput VSMain(VSInput input, uint instance_id : SV_InstanceID) {
  GrassInstance instance = instances[instance_id];
  float s = sin(instance.rotation);
  float c = cos(instance.rotation);
  float3 local = input.position * instance.scale;
  float3 rotated = float3(local.x * c + local.z * s, local.y, -local.x * s + local.z * c);
  float3 world = rotated + instance.position;

  VSOutput output;
  output.position = mul(float4(world, 1), view_projection);
  output.color_variation = instance.color_variation;
  return output;
}
```

<strong>1 つの描画命令にまとめる</strong>ので、<strong>CPU の負担が小さく</strong>、GPU も効率的です。メッシュ（ポリゴン数）が小さいほど、インスタンシングの効果が大きいです。

<!-- fig:instancing-calls:begin -->

<svg class="fig illust motion" data-fig="instancing-calls" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-instancing-calls" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">同じ草を 24 本描く: 1 本ずつ命令を出す vs 1 回でまとめて描く</text>
<text x="70" y="90" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">個別に描く</text>
<rect x="70" y="130" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/></rect>
<rect x="120" y="130" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1021;0.1024;1.0000" values="0;0;1;1"/></rect>
<rect x="170" y="130" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1245;0.1248;1.0000" values="0;0;1;1"/></rect>
<rect x="220" y="130" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1469;0.1472;1.0000" values="0;0;1;1"/></rect>
<rect x="270" y="130" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1693;0.1696;1.0000" values="0;0;1;1"/></rect>
<rect x="320" y="130" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1917;0.1920;1.0000" values="0;0;1;1"/></rect>
<rect x="70" y="180" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2141;0.2144;1.0000" values="0;0;1;1"/></rect>
<rect x="120" y="180" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2365;0.2368;1.0000" values="0;0;1;1"/></rect>
<rect x="170" y="180" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2589;0.2592;1.0000" values="0;0;1;1"/></rect>
<rect x="220" y="180" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2813;0.2816;1.0000" values="0;0;1;1"/></rect>
<rect x="270" y="180" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;1.0000" values="0;0;1;1"/></rect>
<rect x="320" y="180" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3261;0.3264;1.0000" values="0;0;1;1"/></rect>
<rect x="70" y="230" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3485;0.3488;1.0000" values="0;0;1;1"/></rect>
<rect x="120" y="230" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3709;0.3712;1.0000" values="0;0;1;1"/></rect>
<rect x="170" y="230" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3933;0.3936;1.0000" values="0;0;1;1"/></rect>
<rect x="220" y="230" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4157;0.4160;1.0000" values="0;0;1;1"/></rect>
<rect x="270" y="230" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4381;0.4384;1.0000" values="0;0;1;1"/></rect>
<rect x="320" y="230" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4605;0.4608;1.0000" values="0;0;1;1"/></rect>
<rect x="70" y="280" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4829;0.4832;1.0000" values="0;0;1;1"/></rect>
<rect x="120" y="280" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5053;0.5056;1.0000" values="0;0;1;1"/></rect>
<rect x="170" y="280" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;1.0000" values="0;0;1;1"/></rect>
<rect x="220" y="280" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5501;0.5504;1.0000" values="0;0;1;1"/></rect>
<rect x="270" y="280" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5725;0.5728;1.0000" values="0;0;1;1"/></rect>
<rect x="320" y="280" width="40" height="40" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5949;0.5952;1.0000" values="0;0;1;1"/></rect>
<text x="430" y="90" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2ea043">インスタンシング</text>
<rect x="430" y="130" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="480" y="130" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="530" y="130" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="580" y="130" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="630" y="130" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="680" y="130" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="430" y="180" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="480" y="180" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="530" y="180" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="580" y="180" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="630" y="180" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="680" y="180" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="430" y="230" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="480" y="230" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="530" y="230" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="580" y="230" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="630" y="230" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="680" y="230" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="430" y="280" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="480" y="280" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="530" y="280" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="580" y="280" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="630" y="280" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<rect x="680" y="280" width="40" height="40" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></rect>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1021;0.1024;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1021;0.1024;0.1245;0.1248;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1245;0.1248;0.1469;0.1472;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1469;0.1472;0.1693;0.1696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1693;0.1696;0.1917;0.1920;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1917;0.1920;0.2141;0.2144;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">7<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2141;0.2144;0.2365;0.2368;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2365;0.2368;0.2589;0.2592;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2589;0.2592;0.2813;0.2816;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">10<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2813;0.2816;0.3037;0.3040;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">11<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3037;0.3040;0.3261;0.3264;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3261;0.3264;0.3485;0.3488;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">13<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3485;0.3488;0.3709;0.3712;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">14<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3709;0.3712;0.3933;0.3936;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3933;0.3936;0.4157;0.4160;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4157;0.4160;0.4381;0.4384;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">17<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4381;0.4384;0.4605;0.4608;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">18<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4605;0.4608;0.4829;0.4832;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">19<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4829;0.4832;0.5053;0.5056;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">20<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5053;0.5056;0.5277;0.5280;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">21<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.5501;0.5504;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">22<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5501;0.5504;0.5725;0.5728;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">23<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5725;0.5728;0.5949;0.5952;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">24<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5949;0.5952;1.0000" values="0;0;1;1"/></text>
<text x="130" y="365" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b">回の描画命令</text>
<text x="430" y="365" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2ea043" opacity="0">1<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></text>
<text x="450" y="365" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b">回の描画命令（位置の配列を渡す）</text>
</svg>

<!-- fig:instancing-calls:end -->

## なぜ、普通に描くと、遅いのか

草を 1 本ずつ、`DrawIndexed` で描くと、<strong>ドローコールが、数十万回</strong>になります。ドローコール 1 回ごとに、CPU が、状態の設定と、ドライバーの処理を行うので、<strong>1 回あたり数マイクロ秒</strong>でも、積もると、フレームを、使い切ります。

| 方式 | ドローコール | CPU の負荷 |
| --- | --- | --- |
| 1 本ずつ描く | 数十万 | 非常に高い |
| 区画ごとに、まとめる | 数百 | 中程度（メッシュの結合が要る） |
| インスタンシング | 1〜数回 | 低い |
| GPU 駆動（間接描画） | 1 回（インスタンス数も、GPU が決める） | 最小 |

インスタンシングの、基本的な考え方は、Carucci（2005）が、整理しています。

## インスタンスのデータ

```cpp
// 1 本の草のデータ（32 バイト）。位置・向き・大きさ・色。
struct GrassInstance {
  float3 position;      // 12 バイト
  float rotation;       // 4: Y 軸の回転（ラジアン）
  float scale;          // 4
  float height;         // 4
  float color_variation;// 4
  float bend;           // 4
};
static_assert(sizeof(GrassInstance) == 32);
```

インスタンスは、<strong>構造化バッファ（StructuredBuffer）</strong>に、並べます。頂点シェーダーが、`SV_InstanceID` で、自分の番号を受け取って、バッファから読みます。

```cpp
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = UINT(sizeof(GrassInstance) * max_instances);
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;   // 描画で読み、カリングで書く
desc.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
desc.StructureByteStride = sizeof(GrassInstance);
device->CreateBuffer(&desc, nullptr, &instance_buffer);

D3D11_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_UNKNOWN;
srv.ViewDimension = D3D11_SRV_DIMENSION_BUFFER;
srv.Buffer.NumElements = max_instances;
device->CreateShaderResourceView(instance_buffer.Get(), &srv, &instance_srv);
```

## 間接描画（GPU 駆動）

<strong>カリングを GPU で行う</strong>と、「何個、描くか」が、CPU には、分かりません（GPU が、計算してから、決まる）。CPU に読み戻すと、<strong>GPU の処理を、待つことになり、遅くなります</strong>。そこで、描画の引数を、GPU が書き、そのまま、描画に使うのが、間接描画です。

### 全体の流れ

```text
① 全インスタンス（StructuredBuffer）
        ↓  計算シェーダー（カリング）
② 見えるインスタンスだけを、AppendStructuredBuffer に詰める
        ↓  CopyStructureCount（個数を、引数バッファへコピー）
③ 引数バッファ [IndexCount, InstanceCount, ...]
        ↓  DrawIndexedInstancedIndirect
④ 見えるものだけを描く
```

### 引数バッファ

```cpp
// DrawIndexedInstancedIndirect の引数（5 個の UINT）
struct DrawArgs {
  UINT index_count_per_instance;
  UINT instance_count;            // ← GPU が書く
  UINT start_index_location;
  INT base_vertex_location;
  UINT start_instance_location;
};

D3D11_BUFFER_DESC args_desc = {};
args_desc.ByteWidth = sizeof(DrawArgs);
args_desc.Usage = D3D11_USAGE_DEFAULT;
args_desc.MiscFlags = D3D11_RESOURCE_MISC_DRAWINDIRECT_ARGS;      // 間接描画の引数として使う
DrawArgs init = {blade_index_count, 0, 0, 0, 0};
D3D11_SUBRESOURCE_DATA data = {&init};
device->CreateBuffer(&args_desc, &data, &args_buffer);
```

### 見えたものを、詰めるバッファ

```cpp
D3D11_BUFFER_DESC vis_desc = {};
vis_desc.ByteWidth = UINT(sizeof(GrassInstance) * max_instances);
vis_desc.Usage = D3D11_USAGE_DEFAULT;
vis_desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;
vis_desc.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
vis_desc.StructureByteStride = sizeof(GrassInstance);
device->CreateBuffer(&vis_desc, nullptr, &visible_buffer);

D3D11_UNORDERED_ACCESS_VIEW_DESC uav = {};
uav.Format = DXGI_FORMAT_UNKNOWN;
uav.ViewDimension = D3D11_UAV_DIMENSION_BUFFER;
uav.Buffer.NumElements = max_instances;
uav.Buffer.Flags = D3D11_BUFFER_UAV_FLAG_APPEND;                  // Append バッファ（カウンター付き）
device->CreateUnorderedAccessView(visible_buffer.Get(), &uav, &visible_uav);
```

### 毎フレームの処理

```cpp
// ① カウンターを 0 に戻して、カリングを実行する
const UINT zero = 0;
context->CSSetShader(cull_cs.Get(), nullptr, 0);
context->CSSetShaderResources(0, 1, instance_srv.GetAddressOf());
context->CSSetUnorderedAccessViews(0, 1, visible_uav.GetAddressOf(), &zero);   // 初期カウント 0
context->Dispatch((instance_count + 63) / 64, 1, 1);

// UAV を外す（SRV として読むため）
ID3D11UnorderedAccessView* null_uav = nullptr;
context->CSSetUnorderedAccessViews(0, 1, &null_uav, nullptr);

// ② カウンターの値（見えた個数）を、引数バッファの instance_count へコピーする
context->CopyStructureCount(args_buffer.Get(), offsetof(DrawArgs, instance_count), visible_uav.Get());

// ③ 見えたものを、間接描画する
context->VSSetShaderResources(0, 1, visible_srv.GetAddressOf());
context->DrawIndexedInstancedIndirect(args_buffer.Get(), 0);
```

この流れでは、<strong>CPU は、見えた個数を、一度も読みません</strong>。GPU が、自分で決めた個数を、そのまま描画に、使います。

## 描画のシェーダー

```hlsl
struct GrassInstance {
  float3 position; float rotation;
  float scale; float height; float color_variation; float bend;
};
StructuredBuffer<GrassInstance> g_instances : register(t0);

cbuffer FrameCB : register(b0) { float4x4 view_proj; float3 camera_position; float time; };

struct VSOut {
  float4 position : SV_Position;
  float3 color : COLOR;
};

VSOut main(uint vertex_id : SV_VertexID, uint instance_id : SV_InstanceID) {
  GrassInstance inst = g_instances[instance_id];
  float3 local = BladeVertex(vertex_id, 0.05 * inst.scale, inst.height, inst.bend);

  // Y 軸の回転
  float s = sin(inst.rotation), c = cos(inst.rotation);
  float3 rotated = float3(local.x * c + local.z * s, local.y, -local.x * s + local.z * c);

  VSOut o;
  o.position = mul(float4(inst.position + rotated, 1.0), view_proj);
  o.color = lerp(float3(0.1, 0.2, 0.05), float3(0.5, 0.75, 0.2), local.y / inst.height)
          * (0.9 + 0.2 * inst.color_variation);
  return o;
}
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| 順序 | Append バッファの、並びは、スレッドの実行順で決まる（毎フレーム、順序が変わる）。順序に依存する処理（半透明の、ソート）には、使えない |
| ドローコールを減らしすぎない | 種類（草・花・低木）が、違うメッシュは、別のドローコール。1 種類につき 1 回 |
| インスタンスの総数 | 数百万本を超えると、全部の、カリングが、重い。区画ごとに、まとめて、粗いカリングを先に行う（[Vegetation Culling](culling.md)） |
| `SV_InstanceID` の限界 | インスタンスの数が、65,535 を超えても、問題ない（32 ビット）。ただし、1 回の `Dispatch` の、スレッド グループ数に、上限（65,535）がある。数が、多いなら、複数回に分ける |
| デバッグ | 間接描画は、中身が見えにくい。ステージング バッファに、コピーして、読み戻すデバッグ用の経路を、用意しておく |

## 間接描画を、使わない方法

DirectX 11 が使えない環境（古い GPU）や、シンプルな実装では、<strong>CPU でカリングして、見えるものだけを、インスタンス バッファに書く</strong>方法も、あります。

```cpp
// CPU 側で、見えるインスタンスだけを集めて、毎フレーム、書き込む（草が、数万本までなら、十分）。
visible.clear();
for (const GrassInstance& g : all) if (IsVisible(g)) visible.push_back(g);
D3D11_MAPPED_SUBRESOURCE m;
context->Map(dynamic_buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &m);
memcpy(m.pData, visible.data(), visible.size() * sizeof(GrassInstance));
context->Unmap(dynamic_buffer.Get(), 0);
context->DrawIndexedInstanced(index_count, UINT(visible.size()), 0, 0, 0);
```

| 方式 | 向く規模 | 長所 | 短所 |
| --- | --- | --- | --- |
| CPU でカリング | 数万本まで | 実装が簡単 | CPU の負荷が、本数に比例する。毎フレーム、転送する |
| GPU でカリング ＋ 間接描画 | 数十万〜数百万本 | CPU の負荷が、ほぼゼロ | 実装が複雑。デバッグが難しい |

## よくあるミス

??? failure "草の描画命令が多すぎて、CPU が遅い"
    <strong>インスタンシング</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じメッシュを、1 命令で大量に

## 参考

- Carucci, "Inside Geometry Instancing", GPU Gems 2, Chapter 3, 2005
- Haar, Aaltonen, "GPU-Driven Rendering Pipelines", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Wihlidal, "Optimizing the Graphics Pipeline with Compute", Game Developers Conference 2016（フラスタム、背面、オクルージョンの、GPU カリング）
- Microsoft Learn, "ID3D11DeviceContext::DrawIndexedInstancedIndirect"
- Microsoft Learn, "ID3D11DeviceContext::CopyStructureCount"

## 関連ページ

- [Vegetation](index.md)
- [Vegetation Culling](culling.md)
