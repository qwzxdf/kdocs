---
title: Hiding Tiling
tags:
  - 描画
---

# Hiding Tiling

<strong>タイル テクスチャは広い範囲に貼ると、繰り返しが目立ちます</strong>。大きさの違うテクスチャを重ねる・ランダムに回転させることで、隠せます。このページではタイリングの隠し方を説明します。

!!! tip "ポイント"
    - 異なるスケールで 2 回貼って、混ぜる。
    - ノイズでテクスチャ座標をずらす。
    - タイルごとにランダムに回す・反転する。
    - 遠くは低周波の色むらを重ねる。

<!-- fig:tiling-hide:begin -->

<svg class="fig illust motion" data-fig="tiling-hide" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tiling-hide" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">繰り返しを隠す:周期の違う 2 つのパターンを、重ねる</text>
<line x1="60" y1="140" x2="720" y2="140" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="60" y="80" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">パターン A（周期 110）</text>
<line x1="60" y1="230" x2="720" y2="230" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="60" y="170" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">パターン B（周期 163、別のスケール）</text>
<line x1="60" y1="340" x2="720" y2="340" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="60" y="280" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">重ねた結果</text>
<circle cx="100" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="0;0;1;1"/></circle>
<circle cx="210" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1187;0.1190;1.0000" values="0;0;1;1"/></circle>
<circle cx="320" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1425;0.1429;1.0000" values="0;0;1;1"/></circle>
<circle cx="430" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1663;0.1667;1.0000" values="0;0;1;1"/></circle>
<circle cx="540" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1905;1.0000" values="0;0;1;1"/></circle>
<circle cx="650" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2139;0.2143;1.0000" values="0;0;1;1"/></circle>
<circle cx="150" cy="230" r="14" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2663;0.2667;1.0000" values="0;0;1;1"/></circle>
<circle cx="313" cy="230" r="14" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2901;0.2905;1.0000" values="0;0;1;1"/></circle>
<circle cx="476" cy="230" r="14" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3139;0.3143;1.0000" values="0;0;1;1"/></circle>
<circle cx="639" cy="230" r="14" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3377;0.3381;1.0000" values="0;0;1;1"/></circle>
<path d="M60,338.24 L64,336.82 L68,334.59 L72,331.35 L76,327.01 L80,321.68 L84,315.73 L88,309.78 L92,304.64 L96,301.1 L100,299.7 L104,300.59 L108,303.42 L112,307.42 L116,311.56 L120,314.79 L124,316.33 L128,315.81 L132,313.34 L136,309.54 L140,305.34 L144,301.8 L148,299.84 L152,300.05 L156,302.49 L160,306.76 L164,312.07 L168,317.48 L172,322.07 L176,325.13 L180,326.21 L184,325.13 L188,322.07 L192,317.48 L196,312.08 L200,306.79 L204,302.58 L208,300.26 L212,300.29 L216,302.71 L220,307.09 L224,312.72 L228,318.76 L232,324.46 L236,329.32 L240,333.1 L244,335.81 L248,337.6 L252,338.69 L256,339.27 L260,339.5 L264,339.41 L268,338.97 L272,338.03 L276,336.32 L280,333.47 L284,329.08 L288,322.79 L292,314.45 L296,304.27 L300,292.93 L304,281.59 L308,271.71 L312,264.78 L316,261.93 L320,263.65 L324,269.65 L328,278.92 L332,290.04 L336,301.5 L340,312.06 L344,320.89 L348,327.69 L352,332.54 L356,335.74 L360,337.7 L364,338.83 L368,339.43 L372,339.7 L376,339.76 L380,339.66 L384,339.34 L388,338.72 L392,337.61 L396,335.82 L400,333.1 L404,329.32 L408,324.45 L412,318.74 L416,312.69 L420,307.01 L424,302.51 L428,299.87 L432,299.4 L436,300.96 L440,303.91 L444,307.31 L448,310.11 L452,311.47 L456,311.0 L460,308.84 L464,305.62 L468,302.32 L472,299.95 L476,299.35 L480,300.89 L484,304.48 L488,309.55 L492,315.27 L496,320.77 L500,325.25 L504,328.17 L508,329.17 L512,328.17 L516,325.26 L520,320.77 L524,315.29 L528,309.6 L532,304.61 L536,301.2 L540,299.99 L544,301.23 L548,304.7 L552,309.81 L556,315.74 L560,321.69 L564,327.01 L568,331.35 L572,334.58 L576,336.8 L580,338.2 L584,338.97 L588,339.28 L592,339.21 L596,338.7 L600,337.61 L604,335.69 L608,332.6 L612,327.98 L616,321.58 L620,313.34 L624,303.54 L628,292.88 L632,282.41 L636,273.42 L640,267.17 L644,264.62 L648,266.16 L652,271.56 L656,279.97 L660,290.19 L664,300.92 L668,311.02 L672,319.69 L676,326.56 L680,331.6 L684,335.05 L688,337.25 L692,338.56 L696,339.29 L700,339.67 L704,339.86 L708,339.94 L712,339.98 L716,339.99 L720,340.0" fill="none" stroke="#e5484d" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000" values="0;0;1;1"/></path>
<text x="60" y="376" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">A も B も、それぞれ等間隔（規則的な繰り返し）<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000" values="1;1;0;0"/></text>
<text x="60" y="376" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重ねると、山の位置と高さが不揃い → 繰り返しが目立たない（周期が公約数を持たないほど良い）<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:tiling-hide:end -->

## 繰り返し（タイリング）を隠す
<strong>繰り返しテクスチャは広い範囲に貼ると同じ模様の並びが目立ちます</strong>。

| 工夫 | 内容 |
| --- | --- |
| 2 つのスケールを重ねる | 大きさの違う 2 枚を混ぜる（周期がずれる） |
| 近景・遠景のスケール | 距離で細かいタイルと大きなタイルを切り替える |
| タイルごとにランダムに回す | セルごとに回転・オフセットを変える（ハッシュで決める）。境でブレンド |
| マクロ バリエーション | 低周波のノイズで色を少しずらす |
| ディテール テクスチャ | 近づいたときだけ、細かい模様を重ねる |

```hlsl
float2 uv_near = world_position.xz * 0.5;
float2 uv_far = world_position.xz * 0.043;
float3 near_color = albedo.Sample(linear_wrap, uv_near).rgb;
float3 far_color = albedo.Sample(linear_wrap, uv_far).rgb;
float3 color = near_color * far_color * 2.0;
```

2 枚を掛けて 2 倍にすると、平均の明るさが保たれます。

## 繰り返しが目立つ理由

人間の目は <strong>同じ模様の繰り返し</strong>を、とても敏感に見つけます。タイル状のテクスチャを広い地面に貼ると、遠くから見たとき格子状の模様が見えてしまいます。特に、明るさが少し違う大きな斑点（石、花の群れ）があるとそこが目印になります。

| 見える現象 | 理由 |
| --- | --- |
| 格子状の模様 | テクスチャの周期ごとに、同じ目印が並ぶ |
| 地平線に向かって縞が見える | 遠くでは周期が、画面上で並んで見える |
| 同じ石が何度も見える | 近くで、同じ形を見つけられてしまう |

## 方法 1：スケールの違う 2 枚を重ねる

周期の違う 2 枚（たとえば、1 m と 23 m）を混ぜると、<strong>2 つの周期の最小公倍数</strong>が、見かけの周期になります。ほぼ繰り返しが見えなくなります。

```hlsl
float3 near_color = albedo.Sample(g_linear_wrap, world_pos.xz * 0.5).rgb;     // 2 m ごとに繰り返し
float3 far_color  = albedo.Sample(g_linear_wrap, world_pos.xz * 0.043).rgb;   // 約 23 m ごと
// 2 枚を掛けて 2 倍にすると、平均の明るさが、保たれる。
float3 color = near_color * far_color * 2.0;
```

遠くのテクスチャは 平均が 0.5 の、低周波のテクスチャ（明るさの揺らぎだけ）にしておきます。絵柄が強いとそちらが新しい目印になります。

## 方法 2：セルごとにずらして混ぜる

テクスチャを格子のセルに分けて、<strong>セルごとにランダムなずらし</strong>を与えます。隣のセルとの境目はブレンドでつなぎます。1 つのセルの中は普通のタイルですが、セルごとに違う部分を見せることになります。

Quilez が紹介したこの方式の考え方を、手を加えて示します。

```hlsl
float2 Hash2(float2 p) {
  // 整数のセル座標から、0〜1 の乱数を 2 つ作る
  float3 q = frac(float3(p.xyx) * float3(0.1031, 0.1030, 0.0973));
  q += dot(q, q.yzx + 33.33);
  return frac((q.xx + q.yz) * q.zy);
}
```

セルの座標から乱数を 2 つ作る、ハッシュです。同じセルはいつでも同じ値を返し、隣のセルとは無関係な値になります。

```hlsl
float3 SampleNoTiling(Texture2D tex, float2 uv) {
  float2 cell = floor(uv);
  float2 f = frac(uv);
```

UV を整数部（セル）と小数部（セルの中の位置）に、分けます。

```hlsl
  // ミップの選択を、セルの境目で、乱さないために、微分は、最初に計算して使い回す。
  float2 dx = ddx(uv);
  float2 dy = ddy(uv);
```

テクスチャのミップの選択に使う、UV の微分を最初に計算して、使い回します。セルごとに UV をずらすと微分が、セルの境目で飛んでミップが乱れ境目に、線が出るためです。

```hlsl
  float3 sum = 0;
  float wsum = 0;
  [unroll] for (int j = 0; j <= 1; ++j) {
    [unroll] for (int i = 0; i <= 1; ++i) {
      float2 g = float2(i, j);
      float2 offset = Hash2(cell + g);                 // このセルの、ランダムなずらし
      float2 r = g - f + offset * 0.5;                 // 画素から、ずらした中心への向き
      float w = exp(-5.0 * dot(r, r));                 // 中心に近いほど、重みが大きい
      sum += tex.SampleGrad(g_linear_wrap, uv + offset, dx, dy).rgb * w;
      wsum += w;
    }
  }
  return sum / wsum;
}
```

| 注意点 | 内容 |
| --- | --- |
| 読み込み | 4 回（2×2 のセル）。通常の 4 倍 |
| `SampleGrad` | 必須。`Sample` を使うとセルの境目でミップが、急に変わって線が見える |
| コントラストの低下 | 4 つを混ぜると、平均化してコントラストが落ちる。次の方法 3 で補正できる |

## 方法 3：ヒストグラムを保って混ぜる（Heitz と Neyret）

方法 2 の欠点は <strong>混ぜると、コントラストが落ちる</strong>ことです。複数のテクスチャの平均を取ると、ばらつきが小さくなるからです（統計的には、平均化で分散が減る）。

Heitz と Neyret（2018）はこれを、次の流れで直しました。

| 段階 | 内容 |
| --- | --- |
| ① 前処理 | テクスチャの色の分布を、正規分布（ガウス分布）に変換する。変換の表（ルックアップ テーブル）も、保存する |
| ② 実行時の混ぜ合わせ | ずらした 3 つの読み込みを、分散が保たれる重みで混ぜる（ガウス分布の性質を使う） |
| ③ 実行時の戻し | 混ぜた結果に、①のテーブルを逆に適用して元の色の分布に戻す |

結果は もとのテクスチャと同じ色の分布を持ち、しかも繰り返しが見えないテクスチャです。コストは 3 回の読み込みとテーブルの引き 1 回です。

実装では ①の前処理（ツール）が、必要になる点が手間です。

## 方法 4：六角形のタイル（Hex-Tiling）

Mikkelsen（2022）の方法は、<strong>平面を正三角形（または六角形）に分けて、3 つの頂点のそれぞれにずらしを与えて、混ぜる</strong>やり方です。正方形のセルより セルの境目が少なく、目立ちにくい特徴があります。

| 項目 | 内容 |
| --- | --- |
| 読み込み | 3 回（正三角形の 3 頂点） |
| 混ぜる範囲 | 3 つの重みの合計が 1 になるので、広い範囲でなめらか |
| 法線マップ | ずらしだけでなく、回転も与える場合は法線の向きも、回す必要がある |
| 実装の例 | Mikkelsen の論文に、HLSL / GLSL のコードがある |

回転も与えると 向きのある模様（木目、石の層）が乱れて不自然になることがあります。地形の土や砂のように向きのない模様では回転も、有効です。

## 方法 5：遠くで別の模様に切り替える

「近く」と「遠く」で別々の目的の、テクスチャを持ちます。

| 距離 | 使うテクスチャ | 役割 |
| --- | --- | --- |
| 近い（〜 20 m） | 細かい、ディテール テクスチャ | 近づいたときの、細かい凹凸 |
| 中間 | 通常のテクスチャ | 色と模様 |
| 遠い（100 m〜） | 低周波の、大きなスケールの色むら | 繰り返しを、見えなくする |

距離に応じて重みを `smoothstep` で切り替えます。ディテール テクスチャは <strong>平均が 0.5</strong>（掛け算で明るさが変わらない）に、作っておきます。

## 方法 6：Wang タイル

事前に <strong>辺の模様が合うタイルを、複数枚用意</strong>しておきセルごとに、辺の模様が合うタイルをランダムに並べます（Cohen ら、2003）。タイルの数が増えると繰り返しは、ほとんど見えなくなります。ただし、タイルを作る作業（ツール）が、大変で実行時にもタイルの選択の、インデックス テクスチャが必要です。地形では方法 2〜4 の方が、手軽です。

## 選び方

| 状況 | おすすめ |
| --- | --- |
| まず、手軽にやりたい | 方法 1（2 枚を重ねる）と、方法 5（遠くの色むら） |
| 草・土・砂の向きのない模様 | 方法 4（hex-tiling）、または方法 3 |
| コントラストを保ちたい | 方法 3（ヒストグラムを保つ） |
| ツールを作れる品質を最優先 | 方法 3 ＋ 方法 5 |

## よくあるミス

??? failure "格子状の繰り返しが、遠くから見て目立つ"
    <strong>スケールを変えた重ね貼り</strong>をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スケールを変えて重ね、ノイズでずらす

## 参考

- Heitz, Neyret, "High-Performance By-Example Noise using a Histogram-Preserving Blending Operator", High-Performance Graphics 2018
- Mikkelsen, "Practical Real-Time Hex-Tiling", Journal of Computer Graphics Techniques, Vol. 11, No. 2, 2022
- Quilez, "Texture Repetition", iquilezles.org, 2015（セルごとのランダムなずらしと、ブレンド）
- Cohen, Shade, Hiller, Deussen, "Wang Tiles for Image and Texture Generation", ACM Transactions on Graphics (SIGGRAPH 2003)

## 関連ページ

- [Terrain Texturing](index.md)
- [Triplanar Mapping](triplanar.md)
