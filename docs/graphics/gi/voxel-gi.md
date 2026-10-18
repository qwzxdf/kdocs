---
title: Voxel GI
tags:
  - 描画
---

# Voxel GI

**SSGI**は**画面に映っているもの**しか見えませんでした。**ボクセル GI**（Voxel Cone Tracing、**VXGI**）は、**シーン全体を 3D の格子（ボクセル）に変換**し、**そこに「形（遮蔽）」と「光（出射光）」を保存**します。**画素から、半球の方向に「円錐（コーン）」を飛ばし**、**ボクセルの上をミップ マップをたどりながら進む**ことで、**画面外・裏側も含めた間接光**を<strong>ノイズなし（または少なく）</strong>で得られます。**2011 年の Crassin らの手法**で、**当時、リアルタイム GI の大きな進歩**でした。

!!! tip "ポイント"
    - シーンを<strong>ボクセル化</strong>し、<strong>各ボクセルに「不透明度」と「出射光（放射輝度）」</strong>を保存。
    - <strong>ボクセルのミップ マップ</strong>を作る（粗い階層）。<strong>遠くほど粗いミップを読む</strong>。
    - <strong>コーン トレース</strong>：<strong>画素から円錐を飛ばし</strong>、<strong>円錐の広がりに合うミップ</strong>を<strong>前から後ろへ累積</strong>。
    - <strong>拡散</strong>は<strong>広い円錐を数本</strong>（5〜6 本）、<strong>鏡面</strong>は<strong>細い円錐 1 本</strong>。
    - <strong>画面外も反映</strong>。<strong>ノイズが少ない</strong>（円錐が空間をまとめて積分）。
    - 欠点：<strong>ボクセルの解像度が粗い</strong>（<strong>光漏れ</strong>）。<strong>メモリ・更新コスト</strong>が重い。

## 原理

### ① ボクセル化

**シーンのジオメトリ**を、**3D の格子**（例：256³）に**書き込みます**。**各ボクセル**に<strong>そこにある表面の「色（アルベド）」・「法線」・「不透明度」</strong>を**保存**します。

ボクセル化の方法は、大きく 2 つあります。1 つは、ラスタライズを利用する方法です。三角形を、最も面積が大きくなる軸の方向に投影し、ピクセル シェーダーで 3D テクスチャに書き込みます。保守的ラスタライズを併用すると、小さな三角形も漏れなく拾えます。もう 1 つは、コンピュート シェーダーで、三角形ごとにボクセルへ書き込む方法です。更新のコストを抑えるため、静的な部分はキャッシュしておき、動く物だけを毎フレーム更新します。

### ② 光の注入

**各ボクセルに**、**直接光**（光源から、**シャドウ マップ**を使って）を**当てて**、<strong>そのボクセルの「出射光」</strong>（**アルベド × 直接光**）を計算し、**3D テクスチャに保存**します。

ボクセルに保存する値は、放射輝度（RGB）と不透明度（A）です。さらに、方向性も持たせる<strong>異方性ボクセル</strong>では、±X, ±Y, ±Z の 6 方向ごとに、その方向から見たときの値を保存します。これにより、方向による違い（薄い壁の表と裏で光が違うこと）を表せます。

### ③ ミップ マップの生成

**3D テクスチャ**に**ミップ マップ**を作ります。<strong>上位のミップほど、粗く（広い範囲の平均）</strong>なります。**円錐が広がるにつれて**、**粗いミップ**を読むことで、**円錐の太さに合った**、**範囲の平均**を得ます。

**異方性ボクセル**では、**ミップを作る際、方向ごとの値をそれぞれ平均**します。

<!-- fig:voxel-cone-trace:begin -->

<svg class="fig illust motion" data-fig="voxel-cone-trace" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-voxel-cone-trace" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="vx-clip"><rect x="40" y="92" width="700" height="240"/>
</clipPath>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">コーン トレース:遠いほど、粗いミップ（大きなボクセル）を読む</text>
<line x1="40" y1="100" x2="40" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="60" y1="100" x2="60" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="80" y1="100" x2="80" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="100" y1="100" x2="100" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="120" y1="100" x2="120" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="140" y1="100" x2="140" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="160" y1="100" x2="160" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="180" y1="100" x2="180" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="200" y1="100" x2="200" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="220" y1="100" x2="220" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="240" y1="100" x2="240" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="260" y1="100" x2="260" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="280" y1="100" x2="280" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="300" y1="100" x2="300" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="320" y1="100" x2="320" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="340" y1="100" x2="340" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="360" y1="100" x2="360" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="380" y1="100" x2="380" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="400" y1="100" x2="400" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="420" y1="100" x2="420" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="440" y1="100" x2="440" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="460" y1="100" x2="460" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="480" y1="100" x2="480" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="500" y1="100" x2="500" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="520" y1="100" x2="520" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="540" y1="100" x2="540" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="560" y1="100" x2="560" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="580" y1="100" x2="580" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="600" y1="100" x2="600" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="620" y1="100" x2="620" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="640" y1="100" x2="640" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="660" y1="100" x2="660" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="680" y1="100" x2="680" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="700" y1="100" x2="700" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="720" y1="100" x2="720" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="100" x2="740" y2="100" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="120" x2="740" y2="120" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="140" x2="740" y2="140" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="160" x2="740" y2="160" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="180" x2="740" y2="180" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="200" x2="740" y2="200" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="220" x2="740" y2="220" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="240" x2="740" y2="240" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="260" x2="740" y2="260" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="280" x2="740" y2="280" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="300" x2="740" y2="300" stroke="#f1f5f9" stroke-width="1"/>
<line x1="40" y1="320" x2="740" y2="320" stroke="#f1f5f9" stroke-width="1"/>
<rect x="600" y="130" width="40" height="150" fill="#e5aa28"/>
<text x="620" y="120" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5aa28">光る面</text>
<circle cx="40" cy="200" r="8" fill="#2563eb"/>
<polygon points="40,200 600,60.38 600,339.62" fill="#2563eb" fill-opacity="0.08" stroke="#2563eb" stroke-width="1.5"/>
<g opacity="0" clip-path="url(#vx-clip)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><rect x="60.0" y="190.0" width="20" height="20" fill="#fde68a" fill-opacity="0.5" stroke="#e5aa28" stroke-width="2"/>
<text x="70.0" y="226.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">ミップ 0</text>
</g>
<g opacity="0" clip-path="url(#vx-clip)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;1.0000" values="0;0;1;1"/><rect x="84.0" y="190.0" width="20" height="20" fill="#fde68a" fill-opacity="0.5" stroke="#e5aa28" stroke-width="2"/>
<text x="94.0" y="226.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">ミップ 0</text>
</g>
<g opacity="0" clip-path="url(#vx-clip)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;1.0000" values="0;0;1;1"/><rect x="98.0" y="180.0" width="40" height="40" fill="#fcd34d" fill-opacity="0.5" stroke="#e5aa28" stroke-width="2"/>
<text x="118.0" y="236.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">ミップ 1</text>
</g>
<g opacity="0" clip-path="url(#vx-clip)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3182;0.3185;1.0000" values="0;0;1;1"/><rect x="120.0" y="160.0" width="80" height="80" fill="#fbbf24" fill-opacity="0.5" stroke="#e5aa28" stroke-width="2"/>
<text x="160.0" y="256.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">ミップ 2</text>
</g>
<g opacity="0" clip-path="url(#vx-clip)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/><rect x="198.0" y="160.0" width="80" height="80" fill="#fbbf24" fill-opacity="0.5" stroke="#e5aa28" stroke-width="2"/>
<text x="238.0" y="256.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">ミップ 2</text>
</g>
<g opacity="0" clip-path="url(#vx-clip)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000" values="0;0;1;1"/><rect x="236.0" y="120.0" width="160" height="160" fill="#f59e0b" fill-opacity="0.5" stroke="#e5aa28" stroke-width="2"/>
<text x="316.0" y="296.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">ミップ 3</text>
</g>
<g opacity="0" clip-path="url(#vx-clip)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/><rect x="386.0" y="120.0" width="160" height="160" fill="#f59e0b" fill-opacity="0.5" stroke="#e5aa28" stroke-width="2"/>
<text x="466.0" y="296.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">ミップ 3</text>
</g>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 1:円錐の幅 ≒ 20 → ミップ 0（1 辺 20）を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1553;0.1556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 2:円錐の幅 ≒ 27 → ミップ 0（1 辺 20）を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;0.2367;0.2370;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 3:円錐の幅 ≒ 39 → ミップ 1（1 辺 40）を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;0.3182;0.3185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 4:円錐の幅 ≒ 60 → ミップ 2（1 辺 80）を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3182;0.3185;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 5:円錐の幅 ≒ 99 → ミップ 2（1 辺 80）を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 6:円錐の幅 ≒ 138 → ミップ 3（1 辺 160）を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5627;0.5630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 7:円錐の幅 ≒ 212 → ミップ 3（1 辺 160）を読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">近くは細かいボクセル、遠くは粗いミップ。少ない読み取りで、広い範囲の光を集められる（拡散は 5〜6 本の円錐）。</text>
</svg>

<!-- fig:voxel-cone-trace:end -->

### ④ コーン トレース

**画素から**、**半球に数本の円錐**を**飛ばします**。**円錐は進むにつれて、広がり**ます。**各ステップで円錐の太さに対応するミップ**を**読み**、**前から後ろへ（アルファ ブレンドのように）累積**します。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="コーン トレース">
<text x="20" y="24" class="fig-title">円錐が広がるにつれて、粗いミップを読み、前から後ろへ累積する</text>
<circle cx="80" cy="140" r="6" fill="currentColor"/><text x="60" y="166" style="font-size:12px">画素</text>
<polygon points="80,140 700,60 700,220" fill="rgba(76,139,245,0.12)" stroke="currentColor" stroke-dasharray="4 3"/>
<circle cx="140" cy="132" r="8" fill="none" stroke="currentColor"/><circle cx="220" cy="122" r="16" fill="none" stroke="currentColor"/><circle cx="350" cy="106" r="32" fill="none" stroke="currentColor"/><circle cx="550" cy="82" r="60" fill="none" stroke="currentColor"/>
<text x="110" y="210" style="font-size:12px">細かいミップ</text><text x="500" y="210" style="font-size:12px">粗いミップ</text>
<text x="40" y="250" style="font-size:12px">ステップごとに、円の大きさ（円錐の太さ）に合うミップ レベルを読む。不透明度が 1 に達したら終了</text>
</svg>

<div class="formula">color ← color + (1 − α) · c_i　、　α ← α + (1 − α) · a_i　（前から後ろへ）</div>

```hlsl
float4 ConeTrace(float3 origin, float3 dir, float aperture) {
  float4 acc = 0.0;
  float dist = kVoxelSize;
  [loop] for (int i = 0; i < kConeSteps && acc.a < 1.0; ++i) {
    float diameter = max(kVoxelSize, 2.0 * aperture * dist);
    float mip = log2(diameter / kVoxelSize);
    float3 uvw = WorldToVoxelUVW(origin + dir * dist);
    float4 s = voxel_tex.SampleLevel(linear_sampler, uvw, mip);
    acc += (1.0 - acc.a) * s;
    dist += diameter * 0.5;
  }
  return acc;
}
```

| 点 | 説明 |
| --- | --- |
| **`aperture`** | **円錐の開き**（`tan(半角)`）。**広いほど、ぼやけた結果** |
| **`diameter`** | **その距離での円錐の太さ**（`2 · aperture · dist`）。**ミップ選択**に使う |
| **`mip = log2(diameter / voxel_size)`** | **太さがボクセル何個分か**を**ミップ レベル**に**変換** |
| **前から後ろ** | **不透明度が 1 に達する**と、**以降は見えない**ので**打ち切る** |

### 拡散と鏡面

円錐の使い方は、用途によって変わります。拡散の間接光には、半球に 5〜6 本の広い円錐を余弦重み付きで配置します。鏡面の間接光には、反射方向に細い円錐を 1 本置き、粗さで開きを調整します。短い距離の円錐の不透明度からは、環境光遮蔽（AO）も同時に得られます。

## 利点と限界

| 利点 | 限界 |
| --- | --- |
| **画面外・裏側**も**反映**（**世界全体が対象**） | **ボクセルが粗い**（256³ で数 cm〜数十 cm の分解能） |
| **ノイズが少ない**（**円錐が積分済みの値を読む**） | **光漏れ**（**薄い壁**で**ボクセルが混ざる**） |
| **動く物・動くライトが反映される** | **メモリ**（3D テクスチャ ＋ ミップ ＋ 異方性） |
| <strong>鏡面（粗めの反射）</strong>も、**同じ構造**で得られる | **ボクセル化・注入・ミップ生成が毎フレームのコスト** |
| **AO も同時に得られる** | **カスケード**で**遠くを粗く**する工夫が必要（視点の周りのみ） |


限界は、ボクセルが粗いこと（256³ で数 cm〜数十 cm の分解能）、薄い壁でボクセルが混ざる光漏れ、3D テクスチャとミップと異方性によるメモリの大きさ、ボクセル化・注入・ミップ生成が毎フレームのコストになること、そして遠くを粗くするカスケードが必要になることです。

限界は、ボクセルが粗いこと（256³ で数 cm〜数十 cm の分解能）、薄い壁でボクセルが混ざる光漏れ、3D テクスチャとミップと異方性によるメモリの大きさ、ボクセル化・注入・ミップ生成が毎フレームのコストになること、そして遠くを粗くするカスケードが必要になることです。

### 光漏れ

**ボクセルが粗いと薄い壁の両側が同じボクセルに入り**、**壁を貫通して、光が漏れ**ます。

| 対策 | 内容 |
| --- | --- |
| **異方性ボクセル** | **方向ごとの値**を持ち、**表と裏を区別** |
| **ボクセルを細かく** | **解像度を上げる**（メモリ・コストが増える） |
| **壁の厚みを増やす** | **レベル デザインで薄い壁を避ける** |
| **オフセット** | **サンプル位置を法線方向にずらす** |

## カスケード（クリップマップ）

**シーン全体を細かいボクセルで覆う**ことは、**メモリが足りません**。**視点の周りに入れ子になった複数のボクセル グリッド**（**カスケード**）を置き、**近くは細かく、遠くは粗く**します（[Cascaded Shadow Maps (CSM)](../shadows/cascaded.md)と同じ発想）。**カメラの移動に応じて、グリッドをスクロール**させます。

## 現在の位置づけ

**Crassin の VXGI** は、**NVIDIA の VXGI**として製品化されましたが、**メモリ・コスト・光漏れ**の問題から、**現在の主流ではありません**。

ボクセル GI の後継や類似の方式が、いくつかあります。<strong>Lumen</strong>（Unreal Engine 5）は、ソフトウェアのレイトレースで距離場とサーフェス キャッシュを使い、画面空間、距離場、グローバル SDF の階層でトレースします。<strong>SDFGI</strong>（Godot）は、カスケードの SDF とプローブを組み合わせます。<strong>Radiance Cascades</strong> は、空間と方向の階層構造を持つ新しい方式です（[Ray-Traced GI](rt-gi/index.md)）。

<strong>「ボクセル（またはそれに類する 3D 格子）に光を保存し、円錐/レイでたどる」</strong>という**考え方**は、**多くの動的 GI に受け継がれています**。

## よくあるミス

??? failure "ボクセル化で小さい三角形が、漏れて、穴が空く"
    **保守的ラスタライズ**を使います。

??? failure "円錐のミップ選択が合わず、ぼやけすぎ・ブロック状になる"
    **`mip = log2(diameter / voxel_size)`** で、**太さに合わせて**選びます。

??? failure "薄い壁の向こうの光が、漏れる"
    **異方性ボクセル**・**壁を厚く**・**サンプル位置のオフセット**。

??? failure "メモリを使いすぎる"
    **カスケード**で**遠くを粗く**・**ボクセルの解像度を下げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボクセル GI ＝ <strong>シーンを 3D 格子に変換</strong>し、<strong>不透明度と出射光を保存</strong>、<strong>ミップ マップ</strong>を作る
    - [x] <strong>コーン トレース</strong>：<strong>円錐の太さに合うミップ</strong>を、<strong>前から後ろへ累積</strong>
    - [x] <strong>拡散は広い円錐を数本</strong>、<strong>鏡面は細い円錐 1 本</strong>
    - [x] <strong>画面外も反映・ノイズ少ない</strong>が<strong>解像度が粗い・光漏れ・メモリが重い</strong>
    - [x] <strong>現在は Lumen・SDFGI などの派生</strong>に、<strong>考え方が受け継がれている</strong>

## 参考

- Crassin et al., "Interactive Indirect Illumination Using Voxel Cone Tracing"（Pacific Graphics 2011）
- Crassin, "GigaVoxels"（博士論文、2011）
- Godot, "SDFGI"（ドキュメント）

## 関連ページ

- [Global Illumination (GI)](index.md)
- [GI Theory](theory/index.md)
- [SSGI](ssgi.md)
- [Ray-Traced GI](rt-gi/index.md)
- [Cascaded Shadow Maps (CSM)](../shadows/cascaded.md)
