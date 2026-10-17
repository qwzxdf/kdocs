---
title: 3D LUT
tags:
  - 描画
---

# 3D LUT

<strong>カラー グレーディングの調整（露出・ホワイト バランス・LGG・彩度・トーンマップなど）</strong>は、**どれも「画素の色 → 別の色」への変換**です。**これを画素ごとに毎フレーム計算するのは無駄**で、**あらかじめ、すべての色の変換結果を表にしておけば、1 回の表引きで済みます**。この表が<strong>3D LUT（ルックアップ テーブル）</strong>です。**色（R, G, B）をそのまま 3D テクスチャの座標にして、変換後の色を引く**ので**何段階の調整でもコストは一定**です。このページでは、**3D LUT の仕組み・解像度（32³）・DX11 での適用・端の補間・対数エンコードの必要性**を説明します。

!!! tip "ポイント"
    - 3D LUT ＝ <strong>入力色（R, G, B）を座標に出力色を格納した 3D テクスチャ</strong>。
    - <strong>適用は、3D テクスチャを 1 回サンプルするだけ</strong>。<strong>何段階の調整もまとめられる</strong>。
    - <strong>解像度は 16³〜64³</strong>（<strong>32³ が定番</strong>）。<strong>間はハードウェアの 3 線形補間</strong>。
    - <strong>半テクセルのオフセット</strong>（<strong>`× (N−1)/N + 0.5/N`</strong>）を<strong>忘れない</strong>（<strong>端の色がずれる</strong>）。
    - <strong>入力が広いダイナミック レンジ（HDR）なら、対数などでエンコードしてから引く</strong>。
    - <strong>外部ツールで作った LUT を、そのまま使える</strong>（<strong>.cube・.png 形式</strong>）。

## 仕組み

**RGB の各成分（0〜1）を、そのまま 3D テクスチャの X・Y・Z 座標**とします。**その座標の位置に、「変換後の色」を格納**しておきます。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="3D LUT">
<text x="20" y="26" class="fig-title">入力の色 (r, g, b) を座標にして、3D テクスチャから変換後の色を引く</text>
<g transform="translate(60,60)">
<polygon points="0,60 120,60 120,160 0,160" fill="#4c8bf5" fill-opacity="0.1" stroke="#94a3b8" stroke-width="2"/>
<polygon points="0,60 40,20 160,20 120,60" fill="#4c8bf5" fill-opacity="0.18" stroke="#94a3b8" stroke-width="2"/>
<polygon points="120,60 160,20 160,120 120,160" fill="#4c8bf5" fill-opacity="0.14" stroke="#94a3b8" stroke-width="2"/>
<g stroke="#cbd5e1"><line x1="40" y1="60" x2="40" y2="160"/><line x1="80" y1="60" x2="80" y2="160"/><line x1="0" y1="93" x2="120" y2="93"/><line x1="0" y1="126" x2="120" y2="126"/></g>
<circle cx="76" cy="104" r="6" fill="#e5484d"/>
<text x="0" y="190" style="font-size:12px">32 × 32 × 32 のセルに、変換後の RGB を格納</text>
<text x="124" y="176" style="font-size:12px">R →</text><text x="-20" y="82" style="font-size:12px">G ↑</text>
</g>
<g font-size="13"><text x="330" y="96" style="font-weight:700">手順</text>
<text x="330" y="122">① 画素の色 (r, g, b) を読む</text>
<text x="330" y="146">② (r, g, b) を 3D テクスチャ座標にする</text>
<text x="330" y="170">③ サンプル → 変換後の色（3 線形補間）</text>
<text x="330" y="206" style="font-weight:700">何段階の調整でも、1 回のサンプルで済む</text></g>
</svg>

| 項目 | 内容 |
| --- | --- |
| **入力** | <strong>画素の色 (r, g, b)（0〜1）</strong> |
| **出力** | **変換後の色** |
| **格子の点** | **32³ ＝ 32,768 個**（**各点に変換後の RGB**） |
| **間の点** | **GPU の 3 線形補間**が、**自動で滑らかにつなぐ** |

## DX11 での適用

```hlsl
Texture3D<float3> color_lut : register(t4);
SamplerState linear_clamp : register(s1);

static const float kLutSize = 32.0;

float3 ApplyLut(float3 color) {
  float3 uvw = saturate(color) * ((kLutSize - 1.0) / kLutSize) + 0.5 / kLutSize;
  return color_lut.SampleLevel(linear_clamp, uvw, 0);
}
```

| 点 | 説明 |
| --- | --- |
| **`saturate(color)`** | **入力を 0〜1 に収める**（**LUT の範囲**） |
| **`(N−1)/N` と `0.5/N`** | **半テクセルのオフセット**。**0 が最初のセルの中心、1 が最後のセルの中心に当たる**ように**する**（**忘れると黒と白がずれる**） |
| **`linear_clamp`** | **3 線形補間・端で止める** |
| **形式** | **`R10G10B10A2_UNORM`・`R16G16B16A16_FLOAT`**（**8 ビットだとバンディング**） |

### なぜ半テクセルが要るのか

<strong>テクスチャ座標 0.0 は、最初のテクセルの「端」</strong>で、**中心は 0.5/N** です。**LUT の格子点 0 と 1 を、そのまま 0.0・1.0 に対応させる**と、**最初と最後の格子点が補間で薄まります**。**`× (N−1)/N + 0.5/N`** で、**格子点の中心に合わせる**と、**正確な値**が**得られます**。

<!-- fig:lut-half-texel:begin -->

<svg class="fig illust motion" data-fig="lut-half-texel" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lut-half-texel" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">半テクセル補正:LUT の格子点は、テクセルの「中心」にある</text>
<rect x="60.0" y="110" width="149.0" height="60" fill="#000000" stroke="#1f2937" stroke-width="1.5"/>
<text x="135.0" y="190" text-anchor="middle" style="font-size:13px;font-weight:500;fill:#1f2937">格子点 0 = 0.00</text>
<circle cx="135.0" cy="140.0" r="4" fill="#e5aa28"/>
<rect x="210.0" y="110" width="149.0" height="60" fill="#6c6c6c" stroke="#1f2937" stroke-width="1.5"/>
<text x="285.0" y="190" text-anchor="middle" style="font-size:13px;font-weight:500;fill:#1f2937">格子点 1 = 0.15</text>
<circle cx="285.0" cy="140.0" r="4" fill="#e5aa28"/>
<rect x="360.0" y="110" width="149.0" height="60" fill="#cdcdcd" stroke="#1f2937" stroke-width="1.5"/>
<text x="435.0" y="190" text-anchor="middle" style="font-size:13px;font-weight:500;fill:#1f2937">格子点 2 = 0.62</text>
<circle cx="435.0" cy="140.0" r="4" fill="#e5aa28"/>
<rect x="510.0" y="110" width="149.0" height="60" fill="#ffffff" stroke="#1f2937" stroke-width="1.5"/>
<text x="585.0" y="190" text-anchor="middle" style="font-size:13px;font-weight:500;fill:#1f2937">格子点 3 = 1.00</text>
<circle cx="585.0" cy="140.0" r="4" fill="#e5aa28"/>
<text x="60" y="98" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1D の LUT（4 個）。橙の点が各テクセルの中心</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2664;0.2667;1.0000" values="0;0;1;1;0;0"/><line x1="60.0" y1="104" x2="60.0" y2="176" stroke="#e5484d" stroke-width="3"/>
<line x1="135.0" y1="104" x2="135.0" y2="176" stroke="#2ea043" stroke-width="3"/>
<text x="60" y="260" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">入力 v = 0/3 → 引くべきは 格子点 0（0.00）</text>
<text x="60" y="296" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">補正なし u = v = 0.000 → 0.00（誤差 0.00）</text>
<text x="60" y="326" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2ea043">補正あり u = (v·(N−1) + 0.5) / N = 0.125 → 0.00（誤差 0.00）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2664;0.2667;0.4590;0.4593;1.0000" values="0;0;1;1;0;0"/><line x1="260.0" y1="104" x2="260.0" y2="176" stroke="#e5484d" stroke-width="3"/>
<line x1="285.0" y1="104" x2="285.0" y2="176" stroke="#2ea043" stroke-width="3"/>
<text x="60" y="260" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">入力 v = 1/3 → 引くべきは 格子点 1（0.15）</text>
<text x="60" y="296" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">補正なし u = v = 0.333 → 0.12（誤差 0.03）</text>
<text x="60" y="326" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2ea043">補正あり u = (v·(N−1) + 0.5) / N = 0.375 → 0.15（誤差 0.00）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4590;0.4593;0.6516;0.6519;1.0000" values="0;0;1;1;0;0"/><line x1="460.0" y1="104" x2="460.0" y2="176" stroke="#e5484d" stroke-width="3"/>
<line x1="435.0" y1="104" x2="435.0" y2="176" stroke="#2ea043" stroke-width="3"/>
<text x="60" y="260" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">入力 v = 2/3 → 引くべきは 格子点 2（0.62）</text>
<text x="60" y="296" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">補正なし u = v = 0.667 → 0.68（誤差 0.06）</text>
<text x="60" y="326" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2ea043">補正あり u = (v·(N−1) + 0.5) / N = 0.625 → 0.62（誤差 0.00）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6516;0.6519;0.8441;0.8444;1.0000" values="0;0;1;1;0;0"/><line x1="660.0" y1="104" x2="660.0" y2="176" stroke="#e5484d" stroke-width="3"/>
<line x1="585.0" y1="104" x2="585.0" y2="176" stroke="#2ea043" stroke-width="3"/>
<text x="60" y="260" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">入力 v = 3/3 → 引くべきは 格子点 3（1.00）</text>
<text x="60" y="296" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">補正なし u = v = 1.000 → 1.00（誤差 0.00）</text>
<text x="60" y="326" text-anchor="start" style="font-size:16px;font-weight:700;fill:#2ea043">補正あり u = (v·(N−1) + 0.5) / N = 0.875 → 1.00（誤差 0.00）</text>
</g>
<text x="60" y="372" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">u = v のままだと、格子点の位置が半テクセルずれて、中間の値が混ざる。端の 0 と 1 以外で誤差が出る。</text>
</svg>

<!-- fig:lut-half-texel:end -->

## 解像度

| 解像度 | メモリ（FP16×4） | 特徴 |
| --- | --- | --- |
| **16³** | **約 32 KB** | **軽い・単純な調整向き** |
| **32³** | **約 256 KB** | **標準**。**ほとんどのルックで十分** |
| **64³** | **約 2 MB** | <strong>急峻な変換（強いコントラスト・複雑なルック）</strong> |

**調整が滑らか（なだらかな曲線）なら、小さな LUT でも補間で十分**きれいです。**急激な変化（切り捨て・強い色の入れ替え）が含まれる**と**大きな LUT** が**必要**です。

## 2D テクスチャに並べる（ストリップ）

**3D テクスチャを、2D の画像に「スライスを横に並べて」保存**する形式も**よく使われます**（**.png で外部ツールとのやり取り**）。

| 形式 | 内容 |
| --- | --- |
| **32×32×32 のストリップ** | **幅 1024・高さ 32 の画像**（**32 枚のスライスを横に並べる**） |
| **.cube** | **テキスト形式**（**DaVinci Resolve・多くのツールが出力**） |

**ゲームでは読み込み時に、2D のストリップを、3D テクスチャに変換**して**使います**。

## 広いダイナミック レンジを扱う（対数エンコード）

<strong>HDR の値（0〜数十）</strong>を**そのまま 0〜1 に収めて LUT を引く**と、**暗部の細かい階調が足りず、バンディング**が**出ます**。**対数（Log）で、広い範囲を 0〜1 に圧縮してから LUT を引く**ことが**多い**です。

```hlsl
float3 LinearToLog(float3 color) {
  const float kMinLog = -10.0;
  const float kMaxLog = 6.5;
  float3 log_c = log2(max(color, 1e-6));
  return saturate((log_c - kMinLog) / (kMaxLog - kMinLog));
}

float3 ApplyLutHdr(float3 hdr_color) {
  float3 encoded = LinearToLog(hdr_color);
  float3 uvw = encoded * ((kLutSize - 1.0) / kLutSize) + 0.5 / kLutSize;
  return color_lut.SampleLevel(linear_clamp, uvw, 0);
}
```

| 点 | 説明 |
| --- | --- |
| **`log2`** | **EV 単位の等間隔**（**人間の知覚に合う**） |
| **`kMinLog`・`kMaxLog`** | <strong>扱う範囲（例：−10〜+6.5 EV）</strong> |
| **LUT も同じ対数で作る** | **LUT を作る側と引く側で同じエンコード** |

| 方式 | 入力 | 向く場面 |
| --- | --- | --- |
| **LDR LUT** | <strong>トーンマップ後（0〜1）</strong> | **簡単・外部ツールの LUT** |
| **HDR（対数）LUT** | **HDR のリニアを対数でエンコード** | **トーンマップも LUT に含める** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **半テクセルのオフセット** | **必須** |
| **FP16・10 ビット** | **バンディングを避ける** |
| **32³ から始める** | **足りなければ 64³** |
| **LUT は一度作って使い回す** | **パラメータが変わった時だけ再生成**（[LUT の作り方](lut-authoring.md)） |
| **トーンマップも LUT に** | **曲線と色調整をまとめて焼く** |
| **ディザリングで、8 ビット出力のバンディングを消す** | **LUT 後にわずかなノイズを足す** |

## よくあるミス

??? failure "LUT を適用したら、黒と白の色がずれる"
    **半テクセルのオフセット**を入れる。

??? failure "LUT で、暗部にバンディング（縞）が出る"
    **FP16・10 ビットの形式**にする、**対数エンコード**、**ディザリング**。

??? failure "HDR の値をそのまま LUT に入れて、明部が全部同じ色"
    **`saturate` で潰れている**。**対数エンコード**で圧縮してから引く。

??? failure "LUT を作る側と引く側で、エンコードが違って、色が変"
    <strong>同じエンコード（対数・ガンマ）</strong>にそろえる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 3D LUT ＝ <strong>入力色を座標に、変換後の色を格納した 3D テクスチャ</strong>
    - [x] <strong>1 回のサンプルで、何段階の調整もまとめて適用</strong>
    - [x] <strong>32³ が標準</strong>。<strong>半テクセルのオフセット</strong>を<strong>忘れない</strong>
    - [x] <strong>FP16・10 ビット</strong>で<strong>バンディングを避ける</strong>
    - [x] <strong>HDR は対数エンコード</strong>してから引く

## 参考

- Hable, "Uncharted 2: HDR Lighting"（GDC 2010, LUT）
- Selan, "Cinematic Color: From Your Monitor to the Big Screen"（SIGGRAPH 2012）
- Adobe, "Cube LUT Specification"

## 関連ページ

- [カラー グレーディング](index.md)
- [LUT の作り方](lut-authoring.md)
- [基本の調整](basic-adjustments.md)
- [トーンマッピングと露出](../tonemapping/index.md)
