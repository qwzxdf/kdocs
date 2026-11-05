---
title: Taxonomy of Methods
tags:
  - 描画
---

# Taxonomy of Methods

間接光の手法はライトマップ、プローブ、SSGI、ボクセル、DDGI、Lumen、ReSTIR と名前がたくさんあります。1 つずつ覚えようとするとどれも別の物に見えて、選ぶ基準が見えません。ところが、どの手法も「光の情報をいつ計算して、どこに持つか」の 2 つで決まっています。この 2 つが決まるとその手法が何を得意とし、どこで破綻するかがほぼ決まります。このページでは 2 つの軸で手法を整理し、軸 2（どこに持つか）の 4 種類を同じ形の HLSL で並べて書き画面空間が取れない光の割合を、C++ で数えます。

!!! tip "ポイント"
    - 軸 1 は「いつ計算するか」。事前（ベイク）、光だけ動的、全部動的の 3 段階。動く物と動く光に対応できるかが決まる。
    - 軸 2 は「どこに持つか」。面、空間の点、画面、ボクセル、レイの 5 種類。画面の外の光が取れるかが決まる。
    - 画面空間は画面に映っている範囲の光しか取れない。空っぽの部屋の例で水平画角 90° でも光の約半分は視錐台の外から来る。
    - 画面だけでは足りない場面は多い。壁際で平らな壁しか映らないときは画面から取れる光が 0 % になる。
    - 実際のゲームは複数を組み合わせる。焼いた光を土台にして画面空間が取れた分だけ重ねるという形が基本。

!!! info "このページを読む前に"
    - [GI Theory](index.md)（このセクション全体の地図と読む順番）

## 読んだ資料 {#sources}

- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）。全 4 ページを読みました。空間の点に持つ光を 9 個の係数で表せる根拠です。
- Wronski, "Volumetric Fog: Unified compute shader based solution to atmospheric scattering"（SIGGRAPH 2014）と、Valve の Ambient Cube の論文は、別ページ（[Lightmaps](../lightmaps/index.md)、Atmosphere の Volumetric Fog）の執筆で読みました。ここでは、空間に格子で持つという考え方の参照にとどめます。
- Kajiya の "The Rendering Equation"（1986）、Real-Time Rendering 第 4 版、Lumen の SIGGRAPH 2022 の発表は、このページの執筆では読んでいません。各手法の中身はそれぞれのページで扱います。

HLSL は `fxc`（`ps_5_0`）でコンパイルして確かめました。C++ は MSVC で実行しました。「受け取る面の情報から間接光の色を返す」という共通の形は、このページが説明のために作ったもので、どのエンジンのコードでもありません。

間接光とは直接光が当たった面が「次の光源」になって届ける光です。次の図は赤い壁で跳ね返った光が、隣の床に色をにじませる様子です。手法はどれもこの光を何らかの形で近似します。

<!-- fig:gi-color-bleeding:begin -->

<svg class="fig illust motion" data-fig="gi-color-bleeding" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gi-color-bleeding" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<linearGradient id="gi-bleed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff5a5f" stop-opacity="0.75"/>
<stop offset="1" stop-color="#ff5a5f" stop-opacity="0"/>
</linearGradient>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">間接光:光が壁で跳ね返って、隣の面に色がにじむ</text>
<rect x="80" y="60" width="480" height="270" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<rect x="72" y="60" width="16" height="270" fill="#e5484d"/>
<text x="86" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">赤い壁</text>
<rect x="80" y="330" width="480" height="14" fill="#94a3b8"/>
<rect x="80" y="320" width="180" height="10" fill="url(#gi-bleed)" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></rect>
<circle cx="330" cy="72" r="12" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="348" y="78" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光源</text>
<line x1="330" y1="84" x2="420" y2="328" stroke="#e5aa28" stroke-width="3" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.1739;1.0000" values="1;1;0;0"/></line>
<polygon points="420,328 411.36,319.67 421.16,316.06" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;1.0000" values="0;0;1;1"/></polygon>
<rect x="386" y="320" width="68" height="10" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;1.0000" values="0;0;1;1"/></rect>
<line x1="320" y1="82" x2="86" y2="190" stroke="#e5aa28" stroke-width="3" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2435;0.3304;1.0000" values="1;1;0;0"/></line>
<polygon points="86,190 93.62,180.73 98.0,190.21" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="130" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3826;0.4522;1.0000" values="1;1;0;0"/></line>
<polygon points="130,328 121.74,319.29 131.69,316.12" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="210" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4170;0.4174;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4174;0.4870;1.0000" values="1;1;0;0"/></line>
<polygon points="210,328 198.9,323.45 206.66,316.47" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="290" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4522;0.5217;1.0000" values="1;1;0;0"/></line>
<polygon points="290,328 278.13,326.27 283.97,317.62" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></polygon>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">光源から出た光<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① 床に当たる（直接光）→ 明るくなる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2431;0.2435;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② 赤い壁に当たる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">③ 壁は赤い光だけを反射して、四方に跳ね返す<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;0.5214;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">④ 壁の近くの床が赤っぽくなる（色のにじみ）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="80" y="384" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">間接光は、直接光が当たった面が「次の光源」になる。リアルタイムでは、プローブやボクセルで近似する。</text>
<text x="590" y="90" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">光の跳ね返り</text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">0 回<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">1 回（直接）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2431;0.2435;1.0000" values="0;0;1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">1 回（壁へ）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">2 回（壁 → 床）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:gi-color-bleeding:end -->

## 軸 1: いつ計算するか {#when}

1 つ目の軸は光を計算する時点です。

**事前（ベイク）**はオフラインで時間をかけて計算し、結果を保存します。ライトマップとベイク済みのプローブがここに入ります。実行時は保存した値を読むだけなので、最も軽く品質も最も高くできます。その代わり光も物も固定です。扉を開けても太陽が動いても焼いた結果は変わりません。

**光だけ動的**は形（ジオメトリ）は静的なまま光だけを実行時に更新する方式です。ベイク済みのプローブを昼夜に合わせて再ライティングするものや DDGI のようにプローブへ毎フレーム少しずつ光を書き込むものが入ります。太陽の移動、ライトのオン・オフには追従できますが、壁が動いたときは追従できません。

**全部動的**は形も光も動いてよい方式で、毎フレーム計算します。SSGI、ボクセル GI、レイトレ GI が入ります。自由度は最も高くコストも最も大きくなります。

どの段階を選ぶかはゲームの動きで決まります。時間帯が変わらない屋内の道行きなら事前で足ります。オープンワールドで昼夜が変わるなら少なくとも光は動的でなければなりません。壁が壊れる扉が動いて光が漏れる、といった動きがあるなら形も動的にする必要があります。

## 軸 2: どこに持つか {#where}

2 つ目の軸は光の情報の置き場所です。置き場所が決まると**その手法が見える範囲**と**読み出しのコスト**が決まります。5 種類を同じ形の関数で書いてみます。入力はどれも受け取る側の面の情報です。

```hlsl
```hlsl
// 間接光を「どこに情報を持つか」で分けた 4 つの引き方。どれも「受け取る面の情報 → 間接光の色」という同じ形にしてある。
//   ① 面     : ライトマップ（焼いた。UV が要る）
//   ② 空間の点: プローブ格子（Ambient Cube を 8 点から三線形補間）
//   ③ 画面   : 画面空間（深度と色のバッファだけを使う）
//   ④ ボクセル: 3D テクスチャのミップをコーンで引く
// 最後に焼いた光（静的）と画面空間（動的）を画面空間がどれだけ取れたか（信頼度）で混ぜる。
// 座標系は左手系・Y-up、行ベクトル（v * M）。式の骨組みはこのページが説明のために書いたもの（資料のコードではない）。

SamplerState g_linear_clamp : register(s0);

// 受け取る側の面。どの引き方でもこれを入力にする。
struct Surface {
  float3 position;     // ワールド座標 [m]
  float3 normal;       // 単位法線
  float2 lightmap_uv;  // UV2（焼いた物だけ。動く物は無効）
  float2 screen_uv;    // 画面の UV（0〜1）
  uint2 pixel;         // 画素の座標（ノイズの種に使う）
};
```
```

`Surface` にすべての引き方が必要とする情報をまとめています。ライトマップは `lightmap_uv` だけを使い画面空間は `pixel` と `position`、`normal` を使いプローブは `position` と `normal` を使います。**入力に何が要るかでその手法が使える物が決まります。** たとえば動く物は `lightmap_uv` を持たないので、ライトマップを引けません。

<svg class="fig flow" viewBox="0 0 640 294" role="img" aria-label="2 軸で並べた GI の手法"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">手法の位置(横: いつ計算するか、縦: どこに持つか)</text><text x="185.0" y="46" text-anchor="middle" font-size="12" fill="currentColor">事前(ベイク)</text><text x="355.0" y="46" text-anchor="middle" font-size="12" fill="currentColor">光だけ動的</text><text x="525.0" y="46" text-anchor="middle" font-size="12" fill="currentColor">全部動的</text><text x="92" y="85.0" text-anchor="end" font-size="12" fill="currentColor">面(UV)</text><line x1="100" y1="54.0" x2="610" y2="54.0" stroke="#94a3b8" stroke-opacity="0.4"/><text x="92" y="131.0" text-anchor="end" font-size="12" fill="currentColor">空間の点</text><line x1="100" y1="100.0" x2="610" y2="100.0" stroke="#94a3b8" stroke-opacity="0.4"/><text x="92" y="177.0" text-anchor="end" font-size="12" fill="currentColor">画面</text><line x1="100" y1="146.0" x2="610" y2="146.0" stroke="#94a3b8" stroke-opacity="0.4"/><text x="92" y="223.0" text-anchor="end" font-size="12" fill="currentColor">ボクセル</text><line x1="100" y1="192.0" x2="610" y2="192.0" stroke="#94a3b8" stroke-opacity="0.4"/><text x="92" y="269.0" text-anchor="end" font-size="12" fill="currentColor">レイ</text><line x1="100" y1="238.0" x2="610" y2="238.0" stroke="#94a3b8" stroke-opacity="0.4"/><rect x="108" y="60" width="154" height="34" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="185.0" y="81.0" text-anchor="middle" font-size="11" fill="currentColor">ライトマップ</text><rect x="108" y="106" width="154" height="34" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="185.0" y="127.0" text-anchor="middle" font-size="11" fill="currentColor">ベイク済みプローブ</text><rect x="278" y="106" width="154" height="34" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="355.0" y="127.0" text-anchor="middle" font-size="11" fill="currentColor">プローブの再ライティング / DDGI</text><rect x="448" y="152" width="154" height="34" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="525.0" y="173.0" text-anchor="middle" font-size="11" fill="currentColor">SSGI</text><rect x="448" y="198" width="154" height="34" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="525.0" y="219.0" text-anchor="middle" font-size="11" fill="currentColor">ボクセル GI</text><rect x="448" y="244" width="154" height="34" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="525.0" y="265.0" text-anchor="middle" font-size="11" fill="currentColor">レイトレ GI / ReSTIR</text></svg>

### 面: ライトマップ {#surface}

光の情報を物の表面の UV 上に持つ方法です。

```hlsl
```hlsl
// ================= ① 面: ライトマップ =================

Texture2D<float4> g_lightmap : register(t0);

float3 IndirectFromLightmap(Surface s) {
  // 面ごとに UV を持つので、1 回の読み込みで済む。動く物は UV2 を持たないので、この関数は使えない。
  return g_lightmap.SampleLevel(g_linear_clamp, s.lightmap_uv, 0).rgb;
}
```
```

読み込みは 1 回だけです。この軽さがライトマップの強みです。弱みは UV を持つ静的な面にしか使えないこと光や形が動いても変わらないことです。**動く物にライトマップを引こうとすると、UV がないので引けません。** 動く物には別の方法（次のプローブ）が要ります。詳しくは [Lightmaps](../lightmaps/index.md) を見てください。

### 空間の点: プローブ {#probe}

3D 空間の格子点にその場所に届く光を持つ方法です。ここでは、各点が Ambient Cube（上下左右前後の 6 方向の色）を持つとします。

```hlsl
```hlsl
// ================= ② 空間の点: プローブ格子 =================

Texture3D<float4> g_probe_cube : register(t1);   // 幅 = 格子の x 数 × 6。x*6 + 面 の位置に面ごとの色を持つ
cbuffer ProbeCB : register(b0) {
  float3 g_grid_origin;   // 格子の最小の角 [m]
  float g_grid_spacing;   // プローブの間隔 [m]
  int3 g_grid_size;       // 各軸のプローブ数
  int g_pad0;
};

// 1 つのプローブの 1 つの面（0 = +X, 1 = -X, 2 = +Y, 3 = -Y, 4 = +Z, 5 = -Z）の色。
float3 LoadProbeFace(int3 c, int face) {
  c = clamp(c, 0, g_grid_size - 1);                              // 格子の外は端のプローブで代用
  return g_probe_cube.Load(int4(c.x * 6 + face, c.y, c.z, 0)).rgb;
}

// 1 つのプローブの Ambient Cube を法線で評価する（法線の各成分の二乗を重みにする）。
float3 EvalAmbientCube(int3 c, float3 n) {
  float3 w = n * n;                                              // 重みの合計は 1
  return w.x * LoadProbeFace(c, n.x >= 0 ? 0 : 1)
       + w.y * LoadProbeFace(c, n.y >= 0 ? 2 : 3)
       + w.z * LoadProbeFace(c, n.z >= 0 ? 4 : 5);
}

float3 IndirectFromProbes(Surface s) {
  float3 g = (s.position - g_grid_origin) / g_grid_spacing;      // 格子座標（小数）
  int3 c0 = (int3)floor(g);                                      // 手前の角のプローブ
  float3 f = g - c0;                                             // 角の間での位置（0〜1）
  float3 sum = 0;
  [unroll] for (int i = 0; i < 8; ++i) {                         // 8 つの角を三線形補間
    int3 o = int3(i & 1, (i >> 1) & 1, (i >> 2) & 1);
    float3 w3 = lerp(1.0 - f, f, (float3)o);                     // 角ごとの軸別の重み
    sum += w3.x * w3.y * w3.z * EvalAmbientCube(c0 + o, s.normal);
  }
  return sum;
}
```
```

`LoadProbeFace` は格子の外を端のプローブで代用します（`clamp`）。`EvalAmbientCube` は法線の各成分の二乗を重みにして、6 面のうち法線に近い 3 面の色を混ぜます。重みの合計は法線が単位ベクトルなら 1 です。`IndirectFromProbes` は受け取る点を囲む 8 つのプローブを三線形補間します。1 画素あたり 8 プローブ × 3 面で、24 回の読み込みです。

メモリの見積もりも出しておきます。10 × 3 × 10 m の部屋を 1 m 間隔で区切ると、プローブは 11 × 4 × 11 = 484 個です。1 面 1 テクセル 8 バイト（RGBA16F）なら 484 × 6 × 8 = 23,232 バイト（約 23 KB）です。ライトマップに比べると非常に小さい量で済みます。

弱みはプローブの間隔より細かい変化が、取れないことです。壁の両側に別々の明るさがあるのに、プローブが壁をまたいでしまうと**光漏れ**が出ます。プローブは法線の方向を 6 方向の 2 次の重みでしか表せないので、鋭い方向性（窓から差し込む細い光）も苦手です。精度の比較は [Spherical Harmonics (SH)](spherical-harmonics.md) と [Probes](../probes/index.md) を見てください。

### 画面: 深度と色だけ {#screen}

画面に映っている画素の深度と色だけを使う方法です。新しい情報を作らずすでに画面に描かれた物を光源として読み直します。

```hlsl
```hlsl
// ================= ③ 画面: 深度と色だけ =================

Texture2D<float> g_linear_depth : register(t2);   // 視線方向の距離（ビュー空間の z）[m]
Texture2D<float4> g_scene_color : register(t3);   // 直前のフレームの、照明済みの色（光源として読む）
cbuffer ScreenCB : register(b1) {
  float4x4 g_view_proj;   // 行ベクトル用（v * M）
  float2 g_screen_size;   // 画素数
  float g_max_distance;   // 1 本のレイが進む最大の距離 [m]
  uint g_frame;           // フレーム番号（ノイズを変える）
};

// 画素と番号から 0〜1 の乱数を 2 つ作る（足した処理。PCG ハッシュ）。
float2 Random2(uint2 pixel, uint index) {
  uint h = pixel.x * 1973u + pixel.y * 9277u + index * 26699u + g_frame * 747796405u;
  h = (h ^ (h >> 16)) * 2246822519u;
  h = (h ^ (h >> 13)) * 3266489917u;
  h ^= h >> 16;
  uint h2 = h * 747796405u + 2891336453u;
  h2 = ((h2 >> ((h2 >> 28) + 4u)) ^ h2) * 277803737u;
  return float2(h & 0xFFFFu, h2 & 0xFFFFu) / 65535.0;
}

// 余弦重みの半球方向（n の側）。
float3 CosineDirection(float3 n, float2 xi) {
  float r = sqrt(xi.x), phi = 6.2831853 * xi.y;
  float3 t = abs(n.y) < 0.9 ? normalize(cross(n, float3(0, 1, 0))) : normalize(cross(n, float3(1, 0, 0)));
  float3 b = cross(n, t);
  return t * (r * cos(phi)) + b * (r * sin(phi)) + n * sqrt(max(0.0, 1.0 - xi.x));
}

// 画面空間で数本のレイを追う。当たった画素の色を集め当たった割合を confidence（0〜1）で返す。
// 当たらなかった方向（画面の外へ出たまたは深度の裏へ抜けた）の光は、取れていない。
float3 IndirectFromScreen(Surface s, out float confidence) {
  const int kRays = 8, kSteps = 12;
  float3 sum = 0;
  int hits = 0;
  for (int r = 0; r < kRays; ++r) {
    float3 dir = CosineDirection(s.normal, Random2(s.pixel, r));
    float step_len = g_max_distance / kSteps;
    float t = step_len * (0.5 + Random2(s.pixel, r + 100u).x);   // 最初の位置をずらして、段差を目立たなくする
    [loop] for (int k = 0; k < kSteps; ++k, t += step_len) {
      float3 p = s.position + dir * t;
      float4 clip = mul(float4(p, 1.0), g_view_proj);
      if (clip.w <= 0.0) break;                                  // カメラの背後
      float2 uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
      if (any(uv < 0.0) || any(uv > 1.0)) break;                 // 画面の外 → この方向は取れない
      float scene_z = g_linear_depth.SampleLevel(g_linear_clamp, uv, 0);
      if (clip.w > scene_z && clip.w < scene_z + step_len * 2.0) {   // 面の裏に入り、かつ厚みの範囲内 → 当たり
        sum += g_scene_color.SampleLevel(g_linear_clamp, uv, 0).rgb;
        ++hits;
        break;
      }
    }
  }
  confidence = (float)hits / kRays;                              // 0 なら、画面空間は何も取れていない
  return hits > 0 ? sum / hits : 0.0;
}
```
```

`Random2` は画素の座標とフレーム番号から、0〜1 の乱数を 2 つ作ります（足した処理）。`CosineDirection` は法線の側の半球で余弦に比例して方向を選びます。`IndirectFromScreen` は画素ごとに 8 本のレイを最大 12 歩進めます。1 歩ごとにレイの位置を画面に投影して、その画素の深度と比べます。**レイが画面の外に出たらその方向の光は取れません**（`break`）。深度の「裏」に入りかつ厚みの範囲内なら当たりで、その画素の色を光として足します。

最後の `confidence` は 8 本のうち何本が当たったかの割合です。0 ならこの画素では画面空間が何も取れていません。**この値を返すことが画面空間を他の手法と組み合わせる要です。** 取れなかった分を別の手法で補うための目印になります。

コストは画面の解像度に比例します。1920 × 1080（2,073,600 画素）で、1 画素あたり 8 本 × 12 歩なら最大 96 回の深度の読み込みです。全体で最大約 1.99 億回になります。画面の複雑さには影響されません。

### ボクセル: 3D の格子にシーンの光と形を持つ {#voxel}

シーンをボクセルにして各ボクセルに放射輝度と不透明度を持つ方法です。ミップを作っておけば遠くを粗く、近くを細かく読めます。

```hlsl
```hlsl
// ================= ④ ボクセル: コーンで引く =================

Texture3D<float4> g_voxel_radiance : register(t4);   // ボクセル化したシーンの放射輝度（rgb）と不透明度（a）。ミップつき
cbuffer VoxelCB : register(b2) {
  float3 g_voxel_origin;  // ボクセル範囲の最小の角 [m]
  float g_voxel_size;     // ミップ 0 の 1 ボクセルの大きさ [m]
  float g_voxel_count;    // 1 辺のボクセル数
  float3 g_pad1;
};

float3 IndirectFromVoxelCone(Surface s, float3 dir, float aperture_tan) {
  float3 sum = 0;
  float alpha = 0;
  float dist = g_voxel_size * 2.0;                               // 自分のボクセルを避ける最初の距離
  [loop] for (int i = 0; i < 16 && alpha < 0.95; ++i) {
    float diameter = max(g_voxel_size, 2.0 * aperture_tan * dist);   // その距離でのコーンの太さ [m]
    float mip = log2(diameter / g_voxel_size);                   // 太さに合うミップ
    float3 uvw = (s.position + dir * dist - g_voxel_origin) / (g_voxel_size * g_voxel_count);
    if (any(uvw < 0.0) || any(uvw > 1.0)) break;                 // ボクセル範囲の外
    float4 v = g_voxel_radiance.SampleLevel(g_linear_clamp, uvw, mip);
    sum += (1.0 - alpha) * v.rgb * v.a;                          // 手前から奥へ、前の不透明度を引いて足す
    alpha += (1.0 - alpha) * v.a;
    dist += diameter * 0.5;                                      // 太さの半分ずつ進む
  }
  return sum;
}
```
```

コーンは進むほど太くなります。距離 `dist` での太さは `2 · tan(開き角) · dist` で、この太さに合うミップを `log2(太さ / ボクセルの大きさ)` で選びます。開き角の `tan` に 0.577 を渡すと半角 30° の円錐（全角 60°）です。手前から奥へ `(1 - alpha) * v.rgb * v.a` の形で足すのは、手前のボクセルが不透明ならその奥が見えない、という重なりの扱いです。

弱みはボクセル化の範囲と大きさに限界があることです。ボクセルの大きさより細かい形は表せません。カメラの近くだけを細かくするなど範囲を何段か重ねる工夫が要ります。詳しくは [Voxel GI](../voxel-gi.md) を見てください。

### レイ: 保存せずその場で調べる {#ray}

光を保存せずに受け取る点から光線を飛ばして、シーンの形（BVH など）を直接調べる方法です。ハードウェアのレイトレーシング（DXR）が前提になります。画面の外の物もプローブの間隔より細かい形も正確に扱えます。その代わり 1 画素あたりのレイの数が少ないため、結果にノイズが乗ります。ノイズを減らす仕組み（時間方向の再利用、デノイズ）が一緒に要ります。このページでは HLSL を書きません。詳しくは [RT GI](../rt-gi/index.md) と [ReSTIR](../restir.md) を見てください。

## 画面空間はどれだけの光を取れるか {#coverage}

「画面の外の光は取れない」と言われても、どれだけ取れないのかは数字で見ないと分かりません。そこで、空っぽの部屋で光がどこから来るかを数えてみます。

部屋は 10 × 3 × 10 m の箱で、カメラは (5, 1.6, 1)、+z 向きです。画面の縦横比は 16:9 で、near plane は 0.1 m です。床と壁、天井の点を面積に比例して選びその点から余弦重みの方向へレイを飛ばします。最初に当たった壁の点がカメラの視錐台の中にあれば、その光は「画面空間で取れる」光です。この実験は 1 回の反射だけを数え物による遮蔽は考えません。

```cpp
```cpp
﻿// 画面空間の GI が「見える」割合を数える実験。
// 箱形の部屋の中で床や壁の点から余弦重みの半球方向へレイを飛ばし
// 最初に当たった壁の点がカメラの視錐台の中にあるかを数える。視錐台の外に当たった光は画面空間の手法では取れない。
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <random>

struct V3 { double x, y, z; };
static V3 operator+(V3 a, V3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
static V3 operator-(V3 a, V3 b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
static V3 operator*(V3 a, double s) { return {a.x * s, a.y * s, a.z * s}; }
static double Dot(V3 a, V3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static V3 Norm(V3 a) { double l = std::sqrt(Dot(a, a)); return {a.x / l, a.y / l, a.z / l}; }
static V3 Cross(V3 a, V3 b) { return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x}; }
constexpr double kPi = 3.14159265358979323846;

// 部屋: x は [0, 10] m、z は [0, 10] m、y（高さ）は [0, 3] m。空っぽの箱で内側の 6 面が壁。
const V3 kMin{0, 0, 0}, kMax{10, 3, 10};

// 箱の内側から出たレイが、最初に当たる点を返す（スラブ法）。
static V3 HitRoom(V3 o, V3 d) {
  double t = 1e30;
  const double lo[3] = {kMin.x, kMin.y, kMin.z}, hi[3] = {kMax.x, kMax.y, kMax.z};
  const double po[3] = {o.x, o.y, o.z}, pd[3] = {d.x, d.y, d.z};
  for (int a = 0; a < 3; ++a) {
    if (pd[a] > 1e-12) t = std::min(t, (hi[a] - po[a]) / pd[a]);          // 正の向きの壁
    else if (pd[a] < -1e-12) t = std::min(t, (lo[a] - po[a]) / pd[a]);    // 負の向きの壁
  }
  return o + d * t;
}

// カメラ: 位置 eye、前向き fwd、水平画角 fov_h。画面の縦横比は 16:9。
// 点 p が視錐台の中なら true（部屋は空っぽなので、遮蔽は考えない）。
struct Camera {
  V3 eye, fwd, right, up;
  double tan_h, tan_v;
  Camera(V3 e, double yaw_deg, double fov_h_deg) {
    eye = e;
    double yaw = yaw_deg * kPi / 180;
    fwd = {std::sin(yaw), 0, std::cos(yaw)};                 // 水平に向く
    right = Norm(Cross({0, 1, 0}, fwd));
    up = Cross(fwd, right);
    tan_h = std::tan(fov_h_deg * kPi / 360);
    tan_v = tan_h * 9.0 / 16.0;                              // 16:9
  }
  bool Sees(V3 p) const {
    V3 v = p - eye;
    double z = Dot(v, fwd);
    if (z <= 0.1) return false;                              // 背後と near plane（0.1 m）の手前
    return std::fabs(Dot(v, right)) <= z * tan_h && std::fabs(Dot(v, up)) <= z * tan_v;
  }
};

// 余弦重みの半球方向（法線 n の側）。
static V3 CosineHemisphere(V3 n, std::mt19937& rng) {
  std::uniform_real_distribution<double> u(0, 1);
  double r = std::sqrt(u(rng)), phi = 2 * kPi * u(rng);
  double x = r * std::cos(phi), y = r * std::sin(phi), z = std::sqrt(std::max(0.0, 1 - r * r));
  V3 t = std::fabs(n.y) < 0.9 ? Norm(Cross(n, {0, 1, 0})) : Norm(Cross(n, {1, 0, 0}));
  V3 b = Cross(n, t);
  return t * x + b * y + n * z;
}

// 部屋の面の上のランダムな点とその法線（内向き）。面積に比例して選ぶ。
static void RandomSurface(std::mt19937& rng, V3& p, V3& n) {
  std::uniform_real_distribution<double> u(0, 1);
  double ax = 10 * 3, az = 10 * 3, ay = 10 * 10;             // 面積 [m²]: 壁 x 向き、壁 z 向き床と天井
  double total = 2 * (ax + az + ay), r = u(rng) * total;
  if (r < ax) { p = {0, u(rng) * 3, u(rng) * 10}; n = {1, 0, 0}; }
  else if (r < 2 * ax) { p = {10, u(rng) * 3, u(rng) * 10}; n = {-1, 0, 0}; }
  else if (r < 2 * ax + az) { p = {u(rng) * 10, u(rng) * 3, 0}; n = {0, 0, 1}; }
  else if (r < 2 * ax + 2 * az) { p = {u(rng) * 10, u(rng) * 3, 10}; n = {0, 0, -1}; }
  else if (r < 2 * ax + 2 * az + ay) { p = {u(rng) * 10, 0, u(rng) * 10}; n = {0, 1, 0}; }
  else { p = {u(rng) * 10, 3, u(rng) * 10}; n = {0, -1, 0}; }
}

int main() {
  std::mt19937 rng(12345);
  std::printf("room 10 x 3 x 10 m, camera at (5, 1.6, 1) looking +z, empty room\n");
  std::printf("fraction of indirect light (cosine-weighted, 1 bounce) that comes from inside the view frustum\n\n");
  std::printf("%-10s %-22s %-22s\n", "fov_h", "receiver: any surface", "receiver: visible only");
  for (double fov : {60.0, 90.0, 120.0}) {
    Camera cam({5, 1.6, 1}, 0, fov);
    long hit_any = 0, tot_any = 0, hit_vis = 0, tot_vis = 0;
    for (int i = 0; i < 400000; ++i) {
      V3 p, n;
      RandomSurface(rng, p, n);
      V3 d = CosineHemisphere(n, rng);
      V3 q = HitRoom(p + n * 1e-4, d);                       // 光の来る先（壁の点）
      bool seen = cam.Sees(q);
      ++tot_any; hit_any += seen;
      if (cam.Sees(p)) {                                     // 受け取る側も画面に映っている点だけ
        ++tot_vis; hit_vis += seen;
      }
    }
    std::printf("%-10.0f %-22.1f %-22.1f\n", fov, 100.0 * hit_any / tot_any, 100.0 * hit_vis / tot_vis);
  }

  // 同じ部屋でカメラが壁際を向いたとき（部屋の隅に近づく）
  std::printf("\ncamera looking at a wall from 1 m (position (5,1.6,9), looking +z), fov 90\n");
  {
    Camera cam({5, 1.6, 9}, 0, 90);
    long hit = 0, tot = 0;
    for (int i = 0; i < 400000; ++i) {
      V3 p, n;
      RandomSurface(rng, p, n);
      if (!cam.Sees(p)) continue;
      V3 q = HitRoom(p + n * 1e-4, CosineHemisphere(n, rng));
      ++tot; hit += cam.Sees(q);
    }
    std::printf("visible receivers only: %.2f %%\n", 100.0 * hit / tot);
  }
  return 0;
}
```
```

```text title="実行結果"
room 10 x 3 x 10 m, camera at (5, 1.6, 1) looking +z, empty room
fraction of indirect light (cosine-weighted, 1 bounce) that comes from inside the view frustum

fov_h      receiver: any surface  receiver: visible only
60         31.4                   61.6                  
90         53.1                   80.3                  
120        65.5                   85.1                  

camera looking at a wall from 1 m (position (5,1.6,9), looking +z), fov 90
visible receivers only: 0.00 %
```

<svg class="fig flow" viewBox="0 0 640 232" role="img" aria-label="視錐台の中から来る光の割合"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">視錐台の中から来る光の割合(%)(青: 全部の面が受け取る側、黄: 画面に映る点だけ)</text><line x1="60" y1="200" x2="580" y2="200" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="200" stroke="#94a3b8"/><text x="54" y="204.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="124.0" text-anchor="end" font-size="10" fill="currentColor">50</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">100</text><rect x="100" y="149.8" width="50" height="50.2" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="125" y="145.76" text-anchor="middle" font-size="10" fill="currentColor">31.4</text><rect x="154" y="101.4" width="50" height="98.6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="179" y="97.44" text-anchor="middle" font-size="10" fill="currentColor">61.6</text><text x="152" y="216" text-anchor="middle" font-size="11" fill="currentColor">水平画角 60°</text><rect x="265" y="115.0" width="50" height="85.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="290" y="111.03999999999999" text-anchor="middle" font-size="10" fill="currentColor">53.1</text><rect x="319" y="71.5" width="50" height="128.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="344" y="67.52000000000001" text-anchor="middle" font-size="10" fill="currentColor">80.3</text><text x="317" y="216" text-anchor="middle" font-size="11" fill="currentColor">水平画角 90°</text><rect x="430" y="95.2" width="50" height="104.8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="455" y="91.19999999999999" text-anchor="middle" font-size="10" fill="currentColor">65.5</text><rect x="484" y="63.8" width="50" height="136.2" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="509" y="59.84" text-anchor="middle" font-size="10" fill="currentColor">85.1</text><text x="482" y="216" text-anchor="middle" font-size="11" fill="currentColor">水平画角 120°</text></svg>

結果を読みます。水平画角 60° では光の 31.4 % しか視錐台の中から来ません。90° でも 53.1 %、120° まで広げて 65.5 % です。つまり、**画角を広げても光の 3 分の 1 以上は、画面の外から来ます。** 受け取る側も画面に映っている点だけに絞ると、60° で 61.6 %、90° で 80.3 %、120° で 85.1 % と上がります。画面に映っている点どうしなら互いに光を渡せる範囲が広いためです。

<svg class="fig flow" viewBox="0 0 640 430" role="img" aria-label="部屋を上から見た図"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">部屋を上から見た図(水平画角 90° のカメラが (5, 1) から +z を向く)</text><rect x="40" y="36" width="380" height="380" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><polygon points="230,378 40,188 40,36 420,36 420,188" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="1.5"/><circle cx="230" cy="378" r="5" fill="#e5aa28"/><text x="240" y="382" text-anchor="start" font-size="11" fill="currentColor">カメラ</text><text x="230" y="112" text-anchor="middle" font-size="12" fill="currentColor">視錐台の中(取れる)</text><text x="230" y="404.8" text-anchor="middle" font-size="11" fill="currentColor">背後(取れない)</text><text x="51.4" y="302" text-anchor="start" font-size="11" fill="currentColor">横</text><text x="408.59999999999997" y="302" text-anchor="end" font-size="11" fill="currentColor">横</text><text x="444" y="50" text-anchor="start" font-size="11" fill="currentColor">壁際: 同じ画角でも</text><text x="444" y="66" text-anchor="start" font-size="11" fill="currentColor">壁だけが映ると 0 %</text></svg>

最後の 0.00 % はカメラが壁の 1 m 手前に立って、壁だけを映している場合です。映っているのは平らな 1 枚の壁だけで、平らな面どうしは光を渡し合えません。レイは壁から離れる向きにしか出ないので、視錐台の中の点には 1 つも当たりません。結果はちょうど 0 です。**壁際に立つと画面空間 GI は何も取れません。** このとき `confidence` が 0 になるので、焼いた光に完全に切り替わります。

この数字はこの部屋とカメラの一例です。物が置かれると遮蔽によって画面内から来る光は、数字より減る方向に動きます。実際のゲームの値は場面ごとに測る必要があります。

## 組み合わせる {#combine}

1 つの手法で全部まかなうのは難しいので、複数を組み合わせます。基本の形は焼いた光を土台にして、画面空間が取れた分を重ねることです。

```hlsl
```hlsl
// ================= 組み合わせ =================

// 一例: 焼いた光（静的な背景はライトマップ、動く物はプローブ）に画面空間が取れた分を重ねる。
float3 CombineIndirect(Surface s, bool is_static) {
  float3 base = is_static ? IndirectFromLightmap(s) : IndirectFromProbes(s);
  float confidence;
  float3 screen = IndirectFromScreen(s, confidence);
  // 画面空間が取れた割合だけ置き換える。足し算にすると焼いた光と画面空間が同じ光を二重に数える。
  return lerp(base, screen, confidence * 0.5);                   // 0.5 は一例（画面空間の色を信用しすぎない）
}

float4 TaxonomyPS(float4 pos : SV_Position, float3 world_pos : TEXCOORD0, float3 normal : NORMAL,
                  float2 lightmap_uv : TEXCOORD1, float2 albedo_uv : TEXCOORD2, uint is_static : TEXCOORD3) : SV_Target {
  Surface s;
  s.position = world_pos;
  s.normal = normalize(normal);
  s.lightmap_uv = lightmap_uv;
  s.screen_uv = pos.xy / g_screen_size;
  s.pixel = (uint2)pos.xy;
  float3 gi = CombineIndirect(s, is_static != 0);
  float3 cone = IndirectFromVoxelCone(s, s.normal, 0.577);       // 比較用: 法線方向への 1 本のコーン
  return float4(gi + cone * 0.0, 1.0);
}
```
```

`CombineIndirect` は静的な背景ならライトマップ、動く物ならプローブを土台にします。そこへ画面空間の結果を `confidence` に応じて重ねます。**足し算にしない**ことが要点です。焼いた光はすでに部屋全体の間接光を含んでいます。画面空間を足すと同じ光を二重に数えます。`lerp` で置き換えれば画面空間が取れた割合だけ焼いた光を差し替える形になります。`0.5` は一例で画面空間の色（前フレームの照明済みの画像）を信用しすぎないための上限です。

この考え方の延長に Lumen のような製品があります。近くは画面空間で正確に遠くは距離場やキャッシュで近似する、という階層になっています。内部の仕組みは [Lumen and Nanite](../lumen.md) を見てください。ここでは、Lumen の発表は読んでいないので、構成の説明にとどめます。

## どう選ぶか {#choose}

選ぶ順番は軸 1 から決めると整理できます。

1. 光も物も動かないか。動かないならライトマップで足ります。動く物のためにライト プローブを併用します。
2. 光が動くか。動くならプローブの再ライティングや DDGI のような光だけ動的な方式が候補です。
3. 形も動くか。動くなら全部動的な方式（SSGI、ボクセル、レイトレ）が要ります。レイトレーシングが使える GPU なら DDGI や ReSTIR GI も選べます。使えないならボクセル GI かプローブの動的更新です。
4. 予算が最優先なら半球ライトか SH のプローブで十分かを疑います。GI を使わない選択もあります。

どの手法も画面の外と画面の中、静的と動的のどちらかで弱点を持ちます。弱点を別の手法で補う形が基本です。組み合わせの具体的な例と方式ごとのコストの比較は [GI Comparison](../comparison.md) にあります。

## よくあるミス {#mistakes}

??? failure "動く物にライトマップを引いて、真っ黒になる"
    動く物は `lightmap_uv` を持たない。読み込みが 0 になり黒く出る。動く物にはプローブを使う。

??? failure "画面空間 GI だけにして、画面の端で光が消える"
    画面空間は画面の外の光を取れない。壁際や画面の端で急に暗くなる。取れなかった方向は `confidence` を使って、プローブなどに切り替える。

??? failure "焼いた光に画面空間 GI を足して、二重に明るくなる"
    ライトマップはすでに間接光を含んでいる。足し算ではなく置き換え（`lerp`）にする。

??? failure "プローブが壁をまたいで、光漏れが出る"
    プローブの間隔が壁の厚みより大きく、壁の両側が同じプローブから補間されている。プローブを壁の両側に置くか遮蔽を考えた重みづけを足す。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 手法は軸 1（いつ計算するか）と軸 2（どこに持つか）で決まる。
    - [x] 動く物と動く光に対応できるかは軸 1、画面の外の光が取れるかは軸 2 で決まる。
    - [x] 画面空間は空っぽの部屋の例で、光の半分近くを取り逃がす。壁際では 0 になる。
    - [x] 組み合わせでは足さずに取れた割合で置き換える。
    - [x] どの手法にも弱点があるので、補い合う形にする。

## 参考 {#references}

- Ravi Ramamoorthi, Pat Hanrahan, "An Efficient Representation for Irradiance Environment Maps", Proceedings of SIGGRAPH 2001, pp. 497–500, 2001. 全 4 ページを読んだ。
- James T. Kajiya, "The Rendering Equation", Proceedings of SIGGRAPH 1986, pp. 143–150. 読んでいない。レンダリング方程式の出典として挙げる。
- Tomasz Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018. 読んでいない。大域照明の章の存在を示すために挙げる。
- Daniel Wright, Krzysztof Narkowicz, Patrick Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games. 読んでいない。
- このページの HLSL と C++ の実験（視錐台の中から来る光の割合）は、説明のために書いたもので出典はない。数字はその部屋とカメラの一例。

## 関連ページ {#related}

- [GI Theory](index.md)
- [GI Comparison](../comparison.md)
- [Lightmaps](../lightmaps/index.md)
- [Voxel GI](../voxel-gi.md)
- [Lumen and Nanite](../lumen.md)
- [ReSTIR](../restir.md)
