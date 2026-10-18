---
title: Storing SH
tags:
  - 描画
---

# Storing SH

<strong>プローブには、SH の係数を保存します</strong>。<strong>次数（L1 か L2）と、保存の形式（浮動小数点・圧縮）で、メモリと品質が変わります</strong>。このページでは、SH の持ち方の選択肢を説明します。

!!! tip "ポイント"
    - L1（4 係数）：軽いが、方向性が弱い。
    - L2（9 係数）：標準。
    - 色ごと（RGB）に係数を持つので、L2 では 27 個。
    - テクスチャ（3D）に保存して、ハードウェア補間を使う。

## SH をどう持つか

プローブに保存する値は、「各法線方向の放射照度」を表す関数です。これを何個の数値で持つかで、メモリと品質が決まります。選択肢を、軽い順に並べてみます。

### アンビエント キューブ（6 方向）

6 方向（+X, −X, +Y, −Y, +Z, −Z）に、それぞれ 1 色を持ちます（18 個の数値）。法線 n が与えられたら、n の各成分の符号で、3 つの面（X の正負のどちらか、Y のどちらか、Z のどちらか）を選び、n の成分の 2 乗を重みとして混ぜます。

<div class="formula">E(n) = n.x² · C(sign x) + n.y² · C(sign y) + n.z² · C(sign z)</div>

n は単位ベクトルなので、重みの 2 乗の和は 1 になります。計算は掛け算と足し算だけで、とても安いです。Valve の Source エンジンが採用し（『Half-Life 2』など）、軽さが求められる環境では今でも有効な選択です。方向の分解能は粗いですが、拡散の間接光はもともと低周波なので、意外に見た目が保たれます。

### SH L1（4 係数 × RGB = 12 個）

[球面調和関数](../theory/spherical-harmonics.md)の 0 次（1 係数）と 1 次（3 係数）だけを持つ方式です。0 次が平均の明るさ、1 次が「どちらの向きが明るいか」を表します。向きの違いを、緩やかな 1 本の傾きでしか表せないので、空が明るく地面が暗い、のような単純な傾向は表せますが、複雑な向き依存は失われます。メモリが小さく、シェーダーも軽いので、モバイルや大量のプローブに向きます。

### SH L2（9 係数 × RGB = 27 個）

2 次まで持つ標準的な方式です。Ramamoorthi と Hanrahan の結果（2001）のとおり、拡散の放射照度の誤差は 1 % 程度で、ほぼ十分な精度が得られます。一般的なゲームのライト プローブは、これを採用しています（Unity のライト プローブも L2 です）。

### 八面体マップ（小さなテクスチャ）

各プローブに、小さな方向テクスチャ（たとえば 8×8 の八面体展開）を持たせる方式です。DDGI のように、方向ごとの放射照度と可視性（距離）まで保存したい場合に使います（[DDGI](../ddgi.md)）。係数でなく、サンプルの並びなので、SH よりも高周波を持てますが、メモリが増えます。

### リンギングへの対策

SH で光を表すと、<strong>リンギング</strong>（本来は 0 以上のはずの値が、負になる）が出ることがあります。光源が鋭い（太陽のような）ときに、SH の打ち切り誤差で、反対側の方向が負の値になるためです。負の光は、物理的にありえません。対策は、<strong>ウィンドウ関数</strong>（ハンニング窓など）で高次の係数を少し弱めてなだらかにすることと、評価結果を 0 でクランプすることです。窓関数を強くしすぎると、向きの鋭さが失われるので、バランスを取ります。

### どう保存するか

プローブが空間に格子状に並ぶなら、係数を<strong>3D テクスチャ</strong>に格納します。係数ごとに別々の 3D テクスチャ（あるいはチャンネル）にしておくと、ハードウェアの三線形補間で、プローブ間の補間を自動的に行えます。プローブが不規則に置かれる場合は、四面体分割（Unity の方式）や、八分木ベースのブリック（Unreal の Volumetric Lightmap）を使い、補間はシェーダーやコンピュート側で行います。

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

## よくあるミス

??? failure "SH の次数が低く、方向による明暗の差が出ない"
    <strong>L2 に上げる</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] L1 は軽い、L2 は標準
    - [x] 3D テクスチャに入れて、補間をハードウェアに任せる

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Probe GI](index.md)
- [Spherical Harmonics (SH)](../theory/spherical-harmonics.md)
- [Interpolation Methods](interpolation.md)
