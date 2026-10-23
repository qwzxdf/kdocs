---
title: Writing Object Contacts
tags:
  - 描画
---

# Writing Object Contacts

<strong>物が水に触れた所を高さマップに「押し込み」として書き込む</strong>と、そこから波紋が広がります。このページでは接触の書き込み方を説明します。

!!! tip "ポイント"
    - 物の位置・大きさを、高さマップにスタンプする。
    - 動く速さに応じて、強さを変える。
    - 水面の高さと比べて、水に入った部分だけ書く。
    - 書き込みはシミュレーション用のテクスチャへ。

!!! info "このページを読む前に"
    - [Water Interaction](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 物の接触を書き込む
<strong>物が水に触れた所に高さを書き込むと</strong>、そこが波の起点になります。

| 方法 | 内容 |
| --- | --- |
| ブラシ（点） | 位置に丸い凹みを描き込む（キャラクターの足・落ちた物） |
| 移動する物 | 毎フレーム、動いた位置に描く（航跡）。速さに比例して強く |
| 水中の物の深度 | 物を上から描いて、水面と交わる部分を書き込む |
| 雨粒 | ランダムな位置に小さな点を描く |

```hlsl
float2 uv = (world_position.xz - sim_origin) / sim_size;
float distance_to_brush = length(pixel_uv - brush_uv);
float brush = saturate(1.0 - distance_to_brush / brush_radius);
brush = brush * brush * (3.0 - 2.0 * brush);
height_next[p] += brush * brush_strength;
```

コードの要点です。滑らかな減衰は `smoothstep` 風にして、縁を尖らせません。強さは負なら凹み（物が沈む）、正なら盛り上がりです。既にある波に足します（加算）。

## 物の接触を水面に伝える

物が水に触れたことを水面に <strong>波紋として、反映</strong>するには 触れた位置と強さを、シミュレーションに書き込みます（[Applying a Height Map to the Surface](apply-height.md)）。

## 方法 1：ブラシ（位置ごとに描く）

動いている物の <strong>水面との交点</strong>に、ブラシ（円形の押し込み）を、1 つずつ描き込みます。

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
| 数 | ブラシの数が多い（数百）と、全画素が全ブラシを調べるのは重い。ブラシごとに四角形を描く（ラスタライズ）方式が、効率的 |
| 強さ | 物の水面を貫く速さと、大きさに比例させる |
| 向き | 押し下げると周りが、盛り上がって波が広がる |

## 方法 2：物の形を描く（深度から）

ブラシでは <strong>円形の点</strong>しか表せません。船のような細長い物には物の形そのものを水面に、押し当てたいです。水面の上から見下ろす（正射影）カメラで、水面の近くにある物だけを描いて、どれだけ水面を貫いているかを、画像にします。

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

この画像を波のシミュレーションに、押し込む高さとして足します。物の輪郭に沿った波紋が出ます。

| 方式 | 長所 | 短所 |
| --- | --- | --- |
| ブラシ | 簡単。数が多い物に向く | 円形のみ。細長い物は複数のブラシで近似 |
| 物の形を描く | 形どおりの波。船の航跡の形が出る | 物を、もう一度描く。コストが増える |

## 方法 3：速度を描く

波の <strong>押し込み</strong>だけでなく 水の、動き（流れ）も水面に伝えたいときは物の、速度ベクトルを別のチャンネルに、描きます。この流れの情報は泡の流れ航跡の流れに、使えます（[Flow Maps](flow-map.md)）。

```hlsl
// 物の、水平方向の速度を、書き出す（RG チャンネル）。
return float4(depth_below, velocity.x, velocity.z, 1);
```

## 水に入る瞬間

物が水に入った瞬間は <strong>強い衝撃</strong>です。水に入ったことを検出して、1 回だけ大きな波紋（スプラッシュ）を、起こします。

```cpp
// 前のフレームは、水面の上、今は、下 → 水に入った。
if (prev_y > surface_y && cur_y <= surface_y) {
  const float speed = -velocity.y;                       // 水に入る、下向きの速さ
  impulses.push_back({b.position.xz, b.radius * 2.0f, -speed * 0.02f});
  SpawnSplashParticles(b.position, speed);                // 水しぶき（パーティクル）も、同時に出す
}
```

波紋とパーティクル（水しぶき）の、両方を出すと水に落ちた感じが、出ます。

## 注意点

| 項目 | 内容 |
| --- | --- |
| 常時の接触 | 浮いている物は水面を常に少し、押している。弱いブラシを毎フレーム、置く（強すぎると水面が荒れる） |
| 発振 | 同じ位置に強いブラシを、毎フレーム、置くと水面が爆発的に盛り上がる。上限を設ける |
| 窓の外 | シミュレーションの窓（カメラの周り）の外にある物は、無視する |
| 遠くの物 | 遠くの物の波紋は、見えない。距離で省く |

## よくあるミス

??? failure "物が水に入っても、波紋が出ない"
    <strong>接触位置を高さマップに書き込む</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 接触を高さマップに書く

## 参考

- Müller, "Fast Water Simulation for Games Using Height Fields", Game Developers Conference 2008（高さ場の波動方程式による水面）
- Tessendorf, "Interactive Water Surfaces", Game Programming Gems 4, 2004（高さ場の波紋の、シミュレーション）
- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015
- Microsoft Learn, "ID3D11DeviceContext::CSSetUnorderedAccessViews"

## 関連ページ

- [Water Interaction](index.md)
- [Applying a Height Map to the Surface](apply-height.md)
