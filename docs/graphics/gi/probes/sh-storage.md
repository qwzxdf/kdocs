---
title: Storing SH
tags:
  - 描画
---

# Storing SH

<strong>プローブには SH の係数を保存します</strong>。<strong>次数（L1 か L2）と保存の形式（浮動小数点・圧縮）で、メモリと品質が変わります</strong>。このページでは SH の持ち方の選択肢を説明します。

!!! tip "ポイント"
    - L1（4 係数）：軽いが、方向性が弱い。
    - L2（9 係数）：標準。
    - 色ごと（RGB）に係数を持つので、L2 では 27 個。
    - テクスチャ（3D）に保存して、ハードウェア補間を使う。

## SH をどう持つか

プローブに保存する値は「各法線方向の放射照度」を表す関数です。これを何個の数値で持つかでメモリと品質が決まります。選択肢を軽い順に並べてみます。

### アンビエント キューブ（6 方向）

6 方向（+X, −X, +Y, −Y, +Z, −Z）に、それぞれ 1 色を持ちます（18 個の数値）。法線 n が与えられたら n の各成分の符号で、3 つの面（X の正負のどちらか、Y のどちらか Z のどちらか）を選び、n の成分の 2 乗を重みとして混ぜます。

<div class="formula">E(n) = n.x² · C(sign x) + n.y² · C(sign y) + n.z² · C(sign z)</div>

n は単位ベクトルなので重みの 2 乗の和は 1 になります。計算は掛け算と足し算だけでとても安いです。Valve の Source エンジンが採用し（『Half-Life 2』など）、軽さが求められる環境では今でも有効な選択です。方向の分解能は粗いですが拡散の間接光はもともと低周波なので、意外に見た目が保たれます。

### SH L1（4 係数 × RGB = 12 個）

[球面調和関数](../theory/spherical-harmonics.md)の 0 次（1 係数）と 1 次（3 係数）だけを持つ方式です。0 次が平均の明るさ 1 次が「どちらの向きが明るいか」を表します。向きの違いを緩やかな 1 本の傾きでしか表せないので、空が明るく地面が暗いのような単純な傾向は表せますが、複雑な向き依存は失われます。メモリが小さくシェーダーも軽いので、モバイルや大量のプローブに向きます。

### SH L2（9 係数 × RGB = 27 個）

2 次まで持つ標準的な方式です。Ramamoorthi と Hanrahan の結果（2001）のとおり、拡散の放射照度の誤差は 1 % 程度で、ほぼ十分な精度が得られます。一般的なゲームのライト プローブは、これを採用しています（Unity のライト プローブも L2 です）。

### 八面体マップ（小さなテクスチャ）

各プローブに小さな方向テクスチャ（たとえば 8×8 の八面体展開）を持たせる方式です。DDGI のように方向ごとの放射照度と可視性（距離）まで保存したい場合に使います（[DDGI](../ddgi.md)）。係数でなくサンプルの並びなので、SH よりも高周波を持てますが、メモリが増えます。

### リンギングへの対策

SH で光を表すと <strong>リンギング</strong>（本来は 0 以上のはずの値が、負になる）が出ることがあります。光源が鋭い（太陽のような）ときに、SH の打ち切り誤差で反対側の方向が負の値になるためです。負の光は物理的にありえません。対策は <strong>ウィンドウ関数</strong>（ハンニング窓など）で高次の係数を少し弱めてなだらかにすることと、評価結果を 0 でクランプすることです。窓関数を強くしすぎると向きの鋭さが失われるので、バランスを取ります。

### どう保存するか

プローブが空間に格子状に並ぶなら、係数を<strong>3D テクスチャ</strong>に格納します。係数ごとに別々の 3D テクスチャ（あるいはチャンネル）にしておくと、ハードウェアの三線形補間でプローブ間の補間を自動的に行えます。プローブが不規則に置かれる場合は、四面体分割（Unity の方式）や、八分木ベースのブリック（Unreal の Volumetric Lightmap）を使い、補間はシェーダーやコンピュート側で行います。

<!-- fig:sh-coeff-count:begin -->

<svg class="fig illust motion" data-fig="sh-coeff-count" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sh-coeff-count" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">SH の次数が上がると、必要な係数が増える(RGB の 3 色ぶん)</text>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><rect x="170" y="278" width="100" height="22" fill="#2ea043" opacity="0.85"/>
<text x="220" y="250" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#2ea043">1 個</text>
<text x="220" y="268" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">×3 色 = 3</text>
<text x="220" y="320" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">L0（1 次）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2953;0.2957;1.0000" values="0;0;1;1"/><rect x="320" y="212" width="100" height="88" fill="#2563eb" opacity="0.85"/>
<text x="370" y="184" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#2563eb">4 個</text>
<text x="370" y="202" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">×3 色 = 12</text>
<text x="370" y="320" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">L1（2 次）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5040;0.5043;1.0000" values="0;0;1;1"/><rect x="470" y="102" width="100" height="198" fill="#e5484d" opacity="0.85"/>
<text x="520" y="74" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#e5484d">9 個</text>
<text x="520" y="92" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">×3 色 = 27</text>
<text x="520" y="320" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">L2（3 次）</text>
</g>
<line x1="120" y1="300" x2="660" y2="300" stroke="#94a3b8" stroke-width="2"/>
<text x="390" y="365" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">次数ごとの係数の数 (次数 l で 2l+1 個)<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="390" y="365" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">L0: 1 個。向きによらない明るさ<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2953;0.2957;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="365" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">L1: 4 個になる(累計)。大まかな明暗の向き<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2953;0.2957;0.5040;0.5043;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="365" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">L2: 9 個(累計)。×3 色で 27 個。ゲームで一般的な次数<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5040;0.5043;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:sh-coeff-count:end -->

## SH 係数をどう保存するか

プローブ 1 つのデータは <strong>SH L2 の、27 個の浮動小数点数</strong>（9 係数 × RGB）です。<strong>数千個のプローブ</strong>を GPU が高速に、読める形で保存する方法を整理します。

| 方法 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| 構造化バッファ | プローブごとに `float3 sh[9]` の、構造体 | 簡単。任意の配置（格子でなくてもよい） | 補間が、手動（ハードウェアの補間が使えない） |
| 3D テクスチャ（複数枚） | 格子配置の、プローブを 3D テクスチャに。係数ごとに別のテクスチャ | ハードウェアの、トライリニア補間が使える | 格子配置が必須。テクスチャの枚数が増える（7 枚など） |
| 2D テクスチャ アトラス | プローブを、2D のタイルに並べる | 3D テクスチャが、使えない環境でも動く | 補間が、手動 |

## 3D テクスチャで持つ

<strong>格子配置</strong>のプローブは <strong>3D テクスチャ</strong>に、そのまま格納できます。テクセル 1 つがプローブ 1 つです。トライリニア補間をハードウェアが、やってくれます（8 つのプローブを、1 回の読み込みで補間）。

### 係数のパッキング

SH L2 は <strong>9 係数 × RGB = 27 個の数</strong>です。<strong>1 つのテクセル</strong>（`RGBA16_FLOAT`、4 つの値）に収まらないので複数の、テクスチャに分けます。

| テクスチャ | R | G | B | A |
| --- | --- | --- | --- | --- |
| 0 | L0.r | L0.g | L0.b | L1₋₁.r |
| 1 | L1₋₁.g | L1₋₁.b | L1₀.r | L1₀.g |
| 2 | L1₀.b | L1₁.r | L1₁.g | L1₁.b |
| 3 | L2₋₂.r | L2₋₂.g | L2₋₂.b | L2₋₁.r |
| 4 | L2₋₁.g | L2₋₁.b | L2₀.r | L2₀.g |
| 5 | L2₀.b | L2₁.r | L2₁.g | L2₁.b |
| 6 | L2₂.r | L2₂.g | L2₂.b | （未使用） |

<strong>7 枚</strong>の `RGBA16_FLOAT` の 3D テクスチャで、<strong>27 個の数</strong>を収めます（28 個分の領域で 1 つ、余ります）。

```hlsl
// 7 枚の 3D テクスチャから、補間した SH 係数（RGB × 9）を読む。uvw は、プローブ格子の中の、位置（0〜1）。
Texture3D<float4> g_probe_sh[7] : register(t10);

void LoadSH(float3 uvw, out float3 sh[9]) {
  float4 t0 = g_probe_sh[0].SampleLevel(g_linear_clamp, uvw, 0);
  float4 t1 = g_probe_sh[1].SampleLevel(g_linear_clamp, uvw, 0);
  float4 t2 = g_probe_sh[2].SampleLevel(g_linear_clamp, uvw, 0);
  float4 t3 = g_probe_sh[3].SampleLevel(g_linear_clamp, uvw, 0);
  float4 t4 = g_probe_sh[4].SampleLevel(g_linear_clamp, uvw, 0);
  float4 t5 = g_probe_sh[5].SampleLevel(g_linear_clamp, uvw, 0);
  float4 t6 = g_probe_sh[6].SampleLevel(g_linear_clamp, uvw, 0);
  sh[0] = t0.rgb;                      // L0
  sh[1] = float3(t0.a, t1.r, t1.g);    // L1₋₁
  sh[2] = float3(t1.b, t1.a, t2.r);    // L1₀
  sh[3] = float3(t2.g, t2.b, t2.a);    // L1₁
  sh[4] = t3.rgb;                      // L2₋₂
  sh[5] = float3(t3.a, t4.r, t4.g);    // L2₋₁
  sh[6] = float3(t4.b, t4.a, t5.r);    // L2₀
  sh[7] = float3(t5.g, t5.b, t5.a);    // L2₁
  sh[8] = t6.rgb;                      // L2₂
}
```

<strong>7 回の `SampleLevel`</strong>（<strong>ハードウェアの、トライリニア</strong>）で 9 係数 × RGB を、得ます。補間した係数を `IrradianceFromSH9` に渡して放射照度を、求めます（[Spherical Harmonics (SH)](../theory/spherical-harmonics.md)）。

## 係数を減らす（圧縮）

<strong>27 個</strong>は <strong>多すぎる</strong>場合、減らします。

### L1 にする（12 個）

<strong>L2 の 5 係数</strong>（L2₋₂〜L2₂）を、<strong>省き</strong>、L0 + L1 の 4 係数（12 個）に、します。メモリが半分以下、3 枚のテクスチャで済みます。方向の表現が粗くなりますが放射照度の、おおまかな向きは保たれます。

```hlsl
// SH L1（4 係数）から、法線方向の放射照度（近似）を求める。
float3 IrradianceFromSH4(float3 sh[4], float3 n) {
  // L0 + L1: 余弦の畳み込み係数 A0 = π、A1 = 2π/3 を、基底関数の定数と、かけた、形。
  return 0.886227 * sh[0] + 2.0 * 0.511664 * (sh[3] * n.x + sh[1] * n.y + sh[2] * n.z);
}
```

L1 の <strong>放射照度</strong>には <strong>負の値</strong>（光が、マイナス）が出やすい（リンギング）ので `max(0, …)` で切るか、ウィンドウ関数で抑えます（[Spherical Harmonics (SH)](../theory/spherical-harmonics.md)）。

### 色をまとめる

<strong>RGB ごとに別の SH</strong>ではなく、<strong>輝度だけ</strong>に SH L2 を使い色は、L0 だけ（向きなし）の RGB に、する方法です。1 + 9 = 10 個の数に、なります。色が向きによって変わる表現（赤い壁の側だけ、赤い）が失われます。

### 量子化（精度を落とす）

<strong>32 ビットの浮動小数点</strong>を、<strong>16 ビット</strong>（`R16G16B16A16_FLOAT`）、さらに 8 ビット（`R8G8B8A8_UNORM`、スケール調整つき）に落とすと、メモリが減ります。

| 形式 | 1 係数 | 27 係数 | 品質 |
| --- | --- | --- | --- |
| `R32_FLOAT` | 4 バイト | 108 バイト | 最高 |
| `R16_FLOAT` | 2 バイト | 54 バイト | 十分（標準） |
| `R8_UNORM`（スケール付き） | 1 バイト | 27 バイト | 低（バンディング） |

プローブが <strong>1 万個</strong>でも `R16_FLOAT` なら、<strong>540 KB</strong> です。ほとんどの場合、16 ビット浮動小数点で十分です。

## 構造化バッファで持つ

<strong>格子でない</strong>（手動配置、適応的な配置）のプローブは <strong>構造化バッファ</strong>に、持ちます。

```hlsl
struct ProbeSH {
  float3 sh[9];            // 27 個の float（108 バイト）
  float pad;               // 16 バイト境界に、そろえる
};
StructuredBuffer<ProbeSH> g_probes : register(t10);

float3 irradiance = IrradianceFromSH9(g_probes[probe_index].sh, normal);
```

<strong>補間</strong>は <strong>自分で実装</strong>します（周りの、プローブを探し重みつきで SH 係数を、足す）。ハードウェアの補間が使えないのでやや、重いですが配置の自由度は高いです（[Interpolation Methods](interpolation.md)）。

## SH の更新

<strong>動的に更新するプローブ</strong>（[Dynamic Updates](dynamic-update.md)）では、<strong>毎フレーム</strong>（または数フレームに 1 回）、SH 係数を再計算してテクスチャに、書き込みます。

```cpp
// 計算シェーダーで、プローブの SH を、再計算して、UAV（3D テクスチャ）に書き込む。
context->CSSetUnorderedAccessViews(0, 7, probe_uavs, nullptr);       // 7 枚の、3D テクスチャを、UAV として
context->Dispatch(probe_count.x, probe_count.y, probe_count.z);
```

## よくあるミス

??? failure "SH の次数が低く、方向による明暗の差が出ない"
    <strong>L2 に上げる</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] L1 は軽い、L2 は標準
    - [x] 3D テクスチャに入れて、補間をハードウェアに任せる

## 参考

- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001
- Sloan, "Stupid Spherical Harmonics (SH) Tricks", Game Developers Conference 2008
- Iwanicki, "Lighting Technology of The Last of Us", SIGGRAPH 2013, Advances in Real-Time Rendering in Games（アンビエント ダイスなど）
- Majercik, Guertin, Nowrouzezahrai, McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019
- Microsoft Learn, "D3D11_TEXTURE3D_DESC"

## 関連ページ

- [Probe GI](index.md)
- [Spherical Harmonics (SH)](../theory/spherical-harmonics.md)
- [Interpolation Methods](interpolation.md)
