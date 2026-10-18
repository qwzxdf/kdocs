---
title: Writing Object Contacts
tags:
  - 描画
---

# Writing Object Contacts

**物が水に触れた所を、高さマップに「押し込み」として書き込む**と、**そこから波紋が広がります**。このページでは、**接触の書き込み方**を説明します。

!!! tip "ポイント"
    - **物の位置・大きさを、高さマップにスタンプ**する。
    - **動く速さに応じて、強さを変える**。
    - **水面の高さと比べて、水に入った部分だけ書く**。
    - **書き込みは、シミュレーション用のテクスチャへ**。

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

コードの要点です。滑らかな減衰は `smoothstep` 風にして、縁を尖らせません。強さは、負なら凹み（物が沈む）、正なら盛り上がりです。既にある波に足します（加算）。

## 物の接触を、水面に、伝える

物が、水に触れたことを、水面に、**波紋として、反映**するには、**触れた位置と、強さを、シミュレーションに、書き込みます**（[Applying a Height Map to the Surface](apply-height.md)）。

## 方法 1：ブラシ（位置ごとに、描く）

動いている物の、**水面との交点**に、**ブラシ**（円形の、押し込み）を、1 つずつ、描き込みます。

```cpp
struct WaterImpulse {
  float2 position;      // 水面上の位置（ワールド XZ）
  float radius;         // 影響の半径（物の大きさ）
  float strength;       // 押す強さ（負で、押し下げ。正で、持ち上げ）
};

// 各物体について、水面の近くにあるものだけ、ブラシを積む。
std::vector<WaterImpulse> impulses;
for (const Body& b : bodies) {
  const float dist_to_surface = b.position.y - WaterHeightAt(b.position.xz);
  if (std::abs(dist_to_surface) > b.radius) continue;         // 水面から、離れている
  // 水面を、下向きに突いている速さに比例して、強さを決める。
  const float v_down = std::max(-b.velocity.y, 0.0f);
  impulses.push_back({b.position.xz, b.radius, -(0.1f + v_down * 0.05f)});
}
```

```hlsl
// 計算シェーダー: ブラシを、高さマップに足す。
StructuredBuffer<WaterImpulse> g_impulses : register(t2);

[numthreads(8, 8, 1)]
void ApplyImpulses(uint3 id : SV_DispatchThreadID) {
  float2 world_xz = g_origin + (float2(id.xy) + 0.5) * g_texel_size;
  float add = 0.0;
  for (uint i = 0; i < g_impulse_count; ++i) {
    float d = distance(world_xz, g_impulses[i].position) / g_impulses[i].radius;
    add += g_impulses[i].strength * saturate(1.0 - d) * saturate(1.0 - d);   // 縁をなめらかに（2 乗）
  }
  g_h_next[id.xy] += add;
}
```

| 項目 | 内容 |
| --- | --- |
| 数 | ブラシの数が多い（数百）と、全画素が、全ブラシを調べるのは、重い。**ブラシごとに、四角形を描く**（ラスタライズ）方式が、効率的 |
| 強さ | 物の、**水面を貫く速さ**と、**大きさ**に比例させる |
| 向き | 押し下げると、周りが、盛り上がって、波が、広がる |

## 方法 2：物の形を、描く（深度から）

ブラシでは、**円形の、点**しか、表せません。**船のような、細長い、物**には、**物の形そのもの**を、水面に、押し当てたいです。**水面の上から見下ろす（正射影）**カメラで、**水面の近くにある物だけ**を、描いて、**どれだけ、水面を、貫いているか**を、画像にします。

```text
 上から見下ろす、正射影のカメラ
         ↓ ↓ ↓
      ┌───────┐
   ━━━┤ 船の底 ├━━━ 水面
      └───────┘
 深度を調べる → 水面より、下にある部分の、深さ = 押し下げる量
```

```hlsl
// ピクセル シェーダー: 物の、水面より下の深さを、書き出す。
float4 InteractionPS(PSInput input) : SV_Target {
  float depth_below = water_height - input.world_position.y;      // 水面より、下なら、正
  if (depth_below <= 0.0) discard;                                  // 水面より上の部分は、無視
  return float4(depth_below, 0, 0, 1);
}
```

この画像を、波のシミュレーションに、**押し込む高さ**として、足します。**物の、輪郭に沿った、波紋**が、出ます。

| 方式 | 長所 | 短所 |
| --- | --- | --- |
| ブラシ | 簡単。数が多い物に向く | 円形のみ。細長い物は、複数のブラシで、近似 |
| 物の形を描く | **形どおり**の波。船の、航跡の形が、出る | 物を、もう一度描く。コストが、増える |

## 方法 3：速度を、描く

波の、**押し込み**だけでなく、**水の、動き（流れ）**も、水面に、伝えたいときは、物の、**速度ベクトル**を、**別のチャンネル**に、描きます。この流れの情報は、**泡の流れ**、**航跡の、流れ**に、使えます（[Flow Maps](flow-map.md)）。

```hlsl
// 物の、水平方向の速度を、書き出す（RG チャンネル）。
return float4(depth_below, velocity.x, velocity.z, 1);
```

## 水に入る、瞬間

物が、水に入った瞬間は、**強い衝撃**です。**水に入った**ことを、検出して、**1 回だけ**、大きな波紋（スプラッシュ）を、起こします。

```cpp
// 前のフレームは、水面の上、今は、下 → 水に入った。
if (prev_y > surface_y && cur_y <= surface_y) {
  const float speed = -velocity.y;                       // 水に入る、下向きの速さ
  impulses.push_back({b.position.xz, b.radius * 2.0f, -speed * 0.02f});
  SpawnSplashParticles(b.position, speed);                // 水しぶき（パーティクル）も、同時に出す
}
```

**波紋と、パーティクル（水しぶき）の、両方**を、出すと、水に落ちた、感じが、出ます。

## 注意点

| 項目 | 内容 |
| --- | --- |
| 常時の、接触 | 浮いている物は、**水面を、常に、少し、押している**。弱いブラシを、毎フレーム、置く（強すぎると、水面が、荒れる） |
| 発振 | 同じ位置に、強いブラシを、毎フレーム、置くと、**水面が、爆発的に盛り上がる**。上限を設ける |
| 窓の外 | シミュレーションの窓（カメラの周り）の外にある物は、**無視**する |
| 遠くの物 | 遠くの物の波紋は、見えない。**距離で、省く** |

## よくあるミス

??? failure "物が水に入っても、波紋が出ない"
    **接触位置を、高さマップに書き込む**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **接触を、高さマップに書く**

## 参考

- Müller, "Fast Water Simulation for Games Using Height Fields", Game Developers Conference 2008（高さ場の波動方程式による水面）
- Tessendorf, "Interactive Water Surfaces", Game Programming Gems 4, 2004（高さ場の、波紋の、シミュレーション）
- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015
- Microsoft Learn, "ID3D11DeviceContext::CSSetUnorderedAccessViews"

## 関連ページ

- [Water Interaction](index.md)
- [Applying a Height Map to the Surface](apply-height.md)
