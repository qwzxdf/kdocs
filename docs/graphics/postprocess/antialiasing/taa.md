---
title: TAA
tags:
  - 描画
---

# TAA

<strong>TAA（Temporal Anti-Aliasing）</strong>は、**フレームごとにサンプル位置を画素内で少しずつずらし（ジッター）、過去のフレームの結果と混ぜて、時間方向にサンプルを蓄積する**方式です。<strong>事実上「複数フレームで SSAA をしている」</strong>ことになり、**ジオメトリの縁・シェーダー内のエイリアシング・時間的なちらつき**の**全部に効きます**。**現代のゲームの標準**で、**DLSS・FSR・TSR などのアップスケーラーの土台**でもあります。このページでは、**基本の仕組み・ジッター（Halton 列）・再投影・履歴のクランプ・合成の係数・実装の全体**を説明します。

!!! tip "ポイント"
    - TAA ＝ <strong>毎フレーム、サブピクセルだけずらして描き、前フレームの結果（履歴）と混ぜる</strong>。
    - <strong>ジッター</strong>：<strong>投影行列にサブピクセルの微小オフセット</strong>（<strong>Halton(2,3)・8〜16 フレーム周期</strong>）。
    - <strong>再投影</strong>：<strong>速度バッファで前フレームの画面位置を求め、履歴を読む</strong>。
    - <strong>履歴のクランプ</strong>：<strong>現在の画素の周囲 3×3 の色の範囲に、履歴を押し込む</strong>。<strong>ゴーストの主な対策</strong>。
    - <strong>合成</strong>：<strong>履歴 90 %・現在 10 %</strong> が<strong>目安</strong>。<strong>小さいほど滑らか・ゴースト増</strong>。
    - <strong>必要なもの</strong>：<strong>速度バッファ・前フレームの結果・ジッター</strong>。

## 基本の考え方

**1 フレームでは、1 画素につき 1 つのサンプル**しか取れません。**毎フレーム、サンプルの位置を画素内でずらし**、**過去のフレームの結果を、動きに合わせて持ってきて、平均**します。**静止した物なら、数フレームで複数のサンプルが蓄積**され、**SSAA のような画質**になります。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="TAA のジッター">
<text x="20" y="26" class="fig-title">サンプル位置を毎フレームずらして、結果を蓄積する</text>
<g transform="translate(40,56)">
<g stroke="#94a3b8" fill="#f8fafc"><rect x="0" y="0" width="100" height="100"/><rect x="130" y="0" width="100" height="100"/><rect x="260" y="0" width="100" height="100"/><rect x="390" y="0" width="100" height="100"/></g>
<polygon points="0,100 100,100 100,0" fill="#2563eb" fill-opacity="0.25"/><polygon points="130,100 230,100 230,0" fill="#2563eb" fill-opacity="0.25"/><polygon points="260,100 360,100 360,0" fill="#2563eb" fill-opacity="0.25"/><polygon points="390,100 490,100 490,0" fill="#2563eb" fill-opacity="0.25"/>
<circle cx="30" cy="35" r="5" fill="#e5484d"/><circle cx="170" cy="70" r="5" fill="#e5484d"/><circle cx="330" cy="30" r="5" fill="#e5484d"/><circle cx="420" cy="80" r="5" fill="#e5484d"/>
<text x="20" y="124" style="font-size:12px">フレーム 0</text><text x="150" y="124" style="font-size:12px">フレーム 1</text><text x="280" y="124" style="font-size:12px">フレーム 2</text><text x="410" y="124" style="font-size:12px">フレーム 3</text>
</g>
<g font-size="13"><text x="40" y="206">サンプル（赤）が、毎フレーム画素内の違う位置 → 縁をまたぐ画素では、内側・外側の結果が混ざる</text>
<text x="40" y="228">混ぜるたびに、縁の画素が「何割内側か」に収束 → 滑らかな縁（SSAA と同じ）</text></g>
</svg>

## ジッター

**投影行列にサブピクセルの微小なオフセット**を**加え**、**毎フレーム、画素内の違う位置**を**サンプル**します。**位置の列には低食い違い列の Halton(2, 3) が一般的**です。

```cpp
float Halton(uint32_t index, uint32_t base) {
  float result = 0.0f;
  float f = 1.0f / base;
  uint32_t i = index;
  while (i > 0) {
    result += f * (i % base);
    i /= base;
    f /= base;
  }
  return result;
}

DirectX::XMFLOAT2 JitterOffset(uint32_t frame_index, uint32_t width, uint32_t height) {
  uint32_t index = (frame_index % 8) + 1;
  float jitter_x = (Halton(index, 2) - 0.5f) * 2.0f / width;
  float jitter_y = (Halton(index, 3) - 0.5f) * 2.0f / height;
  return {jitter_x, jitter_y};
}
```

```cpp
DirectX::XMMATRIX jittered_projection = projection;
jittered_projection.r[2] = DirectX::XMVectorAdd(
    jittered_projection.r[2], DirectX::XMVectorSet(jitter.x, jitter.y, 0.0f, 0.0f));
```

| 点 | 説明 |
| --- | --- |
| <strong>Halton(2, 3)</strong> | **2 次元に均一に近く分布する列** |
| **`2.0 / width`** | **NDC は幅が 2**。**1 画素 ＝ `2 / width`** |
| **`r[2]` に足す** | **行ベクトル規約**で、**x・y の同次座標が、z（w）に比例してずれる** |
| **8 フレームで一巡** | **周期が短すぎるとパターンが見える**。**8〜16** |

## 履歴の再投影と合成

**現フレームの画素について、速度バッファから、前フレームの画面位置を求め、履歴を読み、現在と混ぜます**。

```hlsl
float3 TAA(float2 uv) {
  float3 current = current_color.SampleLevel(point_sampler, uv, 0).rgb;
  float2 velocity = velocity_texture.SampleLevel(point_sampler, uv, 0).rg;
  float2 history_uv = uv - velocity;
  float3 history = history_color.SampleLevel(linear_sampler, history_uv, 0).rgb;

  float3 neighbor_min = current;
  float3 neighbor_max = current;
  [unroll] for (int y = -1; y <= 1; ++y) {
    [unroll] for (int x = -1; x <= 1; ++x) {
      float3 neighbor = current_color.SampleLevel(point_sampler, uv + float2(x, y) * texel_size, 0).rgb;
      neighbor_min = min(neighbor_min, neighbor);
      neighbor_max = max(neighbor_max, neighbor);
    }
  }

  float3 clamped_history = clamp(history, neighbor_min, neighbor_max);
  float blend = 0.1;
  return lerp(clamped_history, current, blend);
}
```

| 点 | 説明 |
| --- | --- |
| **`history_uv = uv − velocity`** | <strong>速度は「現在 − 前」</strong>なので**引いて前の位置** |
| **近傍クランプ** | **周囲 3×3 の最小・最大の色の範囲に履歴を押し込む**（**ゴースト対策**） |
| **`blend = 0.1`** | **現在の寄与は 10 %**。**小さいほど滑らか・ゴースト増** |
| **履歴はリニア サンプル** | **バイリニアで読む**（**ぼけの原因にもなる**） |

<!-- fig:taa-history-clamp:begin -->

<svg class="fig illust motion" data-fig="taa-history-clamp" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-taa-history-clamp" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">TAA の履歴クランプ: 前の画像の色を、いまの周りの色の範囲に押し込めて、ゴーストを消す</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 40 画素。明るい物(幅 6)が右へ 3 画素動いた。前のフレームの履歴をそのまま混ぜる場合と、周りの最小〜最大に押し込める場合</text>
<text x="60.0" y="104" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">前のフレーム(履歴)</text>
<rect x="60.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="80.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="100.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="120.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="140.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="160.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="180.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="200.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="220.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="240.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="260.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="280.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="300.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="320.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="340.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="360.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="380.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="400.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="420.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="440.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="460.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="480.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="500.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="520.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="540.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="560.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="580.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="600.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="620.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="640.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="660.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="680.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="700.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="720.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="740.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="760.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="780.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="800.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="820.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="840.0" y="108.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="60.0" y="108" width="800.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="160" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">いまのフレーム(物が右へ動いた)</text>
<rect x="60.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="80.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="100.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="120.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="140.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="160.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="180.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="200.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="220.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="240.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="260.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="280.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="300.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="320.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="340.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="360.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="380.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="400.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="420.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="440.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="460.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="480.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="500.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="520.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="540.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="560.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="580.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="600.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="620.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="640.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="660.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="680.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="700.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="720.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="740.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="760.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="780.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="800.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="820.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="840.0" y="164.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="60.0" y="164" width="800.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="216" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">履歴をそのまま混ぜる(α = 0.1)</text>
<rect x="60.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="80.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0689" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="100.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="120.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0733" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="140.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="160.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0778" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="180.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="200.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0822" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="220.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="240.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0867" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="260.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="280.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="300.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#2e2e2e"/></rect>
<rect x="320.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956" values="#e5e7eb;#2e2e2e"/></rect>
<rect x="340.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#2e2e2e"/></rect>
<rect x="360.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000" values="#e5e7eb;#191919"/></rect>
<rect x="380.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#191919"/></rect>
<rect x="400.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044" values="#e5e7eb;#191919"/></rect>
<rect x="420.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067" values="#e5e7eb;#d3d3d3"/></rect>
<rect x="440.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1089" values="#e5e7eb;#d3d3d3"/></rect>
<rect x="460.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#d3d3d3"/></rect>
<rect x="480.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1133" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="500.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1156" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="520.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1178" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="540.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="560.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1222" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="580.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="600.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1267" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="620.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="640.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1311" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="660.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1333" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="680.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1356" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="700.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="720.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1400" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="740.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1422" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="760.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1444" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="780.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="800.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1489" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="820.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1511" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="840.0" y="220.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1533" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="60.0" y="220" width="800.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="272" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">履歴を、周りの最小〜最大に押し込めてから混ぜる</text>
<rect x="60.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2178" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="80.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2200" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="100.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2222" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="120.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2244" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="140.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2267" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="160.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2289" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="180.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2311" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="200.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2333" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="220.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2356" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="240.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2378" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="260.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="280.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2422" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="300.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2444" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="320.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2467" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="340.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2489" values="#e5e7eb;#2e2e2e"/></rect>
<rect x="360.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2511" values="#e5e7eb;#191919"/></rect>
<rect x="380.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2533" values="#e5e7eb;#191919"/></rect>
<rect x="400.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2556" values="#e5e7eb;#191919"/></rect>
<rect x="420.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#191919"/></rect>
<rect x="440.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2600" values="#e5e7eb;#191919"/></rect>
<rect x="460.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2622" values="#e5e7eb;#d3d3d3"/></rect>
<rect x="480.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2644" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="500.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2667" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="520.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2689" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="540.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="560.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2733" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="580.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="600.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2778" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="620.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="640.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2822" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="660.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="680.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2867" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="700.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="720.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2911" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="740.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="760.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2956" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="780.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="800.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3000" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="820.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3022" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="840.0" y="276.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3044" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="60.0" y="276" width="800.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3909;0.3911;1.0000" values="0;0;1;1"/><text x="60.0" y="340" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">画素 14 の例: 履歴 1.0、周りの範囲 0.1〜0.1</text>
<text x="60.0" y="364" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">履歴 1.0 → 範囲に押し込めて 0.1 → 結果 0.10(押し込めないと 0.91)</text>
</g>
<rect x="320.0" y="276.0" width="20.0" height="20.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"/>
<text x="60" y="410" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">ゴースト(物の後ろに残る、画素 11〜15 の差の合計):</text>
<text x="440" y="412" text-anchor="start" style="font-size:18px;font-weight:700;fill:#7c3aed" opacity="0">そのまま 2.43 / クランプ 0.81(3 分の 1)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5020;0.5022;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5243;0.5244;1.0000" values="0;0;1;1"/><rect x="60" y="440" width="860" height="60" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="76" y="464" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">履歴が、いまの周りの色の範囲を外れていたら、その範囲の端に寄せる</text>
<text x="76" y="487" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">動いた後に残る、古い色(ゴースト)が、混ざらなくなる。代わりに、細かい線がちらつくことがある</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">動く物があると、前のフレームの色が、古くなる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">古い色を、そのまま混ぜると、残像になる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.5243;0.5244;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">周りの色の範囲に押し込めば、古い色が、自然に消える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5243;0.5244;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:taa-history-clamp:end -->

## なぜクランプするのか

**履歴は前のフレームの結果**です。<strong>物が動いて、別の物が現れた画素の履歴は、「前に別の物が見えていた色」</strong>で**間違っています**。<strong>そのまま混ぜるとゴースト（残像）</strong>になります。**現在の周囲の色の範囲（最小〜最大）に、履歴を押し込む**と**周囲の色と大きく違う履歴は、範囲内に引き戻され**、**ゴーストが抑えられます**。

クランプの効果を状況別に見ます。静止した物は、履歴が範囲内にあるので、そのまま蓄積されます。新しく現れた物は、履歴（前の物）が範囲外なので、範囲に引き戻されます。急に暗くなった所は、履歴の明るい色が範囲に押し込まれます。

## 流れのまとめ

| 手順 | 内容 |
| --- | --- |
| **① ジッター** | **投影行列に毎フレーム違うオフセット** |
| **② 描画** | <strong>ジッターした行列でシーンを描く（速度バッファも）</strong> |
| **③ TAA パス** | **速度で履歴を再投影、クランプして、現在と合成** |
| **④ 履歴の更新** | **合成結果を次フレームの履歴として保存**（**2 枚をスワップ**） |
| **⑤ 後処理** | **ブルーム・トーンマップなどは、TAA の後** |


原典は、Karis の "High Quality Temporal Supersampling"（SIGGRAPH 2014、Unreal Engine 4）と、Salvi の "An Excursion in Temporal Supersampling"（GDC 2016）です。ジッター・再投影・クランプという基本の構成は、Karis の発表で確立されました。

原典は、Karis の "High Quality Temporal Supersampling"（SIGGRAPH 2014、Unreal Engine 4）と、Salvi の "An Excursion in Temporal Supersampling"（GDC 2016）です。ジッター・再投影・クランプという基本の構成は、Karis の発表で確立されました。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **バイキュービック（Catmull-Rom）で履歴を読む** | **ぼけを減らす**（[TAA Challenges](taa-challenges.md)） |
| **YCoCg 色空間でクランプ** | **色の範囲がより自然**になり、**ゴーストが減る** |
| <strong>分散クリップ（variance clipping）</strong> | **最小・最大の代わりに平均と分散から範囲を決める** |
| **速度の大きさでブレンド率を変える** | **動く所は現在を多めに** |
| **シャープ化を併用** | **TAA のぼけを戻す** |
| <strong>履歴の拒否（リセット）</strong> | **カット・テレポート・露出の急変で履歴を捨てる** |
| **ジッターを速度から除く** | **静止した物がぶれない**（[Velocity Buffer](../motion-blur/velocity-buffer.md)） |

## よくあるミス

??? failure "静止した物が、ぼやける・ちらつく"
    **ジッターが速度に混ざっている**。**速度から、ジッターを除く**。

??? failure "動く物体の後ろに、ゴースト（残像）が出る"
    **近傍クランプ**を入れる。**速度の精度**を上げる。

??? failure "画面全体が、少しぼやけて見える"
    **バイリニアの履歴読み出しが原因**。**バイキュービック**・**シャープ化**。

??? failure "カット・瞬間移動の後、前の絵が残る"
    **履歴をリセット**（**ブレンド率を 1 に**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] TAA ＝ <strong>毎フレーム サブピクセルずらして描き、履歴と混ぜて、時間方向に蓄積</strong>
    - [x] <strong>ジッター（Halton）</strong>＋<strong>再投影（速度バッファ）</strong>＋<strong>履歴クランプ</strong>＋<strong>合成</strong>
    - [x] <strong>縁・シェーダー内・時間のちらつき</strong>の<strong>すべてに効く</strong>
    - [x] <strong>ゴースト対策がクランプ</strong>。<strong>履歴 90 %・現在 10 %</strong>
    - [x] <strong>ジッターを速度から除く</strong>。<strong>カットで履歴をリセット</strong>

## 参考

- Karis, "High Quality Temporal Supersampling"（SIGGRAPH 2014）
- Salvi, "An Excursion in Temporal Supersampling"（GDC 2016）
- Yang et al., "A Survey of Temporal Antialiasing Techniques"（Eurographics 2020）

## 関連ページ

- [Anti-Aliasing](index.md)
- [TAA Challenges](taa-challenges.md)
- [Velocity Buffer](../motion-blur/velocity-buffer.md)
- [TAA・アップスケーラ・VRS](../../../rendering/taa-upscaling.md)
