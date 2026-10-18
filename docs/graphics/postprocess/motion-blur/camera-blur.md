---
title: Camera Motion Blur
tags:
  - 描画
---

# Camera Motion Blur

**カメラが動いたり回ったりすると、静止している背景全体が、流れるように見えます**。**カメラ モーション ブラー**は、**この背景の流れ**を**表現**する**ブラー**で、**コストが安く、スピード感への効果が大きい**ため、**最初に実装すべき**部分です。**必要なのは画素ごとの深度と前フレームのカメラ行列だけ**で、**動く物体の速度バッファを作らなくても実現**できます。このページでは、**深度から速度を再構成する方法・並進と回転の違い・注意点（動く物体・遠景）・より良いやり方**を説明します。

!!! tip "ポイント"
    - カメラ ブラー ＝ <strong>カメラの動きによる、静止した物の見かけの動き</strong>を<strong>ぼかしにする</strong>。
    - <strong>深度（ワールド位置を再構成）</strong>＋<strong>前フレームのカメラ行列</strong>で、<strong>各画素の速度が分かる</strong>。
    - <strong>回転</strong>は<strong>画面全体が同じ向きに流れる</strong>。<strong>並進</strong>は<strong>近い物ほど速く流れる（視差）</strong>。
    - <strong>動く物体には、カメラ速度は不正確</strong>（<strong>物体ブラー</strong>で上書き）。
    - <strong>遠景（深度が最奥）</strong>は<strong>回転の影響だけ</strong>。
    - <strong>ゲーム内のカット切り替え</strong>では<strong>速度を 0 に</strong>する。

<!-- fig:camera-blur:begin -->

<svg class="fig illust motion" data-fig="camera-blur" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-camera-blur" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">カメラ ブラー: カメラが動くと、近い物ほど、画面で大きく動く(流れが長い)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。カメラが右へ 1 m 動く。深度(距離)ごとに、画面の動き(画素)が、距離に反比例する</text>
<rect x="30" y="96" width="900" height="190" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 上から見た図(カメラ → 右へ。柱が距離ごとに立つ)</text>
<circle cx="90.0" cy="250.0" r="9" fill="#1f2937"/>
<text x="90.0" y="276.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">カメラ</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="0;0;1;1"/><rect x="117.0" y="180.0" width="14" height="70" fill="#e5484d" opacity="0.85"/>
<text x="124.0" y="172.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">2 m</text>
<line x1="124.0" y1="220.0" x2="124.0" y2="220.0" stroke="#e5484d" stroke-width="0"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2091;0.2093;1.0000" values="0;0;1;1"/><rect x="151.0" y="180.0" width="14" height="70" fill="#e5aa28" opacity="0.85"/>
<text x="158.0" y="172.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5aa28">4 m</text>
<line x1="158.0" y1="220.0" x2="158.0" y2="220.0" stroke="#e5aa28" stroke-width="0"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3487;0.3488;1.0000" values="0;0;1;1"/><rect x="219.0" y="180.0" width="14" height="70" fill="#2ea043" opacity="0.85"/>
<text x="226.0" y="172.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2ea043">8 m</text>
<line x1="226.0" y1="220.0" x2="226.0" y2="220.0" stroke="#2ea043" stroke-width="0"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4882;0.4884;1.0000" values="0;0;1;1"/><rect x="355.0" y="180.0" width="14" height="70" fill="#2563eb" opacity="0.85"/>
<text x="362.0" y="172.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2563eb">16 m</text>
<line x1="362.0" y1="220.0" x2="362.0" y2="220.0" stroke="#2563eb" stroke-width="0"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6277;0.6279;1.0000" values="0;0;1;1"/><rect x="763.0" y="180.0" width="14" height="70" fill="#7c3aed" opacity="0.85"/>
<text x="770.0" y="172.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#7c3aed">40 m</text>
<line x1="770.0" y1="220.0" x2="770.0" y2="220.0" stroke="#7c3aed" stroke-width="0"/>
</g>
<rect x="30" y="306" width="900" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="296" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 画面での流れの長さ(画素)= 焦点距離 × カメラの動き ÷ 距離</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0882;0.0884;1.0000" values="0;0;1;1"/><text x="50" y="354" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">2 m</text>
<rect x="120" y="342" width="600.0" height="16" fill="#e5484d" opacity="0.85"/>
<text x="728.0" y="355" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">180 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2277;0.2279;1.0000" values="0;0;1;1"/><text x="50" y="376" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">4 m</text>
<rect x="120" y="364" width="300.0" height="16" fill="#e5aa28" opacity="0.85"/>
<text x="428.0" y="377" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">90 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3673;0.3674;1.0000" values="0;0;1;1"/><text x="50" y="398" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">8 m</text>
<rect x="120" y="386" width="150.0" height="16" fill="#2ea043" opacity="0.85"/>
<text x="278.0" y="399" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">45 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5068;0.5070;1.0000" values="0;0;1;1"/><text x="50" y="420" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">16 m</text>
<rect x="120" y="408" width="75.0" height="16" fill="#2563eb" opacity="0.85"/>
<text x="203.0" y="421" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">22 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6463;0.6465;1.0000" values="0;0;1;1"/><text x="50" y="442" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">40 m</text>
<rect x="120" y="430" width="30.0" height="16" fill="#7c3aed" opacity="0.85"/>
<text x="158.0" y="443" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">9 画素</text>
</g>
<text x="40" y="480" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">いま見ている距離の流れ(画素):</text>
<text x="300" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0882;0.0884;1.0000" values="1;1;0;0"/></text>
<text x="300" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">180<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0882;0.0884;0.2277;0.2279;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">90<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2277;0.2279;0.3673;0.3674;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">45<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3673;0.3674;0.5068;0.5070;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">22<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5068;0.5070;0.6463;0.6465;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6463;0.6465;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7673;0.7674;1.0000" values="0;0;1;1"/><rect x="360" y="466" width="570" height="54" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="376" y="490" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">近い物(2 m)は 遠い物(40 m)の 20 倍 流れる</text>
<text x="376" y="513" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">だから、深度バッファから、画素ごとの流れを計算する</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラが動くと、画面全体が流れる。でも、流れ方は、距離で違う<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">近い物ほど、画面で大きく動く<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.7673;0.7674;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠景はほとんど流れず、近景が大きく流れる(視差)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7673;0.7674;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:camera-blur:end -->

## 並進と回転

**カメラの動きは、2 種類**あります。

カメラの動きは 2 種類あります。回転（見回す）では、画面全体が同じ向きにほぼ同じ速さで流れます（距離に依りません）。並進（歩く・走る・走行）では、近い物ほど速く、遠い物ほど遅く流れ（視差）、進行方向の中心から外へ放射状に広がります。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="カメラの動きと速度">
<text x="20" y="26" class="fig-title">回転は一様に流れ、前進は中心から放射状に流れる</text>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">回転（右を向く）</text>
<rect x="0" y="0" width="300" height="140" fill="#f8fafc" stroke="#94a3b8"/>
<g stroke="#e5484d" stroke-width="2.5" marker-end="url(#cb-arrow)"><line x1="260" y1="30" x2="200" y2="30"/><line x1="260" y1="70" x2="200" y2="70"/><line x1="260" y1="110" x2="200" y2="110"/><line x1="140" y1="30" x2="80" y2="30"/><line x1="140" y1="70" x2="80" y2="70"/><line x1="140" y1="110" x2="80" y2="110"/></g>
<defs><marker id="cb-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#e5484d"/></marker></defs>
<text x="0" y="164" style="font-size:12px">どこも同じ向き・同じ大きさ</text>
</g>
<g transform="translate(420,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">並進（前に進む）</text>
<rect x="0" y="0" width="300" height="140" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="150" cy="70" r="4" fill="#2563eb"/>
<g stroke="#e5484d" stroke-width="2.5" marker-end="url(#cb-arrow)"><line x1="160" y1="65" x2="185" y2="52"/><line x1="140" y1="65" x2="115" y2="52"/><line x1="160" y1="75" x2="185" y2="88"/><line x1="140" y1="75" x2="115" y2="88"/><line x1="200" y1="50" x2="262" y2="14"/><line x1="100" y1="50" x2="38" y2="14"/><line x1="200" y1="90" x2="262" y2="126"/><line x1="100" y1="90" x2="38" y2="126"/></g>
<text x="0" y="164" style="font-size:12px">中心は動かず、外へ行くほど速い（近い物ほど速い）</text>
</g>
</svg>

## 深度から速度を作る

**画素の深度から、その点のワールド位置を再構成し**、**前フレームのカメラでその点がどこに見えていたか**を**計算**します。

```hlsl
float2 CameraVelocity(float2 uv, float depth) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  float4 clip = float4(ndc, depth, 1.0);
  float4 world = mul(clip, inverse_view_projection);
  world /= world.w;
  float4 previous_clip = mul(world, previous_view_projection);
  float2 previous_ndc = previous_clip.xy / previous_clip.w;
  float2 previous_uv = float2(previous_ndc.x * 0.5 + 0.5, 0.5 - previous_ndc.y * 0.5);
  return uv - previous_uv;
}
```

| 点 | 説明 |
| --- | --- |
| **`inverse_view_projection`** | **今フレームの逆行列**。**深度 → ワールド位置** |
| **`previous_view_projection`** | **前フレームのカメラ**。**ワールド位置 → 前の画面位置** |
| **`uv − previous_uv`** | **今 − 前**（<strong>[速度バッファ](velocity-buffer.md)と同じ定義</strong>） |
| **ジッター** | **両方の行列から、ジッターを除く** |

## 特徴と注意

| 項目 | 内容 |
| --- | --- |
| **安い** | **フルスクリーンで深度を 1 回読み、行列を 2 回掛けるだけ**。**物体の速度書き込み不要** |
| **動く物体は不正確** | **物体はカメラ以外にも自分で動く**。**物体の速度で上書き** |
| **遠景** | **深度が最奥（スカイ）は、回転の影響だけ**になる（**並進は無視**） |
| **カメラが速く回る** | **ブラーが強くなりすぎる**ので、**最大長で制限** |
| **ジャンプ・カット** | **カメラが瞬間移動したフレームは、前フレームの行列を今に置き換え、速度 0** |

## 速度の合成

**最終的な速度**は、**動く物体は速度バッファ、それ以外はカメラ速度**を**使います**。

```hlsl
float2 FinalVelocity(float2 uv, float depth) {
  float2 object_velocity = velocity_buffer.SampleLevel(point_clamp, uv, 0).xy;
  bool has_object_velocity = any(object_velocity != 0.0) || stencil_flag;
  return has_object_velocity ? object_velocity : CameraVelocity(uv, depth);
}
```

**ステンシル・専用ビットで、「速度を書いた画素」を区別**する**と**、<strong>「速度ぴったり 0 の動く物体」と「書かれていない画素」を、取り違えません</strong>。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **カメラ ブラーだけをまず実装** | **安く、効果が大きい** |
| **速度の最大長を制限** | **急回転でも画面が崩れない**（**画面高さの 3〜5 %**） |
| **カットで即リセット** | **前フレームの行列を今に** |
| **プレイヤーの武器・手を除外** | **カメラに固定された物は、カメラ ブラーを掛けない**（**ステンシル／マスク**） |
| **遠景は強さを弱める** | **空の流れが強すぎるのを防ぐ** |
| **シャッター角で強さを調整** | [強さと TAA](strength-taa.md) |

## よくあるミス

??? failure "カメラに固定された武器まで、ブラーがかかる"
    **ビューモデルは、カメラと同じ動きなので、速度 0**。**マスクして除外**。

??? failure "カメラが瞬間移動したフレームで、画面全体が大きくぶれる"
    **カットや瞬間移動では、前フレームの行列を今の行列にして、速度を 0**。

??? failure "ブラーが強すぎて、酔う"
    **最大長・強さを抑える**。**オプションで切れる**ようにする。

??? failure "静止した物の速度が、ジッターでふるえる"
    **行列からジッターを除いて**速度を計算。

## これだけ覚える

!!! abstract "まとめ"
    - [x] カメラ ブラー ＝ <strong>カメラの動きによる、静止物の見かけの動き</strong>を<strong>ぼかす</strong>
    - [x] <strong>深度 ＋ 前フレームのカメラ行列</strong>で<strong>速度を再構成</strong>
    - [x] <strong>回転は一様、並進は近い物ほど速い</strong>
    - [x] <strong>動く物体は、物体の速度で上書き</strong>
    - [x] <strong>カットで速度 0</strong>、<strong>最大長で制限</strong>

## 参考

- Rosado, "Motion Blur as a Post-Processing Effect"（GPU Gems 3）
- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）

## 関連ページ

- [Motion Blur](index.md)
- [Velocity Buffer](velocity-buffer.md)
- [Object Motion Blur](object-blur.md)
- [Blur Pass Implementation](blur-pass.md)
