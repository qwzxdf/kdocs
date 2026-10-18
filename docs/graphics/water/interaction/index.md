---
title: Water Interaction
tags:
  - 描画
---

# Water Interaction

<strong>物が水に入ると波紋が広がり、水が流れ物が浮きます</strong>。<strong>波の高さをシミュレーションし、水面に反映する</strong>ことでインタラクティブな水ができます。このセクションでは波動方程式・物の接触の書き込み・高さマップの反映・フローマップ・浮力を、1 つずつ別のページで説明します。

## 波動方程式
<strong>水面の高さ `h(x, y, t)` は波動方程式に従います</strong>。

<div class="formula">∂²h/∂t² = c² · ∇²h　（c：波の速さ、∇²：ラプラシアン）</div>

<strong>グリッド上で差分にすると次の更新式</strong>になります。

<div class="formula">h_new = 2 · h − h_prev + c²·Δt² · (h_left + h_right + h_up + h_down − 4h)</div>

| 記号 | 意味 |
| --- | --- |
| h | 今のフレームの高さ |
| h_prev | 1 つ前のフレームの高さ |
| h_new | 次のフレームの高さ |
| <strong>(h_left + … − 4h)</strong> | 上下左右の平均との差（ラプラシアン）。周りより高い所は下がる |

<strong>周囲より高ければ下がり低ければ上がる</strong>ので<strong>振動して波が広がります</strong>。そのままだと永遠に揺れるので、毎回少し減衰させます。

```hlsl
Texture2D<float> height_now : register(t0);
Texture2D<float> height_prev : register(t1);
RWTexture2D<float> height_next : register(u0);
```

波の方程式を数値的に解く計算シェーダーです。今の高さ 1 つ前の高さ次の高さの、3 枚を使い毎フレーム、入れ替えて回します。

```hlsl
cbuffer WaveParams : register(b0) {
  float wave_speed_squared;
  float damping;
  uint2 size;
};
```

波の速さの 2 乗と減衰を定数で、与えます。波の速さは格子の間隔と時間刻みから決まり、大きすぎると計算が発散します。

```hlsl
[numthreads(8, 8, 1)]
void CSMain(uint3 id : SV_DispatchThreadID) {
  if (id.x >= size.x || id.y >= size.y) return;

  int2 p = int2(id.xy);
  float h = height_now[p];
  float left = height_now[clamp(p + int2(-1, 0), 0, int2(size) - 1)];
  float right = height_now[clamp(p + int2(1, 0), 0, int2(size) - 1)];
  float up = height_now[clamp(p + int2(0, -1), 0, int2(size) - 1)];
  float down = height_now[clamp(p + int2(0, 1), 0, int2(size) - 1)];
```

今の高さと上下左右の 4 点の高さを、読みます。端は `clamp` で外側を端と同じ値にして、はみ出しを防ぎます。

```hlsl
  float laplacian = left + right + up + down - 4.0 * h;
  float next = 2.0 * h - height_prev[p] + wave_speed_squared * laplacian;
  height_next[p] = next * damping;
}
```

| 点 | 説明 |
| --- | --- |
| 3 枚をローテーション | 今・前・次を毎フレーム入れ替える（`prev ← now ← next`） |
| `wave_speed_squared` | `c²·Δt²/Δx²`。0.5 を超えると不安定で発散（CFL 条件） |
| `damping` | 0.98〜0.995。小さいほど早く静まる |
| 端の処理 | `clamp` で端を繰り返すと反射する。端で減衰を強くすると吸収される |

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

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Writing Object Contacts](contact.md) | 水に入った物が、波を起こす |
| [Applying a Height Map to the Surface](apply-height.md) | 波紋を、水面の形にする |
| [Flow Maps](flow-map.md) | 水の流れの表現 |
| [Buoyancy and Reaction](buoyancy.md) | 物が浮く・水を押す |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 高さマップで波紋を、フローマップで流れを

## 参考

- Müller, "Fast Water Simulation for Games Using Height Fields", Game Developers Conference 2008（高さ場の波動方程式による水面）
- Tessendorf, "Interactive Water Surfaces", Game Programming Gems 4, 2004（高さ場の波紋の、シミュレーション）
- Vlachos, "Water Flow in Portal 2", SIGGRAPH 2010, Advances in Real-Time Rendering in 3D Graphics and Games（フロー マップと、2 位相の繰り返し）
- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015

## 関連ページ

- [Water](../index.md)
- [Shore Foam](../shore-foam/index.md)
- [Water Waves](../waves/index.md)
