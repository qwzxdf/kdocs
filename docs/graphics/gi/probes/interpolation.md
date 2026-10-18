---
title: Interpolation Methods
tags:
  - 描画
---

# Interpolation Methods

<strong>物体の位置は、プローブとプローブの間にあるので、周囲のプローブから補間して、値を求めます</strong>。<strong>単純な 3 線形補間だと、壁の向こうのプローブの光が漏れる</strong>ので、可視性を考慮する方式があります。このページでは、補間の方式と、光漏れの対策を説明します。

!!! tip "ポイント"
    - 3 線形補間 ＝ 周囲の 8 プローブを、距離で重み付け。
    - 壁の向こうのプローブも混ざると、光が漏れる。
    - 可視性（そのプローブから見えるか）で、重みを減らす。
    - DDGI は、深度情報で可視性を判定する（[DDGI](../ddgi.md)）。

## 補間の方式
### 四面体分割（Delaunay）

<strong>プローブを不規則に置いて</strong>、<strong>その点群を四面体に分割</strong>します。物体がどの四面体の中にいるかを調べ、その 4 つの頂点のプローブを、重心座標の重みで補間します。

四面体分割の利点は、プローブを自由に配置でき、重要な場所は密に、他は疎に置けることです。欠点は、物体ごとに（CPU で）四面体を検索する必要があること、そして四面体が壁を貫通して光が漏れることがあることです。Unity の Light Probe Group が、この方式です。

<!-- fig:probe-bilinear:begin -->

<svg class="fig illust motion" data-fig="probe-bilinear" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-probe-bilinear" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">プローブの補間: 壁を挟むと、普通の補間では光が漏れる(可視性で重みを直す)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">壁の左は明るい部屋、右は暗い部屋。プローブ 5 個の明るさから、間の明るさを補間する。実際の明るさ(正解)と比べる</text>
<rect x="30" y="92" width="900" height="130" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="82" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 断面(壁の左は明るく、右は暗い。プローブは 5 個)</text>
<rect x="367.5" y="96" width="10" height="122" fill="#475569"/>
<text x="384.5" y="114" text-anchor="start" style="font-size:13px;font-weight:700;fill:#475569">壁</text>
<rect x="36" y="100" width="14" height="114" fill="#e5aa28"/>
<text x="60" y="114" text-anchor="start" style="font-size:12px;font-weight:700;fill:#92400e">窓(光が入る)</text>
<circle cx="50.0" cy="185" r="14" fill="#e5d180" stroke="#334155" stroke-width="2"/>
<text x="50.0" y="213" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.90</text>
<circle cx="265.0" cy="185" r="14" fill="#e5d180" stroke="#334155" stroke-width="2"/>
<text x="265.0" y="213" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.90</text>
<circle cx="480.0" cy="185" r="14" fill="#161d2d" stroke="#334155" stroke-width="2"/>
<text x="480.0" y="213" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.03</text>
<circle cx="695.0" cy="185" r="14" fill="#161d2d" stroke="#334155" stroke-width="2"/>
<text x="695.0" y="213" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.03</text>
<circle cx="910.0" cy="185" r="14" fill="#161d2d" stroke="#334155" stroke-width="2"/>
<text x="910.0" y="213" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.03</text>
<text x="40" y="236" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">プローブの明るさ(丸の色と数字)</text>
<rect x="30" y="262" width="900" height="190" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="252" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">② 横軸の位置での明るさ</text>
<rect x="367.5" y="275.0" width="10" height="150.0" fill="#94a3b8" opacity="0.35"/>
<path d="M50.0,305.0 L71.5,305.0 L93.0,305.0 L114.5,305.0 L136.0,305.0 L157.5,305.0 L179.0,305.0 L200.5,305.0 L222.0,305.0 L243.5,305.0 L265.0,305.0 L286.5,305.0 L308.0,305.0 L329.5,305.0 L351.0,305.0 M394.0,421.0 L415.5,421.0 L437.0,421.0 L458.5,421.0 L480.0,421.0 L501.5,421.0 L523.0,421.0 L544.5,421.0 L566.0,421.0 L587.5,421.0 L609.0,421.0 L630.5,421.0 L652.0,421.0 L673.5,421.0 L695.0,421.0 L716.5,421.0 L738.0,421.0 L759.5,421.0 L781.0,421.0 L802.5,421.0 L824.0,421.0 L845.5,421.0 L867.0,421.0 L888.5,421.0 L910.0,421.0 " fill="none" stroke="#2ea043" stroke-width="3" opacity="1" stroke-dasharray="7 5"/>
<path d="M50.0,305.0 L71.5,305.0 L93.0,305.0 L114.5,305.0 L136.0,305.0 L157.5,305.0 L179.0,305.0 L200.5,305.0 L222.0,305.0 L243.5,305.0 L265.0,305.0 L286.5,316.6 L308.0,328.2 L329.5,339.8 L351.0,351.4 M394.0,374.6 L415.5,386.2 L437.0,397.8 L458.5,409.4 L480.0,421.0 L501.5,421.0 L523.0,421.0 L544.5,421.0 L566.0,421.0 L587.5,421.0 L609.0,421.0 L630.5,421.0 L652.0,421.0 L673.5,421.0 L695.0,421.0 L716.5,421.0 L738.0,421.0 L759.5,421.0 L781.0,421.0 L802.5,421.0 L824.0,421.0 L845.5,421.0 L867.0,421.0 L888.5,421.0 L910.0,421.0 " fill="none" stroke="#e5484d" stroke-width="3.5" opacity="1"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0538;0.0541;1.0000" values="0;0;1;1"/></path>
<path d="M50.0,305.0 L71.5,305.0 L93.0,305.0 L114.5,305.0 L136.0,305.0 L157.5,305.0 L179.0,305.0 L200.5,305.0 L222.0,305.0 L243.5,305.0 L265.0,305.0 L286.5,305.0 L308.0,305.0 L329.5,305.0 L351.0,305.0 M394.0,421.0 L415.5,421.0 L437.0,421.0 L458.5,421.0 L480.0,421.0 L501.5,421.0 L523.0,421.0 L544.5,421.0 L566.0,421.0 L587.5,421.0 L609.0,421.0 L630.5,421.0 L652.0,421.0 L673.5,421.0 L695.0,421.0 L716.5,421.0 L738.0,421.0 L759.5,421.0 L781.0,421.0 L802.5,421.0 L824.0,421.0 L845.5,421.0 L867.0,421.0 L888.5,421.0 L910.0,421.0 " fill="none" stroke="#2563eb" stroke-width="3.5" opacity="1"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3241;0.3243;1.0000" values="0;0;1;1"/></path>
<circle cx="52" cy="440" r="6" fill="#2ea043"/>
<text x="62" y="444" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">正解</text>
<circle cx="100.8" cy="440" r="6" fill="#e5484d"/>
<text x="110.8" y="444" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">普通の補間</text>
<circle cx="183.8" cy="440" r="6" fill="#2563eb"/>
<text x="193.8" y="444" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">可視性つき補間</text>
<circle cx="50.0" cy="185" r="5" fill="#7c3aed"><animate attributeName="cx" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0541;0.0668;0.0796;0.0923;0.1051;0.1178;0.1306;0.1433;0.1561;0.1688;0.1816;0.1943;0.2071;0.2198;0.2326;0.2453;0.2581;0.2708;0.2836;0.2963;0.3091;0.3218;0.3346;0.3473;0.3601;0.3728;0.3856;0.3983;0.4111;0.4238;0.4366;0.4493;0.4621;0.4748;0.4876;0.5003;0.5131;0.5258;0.5386;0.5514;1.0000" values="50;50;71.5;93;114.5;136;157.5;179;200.5;222;243.5;265;286.5;308;329.5;351;394;415.5;437;458.5;480;501.5;523;544.5;566;587.5;609;630.5;652;673.5;695;716.5;738;759.5;781;802.5;824;845.5;867;888.5;910;910"/></circle>
<circle cx="50.0" cy="305.0" r="5" fill="#2ea043"><animate attributeName="cx" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0541;0.0668;0.0796;0.0923;0.1051;0.1178;0.1306;0.1433;0.1561;0.1688;0.1816;0.1943;0.2071;0.2198;0.2326;0.2453;0.2581;0.2708;0.2836;0.2963;0.3091;0.3218;0.3346;0.3473;0.3601;0.3728;0.3856;0.3983;0.4111;0.4238;0.4366;0.4493;0.4621;0.4748;0.4876;0.5003;0.5131;0.5258;0.5386;0.5514;1.0000" values="50;50;71.5;93;114.5;136;157.5;179;200.5;222;243.5;265;286.5;308;329.5;351;394;415.5;437;458.5;480;501.5;523;544.5;566;587.5;609;630.5;652;673.5;695;716.5;738;759.5;781;802.5;824;845.5;867;888.5;910;910"/><animate attributeName="cy" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0541;0.0668;0.0796;0.0923;0.1051;0.1178;0.1306;0.1433;0.1561;0.1688;0.1816;0.1943;0.2071;0.2198;0.2326;0.2453;0.2581;0.2708;0.2836;0.2963;0.3091;0.3218;0.3346;0.3473;0.3601;0.3728;0.3856;0.3983;0.4111;0.4238;0.4366;0.4493;0.4621;0.4748;0.4876;0.5003;0.5131;0.5258;0.5386;0.5514;1.0000" values="305;305;305;305;305;305;305;305;305;305;305;305;305;305;305;305;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421"/></circle>
<circle cx="50.0" cy="305.0" r="5" fill="#e5484d" opacity="0"><animate attributeName="cx" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0541;0.0668;0.0796;0.0923;0.1051;0.1178;0.1306;0.1433;0.1561;0.1688;0.1816;0.1943;0.2071;0.2198;0.2326;0.2453;0.2581;0.2708;0.2836;0.2963;0.3091;0.3218;0.3346;0.3473;0.3601;0.3728;0.3856;0.3983;0.4111;0.4238;0.4366;0.4493;0.4621;0.4748;0.4876;0.5003;0.5131;0.5258;0.5386;0.5514;1.0000" values="50;50;71.5;93;114.5;136;157.5;179;200.5;222;243.5;265;286.5;308;329.5;351;394;415.5;437;458.5;480;501.5;523;544.5;566;587.5;609;630.5;652;673.5;695;716.5;738;759.5;781;802.5;824;845.5;867;888.5;910;910"/><animate attributeName="cy" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0541;0.0668;0.0796;0.0923;0.1051;0.1178;0.1306;0.1433;0.1561;0.1688;0.1816;0.1943;0.2071;0.2198;0.2326;0.2453;0.2581;0.2708;0.2836;0.2963;0.3091;0.3218;0.3346;0.3473;0.3601;0.3728;0.3856;0.3983;0.4111;0.4238;0.4366;0.4493;0.4621;0.4748;0.4876;0.5003;0.5131;0.5258;0.5386;0.5514;1.0000" values="305;305;305;305;305;305;305;305;305;305;305;305;316.6;328.2;339.8;351.4;374.6;386.2;397.8;409.4;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421"/><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0538;0.0541;1.0000" values="0;0;1;1"/></circle>
<circle cx="50.0" cy="305.0" r="5" fill="#2563eb" opacity="0"><animate attributeName="cx" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0541;0.0668;0.0796;0.0923;0.1051;0.1178;0.1306;0.1433;0.1561;0.1688;0.1816;0.1943;0.2071;0.2198;0.2326;0.2453;0.2581;0.2708;0.2836;0.2963;0.3091;0.3218;0.3346;0.3473;0.3601;0.3728;0.3856;0.3983;0.4111;0.4238;0.4366;0.4493;0.4621;0.4748;0.4876;0.5003;0.5131;0.5258;0.5386;0.5514;1.0000" values="50;50;71.5;93;114.5;136;157.5;179;200.5;222;243.5;265;286.5;308;329.5;351;394;415.5;437;458.5;480;501.5;523;544.5;566;587.5;609;630.5;652;673.5;695;716.5;738;759.5;781;802.5;824;845.5;867;888.5;910;910"/><animate attributeName="cy" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0541;0.0668;0.0796;0.0923;0.1051;0.1178;0.1306;0.1433;0.1561;0.1688;0.1816;0.1943;0.2071;0.2198;0.2326;0.2453;0.2581;0.2708;0.2836;0.2963;0.3091;0.3218;0.3346;0.3473;0.3601;0.3728;0.3856;0.3983;0.4111;0.4238;0.4366;0.4493;0.4621;0.4748;0.4876;0.5003;0.5131;0.5258;0.5386;0.5514;1.0000" values="305;305;305;305;305;305;305;305;305;305;305;305;305;305;305;305;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421;421"/><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3241;0.3243;1.0000" values="0;0;1;1"/></circle>
<g opacity="0"><animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5944;0.5946;1.0000" values="0;0;1;1"/><rect x="30" y="468" width="900" height="56" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="492" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">壁のすぐ右(x=12.8): 正解 0.03 / 普通 0.29(光が漏れる)/ 可視性つき 0.03</text>
<text x="46" y="515" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">壁のすぐ左(x=11.2): 正解 0.90 / 普通 0.64(暗く引っ張られる)/ 可視性つき 0.90</text>
</g>
<text x="30" y="536" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">プローブは離れた点にだけ置く。間の明るさは補間で作る<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0538;0.0541;1.0000" values="1;1;0;0"/></text>
<text x="30" y="536" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">普通の補間(赤): 壁の向こうのプローブも混ぜるので、壁際で光が漏れる<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.0538;0.0541;0.3241;0.3243;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="536" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">可視性つき(青): 壁で見えないプローブは、重みを 0 にする<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.3241;0.3243;0.5944;0.5946;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="536" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">平均のずれ: 普通 0.044 → 可視性つき 0.000<animate attributeName="opacity" dur="18.5s" repeatCount="indefinite" keyTimes="0.0000;0.5944;0.5946;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:probe-bilinear:end -->

### 3D 格子

<strong>プローブを規則的な 3D 格子</strong>に並べ、<strong>格子上でトライリニア補間</strong>します。

3D 格子の利点は、補間が安いことです。GPU で 3D テクスチャとして引けるので、画素ごとに補間できます。欠点は、密度が一様で疎な所が無駄になること、メモリが体積に比例して増えることです。Light Probe Volume、DDGI、モバイル向けの実装で採用されます。

### 四面体補間の中身

四面体の中の点 p は、4 つの頂点 a, b, c, d の<strong>重心座標</strong>で表せます。`p = w_a·a + w_b·b + w_c·c + w_d·d`（重みの合計は 1）。各頂点のプローブの SH 係数に、同じ重みを掛けて足したものが、p での SH です。重みは、p と他の 3 頂点が作る小さな四面体の体積の比で求まります。計算は軽いですが、どの四面体に p が入っているかを探す処理が必要で、物体が動くたびに、前フレームの四面体から隣へ辿って更新するのが一般的です。

### トライリニア補間の中身

格子の場合は、p を囲む 8 つの格子点があり、各軸で 0〜1 の小数部分を使って、2×2×2 の重みを作ります。ハードウェアの三線形フィルタがそのまま使えるので、SH の係数を 3D テクスチャに入れておけば、1 回のテクスチャ読み込みで補間が済みます。ただし、壁の向こう側のプローブも等しく混ざってしまうので、光漏れが起きます。DDGI のように、各プローブに距離情報を持たせ、見えないプローブの重みを下げる方式があります（[DDGI](../ddgi.md)）。

### 画素ごとの引き

<strong>物体ごと（1 点）</strong>でなく、<strong>画素ごと</strong>に<strong>プローブを引く</strong>（GPU で、3D テクスチャから）と、大きな物体・地形の場所による変化が反映されます。1 つの物体を 1 点で代表すると、大きな物体で不自然です。

## 動く物の、位置で、プローブを、補間する

<strong>動く物</strong>（キャラクター）は、<strong>プローブの、位置ちょうど</strong>には、いません。周りの、プローブを、補間して、その位置の、光を、推定します。補間の、やり方で、光の、なめらかさと、光漏れの、少なさが、変わります。

## 方法 1：トライリニア補間（格子）

<strong>格子配置</strong>の、プローブでは、<strong>物の位置を、含む、セルの、8 つの、頂点</strong>（プローブ）を、3 次元の、線形補間します。

```hlsl
// 格子配置のプローブの、トライリニア補間（手動）。ハードウェアの 3D テクスチャでも、同じ結果。
void TrilinearProbes(float3 world_pos, out float3 sh[9]) {
  float3 grid = (world_pos - g_probe_origin) / g_probe_spacing;           // 格子座標（プローブ単位）
  int3 base = (int3)floor(grid);
  float3 f = grid - base;                                                  // セル内の位置（0〜1）

  for (int i = 0; i < 9; ++i) sh[i] = 0.0;
  for (int dz = 0; dz <= 1; ++dz)
    for (int dy = 0; dy <= 1; ++dy)
      for (int dx = 0; dx <= 1; ++dx) {
        float w = (dx ? f.x : 1.0 - f.x) * (dy ? f.y : 1.0 - f.y) * (dz ? f.z : 1.0 - f.z);   // 8 つの重み
        float3 probe_sh[9];
        LoadProbeSH(base + int3(dx, dy, dz), probe_sh);
        for (int i = 0; i < 9; ++i) sh[i] += w * probe_sh[i];
      }
}
```

<strong>8 つの、頂点</strong>の、<strong>重み</strong>は、位置が、その頂点に、近いほど、大きく、8 つの、重みの、合計は、1 です。SH 係数は、線形なので、係数を、重みつきで、足すだけで、補間した、光が、得られます（[Spherical Harmonics (SH)](../theory/spherical-harmonics.md)）。ハードウェアの、3D テクスチャ（トライリニア）が、そのまま、同じ計算を、1 回の読み込みで、行います。

## 光漏れの、問題

<strong>単純な、トライリニア補間</strong>は、<strong>壁の、向こう側の、プローブ</strong>も、同じ重みで、混ぜます。壁の、両側で、光が、違う（室内と、屋外）と、光漏れ（室内の、物が、屋外の、光で、明るくなる）が、起きます。

```text
 室内（暗い）  │壁│  屋外（明るい）
    ●         │  │      ●          ← プローブ
         ◎ 物   │  │
 物の位置で、トライリニア補間すると、壁の向こうの、明るいプローブが、混ざって、物が、明るくなる（光漏れ）
```

## 方法 2：可視性による、重み

<strong>そのプローブから、物の位置が、見えるか</strong>（<strong>間に、壁が、あるか</strong>）を、判定して、見えないプローブの、重みを、小さくします（DDGI の、方法。Majercik ら、2019）。

```hlsl
// 各プローブに、可視性（見えるか）の重みを、掛ける。見えないプローブの重みは、0 に近づく。
float w = trilinear_weight * VisibilityWeight(probe, world_pos, normal);
```

### 3 つの、重み

DDGI の、補間は、<strong>3 つの、重み</strong>を、<strong>掛け合わせます</strong>。

| 重み | 内容 |
| --- | --- |
| トライリニア | 距離が、近いほど、大きい |
| 法線（面の向き） | 物の法線の、向いている側に、あるプローブを、重視（裏側の、プローブは、軽視） |
| 可視性（チェビシェフ） | プローブから、物の位置が、見える確率（プローブが、持つ、距離の、分布から、求める） |

```hlsl
// DDGI 風の、補間の重み（概略）。
float3 dir_to_probe = normalize(probe_pos - world_pos);
float facing = max(0.0001, (dot(dir_to_probe, normal) + 1.0) * 0.5);        // 法線の側にあるほど、1。裏側は、0
float weight = facing * facing + 0.2;                                         // 二乗で、強調。0.2 は、下限（全部 0 を、防ぐ）

// 可視性: プローブが、各方向の「壁までの距離」の、平均と分散を、持つ（深度の、モーメント）。
float2 moments = SampleProbeDistance(probe, -dir_to_probe);                   // (平均距離, 平均距離の2乗)
float dist_to_probe = length(probe_pos - world_pos);
float visibility = ChebyshevVisibility(moments, dist_to_probe);               // 物が、壁より、手前にある確率
weight *= max(0.05, visibility * visibility * visibility);                    // 立方で、強調。下限を設ける

weight *= trilinear_weight;                                                   // 距離の重み
```

<strong>法線の側にある、プローブ</strong>は、<strong>物の表面を、同じ側から、見ている</strong>ので、信頼できます。裏側のプローブ（壁の、向こう）は、重みを、下げます。可視性は、プローブが、周囲の、壁までの、距離を、持っており、物の位置が、壁の手前にあるかを、確率的に、判定します（シャドウ マップの、VSM と、同じ、チェビシェフの不等式。[VSM, ESM and MSM](../../shadows/vsm/index.md)）。

## 方法 3：法線方向に、ずらして、サンプルする

<strong>面の、法線の方向に、少し、ずらした位置</strong>で、<strong>プローブを、補間</strong>します。壁の、表面の、すぐ近くの、物が、壁の、向こうの、プローブに、影響されにくくなります。

```hlsl
float3 sample_pos = world_pos + normal * g_probe_normal_bias;               // 法線の向きに、ずらす（プローブの、間隔の、0.2〜0.5 倍）
TrilinearProbes(sample_pos, sh);
```

<strong>法線オフセット</strong>（[Normal Offset](../../shadows/bias/normal-offset.md) と、同じ発想）で、<strong>壁の、こちら側の、プローブを、選びやすく</strong>なります。簡単で、効果的ですが、ずらしすぎると、光の位置が、ずれて、不自然に、なります。

## 方法 4：最も近い、複数のプローブだけ

<strong>格子でない</strong>配置（手動、適応的）では、<strong>物の周りの、最も近い、N 個</strong>（4〜8 個）の、プローブを、探し、距離の、逆数などで、重みづけして、補間します。

```hlsl
// 物の周りの、最も近い、4 個のプローブを、距離の逆数で、重みづけして補間する（格子でない配置）。
float total_w = 0.0;
for (int i = 0; i < 4; ++i) {
  int idx = nearest_probes[i];                                               // 事前に、探しておいた、近いプローブ（空間分割で、高速に）
  float d = length(g_probes[idx].position - world_pos);
  float w = 1.0 / (d * d + 0.01);                                             // 近いほど、重い（逆二乗）
  w *= VisibilityWeight(g_probes[idx], world_pos, normal);
  for (int k = 0; k < 9; ++k) sh[k] += w * g_probes[idx].sh[k];
  total_w += w;
}
for (int k = 0; k < 9; ++k) sh[k] /= total_w;                                // 重みの合計で割る（合計を 1 に）
```

<strong>最も近い、プローブを、探す</strong>のが、<strong>重く</strong>なりやすいので、空間分割（八分木、格子）で、高速化します。

## 比較

| 方法 | 光漏れ | コスト | 配置 |
| --- | --- | --- | --- |
| トライリニア（ハードウェア） | 多い | 最小（3D テクスチャの、読み込み） | 格子のみ |
| 法線オフセット + トライリニア | やや、少ない | 最小 | 格子のみ |
| 可視性 + 法線の重み（DDGI） | 少ない | 中（8 プローブ × 3 つの重み） | 格子 |
| 近傍 N 個 + 重み | 重みによる | 中〜大 | 任意 |

## よくあるミス

??? failure "壁の向こうの明るさが、手前に漏れる"
    <strong>可視性を考慮した補間</strong>にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 周囲のプローブを、重み付きで補間
    - [x] 可視性で、光漏れを防ぐ

## 参考

- Majercik, Guertin, Nowrouzezahrai, McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019
- Greger, Shirley, Hubbard, Greenberg, "The Irradiance Volume", IEEE Computer Graphics and Applications, Vol. 18, No. 2, 1998（放射照度ボリューム。プローブ GI の原点）
- Tatarchuk, "Irradiance Volumes for Games", Game Developers Conference 2005
- Donnelly, Lauritzen, "Variance Shadow Maps", Symposium on Interactive 3D Graphics and Games 2006

## 関連ページ

- [Probe GI](index.md)
- [DDGI](../ddgi.md)
- [Probe Placement](placement.md)
