---
title: フローマップ
tags:
  - 描画
---

# フローマップ

**川や渦の水は、一方向に流れます**。**フローマップ（流れの向きを入れたテクスチャ）で、法線マップを流す**と、**流れを表現**できます。このページでは、**フローマップの使い方**を説明します。

!!! tip "ポイント"
    - **フローマップ ＝ 各位置の、流れの向きを入れたテクスチャ**。
    - **その向きに、法線マップの UV をずらす**。
    - **ずらし続けると歪むので、2 層を交互にブレンド**する。
    - **川・滝・渦の表現に使う**。

## フローマップ（水の流れ）
**川の流れ**は**波動のシミュレーションとは別**に、<strong>流れの向きを描いたテクスチャ（フローマップ）</strong>で**表現**します。**法線マップをその向きに流す**ことで**水が流れて見えます**。

**フローマップは、各点の流れの向き（RG に 2D ベクトル）を持つテクスチャ**です。

```hlsl
float2 flow = flow_map.Sample(linear_clamp, uv).rg * 2.0 - 1.0;
float flow_time = time * flow_speed;

float phase0 = frac(flow_time);
float phase1 = frac(flow_time + 0.5);
float2 uv0 = world_uv - flow * phase0 * flow_strength;
float2 uv1 = world_uv - flow * phase1 * flow_strength;

float3 n0 = normal_map.Sample(linear_wrap, uv0).xyz * 2.0 - 1.0;
float3 n1 = normal_map.Sample(linear_wrap, uv1).xyz * 2.0 - 1.0;

float blend = abs(phase0 * 2.0 - 1.0);
float3 flow_normal = normalize(lerp(n0, n1, blend));
```

| 点 | 説明 |
| --- | --- |
| **`frac(time)`** | **UV が流れ続けるとテクスチャが引き伸ばされる**ので、**周期的に元に戻す** |
| **位相をずらした 2 つ** | **0 と 0.5 ずらした 2 つ**を**交互にブレンド**して、**戻る瞬間の「跳び」を隠す** |
| **`blend`** | **片方が戻る（見えなくなる）タイミングでもう片方が最大** |
| **`world_uv` に乱数を足す** | **場所ごとに位相をずらすと、全体が同時に切り替わらない** |

<svg class="fig illust motion" data-fig="water-flow" viewBox="0 0 780 200" role="img" aria-label="フローマップ">
<text x="20" y="24" class="fig-title">フローマップ：流れの向きに、模様が流れていく</text>
<rect x="40" y="50" width="700" height="120" fill="#4c8bf5" fill-opacity="0.18"/>
<g stroke="#4c8bf5" stroke-width="3" fill="none" stroke-linecap="round">
<path d="M0,80 h40">
<animateTransform attributeName="transform" type="translate" values="60,0;680,0" dur="4s" repeatCount="indefinite"/>
</path>
<path d="M0,110 h60">
<animateTransform attributeName="transform" type="translate" values="60,0;680,0" dur="3s" repeatCount="indefinite"/>
</path>
<path d="M0,140 h40">
<animateTransform attributeName="transform" type="translate" values="60,0;680,0" dur="5s" repeatCount="indefinite"/>
</path>
</g>
<text x="60" y="188" style="font-size:12px">流れの向き →</text>
</svg>

### フローマップの作り方

| 方法 | 内容 |
| --- | --- |
| **手描き** | **ペイント ツールで流れの向きを描く**（色が向き） |
| **シミュレーション** | **地形の傾きから、流れを計算して焼き込む**（**高い所から低い所へ**） |
| **障害物を避ける** | **岩の周りで流れが曲がる**ように、**向きを描く** |
| **流速を長さで** | **ベクトルの長さを流れの速さ**にする |

## よくあるミス

??? failure "流れが、時間とともに引き伸ばされる"
    **位相をずらした 2 層**を**交互にブレンド**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **向きを入れたテクスチャで、UV を流す**
    - [x] **2 層のブレンドで、歪みを防ぐ**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水との相互作用](index.md)
- [水面の波](../waves/index.md)
