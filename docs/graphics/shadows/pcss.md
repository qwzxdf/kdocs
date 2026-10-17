---
title: PCSS
tags:
  - 描画
---

# PCSS

[PCF](pcf.md)は、**どこでも同じ幅**で影の縁をぼかします。しかし、**現実の影**は**遮蔽物に近い所は鋭く、離れるほどぼやけます**（半影が広がる）。**PCSS**（Percentage-Closer Soft Shadows）は、**遮蔽物までの距離をシャドウ マップから見積もり**、**その距離に応じて、PCF のカーネルの大きさを変える**方式です。2005 年に NVIDIA の Fernando が提案しました。**面光源が作る半影**を**シャドウ マップ 1 枚で、近似**できます。

!!! tip "ポイント"
    - 半影の幅は<strong>(受け手の距離 − 遮蔽物の距離) × 光源の大きさ ÷ 遮蔽物の距離</strong>（相似三角形）。
    - 3 段階：<strong>① 遮蔽物の探索（平均の遮蔽物の深度を求める）</strong> → <strong>② 半影の幅を計算</strong> → <strong>③ その幅で PCF</strong>。
    - <strong>遮蔽物に近い → 鋭い</strong>、<strong>遠い → ソフト</strong>（<strong>接触硬化</strong>）。
    - 光源の大きさ（<strong>光源サイズ</strong>）が、<strong>ぼけの強さを決める</strong>パラメータ。
    - コストは<strong>探索 ＋ 大きな PCF</strong>で、重い。<strong>サンプル数を減らす工夫</strong>が要る。
    - シャドウ マップは<strong>1 枚</strong>だけ。<strong>1 つの遮蔽物（平均）</strong>を仮定する近似。

## 半影の幾何

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="半影の幅の計算">
<text x="20" y="24" class="fig-title">相似三角形：半影の幅 ＝ (d_receiver − d_blocker) × 光源の幅 ÷ d_blocker</text>
<rect x="100" y="50" width="150" height="16" fill="rgba(229,170,40,0.7)" stroke="currentColor" stroke-width="2"/><text x="108" y="44" style="font-size:12px">面光源（幅 w_light）</text>
<rect x="150" y="140" width="50" height="16" fill="rgba(150,150,150,0.7)" stroke="currentColor" stroke-width="2"/><text x="206" y="154" style="font-size:12px">遮蔽物（距離 d_blocker）</text>
<line x1="20" y1="250" x2="560" y2="250" stroke="currentColor" stroke-width="4"/><text x="20" y="274" style="font-size:12px">受け手（距離 d_receiver）</text>
<line x1="100" y1="66" x2="360" y2="250" stroke="currentColor" stroke-dasharray="4 3"/><line x1="250" y1="66" x2="-10" y2="250" stroke="currentColor" stroke-dasharray="4 3"/>
<line x1="100" y1="66" x2="-10" y2="250" stroke="currentColor" stroke-dasharray="4 3" opacity="0.4"/><line x1="250" y1="66" x2="360" y2="250" stroke="currentColor" stroke-dasharray="4 3" opacity="0.4"/>
<rect x="140" y="246" width="70" height="8" fill="#111" opacity="0.85"/>
<rect x="70" y="246" width="70" height="8" fill="#666" opacity="0.6"/><rect x="210" y="246" width="70" height="8" fill="#666" opacity="0.6"/>
<text x="290" y="238" style="font-size:12px">半影の幅 w_penumbra</text>
<text x="400" y="110" style="font-weight:700">w_penumbra = (d_r − d_b) · w_light / d_b</text>
<text x="400" y="136" style="font-size:12px">遮蔽物が受け手に近い（d_r ≒ d_b）→ 半影が 0（鋭い）</text>
<text x="400" y="156" style="font-size:12px">遮蔽物が光源に近い・受け手が遠い → 半影が広い</text>
</svg>

**光源から**、遮蔽物までの距離を `d_b`、受け手までを `d_r`、光源の幅を `w_light` とすると、**相似な三角形**から、**半影の幅**は次のとおりです。

<div class="formula">w_penumbra = (d_r − d_b) · w_light / d_b</div>

| 場合 | 半影の幅 |
| --- | --- |
| **遮蔽物が受け手に接している**（d_r = d_b） | **0**（鋭い影） |
| **遮蔽物と受け手が離れている**（d_r が d_b より大きい） | **広い**（ソフト） |
| **光源が大きい**（w_light が大きい） | **広い** |
| **遮蔽物が光源に近い**（d_b が小さい） | **非常に広い** |

**物体の足元は鋭く、離れるほどぼやける**という、**現実の影の性質**がこの式で再現できます。

## 3 つの手順

### ① 遮蔽物の探索（Blocker Search）

**受け手の点**から、**光源の方向**に**シャドウ マップのある範囲**を探索し、<strong>「受け手より手前にある（遮蔽物の）深度」</strong>の**平均**を求めます。

**探索する範囲の大きさ**は、**光源の大きさ**と**受け手の位置**で決まります（光源の幅をシャドウ マップ上に投影した幅）。

<div class="formula">w_search = w_light · (d_r − near) / d_r　（透視投影の場合）</div>

```hlsl
float AverageBlockerDepth(float2 uv, float receiver_depth, float search_radius_uv) {
  float sum = 0.0;
  int count = 0;
  [unroll] for (int i = 0; i < kBlockerSamples; ++i) {
    float2 offset = kPoissonDisk[i] * search_radius_uv;
    float stored = shadow_tex_raw.SampleLevel(point_sampler, uv + offset, 0).r;
    if (stored < receiver_depth - bias) {
      sum += stored;
      count++;
    }
  }
  return count > 0 ? sum / count : -1.0;
}
```

| 点 | 説明 |
| --- | --- |
| **生の深度を読む** | 比較サンプラーでなく、**通常のサンプラー**で**深度そのもの**を読む（`shadow_tex_raw`） |
| **受け手より手前のものだけ** | `stored < receiver_depth` を、**遮蔽物**として平均 |
| **`count == 0`** | **遮蔽物が見つからない** → **日向**（影なし）。以降の計算は不要 |
| **サンプル数** | 8〜16（ポワソン円盤）。**探索範囲の大きさ**が品質とコストを決める |

### ② 半影の幅を計算

見つかった**平均の遮蔽物の深度 `d_b`** から、**半影の幅**を計算します。

<div class="formula">w_penumbra = (d_r − d_b) · w_light / d_b</div>

<strong>深度を線形（光からの距離）</strong>にしてから計算します（**非線形の深度のままだと、式が成り立ちません**）。

```hlsl
float penumbra_width = (receiver_z - blocker_z) * light_size_uv / blocker_z;
```

### ③ 可変幅の PCF

**半影の幅**を、**PCF のカーネルの半径**にして、通常の PCF を行います。

```hlsl
float PCSS(float2 uv, float receiver_depth, float receiver_z) {
  float search_radius = light_size_uv * (receiver_z - near_z) / receiver_z;
  float blocker_depth = AverageBlockerDepth(uv, receiver_depth, search_radius);
  if (blocker_depth < 0.0) return 1.0;

  float blocker_z = LinearizeLightDepth(blocker_depth);
  float penumbra = (receiver_z - blocker_z) * light_size_uv / blocker_z;
  float filter_radius = penumbra * near_z / receiver_z;

  return PCFPoisson(uv, receiver_depth, filter_radius, rotation);
}
```

| 点 | 説明 |
| --- | --- |
| **`filter_radius = penumbra · near / d_r`** | **半影の幅を近クリップ面での大きさに直す**（透視投影のシャドウ マップ上の幅） |
| **遮蔽物なしで 1.0** | 無駄な PCF を避ける |
| **PCF は通常の `SampleCmp`** | ポワソン円盤で可変の半径 |

## 平行光（太陽）の PCSS

**太陽**は**平行光**で**正射影**のシャドウ マップです。**光源の大きさ**は、**視直径**（約 0.53 度、半角で約 0.27 度）で表します。**半影の幅**は**深度の差に角度のタンジェントを掛けた**ものです。

<div class="formula">w_penumbra = (d_r − d_b) · tan(θ_light)　（θ_light：光源の角半径）</div>

| 項 | 意味 |
| --- | --- |
| **d_r − d_b** | **受け手と遮蔽物の光の方向の距離差**（ワールド単位） |
| **tan θ** | 光源の見かけの大きさ（太陽は約 0.0047） |
| **シャドウ マップ上の幅** | ワールド単位の幅を**マップの 1 テクセルの大きさ**で割る |

**正射影**では**探索範囲も一定**（遠近の補正が不要）なので**単純**です。

## 現実の影との違い

PCSS は、**1 枚のシャドウ マップ**から、**半影を近似**します。以下の**仮定・限界**があります。

| 限界 | 説明 |
| --- | --- |
| **遮蔽物は平均 1 枚の面** | <strong>複数の遮蔽物（深度が異なる）</strong>を、**平均**した 1 つの面として扱う。<strong>複雑な形（葉・髪）</strong>で、不正確 |
| **シャドウ マップが遮蔽物しか持たない** | **光から見て、一番手前の面**だけ。**奥の遮蔽物**は見えない |
| **探索範囲の限界** | 探索範囲外の遮蔽物は、**見逃す** |
| **光源の形** | 円・矩形程度。**複雑な形の面光源**は、近似 |

## コストと工夫

PCSS は<strong>探索（8〜16 サンプル）＋ PCF（16 サンプル以上）</strong>で、**画素あたり 30 回以上**シャドウ マップを読む、**重い**方式です。

| 工夫 | 内容 |
| --- | --- |
| **探索のサンプル数を減らす** | 4〜8 個に。**画素ごとの回転 ＋ 時間蓄積** |
| **PCF のサンプル数を減らす** | 同上。**半影が小さい所は、少なく** |
| **探索範囲を制限** | 範囲を狭める（遠くの遮蔽物を諦める） |
| **早期終了** | **探索で遮蔽物がなければ即終了**（日向）。**ほぼ全て遮蔽**なら、影（完全な影）として終了 |
| **ノイズ ＋ TAA** | **サンプルを少なく**し、**ノイズを TAA（または時間蓄積）で消す** |
| **半分の解像度で計算** | 影のマスクを**半分の解像度**で作り、**アップサンプル**（バイラテラル） |
| **カスケードの近くだけ** | **遠くは通常の PCF**、**近くだけ PCSS** |

## 他の方式との比較

| 方式 | 接触硬化 | コスト | 備考 |
| --- | --- | --- | --- |
| **PCF** | なし（一定のぼけ） | 小〜中 | 簡単 |
| **PCSS** | **あり** | **大** | 光源サイズの調整が直感的 |
| **VSM 系**（[VSM](vsm.md)） | 近似的（フィルタの大きさを変える） | 中 | フィルタが安い。光漏れ |
| **レイトレ影**（[レイトレース影](ray-traced.md)） | <strong>あり（正確）</strong> | 大（HW が必要） | 面光源を直接サンプル |
| **距離場の影**（[距離場の影](sdf-shadows.md)） | あり（円錐） | 中 | 静的向き |

## 調整のしかた

| パラメータ | 意味 | 目安 |
| --- | --- | --- |
| **光源サイズ** | 大きいほど、ソフト（半影が広がる） | **太陽なら、実際の視直径**（または見た目で大きめ） |
| **探索サンプル数** | 遮蔽物の平均の精度 | 4〜16 |
| **PCF サンプル数** | ぼかしの滑らかさ | 8〜32 |
| **最小・最大の半影幅** | **鋭さ・ぼけすぎの制限** | 最小は数テクセル（エイリアシングを隠す） |
| **探索範囲の上限** | 計算コストの制限 | シーンの大きさ |

**半影の幅に最小値**（たとえば 1〜2 テクセル）を設けると**接触部でもエイリアシングが目立ちません**。

## よくあるミス

??? failure "非線形の深度のまま、半影の式に入れて、ぼけが変"
    **線形（光からの距離）に変換**してから計算します。

??? failure "遮蔽物の探索で、比較サンプラーを使って、深度が得られない"
    **通常のサンプラー**で**生の深度**を読みます。

??? failure "遮蔽物が見つからないのに、PCF をして、無駄・誤判定"
    `count == 0` で、**日向として終了**します。

??? failure "探索範囲が小さすぎて、遠くの遮蔽物を見逃し、半影が狭すぎる"
    **光源サイズ・受け手の距離**から、**探索範囲**を適切に取ります。

??? failure "サンプルが少なすぎて、ノイズがひどい"
    **画素ごとの回転 ＋ TAA**、または**サンプルを増やす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] PCSS ＝ <strong>遮蔽物との距離で、PCF のぼけの幅を変える</strong>（接触硬化を再現）
    - [x] 半影の幅 ＝ <strong>(d_receiver − d_blocker) × 光源の大きさ ÷ d_blocker</strong>
    - [x] 手順：<strong>① 遮蔽物の平均深度を探索 → ② 半影の幅を計算 → ③ その幅で PCF</strong>
    - [x] 深度は<strong>線形</strong>にして計算。<strong>遮蔽物が無ければ、日向で終了</strong>
    - [x] <strong>重い</strong>ので<strong>サンプルを減らして、ノイズ ＋ 時間蓄積</strong>で補う

## 参考

- Fernando, "Percentage-Closer Soft Shadows"（SIGGRAPH 2005 Sketches、NVIDIA）

## 関連ページ

- [影](index.md)
- [PCF](pcf.md)
- [VSM と ESM・MSM](vsm.md)
- [レイトレース影](ray-traced.md)
- [バイアス](bias.md)
