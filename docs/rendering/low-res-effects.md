---
title: 縮小バッファの効果
tags:
  - 最適化
  - 3Dゲーム
---

# 縮小バッファの効果

**AO（環境光遮蔽）・ブルーム・ボリューメトリック フォグ・被写界深度・SSR** などの画面全体に対する効果は、ピクセル数に比例して重くなります。しかし、これらの効果はもともとぼんやりした（低周波な）結果なのでフル解像度で計算する必要がありません。半分・4 分の 1 の解像度で計算し、最後に拡大して合成すれば、計算量・帯域幅が 4 分の 1・16 分の 1になります。このページは縮小バッファの考え方、拡大（アップサンプル）の注意、ほかの解像度の工夫を説明します。

!!! tip "ポイント"
    - 目的：<strong>ピクセル数に比例する効果のコスト削減</strong>。<strong>半分解像度 → 1/4、4 分の 1 解像度 → 1/16</strong>。
    - 向く効果：AO・ブルーム・フォグ・DOF・SSR・パーティクル（煙） ＝ ぼやけた・滑らかな結果。
    - 向かない：鋭い輪郭が必要なもの（UI・文字・細い影）。
    - 注意点：拡大時に物体の境界でにじむ。→ 深度を使った拡大（バイラテラル アップサンプル）。
    - ダウンサンプルの取り方：単純な間引きは、ちらつく。平均・最大・最小深度など 用途で選ぶ。
    - 関連：動的解像度・TAA・チェッカーボード。

## なぜ縮小して良いのか

<svg class="fig illust" viewBox="0 0 800 250" role="img" aria-label="縮小バッファの、計算量">
<defs><marker id="lr1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">フル解像度（100%）と、半分解像度（25%）と、4 分の 1 解像度（6%）</text>
<rect x="20" y="50" width="200" height="120" fill="rgba(229,72,77,0.3)" stroke="currentColor" stroke-width="2"/><text x="120" y="116" text-anchor="middle" style="font-weight:700">1920×1080</text><text x="120" y="136" text-anchor="middle" style="font-size:12px">計算量 100%</text>
<line x1="226" y1="110" x2="276" y2="110" stroke="currentColor" stroke-width="3" marker-end="url(#lr1)"/>
<rect x="284" y="80" width="100" height="60" fill="rgba(229,170,40,0.4)" stroke="currentColor" stroke-width="2"/><text x="334" y="106" text-anchor="middle" style="font-weight:700">960×540</text><text x="334" y="126" text-anchor="middle" style="font-size:12px">計算量 25%</text>
<line x1="390" y1="110" x2="440" y2="110" stroke="currentColor" stroke-width="3" marker-end="url(#lr1)"/>
<rect x="448" y="95" width="50" height="30" fill="rgba(46,160,67,0.45)" stroke="currentColor" stroke-width="2"/><text x="473" y="114" text-anchor="middle" style="font-size:10px">480×270</text><text x="473" y="142" text-anchor="middle" style="font-size:12px">計算量 6%</text>
<text x="20" y="206" style="font-size:12px">AO・ブルーム・フォグは、結果が、ぼやけている。低い解像度で計算して、拡大しても、見た目が、ほぼ変わらない</text>
<text x="20" y="226" style="font-size:12px">計算量・書き込み・読み込み（帯域幅）が、同じ割合で、減る</text>
</svg>

| 効果 | 縮小の目安 |
| --- | --- |
| **SSAO・GTAO** | 半分解像度（さらにブラーで整える） |
| ブルーム | 段階的に半分ずつ縮小（ブラーは縮小した画像で） |
| ボリューメトリック フォグ | 画面の 3D グリッド（160×90×64 など。画面よりはるかに小さい） |
| 被写界深度（DOF） | 半分解像度でぼかし |
| SSR（反射） | 半分解像度（[Hi-Z とスクリーン空間トレース](hiz.md)） |
| パーティクル（煙・霧） | 半分・4 分の 1（[オーバードロー](overdraw.md)） |
| 影のブラー・ソフトシャドウ | 縮小で計算 |

## 拡大（アップサンプル）の問題

**単純に拡大**（バイリニア）すると物体の境界で遠くの値と近くの値が混ざって、にじみます（AO が物体の縁にはみ出す・ハロー）。

| 方法 | 説明 |
| --- | --- |
| バイラテラル アップサンプル | 拡大時にフル解像度の深度と縮小バッファの深度を比べ、近い深度の画素だけを重み付けで混ぜる |
| ナイボー（最近傍）＋深度 | 最も深度が近い縮小画素を選ぶ |
| TAA で時間的に整える | 毎フレーム、サンプルをずらし、時間で平均（[その他の最適化](taa-upscaling.md)） |

```hlsl
float4 UpsampleDepthAware(float2 uv, float full_depth) {
  float4 result = 0;
  float weight_sum = 0;
  for (int i = 0; i < 4; ++i) {
    float low_depth = low_res_depth.SampleLevel(point_sampler, uv, 0, offsets[i]);
    float w = 1.0 / (abs(full_depth - low_depth) + 0.0001);
    result += low_res_color.SampleLevel(point_sampler, uv, 0, offsets[i]) * w;
    weight_sum += w;
  }
  return result / weight_sum;
}
```

| 点 | 説明 |
| --- | --- |
| 重み | 深度の差が小さい画素ほど重い |
| 効果 | 境界がにじまない |

## ダウンサンプルの取り方

**縮小時に 4 画素から 1 画素を作る**方法で結果が変わります。

| 方法 | 向く用途 |
| --- | --- |
| 平均（バイリニア） | 色（ブルーム） |
| 間引き（1 画素だけ取る） | ちらつく。避ける（TAA で補うなら可） |
| 最小深度・最大深度 | 深度（Hi-Z。カリングは保守的に）（[Hi-Z](hiz.md)） |
| 最も手前（最小）の深度 | AO・フォグなど深度で拡大するときの基準 |

## そのほかの解像度の工夫

| 手法 | 説明 |
| --- | --- |
| **動的解像度** | 負荷に応じて、描画解像度をフレームごとに変える。UI はフル解像度（[フレームの予算](../optimize/frame-budget.md)） |
| アップスケーラ（DLSS・FSR・TAAU） | 低解像度で描き、時間情報で高解像度へ（品質を保つ） |
| チェッカーボード レンダリング | 半分のピクセルを市松模様で描き、前フレームで補う |
| 可変レート シェーディング（VRS） | 画面の場所ごとにシェーディングの細かさを変える（[その他の最適化](taa-upscaling.md)） |
| ハーフ解像度のライティング | 拡散ライティングだけを、縮小で（鏡面はフル） |

## 深度を使って境界をにじませずに拡大する

縮小して描いた結果を普通のバイリニアで、拡大すると物体の<strong>輪郭がにじみ</strong>ます。低解像度の 1 ピクセルが手前の物と奥の物の両方にまたがっているためです。フル解像度の深度と低解像度の深度を比べて、「近い深度のサンプル」から色を取ります。

```hlsl
Texture2D<float4> g_low_color : register(t0);       // 低解像度の結果（煙、AO、ブルームなど）
Texture2D<float> g_low_depth : register(t1);        // 低解像度の深度（縮小時に、最大か最小で作る）
Texture2D<float> g_full_depth : register(t2);       // フル解像度の深度
SamplerState g_point_clamp : register(s0);

cbuffer UpsampleCB : register(b0) {
  float2 g_low_size;                                // 低解像度の大きさ（ピクセル）
  float2 pad;
};

// 4 つの、近い低解像度ピクセルのうち、フル解像度の深度に、最も近い深度を持つものを、採る。
float4 PSUpsample(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  const float full_z = LinearizeDepth(g_full_depth.SampleLevel(g_point_clamp, uv, 0));
  const int2 base = int2(floor(uv * g_low_size - 0.5));       // 低解像度の、左上のピクセル

  float4 best_color = 0;
  float best_diff = 1e9;
  [unroll] for (int i = 0; i < 4; ++i) {
    const int2 q = clamp(base + int2(i & 1, i >> 1), 0, int2(g_low_size) - 1);
    const float low_z = LinearizeDepth(g_low_depth.Load(int3(q, 0)));
    const float diff = abs(low_z - full_z);                    // フル解像度の深度との、差
    if (diff < best_diff) {
      best_diff = diff;
      best_color = g_low_color.Load(int3(q, 0));               // 深度が、いちばん近いサンプルの色
    }
  }
  return best_color;
}
```

数行ずつ見ると 「このピクセルと同じ物体にいる、低解像度のピクセル」を深度で選んで、その色をそのまま使います。手前の物体のピクセルは手前の低解像度の色を奥は奥の色を使うので輪郭が、にじみません。ただし、色を混ぜずに選ぶので階段状に見えることがあります。

| 方式 | 内容 | 向く場面 |
| --- | --- | --- |
| バイリニア | 4 つを距離で混ぜる。最も安い | 輪郭が目立たない物（霧、ブルーム） |
| 最近深度（上のコード） | 深度が、近い 1 つを選ぶ | 輪郭のある物の前の煙 |
| 深度で重みづけ | 4 つを深度の近さで、重みづけして混ぜる | 階段が気になるとき（少し重い） |
| 法線も使う | 深度に加えて、法線の近さも見る | AO など面の向きで変わる物 |

## 縮小時の深度の作り方

低解像度の深度はフル解像度の深度から、<strong>縮小して作ります</strong>。平均は使わず 最大（遠い）か最小（近い）を選びます。平均すると手前と奥の間の存在しない深度ができて境界で、おかしくなるためです。

```hlsl
// 2×2 のフル解像度の深度から、最大（最も遠い）を取って、低解像度の深度にする。
float DownsampleDepth(int2 p) {
  float d0 = g_full_depth.Load(int3(p * 2 + int2(0, 0), 0));
  float d1 = g_full_depth.Load(int3(p * 2 + int2(1, 0), 0));
  float d2 = g_full_depth.Load(int3(p * 2 + int2(0, 1), 0));
  float d3 = g_full_depth.Load(int3(p * 2 + int2(1, 1), 0));
  return max(max(d0, d1), max(d2, d3));                       // 通常の深度（0 が近い）なら max が、最も遠い
}
```

縮小する深度が最大か最小かは用途で選びます。煙（手前の物の後ろに隠れるべき）は 最小（最も近い）を選ぶと手前の物に煙が、はみ出しにくくなります。

## よくあるミス

??? failure "バイリニアで拡大して、物体の縁ににじみ（ハロー）が出る"
    **深度を使ったアップサンプル**にします。

??? failure "鋭い輪郭が、必要な物を縮小してぼやける"
    UI・文字・シャープな影は、フル解像度で。

??? failure "縮小時に間引いて、ちらつく"
    平均にするTAA を併用します。

??? failure "縮小バッファのフォーマットを重いまま使う"
    フォーマットも軽くします（[メモリ帯域幅](bandwidth.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 縮小バッファ ＝ <strong>ぼやけた効果を低解像度で計算</strong>。半分で 1/4、4 分の 1 で 1/16
    - [x] 向く：AO・ブルーム・フォグ・DOF・SSR・煙。UI・文字はフル解像度
    - [x] 拡大は深度を考慮（バイラテラル）。単純な拡大は境界がにじむ
    - [x] ダウンサンプルは用途で選ぶ（色は平均、深度は最小・最大）
    - [x] 動的解像度・アップスケーラ・チェッカーボードも同じ発想

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [メモリ帯域幅](bandwidth.md)
- [Hi-Z とスクリーン空間トレース](hiz.md)
- [オーバードロー](overdraw.md)
- [その他の最適化](taa-upscaling.md)
- [Ambient Occlusion (AO)](../graphics/ao/index.md)
- [Bloom](../graphics/postprocess/bloom/index.md)
