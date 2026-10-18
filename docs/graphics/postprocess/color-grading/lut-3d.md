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

<svg class="fig illust motion" data-fig="lut-half-texel" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lut-half-texel" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">LUT の半テクセル補正: テクスチャの座標 0 と 1 は、端のテクセルの「中心」ではない。補正しないと、表全体がずれる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">16 個の表(テクセル)を、GPU の補間で引く。入力 0 〜 1 を、そのまま座標にした場合と、補正した場合の誤差</text>
<rect x="30" y="96" width="660" height="260" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 表の値(黒い点 = 各テクセルの中心)と、引いた値</text>
<path d="M70.0,330.0 L77.5,327.98 L85.0,325.93 L92.5,323.84 L100.0,321.71 L107.5,319.55 L115.0,317.36 L122.5,315.13 L130.0,312.88 L137.5,310.6 L145.0,308.28 L152.5,305.94 L160.0,303.57 L167.5,301.17 L175.0,298.75 L182.5,296.31 L190.0,293.84 L197.5,291.35 L205.0,288.84 L212.5,286.3 L220.0,283.75 L227.5,281.18 L235.0,278.59 L242.5,275.98 L250.0,273.36 L257.5,270.72 L265.0,268.07 L272.5,265.41 L280.0,262.73 L287.5,260.04 L295.0,257.34 L302.5,254.64 L310.0,251.92 L317.5,249.2 L325.0,246.47 L332.5,243.73 L340.0,240.99 L347.5,238.25 L355.0,235.5 L362.5,232.75 L370.0,230.0 L377.5,227.25 L385.0,224.5 L392.5,221.75 L400.0,219.01 L407.5,216.27 L415.0,213.53 L422.5,210.8 L430.0,208.08 L437.5,205.36 L445.0,202.66 L452.5,199.96 L460.0,197.27 L467.5,194.59 L475.0,191.93 L482.5,189.28 L490.0,186.64 L497.5,184.02 L505.0,181.41 L512.5,178.82 L520.0,176.25 L527.5,173.7 L535.0,171.16 L542.5,168.65 L550.0,166.16 L557.5,163.69 L565.0,161.25 L572.5,158.83 L580.0,156.43 L587.5,154.06 L595.0,151.72 L602.5,149.4 L610.0,147.12 L617.5,144.87 L625.0,142.64 L632.5,140.45 L640.0,138.29 L647.5,136.16 L655.0,134.07 L662.5,132.02 L670.0,130.0" fill="none" stroke="#64748b" stroke-width="2.5" stroke-dasharray="5 4"/>
<circle cx="88.75" cy="330.0" r="4" fill="#1f2937"/>
<circle cx="126.25" cy="318.82" r="4" fill="#1f2937"/>
<circle cx="163.75" cy="306.72" r="4" fill="#1f2937"/>
<circle cx="201.25" cy="293.84" r="4" fill="#1f2937"/>
<circle cx="238.75" cy="280.32" r="4" fill="#1f2937"/>
<circle cx="276.25" cy="266.3" r="4" fill="#1f2937"/>
<circle cx="313.75" cy="251.92" r="4" fill="#1f2937"/>
<circle cx="351.25" cy="237.33" r="4" fill="#1f2937"/>
<circle cx="388.75" cy="222.67" r="4" fill="#1f2937"/>
<circle cx="426.25" cy="208.08" r="4" fill="#1f2937"/>
<circle cx="463.75" cy="193.7" r="4" fill="#1f2937"/>
<circle cx="501.25" cy="179.68" r="4" fill="#1f2937"/>
<circle cx="538.75" cy="166.16" r="4" fill="#1f2937"/>
<circle cx="576.25" cy="153.28" r="4" fill="#1f2937"/>
<circle cx="613.75" cy="141.18" r="4" fill="#1f2937"/>
<circle cx="651.25" cy="130.0" r="4" fill="#1f2937"/>
<path d="M70.0,330.0 L77.5,330.0 L85.0,330.0 L92.5,328.88 L100.0,326.65 L107.5,324.41 L115.0,322.18 L122.5,319.94 L130.0,317.61 L137.5,315.19 L145.0,312.77 L152.5,310.35 L160.0,307.93 L167.5,305.43 L175.0,302.86 L182.5,300.28 L190.0,297.7 L197.5,295.13 L205.0,292.49 L212.5,289.78 L220.0,287.08 L227.5,284.37 L235.0,281.67 L242.5,278.91 L250.0,276.11 L257.5,273.31 L265.0,270.5 L272.5,267.7 L280.0,264.86 L287.5,261.98 L295.0,259.11 L302.5,256.23 L310.0,253.36 L317.5,250.46 L325.0,247.54 L332.5,244.63 L340.0,241.71 L347.5,238.79 L355.0,235.86 L362.5,232.93 L370.0,230.0 L377.5,227.07 L385.0,224.14 L392.5,221.21 L400.0,218.29 L407.5,215.37 L415.0,212.46 L422.5,209.54 L430.0,206.64 L437.5,203.77 L445.0,200.89 L452.5,198.02 L460.0,195.14 L467.5,192.3 L475.0,189.5 L482.5,186.69 L490.0,183.89 L497.5,181.09 L505.0,178.33 L512.5,175.63 L520.0,172.92 L527.5,170.22 L535.0,167.51 L542.5,164.87 L550.0,162.3 L557.5,159.72 L565.0,157.14 L572.5,154.57 L580.0,152.07 L587.5,149.65 L595.0,147.23 L602.5,144.81 L610.0,142.39 L617.5,140.06 L625.0,137.82 L632.5,135.59 L640.0,133.35 L647.5,131.12 L655.0,130.0 L662.5,130.0 L670.0,130.0" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="0;0;1;1"/></path>
<path d="M70.0,330.0 L77.5,327.9 L85.0,325.81 L92.5,323.71 L100.0,321.62 L107.5,319.52 L115.0,317.31 L122.5,315.04 L130.0,312.77 L137.5,310.5 L145.0,308.24 L152.5,305.92 L160.0,303.5 L167.5,301.09 L175.0,298.67 L182.5,296.26 L190.0,293.84 L197.5,291.3 L205.0,288.77 L212.5,286.23 L220.0,283.7 L227.5,281.16 L235.0,278.56 L242.5,275.94 L250.0,273.31 L257.5,270.68 L265.0,268.05 L272.5,265.4 L280.0,262.7 L287.5,260.01 L295.0,257.31 L302.5,254.62 L310.0,251.92 L317.5,249.18 L325.0,246.45 L332.5,243.71 L340.0,240.98 L347.5,238.24 L355.0,235.5 L362.5,232.75 L370.0,230.0 L377.5,227.25 L385.0,224.5 L392.5,221.76 L400.0,219.02 L407.5,216.29 L415.0,213.55 L422.5,210.82 L430.0,208.08 L437.5,205.38 L445.0,202.69 L452.5,199.99 L460.0,197.3 L467.5,194.6 L475.0,191.95 L482.5,189.32 L490.0,186.69 L497.5,184.06 L505.0,181.44 L512.5,178.84 L520.0,176.3 L527.5,173.77 L535.0,171.23 L542.5,168.7 L550.0,166.16 L557.5,163.74 L565.0,161.33 L572.5,158.91 L580.0,156.5 L587.5,154.08 L595.0,151.76 L602.5,149.5 L610.0,147.23 L617.5,144.96 L625.0,142.69 L632.5,140.48 L640.0,138.38 L647.5,136.29 L655.0,134.19 L662.5,132.1 L670.0,130.0" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3021;0.3023;1.0000" values="0;0;1;1"/></path>
<circle cx="86" cy="120" r="6" fill="#64748b"/>
<text x="96" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">本当のカーブ</text>
<circle cx="180.39999999999998" cy="120" r="6" fill="#e5484d"/>
<text x="190.39999999999998" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">そのまま 0〜1 を座標に</text>
<circle cx="354.59999999999997" cy="120" r="6" fill="#2ea043"/>
<text x="364.59999999999997" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">補正: u × (N−1)/N + 0.5/N</text>
<rect x="710" y="96" width="220" height="260" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="710" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">最大の誤差</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1161;0.1163;1.0000" values="0;0;1;1"/><text x="726" y="140" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">そのまま</text>
<text x="726" y="170" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d">0.0252</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3487;0.3488;1.0000" values="0;0;1;1"/><text x="726" y="210" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">補正あり</text>
<text x="726" y="240" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2ea043">0.0006</text>
</g>
<rect x="30" y="376" width="900" height="100" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="366" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">クランプと補間の仕組み</text>
<text x="50" y="412" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">座標 0 は、最初のテクセルの「左端」。中心は 0.5/16 = 0.0312 の位置</text>
<text x="50" y="440" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">座標 0〜1 を、そのまま、テクセル 0〜15 の位置に使うと、表全体が、少し伸びて(縮んで)引かれる。中間の色が、本来の値と、ずれる</text>
<text x="50" y="462" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">補正は、入力を、最初と最後のテクセルの中心の間に押し込む</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5347;0.5349;1.0000" values="0;0;1;1"/><rect x="560" y="486" width="370" height="40" rx="12" fill="#fef2f2" stroke="#e5484d" stroke-width="2.5"/>
<text x="576" y="510" text-anchor="start" style="font-size:13px;font-weight:700;fill:#991b1b">補正しないと、中間の明るさが、わずかにずれる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">LUT を引くとき、入力の 0〜1 を、そのまま座標にしてはいけない<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">そのまま引くと、中間で、ずれる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.3021;0.3023;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">半テクセルぶん、内側へ寄せると、ぴったり合う<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3021;0.3023;0.5347;0.5349;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">3D LUT でも、同じ補正をする(3 軸すべて)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5347;0.5349;1.0000;1.0000" values="0;0;1;1;0"/></text>
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

LUT を 2D の画像に保存する形式もよく使われます。32×32×32 のストリップは、幅 1024・高さ 32 の画像に、32 枚のスライスを横に並べたもので、.png で外部ツールとやり取りできます。.cube はテキスト形式で、DaVinci Resolve や多くのツールが出力します。

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

対数エンコードのコードの要点です。`log2` を使うと、EV 単位で等間隔になり、人間の知覚に合います。`kMinLog` と `kMaxLog` は、扱う範囲です（例：−10〜+6.5 EV）。LUT も同じ対数で作ります。LUT を作る側と引く側で、同じエンコードを使います。

LUT には 2 つの方式があります。LDR LUT は、トーンマップ後（0〜1）を入力にし、簡単で、外部ツールの LUT にも対応できます。HDR（対数）LUT は、HDR のリニアを対数でエンコードして入力にし、トーンマップも LUT に含められます。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **半テクセルのオフセット** | **必須** |
| **FP16・10 ビット** | **バンディングを避ける** |
| **32³ から始める** | **足りなければ 64³** |
| **LUT は一度作って使い回す** | **パラメータが変わった時だけ再生成**（[Authoring LUTs](lut-authoring.md)） |
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

- [Color Grading](index.md)
- [Authoring LUTs](lut-authoring.md)
- [Basic Adjustments](basic-adjustments.md)
- [Tone Mapping and Exposure](../tonemapping/index.md)
