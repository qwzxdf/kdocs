---
title: ポストプロセス
tags:
  - 最適化
  - 3Dゲーム
---

# ポストプロセス

ポストプロセスは、描き終えた画面全体に掛ける効果です。ブルーム・トーンマップ・被写界深度・モーション ブラー・色調整・アンチエイリアスなどがあります。1 つ 1 つは軽くても、**全画面を何度も読み書き**するので、積み重なると帯域幅が大きく消費されます。このページでは、ポストプロセスの何が重いのか、どうまとめるかを説明します。

!!! tip "ポイント"
    - 全画面のパスは、<strong>画面サイズのテクスチャを読んで書く</strong>。1 パスで約 16〜33 MB の帯域を使う（1080p・FP16 の場合）。
    - パスが 10 個あれば、帯域は 10 倍。<strong>パスをまとめる</strong>のが基本。
    - ぼかしなどは縮小して計算する。
    - フォーマットを必要以上に重くしない（R11G11B10 など）。
    - 見た目への影響が小さい効果は、やめる。
    - 効果の順序にも意味がある（HDR のうちに行うもの、トーンマップ後に行うもの）。

## 何が重いのか

| 重い所 | 説明 |
| --- | --- |
| **画面サイズの読み書き** | 1 パスごとに入力を読んで出力を書く |
| パスの数 | 効果ごとに別パスにすると、読み書きが積み重なる |
| ぼかしの読み込み回数 | 大きなカーネルは、1 ピクセルあたり数十回読む |
| HDR フォーマット | RGBA16F は 1 ピクセル 8 バイト。RGBA8 の 2 倍 |
| 深度の読み込み | DOF・フォグ・SSAO などが深度バッファを何度も読む |

1920×1080・RGBA16F（8 バイト）の画像 1 枚は約 16 MB です。1 パスで読み書きすると約 33 MB。60 FPS・10 パスで約 20 GB/s の帯域になります。

## パスをまとめる

| 工夫 | 説明 |
| --- | --- |
| **トーンマップ・カラー グレーディング・ビネット・ガンマを 1 パスに** | 1 回の読み込みで全部の計算をする（ALU は安い） |
| LUT で色調整 | 複雑な色の計算を、3D テクスチャ（LUT）の参照 1 回にする |
| ブルームの合成とトーンマップを一緒に | 合成と最終変換を 1 パスで |
| アンチエイリアスとシャープを一緒に | TAA の出力にシャープを足す |

ALU の計算は安く、メモリ読み込みが高いので、計算を足してでもパスを減らすほうが得です。

## 縮小して計算する

| 効果 | 縮小の方法 |
| --- | --- |
| **ブルーム** | 段階的に半分に縮小しながらぼかす（ダウンサンプル チェーン）。上りながら足し合わせる |
| 被写界深度のぼかし | 半分解像度でぼかし、境界を深度で合わせて合成する |
| モーション ブラー | タイル単位で最大の動きを求めて、必要な場所だけぼかす |
| SSAO・SSR | 半分解像度で計算して、深度を考慮して拡大する（[低解像度のエフェクト](low-res-effects.md)） |

ブルームのダウンサンプル チェーンは、1 段ごとに面積が 1/4 になるので、全体で元の約 1.33 倍の計算で済みます。大きなガウスぼかしを 1 回かけるよりも、はるかに安くなります。

## ぼかしの工夫

| 工夫 | 説明 |
| --- | --- |
| **分離可能フィルタ** | 2D のガウスぼかしを、横 1 回 + 縦 1 回に分ける（N×N → 2N 回） |
| バイリニアを使った半減 | テクセルの間をサンプルして、1 回の読み込みで 2 点分を得る |
| groupshared の利用 | コンピュートでタイル内の読み込みを共有メモリにまとめる |
| カーネルを小さく | 縮小と組み合わせて、小さなカーネルで済ませる |

## フォーマットの選択

| フォーマット | サイズ | 用途 |
| --- | --- | --- |
| **RGBA16F** | 8 バイト | 高品質な HDR。アルファが必要な場合 |
| R11G11B10_FLOAT | 4 バイト | HDR のカラーだけ（アルファなし）。帯域が半分 |
| RGBA8 | 4 バイト | LDR（トーンマップ後・UI 前） |
| R8 | 1 バイト | マスク・AO・単色の中間結果 |

中間バッファのフォーマットを軽くするだけで、帯域は大きく減ります（[メモリ帯域幅](bandwidth.md)）。

## 効果の順序

| 段階 | 例 |
| --- | --- |
| **HDR 空間で行う** | ブルーム・DOF・モーション ブラー・フォグ |
| トーンマップ | HDR を LDR に変換する |
| LDR 空間で行う | カラー グレーディング・ビネット・フィルム グレイン・FXAA |
| UI | 最後に出力解像度で描く |

順序を間違えると見た目が不自然になります。ブルームは必ず HDR のうちに行います。

## 帯域を、パスの数で、計算する

1920×1080 の画像 1 枚は、フォーマットで、大きさが変わります。1 パスは、「入力を読み、出力を書く」ので、2 枚ぶんです。

| フォーマット | 1 枚の大きさ | 1 パス（読み + 書き） | 60 FPS、10 パス |
| --- | --- | --- | --- |
| RGBA16F（8 バイト） | 約 16.6 MB | 約 33 MB | 約 20 GB/s |
| R11G11B10F（4 バイト） | 約 8.3 MB | 約 17 MB | 約 10 GB/s |
| RGBA8（4 バイト） | 約 8.3 MB | 約 17 MB | 約 10 GB/s |

フォーマットを、半分にすれば、帯域も、半分です。<strong>パスを 10 から 3 に</strong>減らせば、帯域は、さらに、約 3 分の 1 です。両方で、約 1/6 になります。

## 最終パスを、1 つにまとめる

トーン マッピング、カラー グレーディング（LUT）、ビネット、フィルム グレインを、<strong>1 つのパス</strong>で行います。入力を読むのは、1 回だけです。

```hlsl
Texture2D<float3> g_scene : register(t0);                     // HDR のシーン
Texture3D<float3> g_lut : register(t1);                       // カラー グレーディングの 3D LUT（32³）
Texture2D<float> g_bloom : register(t2);
SamplerState g_linear_clamp : register(s0);

cbuffer FinalCB : register(b0) {
  float g_exposure;
  float g_vignette_strength;
  float g_grain_strength;
  float g_time;
};

float3 TonemapAces(float3 x) {                                // ACES の近似（Narkowicz）
  return saturate((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14));
}

float4 PSFinal(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float3 color = g_scene.Load(int3(pos.xy, 0));               // ① 読むのは、ここ 1 回
  color += g_bloom.Sample(g_linear_clamp, uv);                // ブルームを足す（HDR のうちに）
  color *= g_exposure;                                        // 露出
  color = TonemapAces(color);                                 // トーン マッピング（HDR → LDR）

  // カラー グレーディング: LUT を引く。LUT の端に、半テクセルの余白を足して、補間の誤差を避ける。
  float3 lut_uv = color * (31.0 / 32.0) + 0.5 / 32.0;
  color = g_lut.SampleLevel(g_linear_clamp, lut_uv, 0);

  // ビネット: 画面の端を暗く。
  float2 d = uv - 0.5;
  color *= 1.0 - g_vignette_strength * dot(d, d) * 2.0;

  // フィルム グレイン: 軽いノイズを足す（LDR のうちに）。
  float noise = frac(sin(dot(pos.xy + g_time, float2(12.9898, 78.233))) * 43758.5453) - 0.5;
  color += noise * g_grain_strength;

  return float4(color, 1.0);                                  // ② 書くのは、ここ 1 回
}
```

数行ずつ見ると、読み込み（①）が 1 回、書き込み（②）が 1 回です。個別のパスで行うと、4 回の読み書き（約 130 MB）になる所が、1 回（約 33 MB）に減ります。ALU の計算（ACES、LUT の補間、ビネット）は、安いので、計算を足して、パスを減らすほうが、得です（[Tone Mapping and Exposure](../graphics/postprocess/tonemapping/index.md)、[3D LUT](../graphics/postprocess/color-grading/lut-3d.md)）。

## ガウスぼかしを、バイリニアで、半分の回数に

分離可能な、ガウスぼかしは、横 1 回 + 縦 1 回に分けて、サンプルを、N 回にできます。さらに、<strong>テクセルの間を、バイリニアで読む</strong>と、1 回の読み込みで、2 つのテクセルぶんが、得られ、回数が、ほぼ半分になります。

```hlsl
// 9 タップのガウス（横方向）を、5 回の読み込みで行う。重みとオフセットは、バイリニアで 2 点分を、1 回にまとめた値。
static const float kOffsets[3] = {0.0, 1.3846153846, 3.2307692308};
static const float kWeights[3] = {0.2270270270, 0.3162162162, 0.0702702703};

float3 BlurHorizontal(Texture2D<float3> src, SamplerState linear_clamp, float2 uv, float2 texel) {
  float3 color = src.SampleLevel(linear_clamp, uv, 0) * kWeights[0];
  for (int i = 1; i < 3; ++i) {
    float2 offset = float2(kOffsets[i] * texel.x, 0.0);
    color += src.SampleLevel(linear_clamp, uv + offset, 0) * kWeights[i];
    color += src.SampleLevel(linear_clamp, uv - offset, 0) * kWeights[i];
  }
  return color;
}
```

重みの合計は `0.2270 + 2 × (0.3162 + 0.0703) ≈ 1.0` です。9 タップが、5 回の読み込みで済みます（[Gaussian Blur](../graphics/postprocess/bloom/gaussian.md)）。さらに、縮小してから、ぼかすと、ピクセル数が 1/4 になり、同じ見た目で、数倍速くなります。

## よくあるミス

??? failure "効果ごとに別パスにして、全画面を何度も読み書きする"
    LUT・まとめたパスで減らします。

??? failure "大きなカーネルのぼかしを、フル解像度で 1 回かける"
    縮小して、分離可能フィルタにします。

??? failure "中間バッファを RGBA32F にしている"
    R11G11B10 や FP16 で足ります。

??? failure "ブルームをトーンマップ後に行う"
    HDR のうちに行います。

??? failure "見た目の効果が小さいのに、重い効果を残す"
    A/B で比べて、効果が薄いものは外します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全画面パスは帯域幅を消費する。パス数が肝
    - [x] パスをまとめる。ALU は安く、メモリが高い
    - [x] ぼかしは縮小・分離可能フィルタで軽く
    - [x] 中間バッファのフォーマットを軽く
    - [x] 効果の順序（HDR → トーンマップ → LDR → UI）を守る

## 関連ページ

- [描画最適化](index.md)
- [メモリ帯域幅](bandwidth.md)
- [低解像度のエフェクト](low-res-effects.md)
- [TAA・アップスケーラ・VRS](taa-upscaling.md)
- [Post-Processing](../graphics/postprocess/index.md)
