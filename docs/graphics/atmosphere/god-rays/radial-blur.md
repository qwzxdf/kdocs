---
title: 画面空間の放射ぼかし
tags:
  - 描画
---

# 画面空間の放射ぼかし

**太陽の画面上の位置から外側へ、画像を放射状にぼかして、光の筋を作る**のが**最も手軽**な方法です。**太陽が画面内にある時だけ使え、遮蔽物の形が筋に反映されます**。このページでは、**放射ぼかし**を説明します。

!!! tip "ポイント"
    - **明るい部分を抽出し、太陽の位置から放射状にぼかす**。
    - **遮蔽物の影が、筋として現れる**。
    - **太陽が画面外にあると、使えない**。
    - **サンプル数が少ないと、縞が出る**。

## 画面空間の放射ぼかし
**画面上の太陽の位置を中心に、各ピクセルから太陽へ向かう直線上の明るさを、何度かサンプルして足し合わせる**方法です。**簡単・安価で古くから使われています**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="放射ぼかし">
<text x="20" y="24" class="fig-title">放射ぼかし：各ピクセルから太陽に向かって、明るさを平均する</text>
<rect x="60" y="50" width="360" height="160" fill="#87ceeb" fill-opacity="0.2" stroke="currentColor" stroke-opacity="0.5"/>
<circle cx="360" cy="80" r="14" fill="#e5aa28"/>
<polygon points="120,210 160,100 190,210" fill="#333"/><polygon points="220,210 240,120 270,210" fill="#333"/>
<g stroke="#e5aa28" stroke-dasharray="4 3"><line x1="150" y1="180" x2="360" y2="80"/><line x1="250" y1="190" x2="360" y2="80"/></g>
<circle cx="150" cy="180" r="4" fill="#e5484d"/><circle cx="250" cy="190" r="4" fill="#e5484d"/>
<g font-size="12">
<text x="450" y="80" style="font-weight:700">手順</text>
<text x="450" y="104">① 太陽の画面上の位置を求める</text>
<text x="450" y="126">② 明るい所（空）を別の画像に抜き出す（物は黒）</text>
<text x="450" y="148">③ 各ピクセルから太陽へ向かう線上を、</text><text x="450" y="166">　 数十回サンプルして足す（減衰しながら）</text>
<text x="450" y="188">④ 元の絵に加算</text>
</g>
</svg>

```hlsl
float3 GodRays(float2 uv, float2 sun_uv) {
  float2 delta = (uv - sun_uv) * (density / kSampleCount);
  float2 sample_uv = uv;
  float illumination_decay = 1.0;
  float3 accumulated = 0;

  for (int i = 0; i < kSampleCount; ++i) {
    sample_uv -= delta;
    float3 sample_color = occlusion_texture.Sample(linear_clamp, sample_uv).rgb;
    sample_color *= illumination_decay * weight;
    accumulated += sample_color;
    illumination_decay *= decay;
  }
  return accumulated * exposure;
}
```

| 点 | 説明 |
| --- | --- |
| **`occlusion_texture`** | **空の明るい部分だけが残り、物は黒**の画像（深度から作る） |
| **`decay`** | **0.95〜0.99**。**光源から遠いほど弱くする** |
| **`density`** | **ぼかしの長さ**（0.5〜1.0） |
| **サンプル数** | **32〜100**。**半解像度で描く**と**軽い** |
| **欠点** | **太陽が画面の外だと使えない**。**太陽の向きを見ていないと、筋が消える**。**空気の濃さ・影の奥行きは表現できない** |

**太陽が画面外のときにも自然にするため**、**太陽が画面に近いほど強く、離れると弱くする**フェードを**付けます**。

## よくあるミス

??? failure "太陽が画面外に出ると、光の筋が消える"
    **他の方式**に**切り替える**、または**フェード**させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **太陽から放射状にぼかす。手軽だが制約あり**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [ゴッド レイ](index.md)
- [ガウスぼかし](../../postprocess/bloom/gaussian.md)
