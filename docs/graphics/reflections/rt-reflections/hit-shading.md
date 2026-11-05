---
title: Hit Shading and BVH
tags:
  - 描画
---

# Hit Shading and BVH

反射レイが何かに当たると DXR は「どの三角形のどの位置に当たったか」しか教えてくれません。色は自分で作ります。三角形の頂点を読み重心座標で UV と法線を補間し、テクスチャを読み光を足します。ところが、ヒット シェーダーには画面の微分（`ddx`、`ddy`）がないのでどのミップを読むかも自分で決めます。ミップを間違えると遠くの反射がチラチラ光る（エイリアス）かぼやけます。このページではヒット点のシェーディングをミップの選び方（レイ コーン）を中心に、コメント付きの完成形で説明します。BVH の準備は最後にまとめます。

!!! tip "ポイント"
    - ヒット シェーダーの仕事は、属性の補間、ミップの選択、テクスチャ、影、ライティングの 5 つである。
    - ミップはレイ コーンの幅から決める。式は 1 つで `λ = Δ + log2(w) + 0.5 × log2(1 / |n・d|)` である。
    - レイ コーンが運ぶ値は 2 つ（幅と広がり角）で、ペイロードに載せても軽い。ray differentials は 12 個の float を運ぶ。
    - 曲面の反射では広がり角が変わる。凸面は広がり凹面は縮む。
    - デノイザーで強くぼかすならミップ 0 でも足りることがある。

!!! info "このページを読む前に"
    - [Ray-Traced Reflections](index.md)（このセクション全体の地図と、読む順番）
    - [Ray Generation](ray-generation.md)（反射レイの作り方）

## 読んだ資料 {#sources}

- Akenine-Möller, Nilsson, Andersson, Barré-Brisebois, Toth, Karis, "Texture Level of Detail Strategies for Real-Time Ray Tracing", Ray Tracing Gems 第 20 章。20.1〜20.2、20.3.4（レイ コーン）、20.4、20.5 の本文を読みました。ray differentials の導出（20.3.2〜20.3.3）と、付録のコード（20.6）は読んでいません。
- Barré-Brisebois ほか, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems 第 25 章。パイプラインの概観（25.1）と反射（25.2.2）、AO（25.2.3）を読みました。ほかの節は読んでいません。

BLAS・TLAS の数字（メモリ、更新時間）は読んだ範囲に載っていません。BVH の節は DXR の基本の仕組みの説明にとどめます。

## ヒット点で何をするか {#overview}

<svg class="fig flow" viewBox="0 0 730 122" role="img" aria-label="ヒット点のシェーディングの流れ"><defs><marker id="hs-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">反射レイが当たってから、色を返すまで</text><rect x="10" y="34" width="106" height="52" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="63.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">三角形の</text><text x="63.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">頂点を読む</text><line x1="116" y1="60" x2="128" y2="60" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#hs-a)"/><rect x="128" y="34" width="106" height="52" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="181.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">重心座標で</text><text x="181.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">UV・法線を補間</text><line x1="234" y1="60" x2="246" y2="60" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#hs-a)"/><rect x="246" y="34" width="106" height="52" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="299.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">レイ コーンで</text><text x="299.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">ミップを決める</text><line x1="352" y1="60" x2="364" y2="60" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#hs-a)"/><rect x="364" y="34" width="106" height="52" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="417.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">テクスチャを</text><text x="417.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">読む</text><line x1="470" y1="60" x2="482" y2="60" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#hs-a)"/><rect x="482" y="34" width="106" height="52" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="535.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">影レイを</text><text x="535.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">飛ばす</text><line x1="588" y1="60" x2="600" y2="60" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#hs-a)"/><rect x="600" y="34" width="106" height="52" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="653.0" y="57.0" text-anchor="middle" font-size="11" fill="currentColor">光を足して</text><text x="653.0" y="71.0" text-anchor="middle" font-size="11" fill="currentColor">payload へ</text><text x="10" y="110" text-anchor="start" font-size="10" fill="currentColor">黄: ヒット シェーダーに画面の微分が無いので、自分で決める所</text></svg>

反射レイが当たると次の順で色を作ります。

1. 三角形の 3 頂点を読みます。DXR は `PrimitiveIndex()` で三角形の番号をくれるので、インデックス バッファから頂点の番号を引きます。
2. 重心座標で UV と法線を補間します。`attr.barycentrics` に入っているのは (b1, b2) の 2 つだけで、b0 は `1 − b1 − b2` です。
3. レイ コーンの幅からミップを決めます。
4. ミップを指定してテクスチャを読みます。
5. 太陽の方向に影レイを飛ばします。
6. 直接光と環境光を足して、`payload` に返します。

PICA PICA（Ray Tracing Gems 第 25 章）も同じ構成です。パイプラインの手順に「反射の交点でのレイトレースの影」が入っています（25.1 の 5.2）。反射は G バッファから 1/4 レイ/画素で出し、反射の交点では影を取りあとで反射をデノイズする、という順番です。

## 属性を補間する {#interpolate}

```hlsl
// 反射レイが当たった点の色を決める DXR のシェーダー一式（Shader Model 6.3 の lib）。
// 流れ: G バッファから反射レイを出す → 当たった三角形の属性を補間 → レイ コーンでミップを決める
//       → テクスチャを読む → 太陽の影レイを飛ばす → 光を足して payload に返す。
// 読み方: ① 型と束縛 ② レイ コーン ③ ライティング ④ closest hit ⑤ 影の miss ⑥ レイ生成 の順。

// ================= ① 型と束縛 =================

// 反射レイが運ぶ値。小さいほど速いので、必要な物だけにする。
struct ReflectionPayload {
  float3 radiance;       // 当たった点から戻ってくる光（HDR、線形）
  float hit_distance;    // 当たるまでの距離 [m]。デノイザーが反射の視差を追うのに使う
  float cone_width;      // レイ コーンの幅 w_i [m]（今のレイの原点での幅）
  float cone_spread;     // レイ コーンの広がり角 gamma_i [rad]（1 m 進むごとに幅が増える量）
};

// 影レイの payload。当たったかどうかの 1 ビットだけで足りる。
struct ShadowPayload {
  bool shadowed;         // true のままなら、何かに遮られた
};

// 頂点（位置は使わない。BLAS が持っているので、ここでは属性だけ）。
struct Vertex {
  float3 normal;         // オブジェクト空間の法線
  float2 uv;             // テクスチャ座標 [0, 1]
};

// マテリアル（インスタンスごとに 1 つ）。
struct Material {
  uint albedo_index;     // g_textures 内の添字
  float roughness;       // 粗さ（知覚的な粗さ。0 = 鏡面、1 = 拡散に近い）
  float metallic;        // 金属度
  float tex_size;        // テクスチャの一辺 [texel]（正方形を仮定。LOD の基準 Δ に使う）
};

RaytracingAccelerationStructure g_scene : register(t0);   // TLAS（シーン全体）
StructuredBuffer<Vertex> g_vertices : register(t1);       // 全メッシュの頂点を連結した配列
ByteAddressBuffer g_indices : register(t2);               // 全メッシュの 16 bit インデックスを連結した配列
StructuredBuffer<Material> g_materials : register(t3);    // マテリアル（InstanceID で引く）
Texture2D<float4> g_textures[] : register(t0, space1);    // ビンドレス テクスチャ（非一様な添字が使える）
SamplerState g_linear_wrap : register(s0);                // ミップを手で選ぶので SampleLevel と組み合わせる

// 三角形のアドレス計算に使う、メッシュごとの先頭位置。InstanceID() で引く。
struct MeshInfo {
  uint first_index;      // g_indices の中の先頭（インデックス単位）
  uint first_vertex;     // g_vertices の中の先頭（頂点単位）
  float uv_area_2x;      // uv 空間の三角形の面積の 2 倍の平均（LOD の基準 Δ 用。事前計算）
  float world_area_2x;   // ワールド空間の三角形の面積の 2 倍の平均（同上）
};
StructuredBuffer<MeshInfo> g_meshes : register(t4);

cbuffer FrameCB : register(b0) {
  float4x4 g_inv_view_proj;   // クリップ → ワールド
  float3 g_camera_pos;        // カメラ位置 [m]
  float g_pixel_spread;       // 画素の広がり角 alpha [rad]（②で式を示す）
  float3 g_sun_dir;           // 太陽へ向かう単位ベクトル（光が来る向きの逆）
  float g_sun_intensity;      // 太陽の放射照度スケール
  float3 g_sun_color;         // 太陽の色（線形）
  float g_shadow_bias;        // 影レイの原点を法線方向にずらす量 [m]（一例: 0.002）
  float4 g_sh[4];             // 環境光の L1 球面調和（xyz = 係数、w は使わない）。0 = 定数項、1〜3 = x, y, z
  float2 g_inv_size;          // 1 / (幅, 高さ)
  uint g_frame_index;         // フレーム番号（乱数のシード）
  float g_max_distance;       // 反射レイの最大距離 [m]
  float g_k1;                 // 曲率の係数（論文の既定値は 1）
  float g_k2;                 // 平面のときに足す広がり（論文の既定値は 0）
  float2 g_pad;
};

Texture2D<float> g_depth : register(t5);          // G バッファの深度
Texture2D<float4> g_normal_rough : register(t6);  // xyz = ワールド法線、w = 粗さ
Texture2D<float4> g_cone_in : register(t7);       // G バッファの曲率 beta（x）。ラスタライズ時の ddx/ddy から作る
RWTexture2D<float4> g_out : register(u0);         // 反射の色（rgb）と距離（a）
```

束縛はビンドレスです。`Texture2D g_textures[]` のようにサイズを決めない配列にして、`NonUniformResourceIndex` で引きます。隣の画素のレイが別のメッシュに当たるので、添字が画素ごとに違うためです。`NonUniformResourceIndex` を付け忘れると動く GPU と動かない GPU が出ます。

`ReflectionPayload` には光（`radiance`）と距離のほかにレイ コーンの 2 つの値が入ります。ペイロードは大きくなるほどレジスタを食うので、この 2 つで済むのは利点です。

```hlsl
// ================= ④ closest hit =================

// 三角形の 3 頂点のインデックスを読む（16 bit インデックスを 2 つずつ詰めた配列）。
uint3 LoadTriangleIndices(uint first_index, uint primitive) {
  uint byte_offset = (first_index + primitive * 3) * 2;     // 16 bit × 3 つ = 6 バイト / 三角形
  uint word = byte_offset & ~3u;                            // 4 バイト境界に切り下げ
  uint2 packed = g_indices.Load2(word);                     // 8 バイト読めば 3 つ入る
  uint shift = (byte_offset & 2u) ? 16 : 0;                 // 先頭が上位か下位か
  uint i0 = (packed.x >> shift) & 0xFFFF;
  uint i1 = (shift == 0) ? (packed.x >> 16) : (packed.y & 0xFFFF);
  uint i2 = (shift == 0) ? (packed.y & 0xFFFF) : (packed.y >> 16);
  return uint3(i0, i1, i2);
}

// 影レイ。当たった物があるかどうかだけ調べる。
float TraceShadow(float3 origin, float3 dir) {
  RayDesc ray;
  ray.Origin = origin;
  ray.Direction = dir;
  ray.TMin = 0.0;                    // 原点を法線方向にずらしてあるので 0 でよい
  ray.TMax = 1e4;                    // 太陽は遠い。十分長く
  ShadowPayload p;
  p.shadowed = true;                 // ミス シェーダーが false にするまで、遮られたとみなす
  TraceRay(g_scene,
           RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH |   // 最初に見つかった交点で終える（距離は不要）
           RAY_FLAG_SKIP_CLOSEST_HIT_SHADER,            // ヒット シェーダーは要らない
           0xFF, 1, 0, 1, ray, p);                      // ヒット グループは影用（添字 1）、ミスも影用（添字 1）
  return p.shadowed ? 0.0 : 1.0;
}

[shader("closesthit")]
void ReflectionClosestHit(inout ReflectionPayload payload, BuiltInTriangleIntersectionAttributes attr) {
  // 1. 当たった三角形の頂点を読む。
  MeshInfo mesh = g_meshes[InstanceID()];                    // InstanceID() = メッシュの番号（TLAS で設定）
  uint3 idx = LoadTriangleIndices(mesh.first_index, PrimitiveIndex());
  Vertex v0 = g_vertices[mesh.first_vertex + idx.x];
  Vertex v1 = g_vertices[mesh.first_vertex + idx.y];
  Vertex v2 = g_vertices[mesh.first_vertex + idx.z];

  // 2. 重心座標で属性を補間する。attr.barycentrics は (b1, b2)。b0 = 1 - b1 - b2。
  float3 b = float3(1.0 - attr.barycentrics.x - attr.barycentrics.y, attr.barycentrics.x, attr.barycentrics.y);
  float2 uv = v0.uv * b.x + v1.uv * b.y + v2.uv * b.z;
  float3 n_obj = v0.normal * b.x + v1.normal * b.y + v2.normal * b.z;
  // 逆転置行列で法線をワールドへ（行ベクトルの mul の向きに注意）。非一様スケールでも正しい。
  float3 n = normalize(mul((float3x3)WorldToObject4x3(), n_obj));

  // 3. 面が裏向きなら法線を反転する。裏から当たったとき、光が逆に入るのを防ぐ。
  float3 d = WorldRayDirection();                            // 当たったレイの向き（単位ベクトル）
  if (dot(n, d) > 0.0) n = -n;

  float3 hit_pos = WorldRayOrigin() + d * RayTCurrent();     // ワールドの当たった位置

  // 4. レイ コーンを進めて、ミップを決める。
  //    この点までの距離 RayTCurrent() で幅が増える。曲率はラスタライズ時に G バッファに入れたぶんだけを
  //    最初のレイで使い、2 回目以降の面は平面として扱う（論文も同じ割り切り）。
  float width = payload.cone_width + payload.cone_spread * RayTCurrent();
  Material mat = g_materials[InstanceID()];
  float base_lod = BaseLod(mesh.uv_area_2x, mat.tex_size, mesh.world_area_2x);
  float lod = ConeLod(base_lod, width, n, d);
  lod = clamp(lod, 0.0, 12.0);                               // 4096 まで。範囲外のミップを読まない

  // 5. テクスチャを読む。ヒット シェーダーには画面の微分がないので、SampleLevel でミップを明示する。
  float3 albedo = g_textures[NonUniformResourceIndex(mat.albedo_index)].SampleLevel(g_linear_wrap, uv, lod).rgb;

  // 6. 影。太陽の向きに影レイを飛ばす。面の上に出るよう、法線方向にずらす。
  float shadow = TraceShadow(hit_pos + n * g_shadow_bias, g_sun_dir);

  // 7. ライティング。視線は「当たった点からレイの元へ」向かう -d。
  float3 radiance = DirectLighting(albedo, mat.roughness, mat.metallic, n, -d, shadow);
  radiance += albedo * (1.0 - mat.metallic) * EvaluateAmbient(n) / kPi;   // 環境光（拡散だけ。反射の反射は 1 回で打ち切る）

  payload.radiance = radiance;
  payload.hit_distance = RayTCurrent();
}
```

三角形のインデックスは 16 bit を詰めた `ByteAddressBuffer` から読みます。`Load2` で 8 バイト読めば 3 つのインデックス（6 バイト）が入ります。先頭が 4 バイト境界の上位か下位かで、詰め方が変わります。

法線のワールド変換には `WorldToObject4x3()` を使います。法線は逆転置行列で変えるので、行ベクトルの `mul` の向きを間違えると、非一様スケールで法線が曲がります。当たった面が裏向き（`dot(n, d) > 0`）のときは法線を反転します。そうしないと裏から当たったときに光が逆に入ります。

## テクスチャのミップを選ぶ {#texture-lod}

### ヒット シェーダーに微分がない {#no-derivative}

ラスタライズでは GPU が 2×2 の画素のクアッドで隣との差を取って、ミップを決めます。レイトレースでは画素が隣のレイと同じ三角形に当たる保証がないので、この仕組みは使えません。Ray Tracing Gems 第 20 章は、最も簡単な方法としてミップ 0 を読むことを挙げています。レイが少ないとエイリアスが出ますが、強いデノイザーがあるならこれで足りることがあります。

### レイ コーンの考え方 {#ray-cone}

<svg class="fig flow" viewBox="0 0 660 196" role="img" aria-label="レイ コーンの幅の広がり"><defs><marker id="hs-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">レイ コーン: 進むほど幅が広がり、曲面で広がり角が変わる</text><circle cx="40" cy="100" r="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="40" y="124" text-anchor="middle" font-size="10" fill="currentColor">カメラ</text><polygon points="46,98 300,70 300,130 46,102" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="0.8"/><line x1="300" y1="40" x2="300" y2="160" stroke="#94a3b8" stroke-width="4"/><text x="300" y="34" text-anchor="middle" font-size="10" fill="currentColor">凸面で反射</text><text x="170" y="150" text-anchor="middle" font-size="10" fill="currentColor">w0 = α × t0</text><polygon points="300,100 560,40 560,160" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="0.8"/><line x1="560" y1="30" x2="560" y2="170" stroke="#94a3b8" stroke-width="4"/><text x="560" y="24" text-anchor="middle" font-size="10" fill="currentColor">テクスチャの面</text><text x="430" y="182" text-anchor="middle" font-size="10" fill="currentColor">w1 = w0 + (α + β) × t1</text><text x="430" y="70" text-anchor="middle" font-size="10" fill="currentColor">β > 0 (凸): 広がる</text></svg>

画素から出るレイを広がり角 α の円錐だと考えます。円錐は進むと幅が増えます。当たった点での幅 w が分かれば、テクスチャの 1 テクセルより広いぶんだけミップを上げればよいという考え方です。

画素の広がり角は垂直画角 ψ と画面の高さ H から、`α = atan(2 tan(ψ/2) / H)` です。1080p・画角 60 度ではα = 0.001069 rad（0.0613 度）です。中心の画素の角度を全画素に使う近似です。論文も同じ近似を使い VR や視線追跡つきの描画では、より複雑な方法が要ると断っています。

最初の当たり（G バッファの面）では、幅は `w0 = α × t0`（t0 はカメラからの距離）です。距離 4 m なら 4.28 mm、16 m なら 17.1 mm です。

斜めに見るほど 1 画素が面の上で伸びます。論文は投影後のフットプリントを `w / sqrt(|n・d|)` と近似し、それが 2 倍になったらミップを 1 つ上げると考えて log2 を取ります。これに三角形そのものの基準 LOD、Δ を足したのが式 34 です。

```text
λ = Δ + log2(w) + 0.5 × log2(1 / |n・d|)
```

Δ は三角形のテクセル空間の面積とワールド空間の面積の比で決まります。`Δ = 0.5 × log2(ta / pa)` です（ta、pa はそれぞれ面積の 2 倍）。たとえば、1 m 四方の板に 2048² のテクスチャを貼ると、Δ = 0.5 × log2(2048²) ＝ 11 です。三角形が 2 倍の面積になれば、Δ は 0.5 下がります。

### 数字で確かめる {#lod-numbers}

この板を正面（角度 0 度）から見たときの λ を距離ごとに計算しました。距離が 2 倍になるごとにλ が 1 ずつ増えます。幅が 2 倍になってフットプリントが 2 倍のテクセルを覆うからです。

<svg class="fig flow" viewBox="0 0 620 214" role="img" aria-label="テクスチャのミップ λ と距離の関係"><defs><marker id="hs-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">λ(2048² のテクスチャ、1080p、画角 60 度)。距離が 2 倍で λ が 1 増える</text><line x1="60" y1="174" x2="520" y2="174" stroke="#94a3b8"/><line x1="60" y1="34" x2="60" y2="174" stroke="#94a3b8"/><line x1="60" y1="154.0" x2="520" y2="154.0" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="158.0" text-anchor="end" font-size="10" fill="currentColor">1</text><line x1="60" y1="114.0" x2="520" y2="114.0" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="118.0" text-anchor="end" font-size="10" fill="currentColor">3</text><line x1="60" y1="74.0" x2="520" y2="74.0" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="78.0" text-anchor="end" font-size="10" fill="currentColor">5</text><line x1="60" y1="34.0" x2="520" y2="34.0" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.5"/><text x="54" y="38.0" text-anchor="end" font-size="10" fill="currentColor">7</text><polyline points="80.0,151.4 185.0,131.4 290.0,111.4 395.0,91.4 500.0,71.4" fill="none" stroke="#4c8bf5" stroke-width="2.5"/><text x="508.0" y="75.39999999999999" text-anchor="start" font-size="10" fill="currentColor">0 度</text><polyline points="80.0,141.4 185.0,121.4 290.0,101.4 395.0,81.4 500.0,61.4" fill="none" stroke="#94a3b8" stroke-width="2.5"/><text x="508.0" y="65.4" text-anchor="start" font-size="10" fill="currentColor">60 度</text><polyline points="80.0,126.2 185.0,106.2 290.0,86.2 395.0,66.2 500.0,46.2" fill="none" stroke="#e5aa28" stroke-width="2.5"/><text x="508.0" y="50.2" text-anchor="start" font-size="10" fill="currentColor">80 度</text><text x="80.0" y="190" text-anchor="middle" font-size="10" fill="currentColor">1 m</text><text x="185.0" y="190" text-anchor="middle" font-size="10" fill="currentColor">2 m</text><text x="290.0" y="190" text-anchor="middle" font-size="10" fill="currentColor">4 m</text><text x="395.0" y="190" text-anchor="middle" font-size="10" fill="currentColor">8 m</text><text x="500.0" y="190" text-anchor="middle" font-size="10" fill="currentColor">16 m</text></svg>

角度が 60 度になると 0.5 増え 80 度では 1.26 増えます。|n・d| ＝ cos 60° ＝ 0.5 なら 0.5 × log2(2) ＝ 0.5 です。

### 曲面での反射 {#curvature}

反射すると円錐は曲面の曲率で広がり角を変えます。凸面は広がり凹面は縮み平面は変わりません。論文はこの量を表面の広がり角 β で表します。

```text
w_i = w_{i-1} + γ_i × t_i
γ_i = γ_{i-1} + β_{i-1}      （γ_0 = α）
```

t_i は直前の点からこの点までの距離です。β の求め方は G バッファで `ddx`、`ddy` を使う方法です。法線が画素ごとにどれだけ回るかが、曲率の目安になります。論文は曲率の符号 s を `∂n` と `∂P` の内積の符号で決めると書いています。鞍点（凸でも凹でもある面）では s ＝ 1 にするのがよいとも書いています。

論文の式 31〜32 は PDF の文字の抽出で括弧の位置が崩れて、確かめられませんでした。そこで、球を使って実測しました。カメラ（1920×1080、画角 60 度）から球（半径 0.5、1、2 m）を見て反射した先の床までの幅を隣の画素のレイを実際に反射して測り、レイ コーンの予測と比べました。

<svg class="fig flow" viewBox="0 0 640 236" role="img" aria-label="球での実測とレイ コーンの予測の比"><defs><marker id="hs-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">レイ コーンの予測 / 実測(1.0 が一致)。球の半径 0.5, 1, 2 m の平均</text><text x="152" y="54" text-anchor="end" font-size="11" fill="currentColor">A 二乗和の平方根</text><rect x="160" y="34" width="249.4" height="14" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="415.3818181818182" y="45" text-anchor="start" font-size="10" fill="currentColor">1.524  (R=0.5 m)</text><rect x="160" y="51" width="242.0" height="14" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="408.0181818181818" y="62" text-anchor="start" font-size="10" fill="currentColor">1.479  (R=1 m)</text><rect x="160" y="68" width="218.6" height="14" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="384.6181818181818" y="79" text-anchor="start" font-size="10" fill="currentColor">1.336  (R=2 m)</text><text x="152" y="114" text-anchor="end" font-size="11" fill="currentColor">B 和</text><rect x="160" y="94" width="340.9" height="14" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="506.8545454545454" y="105" text-anchor="start" font-size="10" fill="currentColor">2.083  (R=0.5 m)</text><rect x="160" y="111" width="326.3" height="14" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="492.29090909090905" y="122" text-anchor="start" font-size="10" fill="currentColor">1.994  (R=1 m)</text><rect x="160" y="128" width="282.8" height="14" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="448.76363636363635" y="139" text-anchor="start" font-size="10" fill="currentColor">1.728  (R=2 m)</text><text x="152" y="174" text-anchor="end" font-size="11" fill="currentColor">C 平均 × 2 (採用)</text><rect x="160" y="154" width="177.1" height="14" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="343.05454545454546" y="165" text-anchor="start" font-size="10" fill="currentColor">1.082  (R=0.5 m)</text><rect x="160" y="171" width="176.2" height="14" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="342.23636363636365" y="182" text-anchor="start" font-size="10" fill="currentColor">1.077  (R=1 m)</text><rect x="160" y="188" width="171.0" height="14" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="337.0" y="199" text-anchor="start" font-size="10" fill="currentColor">1.045  (R=2 m)</text><line x1="323.6" y1="28" x2="323.6" y2="214" stroke="#94a3b8" stroke-dasharray="3 3"/><text x="323.6363636363636" y="226" text-anchor="middle" font-size="10" fill="currentColor">1.0</text></svg>

法線の変化の平均（|∂n/∂x| と |∂n/∂y| の平均の 2 倍を β とする形）が、実測と 1.05〜1.08 倍で最もよく合いました。二乗和の平方根は 1.34〜1.52 倍、単純な和は 1.73〜2.08 倍で、過大でした。このページのコードは合った形にしています。ただし、これは私の実測で論文の式そのものではありません。係数 `k1`、`k2` を調整値として残してあります。

### 割り切りと精度 {#cone-limits}

論文のレイ コーンの実装は最初のヒットだけ曲率を持ち 2 回目以降の面は平面として扱います（β_i ＝ 0、i > 0）。反射の中の反射で曲面のテクスチャが強いエイリアスを起こすことがある、と図 20-8 で示しています。また、レイ コーンは円（等方）の足跡しか表せないので鞍点や半円筒のように 1 方向にしか曲がらない面は、ray differentials より少しぼけます。

精度は fp16 で足ります。論文はβ、w、γ を fp16 にしても見た目の差は分からず最大の差は 255 段階中 5 だったと書いています。`tan α ≈ α` の近似でも同じ程度の差でした。ペイロードには幅と広がり角の 2 つを載せるだけです。ray differentials は、1 本のレイにつき 12 個の float が要ります。

### コスト {#lod-cost}

論文は 2080 Ti、3840×2160 で測っています。ミップ 0 の平均フレーム時間は Pink Room が 3.4 ms、Large Interior が 13.4 ms です。LOD の計算が上乗せするコストは ray differentials（G バッファ使用）が約 2 倍、ray differentials（全部レイトレース）が約 3 倍で、レイ コーンを 1 とした比です。

画質は双曲放物面の例で PSNR がミップ 0 で 25.0 dB、レイ コーンで 26.7 dB、ray differentials で 31.0 dB です。SSIM は 0.95、0.95、0.97 です。論文はどれも地の真値（1 画素 1024 本）よりぼけるので、数値が低いと述べています。エイリアスはミップ 0 のほうがずっと強く出ます。

結論として論文は次のように勧めています。強いデノイザーを使うか多くのフレームを積むならミップ 0 が速く、十分です。きれいに filter された反射が要りレイの記憶量と命令を減らしたいなら、レイ コーンです。

```hlsl
// ================= ② レイ コーン =================
// 資料: Akenine-Möller ほか, Ray Tracing Gems 第 20 章（式 3, 26, 29, 34, 35）。
// コードは式から書き直したもの。

// 画素の広がり角 alpha。垂直画角 fov_y [rad] と画面の高さ height [px] から。
// 中心の画素の角度を全画素で使う近似（論文も同じ近似）。
float PixelSpreadAngle(float fov_y, float height) {
  return atan(2.0 * tan(0.5 * fov_y) / height);
}

// 三角形ごとの基準 LOD、Δ = 0.5 log2(ta / pa)（式 3）。
// ta: テクセル空間の面積の 2 倍、pa: ワールド空間の面積の 2 倍。
// 三角形が 2 倍の面積になれば、Δ は 0.5 log2(1/2) だけ、つまり 0.5 下がる。
float BaseLod(float uv_area_2x, float tex_size, float world_area_2x) {
  float ta = uv_area_2x * tex_size * tex_size;    // uv 面積 × テクセル数 = テクセル空間の面積
  return 0.5 * log2(max(ta / max(world_area_2x, 1e-12), 1e-12));
}

// 当たった点でのミップ（式 34）。
//   lambda = Δ + log2(w) + 0.5 log2(1 / |n・d|)
//   w は円錐の幅 [m]。n は当たった面の法線、d はレイの向き（どちらも単位ベクトル）。
// 斜めに見るほど（|n・d| が 0 に近いほど）フットプリントが伸びるので、ミップを上げる。
// |n・d| = 0 なら log2(0) = -inf から inf になり、最上位ミップを読む（論文もこれを許している）。
float ConeLod(float base_lod, float cone_width, float3 n, float3 d) {
  float n_dot_d = abs(dot(n, d));
  return base_lod + log2(max(cone_width, 1e-6)) + 0.5 * log2(1.0 / max(n_dot_d, 1e-4));
}

// 当たった点で円錐を更新する（式 35）。
//   w_i = w_{i-1} + gamma_i * t_i,  gamma_i = gamma_{i-1} + beta_{i-1}
// t は直前の点からこの点までの距離、beta は直前の面の曲率による広がり。
// 凸面（beta > 0）では広がり、凹面（beta < 0）では縮む。
void AdvanceCone(inout float width, inout float spread, float t, float beta_at_hit) {
  width += spread * t;            // 進んだぶん、幅が増える（spread が負なら減る）
  spread += beta_at_hit;          // 次のレイは、この面の曲率ぶん広がり角が変わる
}

// G バッファのときの曲率 beta。ラスタライズ中に ddx/ddy で法線の変化を測る。
// 式 31〜32 の括弧の位置は PDF の抽出で確かめられなかったので、
// 球での実測（本文の C++）に合わせて、法線の変化の平均を 2 倍にした形にしている。
float SurfaceSpreadAngle(float3 n, float3 p, float k1, float k2) {
  float3 dn_dx = ddx(n);          // 隣の画素との法線の差（画素あたり）
  float3 dn_dy = ddy(n);
  float3 dp_dx = ddx(p);          // 隣の画素との位置の差（画素あたり）
  float3 dp_dy = ddy(p);
  float change = length(dn_dx) + length(dn_dy);                   // 法線の変化の大きさ [rad / 画素]
  // 凸なら ∂n と ∂p が同じ向き、凹なら逆向き（式 33）。鞍点では常に +1 にするのがよい。
  float s = (dot(dn_dx, dp_dx) + dot(dn_dy, dp_dy) > 0.0) ? 1.0 : -1.0;
  return k1 * s * change + k2;
}
```

`PixelSpreadAngle`、`BaseLod`、`ConeLod`、`AdvanceCone`、`SurfaceSpreadAngle` がレイ コーンの完成形です。`SurfaceSpreadAngle` はラスタライズ側（G バッファを書くピクセル シェーダー）で呼んで、結果を G バッファに入れておく関数です。ヒット シェーダーの中では `ddx` が使えません。

## ライティング {#lighting}

```hlsl
// ================= ③ ライティング =================

static const float kPi = 3.14159265;

// L1 球面調和から、法線方向の放射照度（拡散の環境光）を求める。
// 係数の並びは 0 = 定数項、1〜3 = (x, y, z)。この係数の作り方は別ページの話で、ここでは受け取るだけ。
float3 EvaluateAmbient(float3 n) {
  // L0 の基底は 0.282095、L1 の基底は 0.488603 × (x, y, z)（実数球面調和の係数）。
  // ランバートの畳み込みで L0 は π、L1 は 2π/3 を掛ける。
  float3 irradiance = g_sh[0].xyz * (0.282095 * kPi)
                    + g_sh[1].xyz * (0.488603 * n.x * 2.0944)
                    + g_sh[2].xyz * (0.488603 * n.y * 2.0944)
                    + g_sh[3].xyz * (0.488603 * n.z * 2.0944);
  return max(irradiance, 0.0);   // L1 は負になりうるので 0 で打ち切る
}

// GGX の法線分布 D。a = 粗さ^2。
float DistributionGGX(float n_dot_h, float a) {
  float a2 = a * a;
  float d = n_dot_h * n_dot_h * (a2 - 1.0) + 1.0;
  return a2 / (kPi * d * d);
}

// Smith の可視性（高さ相関）の近似形。
float VisibilitySmith(float n_dot_v, float n_dot_l, float a) {
  float gv = n_dot_l * (n_dot_v * (1.0 - a) + a);
  float gl = n_dot_v * (n_dot_l * (1.0 - a) + a);
  return 0.5 / max(gv + gl, 1e-5);
}

// シュリックのフレネル近似。
float3 FresnelSchlick(float v_dot_h, float3 f0) {
  return f0 + (1.0 - f0) * pow(1.0 - v_dot_h, 5.0);
}

// 太陽 1 つぶんの直接光（拡散 + 鏡面）。shadow は 0（影）〜 1（日向）。
float3 DirectLighting(float3 albedo, float roughness, float metallic, float3 n, float3 v, float shadow) {
  float3 l = g_sun_dir;
  float n_dot_l = saturate(dot(n, l));
  if (n_dot_l <= 0.0 || shadow <= 0.0) return 0.0;          // 裏側と影は計算しない

  float3 h = normalize(l + v);                              // ハーフベクトル
  float n_dot_v = max(dot(n, v), 1e-4);                     // 0 割りを避ける。足した処理
  float n_dot_h = saturate(dot(n, h));
  float v_dot_h = saturate(dot(v, h));

  float a = roughness * roughness;                          // 知覚的な粗さから GGX の a へ
  float3 f0 = lerp(0.04.xxx, albedo, metallic);             // 誘電体は 4 %、金属はアルベド
  float3 fresnel = FresnelSchlick(v_dot_h, f0);

  float3 specular = DistributionGGX(n_dot_h, a) * VisibilitySmith(n_dot_v, n_dot_l, a) * fresnel;
  float3 diffuse = (1.0 - fresnel) * (1.0 - metallic) * albedo / kPi;   // 金属は拡散しない
  return (diffuse + specular) * g_sun_color * g_sun_intensity * n_dot_l * shadow;
}
```

ヒット点のライティングは直接光、環境光、反射の反射の 3 つに分けて考えます。

直接光はここでは太陽 1 つです。ランバートの拡散に GGX の鏡面を足しています。金属度が 1 に近いときは拡散がなくなります。影は次のステップの影レイで 0 か 1 です。

環境光は L1 の球面調和（4 係数）で、拡散だけにしています。反射の反射はここでは追わず環境光で打ち切ります。PICA PICA も反射を 1 回に絞り反射の交点では影を取るだけにしています。

## 影と miss とレイ生成 {#shadow-raygen}

```hlsl
// ================= ⑤ miss =================

// 反射レイが何にも当たらなかったら、空の色を返す。
[shader("miss")]
void ReflectionMiss(inout ReflectionPayload payload) {
  float3 dir = WorldRayDirection();
  // 空は、地平線で暗く、天頂で明るい簡単なグラデーション（足した処理。本番はスカイ プローブを引く）。
  float t = saturate(dir.y * 0.5 + 0.5);
  payload.radiance = lerp(float3(0.4, 0.5, 0.6), float3(0.1, 0.25, 0.6), t);
  payload.hit_distance = g_max_distance;     // 遠くに当たったことにして、デノイザーの視差を破綻させない
}

[shader("miss")]
void ShadowMiss(inout ShadowPayload payload) {
  payload.shadowed = false;                  // 何にも当たらなかった = 日向
}

// ================= ⑥ レイ生成 =================

[shader("raygeneration")]
void ReflectionRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;                      // この画素
  float depth = g_depth.Load(int3(pixel, 0));
  if (depth >= 1.0) { g_out[pixel] = 0; return; }            // 空は反射しない

  // G バッファからワールド位置と法線を復元する。
  float2 uv = (pixel + 0.5) * g_inv_size;
  float4 clip = float4(uv * float2(2, -2) + float2(-1, 1), depth, 1);   // y は上下反転
  float4 world = mul(clip, g_inv_view_proj);
  float3 position = world.xyz / world.w;
  float4 nr = g_normal_rough.Load(int3(pixel, 0));
  float3 n = normalize(nr.xyz);

  float3 view = normalize(position - g_camera_pos);          // カメラから表面へ
  float3 dir = reflect(view, n);                             // 鏡面反射（ここでは粗さのサンプリングは省略）

  // レイ コーンの初期値。最初のヒット（G バッファの面）では、距離 t0 だけ進んだ幅 alpha × t0 と、
  // 広がり角 gamma_0 + beta_0 = alpha + beta_0 から始める（式 35）。
  float t0 = length(position - g_camera_pos);
  float beta0 = g_cone_in.Load(int3(pixel, 0)).x;
  ReflectionPayload payload;
  payload.radiance = 0;
  payload.hit_distance = 0;
  payload.cone_width = g_pixel_spread * t0;
  payload.cone_spread = g_pixel_spread + beta0;

  RayDesc ray;
  ray.Origin = position + n * g_shadow_bias;                 // 自己交差を避けて少し浮かす
  ray.Direction = dir;
  ray.TMin = 0.0;
  ray.TMax = g_max_distance;
  TraceRay(g_scene, RAY_FLAG_NONE, 0xFF, 0, 0, 0, ray, payload);   // ヒット グループ 0、ミス 0 = 反射用

  // 色は HDR のまま、距離は a に入れる（デノイザーが視差で履歴を合わせるのに使う）。
  g_out[pixel] = float4(payload.radiance, payload.hit_distance);
}
```

影レイは `RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH` で最初の交点で止め `RAY_FLAG_SKIP_CLOSEST_HIT_SHADER` でヒット シェーダーを省きます。ペイロードは `shadowed = true` から始めて、ミス シェーダーだけが false にします。Ray Tracing Gems の影・AO と同じ作りです。

反射のレイ生成ではレイ コーンの初期値を G バッファから作ります。幅は `α × t0`、広がり角は `α + β0` です。

## BVH の準備 {#bvh}

ここは DXR の基本の仕組みの説明で、読んだ資料に数字はありません。

- BLAS（Bottom-Level AS）は、メッシュごとの三角形の BVH です。静的なメッシュは 1 回だけ作ります。
- TLAS（Top-Level AS）は、BLAS のインスタンス（変換行列つき）の BVH です。インスタンスの数に比例して毎フレーム作り直すのが普通です。
- 動く剛体は TLAS の変換行列だけを更新します。スキンメッシュのように形が変わる物は、BLAS を更新（refit）するか作り直します。

BLAS の更新は構造を変えずに各ノードの箱だけを広げ直します。速いが形が大きく変わると探索が遅くなります。何フレームかおきに作り直して品質を戻すという運用がよく行われます。

```text
TLAS（シーン全体）
 ├ インスタンス 1: 岩（BLAS A）  位置 (10, 0, 5)
 ├ インスタンス 2: 岩（BLAS A）  位置 (30, 0, 8)     ← 同じ BLAS を使い回す
 ├ インスタンス 3: 木（BLAS B）  位置 (15, 0, 2)
 └ インスタンス 4: キャラクター（BLAS C）            ← 形が変わるなら BLAS を更新
```

## 数字を出す C++ {#cpp}

レイ コーンの式を確かめる C++ です。球に当たった画素のレイを実際に反射して、床で測った幅とレイ コーンの予測を比べます。最後に、λ の表を出します。

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。

```cpp
// レイ コーンで予測した反射先の幅と、隣の画素のレイを実際に反射して測った幅を比べる。
// 反射体は球、受け側は床（y = -2.5 m の平面）。
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

namespace {
struct V3 {
  double x, y, z;
};
V3 operator+(V3 a, V3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
V3 operator-(V3 a, V3 b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
V3 operator*(V3 a, double s) { return {a.x * s, a.y * s, a.z * s}; }
double Dot(V3 a, V3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
double Len(V3 a) { return std::sqrt(Dot(a, a)); }
V3 Norm(V3 a) { return a * (1.0 / Len(a)); }

constexpr int kW = 1920, kH = 1080;       // 画面の大きさ [px]
constexpr double kFovY = 60.0 * 3.14159265358979 / 180.0;   // 縦の画角 [rad]
const V3 kCenter = {0, 0, 6};             // 球の中心 [m]
constexpr double kFloorY = -2.5;          // 床の高さ [m]

// 画素 (px, py) のカメラ レイの向き。カメラは原点で +z を向き、y が上。
V3 EyeDir(double px, double py) {
  const double pix = 2.0 * std::tan(kFovY * 0.5) / kH;   // 画素 1 つぶんの tan
  return Norm({(px - kW * 0.5) * pix, -(py - kH * 0.5) * pix, 1.0});
}

struct Hit {
  bool ok;
  V3 pos, normal, dir_in, dir_out;   // 球の上の位置、法線、入射方向、反射方向
  double t0;                         // カメラから球まで
};

Hit HitSphere(double px, double py, double radius) {
  const V3 d = EyeDir(px, py);
  const V3 oc = V3{0, 0, 0} - kCenter;
  const double b = Dot(oc, d);
  const double c = Dot(oc, oc) - radius * radius;
  const double disc = b * b - c;
  if (disc < 0) return {false, {}, {}, {}, {}, 0};
  const double t = -b - std::sqrt(disc);     // 手前の交点
  const V3 p = d * t;
  const V3 n = Norm(p - kCenter);
  const V3 r = d - n * (2.0 * Dot(d, n));    // 鏡面反射
  return {true, p, n, d, r, t};
}
}  // namespace

int main() {
  const double alpha = std::atan(2.0 * std::tan(kFovY * 0.5) / kH);   // 画素の広がり角 [rad]
  std::printf("画素の広がり角 alpha = %.6f rad (= %.4f 度)\n", alpha, alpha * 180 / 3.14159265358979);
  std::printf("\n半径   phi の定義        予測/測定 の平均   最小   最大   (標本数)\n");

  for (double radius : {0.5, 1.0, 2.0}) {
    // 3 通りの phi: A = sqrt(|dnx|^2 + |dny|^2)、B = |dnx| + |dny|、C = (|dnx| + |dny|) / 2
    for (int variant = 0; variant < 3; ++variant) {
      std::vector<double> ratios;
      for (int j = 10; j < 300; j += 7) {
        for (int k = -150; k <= 150; k += 7) {
          const double px = kW * 0.5 + k, py = kH * 0.5 + j;
          const Hit h = HitSphere(px, py, radius);
          const Hit hx = HitSphere(px + 1, py, radius);
          const Hit hy = HitSphere(px, py + 1, radius);
          if (!h.ok || !hx.ok || !hy.ok || h.dir_out.y > -0.05) continue;

          // 床までの距離 t1（球から床まで、反射レイに沿って）。
          const double t1 = (kFloorY - h.pos.y) / h.dir_out.y;
          // 測定: 隣のレイを同じ距離 t1 まで進めた点の間隔。x と y の平均。
          const V3 q0 = h.pos + h.dir_out * t1;
          const V3 qx = hx.pos + hx.dir_out * t1;
          const V3 qy = hy.pos + hy.dir_out * t1;
          const double measured = 0.5 * (Len(qx - q0) + Len(qy - q0));

          // 予測: w0 = alpha * t0、gamma1 = alpha + beta、w1 = w0 + gamma1 * t1。
          const double dnx = Len(hx.normal - h.normal);   // 法線の画素あたりの変化（ddx 相当）
          const double dny = Len(hy.normal - h.normal);
          double phi = 0;
          if (variant == 0) phi = std::sqrt(dnx * dnx + dny * dny);
          if (variant == 1) phi = dnx + dny;
          if (variant == 2) phi = 0.5 * (dnx + dny);
          const double s = 1.0;                  // 凸面（球の外側）なので正
          const double beta = 2.0 * s * phi;     // k1 = 1, k2 = 0
          const double w0 = alpha * h.t0;
          const double predicted = w0 + (alpha + beta) * t1;
          ratios.push_back(predicted / measured);
        }
      }
      double sum = 0, lo = 1e9, hi = 0;
      for (double r : ratios) { sum += r; lo = std::min(lo, r); hi = std::max(hi, r); }
      const char* names[] = {"A sqrt(dnx^2+dny^2)", "B |dnx|+|dny|", "C (|dnx|+|dny|)/2"};
      std::printf("%.1f   %-20s %.3f          %.3f  %.3f  (%d)\n", radius, names[variant],
                  sum / ratios.size(), lo, hi, static_cast<int>(ratios.size()));
    }
  }

  // ---- テクスチャ LOD の例: 2048x2048 のテクスチャを貼った 1 m 四方の板 ----
  // Δ = 0.5 log2(ta / pa)（ta: テクセル空間の面積の 2 倍、pa: ワールド空間の面積の 2 倍）。
  const double tex = 2048.0;
  const double ta = tex * tex * 1.0;         // uv の三角形 (0,0)-(1,0)-(0,1) の面積の 2 倍 = 1
  const double pa = 1.0;                     // 1 m 四方の板の半分の三角形の面積の 2 倍 = 1 m^2
  const double delta = 0.5 * std::log2(ta / pa);
  std::printf("\nΔ(基準の LOD) = %.2f\n", delta);
  std::printf("距離[m]  角度[度]  w[mm]   lambda\n");
  for (double dist : {1.0, 2.0, 4.0, 8.0, 16.0}) {
    for (double deg : {0.0, 60.0, 80.0}) {
      const double w = alpha * dist;                              // 円錐の幅 [m]
      const double cos_t = std::cos(deg * 3.14159265358979 / 180.0);   // |n・d|
      const double lambda = delta + std::log2(w) + 0.5 * std::log2(1.0 / cos_t);
      std::printf("%5.0f   %5.0f   %6.2f  %6.2f\n", dist, deg, w * 1000.0, lambda);
    }
  }
  return 0;
}
```

```text title="実行結果"
画素の広がり角 alpha = 0.001069 rad (= 0.0613 度)
```

```text title="実行結果（続き）"
半径   phi の定義        予測/測定 の平均   最小   最大   (標本数)
0.5   A sqrt(dnx^2+dny^2)  1.524          1.393  1.811  (173)
0.5   B |dnx|+|dny|        2.083          1.942  2.303  (173)
0.5   C (|dnx|+|dny|)/2    1.082          1.004  1.176  (173)
1.0   A sqrt(dnx^2+dny^2)  1.479          1.364  1.944  (740)
1.0   B |dnx|+|dny|        1.994          1.859  2.314  (740)
1.0   C (|dnx|+|dny|)/2    1.077          1.001  1.192  (740)
2.0   A sqrt(dnx^2+dny^2)  1.336          1.304  1.453  (1800)
2.0   B |dnx|+|dny|        1.728          1.661  1.885  (1800)
2.0   C (|dnx|+|dny|)/2    1.045          0.928  1.080  (1800)
```

```text title="実行結果（続き）"
Δ(基準の LOD) = 11.00
距離[m]  角度[度]  w[mm]   lambda
    1       0     1.07    1.13
    1      60     1.07    1.63
    1      80     1.07    2.39
    2       0     2.14    2.13
    2      60     2.14    2.63
    2      80     2.14    3.39
    4       0     4.28    3.13
    4      60     4.28    3.63
    4      80     4.28    4.39
    8       0     8.55    4.13
    8      60     8.55    4.63
    8      80     8.55    5.39
   16       0    17.11    5.13
   16      60    17.11    5.63
   16      80    17.11    6.39
```

HLSL は `dxc`（`-T lib_6_3`）でコンパイルして確かめました。実行して絵は確かめていません。「足した処理」「一例」と書いた所は資料にない処理です。

## よくあるミス

??? failure "遠くの反射のテクスチャが、チラチラ光る"
    ミップ 0 を読んでいる。レイ コーンの幅からミップを求める。強いデノイザーがあるならミップ 0 のままでもぼけて目立たなくなることがある。

??? failure "反射の中のテクスチャが、ぼやけすぎる"
    `λ` に足す項を多く見積もっている。|n・d| の項が大きすぎないか `k1`・`k2` を 0 にして確かめる。

??? failure "テクスチャの添字が、画素ごとに違う場所で乱れる"
    `NonUniformResourceIndex` を付けていない。隣のレイが別のメッシュに当たると、添字が異なる。

??? failure "裏から当たった面が真っ暗になる"
    法線を反転していない。`dot(n, d) > 0` なら法線を反転する。

??? failure "影の中にギザギザの縞が出る"
    影レイの原点が面の中に埋まっている。法線方向にずらす量（`g_shadow_bias`）を大きくする。大きすぎると影が面から離れて浮く。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒット シェーダーは、属性の補間、ミップの選択、テクスチャ、影、ライティングを行う。
    - [x] 画面の微分がないので、レイ コーンの幅からミップを求める。
    - [x] `λ = Δ + log2(w) + 0.5 log2(1 / |n・d|)`。距離が 2 倍になると λ が 1 増える。
    - [x] 曲面の反射は広がり角が変わる。最初のヒットだけ曲率を持たせる。
    - [x] 強いデノイザーがあるならミップ 0 でも足りる。

## 参考

- Tomas Akenine-Möller, Jim Nilsson, Magnus Andersson, Colin Barré-Brisebois, Robert Toth, Tero Karras, "Texture Level of Detail Strategies for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 20, Apress, 2019. DOI: 10.1007/978-1-4842-4427-2_20（20.1〜20.2、20.3.4、20.4、20.5 を読んだ。ray differentials の導出とコードの付録は読んでいない）
- Colin Barré-Brisebois, Henrik Halén, Graham Wihlidal, Andrew Lauritzen, Jasper Bekkers, Tomasz Stachowiak, Johan Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, Apress, 2019. DOI: 10.1007/978-1-4842-4427-2_25（25.1、25.2.2、25.2.3 を読んだ）
- Microsoft, "DirectX Raytracing (DXR) Functional Spec"（今回は読み直していない）。

## 関連ページ

- [Ray-Traced Reflections](index.md)
- [Ray Generation](ray-generation.md)
- [Hybrid Pipeline](hybrid.md)
- [Denoising](denoise.md)
