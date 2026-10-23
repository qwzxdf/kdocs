---
title: Quality and Performance
tags:
  - 描画
---

# Quality and Performance

<strong>ボリューメトリック フォグは、解像度とスライス数で品質とコストが大きく変わります</strong>。このページでは 品質と速度の目安を説明します。

!!! tip "ポイント"
    - 解像度：160×90 が標準（1080p の場合）。
    - スライス数：64が標準。
    - ライトの数が多いと重い。
    - 品質設定で解像度とスライス数を切り替える。

## 品質と速度
| 項目 | 内容 |
| --- | --- |
| 解像度 | 160×90×64 で十分。重ければ 80×45×32 |
| コスト | 0.3〜1 ms 程度 |
| 局所ライトの数 | 多いほど重い。影付きのライトは数本まで |
| 遠距離 | 範囲外は距離フォグ（[Aerial Perspective and Fog](../aerial-fog/index.md)）に任せる |
| 雲・大気との組み合わせ | 近くはボリューメトリック フォグ、遠くは空気遠近法 LUT |

### どこでコストが決まるか

ボリューメトリック フォグのコストは、主に 3 つのパスで発生します。<strong>光の注入</strong>はセルごとにすべてのライトと影を評価するので、セル数 × ライト数に比例します。最も重いパスで影付きライトの数が最大の要因です。積分は奥行き方向の累積で、セル数に比例しますが 1 セルあたりの処理は軽く、全体で 0.1 ms 以下です。適用は画素ごとに 3D テクスチャを 1 回引くだけで、安価です。

したがってコストを下げたいときは、まず光の注入を見ます。影付きライトを減らすライトを遠くのものから省く、セル数（解像度）を下げるのいずれかです。解像度を下げると品質が落ちるのは主に光の筋の細かさなので、時間蓄積（[Temporal Accumulation](temporal.md)）で補うと、見た目を保ちながら軽くできます。

### 範囲の選び方

froxel はカメラの前方のごく近い範囲だけを覆うのが現実的です。たとえば最大距離を 64〜128 m にすれば、64 スライスで十分な密度が出ます。それより遠くは空気遠近法の LUT で連続的につなぎます。境目で急に変わらないよう最大距離の手前でボリューメトリック フォグの寄与をフェードアウトさせ、遠景のフォグと重ねます。

<!-- fig:froxel-depth-split:begin -->

<svg class="fig illust motion" data-fig="froxel-depth-split" viewBox="0 0 780 340" role="img"><rect x="0" y="0" width="780" height="340" rx="14" fill="#ffffff"/>
<defs><marker id="arr-froxel-depth-split" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">スライスを奥行きに並べる 2 通り: 等間隔と、手前を細かく</text>
<line x1="60" y1="110" x2="720" y2="110" stroke="#94a3b8" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="0;0;1;1"/><line x1="60.0" y1="88" x2="60.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="101.25" y1="88" x2="101.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="142.5" y1="88" x2="142.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="183.75" y1="88" x2="183.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="225.0" y1="88" x2="225.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="266.25" y1="88" x2="266.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="307.5" y1="88" x2="307.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="348.75" y1="88" x2="348.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="390.0" y1="88" x2="390.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="431.25" y1="88" x2="431.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="472.5" y1="88" x2="472.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="513.75" y1="88" x2="513.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="555.0" y1="88" x2="555.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="596.25" y1="88" x2="596.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="637.5" y1="88" x2="637.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="678.75" y1="88" x2="678.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="720.0" y1="88" x2="720.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<text x="60" y="72" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">等間隔(1 枚 6.3 m)</text>
</g>
<line x1="60" y1="220" x2="720" y2="220" stroke="#94a3b8" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000" values="0;0;1;1"/><line x1="60.0" y1="198" x2="60.0" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="63.49744860406542" y1="198" x2="63.49744860406542" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="67.98826150524448" y1="198" x2="67.98826150524448" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="73.75457941194762" y1="198" x2="73.75457941194762" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="81.1586781648561" y1="198" x2="81.1586781648561" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="90.66572915125658" y1="198" x2="90.66572915125658" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="102.87302425554108" y1="198" x2="102.87302425554108" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="118.54750143845021" y1="198" x2="118.54750143845021" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="138.6739285345976" y1="198" x2="138.6739285345976" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="164.5167724731637" y1="198" x2="164.5167724731637" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="197.69964092977727" y1="198" x2="197.69964092977727" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="240.3072874266751" y1="198" x2="240.3072874266751" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="295.01658847393827" y1="198" x2="295.01658847393827" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="365.2647215478455" y1="198" x2="365.2647215478455" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="455.46510988960506" y1="198" x2="455.46510988960506" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="571.2847011155291" y1="198" x2="571.2847011155291" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="720.0" y1="198" x2="720.0" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<text x="60" y="182" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">指数(手前が細かい)</text>
</g>
<text x="60" y="275" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">カメラ 0 m</text>
<text x="720" y="275" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">100 m</text>
<text x="390" y="315" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">16 枚のスライスを、0〜100 m に並べる<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="1;1;0;0"/></text>
<text x="390" y="315" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">等間隔: 遠くも近くも同じ粗さ<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;0.3330;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="315" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">指数: 目に近い所を細かく、遠くを粗く(遠くは、もともと小さく見える)<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:froxel-depth-split:end -->

## 品質を決める要素

ボリューム フォグの <strong>見た目</strong>と、コストはいくつかの設定で、決まります。

| 要素 | 内容 | 大きくすると |
| --- | --- | --- |
| froxel の解像度（x、y） | 画面の横・縦の分割数 | 細かい光の筋。重い |
| 奥行きの分割数（z） | 奥行きの、スライス数 | 縞が減る。重い |
| 最大の距離 | froxel が、覆う範囲 | 遠くまでボリュームの霧。スライスが粗くなる |
| ライトの数 | 注入する、ライトの数 | 光の玉が増える。重い |
| 影の品質 | 注入でのシャドウ マップの、読み方 | 光の筋がきれい |

## よくある見た目の問題と対策

### ① 縞（バンディング）

<strong>奥行き方向のスライス</strong>に沿って、縞模様が見えます。スライスの境目で値が急に変わるためです。

| 原因 | 対策 |
| --- | --- |
| スライスが粗い | スライス数を、増やす。近くを細かく（指数的な割り当て。[Froxels](froxel.md)） |
| トライリニア補間でも滑らかさが、足りない | トリキュービック補間（高次の補間）で読む。コストが増える |
| ジッターなし | ジッター + 時間方向の平均（[Temporal Accumulation](temporal.md)）で縞を、細かいノイズに変えて平均 |

### ② 光の筋がぼやける

低解像度の froxel では 細い、光の筋（窓の格子）がぼやけ、消えます。

| 対策 | 内容 |
| --- | --- |
| 解像度を上げる | 160×90 → 240×135 など。メモリ・コストが増える |
| 重要なライトだけ別の方法（放射状ブラー、メッシュ）で補う | [Screen-Space Radial Blur](../god-rays/radial-blur.md)、[Light Shaft Meshes](../god-rays/mesh-shafts.md) |
| ぼやけを許容 | 霧はゆるやかな効果。ある程度のぼやけは自然 |

### ③ 光漏れ（ライトが壁を、越える）

低解像度の froxelでは 壁の、向こう側のセルも壁のこちら側と、同じセルに混ざり壁の向こうの光が、漏れて見えます。

| 対策 | 内容 |
| --- | --- |
| 解像度を上げる | セルを、小さくする |
| セルの影を複数サンプル | セルの中の、複数の位置でシャドウ マップを引き、平均 |
| ジッター + 履歴 | 複数フレームで、平均すると漏れが目立ちにくい |

### ④ 遠景で解像度が粗い

奥行きが遠いスライスは 厚く、1 つのセルが非常に広い範囲を、代表します。遠くの霧の細部（光の筋、局所的な霧）が失われます。

| 対策 | 内容 |
| --- | --- |
| 最大距離を短く（64 m〜128 m） | 近くだけ、細かく |
| 遠景は別の方法（空気遠近法） | [Physically Based Aerial Perspective](../aerial-fog/physical.md)、[Height Fog](../aerial-fog/height-fog.md) |

## コストの内訳（目安、1080p）

| 処理 | コスト |
| --- | --- |
| 密度（ノイズ読み込みボリューム） | 0.1〜0.2 ms |
| ライト注入（太陽 + 数個のライト、影の読み込み） | 0.3〜0.8 ms（ライトの数、影の有無で変わる） |
| 積分（奥行き方向のループ） | 0.05〜0.1 ms |
| 時間方向の平均 | 0.05〜0.1 ms |
| 適用（全画素で 1 回の 3D テクスチャ読み込み） | 0.1〜0.2 ms |
| 合計 | 0.6〜1.4 ms |

<strong>ライト注入が最も重い</strong>ことが、多いです。影つきライトの数を絞る（[Shadows for Many Lights](../../shadows/local-lights/many-lights.md)）、重要なライトだけボリューム フォグに、注入するといった工夫が効きます。

## 品質設定のプリセット

| 設定 | froxel | 最大距離 | ライト | 時間方向 |
| --- | --- | --- | --- | --- |
| 低 | 80×45×32 | 64 m | 太陽のみ | あり |
| 中 | 160×90×64 | 128 m | 太陽 + 影つき 2 | あり |
| 高 | 240×135×96 | 256 m | 太陽 + 影つき 4 + 影なし 多数 | あり |
| 最高 | 320×180×128 | 512 m | すべて | あり |

<strong>ユーザー設定</strong>で 切り替えられるように、しておくと幅広い環境で動かせます。

## よくあるミス

??? failure "フォグの計算が重く、フレーム時間が伸びる"
    <strong>解像度・スライス数を下げる</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 解像度とスライス数で調整

## 参考

- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Volumetric Fog](index.md)
- [Froxels](froxel.md)
