---
title: Writing Object Contacts
tags:
  - 描画
---

# Writing Object Contacts

水に石を投げると落ちた所から輪になって波が広がります。高さマップで水面を動かしている場合、この波は物が水に触れた場所に高さを書き込むとそこが起点になって自然に広がります。物の位置を水面のシミュレーションへ伝える部分が、このページの内容です。

<strong>物が水に触れた所を高さマップに「押し込み」として書き込みます</strong>。点で押すブラシ、物の形で押す方法、速度を描く方法、水に入る瞬間の扱い書き込みの安定性を説明します。

!!! tip "ポイント"
    - 物の位置と大きさを丸いブラシにして、高さマップへ足します。
    - 強さは水面を貫く速さと大きさに比例させます。
    - 水面との高さを比べて、水に入った部分だけを書きます。
    - 細長い物は上から見下ろして、水面下の深さを描くと形どおりの波が出ます。
    - 強すぎるブラシを毎フレーム置くと水面が爆発的に盛り上がります。上限を設けます。

!!! info "このページを読む前に"
    - [Water Interaction](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 何を書き込むか {#what}

接触の書き込みには次の 4 つの種類があります。

- ブラシは位置に丸い凹みを描き込みます。キャラクターの足や落ちた物に使います。
- 移動する物は毎フレーム、動いた位置に描きます。航跡ができて速さに比例して強くなります。
- 水中の物の深度は物を上から描いて、水面と交わる部分を書き込みます。細長い物に向きます。
- 雨粒はランダムな位置に小さな点を描きます。

書き込み先は高さマップの「次のフレーム」のテクスチャで、既にある波に足します（加算）。強さが負なら凹み（物が水面を押し下げる）、正なら盛り上がりです（[Applying a Height Map to the Surface](apply-height.md)）。

## 方法 1: ブラシ {#brush}

動いている物と水面の交点に円形の押し込みを 1 つずつ描きます。縁を尖らせると高さの不連続がシミュレーションで高周波のノイズになるので、縁を滑らかに落とします。

<svg class="fig flow" viewBox="0 0 720 240" role="img" aria-label="ブラシの断面。縁がなめらかに 0 へ落ちる曲線と、尖った曲線の比較"><text x="14" y="22" class="fig-title">ブラシの断面（中心から縁まで）</text>
<line x1="60" y1="190" x2="660" y2="190" stroke="currentColor" stroke-width="1.5"/><line x1="360" y1="190" x2="360" y2="50" stroke="#94a3b8" stroke-dasharray="4 4"/>
<text x="360" y="212" text-anchor="middle" style="font-size:12px">中心</text><text x="640" y="212" text-anchor="middle" style="font-size:12px">縁（半径）</text>
<path d="M360,60 L640,190" fill="none" stroke="#e5484d" stroke-width="3" stroke-dasharray="6 4"/><text x="540" y="104" style="font-size:12px;fill:#e5484d;font-weight:600">線形: 縁と中心で折れる</text>
<path d="M360,60 C440,62 540,120 640,190" fill="none" stroke="#4c8bf5" stroke-width="3.5"/><text x="470" y="170" style="font-size:12px;fill:#4c8bf5;font-weight:600">saturate(1 − d)² : 縁がなめらか</text>
<text x="360" y="232" text-anchor="middle" style="font-size:12px">d = 中心からの距離 ÷ 半径。左右は対称（右半分だけ示した）</text></svg>

C++ 側で物ごとに押し込みの量を決めます。水面の近くにある物だけを対象にして、水面を下へ貫く速さに比例させます。

```cpp
// （コンパイルしていない）
struct WaterImpulse {
  DirectX::XMFLOAT2 position;   // 水面上の位置（ワールド XZ）
  float radius;                 // 影響の半径（物の大きさ）
  float strength;               // 押す強さ（負で押し下げ、正で持ち上げ）
};

std::vector<WaterImpulse> impulses;
for (const Body& b : bodies) {
  const float dist_to_surface = b.position.y - WaterHeightAt(b.position.x, b.position.z);
  if (std::abs(dist_to_surface) > b.radius) continue;       // 水面から離れている
  // 水面を下向きに突いている速さに比例して、強さを決める
  const float v_down = std::max(-b.velocity.y, 0.0f);
  impulses.push_back({{b.position.x, b.position.z}, b.radius, -(0.1f + v_down * 0.05f)});
}
```

強さの `0.1` は速さが 0 でも浮いている物が弱く水面を押すための下駄で、`0.05` は速さへの係数です。値は一例でシミュレーションのスケールに合わせて調整します。

計算シェーダーで全ブラシを全画素に足します。

```hlsl
struct WaterImpulse {
  float2 position;
  float radius;
  float strength;
};
StructuredBuffer<WaterImpulse> g_impulses : register(t2);
RWTexture2D<float> g_h_next : register(u0);       // 次のフレームの高さ

cbuffer SimConstants : register(b0) {
  float2 g_origin;           // シミュレーション窓の左下（ワールド XZ）
  float g_texel_size;        // 1 テクセルのメートル数
  uint g_impulse_count;
  uint2 g_sim_size;
  uint2 _pad;
};

[numthreads(8, 8, 1)]
void ApplyImpulsesCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_sim_size)) return;
  float2 world_xz = g_origin + (float2(id.xy) + 0.5) * g_texel_size;   // テクセルの中心
  float add = 0.0;
  for (uint i = 0; i < g_impulse_count; ++i) {
    float d = distance(world_xz, g_impulses[i].position) / g_impulses[i].radius;
    float k = saturate(1.0 - d);
    add += g_impulses[i].strength * k * k;          // 縁をなめらかに（2 乗）
  }
  g_h_next[id.xy] += add;
}
```

数字で確かめます。シミュレーションが 512 × 512 で、ブラシが 100 個なら全画素が全ブラシを調べるので、`512 × 512 × 100 ≒ 2600 万回` の距離計算です。多くの画素はどのブラシの半径にも入らないので、無駄が大きくなります。ブラシの数が増えるならブラシごとに小さな四角形を描いて、加算ブレンドで書き込む方が軽くなります。

```hlsl
struct BrushVsOut {
  float4 pos : SV_Position;
  float2 local : TEXCOORD0;      // -1..1。四角形の中の位置
  float strength : TEXCOORD1;
};

cbuffer BrushRasterConstants : register(b1) {
  float2 g_sim_origin;
  float2 g_sim_extent;           // シミュレーション窓の大きさ（メートル）
};

// 1 ブラシ = 1 インスタンス、4 頂点のストリップ。水面の高さ用レンダー ターゲットへ加算ブレンドで描く
BrushVsOut BrushVS(uint vertex_id : SV_VertexID, uint instance_id : SV_InstanceID) {
  WaterImpulse imp = g_impulses[instance_id];
  float2 corner = float2(vertex_id & 1, vertex_id >> 1) * 2.0 - 1.0;
  float2 world_xz = imp.position + corner * imp.radius;
  float2 uv = (world_xz - g_sim_origin) / g_sim_extent;

  BrushVsOut o;
  o.pos = float4(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0, 0.0, 1.0);
  o.local = corner;
  o.strength = imp.strength;
  return o;
}

float BrushPS(BrushVsOut i) : SV_Target {
  float k = saturate(1.0 - length(i.local));
  return i.strength * k * k;     // ブレンドは、加算（ONE, ONE）にする
}
```

## 方法 2: 物の形を描く {#shape}

ブラシは円形の点しか表せません。船のような細長い物には物の形そのものを水面に押し当てたいところです。水面の上から見下ろす（正射影の）カメラで、水面の近くにある物だけを描いて、水面をどれだけ貫いているかを画像にします。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="上から見下ろす正射影カメラで、船の水面下の深さを画像にする"><defs><marker id="ctA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">船の水面下の形を、上から描く</text>
<line x1="40" y1="130" x2="360" y2="130" stroke="#4c8bf5" stroke-width="3"/><text x="52" y="124" style="font-size:12px">水面</text>
<path d="M130,100 L270,100 L250,172 L150,172 Z" fill="rgba(229,170,40,0.3)" stroke="#e5aa28" stroke-width="2"/><text x="200" y="192" text-anchor="middle" style="font-size:12px">船（水面下の部分だけ使う）</text>
<g stroke="currentColor" stroke-width="2" marker-end="url(#ctA)"><line x1="170" y1="40" x2="170" y2="95"/><line x1="200" y1="40" x2="200" y2="95"/><line x1="230" y1="40" x2="230" y2="95"/></g><text x="200" y="36" text-anchor="middle" style="font-size:12px">正射影カメラ（真下向き）</text>
<line x1="380" y1="110" x2="430" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#ctA)"/>
<rect x="440" y="60" width="240" height="130" rx="9" fill="rgba(148,163,184,0.15)" stroke="#94a3b8"/><path d="M500,120 Q500,95 560,92 L620,120 L560,148 Q500,145 500,120 Z" fill="rgba(76,139,245,0.4)" stroke="#4c8bf5"/>
<text x="560" y="175" text-anchor="middle" style="font-size:12px">押し込み量の画像（水面下の深さ）</text>
<text x="360" y="232" text-anchor="middle" style="font-size:12px">この画像を、高さマップへ「押し込み」として足す。形どおりの波が出る</text></svg>

ピクセル シェーダーで物の水面下の深さを書き出します。

```hlsl
cbuffer InteractionConstants : register(b2) {
  float g_water_height;      // 水面の高さ（ワールド y）
  float g_max_depth;         // 押し込む深さの上限（メートル）。例: 1.0
  float2 _pad2;
};

struct InteractionPsInput {
  float4 position : SV_Position;
  float3 world_position : TEXCOORD0;
  float3 velocity : TEXCOORD1;
};

float4 InteractionPS(InteractionPsInput input) : SV_Target {
  float depth_below = g_water_height - input.world_position.y;   // 水面より下なら正
  if (depth_below <= 0.0) discard;                                 // 水面より上の部分は無視
  // 深すぎる部分は押し込みを頭打ちにする（安定のため。足した処理）
  return float4(min(depth_below, g_max_depth), 0, 0, 1);
}
```

この画像を波のシミュレーションに足す高さとして使います。物の輪郭に沿った波紋が出ます。

ブラシは簡単で数が多い物に向きますが、円形に限られます。細長い物は複数のブラシで近似します。物の形を描く方法は形どおりの波が出て、船の航跡の形が出ます。代償は物をもう一度描くコストです。

## 方法 3: 速度を描く {#velocity}

波の押し込みだけでなく水の流れも水面に伝えたいときは、物の速度ベクトルを別のチャンネルに描きます。この流れの情報は泡の流れや航跡の流れに使えます（[Flow Maps](flow-map.md)）。

```hlsl
float4 InteractionVelocityPS(InteractionPsInput input) : SV_Target {
  float depth_below = g_water_height - input.world_position.y;
  if (depth_below <= 0.0) discard;
  // R = 押し込みの深さ、GB = 水平方向の速度（m/s）
  return float4(min(depth_below, g_max_depth), input.velocity.x, input.velocity.z, 1);
}
```

## 水に入る瞬間 {#splash}

物が水に入った瞬間は強い衝撃です。水に入ったことを検出して 1 回だけ大きな波紋（スプラッシュ）を起こします。

```cpp
// （コンパイルしていない）前のフレームは水面の上、今は下 → 水に入った
if (prev_y > surface_y && cur_y <= surface_y) {
  const float speed = -velocity.y;                          // 下向きの速さ
  impulses.push_back({{b.position.x, b.position.z}, b.radius * 2.0f, -speed * 0.02f});
  SpawnSplashParticles(b.position, speed);                   // 水しぶき（パーティクル）も同時に出す
}
```

波紋とパーティクル（水しぶき）の両方を出すと水に落ちた感じが出ます。入った瞬間の強さは速さに比例させます。速さ 5 m/s の物が `speed * 0.02` で、`−0.1` の押し込みです。1 フレームで 1 回だけ置くので、毎フレーム置く常時のブラシより強くしても安全です。

!!! note "確かめた範囲"
    HLSL は `fxc` で、`ApplyImpulsesCS`（`cs_5_0`）、`BrushVS`（`vs_5_0`）、`BrushPS`・`InteractionPS`・`InteractionVelocityPS`（`ps_5_0`）をコンパイルして、エラーが出ないことを確かめました。C++ はコンパイルしていません。数字は式からの手計算です。GPU での描画は確認していません。

## 安定性と注意点 {#stability}

- 常時の接触は浮いている物が水面を常に少し押しているので、弱いブラシを毎フレーム置きます。強すぎると水面が荒れます。
- 同じ位置に強いブラシを毎フレーム置くと水面が爆発的に盛り上がります。1 フレームの押し込みに上限を設けて、`clamp` します。
- シミュレーションの窓（カメラの周り）の外にある物は、無視します。
- 遠くの物の波紋は見えないので、距離で省きます。

## よくあるミス {#mistakes}

??? failure "物が水に入っても、波紋が出ない"
    原因は接触位置を高さマップに書き込んでいないことです。物の位置と大きさから押し込みを作って、次のフレームの高さに足します。ワールド座標とシミュレーションの座標の変換（原点と大きさ）が合っているかも確認します。

??? failure "水面が爆発的に盛り上がって、荒れる"
    原因は強いブラシを毎フレーム同じ位置に置き続けて、高さが累積することです。押し込みの上限を決めて常時の接触は弱くします。

??? failure "ブラシの縁にリング状のノイズが出る"
    原因はブラシの縁が尖っていて、高さが不連続なことです。縁を `saturate(1 − d)²` のようになめらかに落とします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 物の位置と大きさをなめらかなブラシにして、高さマップへ足します。
    - [x] 強さは水面を貫く速さと大きさに比例させます。
    - [x] 細長い物は上から水面下の深さを描いて、形どおりに押し込みます。
    - [x] 毎フレームの押し込みには上限を設けます。

## 参考 {#references}

このページは次の資料を読まずに書きました。強さの係数は一例でシミュレーションのスケールに合わせて決めます。

- Müller, "Fast Water Simulation for Games Using Height Fields", Game Developers Conference 2008（高さ場の波動方程式による水面）
- Tessendorf, "Interactive Water Surfaces", Game Programming Gems 4, 2004（高さ場の波紋のシミュレーション）
- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015
- Microsoft Learn, "ID3D11DeviceContext::CSSetUnorderedAccessViews"

## 関連ページ

- [Water Interaction](index.md)
- [Applying a Height Map to the Surface](apply-height.md)
