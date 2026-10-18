---
title: 法線とライティング
tags:
  - 3Dゲーム
---

# 法線とライティング

3D の物体に**陰影**をつけるには、**面がどちらを向いているか**（**法線**）と、**光がどちらから来るか**が必要です。このページは法線の意味、ランバート拡散とブリン・フォンのスペキュラ、**法線を変換するときの落とし穴**（逆転置行列）、DX11 / HLSL のシェーダー例をまとめます。

!!! tip "ポイント"
    - <strong>法線</strong>は<strong>面に垂直な、長さ 1 のベクトル</strong>。頂点に持たせる。
    - <strong>拡散光（ランバート）</strong>は、<strong>`max(dot(N, L), 0)`</strong>。<strong>L は面から光への向き</strong>。
    - <strong>スペキュラ（ブリン・フォン）</strong>は、<strong>`pow(max(dot(N, H), 0), 光沢)`</strong>。H は光と視線の中間。
    - <strong>法線はワールド行列では変換しない</strong>。<strong>逆転置行列</strong>で変換する（非一様スケールがあるとき）。
    - シェーダーで<strong>法線を毎回 `normalize`</strong> する（補間で長さがずれる）。
    - ライトの向きは、<strong>光が進む向きではなく、光源へ向かう向き</strong>で持つと、計算が楽。

## 法線

**法線**は**面に垂直な、長さ 1 のベクトル**です。陰影の計算の中心です。

<svg class="fig" viewBox="0 0 380 140" role="img" aria-label="面と法線"><defs><marker id="ah2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><line x1="40" y1="110" x2="320" y2="110" stroke="currentColor" stroke-width="3"/><text x="326" y="115">面</text><line x1="180" y1="110" x2="180" y2="30" stroke="currentColor" stroke-width="2" marker-end="url(#ah2)"/><text x="190" y="45">N（法線：面に垂直・長さ 1）</text><rect x="174" y="104" width="12" height="12" fill="none" stroke="currentColor"/></svg>

### 面法線と頂点法線

<svg class="fig" viewBox="0 0 575 200" role="img" aria-label="面法線と頂点法線"><defs><marker id="m1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="22" class="fig-title">面法線（フラット）：面ごとに 1 つ</text><polyline points="30,150 110,110 190,150 270,110" fill="none" stroke="currentColor" stroke-width="3"/><line x1="70" y1="130" x2="58" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="150" y1="130" x2="162" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="230" y1="130" x2="218" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><text x="30" y="182">法線が面ごとに変わる → カクカク</text><text x="310" y="22" class="fig-title">頂点法線（スムース）：頂点ごとに平均</text><polyline points="310,150 390,110 470,150 550,110" fill="none" stroke="currentColor" stroke-width="3"/><line x1="310" y1="150" x2="310" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="390" y1="110" x2="390" y2="60" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="470" y1="150" x2="470" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="550" y1="110" x2="550" y2="60" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><text x="310" y="182">三角形の中で補間 → 滑らかに見える</text></svg>

| 種類 | 説明 | 見た目 |
| --- | --- | --- |
| **面法線** | 三角形ごとに 1 つ（外積で求める） | **カクカク**（フラットシェーディング） |
| **頂点法線** | 頂点ごとに持つ。**隣り合う面の法線の平均** | **滑らか**（スムースシェーディング） |

```cpp
Vector3 FaceNormal(const Vector3& v0, const Vector3& v1, const Vector3& v2) {
  Vector3 n = (v1 - v0).Cross(v2 - v0);
  n.Normalize();
  return n;
}
```

**CW（時計回り）が表の三角形**なら、<strong>`Cross(v1 - v0, v2 - v0)` の向きが表（外向き）</strong>になります（左手系）。巻き順が逆だと法線が内向きになり、**暗く**なります。

## 拡散光（ランバート）

<svg class="fig" viewBox="0 0 609 240" role="img" aria-label="ランバート拡散光"><defs><marker id="m2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><line x1="40" y1="200" x2="300" y2="200" stroke="currentColor" stroke-width="3"/><line x1="170" y1="200" x2="170" y2="70" stroke="currentColor" stroke-width="2" marker-end="url(#m2)" /><text x="178" y="80">N（法線）</text><line x1="170" y1="200" x2="270" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m2)" /><text x="275" y="84">L（面→光源）</text><path d="M 170 150 A 50 50 0 0 1 205 165" fill="none" stroke="currentColor"/><text x="200" y="150">θ</text><text x="330" y="60" class="fig-title">明るさ ＝ max( dot(N, L), 0 ) ＝ cosθ</text><text x="330" y="100">θ = 0°（正面）　　→ 1（最大）</text><text x="330" y="125">θ = 60°　　　　　　→ 0.5</text><text x="330" y="150">θ = 90°（真横）　　→ 0</text><text x="330" y="175">θ &gt; 90°（裏側）　　→ 0（負は 0 に）</text></svg>

面が**光に向いているほど明るく**、横を向くと**暗く**なります。**法線と光への向きの内積**で決まります。

```text
明るさ = max( dot(N, L), 0 )

N と L が同じ向き → 1（最大）　　直角 → 0　　逆向き → 0（負は 0 にする）
```

**L は面から光源へ向かう向き**です。光が上から下へ進む（`(0, -1, 0)`）なら、**L は `(0, 1, 0)`** です。逆にすると陰影が反転します。

## スペキュラ（ブリン・フォン）

<svg class="fig" viewBox="0 0 680 240" role="img" aria-label="ブリン・フォンのハーフベクトル"><defs><marker id="m3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><line x1="40" y1="200" x2="360" y2="200" stroke="currentColor" stroke-width="3"/><line x1="200" y1="200" x2="200" y2="60" stroke="currentColor" stroke-width="2" marker-end="url(#m3)" /><text x="206" y="66">N</text><line x1="200" y1="200" x2="90" y2="90" stroke="currentColor" stroke-width="2" marker-end="url(#m3)" /><text x="60" y="84">L（光源へ）</text><line x1="200" y1="200" x2="310" y2="90" stroke="currentColor" stroke-width="2" marker-end="url(#m3)" /><text x="296" y="84">V（カメラへ）</text><line x1="200" y1="200" x2="200" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#m3)" stroke-dasharray="5 4"/><text x="380" y="60" class="fig-title">H ＝ normalize(L + V)</text><text x="380" y="90">L と V の、ちょうど真ん中の向き</text><text x="380" y="120">N と H が重なるほど、ハイライトが強い</text><text x="380" y="150">pow( max(dot(N, H), 0), 光沢 )</text><text x="380" y="180">鏡のように反射する向きに、カメラがあると光る</text></svg>

**ツヤのある反射**（ハイライト）です。**視線と光の中間のベクトル H** を使います。

```text
H = normalize(L + V)          V は、面から、カメラへの向き
スペキュラ = pow( max(dot(N, H), 0), 光沢 )
```

| 光沢（shininess） | 見た目 |
| --- | --- |
| 小さい（8 など） | ぼんやり広いハイライト（ゴム） |
| 大きい（128 など） | 小さく鋭いハイライト（金属・ガラス） |

## ライトの種類

<svg class="fig" viewBox="0 0 616 220" role="img" aria-label="ライトの種類"><defs><marker id="m4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">ディレクショナル</text><line x1="30" y1="40" x2="50" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="70" y1="40" x2="90" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="110" y1="40" x2="130" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="150" y1="40" x2="170" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="10" y1="170" x2="190" y2="170" stroke="currentColor" stroke-width="3"/><text x="30" y="200">全体が、同じ向き（太陽）</text><text x="225" y="20" class="fig-title">ポイント</text><circle cx="300" cy="90" r="8" fill="currentColor"/><line x1="300" y1="90" x2="300" y2="30" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="355" y2="50" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="365" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="340" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="260" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="235" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="245" y2="50" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><text x="225" y="200">位置から四方へ（電球）。距離で減る</text><text x="430" y="20" class="fig-title">スポット</text><circle cx="480" cy="40" r="8" fill="currentColor"/><polygon points="480,40 420,170 540,170" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/><line x1="480" y1="40" x2="480" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><text x="420" y="200">位置・向き・角度（懐中電灯）</text></svg>

| 種類 | 向き | 減衰 | 用途 |
| --- | --- | --- | --- |
| **ディレクショナル** | 全体で同じ向き | なし | 太陽、月 |
| **ポイント** | 光源の位置から、四方へ | 距離で減る | 電球、松明、爆発 |
| **スポット** | 位置 + 向き + 角度の制限 | 距離と角度 | 懐中電灯、ヘッドライト |
| <strong>環境光（アンビエント）</strong> | なし | なし | 影の部分が真っ黒にならないための、一定の明るさ |

## HLSL の例（DX11）

<svg class="fig flow" viewBox="0 0 1201 112" role="img" aria-label="ライティングの流れ：頂点で法線を渡し、ピクセルごとに明るさを計算する"><defs><marker id="fl94" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ライティングの流れ：頂点で法線を渡し、ピクセルごとに明るさを計算する</text><line x1="163.0" y1="64.0" x2="221.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl94)"/><text x="192.0" y="58.0" text-anchor="middle" style="font-size:12px">逆転置行列で</text><line x1="457.0" y1="64.0" x2="515.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl94)"/><text x="486.0" y="58.0" text-anchor="middle" style="font-size:12px">三角形の中を</text><line x1="695.0" y1="64.0" x2="753.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl94)"/><text x="724.0" y="58.0" text-anchor="middle" style="font-size:12px">N・L・V を使う</text><line x1="1030.0" y1="64.0" x2="1088.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl94)"/><rect x="28.0" y="44.0" width="132" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="94.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">頂点 法線を持つ</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="224.0" y="44.0" width="230" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="339.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">頂点シェーダー ワールドへ変換</text><circle cx="226.0" cy="46.0" r="10" fill="#2ea043"/><text x="226.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="518.0" y="44.0" width="174" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="605.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">補間 （ラスタライズ）</text><circle cx="520.0" cy="46.0" r="10" fill="#e5a828"/><text x="520.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="756.0" y="44.0" width="271" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="891.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ピクセルシェーダー normalize・内積</text><circle cx="758.0" cy="46.0" r="10" fill="#e5484d"/><text x="758.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="1091.0" y="44.0" width="82" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="1132.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">画面の色</text><circle cx="1093.0" cy="46.0" r="10" fill="#9664e6"/><text x="1093.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text></svg>

<svg class="fig" viewBox="0 0 640 200" role="img" aria-label="環境光・拡散光・スペキュラの合成"><defs><radialGradient id="g1" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#7a7f8a"/><stop offset="1" stop-color="#7a7f8a"/></radialGradient><radialGradient id="g2" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#e8e8ee"/><stop offset="0.6" stop-color="#7a7f8a"/><stop offset="1" stop-color="#15171c"/></radialGradient><radialGradient id="g3" cx="35%" cy="30%" r="22%"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#000000"/></radialGradient><radialGradient id="g4" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#ffffff"/><stop offset="0.12" stop-color="#e8e8ee"/><stop offset="0.6" stop-color="#7a7f8a"/><stop offset="1" stop-color="#1e2026"/></radialGradient></defs><circle cx="70" cy="90" r="55" fill="#3c3f47"/><text x="22" y="170">環境光（一定）</text><text x="145" y="98" class="fig-title">＋</text><circle cx="230" cy="90" r="55" fill="url(#g2)"/><text x="170" y="170">拡散光（ランバート）</text><text x="305" y="98" class="fig-title">＋</text><circle cx="390" cy="90" r="55" fill="url(#g3)"/><text x="335" y="170">スペキュラ</text><text x="465" y="98" class="fig-title">＝</text><circle cx="550" cy="90" r="55" fill="url(#g4)"/><text x="520" y="170">完成</text></svg>

### 頂点シェーダーとピクセルシェーダー

```hlsl
cbuffer Transform : register(b0) {
  row_major float4x4 world;
  row_major float4x4 world_inverse_transpose;
  row_major float4x4 view_proj;
};

cbuffer Light : register(b1) {
  float3 light_direction;   // 面から光源へ向かう向き（正規化済み）
  float pad0;
  float3 light_color;
  float pad1;
  float3 camera_position;
  float shininess;
};

struct VsInput {
  float3 position : POSITION;
  float3 normal : NORMAL;
  float2 uv : TEXCOORD0;
};

struct VsOutput {
  float4 position : SV_POSITION;
  float3 world_position : TEXCOORD1;
  float3 normal : TEXCOORD2;
  float2 uv : TEXCOORD0;
};

VsOutput VSMain(VsInput input) {
  VsOutput output;
  float4 world_pos = mul(float4(input.position, 1.0f), world);
  output.position = mul(world_pos, view_proj);
  output.world_position = world_pos.xyz;
  output.normal = mul(input.normal, (float3x3)world_inverse_transpose);
  output.uv = input.uv;
  return output;
}

Texture2D albedo_texture : register(t0);
SamplerState linear_sampler : register(s0);

float4 PSMain(VsOutput input) : SV_TARGET {
  float3 n = normalize(input.normal);
  float3 l = normalize(light_direction);
  float3 v = normalize(camera_position - input.world_position);
  float3 h = normalize(l + v);

  float diffuse = max(dot(n, l), 0.0f);
  float specular = pow(max(dot(n, h), 0.0f), shininess) * step(0.0f, diffuse);
  float3 ambient = float3(0.1f, 0.1f, 0.12f);

  float3 albedo = albedo_texture.Sample(linear_sampler, input.uv).rgb;
  float3 color = albedo * (ambient + light_color * diffuse) + light_color * specular;
  return float4(color, 1.0f);
}
```

| ポイント | 説明 |
| --- | --- |
| **`row_major`** | SimpleMath の行列を、そのまま渡すため（[MVP](transforms-mvp.md)） |
| **`mul(ベクトル, 行列)`** | 行ベクトル規約 |
| **ピクセルシェーダーで `normalize`** | 頂点から補間された法線は、長さが 1 からずれる |
| **`float pad`** | 定数バッファの **16 バイト境界**（`float3` の後ろに詰め物） |
| **`step(0, diffuse)`** | 光が当たっていない面に、ハイライトが出ないように |

### C++ 側の定数バッファ

```cpp
struct TransformCB {
  Matrix world;
  Matrix world_inverse_transpose;
  Matrix view_proj;
};

struct LightCB {
  Vector3 direction;
  float pad0;
  Vector3 color;
  float pad1;
  Vector3 camera_position;
  float shininess;
};

TransformCB cb;
cb.world = world;
cb.world_inverse_transpose = world.Invert().Transpose();
cb.view_proj = view * proj;
```

**C++ と HLSL の構造体の並びを、そろえます**。`float3` の次に `float` を置くと、ちょうど 16 バイトに収まります。

## 法線の変換（逆転置行列）

<svg class="fig" viewBox="0 0 629 230" role="img" aria-label="非一様スケールで法線がずれる"><defs><marker id="m5" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="22" class="fig-title">元の面（45°）と法線</text><line x1="40" y1="170" x2="160" y2="70" stroke="currentColor" stroke-width="3"/><line x1="100" y1="120" x2="140" y2="76" stroke="currentColor" stroke-width="2" marker-end="url(#m5)" /><text x="200" y="22" class="fig-title">X を 3 倍にすると</text><line x1="210" y1="170" x2="360" y2="130" stroke="currentColor" stroke-width="3"/><line x1="285" y1="150" x2="345" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#m5)" stroke-dasharray="4 3"/><line x1="285" y1="150" x2="303" y2="88" stroke="currentColor" stroke-width="2" marker-end="url(#m5)" /><text x="210" y="205">破線：面と同じ変換をした法線（垂直でなくなる）</text><text x="210" y="222">実線：逆転置行列で変換した法線（垂直のまま）</text><text x="420" y="22" class="fig-title">法線は「向き」</text><text x="420" y="60">面と垂直であることを</text><text x="420" y="85">保つ変換が必要</text><text x="420" y="120">→ transpose( inverse(World) )</text></svg>

!!! warning "法線を、ワールド行列で変換してはいけない"
    **非一様スケール**（`Scale(2, 1, 1)` など）があると法線が**面に垂直でなくなります**。法線は**ワールド行列の逆行列の転置**で変換します。

```text
位置：  p' = p × World
法線：  n' = n × transpose( inverse(World) )   → normalize
```

| 場面 | 法線の変換 |
| --- | --- |
| **回転と平行移動だけ**（スケールなし） | ワールド行列の回転部分で、よい |
| **一様スケール**（`Scale(2,2,2)`） | 回転部分でよい。**`normalize`** は必須 |
| **非一様スケール** | **逆転置行列が必要** |
| **迷ったら** | **逆転置行列**（安全） |

逆転置行列は**物体ごとに、C++ で 1 回**計算して、定数バッファで渡します。**ピクセルごとにシェーダーで逆行列を計算しません**（重い）。

## 法線マップ

<svg class="fig" viewBox="0 0 560 220" role="img" aria-label="接空間と TBN"><defs><marker id="m6" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><polygon points="60,180 300,180 380,110 140,110" fill="none" stroke="currentColor" stroke-width="2"/><line x1="220" y1="150" x2="300" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m6)" /><text x="304" y="154">T（接線：U の向き）</text><line x1="220" y1="150" x2="250" y2="112" stroke="currentColor" stroke-width="2" marker-end="url(#m6)" /><text x="254" y="108">B（従接線：V の向き）</text><line x1="220" y1="150" x2="220" y2="55" stroke="currentColor" stroke-width="2" marker-end="url(#m6)" /><text x="228" y="62">N（法線）</text><text x="20" y="22" class="fig-title">TBN：面の上の座標系</text><text x="400" y="190">法線マップの値を、</text><text x="400" y="210">この座標系でワールドへ</text></svg>

**テクスチャで細かい凹凸の法線**を与えると、**頂点数を増やさず**、凹凸を表現できます。

| 要素 | 説明 |
| --- | --- |
| **法線マップ** | RGB に法線の XYZ（`0..1` → `-1..1`）を入れた、テクスチャ |
| <strong>接空間（タンジェント空間）</strong> | 法線マップの座標系。頂点に<strong>接線（tangent）</strong> が必要 |
| **TBN 行列** | 接線・従接線・法線から作る、接空間 → ワールドの変換 |

法線マップは**法線の向きがモデルの表面に沿っている**前提です。**Y 軸の向き（OpenGL 系と DirectX 系）の違い**で凹凸が反転することがあります。

## ライトの計算の注意

| 注意 | 説明 |
| --- | --- |
| **ポイントライトの L** | `normalize(light_position - world_position)`。**ピクセルごと**に求める |
| **減衰** | `1 / (1 + k1*d + k2*d*d)` など。**範囲外は 0**にする |
| <strong>色空間（ガンマ）</strong> | 計算は**リニア**空間。表示の前にガンマ補正（sRGB のレンダーターゲットなら、自動） |
| **HDR・トーンマッピング** | 明るさが 1 を超えるなら、トーンマッピングで画面に収める |
| **コストの目安** | ピクセルごとの計算。ライト数に比例。多数なら、ディファード・タイルベース |

<!-- fig:lambert-curves:begin -->

<svg class="fig illust motion" data-fig="lambert-curves" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lambert-curves" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">光の当たり方: 面と光の角度で、明るさが変わる</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">明るさ</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">光の向きと法線の角度 (度)</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<text x="230.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">45</text>
<text x="390.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">90</text>
<text x="550.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">135</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">180</text>
<path d="M70.0,81.43 L75.33,81.51 L80.67,81.74 L86.0,82.13 L91.33,82.68 L96.67,83.38 L102.0,84.24 L107.33,85.26 L112.67,86.42 L118.0,87.74 L123.33,89.22 L128.67,90.84 L134.0,92.62 L139.33,94.54 L144.67,96.61 L150.0,98.83 L155.33,101.19 L160.67,103.69 L166.0,106.34 L171.33,109.13 L176.67,112.05 L182.0,115.11 L187.33,118.3 L192.67,121.63 L198.0,125.08 L203.33,128.66 L208.67,132.37 L214.0,136.19 L219.33,140.14 L224.67,144.2 L230.0,148.38 L235.33,152.66 L240.67,157.06 L246.0,161.55 L251.33,166.16 L256.67,170.85 L262.0,175.65 L267.33,180.54 L272.67,185.51 L278.0,190.57 L283.33,195.71 L288.67,200.94 L294.0,206.23 L299.33,211.6 L304.67,217.03 L310.0,222.53 L315.33,228.09 L320.67,233.7 L326.0,239.37 L331.33,245.08 L336.67,250.84 L342.0,256.64 L347.33,262.48 L352.67,268.35 L358.0,274.24 L363.33,280.17 L368.67,286.11 L374.0,292.07 L379.33,298.04 L384.67,304.02 L390.0,310.0 L395.33,310.0 L400.67,310.0 L406.0,310.0 L411.33,310.0 L416.67,310.0 L422.0,310.0 L427.33,310.0 L432.67,310.0 L438.0,310.0 L443.33,310.0 L448.67,310.0 L454.0,310.0 L459.33,310.0 L464.67,310.0 L470.0,310.0 L475.33,310.0 L480.67,310.0 L486.0,310.0 L491.33,310.0 L496.67,310.0 L502.0,310.0 L507.33,310.0 L512.67,310.0 L518.0,310.0 L523.33,310.0 L528.67,310.0 L534.0,310.0 L539.33,310.0 L544.67,310.0 L550.0,310.0 L555.33,310.0 L560.67,310.0 L566.0,310.0 L571.33,310.0 L576.67,310.0 L582.0,310.0 L587.33,310.0 L592.67,310.0 L598.0,310.0 L603.33,310.0 L608.67,310.0 L614.0,310.0 L619.33,310.0 L624.67,310.0 L630.0,310.0 L635.33,310.0 L640.67,310.0 L646.0,310.0 L651.33,310.0 L656.67,310.0 L662.0,310.0 L667.33,310.0 L672.67,310.0 L678.0,310.0 L683.33,310.0 L688.67,310.0 L694.0,310.0 L699.33,310.0 L704.67,310.0 L710.0,310.0" fill="none" stroke="#e5484d" stroke-width="4" opacity="1"/>
<path d="M70.0,81.43 L75.33,81.51 L80.67,81.74 L86.0,82.13 L91.33,82.68 L96.67,83.38 L102.0,84.23 L107.33,85.24 L112.67,86.4 L118.0,87.7 L123.33,89.15 L128.67,90.74 L134.0,92.48 L139.33,94.35 L144.67,96.36 L150.0,98.5 L155.33,100.76 L160.67,103.15 L166.0,105.66 L171.33,108.29 L176.67,111.03 L182.0,113.87 L187.33,116.82 L192.67,119.86 L198.0,123.0 L203.33,126.22 L208.67,129.53 L214.0,132.91 L219.33,136.37 L224.67,139.89 L230.0,143.47 L235.33,147.11 L240.67,150.8 L246.0,154.53 L251.33,158.3 L256.67,162.11 L262.0,165.94 L267.33,169.79 L272.67,173.66 L278.0,177.54 L283.33,181.43 L288.67,185.31 L294.0,189.19 L299.33,193.07 L304.67,196.92 L310.0,200.75 L315.33,204.56 L320.67,208.34 L326.0,212.08 L331.33,215.79 L336.67,219.45 L342.0,223.06 L347.33,226.63 L352.67,230.13 L358.0,233.58 L363.33,236.97 L368.67,240.29 L374.0,243.54 L379.33,246.72 L384.67,249.83 L390.0,252.86 L395.33,255.81 L400.67,258.68 L406.0,261.47 L411.33,264.18 L416.67,266.8 L422.0,269.34 L427.33,271.79 L432.67,274.15 L438.0,276.42 L443.33,278.61 L448.67,280.71 L454.0,282.72 L459.33,284.64 L464.67,286.47 L470.0,288.22 L475.33,289.89 L480.67,291.47 L486.0,292.96 L491.33,294.38 L496.67,295.71 L502.0,296.97 L507.33,298.15 L512.67,299.26 L518.0,300.29 L523.33,301.25 L528.67,302.15 L534.0,302.98 L539.33,303.74 L544.67,304.45 L550.0,305.1 L555.33,305.69 L560.67,306.23 L566.0,306.72 L571.33,307.16 L576.67,307.56 L582.0,307.92 L587.33,308.23 L592.67,308.51 L598.0,308.76 L603.33,308.97 L608.67,309.16 L614.0,309.32 L619.33,309.46 L624.67,309.57 L630.0,309.67 L635.33,309.75 L640.67,309.81 L646.0,309.86 L651.33,309.9 L656.67,309.93 L662.0,309.96 L667.33,309.97 L672.67,309.98 L678.0,309.99 L683.33,310.0 L688.67,310.0 L694.0,310.0 L699.33,310.0 L704.67,310.0 L710.0,310.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<text x="119.78" y="236.86" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">赤: ランバート max(0, N·L)</text>
<text x="119.78" y="268.86" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">青: ハーフランバート</text>
<circle cx="70.0" cy="81.43" r="7" fill="#e5484d"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0741;0.0844;0.0947;0.1049;0.1152;0.1255;0.1358;0.1461;0.1564;0.1667;0.1770;0.1872;0.1975;0.2078;0.2181;0.2284;0.2387;0.2490;0.2593;0.2695;0.2798;0.2901;0.3004;0.3107;0.3210;0.3313;0.3416;0.3519;0.3621;0.3724;0.3827;0.3930;0.4033;0.4136;0.4239;0.4342;0.4444;0.4547;0.4650;0.4753;0.4856;0.4959;0.5062;0.5165;0.5267;0.5370;0.5473;0.5576;0.5679;0.5782;0.5885;0.5988;0.6091;0.6193;0.6296;0.6399;0.6502;0.6605;0.6708;0.6811;0.6914;0.7016;0.7119;0.7222;0.7325;0.7428;0.7531;0.7634;0.7737;0.7840;0.7942;0.8045;0.8148;1.0000" values="70;70;78.89;87.78;96.67;105.56;114.44;123.33;132.22;141.11;150;158.89;167.78;176.67;185.56;194.44;203.33;212.22;221.11;230;238.89;247.78;256.67;265.56;274.44;283.33;292.22;301.11;310;318.89;327.78;336.67;345.56;354.44;363.33;372.22;381.11;390;398.89;407.78;416.67;425.56;434.44;443.33;452.22;461.11;470;478.89;487.78;496.67;505.56;514.44;523.33;532.22;541.11;550;558.89;567.78;576.67;585.56;594.44;603.33;612.22;621.11;630;638.89;647.78;656.67;665.56;674.44;683.33;692.22;701.11;710;710"/><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0741;0.0844;0.0947;0.1049;0.1152;0.1255;0.1358;0.1461;0.1564;0.1667;0.1770;0.1872;0.1975;0.2078;0.2181;0.2284;0.2387;0.2490;0.2593;0.2695;0.2798;0.2901;0.3004;0.3107;0.3210;0.3313;0.3416;0.3519;0.3621;0.3724;0.3827;0.3930;0.4033;0.4136;0.4239;0.4342;0.4444;0.4547;0.4650;0.4753;0.4856;0.4959;0.5062;0.5165;0.5267;0.5370;0.5473;0.5576;0.5679;0.5782;0.5885;0.5988;0.6091;0.6193;0.6296;0.6399;0.6502;0.6605;0.6708;0.6811;0.6914;0.7016;0.7119;0.7222;0.7325;0.7428;0.7531;0.7634;0.7737;0.7840;0.7942;0.8045;0.8148;1.0000" values="81.43;81.43;81.65;82.3;83.38;84.9;86.85;89.22;92.01;95.21;98.83;102.84;107.25;112.05;117.22;122.77;128.66;134.9;141.48;148.38;155.58;163.08;170.85;178.9;187.19;195.71;204.46;213.4;222.53;231.82;241.27;250.84;260.53;270.31;280.17;290.08;300.03;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310;310"/></circle>
<circle cx="70.0" cy="81.43" r="7" fill="#2563eb"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0741;0.0844;0.0947;0.1049;0.1152;0.1255;0.1358;0.1461;0.1564;0.1667;0.1770;0.1872;0.1975;0.2078;0.2181;0.2284;0.2387;0.2490;0.2593;0.2695;0.2798;0.2901;0.3004;0.3107;0.3210;0.3313;0.3416;0.3519;0.3621;0.3724;0.3827;0.3930;0.4033;0.4136;0.4239;0.4342;0.4444;0.4547;0.4650;0.4753;0.4856;0.4959;0.5062;0.5165;0.5267;0.5370;0.5473;0.5576;0.5679;0.5782;0.5885;0.5988;0.6091;0.6193;0.6296;0.6399;0.6502;0.6605;0.6708;0.6811;0.6914;0.7016;0.7119;0.7222;0.7325;0.7428;0.7531;0.7634;0.7737;0.7840;0.7942;0.8045;0.8148;1.0000" values="70;70;78.89;87.78;96.67;105.56;114.44;123.33;132.22;141.11;150;158.89;167.78;176.67;185.56;194.44;203.33;212.22;221.11;230;238.89;247.78;256.67;265.56;274.44;283.33;292.22;301.11;310;318.89;327.78;336.67;345.56;354.44;363.33;372.22;381.11;390;398.89;407.78;416.67;425.56;434.44;443.33;452.22;461.11;470;478.89;487.78;496.67;505.56;514.44;523.33;532.22;541.11;550;558.89;567.78;576.67;585.56;594.44;603.33;612.22;621.11;630;638.89;647.78;656.67;665.56;674.44;683.33;692.22;701.11;710;710"/><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0741;0.0844;0.0947;0.1049;0.1152;0.1255;0.1358;0.1461;0.1564;0.1667;0.1770;0.1872;0.1975;0.2078;0.2181;0.2284;0.2387;0.2490;0.2593;0.2695;0.2798;0.2901;0.3004;0.3107;0.3210;0.3313;0.3416;0.3519;0.3621;0.3724;0.3827;0.3930;0.4033;0.4136;0.4239;0.4342;0.4444;0.4547;0.4650;0.4753;0.4856;0.4959;0.5062;0.5165;0.5267;0.5370;0.5473;0.5576;0.5679;0.5782;0.5885;0.5988;0.6091;0.6193;0.6296;0.6399;0.6502;0.6605;0.6708;0.6811;0.6914;0.7016;0.7119;0.7222;0.7325;0.7428;0.7531;0.7634;0.7737;0.7840;0.7942;0.8045;0.8148;1.0000" values="81.43;81.43;81.65;82.3;83.38;84.89;86.81;89.15;91.89;95.01;98.5;102.34;106.53;111.03;115.82;120.9;126.22;131.78;137.54;143.47;149.57;155.79;162.11;168.51;174.95;181.43;187.9;194.35;200.75;207.08;213.32;219.45;225.44;231.29;236.97;242.46;247.76;252.86;257.73;262.38;266.8;270.98;274.92;278.61;282.06;285.26;288.22;290.95;293.44;295.71;297.77;299.61;301.25;302.71;303.99;305.1;306.06;306.87;307.56;308.13;308.6;308.97;309.27;309.5;309.67;309.79;309.88;309.93;309.97;309.99;310;310;310;310;310"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">0 度（真正面から当たる）: どちらも最大 1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2590;0.2593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">45 度: ランバート 0.71、ハーフランバート 0.73<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;0.4441;0.4444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">90 度（真横）: ランバートは 0、ハーフは 0.25 でまだ見える<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4444;0.6293;0.6296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">90 度を超える（裏側）: ランバートは真っ黒のまま<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;0.8145;0.8148;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:lambert-curves:end -->

## よくあるミス

??? failure "陰影が、反転して見える"
    **L の向き**が逆です。L は**面から光源へ**向かう向きです。

??? failure "拡大・縮小した物体の陰影がおかしい"
    法線をワールド行列で変換しています。**逆転置行列**を使います。

??? failure "カクカク・ギザギザに見える"
    頂点法線が面法線のままです。**隣の面の法線を平均**します。

??? failure "ハイライトが、光の反対側に出る"
    スペキュラの H や V の向きが、逆です。V は**面から、カメラへ**。

??? failure "モデル全体が、暗い"
    法線が**内向き**（巻き順の間違い）、または、`normalize` していません。

??? failure "定数バッファの値が、ずれる"
    `float3` の後ろに、詰め物が足りません。**16 バイト境界**を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>法線</strong>は、面に垂直な長さ 1 のベクトル。<strong>頂点法線</strong>で滑らかに
    - [x] <strong>拡散</strong>＝<strong>`max(dot(N, L), 0)`</strong>（<strong>L は面から光源へ</strong>）。<strong>スペキュラ</strong>＝<strong>`pow(dot(N, H), 光沢)`</strong>
    - [x] <strong>法線は、逆転置行列で変換</strong>。<strong>C++ で 1 回計算</strong>して渡す
    - [x] <strong>シェーダーで `normalize`</strong>。<strong>定数バッファは 16 バイト境界</strong>

## 関連ページ

- [PBR（物理ベースレンダリング）](pbr.md)
- [3D ゲーム（目次）](index.md)
- [変換と MVP](transforms-mvp.md)
- [メッシュとテクスチャ](mesh-textures.md)
- [行列](../gamemath/matrices.md)
