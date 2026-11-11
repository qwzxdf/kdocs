---
title: Terrain Decals and Roads
tags:
  - 描画
---

# Terrain Decals and Roads

地形に道を通したい爆発の焦げ跡を残したい足跡をつけたいという場面は多いものです。地形の素材を全部描き直す方法もありますが、道は 1 本ごとに素材を作れませんし足跡は、ゲーム中に増えます。地形の表面にあとから「貼る」仕組みが要ります。

<strong>地形に貼るものは 2 通りに分けて考えます</strong>。素材の重みを塗り替えるスプラットと地形とは別のテクスチャを地形の形に沿って投影するデカールです。このページでは両者の使い分け道をスプラインから作る方法（距離、整地、草の除外）、箱で投影するデカール、足跡のような動的な跡を説明します。

!!! tip "ポイント"
    - 道や広い範囲の跡はスプラットの重みを塗って、地形の素材として扱います。足音やぬかるみの材質まで変えられます。
    - 焼け跡や血痕のような一時的な跡は、デカールで投影します。後から消せます。
    - 道はスプラインからの距離で重みを決めて、高さも整地して草や木を避けます。
    - デカールは箱の中の画素だけにテクスチャを貼ります。深度からワールド座標を復元して、箱のローカル座標で判定します。
    - 急斜面ではデカールが引き伸ばされるので、法線でフェードさせます。

!!! info "このページを読む前に"
    - [Terrain Texturing](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）

## スプラットとデカールの使い分け {#choice}

スプラットは地形の素材の重みを書き換える方法です。道、小道、広い範囲の足跡に向いています。地形の素材の一部になるので足音やぬかるみのような材質まで変えられます。

デカールは地形のデータに触れずに見た目だけを重ねる方法です。焼け跡、血痕、爆発の跡、魔法陣に向いています。あとから消せるので動的な跡にも向きます。

## 道をつくる {#road}

道は制御点を結んだ曲線（スプライン）で定義します。曲線に沿って 3 つのことを行います。

1. スプラットに塗ります。曲線からの距離で重みを決めます。中心は 1 で縁へ向かって 0 に減らします。
2. 高さマップを整えます。道の中央で地形の高さと道の高さを混ぜて、平らにします。斜面を横切る道が凸凹だと不自然になります。
3. 草や木を避けます。道の上に置かないように配置のマスクにも道を書きます。

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="道の断面。中心が平らに整地され、両側に緩やかな土手ができる。重みは中心で 1 で縁で 0 になる"><text x="14" y="22" class="fig-title">道の断面: 整地と、素材の重み</text>
<path d="M40,150 C120,130 180,100 240,92 L300,92 L420,92 L480,92 C540,100 600,130 680,140" fill="none" stroke="#94a3b8" stroke-dasharray="5 4" stroke-width="2"/>
<path d="M40,150 C120,140 180,120 240,110 L300,92 L420,92 L480,110 C540,118 600,130 680,140" fill="none" stroke="#4c8bf5" stroke-width="3.5"/>
<text x="360" y="84" text-anchor="middle" style="font-size:12px;font-weight:600;fill:#4c8bf5">道の高さ（平ら）</text><text x="120" y="120" style="font-size:12px;fill:#64748b">元の地形</text>
<rect x="300" y="170" width="120" height="14" fill="rgba(229,170,40,0.55)"/><rect x="240" y="170" width="60" height="14" fill="rgba(229,170,40,0.25)"/><rect x="420" y="170" width="60" height="14" fill="rgba(229,170,40,0.25)"/>
<text x="360" y="204" text-anchor="middle" style="font-size:12px">スプラットの重み（中心 1 → 縁 0）</text>
<line x1="240" y1="222" x2="480" y2="222" stroke="currentColor" stroke-width="1.5"/><text x="360" y="240" text-anchor="middle" style="font-size:12px">整地の重みは、道の幅より少し広く取る → 両側に緩やかな土手ができる</text></svg>

距離はスプラインを折れ線に分けて、点と線分の最短距離で求めます。

```hlsl
StructuredBuffer<float2> g_spline_points : register(t0);   // スプラインを折れ線にした点列（ワールド XZ）
RWTexture2D<float> g_road_weight : register(u0);           // スプラットの道の重み
RWTexture2D<float> g_road_grade : register(u1);            // 整地の重み

cbuffer RoadConstants : register(b0) {
  float2 g_map_origin;       // マップの左下（ワールド XZ）
  float g_texel_size;        // 1 テクセルのメートル数
  uint g_point_count;
  float g_road_width;        // 道の幅（メートル）。例: 4
  float g_grade_width;       // 整地の幅（メートル）。道より広く。例: 8
  uint2 g_map_size;
};

// 点 p から、線分 a-b までの最短距離
float DistanceToSegment(float2 p, float2 a, float2 b) {
  float2 ab = b - a;
  float t = saturate(dot(p - a, ab) / max(dot(ab, ab), 1e-6));   // 線分上の位置 0..1
  return distance(p, a + ab * t);
}

[numthreads(8, 8, 1)]
void RoadSplatCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_map_size)) return;
  float2 p = g_map_origin + (float2(id.xy) + 0.5) * g_texel_size;

  // 折れ線の全線分のうち、最も近い距離を探す
  float d = 1e9;
  for (uint i = 0; i + 1 < g_point_count; ++i) {
    d = min(d, DistanceToSegment(p, g_spline_points[i], g_spline_points[i + 1]));
  }

  // 道の重み: 幅の 0.4〜0.5 倍で 1 から 0 へ落とす（縁をなめらかに）
  float w = 1.0 - smoothstep(g_road_width * 0.4, g_road_width * 0.5, d);
  // 整地の重み: 道より広く取って、土手をつくる
  float g = 1.0 - smoothstep(g_road_width * 0.5, g_grade_width * 0.5, d);

  g_road_weight[id.xy] = max(g_road_weight[id.xy], w);     // 既存の道に足す（交差点で合成される）
  g_road_grade[id.xy] = max(g_road_grade[id.xy], g);
}
```

高さの整地は次の式で混ぜます。

```text
新しい高さ = lerp(元の高さ, 道の高さ, 整地の重み)
```

「道の高さ」はスプラインの高さ（制御点の高さの補間）です。整地の重みを道の幅より広く取ると、道の両側に緩やかな土手ができて、自然に見えます。

数字で確かめます。道の幅が 4 m、整地の幅が 8 m なら中心から 2 m までが道（重み 1 に近い）、2〜4 m までが土手です。高さマップの 1 テクセルが 1 m なら土手は 2 テクセルです。点の数が 1000、マップが 1024 × 1024 ならこの計算シェーダーは、`1024 × 1024 × 1000 ≒ 10 億回` の距離計算になるので実際は線分の範囲に入るテクセルだけを調べる（線分ごとに四角形を描く）方が軽くなります。

## デカール: 箱で投影する {#box}

デカールは箱（ボリューム）の中に入った地形の表面にだけテクスチャを貼る方式が標準です（Persson、2011「Volume Decals」）。

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="デカールの箱。箱の中に入っている地形の画素だけにテクスチャを貼る"><defs><marker id="dcA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">箱の中の画素だけに貼る</text>
<path d="M40,200 C140,170 220,160 300,150 C380,140 460,170 680,150 L680,230 L40,230 Z" fill="rgba(148,163,184,0.25)" stroke="#94a3b8" stroke-width="2"/>
<rect x="250" y="70" width="190" height="130" fill="none" stroke="#e5aa28" stroke-width="2.5" stroke-dasharray="6 4"/><text x="345" y="62" text-anchor="middle" style="font-size:12px;font-weight:600">デカールの箱（位置・向き・大きさ）</text>
<path d="M250,150 C290,150 320,148 345,146 C390,142 420,150 440,152" fill="none" stroke="#e5484d" stroke-width="5"/>
<text x="345" y="122" text-anchor="middle" style="font-size:12px;fill:#e5484d;font-weight:600">箱の中の地形だけにテクスチャが貼られる</text>
<g stroke="currentColor" stroke-width="2" marker-end="url(#dcA)"><line x1="300" y1="30" x2="300" y2="68"/><line x1="345" y1="30" x2="345" y2="68"/><line x1="390" y1="30" x2="390" y2="68"/></g><text x="470" y="40" style="font-size:12px">箱の「上から」投影（ローカル XZ → UV）</text>
<text x="360" y="250" text-anchor="middle" style="font-size:12px">箱の外の地形は、ピクセル シェーダーで捨てる</text></svg>

手順は次のとおりです。

1. 箱を描きます。立方体のメッシュをデカールの位置、向き大きさに変換して描きます。
2. ピクセル シェーダーで、その画素のワールド座標を深度から復元します。
3. ワールド座標を箱のローカル座標に変換します。
4. ローカル座標が箱の外（各軸の `[-0.5, 0.5]` の外）なら捨てます。中ならローカルの XZ を UV にして、テクスチャを引きます。

まず、定数と頂点シェーダー（箱を描くだけ）です。

```hlsl
Texture2D<float> g_depth : register(t0);          // シーンの深度（SRV）
Texture2D<float4> g_decal : register(t1);         // デカールのテクスチャ
SamplerState g_linear_clamp : register(s0);

cbuffer DecalConstants : register(b1) {
  float4x4 g_view_proj;
  float4x4 g_decal_world;      // 単位立方体（-0.5〜0.5）→ ワールド
  float4x4 g_inv_view_proj;    // クリップ空間 → ワールド
  float4x4 g_world_to_decal;   // ワールド → デカールのローカル（箱は -0.5〜0.5）
  float3 g_decal_up_world;     // デカールが向いている方向（ワールドの単位ベクトル）
  float _pad;
  float2 g_inv_screen_size;    // 1 / 画面の幅・高さ
  float2 _pad2;
};

float4 DecalVS(float3 local_pos : POSITION) : SV_Position {
  float4 world = mul(float4(local_pos, 1.0), g_decal_world);
  return mul(world, g_view_proj);
}
```

次に、ピクセル シェーダーです。

```hlsl
float4 DecalPS(float4 pos : SV_Position) : SV_Target {
  // ① 画素の深度から、ワールド座標を復元する
  float2 uv = pos.xy * g_inv_screen_size;
  float depth = g_depth.Load(int3(pos.xy, 0));
  float4 ndc = float4(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0, depth, 1.0);
  float4 world = mul(ndc, g_inv_view_proj);
  world.xyz /= world.w;                                  // 同次座標を戻す

  // ② デカールのローカル座標へ。箱の中は各軸が -0.5〜0.5
  float3 local = mul(float4(world.xyz, 1.0), g_world_to_decal).xyz;

  // ③ 箱の外の画素は捨てる。0.5 - |local| が 1 軸でも負なら外
  clip(0.5 - abs(local));

  // ④ XZ を UV にして、テクスチャを引く
  float2 decal_uv = local.xz + 0.5;
  float4 c = g_decal.SampleLevel(g_linear_clamp, decal_uv, 0);

  // ⑤ 急斜面で引き伸ばされるのを、法線でフェードして防ぐ（足した処理）
  //    法線は、深度の画面微分から復元する（G バッファがあればそれを読む）
  float3 n = normalize(cross(ddx(world.xyz), ddy(world.xyz)));
  float facing = saturate(dot(n, g_decal_up_world));
  c.a *= smoothstep(0.3, 0.7, facing);

  return c;       // アルファ ブレンド（SrcAlpha / InvSrcAlpha）でシーンに重ねる
}
```

①の `ndc.z` は深度バッファの値をそのまま使います。標準の深度なら 0（近い）〜 1（遠い）です。リバース Z なら同じ式で動きますが `g_inv_view_proj` をリバース Z の射影行列から作る必要があります。

箱は裏面（背面）を描いて深度テストを無効にします。カメラが箱の中に入っても描画が消えないようにするためです。ブレンドは `SrcAlpha / InvSrcAlpha` のアルファ ブレンドです。

!!! note "確かめた範囲"
    HLSL は `fxc` で、`RoadSplatCS`（`cs_5_0`）、`DecalVS`（`vs_5_0`）、`DecalPS`（`ps_5_0`）、足跡の減衰（`FootprintDecayCS`、`cs_5_0`）をコンパイルしてエラーが出ないことを確かめました。数字は式からの手計算です。GPU での描画は確認していません。

注意点は次のとおりです。

- 急斜面で引き伸ばされます。箱の「上から」の投影なので急斜面ではデカールが伸びます。法線でフェードさせるか急な場所に貼らないようにします。
- 重ねる数が多いと重くなります。デカール 1 枚につき箱の面積ぶんの画素処理が増えます。数百枚を超えると目立ちます。
- 色だけでなく法線や粗さも変えるならディファードの G バッファに書き込むか、ライティングで直接足します。
- 重ねる順序が見た目を変えるので、優先度で並べます。

## 足跡など動的な跡 {#dynamic}

足跡やタイヤの跡のようにゲーム中に増える跡は、スプラット マップに直接書き込みます。足の位置に足跡の形のブラシを描きます。毎フレーム全体を少し暗くすると、古い跡が消えます（[Trampled Grass](../vegetation/trample.md) も同じ仕組みです）。

跡のマップはカメラの周りの数十メートルだけを覆う窓として持ちます。円環バッファ（クリップマップと同じ発想）にして、カメラが動いたら窓の外へ出た側を捨てます。跡のテクスチャは `R8_UNORM` 1 枚で十分です。0 が跡なし 1 が深い跡です。

```hlsl
RWTexture2D<unorm float> g_footprint : register(u2);

cbuffer FootprintConstants : register(b2) {
  float g_decay;             // 1 フレームに引く量。例: 0.002（1/60 秒なら約 8 秒で消える）
  uint2 g_footprint_size;
  float _pad3;
};

// 毎フレーム、全体を少しずつ薄くする
[numthreads(8, 8, 1)]
void FootprintDecayCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_footprint_size)) return;
  g_footprint[id.xy] = max(g_footprint[id.xy] - g_decay, 0.0);
}
```

減衰が `0.002` なら 1 から 0 まで 500 フレーム（60 fps で約 8 秒）です。値は跡を何秒残したいかから `1 / (残したい秒数 × フレームレート)` で決めます。8 ビットの `R8_UNORM` は 1 段階が `1 / 255 ≒ 0.0039` なので、`0.002` の減衰は丸めで 0 になって、跡が消えません。減衰を 1 段階（`1/255`）の倍数にするかフレームを間引いて引きます。この落とし穴は 8 ビットのマップで起きます。

## よくあるミス {#mistakes}

??? failure "道が地形から浮いて見える"
    原因は道の高さと地形の高さが合っていないことです。高さマップを道の高さへ整地するかデカールとして地形に投影します。整地の重みは道の幅より少し広くして、土手を作ります。

??? failure "斜面でデカールが、縞状に引き伸ばされる"
    原因は箱の上から投影しているので、急な面でデカールの 1 テクセルが広い面積に伸びることです。法線でデカールの強さを落とします。

??? failure "足跡が、いつまでも消えない"
    原因は 8 ビットのマップに対して、減衰が 1 段階（約 0.0039）より小さいことです。引き算が丸めで 0 になります。減衰を大きくするか数フレームに 1 回、大きく引きます。

??? failure "カメラが箱の中に入ると、デカールが消える"
    原因は箱の表面を描いていることです。カメラが箱の内側にいると表面が裏返って、カリングされます。裏面を描いて深度テストを無効にします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 道や広い範囲の跡はスプラットで、一時的な跡はデカールで貼ります。
    - [x] 道はスプラインからの距離で重みを決めて、整地して草を避けます。
    - [x] デカールは箱の中の画素だけに深度から復元したワールド座標で貼ります。
    - [x] 急斜面では法線でフェードします。
    - [x] 8 ビットの跡のマップは、減衰が 1 段階より小さいと消えません。

## 参考 {#references}

このページは次の資料を読まずに書きました。式と HLSL は一般的な考え方から自分で書いたもので、`fxc` でのコンパイルまで確かめています。

- Persson, "Volume Decals", GPU Pro 2, 2011
- Andersson, "Terrain Rendering in Frostbite Using Procedural Shader Splatting", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games（Frostbite の地形の素材合成）
- Microsoft Learn, "HLSL: clip"（`clip` 関数）

## 関連ページ

- [Terrain Texturing](index.md)
- [Virtual Texturing](virtual-texture.md)
