---
title: 法線とライティング
tags:
  - 3Dゲーム
---

# 法線とライティング

3D の物体に**陰影**をつけるには、**面が、どちらを向いているか**（**法線**）と、**光が、どちらから来るか**が必要です。このページは、法線の意味、ランバート拡散とブリン・フォンのスペキュラ、**法線を変換するときの落とし穴**（逆転置行列）、DX11 / HLSL のシェーダー例をまとめます。

!!! tip "ポイント"
    - <strong>法線</strong>は、<strong>面に垂直な、長さ 1 のベクトル</strong>。頂点に持たせる。
    - <strong>拡散光（ランバート）</strong>は、<strong>`max(dot(N, L), 0)`</strong>。<strong>L は、面から光への向き</strong>。
    - <strong>スペキュラ（ブリン・フォン）</strong>は、<strong>`pow(max(dot(N, H), 0), 光沢)`</strong>。H は、光と視線の中間。
    - <strong>法線は、ワールド行列では変換しない</strong>。<strong>逆転置行列</strong>で変換する（非一様スケールがあるとき）。
    - シェーダーで、<strong>法線を、毎回 `normalize`</strong> する（補間で、長さがずれる）。
    - ライトの向きは、<strong>光が進む向きではなく、光源へ向かう向き</strong>で持つと、計算が楽。

## 法線

**法線**は、**面に垂直な、長さ 1 のベクトル**です。陰影の計算の、中心です。

<svg class="fig" viewBox="0 0 360 140" role="img" aria-label="面と法線"><defs><marker id="ah2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><line x1="40" y1="110" x2="320" y2="110" stroke="currentColor" stroke-width="3"/><text x="326" y="115">面</text><line x1="180" y1="110" x2="180" y2="30" stroke="currentColor" stroke-width="2" marker-end="url(#ah2)"/><text x="190" y="45">N（法線：面に垂直・長さ 1）</text><rect x="174" y="104" width="12" height="12" fill="none" stroke="currentColor"/></svg>

### 面法線と頂点法線

<svg class="fig" viewBox="0 0 560 200" role="img" aria-label="面法線と頂点法線"><defs><marker id="m1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="22" class="fig-title">面法線（フラット）：面ごとに 1 つ</text><polyline points="30,150 110,110 190,150 270,110" fill="none" stroke="currentColor" stroke-width="3"/><line x1="70" y1="130" x2="58" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="150" y1="130" x2="162" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="230" y1="130" x2="218" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><text x="30" y="182">法線が、面ごとにカクッと変わる → カクカクに見える</text><text x="310" y="22" class="fig-title">頂点法線（スムース）：頂点ごとに平均</text><polyline points="310,150 390,110 470,150 550,110" fill="none" stroke="currentColor" stroke-width="3"/><line x1="310" y1="150" x2="310" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="390" y1="110" x2="390" y2="60" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="470" y1="150" x2="470" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><line x1="550" y1="110" x2="550" y2="60" stroke="currentColor" stroke-width="2" marker-end="url(#m1)" /><text x="310" y="182">三角形の中で補間 → 滑らかに見える</text></svg>

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

**CCW が表の三角形**なら、<strong>外積の向きが、表（外向き）</strong>になります（右手系）。巻き順が逆だと、法線が内向きになり、**暗く**なります。

## 拡散光（ランバート）

<svg class="fig" viewBox="0 0 560 240" role="img" aria-label="ランバート拡散光"><defs><marker id="m2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><line x1="40" y1="200" x2="300" y2="200" stroke="currentColor" stroke-width="3"/><line x1="170" y1="200" x2="170" y2="70" stroke="currentColor" stroke-width="2" marker-end="url(#m2)" /><text x="178" y="80">N（法線）</text><line x1="170" y1="200" x2="270" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m2)" /><text x="275" y="100">L（面→光源）</text><path d="M 170 150 A 50 50 0 0 1 205 165" fill="none" stroke="currentColor"/><text x="200" y="150">θ</text><text x="330" y="60" class="fig-title">明るさ ＝ max( dot(N, L), 0 ) ＝ cosθ</text><text x="330" y="100">θ = 0°（正面）　　→ 1（最大）</text><text x="330" y="125">θ = 60°　　　　　　→ 0.5</text><text x="330" y="150">θ = 90°（真横）　　→ 0</text><text x="330" y="175">θ &gt; 90°（裏側）　　→ 0（負は 0 に）</text></svg>

面が、**光に向いているほど明るく**、横を向くと**暗く**なります。**法線と、光への向きの内積**で決まります。

```text
明るさ = max( dot(N, L), 0 )

N と L が同じ向き → 1（最大）　　直角 → 0　　逆向き → 0（負は 0 にする）
```

**L は、面から光源へ向かう向き**です。光が、上から下へ進む（`(0, -1, 0)`）なら、**L は `(0, 1, 0)`** です。逆にすると、陰影が反転します。

## スペキュラ（ブリン・フォン）

<svg class="fig" viewBox="0 0 560 240" role="img" aria-label="ブリン・フォンのハーフベクトル"><defs><marker id="m3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><line x1="40" y1="200" x2="360" y2="200" stroke="currentColor" stroke-width="3"/><line x1="200" y1="200" x2="200" y2="60" stroke="currentColor" stroke-width="2" marker-end="url(#m3)" /><text x="206" y="66">N</text><line x1="200" y1="200" x2="90" y2="90" stroke="currentColor" stroke-width="2" marker-end="url(#m3)" /><text x="60" y="84">L（光源へ）</text><line x1="200" y1="200" x2="310" y2="90" stroke="currentColor" stroke-width="2" marker-end="url(#m3)" /><text x="296" y="84">V（カメラへ）</text><line x1="200" y1="200" x2="200" y2="85" stroke="currentColor" stroke-width="2" marker-end="url(#m3)" stroke-dasharray="5 4"/><text x="380" y="60" class="fig-title">H ＝ normalize(L + V)</text><text x="380" y="90">L と V の、ちょうど真ん中の向き</text><text x="380" y="120">N と H が重なるほど、ハイライトが強い</text><text x="380" y="150">pow( max(dot(N, H), 0), 光沢 )</text><text x="380" y="180">鏡のように反射する向きに、カメラがあると光る</text></svg>

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

<svg class="fig" viewBox="0 0 600 220" role="img" aria-label="ライトの種類"><defs><marker id="m4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">ディレクショナル</text><line x1="30" y1="40" x2="50" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="70" y1="40" x2="90" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="110" y1="40" x2="130" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="150" y1="40" x2="170" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="10" y1="170" x2="190" y2="170" stroke="currentColor" stroke-width="3"/><text x="30" y="200">全体が、同じ向き（太陽）</text><text x="225" y="20" class="fig-title">ポイント</text><circle cx="300" cy="90" r="8" fill="currentColor"/><line x1="300" y1="90" x2="300" y2="30" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="355" y2="50" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="365" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="340" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="260" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="235" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><line x1="300" y1="90" x2="245" y2="50" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><text x="225" y="200">位置から四方へ（電球）。距離で減る</text><text x="430" y="20" class="fig-title">スポット</text><circle cx="480" cy="40" r="8" fill="currentColor"/><polygon points="480,40 420,170 540,170" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/><line x1="480" y1="40" x2="480" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m4)" /><text x="420" y="200">位置・向き・角度（懐中電灯）</text></svg>

| 種類 | 向き | 減衰 | 用途 |
| --- | --- | --- | --- |
| **ディレクショナル** | 全体で、同じ向き | なし | 太陽、月 |
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

<svg class="fig" viewBox="0 0 600 230" role="img" aria-label="非一様スケールで法線がずれる"><defs><marker id="m5" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="22" class="fig-title">元の面（45°）と法線</text><line x1="40" y1="170" x2="160" y2="70" stroke="currentColor" stroke-width="3"/><line x1="100" y1="120" x2="140" y2="76" stroke="currentColor" stroke-width="2" marker-end="url(#m5)" /><text x="200" y="22" class="fig-title">X を 3 倍にすると</text><line x1="210" y1="170" x2="360" y2="130" stroke="currentColor" stroke-width="3"/><line x1="285" y1="150" x2="345" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#m5)" stroke-dasharray="4 3"/><line x1="285" y1="150" x2="303" y2="88" stroke="currentColor" stroke-width="2" marker-end="url(#m5)" /><text x="210" y="205">破線：面と同じ変換をした法線（垂直でなくなる）</text><text x="210" y="222">実線：逆転置行列で変換した法線（垂直のまま）</text><text x="420" y="22" class="fig-title">法線は「向き」</text><text x="420" y="60">面と垂直であることを</text><text x="420" y="85">保つ変換が必要</text><text x="420" y="120">→ transpose( inverse(World) )</text></svg>

!!! warning "法線を、ワールド行列で変換してはいけない"
    **非一様スケール**（`Scale(2, 1, 1)` など）があると、法線が**面に垂直でなくなります**。法線は、**ワールド行列の逆行列の転置**で変換します。

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

逆転置行列は、**物体ごとに、C++ で 1 回**計算して、定数バッファで渡します。**ピクセルごとに、シェーダーで逆行列を計算しません**（重い）。

## 法線マップ

<svg class="fig" viewBox="0 0 560 220" role="img" aria-label="接空間と TBN"><defs><marker id="m6" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><polygon points="60,180 300,180 380,110 140,110" fill="none" stroke="currentColor" stroke-width="2"/><line x1="220" y1="150" x2="300" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#m6)" /><text x="304" y="154">T（接線：U の向き）</text><line x1="220" y1="150" x2="250" y2="112" stroke="currentColor" stroke-width="2" marker-end="url(#m6)" /><text x="254" y="108">B（従接線：V の向き）</text><line x1="220" y1="150" x2="220" y2="55" stroke="currentColor" stroke-width="2" marker-end="url(#m6)" /><text x="228" y="62">N（法線）</text><text x="20" y="22" class="fig-title">TBN：面の上の座標系</text><text x="400" y="190">法線マップの値を、</text><text x="400" y="210">この座標系でワールドへ</text></svg>

**テクスチャで、細かい凹凸の法線**を与えると、**頂点数を増やさず**、凹凸を表現できます。

| 要素 | 説明 |
| --- | --- |
| **法線マップ** | RGB に、法線の XYZ（`0..1` → `-1..1`）を入れた、テクスチャ |
| <strong>接空間（タンジェント空間）</strong> | 法線マップの座標系。頂点に、<strong>接線（tangent）</strong> が必要 |
| **TBN 行列** | 接線・従接線・法線から作る、接空間 → ワールドの変換 |

法線マップは、**法線の向きが、モデルの表面に沿っている**前提です。**Y 軸の向き（OpenGL 系と DirectX 系）の違い**で、凹凸が反転することがあります。

## ライトの計算の注意

| 注意 | 説明 |
| --- | --- |
| **ポイントライトの L** | `normalize(light_position - world_position)`。**ピクセルごと**に求める |
| **減衰** | `1 / (1 + k1*d + k2*d*d)` など。**範囲外は 0**にする |
| <strong>色空間（ガンマ）</strong> | 計算は**リニア**空間。表示の前に、ガンマ補正（sRGB のレンダーターゲットなら、自動） |
| **HDR・トーンマッピング** | 明るさが 1 を超えるなら、トーンマッピングで画面に収める |
| **コストの目安** | ピクセルごとの計算。ライト数に比例。多数なら、ディファード・タイルベース |

## よくあるミス

??? failure "陰影が、反転して見える"
    **L の向き**が逆です。L は、**面から光源へ**向かう向きです。

??? failure "拡大・縮小した物体の、陰影がおかしい"
    法線を、ワールド行列で変換しています。**逆転置行列**を使います。

??? failure "カクカク・ギザギザに見える"
    頂点法線が、面法線のままです。**隣の面の法線を平均**します。

??? failure "ハイライトが、光の反対側に出る"
    スペキュラの H や V の向きが、逆です。V は、**面から、カメラへ**。

??? failure "モデル全体が、暗い"
    法線が、**内向き**（巻き順の間違い）、または、`normalize` していません。

??? failure "定数バッファの値が、ずれる"
    `float3` の後ろに、詰め物が足りません。**16 バイト境界**を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>法線</strong>は、面に垂直な長さ 1 のベクトル。<strong>頂点法線</strong>で滑らかに
    - [x] <strong>拡散</strong>＝<strong>`max(dot(N, L), 0)`</strong>（<strong>L は、面から光源へ</strong>）。<strong>スペキュラ</strong>＝<strong>`pow(dot(N, H), 光沢)`</strong>
    - [x] <strong>法線は、逆転置行列で変換</strong>。<strong>C++ で 1 回計算</strong>して渡す
    - [x] <strong>シェーダーで `normalize`</strong>。<strong>定数バッファは 16 バイト境界</strong>

## 関連ページ

- [PBR（物理ベースレンダリング）](pbr.md)
- [3D ゲーム（目次）](index.md)
- [変換と MVP](transforms-mvp.md)
- [メッシュとテクスチャ](mesh-textures.md)
- [行列](matrices.md)
