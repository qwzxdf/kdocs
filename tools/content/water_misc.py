import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

MULLER = '''Müller, "Fast Water Simulation for Games Using Height Fields", Game Developers Conference 2008（高さ場の波動方程式による水面）'''
TESSENDORF_IW = '''Tessendorf, "Interactive Water Surfaces", Game Programming Gems 4, 2004（高さ場の、波紋の、シミュレーション）'''
KERNER = '''Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015'''
VLACHOS = '''Vlachos, "Water Flow in Portal 2", SIGGRAPH 2010, Advances in Real-Time Rendering in 3D Graphics and Games（フロー マップと、2 位相の繰り返し）'''
NEYRET = '''Neyret, "Advected Textures", Symposium on Computer Animation 2003（流れに乗せて、テクスチャを動かす）'''
TESSENDORF = '''Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）'''
JENSEN = '''Jensen, Golias, "Deep-Water Animation and Rendering", Gamasutra, 2001（海の描画。泡、波頭）'''
GUARDADO = '''Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004'''
WALLACE = '''Wallace, "Rendering Realtime Caustics in WebGL", Medium, 2015（屈折した光の、面積の変化から、コースティクスを作る）'''
MITCHELL = '''Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018'''
POPE = '''Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997'''
D3D11_UAV = '''Microsoft Learn, "ID3D11DeviceContext::CSSetUnorderedAccessViews"'''

# ================================================================ interaction
pg.Dedup("water/interaction/apply-height.md")
pg.Add("water/interaction/apply-height.md", '''
## 波紋を、シミュレーションする（波動方程式）

水面に、物が触れたとき、**波紋が、広がる**様子は、**波動方程式**を、**高さ場**（格子の、各点が、高さを持つ）で、解くと、再現できます（Tessendorf、2004、Müller、2008）。

```text
∂²h/∂t² = c² × ∇²h            h: 水面の高さ、c: 波の速さ、∇²h: 周りとの、高さの差（ラプラシアン）
```

「**周りより、高い所は、下がる方向へ、加速し、周りより低い所は、上がる方向へ、加速する**」という意味です。バネが、つながったような動きで、**波が、伝わります**。

## 離散化

格子の各点 `h[x, z]` を、時間ステップ `dt` ごとに、更新します。**今のフレーム**の高さ `h` と、**1 つ前のフレーム**の高さ `h_prev` を持ちます。

```text
laplacian = h[x+1,z] + h[x−1,z] + h[x,z+1] + h[x,z−1] − 4 h[x,z]
h_new = 2 h − h_prev + (c dt / dx)² × laplacian
h_new *= damping            （1 より少し小さい値。波が、だんだん消える）
```

| 値 | 意味 |
| --- | --- |
| `2 h − h_prev` | 速度（前回からの変化）を、そのまま続ける（慣性） |
| `(c dt / dx)² × laplacian` | 周りに、引っ張られる力 |
| `damping` | 0.99〜0.999。小さいほど、波が早く消える |

!!! warning "時間ステップには、上限がある（CFL 条件）"
    `c dt / dx` が、大きすぎると、**計算が、発散**します（波が、爆発的に、大きくなる）。2 次元の格子では、**`c dt / dx ≤ 1/√2 ≈ 0.707`** を守ります。`dx` が小さいほど、`dt` も、小さくする必要があります。**固定の時間ステップ**で、計算するのが、安全です。

## 計算シェーダー

3 つの高さマップ（今、前、次）を、**ローテーション**して使います。

```hlsl
Texture2D<float> g_h : register(t0);              // 現在の高さ
Texture2D<float> g_h_prev : register(t1);         // 1 つ前
RWTexture2D<float> g_h_next : register(u0);       // 次（出力）

cbuffer WaveSimCB : register(b0) {
  float g_wave_coeff;      // (c dt / dx)²（0.5 以下）
  float g_damping;         // 0.995 など
  int g_size;
  float pad;
};

[numthreads(8, 8, 1)]
void Step(uint3 id : SV_DispatchThreadID) {
  int2 p = int2(id.xy);
  float h = g_h[p];
  float lap = g_h[min(p + int2(1, 0), g_size - 1)] + g_h[max(p - int2(1, 0), 0)]
            + g_h[min(p + int2(0, 1), g_size - 1)] + g_h[max(p - int2(0, 1), 0)]
            - 4.0 * h;
  float next = 2.0 * h - g_h_prev[p] + g_wave_coeff * lap;
  g_h_next[p] = next * g_damping;
}
```

```cpp
// 3 枚を、ローテーションして、毎フレーム（または、固定ステップごとに）実行する。
std::swap(h_prev, h);          // h_prev ← 今の h
std::swap(h, h_next);          // h ← 計算した次の h
// （h_next は、次のステップで、上書きされる）
context->CSSetShader(step_cs.Get(), nullptr, 0);
ID3D11ShaderResourceView* srvs[2] = {h_srv.Get(), h_prev_srv.Get()};
context->CSSetShaderResources(0, 2, srvs);
context->CSSetUnorderedAccessViews(0, 1, h_next_uav.GetAddressOf(), nullptr);
context->Dispatch(size / 8, size / 8, 1);
```

読み書きに、**同じテクスチャを、同時に使えない**ので、3 枚を、役割を替えながら使います（今を読み、前を読み、次に書く）。

## 波を起こす（外力）

物が水面に触れたとき、**その位置の高さを、押し下げる（または、持ち上げる）**ことで、波紋を、起こします（[Writing Object Contacts](contact.md)）。

```hlsl
// 物が、水面を押した位置に、高さを足す（ブラシ）。
float d = distance(float2(id.xy), impact_pos);
float push = impact_strength * saturate(1.0 - d / impact_radius);
g_h_next[id.xy] += push;
```

## 水面メッシュに、適用する

シミュレーションの結果（高さマップ）を、**水面の頂点の高さに、足し込み**ます。

```hlsl
// 頂点シェーダー: 通常の波（FFT、Gerstner）に、波紋の高さを、足す。
float2 interaction_uv = (world_xz - g_interaction_origin) / g_interaction_size;
float ripple = g_ripple_height.SampleLevel(g_linear_clamp, interaction_uv, 0);
// 範囲の端では、波紋の影響を、0 にする（窓の外へ、波紋が、はみ出さないよう）
float edge_fade = 1.0 - saturate(max(abs(interaction_uv.x - 0.5), abs(interaction_uv.y - 0.5)) * 2.0 - 0.9) * 10.0;
world_pos.y += ripple * edge_fade;
```

**法線**も、波紋の高さから、**差分で**、求めて、水面の法線に、足します（[Computing Normals](../waves/normals.md)、傾きを足し合わせる）。

## 窓を、カメラに合わせる

高さマップは、**プレイヤーの周りの、数十メートル**だけを覆います（256×256 を、50 m に、割り当てて、1 画素 約 20 cm）。カメラが動くと、窓も動き、**中身を、ずらす**必要があります。**円環バッファ**（`WRAP`）を使うと、コピーなしで、窓を動かせます（[Trampled Grass](../../terrain/vegetation/trample.md) と、同じ考え方）。窓が動いたとき、**新しく、範囲に入った帯**は、**0 にクリア**します。

## 性能と、品質

| 項目 | 内容 |
| --- | --- |
| 解像度 | 256×256〜512×512。**1 画素 10〜20 cm** が、波紋の細かさの、限界 |
| 計算量 | 1 ステップ、数万〜数十万画素。GPU では、**0.05 ms** 程度 |
| 波の速さ | `c` を小さくすると、波紋が、**ゆっくり**広がる。見た目で調整 |
| 減衰 | 小さい波紋は、**すぐ消える**ように、`damping` を小さめにする |
| 反射 | 窓の端で、波が、**跳ね返る**。端で、減衰を、強くして、吸収する（スポンジ層） |

''', before="## よくあるミス")
pg.Refs("water/interaction/apply-height.md", [MULLER, TESSENDORF_IW, "Courant, Friedrichs, Lewy, \"Über die partiellen Differenzengleichungen der mathematischen Physik\", Mathematische Annalen, Vol. 100, 1928（CFL 条件の原典）"])

pg.Dedup("water/interaction/buoyancy.md")
pg.Add("water/interaction/buoyancy.md", '''
## 浮力と、反作用

水と物の、相互作用は、**2 方向**です。

| 方向 | 内容 |
| --- | --- |
| 水 → 物 | **浮力**、**抵抗**、**波に押される**力。物の動きを、決める |
| 物 → 水 | **押しのけた水が、波になる**。波紋、航跡、しぶき。水面の見た目を、変える |

## 浮力の物理

**アルキメデスの原理**：**物が押しのけた水の重さ**だけ、**上向きの力**を受けます。

```text
F_buoyancy = ρ × g × V_submerged             ρ: 水の密度（1000 kg/m³）、V: 水に沈んでいる体積
```

| 状況 | 浮力 | 結果 |
| --- | --- | --- |
| 沈んでいる体積が、小さい | 小さい | 物が、重力で、沈む |
| 沈んでいる体積が、増える | 増える | **重力と、釣り合う深さで、止まる**（浮く） |
| 完全に沈んだ | 最大（`ρ g V`） | 物の重さが、これより軽ければ、浮き上がる |

浮力が、**重力と、釣り合う**喫水（沈む深さ）が、**自然に、浮く高さ**です。物の密度が、水より小さいと、**一部が、水面の上に、出て浮きます**。

## 実装：沈んだ体積を、近似する

正確な、沈んだ体積の計算は、**水面の高さと、物の形状の、交差**が、必要で、重いです。実用的な、近似を、示します。

### ① 点サンプリング（簡単）

物の、複数の点（浮力点）で、水面の高さを調べ、**各点が、受け持つ体積の、沈んだ割合**を、浮力に変えます（[Floating Objects](../waves/floating.md)）。

### ② 箱で、近似

物を、**箱**とみなして、**水面と箱の、交差から、沈んだ体積**を、求めます。

```cpp
// 箱（軸に沿った、水平な箱とみなす）の、沈んだ高さから、体積を求める。
float SubmergedVolume(float box_bottom_y, float box_height, float width, float depth, float water_y) {
  const float submerged_h = std::clamp(water_y - box_bottom_y, 0.0f, box_height);
  return submerged_h * width * depth;
}
```

波の高さが、**箱の下で、均一でない**ので、箱を、**水平方向に、いくつかのマスに分けて**、マスごとに、水面の高さを調べると、**傾いた、水面**にも、対応できます。

### ③ 三角形ごと（Kerner の方法）

船体を、**三角形のメッシュ**として、扱います。**水面の下にある三角形**を、すべて集め、各三角形に、次の力を、かけます。

| 力 | 計算 |
| --- | --- |
| 静水圧（浮力） | `ρ g × (水面からの深さ) × 面積 × (−法線)`。**深い所ほど、強く、法線の向きに**押す |
| 粘性抵抗 | 三角形の位置での、**水に対する相対速度**に比例した、摩擦 |
| 圧力抗力 | 進行方向を向く、三角形が、水を押しのける力 |
| スラミング | 面が、水面へ、**勢いよく入った**ときの、衝撃 |

三角形ごとの、静水圧を、足し合わせると、**浮力と、船体の傾きを、戻そうとする力（復元力）**が、**自然に**出ます。点サンプリングより、重いですが、**船の揺れが、はるかに、もっともらしく**なります（Kerner、2015）。

## 抵抗で、安定させる

浮力だけだと、物は、**上下に、跳ね続けます**。**抵抗**（速度に比例して、動きを遅くする力）を、加えて、**揺れを、収束**させます。

```cpp
// 水の中の物には、速度に比例した、抵抗をかける。沈んでいる割合に応じて、強くする。
float3 drag = -body.velocity * linear_drag * submerged_ratio;
float3 angular_drag = -body.angular_velocity * angular_drag_coeff * submerged_ratio;
body.ApplyForce(drag);
body.ApplyTorque(angular_drag);
```

| 抵抗 | 効果 |
| --- | --- |
| 小さい | いつまでも、ゆらゆら揺れる |
| 大きい | **すぐに、止まる**。重たい、動きにくい物に見える |

## 水面に、反作用を返す

物が、水を押しのけると、**波**が出ます。物の、**速さと、水面への、侵入量**に、応じて、波紋を、起こします（[Writing Object Contacts](contact.md)）。

| 状況 | 起こす波 |
| --- | --- |
| 物が、水面に、落ちる | 落ちた位置に、**強い、1 回の波紋**（スプラッシュ） |
| 物が、水面を、進む | 進む軌跡に、**連続した、弱い波紋**（航跡） |
| 物が、浮いて、揺れる | 揺れの、強さに応じた、**小さな波紋** |

## 注意点

| 項目 | 内容 |
| --- | --- |
| 物理エンジンとの、連携 | 浮力は、**物理エンジンの、外力**として、毎ステップ、かける（`ApplyForceAtPoint`） |
| 固定ステップ | 浮力の計算は、**物理の固定ステップ**で、行う。フレームレートに、依存させない |
| 水面の高さの、取得 | GPU と、同じ波の式。時間を、そろえる（[Floating Objects](../waves/floating.md)） |
| 発振 | 浮力が、強い、質量が、軽い、ステップが、粗いと、物理が、**不安定**になる。抵抗で、抑える |
| 水の、流れ | 川では、**流れの速度**を、水の速度として、相対速度に使う。物が、流される |

''', before="## よくあるミス")
pg.Refs("water/interaction/buoyancy.md", [KERNER, MULLER, TESSENDORF, "Catto, \"Understanding Constraints\" など、Box2D / 物理エンジンの、固定ステップのドキュメント"])

pg.Dedup("water/interaction/contact.md")
pg.Add("water/interaction/contact.md", '''
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

''', before="## よくあるミス")
pg.Refs("water/interaction/contact.md", [MULLER, TESSENDORF_IW, KERNER, D3D11_UAV])

pg.Dedup("water/interaction/flow-map.md")
pg.Add("water/interaction/flow-map.md", '''
## フロー マップとは

川、滝、水路では、水が、**一定の方向に、流れます**。法線マップを、一方向に、スクロールさせるだけでは、**水面が、全体として、一定の向きに、滑る**ように見えます。実際の川は、**場所ごとに、流れの向きと速さが、違い**ます（岩の周りで、曲がる、渦を巻く）。

**フロー マップ**は、**水面の、各位置の、流れの向きと速さを、記録したテクスチャ**です。水面の、法線や、泡を、そのベクトルに沿って、**動かし**ます。

| チャンネル | 内容 |
| --- | --- |
| R | 流れの x 成分（0〜1 → −1〜1） |
| G | 流れの z 成分（0〜1 → −1〜1） |
| B（任意） | 流れの速さ、または、泡の量 |

```hlsl
// フロー マップから、流れの向きと速さを読む（0〜1 を、−1〜1 にする）。
float2 flow = g_flow_map.Sample(g_linear_clamp, flow_uv).xy * 2.0 - 1.0;
```

## 単純に、流すと、どうなるか

UV を、**時間に、比例して、流れの向きに、ずらす**と、模様が、**流れて見えます**。

```hlsl
float2 uv = world_uv - flow * time * speed;      // 流れの向きに、時間とともに、動かす
float3 n = g_normal_map.Sample(g_linear_wrap, uv).xyz;
```

しかし、これには、**問題**があります。流れの向きが、**場所ごとに違う**ので、**時間が経つと、UV が、場所ごとに、違う量だけ、ずれて、模様が、引き伸ばされ、ねじれ**ます。

```text
時刻 0:   ▒▒▒▒▒▒▒▒  きれいな模様
時刻 5:   ▒▒░░▒▒░░  場所ごとに、ずれて、引き伸ばされる
時刻 20:  ░░░░░░░░  模様が、ほとんど、線になる
```

## 2 つの位相を、混ぜる（Portal 2 の方法）

Vlachos（2010）は、**この、引き伸ばしを、避ける方法**を、示しています。

1. 時間を、**周期的に**、0 → 1 に、動かす（のこぎり波）。ずらす量が、一定の範囲で、**リセット**される
2. リセットの瞬間は、模様が、**ぱっと、元に戻る**ので、**半周期ずれた、もう 1 つ**を、用意する
3. 2 つを、**交互に、フェード**しながら、混ぜる

```hlsl
// 2 つの位相: 周期 1 のこぎり波を、半周期ずらして、2 つ用意する。
float phase0 = frac(time * flow_speed);
float phase1 = frac(time * flow_speed + 0.5);

// それぞれの位相で、UV をずらして、法線マップを読む。
float2 uv0 = world_uv - flow * phase0 * flow_scale;
float2 uv1 = world_uv - flow * phase1 * flow_scale + 0.5;           // 0.5 は、2 つの模様が、重ならないよう、ずらす
float3 n0 = g_normal_map.Sample(g_linear_wrap, uv0).xyz * 2.0 - 1.0;
float3 n1 = g_normal_map.Sample(g_linear_wrap, uv1).xyz * 2.0 - 1.0;

// 重み: 位相が 0 や 1 に近い（リセット直前直後）ほど小さく、0.5 付近で最大。
float w0 = 1.0 - abs(2.0 * phase0 - 1.0);
float3 n = normalize(lerp(n1, n0, w0));         // w0 が 1 のとき n0、0 のとき n1
```

| 位相 phase0 | w0 | 見えるもの |
| --- | --- | --- |
| 0（リセット直後） | 0 | **n1**（位相 0.5。最大にずれている、安定した状態） |
| 0.5 | 1 | **n0**（位相 0.5） |
| 1（リセット直前） | 0 | n1 |

**リセットの瞬間は、重みが 0 の方の模様**なので、ぱっと、戻っても、**見えません**。

### 模様が、周期的に、脈打つ問題

周期ごとに、2 つの模様が、**入れ替わる**ので、**水面が、一定の周期で、脈打つ**ように、見えることがあります。軽減策は、次のとおりです。

| 対策 | 内容 |
| --- | --- |
| 位相に、ノイズ | 位相に、位置依存の、ノイズを足して、場所ごとに、周期を、ずらす |
| 周期を、長くする | 周期が、長いほど、脈打ちが、ゆっくりで、目立たない（ただし、引き伸ばしが、大きくなる） |
| 3 つの位相 | 3 位相で、重みを混ぜる。より、なめらかになる |

```hlsl
// 位相に、位置依存の、ずれを足して、水面全体が、同時に、脈打たないようにする。
float noise = g_noise.Sample(g_linear_wrap, world_uv * 0.5).r;
float phase0 = frac(time * flow_speed + noise);
float phase1 = frac(time * flow_speed + noise + 0.5);
```

## 流れの速さを、法線マップの、スクロール速度に

流れの**速さ**は、フロー ベクトルの**長さ**で、表します。**速い所**ほど、模様が、速く流れます。流れが、**ゼロ**（静かな所）のとき、模様は、**止まって**見えます。

```hlsl
float speed = length(flow);
// 流れが弱いほど、波も穏やかに（法線の強さを、速さで変える）
float normal_strength = lerp(0.3, 1.0, saturate(speed));
```

## フロー マップの、作り方

| 方法 | 内容 |
| --- | --- |
| 手描き | ブラシで、流れの向きを、描く（専用のツール、または Photoshop の拡張） |
| 地形から計算 | **地形の、高さマップ**から、**水が、流れる向き**（斜面の下り）を、求める。川の、流れを、自動で作る（[Rivers and Lakes](../../terrain/generation/rivers.md) の、D8 法の方向） |
| 流体シミュレーション | 川のシミュレーション（流体の計算）の結果を、焼く |
| 障害物の周りに、曲げる | 岩や、橋脚の周りの、流れを、**回り込む向き**で、描く |

川の、中心線（スプライン）から、**流れの向きを、スプラインの、接線方向**として、作る方法も、あります。川の岸に近いほど、流れを、**遅く**します（岸は、摩擦で、遅い）。

```text
岸に近い所: 流れが遅い（0.2）
川の中央:   流れが速い（1.0）
```

## 泡や、ごみも、流す

水面の上の、**泡**、**木の葉**、**油**など、**水に浮かぶ、模様**も、**同じ、フロー マップで、流せます**（[Persistent Foam](../shore-foam/foam-history.md)）。

| 流す対象 | 方法 |
| --- | --- |
| 泡のテクスチャ | 法線と、同じ、2 位相の、混ぜ合わせ |
| 泡の履歴（蓄積されたもの） | 履歴のテクスチャを、**フロー マップの向きに、毎フレーム、少しずつ、ずらして、書き直す**（移流） |
| 水面に浮く、オブジェクト | 位置を、フロー マップの、向きに、動かす（物理の、外力として） |

## 移流（advection）：テクスチャ自体を、流す

2 位相の方法は、**模様のテクスチャ**を、流す、簡単な方法です。**蓄積した情報（泡の履歴）**を、流すときは、**毎フレーム、流れの向きの、逆向きに、サンプルして**、書き直す方法（**移流**、Neyret 2003 の、考え方の、一部）を使います。

```hlsl
// 前のフレームの泡の量を、流れに沿って動かす（半ラグランジュ法）。
float2 flow = g_flow_map.Sample(g_linear_clamp, uv).xy * 2.0 - 1.0;
float2 prev_uv = uv - flow * flow_scale * dt;               // 流れの上流側から、読む
float foam = g_foam_prev.Sample(g_linear_clamp, prev_uv).r;
```

「自分の位置に、流れてきたのは、**上流の位置にあった、泡**」と考えて、**上流を読む**のが、ポイントです。読み方を、逆にすると、泡が、**逆流**します。

''', before="## よくあるミス")
pg.Refs("water/interaction/flow-map.md", [VLACHOS, NEYRET, "Stam, \"Stable Fluids\", SIGGRAPH 1999（移流（半ラグランジュ法）の、原典）"])
pg.Refs("water/interaction/index.md", [MULLER, TESSENDORF_IW, VLACHOS, KERNER])

# ================================================================ shore foam
pg.Dedup("water/shore-foam/crest-jacobian.md")
pg.Add("water/shore-foam/crest-jacobian.md", '''
## 波頭の、泡は、いつ出るか

海の波は、**波頭が、尖り**、さらに強くなると、**波頭が、砕けて、泡**になります。波が、砕けるのは、**波の、斜面が、急になりすぎたとき**です。**水の粒が、波頭で、集まりすぎて、ぶつかる**とも、言えます。

波の頂点を、水平にも動かす方式（Gerstner 波、FFT 海面）では、**頂点が、集まって、面積が、小さくなった場所**が、砕けそうな場所です。この「**面積の縮み具合**」を、数値にしたものが、**ヤコビアン**です。

## ヤコビアン

各頂点を、動く前の位置 `P₀ = (x₀, z₀)` から、動いた後の位置 `P = P₀ + D(P₀)` へ、移すとします（`D` は、水平の変位）。この写像が、**面積を、どれだけ変えるか**を表すのが、ヤコビアン `J` です。

```text
J = ( 1 + ∂Dx/∂x )( 1 + ∂Dz/∂z ) − ( ∂Dx/∂z )( ∂Dz/∂x )
```

| J の値 | 意味 |
| --- | --- |
| 1 | 面積が、変わらない（頂点の、間隔が、そのまま） |
| 1 より大きい | 面積が、広がる（谷。頂点が、散る） |
| 0 に近づく | 面積が、つぶれる（**波頭。頂点が、集まる**） |
| 負 | 写像が、裏返る（頂点が、追い越して、波頭が、折れている） |

**`J` が、小さい（しきい値より、小さい）場所に、泡を出します**。

```hlsl
// ヤコビアンが、しきい値（たとえば 0.5）より小さい場所を、泡にする。
float foam = saturate((foam_threshold - jacobian) / foam_softness);
```

| パラメーター | 目安 | 効果 |
| --- | --- | --- |
| `foam_threshold` | 0.3〜0.8 | 大きいほど、**多くの場所**に、泡が出る |
| `foam_softness` | 0.1〜0.5 | 大きいほど、泡の縁が、**なだらか** |

## Gerstner 波の、ヤコビアン

Gerstner 波では、水平変位の偏微分が、**解析的**に、求まります（[Gerstner Waves](../waves/gerstner.md)）。

```text
∂Dx/∂x = −Σ Q A ω Dx² sinθ         ∂Dz/∂z = −Σ Q A ω Dz² sinθ
∂Dx/∂z = −Σ Q A ω Dx Dz sinθ      ∂Dz/∂x = ∂Dx/∂z（対称）
```

```hlsl
// 各波について、足し込む。
float s = sin(theta);
dxdx -= w.steepness * w.amplitude * k * s * w.direction.x * w.direction.x;
dzdz -= w.steepness * w.amplitude * k * s * w.direction.y * w.direction.y;
dxdz -= w.steepness * w.amplitude * k * s * w.direction.x * w.direction.y;
// 最後に:
float jacobian = (1.0 + dxdx) * (1.0 + dzdz) - dxdz * dxdz;
```

## FFT 海面の、ヤコビアン

FFT 海面（[FFT Ocean](../waves/fft-ocean.md)）では、**水平変位の画像 `Dx`、`Dz`** が、テクスチャとして、得られます。その**隣の画素との差**（中央差分）から、偏微分を求めます。

```hlsl
// 変位テクスチャ（xy = Dx, Dz）から、ヤコビアンを求める。
float2 d_right = g_displacement.SampleLevel(g_point_wrap, uv + float2(texel, 0), 0).xz;
float2 d_left  = g_displacement.SampleLevel(g_point_wrap, uv - float2(texel, 0), 0).xz;
float2 d_up    = g_displacement.SampleLevel(g_point_wrap, uv + float2(0, texel), 0).xz;
float2 d_down  = g_displacement.SampleLevel(g_point_wrap, uv - float2(0, texel), 0).xz;

float2 ddx_ = (d_right - d_left) / (2.0 * texel_world);       // (∂Dx/∂x, ∂Dz/∂x)
float2 ddz_ = (d_up - d_down) / (2.0 * texel_world);          // (∂Dx/∂z, ∂Dz/∂z)

float jacobian = (1.0 + ddx_.x) * (1.0 + ddz_.y) - ddz_.x * ddx_.y;
```

`texel_world` は、変位マップの、**1 画素のワールド上の大きさ**（`patch_size / N`）です。

!!! tip "ヤコビアンを、FFT で、直接求める"
    差分は、**ノイズを増やしやすい**です。**周波数空間で、微分を掛けて、逆 FFT する**と、正確に、偏微分が、得られます（`∂/∂x ↔ i kx`）。逆 FFT の、画像の枚数が、増えますが、**きれいな泡**になります。

## 泡の、ためる・消す

ヤコビアンが、小さい瞬間だけ、泡を出すと、**一瞬で消えて、ちらつきます**。**泡を、ためて、ゆっくり消す**と、波頭が、通り過ぎた後にも、**泡が、尾を引いて**残ります（[Persistent Foam](foam-history.md)）。

```hlsl
// 泡の蓄積: 新しい泡と、前の泡（減衰させたもの）の、大きい方を取る。
float new_foam = saturate((foam_threshold - jacobian) / foam_softness);
float foam = max(new_foam, prev_foam * exp(-decay_rate * dt));
```

## 泡の、位置の補正

ヤコビアンは、**動く前の位置 `P₀`** の関数です。泡を、**画面の、どこに、出すか**は、**動いた後の位置 `P`** です。**頂点シェーダーで、ヤコビアンを求めて、補間して**、ピクセルへ、渡すなら、自動で、合います。**テクスチャに焼く**場合は、`P₀` の座標に、書かれるので、**波頭の位置と、泡が、わずかに、ずれて**見えることがあります。変位を、足して、**`P` の位置で、読む**ように、補正します（水平変位は、頂点シェーダーが、すでに、反映しているので、頂点の `P₀` を、UV として、読めばよい）。

''', before="## よくあるミス")
pg.Refs("water/shore-foam/crest-jacobian.md", [TESSENDORF, JENSEN, "Fournier, Reeves, \"A Simple Model of Ocean Waves\", SIGGRAPH 1986"])

pg.Dedup("water/shore-foam/foam-history.md")
pg.Add("water/shore-foam/foam-history.md", '''
## なぜ、履歴が、要るのか

波頭や、岸の泡を、**そのフレームの、条件だけ**で決めると、**波頭が、通り過ぎた瞬間に、泡も消えて**、ちらつきます。現実の泡は、**ゆっくり消え**、**水の動き**に乗って、**流れます**。**泡の量を、テクスチャに、記録して、毎フレーム更新**します（履歴）。

| 現象 | 履歴での表現 |
| --- | --- |
| 波頭が、通った後に、泡が、残る | 新しい泡を、足し、**減衰**で、ゆっくり消す |
| 泡が、水の流れに乗って、動く | 履歴を、流れの向きに、**移流**させる |
| 泡が、広がって、薄くなる | 履歴を、少し、**ぼかす** |
| 物（船）が、通ると、泡が、出る | 物の位置に、泡を、**描き込む**（[Wakes and Collisions](wake.md)） |

## 泡の、履歴テクスチャ

カメラの周りの、**数十〜数百メートル**を、覆う、小さな、**テクスチャ**（`R8_UNORM` で十分）を、用意します。2 枚を、**ping-pong**（前のフレームを、読み、今のフレームに、書く）します。

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 512; desc.Height = 512;
desc.MipLevels = 1; desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R8_UNORM;                        // 泡の量（0〜1）
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_RENDER_TARGET;
device->CreateTexture2D(&desc, nullptr, &foam_tex[0]);
device->CreateTexture2D(&desc, nullptr, &foam_tex[1]);
// 毎フレーム: foam_tex[prev] を読み、foam_tex[cur] に書く。終わったら、役割を、入れ替える。
```

## 更新のシェーダー

全画面の、ピクセル シェーダーで、更新します。**前のフレームの、泡を、流れに沿って、動かし（移流）、減衰させ、新しい泡を、足し**ます。

```hlsl
Texture2D<float> g_foam_prev : register(t0);
Texture2D<float2> g_flow : register(t1);             // 水の流れ（ワールド XZ の速度）
Texture2D<float> g_new_foam : register(t2);          // このフレームで、新しく出る泡（波頭、物）

cbuffer FoamCB : register(b0) {
  float g_dt;
  float g_decay;          // 1 秒あたりの減衰率（例: 0.5 → 約 2 秒で、半分以下）
  float g_blur;           // 広がり（0〜1）
  float g_texel;          // 1 画素の、UV 上の大きさ
  float2 g_origin_shift;  // 窓が、動いた分（UV）
  float2 pad;
};

float4 main(float2 uv : TEXCOORD0) : SV_Target {
  // ① 移流: 上流の位置から、前の泡を読む（窓の移動分も、補正する）
  float2 flow = g_flow.Sample(g_linear_clamp, uv);
  float2 prev_uv = uv - flow * g_dt * g_flow_to_uv - g_origin_shift;
  float prev = g_foam_prev.Sample(g_linear_clamp, prev_uv);

  // ② 広がり: 周りの泡を、少し混ぜる（ぼかし）
  float blur = 0.25 * (g_foam_prev.Sample(g_linear_clamp, prev_uv + float2( g_texel, 0))
                     + g_foam_prev.Sample(g_linear_clamp, prev_uv + float2(-g_texel, 0))
                     + g_foam_prev.Sample(g_linear_clamp, prev_uv + float2(0,  g_texel))
                     + g_foam_prev.Sample(g_linear_clamp, prev_uv + float2(0, -g_texel)));
  prev = lerp(prev, blur, g_blur);

  // ③ 減衰
  prev *= exp(-g_decay * g_dt);

  // ④ 新しい泡を足す（大きい方）
  float fresh = g_new_foam.Sample(g_linear_clamp, uv);
  return max(prev, fresh);
}
```

| 段階 | 内容 |
| --- | --- |
| 移流 | 流れが、無い海では、**省く**（`flow = 0`）。川や、波の押し寄せる岸で、効く |
| ぼかし | **強すぎる**と、泡が、にじんで、輪郭が失われる。弱く（0.05〜0.2） |
| 減衰 | 遅いと、泡が、ずっと残る。**波の周期と、同じくらい**（2〜5 秒） |
| 新しい泡 | ヤコビアン、物の位置、岸の深度差など、**複数の源を、`max` でまとめる** |

## 窓を、カメラに追従させる

履歴は、**カメラの周りだけ**を、覆います。窓が、動いたとき、**中身を、ずらす**必要があります。

| 方法 | 内容 |
| --- | --- |
| UV を、ずらして、読む | 上のコードの `g_origin_shift`。窓が、動いた分だけ、読む位置を、ずらす。**ずらすと、ぼやける**（補間のため） |
| 画素単位で、動かす | 窓を、**画素の整数倍**でだけ動かす。ぼやけない。窓が、少しずつ、カクカク動く |
| 円環バッファ | `WRAP` で、コピーせずに済む（[Trampled Grass](../../terrain/vegetation/trample.md)） |

**窓が、1 画素動くたびに、更新**する方式では、**ぼやけない**ので、泡のように、**細かい模様**に、向きます。

## 解像度と、見た目

泡の履歴は、**低解像度**（512×512）でも、**ディテール**を、別に、足せば、十分です。泡の、**形（細かい模様）**は、**高解像度の、泡のテクスチャ**で、作り、履歴は、**どこに、どれだけ、泡があるか**（マスク）だけを、持ちます（[Foam Textures and Compositing](foam-texture.md)）。

| 解像度の、役割 | 内容 |
| --- | --- |
| 履歴（低解像度） | 泡の**量**。大きなスケールで、変化する |
| 泡のテクスチャ（高解像度） | 泡の**形**。履歴の値を、しきい値に、使って、**切り出す** |

''', before="## よくあるミス")
pg.Refs("water/shore-foam/foam-history.md", [TESSENDORF, JENSEN, VLACHOS, NEYRET])

pg.Dedup("water/shore-foam/foam-texture.md")
pg.Add("water/shore-foam/foam-texture.md", '''
## 泡の量から、泡の見た目へ

履歴や、ヤコビアンから得られるのは、**泡の量**（0〜1 のマスク）です。これを、**泡らしい、模様**に変えるのが、**泡のテクスチャ**の役目です。

## しきい値で、切り出す

**泡の量が、多い場所ほど、泡のテクスチャが、濃く出る**ように、**テクスチャの値と、泡の量を、比較**します。

```hlsl
// 泡のテクスチャ（白黒のノイズ状の模様）を、泡の量でしきい値処理する。
float foam_pattern = g_foam_tex.Sample(g_linear_wrap, world_uv * foam_scale).r;
// 泡の量が多いほど、小さい値のところまで、泡になる（しきい値が、下がる）。
float foam = smoothstep(1.0 - foam_amount, 1.0 - foam_amount + foam_softness, foam_pattern);
```

| 泡の量 | 見え方 |
| --- | --- |
| 0.1 | まばらな、小さな泡の点 |
| 0.5 | 網目状の、泡の層 |
| 0.9 | ほぼ一面の、泡（切れ目が、わずか） |

**しきい値で、切る**ことで、泡の**縁が、くっきり**し、量の変化に、応じて、**泡の面積が、なめらかに、増減**します。単純に、泡の量を、アルファとして掛けると、**ぼんやりした、白いもや**になります。

## 2 つのスケールを、重ねる

1 つの、スケールだけだと、**繰り返しが、目立ち**ます。**大きさの違う、2 枚**を、**逆向きに、ゆっくり、動かして**、混ぜます。

```hlsl
float p1 = g_foam_tex.Sample(g_linear_wrap, world_uv * 0.5 + time * float2( 0.01, 0.005)).r;
float p2 = g_foam_tex.Sample(g_linear_wrap, world_uv * 1.7 + time * float2(-0.007, 0.011)).r;
float foam_pattern = p1 * p2 * 2.0;          // 掛けて 2 倍。平均の明るさが、保たれる
```

## 泡の、色と、ライティング

泡は、**白く、不透明に近い**ですが、**水の中に、浮いている**ため、**水の色が、少し、混ざります**。

| 要素 | 内容 |
| --- | --- |
| 色 | 白〜薄いグレー。**水の色を、少し混ぜる**（水の中の、泡は、青みがかる） |
| 拡散反射 | **ランバート**。泡は、粗い表面なので、**反射が、拡散**する |
| スペキュラー | **ほぼ無し**（粗さが、高い）。水のスペキュラーを、**泡の量で、打ち消す** |
| 水の反射の、打ち消し | 泡のある所は、水面の**鏡面反射が、弱まる**（泡が、水面を覆うため） |

```hlsl
// 泡の量で、水の反射と、スペキュラーを弱めて、泡の拡散色に、置き換える。
float3 water_shaded = water_color + reflection + specular;
float3 foam_shaded = foam_color * (ambient + sun_color * saturate(dot(N, L)));
float3 color = lerp(water_shaded, foam_shaded, foam * foam_opacity);
```

## 泡の厚みと、凹凸

泡の、**模様の濃淡**は、**泡の厚み**として、解釈できます。厚い所は、**盛り上がって**います。この、**凹凸**を、**法線**に反映すると、泡が、**立体的**に見えます。

```hlsl
// 泡のテクスチャの、勾配から、法線を作る（簡易）。
float h = foam_pattern;
float2 gradient = float2(ddx(h), ddy(h)) * foam_normal_strength;       // 画面の微分
float3 foam_normal = normalize(float3(-gradient.x, 1.0, -gradient.y));
N = normalize(lerp(N, foam_normal, foam));
```

## 泡が、水面を、覆っているときの、透明度

泡は、**完全に不透明ではありません**。薄い泡の層は、**下の、水が、透けて見える**ことがあります。**泡の、アルファ**は、**泡のテクスチャの、値**から決めます。

```hlsl
float foam_alpha = saturate(foam * foam_opacity);
// 下の水の色と、泡の色を、アルファでブレンドする。
```

## 泡の、縁の、扱い

**岸に、打ち寄せる、泡**は、岸の、陸の部分で、**切れ目**が、できます。陸と水の、**境目**では、泡を、**陸の方へ、はみ出さない**ようにします（[Shore Foam: Depth Difference](shore-depth.md)）。

## 低解像度の、履歴と、高解像度の、模様の、組み合わせ

| 層 | 解像度 | 内容 |
| --- | --- | --- |
| 泡の履歴（量） | 低（512×512） | **どこに、どれだけ**、泡があるか |
| 泡のテクスチャ（模様） | 高（1024×1024、タイル） | 泡の**形** |
| しきい値処理 | ピクセル | 履歴の値で、模様を、**切り出す** |

**低解像度の履歴**を、高解像度の、泡の模様で、**切り出す**ことで、**少ない、メモリと、計算**で、**細かい泡**が、表現できます。

''', before="## よくあるミス")
pg.Refs("water/shore-foam/foam-texture.md", [JENSEN, TESSENDORF, VLACHOS, RTR])

pg.Dedup("water/shore-foam/shore-depth.md")
pg.Add("water/shore-foam/shore-depth.md", '''
## 岸の、泡の、位置

波が、岸に打ち寄せるとき、**水が、浅くなるにつれて、波が、砕け、岸に沿って、泡の帯**が、できます。泡の位置は、**水深**で、決まります。水深が、**浅いほど**、泡が、多く出ます。

## 水深を、求める

水深は、**水面の深度**と、**水の後ろの、地形（不透明な物）の深度**の、**差**から、求めます（[Color by Water Depth](../shading/depth-color.md)）。

```hlsl
float scene_depth = LinearizeDepth(g_scene_depth.Sample(g_point_clamp, screen_uv).r);
float surface_depth = LinearizeDepth(input.position.z);
float depth_diff = max(scene_depth - surface_depth, 0.0);         // 視点深度の差（水の厚み）
```

## 泡の帯

**水深が、浅いほど、泡が出る**ように、水深から、泡のマスクを作ります。

```hlsl
// 水深が foam_width より浅い所に、泡を出す。0 に近いほど濃い。
float shore_foam = 1.0 - saturate(depth_diff / foam_width);
shore_foam = shore_foam * shore_foam;           // 岸に近いほど、急に、濃く
```

| パラメーター | 目安 | 効果 |
| --- | --- | --- |
| `foam_width` | 0.5〜2 m | **泡の帯の、幅**。大きいほど、岸から、沖まで、泡が出る |
| 2 乗 | — | 岸の、ごく近くを、強調する |

### 縁に、ノイズを、足す

泡の帯が、**なめらかな、直線**だと、不自然です。**ノイズ**で、**境界を、ゆらします**。

```hlsl
float noise = g_noise.Sample(g_linear_wrap, world_uv * 2.0 + time * 0.05).r;
float shore_foam = saturate(1.0 - depth_diff / (foam_width * (0.5 + noise)));
```

## 波が、押し寄せて、引く

岸の泡は、**静止した帯**ではなく、**波が来て、引くたびに、岸に沿って、前後に動き**ます。水深に、**時間とともに、動く、しきい値**を使うと、この動きを、再現できます。

```hlsl
// 波の周期で、泡の帯が、岸へ寄せて、引く。
float wave = 0.5 + 0.5 * sin(time * wave_speed - depth_diff * wave_frequency);   // 水深に応じて位相がずれる
float threshold = foam_width * wave;                                              // 波が寄せると、帯が、広がる
float shore_foam = saturate(1.0 - depth_diff / max(threshold, 0.01));
```

`depth_diff × wave_frequency` を、位相に入れると、**波の位相が、水深によって、ずれる**ので、**岸に向かって、進む帯**のように見えます。波が、**岸へ進む**向きは、`−depth_diff` の符号で、決まります。符号を、逆にすると、**沖へ引いて**行く動きになります。

## 水と陸の、境目を、なめらかにする

水面と地形が、交差する線は、**ぱっきり、線が見えます**。**深度の差が、小さい所の、アルファ**を、下げて、**水面を、岸で、透明に、フェード**させます（ソフト パーティクルと、同じ考え方、[Soft Particles](../../translucency/blending-sorting/soft-particles.md)）。

```hlsl
// 水面の、岸の近くを、透明にして、交差の線を、消す。
float edge_alpha = saturate(depth_diff / edge_fade_distance);       // 浅いほど透明
float alpha = edge_alpha;
// 泡は、その上に、不透明に近く、描く（泡のアルファは、別）。
```

| 要素 | 役割 |
| --- | --- |
| 水面の、アルファ | 岸で、**透明**に。交差の線が、見えない |
| 泡 | 岸の近くで、**濃い**。水面が、透けても、泡が、境目を、隠す |

**泡の帯が、境目を、隠す**ので、この 2 つは、**セット**で使います。

## 波の、勢いと、泡の、強さ

波が**強い**日は、**泡が、広く、濃く**出ます。泡の強さを、**波の振幅**（風の強さ）で、変えます。

```hlsl
float shore_foam_strength = lerp(0.4, 1.0, saturate(wind_strength));
float foam_width = base_width * lerp(0.7, 1.5, saturate(wind_strength));
```

## 地形の傾き

**傾きが、緩やか**な浜辺では、水深が、**ゆっくり**浅くなるので、**泡の帯が、広く**なります。**崖の下**では、水深が、急に、深くなり、**帯が、細く**なります。水深マップを使うので、**この違いは、自動で**出ます。

## 注意点

| 項目 | 内容 |
| --- | --- |
| 屈折との、整合 | 水深を、読む UV を、**屈折で歪ませた位置**と、そろえる（[Water Refraction Distortion](../shading/refraction.md)） |
| 画面外の地形 | 画面の外の、地形の深度は、読めない。**水深マップ（別のテクスチャ）**を、持つと、安定する |
| 深度の精度 | 遠くでは、深度の精度が低く、**泡の帯が、ちらつく**。水深を、**事前に、テクスチャに焼いて**おく（地形から、ツールで作る） |
| ノイズの、サイズ | 小さすぎると、**ちらつく**。大きめの、ゆっくり動くノイズを使う |

''', before="## よくあるミス")
pg.Refs("water/shore-foam/shore-depth.md", [JENSEN, TESSENDORF, VLACHOS, "Microsoft Learn, \"Depth Buffers\" (Direct3D 11)"])

pg.Dedup("water/shore-foam/wake.md")
pg.Add("water/shore-foam/wake.md", '''
## 航跡の形（ケルビン波）

船が、水面を進むと、**V 字形の、波の模様**が、できます。**ケルビン卿**が、理論的に、示した形で、**ケルビン波**と呼ばれます。

```text
              船
       ╲      ●      ╱
         ╲   ↑ ↑   ╱         ← 発散波（V 字の、外側）
           ╲     ╱
            ╲   ╱  ← 横波（V 字の、内側の、横縞）
             ╲ ╱
              ·
```

| 項目 | 内容 |
| --- | --- |
| V 字の、開き角 | 船の進行方向から、約 **19.47°**（片側）。**船の速さに、依存しない** |
| 構成 | 船の進行方向に、垂直な**横波**と、斜めに広がる**発散波** |
| 泡 | 船の真後ろに、**白い泡の帯**（スクリュー、船体の、乱れ） |

**19.47° という値は、船の速さに、無関係**で、水の分散関係から、決まります（`sin⁻¹(1/3)`）。ゲームでは、**V 字の、見た目**を、作るだけなら、この角度の、**2 本の線**を、描くだけで、十分です。

## 作る方法

| 方法 | 内容 | 向く場面 |
| --- | --- | --- |
| 泡の履歴に、**船の軌跡を描く** | 船の位置に、泡を、毎フレーム描き込む。**軌跡**が、履歴として、残り、泡が、広がって、消える（[Persistent Foam](foam-history.md)） | 基本。どんな船でも |
| **航跡のメッシュ** | 船の後ろに、**V 字形の、リボン（帯）**を、置く。テクスチャで、波と泡を、描く | 大きな船。決まった形の、航跡 |
| 波の、シミュレーション | 船が、水面を、押す。波が、**自然に、V 字形**になる（[Applying a Height Map to the Surface](../interaction/apply-height.md)） | 静かな、水面。小さな船、泳ぐ人 |
| パーティクル | 船首の、しぶき、船尾の、泡 | 補助として、併用 |

## 方法 1：泡の履歴に、軌跡を描く

船の、**水面に触れている、船体**の位置に、**泡を、描き込み**ます（[Writing Object Contacts](../interaction/contact.md) の、方法 2 を、応用）。

```hlsl
// 船の底を、上から見下ろして描く。水面より下の部分に、泡を、書く。
float4 WakePS(PSInput input) : SV_Target {
  float depth_below = water_height - input.world_position.y;
  if (depth_below <= 0.0) discard;
  // 船の速さに応じて、泡の強さを決める（止まっている船は、泡が出ない）
  float foam = saturate(ship_speed / max_speed) * wake_strength;
  return float4(foam, 0, 0, 1);
}
```

船が、進むたびに、泡が、描き込まれ、**軌跡**が、残ります。履歴の、**減衰と、広がり**で、**後ろに行くほど、広がって、薄くなる**航跡が、自然にできます。

| パラメーター | 内容 |
| --- | --- |
| 泡の強さ | 船の**速さ**に、比例。速いほど、泡が、濃い |
| 減衰 | 遅い（5〜10 秒）。軌跡が、長く、残る |
| 広がり（ぼかし） | 少し。航跡が、後ろで、**広がる** |

## 方法 2：航跡のメッシュ

船の後ろに、**V 字の、リボンを、置いて、アニメーション**させます。

```text
上から見た、リボンのメッシュ:

  ╲                ╱
   ╲              ╱           各頂点に、船からの、距離（0〜1）を持たせる。
    ╲            ╱            距離に応じて、リボンが、広がり、薄くなる。
     ╲          ╱
      ╲___●___╱
```

```hlsl
// リボンの、頂点シェーダー: 船からの距離で、幅を広げる。
float t = input.distance_from_ship;                  // 0（船尾）〜 1（遠い）
float width = lerp(ship_width, ship_width * 8.0, t);
world_pos += side_vector * input.side * width;       // side: −1（左）〜 +1（右）
```

```hlsl
// ピクセル シェーダー: 距離で薄くし、V 字の縁と、中央の泡の帯を、テクスチャで描く。
float fade = 1.0 - smoothstep(0.0, 1.0, t);
float foam_pattern = g_wake_tex.Sample(g_linear_wrap, float2(input.side * 0.5 + 0.5, t * 8.0 - time * 0.5)).r;
float alpha = foam_pattern * fade * wake_strength;
```

方法 1 に比べて、**形を、制御しやすい**ですが、**船が、曲がる**と、リボンも、船の軌跡に沿って、**曲げる**必要があり、実装が、増えます（船の過去の位置を、リストで持ち、そこへリボンを、並べる）。

## 船首の波と、スプレー

船首は、水を、**押しのけて**、**船首波**（バウ ウェーブ）と、**しぶき**を、作ります。

| 要素 | 方法 |
| --- | --- |
| 船首波 | 船首の位置に、**強い、押し込み**を、波のシミュレーションに加える（[Applying a Height Map to the Surface](../interaction/apply-height.md)） |
| しぶき | 船首で、**パーティクル**を、出す。速さに応じた、数と、向き |
| 泡 | 船首から、船体の側面に沿って、泡を、描く（方法 1） |

## 衝突と、水しぶき

物が、水に、**落ちたり、ぶつかったり**したときは、**一瞬の、波紋と、泡**が、出ます。

```cpp
// 水に入った瞬間: 波紋 + 泡 + しぶき（3 つを同時に）。
void OnEnterWater(const float3& pos, float speed) {
  AddImpulse(pos.xz, radius, -speed * 0.02f);        // 波紋
  AddFoam(pos.xz, radius * 1.5f, saturate(speed / 10.0f));   // 泡を、履歴に描く
  SpawnSplash(pos, speed);                           // しぶき
}
```

波紋は、**広がって消える**、泡は、**ゆっくり消える**、しぶきは、**落ちて、また、水面に、小さな波紋**を、作ります。この、**3 つの、時間スケールの違い**が、水に落ちた感じを、作ります。

## 水の中の、航跡

船が、**スクリュー**を、回すと、**水中に、泡の、柱**ができます。水面から、**水中に向かって、泡の、パーティクル**を出すと、**水中から、航跡**が見えます（[Underwater Rendering](../underwater/index.md)）。

''', before="## よくあるミス")
pg.Refs("water/shore-foam/wake.md", [KERNER, TESSENDORF, JENSEN, "Thomson (Lord Kelvin), \"On Ship Waves\", Proceedings of the Institution of Mechanical Engineers, 1887（ケルビン波の原典）"])
pg.Refs("water/shore-foam/index.md", [TESSENDORF, JENSEN, VLACHOS, KERNER])

# ================================================================ underwater
pg.Dedup("water/underwater/caustics.md")
pg.Add("water/underwater/caustics.md", '''
## コースティクスとは

水面の波は、**レンズのように、光を、屈折**させます。屈折した光は、**水底で、集まる場所と、散る場所**ができ、**明るい、網目状の模様**が、揺れます。これが、**コースティクス**（集光模様）です。プールの底で、ゆらゆら動く、光の網が、典型です。

```text
        太陽
       ↓ ↓ ↓ ↓ ↓ ↓
━━━━ ╲╱ ╲╱ ╲╱ ╲╱ ━━━━  ← 波のある水面（光が、曲がる）
     ↘ ↓ ↙   ↘ ↓ ↙
        ↘↓↙       ↘↓↙
    ──── 明るい ──── 暗い ──── 明るい ──   ← 水底（光が、集まった所が、明るい）
```

## 方法 1：アニメーションする、テクスチャを、投影する

最も簡単な方法は、**コースティクスの、模様を、あらかじめ作ったテクスチャ**を、**水底に、投影して、ゆっくり動かす**ことです。

```hlsl
// 水底の、ライティングに、コースティクスを、足す。
float2 uv = world_pos.xz * caustic_scale;
// 2 枚を、違う速さと、向きで、動かして、重ねる（周期が、見えにくくなる）。
float c1 = g_caustic_tex.Sample(g_linear_wrap, uv + time * float2( 0.03, 0.02)).r;
float c2 = g_caustic_tex.Sample(g_linear_wrap, uv * 1.3 - time * float2(0.02, 0.03)).r;
float caustic = min(c1, c2);                                 // 小さい方を取る → 模様が、細く、鋭くなる
float3 lit = sun_color * n_dot_l * (1.0 + caustic * caustic_strength);
```

| 項目 | 内容 |
| --- | --- |
| テクスチャ | **タイルできる**、コースティクスの画像。**ゆっくり変化するアニメーション**（フレームの、連続）も、使える |
| 投影の向き | **太陽の方向**。水底の傾きに、関係なく、真上から（または、太陽の向きで）投影する |
| `min` で、重ねる | 2 枚の、**暗い所**が、重なった所が、さらに、暗くなり、**網の線が、細く**見える |
| 強さ | 水深とともに、**弱める**（深いと、光が、届かない） |

### 水深で、弱める

```hlsl
// 深さとともに、コースティクスを弱める（水の吸収）。
float3 caustic_color = sun_color * exp(-absorption * depth_below_surface) * caustic * caustic_strength;
```

コースティクスは、**太陽光**の模様なので、**水に、吸収**されます。水深が深いと、**暗く、青く**なります（[Color by Water Depth](../shading/depth-color.md)）。

## 方法 2：波から、リアルタイムに、計算する

波の形（法線）から、**屈折した光が、水底の、どこに届くか**を、計算し、**光が、集まる場所を、数える**ことで、コースティクスを、計算できます（Guardado ら、2004、Wallace、2015）。

### 考え方

水面の、**1 つの小さな面**を、通った光は、屈折して、**水底の、別の大きさの面**に、当たります。

| 水底での、面積 | 光の強さ |
| --- | --- |
| 水面の面積より、**小さい** | 光が、集まる → **明るい** |
| 水面の面積より、**大きい** | 光が、広がる → **暗い** |

```text
明るさ ∝ 水面での面積 / 水底での面積
```

### 実装（画面の微分を使う方法）

水面の、各点から、**屈折光を、水底へ**飛ばし、**水底の位置の、隣のピクセルとの差**から、**面積の変化**を、求めます。

```hlsl
// 水面の、頂点（または画素）から、屈折光が、水底に当たる位置を求める。
float3 refracted = refract(-sun_dir, wave_normal, 1.0 / 1.33);
float t = (floor_height - world_pos.y) / refracted.y;           // 水底（y = floor_height）までの距離
float3 floor_pos = world_pos + refracted * t;                    // 水底の位置

// 隣のピクセルとの、水底の位置の差から、面積の変化を求める。
float3 dx = ddx(floor_pos);
float3 dy = ddy(floor_pos);
float new_area = length(cross(dx, dy));                           // 水底での面積
float3 ox = ddx(world_pos);
float3 oy = ddy(world_pos);
float old_area = length(cross(ox, oy));                           // 水面での面積

float caustic = old_area / max(new_area, 1e-5);                   // 面積が小さくなるほど、明るい
```

この計算を、**水底に、描く**（水面から見て、水底の位置に、書き込む）ことで、コースティクスの画像（**テクスチャ**）を、作れます。そのテクスチャを、**水底や水中の物に、投影して**使います。

| 項目 | 内容 |
| --- | --- |
| 解像度 | 512×512〜1024×1024 のテクスチャ。カメラの周りの、窓（円環バッファでもよい） |
| 精度 | 波の、法線の精度に、依存。**高周波の波**を、使うほど、模様が、細かい |
| 水底の、形 | 水底を、**平面**と、仮定する簡易版が、多い（実際の、起伏のある水底では、ずれる） |
| 太陽以外の光 | 空からの光は、広い範囲から来るので、コースティクスは、出ない（ぼやける） |

## 方法の選び方

| 方法 | 見た目 | コスト | 向く場面 |
| --- | --- | --- | --- |
| 投影テクスチャ（事前に作った） | 動きが、**一定の、模様** | 小 | ほとんどのゲーム |
| 波から、リアルタイムに、計算 | **波と、正確に、連動** | 中 | 波が大きい海。見た目を、重視 |

波の動きと、連動しなくても、**多くの人は、気づきません**。**投影テクスチャ**で、十分なことが、ほとんどです。

## 水の外に、出る光

水の**外**にある、**壁や、船体**にも、水面で反射した、**揺れる光の模様**が、映ります（水辺の、壁に、水の揺れが、映る）。**同じ、コースティクスの、テクスチャ**を、水の近くの、物に、**弱く**投影すると、**水辺の、雰囲気**が、出ます。

## 注意点

| 項目 | 内容 |
| --- | --- |
| 水面の外には、出さない | コースティクスを、水の中の物にだけ、掛ける（水の上の地面に、掛けない）。**水位以下の、物**だけ |
| 影との関係 | 影の中は、太陽が、当たらない。コースティクスも、**影の中では、消す**（影の係数を、掛ける） |
| 夜 | 太陽が無いので、**消える** |
| 曇り | 太陽光が、弱いので、**弱める** |

''', before="## よくあるミス")
pg.Refs("water/underwater/caustics.md", [GUARDADO, WALLACE, TESSENDORF, RTR])

pg.Dedup("water/underwater/fog.md")
pg.Add("water/underwater/fog.md", '''
## 水中は、霧の中

水の中は、光が、**吸収と散乱**で、すぐに、減ります。**遠くの物が、見えず、色が、青緑に、染まる**様子は、**霧**（フォグ）と、同じ式で、表現できます。ただし、**色ごとに、吸収の強さが違う**点が、空気中の霧との、大きな違いです。

## 色ごとの減衰

空気中の霧は、**色に関係なく、同じ割合**で、遠くの物の色を、霧の色へ近づけます。水中では、**赤が、すぐに消え、青が、遠くまで残ります**。

```hlsl
// 水中の霧: 色（RGB）ごとに、透過率が違う。
float3 transmittance = exp(-absorption * distance_in_water);      // absorption は RGB ごとの値（1/m）
float3 color = scene_color * transmittance + water_color * (1.0 - transmittance);
```

| 距離 | 赤の残り | 緑の残り | 青の残り | 見た目 |
| --- | --- | --- | --- | --- |
| 0 m | 100% | 100% | 100% | 元の色 |
| 3 m | 26% | 81% | 91% | 赤が、ほぼ消える |
| 10 m | 1% | 50% | 74% | 青緑 |
| 30 m | 0% | 12% | 41% | 青（暗い） |

吸収係数 `(0.45, 0.07, 0.03)`（1/m）で、計算しました（[Color by Water Depth](../shading/depth-color.md)）。

空気中の霧の式（[Fog Equations](../../atmosphere/aerial-fog/fog-equation.md)）と、**形は同じ**ですが、**係数が、RGB で、違う**のが、特徴です。

## 水中の霧を、全画面で適用する

**カメラが、水の中にある**とき、**画面全体**に、霧をかけます。ポストプロセスで、**画素ごとの、距離**（深度バッファから）を、使います。

```hlsl
// ポストプロセス: カメラが水中のとき、全画面に、水中の霧をかける。
float depth = LinearizeDepth(g_depth.Sample(g_point_clamp, uv).r);
float3 view_ray = ReconstructViewDirection(uv);
float distance = depth * length(view_ray);                       // 視線方向の距離

float3 scene = g_scene.Sample(g_linear_clamp, uv).rgb;
float3 T = exp(-g_absorption * distance);
float3 color = scene * T + g_water_color * (1.0 - T);
```

| 項目 | 内容 |
| --- | --- |
| 空（深度が、最大の画素） | 空は、水の中からは、見えない（水面の向こう）。**水の色**で、塗る |
| 水面を見上げたとき | 水面の描画（[The Underside of the Surface and Crossing It](surface-back.md)）。水面より向こうの、空の描画は、別に扱う |
| 水中の、遠い物 | 距離が、大きいほど、**水の色**（`water_color`）に、近づく |

### 水の色（`water_color`）と、深さ

水中の、**水の色**は、**深くなるほど、暗く**なります。**太陽の光が、深さとともに、減る**ためです。

```hlsl
// カメラの深さに応じて、水の色を、暗くする（太陽光が、届かなくなる）。
float camera_depth_below_surface = max(water_surface_y - camera_position.y, 0.0);
float3 sun_at_camera = exp(-g_absorption * camera_depth_below_surface);
float3 water_color = g_deep_color * (0.2 + 0.8 * sun_at_camera.b);     // 青の光の、残り具合で、明るさを決める
```

| 深さ | 水の色の、明るさ |
| --- | --- |
| 水面の近く | 明るい青緑 |
| 10 m | 暗い青 |
| 50 m | ほぼ、真っ暗 |
| 200 m | 真っ暗（太陽光は、届かない） |

## 光源の、色も、変わる

水中の物を、ライティングするとき、**光が、水の中を、通ってくる**間に、吸収されます。

| 光源 | 水中での、色 |
| --- | --- |
| 太陽光 | 水面から、物までの、**深さ**に応じて、赤から、消える |
| 環境光（空の光） | 同様。**全体に、暗く、青く**なる |
| 水中の、ライト（懐中電灯、ランプ） | 光源から、物までの、**距離**に応じて、吸収される。近くでは、白く、遠くでは、青緑 |

```hlsl
// 太陽光を、水中の深さ d で減衰させる。
float3 sun_underwater = sun_color * exp(-g_absorption * depth_below_surface);
```

## 水中の、遠景の、扱い

遠くの地形や、物を描くとき、**空気中の大気（空気遠近法）は、水中では、使いません**。水中では、**水の霧**で、置き換えます。

| カメラの位置 | 使う霧 |
| --- | --- |
| 空気中 | 大気の霧（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)） |
| 水中 | 水中の霧（このページ） |
| 水面をまたぐ（半分水中、半分空気中） | 水面の高さで、**霧を、切り替える**（[The Underside of the Surface and Crossing It](surface-back.md)） |

水中では、**視界が、非常に短く**なるので、**遠景（地形のチャンク、遠くの物）の描画**は、**早めに、打ち切って**、**コストを、減らせます**。

## 濁り：吸収と、散乱

澄んだ海では、吸収が、主です。**濁った水**（泥、プランクトン）では、**散乱**が、強く、**光が、水中で、あらゆる方向に、散って、視界が、さらに短く**なり、**霧のような、もや**が見えます。

| 水の種類 | 吸収 | 散乱 | 見た目 |
| --- | --- | --- | --- |
| 澄んだ海 | 小さい（赤だけ強い） | ごく小さい | 青く、遠くまで見える |
| 湖 | 中（緑が、残る） | 中 | 緑がかった、少し、もやっとした |
| 川（濁り） | 大きい | **大きい** | **茶色の、もや**。数メートルしか、見えない |

濁った水では、`water_color` を、**明るく、不透明に近く**して、**吸収係数を、大きく**します。**霧のような見た目**になります。

''', before="## よくあるミス")
pg.Refs("water/underwater/fog.md", [POPE, "Jerlov, \"Marine Optics\", Elsevier, 1976", "Gordon, Brown, Jacobs, \"Computed Relationships between the Inherent and Apparent Optical Properties of a Flat Homogeneous Ocean\", Applied Optics, Vol. 14, No. 2, 1975", RTR])

pg.Dedup("water/underwater/god-rays.md")
pg.Add("water/underwater/god-rays.md", '''
## 水中の、光の筋

水の中では、**水面から、差し込む太陽光が、筋になって、見えます**。水中に、**細かい粒子**（プランクトン、泥）があり、光の通り道で、**光が、散乱して**、**光の通り道だけが、明るく**なるためです（空気中の、ゴッド レイと、同じ原理、[God Rays](../../atmosphere/god-rays/index.md)）。

水中では、**波が、光を、集めたり、散らしたり**する（コースティクスの、3 次元版）ので、**光の筋が、揺れ動き**ます。

## 方法 1：放射状の、ブラー（画面空間）

**太陽の画面上の位置**から、**画素に向かって、何回か、読んで、足す**方法です（[Screen-Space Radial Blur](../../atmosphere/god-rays/radial-blur.md)）。水中では、**太陽は、水面の向こうなので**、**水面の、明るさ**（波を通った、太陽光）を、**光の源**とします。

```hlsl
// 水中で、画面の上方（太陽の方向）へ向かって、放射状に読んで、足す。
float2 sun_screen = ProjectToScreen(camera_position - sun_dir * 1000.0);   // 太陽の画面上の位置
float2 delta = (uv - sun_screen) / kSamples * density;
float2 sample_uv = uv;
float illum = 0.0, weight = 1.0;
for (int i = 0; i < kSamples; ++i) {
  sample_uv -= delta;
  illum += g_light_mask.Sample(g_linear_clamp, sample_uv).r * weight;     // 明るい（光が、通っている）部分
  weight *= decay;
}
float3 god_rays = illum / kSamples * sun_color_underwater * intensity;
```

| 項目 | 内容 |
| --- | --- |
| 軽い | 画面全体の、後処理。**数回〜数十回の読み込み** |
| 光の源 | **水面の、明るさ**（波を通った、太陽光）、または、**水面の、見え方**を、マスクにする |
| 弱点 | **遮蔽物**（岩、船）が、光を遮る、正確な影が、出ない。太陽が、画面の外にあると、**使えない** |

## 方法 2：シャドウ マップを使った、レイマーチ

**水中の、各画素について**、**視線に沿って、少しずつ進み**、**各点が、太陽光を、受けているか**（影の中か）を、調べて、足し合わせます。**水面の波**による、**光の、変調**も、含められます（[Shadow Map Raymarching](../../atmosphere/god-rays/shadowmap-march.md)）。

```hlsl
// 視線に沿って進み、各点で、太陽光が届いているかを、シャドウ マップと、コースティクスで調べる。
float3 pos = camera_position;
float step = ray_length / kSteps;
float3 in_scatter = 0;
for (int i = 0; i < kSteps; ++i) {
  pos += view_dir * step;
  float lit = SampleShadowMap(pos);                              // 太陽光が、届いているか（0〜1）
  float caustic = SampleCaustic(pos);                            // 波が作る、光の濃淡
  float depth_below = surface_y - pos.y;
  float3 sun = sun_color * exp(-g_absorption * depth_below);     // 水面から、この点までの、吸収
  float3 T = exp(-g_absorption * (distance(pos, camera_position)));     // この点から、カメラまでの、吸収
  in_scatter += sun * lit * caustic * T * g_scatter * step;
}
```

| 項目 | 内容 |
| --- | --- |
| 精度 | **岩や船の影**で、光の筋が、**遮られる**。正確 |
| 波の影響 | コースティクスを、掛けると、**光の筋が、波で、揺れる** |
| 重い | 画素ごとに、数十回の、ステップ。**低解像度で計算**して、**アップサンプル**する |
| 吸収 | **水面からの深さ**と、**カメラまでの距離**の、**両方で、減衰**を掛ける |

## 方法 3：光の筋の、メッシュ

水面から、水中に向かって、**細長い、半透明の、板（またはメッシュ）**を、置く方法です（[Light Shaft Meshes](../../atmosphere/god-rays/mesh-shafts.md)）。

| 項目 | 内容 |
| --- | --- |
| 形 | 太陽の向きに沿った、細長い板。上は、明るく、下に向かって、**消える** |
| 動き | 波に合わせて、**ゆっくり、揺らす**（位置と、明るさ） |
| 軽い | 板を、数十枚描くだけ |
| 弱点 | 影や、遮蔽物と、**連動しない**。見た目が、**決まった形**に |

**加算ブレンド**で、描きます。板が、重なる所が、**明るくなります**。

## 水中らしさを、出す工夫

| 工夫 | 内容 |
| --- | --- |
| 波で、揺らす | 光の筋の、強さを、**コースティクスの、模様**で、変調する（水面の、揺れが、筋の揺れになる） |
| 深さで、消す | 光は、深くなるほど、**吸収**されて、消える。**浅い所**だけ、明るい筋 |
| 青緑に、着色 | 水中の、太陽光の、色（赤が、吸収された、青緑）で、描く |
| 粒子 | 光の筋の中に、**細かい粒子**（マリン スノー）を、漂わせると、光の筋が、**立体的**に見える（[Other Underwater Elements](other.md)） |

## 太陽の位置による、見え方

| 太陽の位置 | 見え方 |
| --- | --- |
| 真上（正午） | 光の筋が、**真下**へ、まっすぐ。ほぼ、垂直 |
| 低い（朝夕） | 光の筋が、**斜め**。筋が、長く、屈折で、曲がる |
| 水面の向こう側を、見る | 筋が、**カメラに向かって**来る。**まぶしい**（光が、強い） |
| 曇り、夜 | 光の筋が、**無い** |

太陽が、**水面で屈折**するので、水中での、光の向きは、**空気中の向きと、違います**（スネルの法則、[Refraction](../shading/refraction.md)）。**水中の光の向き**は、`refract(−sun_dir, (0,1,0), 1/1.33)` で、求めます。太陽が、水平線に近くても、水中では、**真下に、近づく**向きに、曲がります（最大でも、約 48.6°）。

''', before="## よくあるミス")
pg.Refs("water/underwater/god-rays.md", [MITCHELL, GUARDADO, RTR, "Wronski, \"Volumetric Fog and Lighting\", SIGGRAPH 2014（ボリューム ライティング）"])

pg.Dedup("water/underwater/other.md")
pg.Add("water/underwater/other.md", '''
## 水中らしさを、作る、小さな要素

霧と、コースティクス、光の筋に加えて、**小さな、要素**を足すと、**水中の、雰囲気**が、大きく、変わります。

## 浮遊粒子（マリン スノー）

水中には、**細かい粒子**（プランクトンの死骸、泥、微生物）が、**ゆっくり**漂っています。カメラの周りに、**小さな、白い点**を、ゆっくり動かすだけで、**水中にいる**感じが、出ます。

| 項目 | 内容 |
| --- | --- |
| 数 | 数百〜数千個 |
| 大きさ | 小さい（数ピクセル）。**奥にあるほど、小さく** |
| 動き | ゆっくり、**漂い、ゆっくり沈む**。水流（フロー マップ）があれば、**流れに乗る** |
| 範囲 | カメラの周りの、**箱の中**。箱の外に出た粒子は、**反対側へ戻す**（ループ） |
| ライティング | **光の筋の中**で、明るく光る（散乱）。影の中は、暗い |
| 描画 | **加算ブレンド**、またはアルファ ブレンドの、小さな板（ビルボード） |

```hlsl
// 粒子: カメラの周りの箱の中に、ループさせる（箱の外に出ると、反対側に出る）。
float3 pos = initial_position + velocity * time;
pos = camera_position + fmod(pos - camera_position + box_size * 0.5, box_size) - box_size * 0.5;
```

**カメラの周りの箱の中だけ**に、粒子を置き、**箱の外に出た粒子は、反対側から、再登場**させると、**数百個**で、**無限に広がる、粒子の海**に見えます。

## 泡（気泡）

| 種類 | 内容 |
| --- | --- |
| 吐いた息（ダイバー） | プレイヤーの、口から、**大きな泡**が、上昇する。**だんだん、大きくなる**（水圧が下がる） |
| 水に落ちた、物の泡 | 水に入った瞬間、**多数の、小さな泡**。数秒で、水面へ上がる |
| スクリュー、物の動き | 船のスクリューの後ろに、**泡の帯** |
| 火山、熱水 | 地面から、**泡が、立ち上る** |

泡は、**パーティクル**で、表現します。**上に向かって、上昇し、ゆらゆら揺れ**、**水面で、消える**ように、します。

| パラメーター | 目安 |
| --- | --- |
| 上昇速度 | 0.2〜0.5 m/s |
| 揺れ | 左右に、小さな、サイン波 |
| 寿命 | 水面に着くまで（または、固定の時間） |
| 見た目 | **半透明の、丸**。縁が、明るく、中心が、透ける。小さな、**ハイライト** |

## 水の動き（ゆらぎ）

水中では、**水の流れ**で、**海藻が、ゆらゆら揺れ**、**物が、わずかに、漂い**ます。

| 要素 | 方法 |
| --- | --- |
| 海藻、サンゴ | 頂点シェーダーで、**ゆっくりした、揺れ**（[Wind](../../terrain/vegetation/wind.md) と、同じ方法を、ゆっくり、大きな、波長で） |
| 魚の群れ | ボイド（群れの、アルゴリズム）で、動かす。GPU で、数千匹 |
| 浮かぶごみ | 水の流れに、沿って、**ゆっくり**動かす |

水中の動きは、**空気中より、はるかに、ゆっくり**で、**周期も、長い**。同じ式でも、**速さの係数を、小さく**します。

## 画面の、歪み（水中のレンズ効果）

カメラが、水の中に入ると、**画面全体が、ゆらゆらと、歪んで**見えます（光が、波打つ水の中を、通るため。マスクを、通して見るときも、歪む）。

```hlsl
// ポストプロセス: 画面を、ゆっくり歪ませる。
float2 wobble = float2(
    sin(uv.y * 20.0 + time * 1.5),
    cos(uv.x * 20.0 + time * 1.2)) * 0.002;           // ごく小さく（0.002 程度）
float3 color = g_scene.Sample(g_linear_clamp, uv + wobble).rgb;
```

歪みは、**ごく、わずか**にします。強すぎると、**酔います**。

## 色補正

水中は、全体の、**色味**が、変わります。

| 要素 | 変更 |
| --- | --- |
| 彩度 | **下げる**（赤が失われ、全体が、青緑に偏る） |
| コントラスト | **下げる**（霧で、コントラストが落ちる） |
| 色相 | **青緑に、寄せる**（カラー グレーディング、[Color Grading](../../postprocess/color-grading/index.md)） |
| 周辺減光 | **強める**（暗い、閉じた視界の印象） |
| 被写界深度 | 遠くを、**ぼかす**（水の濁りで、遠くが、ぼやける） |

水に入った瞬間に、カラー グレーディングの、**LUT を、切り替える**（または、補間する）と、**水の中に入った**ことが、はっきり伝わります。

## 音

見た目だけでなく、**音**も、水中の、**雰囲気**を、大きく変えます。

| 要素 | 変更 |
| --- | --- |
| 周波数 | **高音を、カット**する（ローパス フィルタ）。水中では、こもった音になる |
| 反響 | 音が、**ぼやけて**、遠くまで届く |
| 環境音 | 水の、ごぼごぼ、という低音。泡の音 |
| 水面の、上の音 | **小さく、こもって**聞こえる（逆に、水面の上から、水中の音は、ほぼ聞こえない） |

水に入る、**境目**で、**フィルタを、なめらかに、切り替える**と、水中に入った感じが、出ます。

## 水に入った、瞬間と、出る瞬間

| 瞬間 | 演出 |
| --- | --- |
| 水に、入る | 水しぶき、泡、**画面の、水滴**、音の、フィルタ、霧と、色補正の、切り替え（数フレームで、補間） |
| 水から、出る | **画面を、水が、流れ落ちる**（レンズの水滴）、音が、元に戻る、霧と色補正が、元に戻る |

**瞬間的に、切り替える**と、不自然です。**水面を、またぐ間**（0.2〜0.5 秒）で、**補間**します（[The Underside of the Surface and Crossing It](surface-back.md)）。

''', before="## よくあるミス")
pg.Refs("water/underwater/other.md", [GUARDADO, MITCHELL, RTR, "Reynolds, \"Flocks, Herds, and Schools: A Distributed Behavioral Model\", SIGGRAPH 1987（ボイド（群れ）の原典）"])

pg.Dedup("water/underwater/surface-back.md")
pg.Add("water/underwater/surface-back.md", '''
## 水中から、水面を見上げる

水面を、**下から**見上げると、見え方が、**上から見たときと、まったく違います**。

| 見る角度 | 見え方 |
| --- | --- |
| **真上**（水面に、ほぼ垂直） | 水面が、**透けて**、空が、見える。明るい円（**スネルの窓**） |
| **浅い角度** | 水面が、**鏡**のように、水中の景色を、**反射**する（全反射） |
| **その間** | 窓の縁。**空の景色が、圧縮されて**、映る |

## スネルの窓

水中から、水面を見ると、**空が見える範囲が、円形に、限られます**。この円を、**スネルの窓**と呼びます。

```text
水中から見上げる
          空（全体が、窓の中に、圧縮されて見える）
         ╱  ╲
       ╱      ╲        ← 窓の外側は、水面が、鏡のように、水中を映す
      │  窓    │
       ╲      ╱
         ╲  ╱
          ●  カメラ（水中）
```

| 項目 | 値 |
| --- | --- |
| 臨界角 | `θ_c = asin(1 / 1.33) ≈ 48.6°`（真上から測った角度） |
| 窓の開き角 | `2 × 48.6° ≈ 97.2°`（円錐） |
| 窓の内側 | **空の全体（180°）**が、97.2° に、**圧縮**されて見える |
| 窓の外側 | **全反射**で、**水中の景色**が、水面に映る |

窓の**縁**に近づくほど、**水平に近い空の景色**が、見えます。**窓の縁で、空の地平線が、見えます**。

## 全反射

光が、**水から、空気へ**出るとき（`n₁ = 1.33`、`n₂ = 1.0`）、**入射角が、臨界角より大きい**と、**光は、外へ出られず、すべて、反射**します。**スネルの法則を、満たす、屈折角が、存在しない**（`sin θₜ > 1`）ためです。

```hlsl
// 水中から、水面を見上げるとき、屈折ベクトルを求める（HLSL の refract）。
// eta = n_水 / n_空気 = 1.33。屈折できないとき（全反射）、refract は、ゼロ ベクトルを返す。
float3 refracted = refract(view_dir, -wave_normal, 1.33);     // 水面の法線は、下向きに（水中から見る向き）
bool total_internal_reflection = dot(refracted, refracted) < 1e-5;
```

| 結果 | 意味 |
| --- | --- |
| `refracted` が、有効 | 空が、見える（窓の中）。`refracted` の向きで、**空を読む** |
| `refracted` が、ゼロ | **全反射**。水面が、**鏡**。反射ベクトル `reflect(view_dir, -wave_normal)` で、**水中の景色**（水底、水中の物）を読む |

```hlsl
// 水中から見た、水面の色。
float3 N = -wave_normal;                                     // 下向き（水中から見た、法線）
float3 refracted = refract(view_dir, N, 1.33);
float3 color;
if (dot(refracted, refracted) < 1e-5) {
  // 全反射: 水中の景色を、映す（水中の霧で、暗く青い）
  float3 r = reflect(view_dir, N);
  color = SampleUnderwaterReflection(r);
} else {
  // 窓の内側: 空が、見える
  float F = FresnelExact(saturate(dot(-view_dir, N)), 1.0 / 1.33);   // 水から空気への、反射率
  float3 sky = SampleSky(refracted);
  float3 refl = SampleUnderwaterReflection(reflect(view_dir, N));
  color = lerp(sky, refl, F);
}
```

窓の、内側でも、**一部は、反射**します（フレネル）。窓の縁に近づくほど、反射の割合が、**1 に近づく**（全反射へ、なめらかに、つながる）。**フレネルの式を、正しく使う**と、窓の縁が、なめらかに、**自然**に見えます（[Water Fresnel](../shading/fresnel.md)）。

## 水面を、下から描く

水面の、メッシュを、**裏側から**描く必要があります。

| 項目 | 内容 |
| --- | --- |
| カリング | 通常、水面は、**上から見る**前提で、裏面を、描かない。水中では、**裏面を描く**（カリングを、切り替える、または、無効にする） |
| 法線 | **水面の法線を、反転**する（水中から見ると、下向きが、表） |
| シェーダー | 水中用の、**別のシェーダー**を使う（反射、屈折、フレネルの、向きが、逆） |
| 霧 | 水面の、**手前**（カメラ側）は、水中なので、水中の霧を、かける |

```cpp
// カメラが、水の中にあるか。波の高さを、カメラの位置で調べる。
bool IsUnderwater(const float3& camera_position) {
  return camera_position.y < WaterHeightAt({camera_position.x, camera_position.z}, time);
}

// 水中なら、水面を、裏から、描く（ラスタライザー ステートを切り替える）。
context->RSSetState(underwater ? rs_cull_front.Get() : rs_cull_back.Get());
```

`rs_cull_front` は、**表面を、カリング**する（裏面だけを描く）ステートです。

## 水面を、またぐ

カメラが、**水面を、通り抜ける**とき、**画面の半分が、水中、半分が、空気中**になります。

```text
  ──────────────  空気中（画面の上半分）
  ~~~~~~~~~~~~~~  ← 水面の線（カメラが、水面にある）
  ──────────────  水中（画面の下半分）
```

| 問題 | 内容 |
| --- | --- |
| 画面の半分に、水中の霧が、必要 | 水中の霧は、**カメラが、水の中にあるとき**に、全画面に、かける。**半分だけ**は、できない |
| 近クリップ面 | 近クリップ面が、水面を、切ると、**水面が、一瞬消える**（近クリップで、切れる）。水面の、メッシュが、カメラの前を、通過する |
| 水面の、メッシュの、厚み | 水面が、薄い**面**だと、近クリップ面に、**切断**される。切断された、部分は、**水面が、見えなくなり**、水中と空気中の境目が、見える |

### 対策：水面の、ボリューム

水面の下に、**水の、ボリューム（箱、または、メッシュ）**を、置きます。カメラが、水面を、またいでいるとき、**カメラの前の、近クリップ面が、水のボリュームの中にある**部分だけを、**水中の霧で、塗ります**。

| 方法 | 内容 |
| --- | --- |
| ステンシル | **水の、ボリュームの、裏面と、表面**を、ステンシルに描く。**水の中にいる、画素**を、判定して、水中の霧を、かける |
| 水面の高さで、判定 | **画素ごとに、視線と、水面の交点**を、求め、**水面より、手前**が、水の中か、判定する |
| 水面の線を、描く | 画面に、**水面の線**（ウォーターライン）を、描く。上は、空気、下は、水中の見た目。画面の水平の線ではなく、**波の形**で |

```hlsl
// ポストプロセス: 各画素の、視線方向の点が、水面の下か上かで、水中の霧を、かけ分ける。
float3 world_pos = ReconstructWorldPosition(uv, depth);
float surface_y = WaterHeightAt(world_pos.xz);

if (camera_position.y < surface_y) {
  // カメラは、水中: 全画素に、水中の霧（距離に応じて）をかける。
} else {
  // カメラは、水面の上: 水面の、手前の画素は、空気中。水面より、下にある、水中の画素に、水中の霧をかける。
  // 画素が、水の下にある（world_pos.y < surface_y）なら、水中の霧を、水に入った距離ぶん、かける。
}
```

水面を、またぐ瞬間の、**画面の、きれいな切り替え**は、**難しい**ので、**実際の作品でも**、**わずかなごまかし**（短い、フェード、水面の線の強調）が、使われています。

## 水面の、すぐ下

水面の、すぐ下にいるとき、**水面の、波が、天井のように**見えます。

| 要素 | 内容 |
| --- | --- |
| 揺れる光 | 水面を通った光が、**コースティクスとして、水中の物に、映る**（[Caustics](caustics.md)） |
| 水面の、裏の、色 | 空が、見える（窓の中）。窓の外は、**水中の景色が、映る** |
| 泡 | 水に入った、泡が、**水面の、すぐ下に、たまり**、白い、層になる |
| 水面の、法線 | 波で、細かく、傾く。窓の形が、**揺れて**歪む |

''', before="## よくあるミス")
pg.Refs("water/underwater/surface-back.md", [RTR, "Hecht, \"Optics\", 5th Edition, Pearson, 2016（スネルの法則、全反射、スネルの窓）", "Lynch, Livingston, \"Color and Light in Nature\", 2nd Edition, Cambridge University Press, 2001（水中から見た景色）", TESSENDORF])
pg.Refs("water/underwater/index.md", [GUARDADO, MITCHELL, POPE, TESSENDORF])
print("ok")
