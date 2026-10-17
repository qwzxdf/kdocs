---
title: 波紋と水面のインタラクション
tags:
  - 描画
---

# 波紋と水面のインタラクション

**物が水に触れると波紋が広がります**。**Gerstner 波や FFT 海面は、物と関係なく動く波**なので、**物との相互作用は別に作る**必要があります。このページでは、<strong>高さマップの波動シミュレーション（波紋）・物の接触を書き込む方法・法線の作り方・フローマップ（水の流れ）</strong>を説明します。

!!! tip "ポイント"
    - 波紋 ＝ <strong>水面の高さを 2D テクスチャで持ち</strong>、<strong>毎フレーム波動方程式で更新</strong>する。
    - <strong>物が触れた所に高さを書き込む</strong>（<strong>ブラシ</strong>）と、<strong>そこから波紋が広がる</strong>。
    - <strong>更新は、2 枚（前と今）の高さマップ</strong>を使う：<strong>新しい高さ ＝ 周囲の平均 × 2 − 1 つ前の高さ</strong>（<strong>減衰付き</strong>）。
    - <strong>高さマップの勾配</strong>が<strong>法線</strong>。<strong>波の法線に足す</strong>。
    - <strong>フローマップ</strong>：<strong>水の流れる向きをテクスチャに描き</strong>、<strong>法線マップをその向きに流す</strong>（<strong>川</strong>）。
    - <strong>シミュレーション領域は、カメラの周りの狭い範囲</strong>。<strong>カメラに追従</strong>させる。

## 波動方程式

**水面の高さ `h(x, y, t)` は、波動方程式に従います**。

<div class="formula">∂²h/∂t² = c² · ∇²h　（c：波の速さ、∇²：ラプラシアン）</div>

**グリッド上で差分にすると、次の更新式**になります。

<div class="formula">h_new = 2 · h − h_prev + c²·Δt² · (h_left + h_right + h_up + h_down − 4h)</div>

| 記号 | 意味 |
| --- | --- |
| **h** | **今のフレームの高さ** |
| **h_prev** | **1 つ前のフレームの高さ** |
| **h_new** | **次のフレームの高さ** |
| <strong>(h_left + … − 4h)</strong> | **上下左右の平均との差**（**ラプラシアン**）。**周りより高い所は、下がる** |

**周囲より高ければ下がり、低ければ上がる**ので**振動して波が広がります**。**そのままだと永遠に揺れる**ので、**毎回少し減衰**させます。

```hlsl
Texture2D<float> height_now : register(t0);
Texture2D<float> height_prev : register(t1);
RWTexture2D<float> height_next : register(u0);

cbuffer WaveParams : register(b0) {
  float wave_speed_squared;
  float damping;
  uint2 size;
};

[numthreads(8, 8, 1)]
void CSMain(uint3 id : SV_DispatchThreadID) {
  if (id.x >= size.x || id.y >= size.y) return;

  int2 p = int2(id.xy);
  float h = height_now[p];
  float left = height_now[clamp(p + int2(-1, 0), 0, int2(size) - 1)];
  float right = height_now[clamp(p + int2(1, 0), 0, int2(size) - 1)];
  float up = height_now[clamp(p + int2(0, -1), 0, int2(size) - 1)];
  float down = height_now[clamp(p + int2(0, 1), 0, int2(size) - 1)];

  float laplacian = left + right + up + down - 4.0 * h;
  float next = 2.0 * h - height_prev[p] + wave_speed_squared * laplacian;
  height_next[p] = next * damping;
}
```

| 点 | 説明 |
| --- | --- |
| **3 枚をローテーション** | **今・前・次を毎フレーム入れ替える**（`prev ← now ← next`） |
| **`wave_speed_squared`** | **`c²·Δt²/Δx²`**。**0.5 を超えると不安定で発散**（**CFL 条件**） |
| **`damping`** | **0.98〜0.995**。**小さいほど、早く静まる** |
| **端の処理** | **`clamp` で端を繰り返す**と**反射する**。**端で減衰を強くすると吸収される** |

<svg class="fig illust motion" data-fig="water-ripple" viewBox="0 0 780 220" role="img" aria-label="波紋の広がり">
<text x="20" y="24" class="fig-title">波紋：1 点の高さが、周りに広がりながら小さくなる</text>
<line x1="60" y1="130" x2="720" y2="130" stroke="currentColor" stroke-opacity="0.3"/>
<circle cx="390" cy="130" r="10" fill="none" stroke="#4c8bf5" stroke-width="3">
<animate attributeName="r" values="10;240" dur="3s" repeatCount="indefinite"/>
<animate attributeName="stroke-opacity" values="1;0" dur="3s" repeatCount="indefinite"/>
</circle>
<circle cx="390" cy="130" r="10" fill="none" stroke="#4c8bf5" stroke-width="3">
<animate attributeName="r" values="10;240" dur="3s" begin="1s" repeatCount="indefinite"/>
<animate attributeName="stroke-opacity" values="1;0" dur="3s" begin="1s" repeatCount="indefinite"/>
</circle>
<circle cx="390" cy="130" r="10" fill="none" stroke="#4c8bf5" stroke-width="3">
<animate attributeName="r" values="10;240" dur="3s" begin="2s" repeatCount="indefinite"/>
<animate attributeName="stroke-opacity" values="1;0" dur="3s" begin="2s" repeatCount="indefinite"/>
</circle>
<circle cx="390" cy="130" r="4" fill="#e5484d"/>
<text x="402" y="116" style="font-size:12px">物が触れた点</text>
</svg>

## 物の接触を書き込む

**物が水に触れた所に高さを書き込むと**、**そこが波の起点になります**。

| 方法 | 内容 |
| --- | --- |
| <strong>ブラシ（点）</strong> | **位置に丸い凹みを描き込む**（**キャラクターの足・落ちた物**） |
| **移動する物** | **毎フレーム、動いた位置に描く**（**航跡**）。**速さに比例して強く** |
| **水中の物の深度** | **物を上から描いて**、**水面と交わる部分を書き込む** |
| **雨粒** | **ランダムな位置に小さな点**を**描く** |

```hlsl
float2 uv = (world_position.xz - sim_origin) / sim_size;
float distance_to_brush = length(pixel_uv - brush_uv);
float brush = saturate(1.0 - distance_to_brush / brush_radius);
brush = brush * brush * (3.0 - 2.0 * brush);
height_next[p] += brush * brush_strength;
```

| 点 | 説明 |
| --- | --- |
| **滑らかな減衰** | **`smoothstep` 風**にして、**縁を尖らせない** |
| **強さ** | **負なら凹む**（**物が沈む**）、**正なら盛り上がる** |
| **加算** | **既にある波に足す** |

## 高さマップを水面に反映する

**シミュレーションの高さを、水面に反映**します。

| 反映先 | 内容 |
| --- | --- |
| **頂点の高さ** | **頂点シェーダーで高さマップを読み**、**波の高さに足す** |
| **法線** | **高さマップの勾配**から**法線**を作り、**波の法線に足す**（**細かい凹凸が見える**） |

```hlsl
float2 texel = 1.0 / sim_size;
float hl = ripple_map.Sample(linear_clamp, uv - float2(texel.x, 0)).r;
float hr = ripple_map.Sample(linear_clamp, uv + float2(texel.x, 0)).r;
float hd = ripple_map.Sample(linear_clamp, uv - float2(0, texel.y)).r;
float hu = ripple_map.Sample(linear_clamp, uv + float2(0, texel.y)).r;

float3 ripple_normal = normalize(float3((hl - hr) * normal_strength, 2.0 * texel_world, (hd - hu) * normal_strength));
```

| 点 | 説明 |
| --- | --- |
| **中心差分** | **左右・上下の差**が**勾配** |
| **`normal_strength`** | **大きいほど、凹凸がはっきり** |
| **合成** | **波の法線の XZ に波紋の XZ を足して正規化** |

## シミュレーション領域

**水面全体を高解像度でシミュレーションするのは、重すぎます**。**カメラ周りの狭い領域だけ**を**対象にします**。

| 工夫 | 内容 |
| --- | --- |
| **カメラ追従** | **領域の中心をカメラの近くに置く** |
| **ずれの処理** | **領域が動くとき、テクセル単位で動かして、高さを読み替える**（**波がずれない**ように**ワールド座標をテクセルに揃える**） |
| **解像度** | **512×512 を、20〜30 m 四方**など。**1 テクセル 5 cm 程度** |
| **端でフェード** | **領域の端で高さを 0 に近づける**（**切れ目が見えない**） |

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

## 浮力と水への反作用

**水面と物の相互作用は、見た目だけでなく、物理にも影響します**。

| 要素 | 内容 |
| --- | --- |
| **浮力** | **水に浸かった体積に比例**（[波のジオメトリ](waves.md)） |
| **抵抗** | **水中を動く物は、速さに比例して減速** |
| **波紋の起点** | **物理エンジンの接触・速度から、ブラシの強さを決める** |

## よくあるミス

??? failure "波紋が発散して、画面が真っ白になる"
    **`wave_speed_squared` を 0.5 以下に抑え**、**`damping` を 1 未満にする**。

??? failure "領域を動かしたとき、波紋が滑って見える"
    **領域の移動をテクセル単位に丸め**、**高さを読み替えて**、**ワールドに固定する**。

??? failure "フローマップのテクスチャが、時間とともに引き伸ばされる"
    **`frac` で周期的に戻し**、**位相をずらした 2 つをブレンドする**。

??? failure "波紋の法線が、強すぎて泡立つ"
    **`normal_strength` を下げる**。**高さに上限をかける**。

??? failure "領域の端で、波紋が途切れる"
    **端で高さをフェード**し、**領域をカメラ追従にする**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 波紋 ＝ <strong>高さマップを波動方程式で更新</strong>。<strong>今・前・次の 3 枚を回す</strong>
    - [x] <strong>新しい高さ ＝ 2h − 前 ＋ c²·ラプラシアン</strong>、<strong>減衰を掛ける</strong>。<strong>c² を大きくしすぎると発散</strong>
    - [x] <strong>物の接触は、ブラシで高さに書き込む</strong>
    - [x] <strong>高さの勾配 ＝ 法線</strong>。<strong>波の法線に足す</strong>
    - [x] <strong>川はフローマップ</strong>：<strong>位相をずらした 2 つの法線マップをブレンド</strong>

## 参考

- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010、フローマップ）
- Hugo Elias, "Water Ripples"（2D 波紋の古典的な解説）
- Jensen & Golias, "Deep-Water Animation and Rendering"（Gamasutra 2001）

## 関連ページ

- [水](index.md)
- [波のジオメトリ](waves.md)
- [岸辺と泡](shore-foam.md)
- [水中の表現](underwater.md)
