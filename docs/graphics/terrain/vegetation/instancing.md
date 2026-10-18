---
title: Instancing
tags:
  - 描画
---

# Instancing

**草は、同じメッシュを何十万個も描きます**。**インスタンシングは、1 回の描画命令で、同じメッシュを、位置を変えて、大量に描く**方法で、**描画命令の数を減らせます**。このページでは、**インスタンシング**を説明します。

!!! tip "ポイント"
    - **1 回の DrawIndexedInstanced で、大量に描く**。
    - **位置・向き・大きさは、インスタンス バッファに**。
    - **GPU 駆動なら、カリングも GPU で**行える。
    - **描画命令の数が、減る**。

## Instancing {#インスタンシング}
**同じメッシュを位置・向き・大きさだけ変えて、大量に描く**のが**インスタンシング**です。

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

**1 つの描画命令にまとめる**ので、**CPU の負担が小さく**、**GPU も効率的**です。**メッシュ（ポリゴン数）が小さい**ほど、**インスタンシングの効果が大きい**です。

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

## Common Mistakes {#よくあるミス}

??? failure "草の描画命令が多すぎて、CPU が遅い"
    **インスタンシング**を使う。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **同じメッシュを、1 命令で大量に**

## References {#参考}

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## Related Pages {#関連ページ}

- [Vegetation](index.md)
- [カリング](culling.md)
