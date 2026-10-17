---
title: VSM と ESM・MSM
tags:
  - 描画
---

# VSM と ESM・MSM

[PCF](pcf.md)は、**複数回サンプルして、比較の結果を平均**するので、**広くぼかすほど、重く**なります。**VSM**（Variance Shadow Maps）は、**比較の結果を平均するのではなく、深度の統計量（平均と 2 乗平均）を保存して**、**普通のテクスチャ フィルタ（ぼかし・ミップ・異方性）で、事前にぼかせる**ようにした方式です。**シャドウ マップを画像としてぼかせる**ので、**ソフトな影が安く**作れます。その代わり、<strong>光漏れ（ライト ブリーディング）</strong>という、独特のアーティファクトが出ます。**ESM・EVSM・MSM**はその**改良版**です。

!!! tip "ポイント"
    - VSM ＝ <strong>深度 z と z² の「平均（モーメント）」</strong>を保存する。<strong>ぼかして</strong>から使える。
    - 影の割合は、<strong>チェビシェフの不等式</strong>で、<strong>平均と分散から、上限</strong>として見積もる。
    - <strong>フィルタ可能</strong>：<strong>ガウス ブラー・ミップ・異方性フィルタ・MSAA</strong>がそのまま使える。<strong>ソフトな影がサンプルを増やさずに</strong>得られる。
    - 弱点：<strong>光漏れ</strong>（影が薄く抜ける）。<strong>精度</strong>（浮動小数点が必要）。
    - <strong>ESM</strong>：<strong>exp(c·z)</strong> を保存。<strong>EVSM</strong>：exp ワープした VSM。<strong>MSM</strong>：4 つのモーメントで光漏れを減らす。
    - <strong>バイアスの悩みが小さい</strong>（アクネが出にくい）のも利点。

## 発想：深度でなく、統計を保存する

PCF が**平均できない**理由は、**深度を平均してから比べると、誤る**ことでした。VSM は<strong>「ある範囲の深度の分布」</strong>を、**平均 μ と 2 乗平均**の 2 つの数で、**保存**します。**これらは平均（ぼかし）しても意味が保たれる**量です。

| 保存する量 | 意味 |
| --- | --- |
| <strong>M₁ = E[z]</strong> | 深度の平均 |
| <strong>M₂ = E[z²]</strong> | 深度の 2 乗の平均 |

**分散** は次のとおりです。

<div class="formula">σ² = M₂ − M₁²</div>

シャドウ マップに**深度 z と z² を書き**、<strong>ぼかし（平均）</strong>をすれば、**範囲の M₁・M₂** が得られます。**ぼかしても統計としての意味が保たれる**のがポイントです。

## 影の割合：チェビシェフの不等式

受け手の深度を `t` とします。**範囲の深度の分布**（平均 μ・分散 σ²）から、<strong>「t より、奥にある深度の割合」</strong>＝**日向の割合**を**見積もります**。**正確な分布は分からない**ので、**チェビシェフの（片側）不等式**で**上限**を使います。

<div class="formula">t ≤ μ のとき：日向 = 1　、　t &gt; μ のとき：p_max(t) = σ² / (σ² + (t − μ)²)</div>

| 条件 | 意味 |
| --- | --- |
| **t ≤ μ** | 受け手が**平均より手前**。**完全に日向** |
| **t &gt; μ** | 受け手が**平均より奥**。**遮蔽物がある**可能性。**日向の割合の上限**が `p_max` |

`p_max` は、**t が μ に近いほど 1 に近く、離れるほど 0 に近づきます**。**分散が大きい**（深度がばらついている＝**エッジの近く**）ほど、<strong>半影（中間の値）</strong>が出ます。

```hlsl
float ChebyshevUpperBound(float2 moments, float t) {
  float mean = moments.x;
  float variance = max(moments.y - mean * mean, kMinVariance);
  float d = t - mean;
  float p_max = variance / (variance + d * d);
  return (t <= mean) ? 1.0 : p_max;
}
```

| 点 | 説明 |
| --- | --- |
| **`kMinVariance`** | 分散が 0（平らな面）で、**0 除算・アクネ**にならない**下限**（バイアスの代わり） |
| **`t ≤ mean`** | 完全に日向 |
| **戻り値** | <strong>日向の割合（上限）</strong>。**影の濃さ**は、`1 − 日向` |

## 手順

| 手順 | 内容 |
| --- | --- |
| **① シャドウ マップを描く** | 深度ではなく、<strong>(z, z²)</strong> を、ピクセルシェーダーで書く（浮動小数点の 2 チャンネル） |
| **② ぼかす** | <strong>ガウス ブラー（分離可能）</strong>や、**ミップ・異方性フィルタ** |
| **③ 受け手の深度で比べる** | **ぼかされたモーメント**を引き、**チェビシェフ**で日向の割合 |

```hlsl
float2 WriteMoments(float depth) {
  float dx = ddx(depth);
  float dy = ddy(depth);
  float moment2 = depth * depth + 0.25 * (dx * dx + dy * dy);
  return float2(depth, moment2);
}
```

| 点 | 説明 |
| --- | --- |
| **`ddx・ddy` の項** | **面の傾き**による、**深度の分散**を、`M₂` に足す。**傾いた面でもアクネが出ない**（バイアスの代わり） |
| **フォーマット** | **`R32G32_FLOAT`**（精度が大事。16 ビットは、足りないことが多い） |
| **ぼかし** | シャドウ マップに**ガウス ブラー**（分離）。**ミップを作って、遠くを粗く**も可能 |

### 利点：フィルタが安い

| フィルタ | PCF | VSM |
| --- | --- | --- |
| **広いソフトネス** | サンプルを**増やす**（重い） | **ぼかして**おくだけ（シャドウ マップ全体に、1 回）。**画素あたりは、1 サンプル** |
| **ミップ・異方性** | **使えない** | **使える**（遠くの影を安く滑らか） |
| **MSAA** | 難しい | **使える** |
| **アクネ** | バイアスが必要 | **出にくい**（面の傾きが分散に入る） |

## 弱点：光漏れ（ライト ブリーディング）

VSM は<strong>「分散」と「平均」だけ</strong>しか見ません。**遮蔽物が複数あり、深度が違う**場合、**統計だけでは区別できず**、**影の中に光が漏れた**ように見える部分が出ます。

<svg class="fig illust" viewBox="0 0 780 270" role="img" aria-label="VSM の光漏れ">
<text x="20" y="24" class="fig-title">深度の異なる遮蔽物が重なると、統計だけでは区別できず、影に光が漏れる</text>
<rect x="100" y="60" width="140" height="14" fill="rgba(150,150,150,0.7)" stroke="currentColor" stroke-width="2"/><text x="108" y="54" style="font-size:12px">遮蔽物 A（手前）</text>
<rect x="160" y="110" width="140" height="14" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/><text x="308" y="124" style="font-size:12px">遮蔽物 B（奥）</text>
<line x1="60" y1="230" x2="560" y2="230" stroke="currentColor" stroke-width="4"/><text x="60" y="254" style="font-size:12px">受け手</text>
<rect x="160" y="226" width="80" height="8" fill="#111" opacity="0.8"/><rect x="240" y="226" width="60" height="8" fill="#888" opacity="0.5"/>
<text x="330" y="190" style="font-size:12px;fill:#e5484d;font-weight:700">B の影の領域のうち、A に遮られていない所が、</text>
<text x="330" y="208" style="font-size:12px;fill:#e5484d;font-weight:700">本来より、薄く（明るく）見える ＝ 光漏れ</text>
<text x="400" y="100" style="font-size:12px">原因：A と B の深度の平均・分散だけでは、</text>
<text x="400" y="118" style="font-size:12px">「どちらが、何割か」が、分からない</text>
</svg>

### 対策

| 対策 | 内容 |
| --- | --- |
| <strong>光漏れの低減（リマップ）</strong> | 日向の割合 `p` を、**`(p − a) / (1 − a)`**（`a` は 0.2〜0.5）で、**下側を切り捨てて**引き伸ばす。**薄い漏れを消せる**が**半影の滑らかさが減る** |
| **分散の下限を調整** | `kMinVariance` を大きく |
| **ESM・EVSM・MSM** | 方式を変える（下記） |
| **遮蔽物の深度差を小さく** | シーンの設計（**重なりを少なく**） |

```hlsl
float ReduceLightBleeding(float p_max, float amount) {
  return saturate((p_max - amount) / (1.0 - amount));
}
```

## ESM（指数シャドウ マップ）

**ESM**（Exponential Shadow Maps）は、**深度の指数 `exp(c · z)`** を保存します。

<div class="formula">日向 = clamp( exp(−c · t) · E[exp(c · z)] , 0, 1 )</div>

| 項目 | 内容 |
| --- | --- |
| **保存するもの** | `exp(c · z)`（**1 チャンネル**） |
| **フィルタ** | **ぼかしても意味が保たれる**（指数は平均できる） |
| **`c`** | **鋭さ**。大きいほど、**影が鋭く**（`z` の差を強く強調）。ただし、<strong>浮動小数点の範囲（オーバーフロー）</strong>に注意 |
| **利点** | **1 チャンネル**で済む。**VSM のような、光漏れは小さい** |
| **欠点** | **受け手が遮蔽物に近い**と**影が薄く**なる（**接触部が明るく漏れる**）。`c` と**精度のトレードオフ** |

## EVSM（指数 VSM）

**EVSM**（Exponential Variance Shadow Maps）は、**深度を exp でワープしてから、VSM**を行います。**正のワープ `exp(c z)`** と**負のワープ `−exp(−c z)`** を、**それぞれ VSM**にして、**小さい方**（保守的な方）を採用します。

| 項目 | 内容 |
| --- | --- |
| **保存するもの** | `(exp(c₊ z), exp(2 c₊ z), −exp(−c₋ z), exp(−2 c₋ z))`（**4 チャンネル**） |
| **光漏れ** | **VSM より、大幅に減る**（exp で深度の差が強調される） |
| **欠点** | **4 チャンネル**（メモリ・帯域が倍）。**浮動小数点の精度・範囲**に注意（32 ビット推奨） |

## MSM（モーメント シャドウ マップ）

**MSM**（Moment Shadow Maps、Peters & Klein 2015）は、**4 つのモーメント**（z, z², z³, z⁴）を保存し、**ハンバーガーのモーメント問題**を解いて、**より正確な、可視性の上限**を求めます。

| 項目 | 内容 |
| --- | --- |
| **保存** | 4 つのモーメント（**4 チャンネル**。**16 ビットでも変換すれば足りる**ように工夫） |
| **利点** | **光漏れが非常に小さい**。**VSM・ESM より、安定** |
| **欠点** | **計算が複雑**（4 モーメントから、可視性を求める計算が重い） |

## VSM 系の比較

| 項目 | VSM | ESM | EVSM | MSM |
| --- | --- | --- | --- | --- |
| **チャンネル数** | 2 | 1 | 4（または 2） | 4 |
| **光漏れ** | <strong>あり（大）</strong> | 小（接触部で薄い） | **小** | **最小** |
| **精度の要求** | F32 | F32（オーバーフロー注意） | F32 | F16 でも可（工夫） |
| **計算コスト** | 小 | 最小 | 中 | 中〜大 |
| **フィルタ可能** | ○ | ○ | ○ | ○ |
| **実装の簡単さ** | ○ | ○ | △ | × |

## PCF との使い分け

| 状況 | おすすめ |
| --- | --- |
| **広いソフト シャドウを、安く** | VSM・EVSM（**シャドウ マップをぼかすだけ**） |
| **精度・光漏れを避けたい** | **PCF**（扱いが素直） |
| **接触硬化が欲しい** | PCSS・レイトレ |
| **メモリ・帯域が厳しい** | PCF（深度 1 チャンネル）・ESM |
| **多くのライト** | VSM 系（**ぼかしが、1 回**） |

**現代のゲームでは、PCF（＋ ノイズ ＋ TAA）が、主流**です。VSM 系は**光漏れ・精度・メモリ**の問題から、**限定的**に使われます（**スポットライト・遠景・UI や特殊な効果**など）。

## よくあるミス

??? failure "16 ビットのシャドウ マップで、VSM を使い、精度不足でアクネ・縞"
    **32 ビット浮動小数点**を使います。

??? failure "光漏れ対策なしで、複雑な形の影が薄く抜ける"
    **リマップ**（`(p − a) / (1 − a)`）・EVSM・MSM を使います。

??? failure "ESM の `c` が大きすぎて、浮動小数点がオーバーフロー"
    `c` を下げる（深度範囲を小さく）・精度を考慮します。

??? failure "ぼかしを、深度シャドウ マップ（比較サンプラー）に掛けて、境界が破綻"
    VSM のぼかしは、**モーメント**に対して行います。**深度**には掛けません。

## これだけ覚える

!!! abstract "まとめ"
    - [x] VSM ＝ <strong>深度の平均 M₁ と 2 乗平均 M₂ を保存</strong>し、<strong>チェビシェフの不等式で日向の割合を見積もる</strong>
    - [x] <strong>モーメントは、ぼかしてよい</strong>。<strong>ソフトな影がサンプルを増やさず</strong>得られる（ミップ・異方性・MSAA も可）
    - [x] 弱点は<strong>光漏れ</strong>。<strong>リマップ・EVSM・MSM</strong>で軽減
    - [x] <strong>ESM</strong> は<strong>exp(c·z)</strong>（1 チャンネル）。<strong>MSM</strong> は<strong>4 モーメント</strong>
    - [x] 現代では<strong>PCF が主流</strong>。VSM 系は<strong>限定的</strong>

## 参考

- Donnelly, Lauritzen, "Variance Shadow Maps"（I3D 2006）
- Lauritzen, McCool, "Layered Variance Shadow Maps"（GI 2008）
- Peters, Klein, "Moment Shadow Mapping"（I3D 2015）

## 関連ページ

- [影](index.md)
- [PCF](pcf.md)
- [PCSS](pcss.md)
- [カスケード シャドウ マップ](cascaded.md)
- [AO のフィルタ（ぼかし）](../ao/filtering.md)
