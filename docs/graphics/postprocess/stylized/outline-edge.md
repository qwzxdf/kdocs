---
title: Screen-Space Edge Detection
tags:
  - 描画
---

# Screen-Space Edge Detection

<strong>背面法はモデルの外側の輪郭しか出ません</strong>。<strong>モデルの内側の折り目（鼻・袖・服のしわの境）や、物体どうしの境の線も出したい</strong>場合は、画面の画像（深度・法線・ID）から、「値が大きく変わる場所」を検出して線にする、画面空間のエッジ検出を使います。どんな形状でも後処理で線を引けるので柔軟ですが、線の太さの制御や細部のちらつきに注意が必要です。このページでは、深度・法線・ID による検出・Sobel フィルタ・線の太さ・ちらつきの抑制・色の付け方を説明します。

!!! tip "ポイント"
    - エッジ検出 ＝ <strong>隣り合う画素の、深度・法線・ID の差が大きい所を線にする</strong>。
    - <strong>深度</strong>：<strong>物体の輪郭・前後関係の境</strong>。<strong>法線</strong>：<strong>折り目・面の向きが変わる所</strong>。<strong>ID</strong>：<strong>物体・材質の境</strong>。
    - 3 つを<strong>組み合わせる</strong>と<strong>内側の線も外側の線も出る</strong>。
    - <strong>Sobel フィルタ</strong>が<strong>標準</strong>。<strong>勾配の大きさで線の強さ</strong>を決める。
    - <strong>線の太さ</strong>は<strong>サンプル間隔</strong>で調整する。<strong>距離で補正</strong>。
    - <strong>斜めの面で深度の差が出て、不要な線</strong>が出る → <strong>深度勾配で補正</strong>。

## 3 つの検出

<strong>検出に使う画像</strong>は、<strong>不透明パスの出力</strong>（深度バッファ・法線バッファ・ID バッファ）です。

| 入力 | 検出される線 | 弱点 |
| --- | --- | --- |
| 深度 | 物体の外側の輪郭・手前と奥の境 | 同じ深度の折り目は出ない・斜めの面で誤検出 |
| 法線 | <strong>折り目・面の向きの境（内側の線）</strong> | 滑らかな面の境は出ない・法線マップの細かい凹凸で、ノイズ |
| <strong>ID（材質・物体）</strong> | 材質・物体どうしの境 | ID バッファが別途必要 |

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="エッジ検出の入力">
<text x="20" y="26" class="fig-title">深度・法線・ID から、それぞれ違う線が取れる</text>
<g font-size="12">
<g transform="translate(40,52)"><rect x="0" y="0" width="200" height="130" fill="#f1f5f9" stroke="#94a3b8"/><circle cx="100" cy="66" r="42" fill="#cbd5e1"/><circle cx="100" cy="66" r="42" fill="none" stroke="#111827" stroke-width="4"/><text x="0" y="152">深度：外側の輪郭</text></g>
<g transform="translate(290,52)"><rect x="0" y="0" width="200" height="130" fill="#f1f5f9" stroke="#94a3b8"/><rect x="50" y="30" width="100" height="76" fill="#e2e8f0"/><line x1="100" y1="30" x2="100" y2="106" stroke="#111827" stroke-width="4"/><line x1="50" y1="68" x2="150" y2="68" stroke="#111827" stroke-width="4"/><text x="0" y="152">法線：内側の折り目</text></g>
<g transform="translate(540,52)"><rect x="0" y="0" width="200" height="130" fill="#f1f5f9" stroke="#94a3b8"/><rect x="30" y="30" width="70" height="76" fill="#fecaca"/><rect x="100" y="30" width="70" height="76" fill="#bfdbfe"/><line x1="100" y1="30" x2="100" y2="106" stroke="#111827" stroke-width="4"/><text x="0" y="152">ID：物体・材質の境</text></g>
</g>
</svg>

## Sobel フィルタ

<strong>画像の勾配（変化の大きさ）</strong>を<strong>測る標準的な方法</strong>が<strong>Sobel フィルタ</strong>です。周囲 3×3 の画素に、重みを掛けて、縦・横の勾配を求めます。

```hlsl
float Sobel(Texture2D<float> source, float2 uv, float2 texel) {
  float tl = source.SampleLevel(point_clamp, uv + texel * float2(-1, -1), 0);
  float t  = source.SampleLevel(point_clamp, uv + texel * float2( 0, -1), 0);
  float tr = source.SampleLevel(point_clamp, uv + texel * float2( 1, -1), 0);
  float l  = source.SampleLevel(point_clamp, uv + texel * float2(-1,  0), 0);
  float r  = source.SampleLevel(point_clamp, uv + texel * float2( 1,  0), 0);
  float bl = source.SampleLevel(point_clamp, uv + texel * float2(-1,  1), 0);
  float b  = source.SampleLevel(point_clamp, uv + texel * float2( 0,  1), 0);
  float br = source.SampleLevel(point_clamp, uv + texel * float2( 1,  1), 0);
  float gx = (tr + 2.0 * r + br) - (tl + 2.0 * l + bl);
  float gy = (bl + 2.0 * b + br) - (tl + 2.0 * t + tr);
  return sqrt(gx * gx + gy * gy);
}
```

| 点 | 説明 |
| --- | --- |
| `gx`・`gy` | 横方向・縦方向の勾配（重み 1・2・1） |
| `sqrt(gx² + gy²)` | 勾配の大きさ（エッジの強さ） |
| しきい値で 2 値化 | `step(threshold, 強さ)` で、線あり・なし |
| 簡易版 | 上下左右の 4 点だけの差（Roberts Cross など）も使える |

<!-- fig:outline-edge-detect:begin -->

<svg class="fig illust motion" data-fig="outline-edge-detect" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-outline-edge-detect" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">輪郭線(エッジ検出): 深度の差だけでは、同じ深さで、向きが変わる折れ目を見逃す。法線の差も、使う</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">24×12 画素。後ろの壁(深度 10)の前に、手前の箱(深度 4、上面と側面)がある。3 つの方法で、輪郭の画素を、見つける</text>
<rect x="30" y="100" width="300.0" height="150.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">① 深度の差だけ</text>
<rect x="30.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="80.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="92.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="105.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="117.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="130.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="142.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="155.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="167.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="180.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="192.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="205.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="217.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="230.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="242.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="255.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="267.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="280.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="292.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="80.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="92.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="105.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="117.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="130.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="142.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="155.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="167.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="180.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="192.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="205.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="217.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="230.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="242.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="255.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="267.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="280.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="292.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="80.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0800" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="92.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0822" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="105.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0844" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="117.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0867" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="130.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0889" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="142.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0911" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="155.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0933" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="167.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0956" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="180.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0978" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="192.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1000" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="205.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1022" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="217.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1044" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="230.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1067" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="242.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1089" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="255.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1111" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="267.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1133" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="280.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="292.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0800" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="80.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0822" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="92.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0844" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="105.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0867" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="117.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0889" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="130.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0911" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="142.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0933" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="155.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0956" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="167.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0978" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="180.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1000" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="192.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1022" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="205.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1044" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="217.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1067" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="230.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1089" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="242.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1111" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="255.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1133" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="267.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1156" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="280.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1178" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="292.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0822" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="80.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0844" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="92.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="105.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="117.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="130.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="142.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="155.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="167.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="180.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="192.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="205.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="217.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="230.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="242.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="255.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="267.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1178" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="280.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1200" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="292.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0844" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="80.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0867" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="92.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="105.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="117.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="130.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="142.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="155.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="167.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="180.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="192.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="205.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="217.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="230.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="242.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="255.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="267.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1200" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="280.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1222" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="292.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0867" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="80.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0889" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="92.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="105.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="117.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="130.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="142.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="155.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="167.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="180.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="192.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="205.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="217.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="230.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="242.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="255.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="267.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1222" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="280.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1244" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="292.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0889" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="80.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0911" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="92.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="105.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="117.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="130.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="142.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="155.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="167.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="180.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="192.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="205.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="217.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="230.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="242.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="255.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="267.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1244" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="280.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1267" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="292.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0911" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="80.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0933" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="92.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="105.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="117.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="130.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="142.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="155.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="167.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="180.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="192.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="205.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="217.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="230.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="242.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="255.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="267.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1267" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="280.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1289" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="292.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0933" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="80.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0956" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="92.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="105.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="117.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="130.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="142.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="155.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="167.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="180.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="192.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="205.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="217.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="230.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="242.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="255.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="267.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1289" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="280.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1311" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="292.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0956" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="80.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.0978" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="92.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1000" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="105.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1022" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="117.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1044" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="130.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1067" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="142.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1089" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="155.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1111" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="167.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1133" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="180.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1156" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="192.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1178" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="205.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1200" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="217.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1222" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="230.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1244" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="242.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1267" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="255.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1289" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="267.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1311" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="280.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1333" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="292.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="30.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="42.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="55.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="67.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="80.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1000" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="92.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1022" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="105.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1044" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="117.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1067" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="130.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1089" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="142.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1111" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="155.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1133" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="167.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1156" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="180.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1178" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="192.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1200" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="205.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1222" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="217.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1244" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="230.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1267" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="242.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1289" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="255.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1311" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="267.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.1333" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="280.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="292.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="305.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="317.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335" y="100" width="300.0" height="150.0" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="335" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">② 法線の差だけ</text>
<rect x="335.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="385.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="397.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="410.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="422.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="435.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="447.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="460.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="472.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="485.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="497.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="510.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="522.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="535.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="547.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="560.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="572.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="585.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="597.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="385.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="397.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="410.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="422.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="435.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="447.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="460.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="472.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="485.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="497.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="510.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="522.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="535.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="547.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="560.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="572.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="585.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="597.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="385.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2489" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="397.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2511" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="410.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2533" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="422.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2556" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="435.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2578" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="447.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2600" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="460.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2622" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="472.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2644" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="485.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2667" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="497.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2689" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="510.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2711" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="522.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2733" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="535.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2756" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="547.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2778" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="560.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2800" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="572.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2822" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="585.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="597.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2489" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="385.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2511" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="397.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2533" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="410.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2556" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="422.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2578" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="435.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2600" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="447.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2622" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="460.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2644" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="472.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2667" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="485.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2689" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="497.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2711" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="510.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2733" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="522.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2756" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="535.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2778" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="547.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2800" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="560.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2822" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="572.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2844" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="585.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2867" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="597.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2511" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="385.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2533" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="397.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="410.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="422.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="435.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="447.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="460.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="472.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="485.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="497.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="510.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="522.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="535.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="547.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="560.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="572.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2867" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="585.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2889" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="597.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2533" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="385.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2556" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="397.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2578" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="410.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2600" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="422.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2622" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="435.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2644" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="447.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2667" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="460.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2689" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="472.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2711" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="485.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2733" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="497.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2756" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="510.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2778" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="522.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2800" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="535.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2822" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="547.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2844" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="560.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2867" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="572.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2889" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="585.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2911" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="597.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="385.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2578" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="397.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2600" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="410.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2622" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="422.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2644" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="435.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2667" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="447.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2689" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="460.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2711" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="472.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2733" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="485.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2756" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="497.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2778" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="510.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2800" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="522.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2822" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="535.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2844" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="547.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2867" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="560.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2889" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="572.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.2911" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="585.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="597.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="385.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="397.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="410.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="422.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="435.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="447.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="460.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="472.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="485.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="497.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="510.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="522.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="535.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="547.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="560.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="572.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="585.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="597.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="385.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="397.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="410.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="422.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="435.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="447.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="460.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="472.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="485.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="497.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="510.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="522.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="535.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="547.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="560.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="572.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="585.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="597.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="385.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="397.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="410.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="422.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="435.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="447.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="460.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="472.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="485.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="497.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="510.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="522.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="535.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="547.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="560.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="572.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="585.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="597.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="385.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="397.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="410.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="422.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="435.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="447.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="460.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="472.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="485.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="497.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="510.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="522.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="535.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="547.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="560.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="572.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="585.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="597.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="335.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="347.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="360.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="372.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="385.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="397.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="410.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="422.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="435.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="447.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="460.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="472.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="485.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="497.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="510.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="522.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="535.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="547.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="560.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="572.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="585.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="597.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="610.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="622.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640" y="100" width="300.0" height="150.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="640" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">③ 両方</text>
<rect x="640.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="690.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="702.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="715.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="727.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="740.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="752.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="765.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="777.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="790.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="802.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="815.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="827.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="840.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="852.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="865.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="877.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="890.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="902.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="100.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="690.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="702.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="715.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="727.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="740.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="752.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="765.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="777.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="790.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="802.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="815.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="827.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="840.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="852.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="865.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="877.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="890.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="902.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="112.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="690.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4178" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="702.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4200" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="715.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4222" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="727.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4244" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="740.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4267" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="752.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4289" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="765.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4311" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="777.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4333" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="790.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4356" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="802.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4378" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="815.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4400" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="827.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4422" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="840.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4444" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="852.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4467" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="865.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4489" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="877.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4511" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="890.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="902.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="125.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4178" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="690.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4200" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="702.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4222" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="715.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4244" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="727.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4267" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="740.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4289" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="752.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4311" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="765.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4333" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="777.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4356" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="790.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4378" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="802.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4400" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="815.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4422" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="827.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4444" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="840.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4467" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="852.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4489" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="865.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4511" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="877.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4533" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="890.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4556" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="902.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="137.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4200" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="690.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4222" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="702.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="715.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="727.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="740.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="752.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="765.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="777.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="790.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="802.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="815.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="827.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="840.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="852.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="865.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#e2e8f0"/></rect>
<rect x="877.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4556" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="890.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4578" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="902.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="150.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4222" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="690.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4244" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="702.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4267" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="715.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4289" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="727.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4311" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="740.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4333" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="752.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4356" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="765.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4378" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="777.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4400" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="790.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4422" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="802.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4444" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="815.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4467" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="827.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4489" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="840.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4511" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="852.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4533" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="865.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4556" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="877.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4578" values="#f8fafc;#e2e8f0;#111827"/></rect>
<rect x="890.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4600" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="902.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="162.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4244" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="690.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4267" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="702.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4289" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="715.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4311" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="727.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4333" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="740.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4356" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="752.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4378" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="765.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4400" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="777.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4422" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="790.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4444" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="802.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4467" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="815.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4489" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="827.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4511" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="840.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4533" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="852.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4556" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="865.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4578" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="877.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4600" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="890.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4622" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="902.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="175.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4267" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="690.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4289" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="702.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="715.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="727.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="740.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="752.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="765.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="777.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="790.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="802.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="815.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="827.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="840.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="852.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="865.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="877.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4622" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="890.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4644" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="902.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="187.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4289" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="690.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4311" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="702.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="715.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="727.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="740.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="752.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="765.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="777.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="790.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="802.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="815.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="827.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="840.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="852.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="865.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="877.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4644" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="890.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4667" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="902.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="200.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4311" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="690.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4333" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="702.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="715.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="727.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="740.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="752.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="765.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="777.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="790.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="802.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="815.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="827.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="840.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="852.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="865.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#cbd5e1"/></rect>
<rect x="877.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4667" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="890.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4689" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="902.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="212.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4333" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="690.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4356" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="702.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4378" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="715.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4400" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="727.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4422" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="740.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4444" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="752.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4467" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="765.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4489" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="777.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4511" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="790.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4533" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="802.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4556" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="815.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4578" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="827.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4600" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="840.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4622" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="852.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4644" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="865.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4667" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="877.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4689" values="#f8fafc;#cbd5e1;#111827"/></rect>
<rect x="890.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4711" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="902.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="225.0" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="640.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="652.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="665.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="677.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="690.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4378" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="702.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4400" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="715.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4422" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="727.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4444" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="740.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4467" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="752.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4489" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="765.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4511" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="777.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4533" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="790.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4556" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="802.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4578" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="815.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4600" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="827.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4622" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="840.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4644" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="852.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4667" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="865.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4689" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="877.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133;0.4711" values="#f8fafc;#f1f5f9;#111827"/></rect>
<rect x="890.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="902.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="915.0" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<rect x="927.5" y="237.5" width="12.8" height="12.8" fill="#f8fafc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#f8fafc;#f1f5f9"/></rect>
<text x="30" y="280" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">箱の上面と前面の境(深度は同じ 4)が、輪郭に、なるか?</text>
<text x="30" y="320" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">輪郭の画素:</text>
<text x="150" y="324" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1465;0.1467;1.0000" values="1;1;0;0"/></text>
<text x="150" y="324" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">92<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1465;0.1467;0.3154;0.3156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="324" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">72<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3154;0.3156;0.4843;0.4844;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="324" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">120<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4843;0.4844;1.0000" values="0;0;1;1"/></text>
<text x="30" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">深度だけ: 92 画素。箱の折れ目の 28 画素を見逃す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5732;0.5733;1.0000" values="0;0;1;1"/></text>
<text x="30" y="386" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">法線だけ: 72 画素。背景と前面は向きが同じなので、箱の左右・下の外側を見逃す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6176;0.6178;1.0000" values="0;0;1;1"/></text>
<text x="30" y="412" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb" opacity="0">両方: 120 画素。外側も、折れ目も、拾える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6620;0.6622;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000" values="0;0;1;1"/><rect x="560" y="340" width="370" height="120" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="576" y="364" text-anchor="start" style="font-size:14px;font-weight:700;fill:#991b1b">深度 = 輪郭の外側(物と背景)</text>
<text x="576" y="387" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">法線 = 輪郭の内側(折れ目)</text>
<text x="576" y="410" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">両方を足すと、きれいな線画になる</text>
<text x="576" y="433" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">読み込み: 各画素で、深度と法線を 4 近傍に読む</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画面の絵から、輪郭線を作る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">深度の差・法線の差で、隣と違う画素を見つける<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.5732;0.5733;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">どちらか一方だと、線が足りない<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5732;0.5733;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:outline-edge-detect:end -->

## 深度によるエッジ

<strong>線形化した深度</strong>に<strong>Sobel を適用</strong>し、差が一定以上の所を線にします。

```hlsl
float DepthEdge(float2 uv) {
  float center = LinearDepth(uv);
  float edge = Sobel(linear_depth, uv, texel);
  float threshold = kDepthThreshold * center;
  return step(threshold, edge);
}
```

深度の扱いの要点です。線形な深度を使います（非線形な深度では遠くで差が出ません）。しきい値を深度に比例させます（遠い物体ほど深度の差が大きく出るため補正します）。斜めの面の誤検出は、地面のような斜めの面で、隣の画素の深度が少し違う（勾配）ことで起きるので、深度の勾配を法線から予測して差し引きます。

### 斜めの面の誤検出の対策

<strong>斜めの面では隣の画素との深度の差が、自然に生じます</strong>（<strong>エッジではない</strong>）。法線と視線の角度から、その差の予想値を求め、予想を超える差だけをエッジとします。

```hlsl
float DepthEdgeCorrected(float2 uv, float3 normal, float3 view_dir) {
  float center = LinearDepth(uv);
  float cos_angle = abs(dot(normal, view_dir));
  float expected_difference = center * texel_world_size / max(cos_angle, 0.05);
  float edge = Sobel(linear_depth, uv, texel);
  return step(expected_difference * kSlopeScale + kBias, edge);
}
```

## 法線によるエッジ

<strong>隣り合う法線の差（内積）が小さい所</strong>が<strong>折り目</strong>です。

```hlsl
float NormalEdge(float2 uv) {
  float3 n = normal_buffer.SampleLevel(point_clamp, uv, 0).xyz * 2.0 - 1.0;
  float3 n_r = normal_buffer.SampleLevel(point_clamp, uv + float2(texel.x, 0), 0).xyz * 2.0 - 1.0;
  float3 n_b = normal_buffer.SampleLevel(point_clamp, uv + float2(0, texel.y), 0).xyz * 2.0 - 1.0;
  float d = (1.0 - dot(n, n_r)) + (1.0 - dot(n, n_b));
  return step(kNormalThreshold, d);
}
```

法線の扱いの要点です。`1 − dot(n, n_neighbor)` は、同じ向きなら 0、直角なら 1 になります。法線マップの影響で、細かい凹凸の法線マップが入るとノイズになるので、ジオメトリの法線（法線マップなし）を別に使います。

## ID によるエッジ

<strong>物体 ID・材質 ID を画素ごとに別のバッファへ書き</strong>、<strong>隣と ID が違えば線</strong>とします。

ID の使い道です。物体どうしの境として、キャラクターと背景の境やキャラ同士の境を出せます。材質の境として、髪と肌、服と肌を分けられます。選択した物体の強調として、選択された ID だけ輪郭を出すこともできます（ハイライト）。

```hlsl
float IdEdge(float2 uv) {
  uint id = id_buffer.Load(int3(uv * resolution, 0));
  uint id_r = id_buffer.Load(int3(uv * resolution + int2(1, 0), 0));
  uint id_b = id_buffer.Load(int3(uv * resolution + int2(0, 1), 0));
  return (id != id_r || id != id_b) ? 1.0 : 0.0;
}
```

## 線の太さ

| 方法 | 内容 |
| --- | --- |
| サンプル間隔を広げる | `texel × 2` など、隣より離れた画素と比べると、線が太くなる |
| 距離による補正 | <strong>遠くで間隔を狭める（細く）</strong>・近くで広げる |
| 複数の間隔を混ぜる | 細い線 ＋ 太い線で強弱 |
| ぼかしで太く | 検出後に軽くぼかして太くする |

<strong>注意</strong>：<strong>間隔を広げると離れた 2 点の差を見るので、細かい形状の線が出にくく</strong>なります。

## ちらつきと安定

<strong>画面空間のエッジは、カメラが動くと検出される画素が変わり、線がちらつく</strong>ことが<strong>あります</strong>。

| 対策 | 内容 |
| --- | --- |
| TAA で平均 | TAA の後に線を引くのではなく、線を引いてから TAA で滑らかに |
| <strong>しきい値にソフトな境（`smoothstep`）</strong> | 線の強さが連続的に変わる |
| アンチエイリアス済みの深度・法線から検出 | ジャギーが少ない |
| 線をジオメトリ側（背面法）で出す部分を併用 | 外側の輪郭は背面法で安定 |

## 色の付け方

| 方法 | 内容 |
| --- | --- |
| 黒 | 標準 |
| 元の色の暗い版 | <strong>柔らかい絵（線が浮かない）</strong> |
| 材質ごとの色 | 肌は赤っぽい、髪は暗い |
| 深度でフェード | 遠くの線を薄く |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 深度・法線・ID を組み合わせる | 内側・外側の線を両方 |
| 斜めの面の補正 | 地面の誤検出を防ぐ |
| <strong>ジオメトリの法線（法線マップなし）</strong> | 細かい凹凸でノイズが出ない |
| TAA を併用 | ちらつきを抑える |
| 背面法と併用 | 外側は背面法、内側は画面空間 |
| 線の強さを `smoothstep` | 滑らか |

## よくあるミス

??? failure "地面（斜めの面）に、縞のような線が出る"
    <strong>深度の勾配補正</strong>を入れる。

??? failure "法線マップのせいで、細かい線がうるさい"
    <strong>法線マップを含まない、ジオメトリの法線</strong>を別に書く。

??? failure "遠くで線が太く、近くで細い"
    <strong>距離でサンプル間隔を補正</strong>する。

??? failure "動くと線がちらつく"
    <strong>`smoothstep` で滑らかに</strong>、<strong>TAA を併用</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 画面空間エッジ ＝ <strong>隣の画素との、深度・法線・ID の差が大きい所を線にする</strong>
    - [x] <strong>深度は外側の輪郭、法線は内側の折り目、ID は物体・材質の境</strong>
    - [x] <strong>Sobel フィルタ</strong>で<strong>勾配の大きさ</strong>を測る
    - [x] <strong>斜めの面の誤検出</strong>は<strong>深度勾配の補正</strong>で防ぐ
    - [x] <strong>背面法と併用</strong>。<strong>TAA でちらつきを抑える</strong>

## 参考

- Saito & Takahashi, "Comprehensible Rendering of 3-D Shapes"（SIGGRAPH 1990）
- Decaudin, "Cartoon-Looking Rendering of 3D-Scenes"（1996）
- Vergne et al., "Apparent Relief"（SIGGRAPH 2011）

## 関連ページ

- [Outlines and Toon](index.md)
- [Inverted Hull Outlines](outline-hull.md)
- [Cel Shading](cel-shading.md)
- [TAA](../antialiasing/taa.md)
