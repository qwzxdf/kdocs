---
title: Screen-Space Refraction
tags:
  - 描画
---

# Screen-Space Refraction

**屈折する物体の後ろの景色は、既に描いた画面（不透明パスの結果）に入っています**。**法線に応じて、読み出す位置をずらすだけ**で、**屈折の見た目が得られます**。このページでは、**画面空間の屈折の仕組みと、コード**を説明します。

!!! tip "ポイント"
    - **不透明パスの結果を、テクスチャとしてコピーしておく**。
    - **法線（のXY）に比例して、UV をずらして読む**。
    - **ずらす量 ＝ 屈折の強さ**。
    - **画面の外は読めない**ので、**端で破綻**する。

## 画面空間の屈折
**屈折した光線を、本当に追跡する**（レイトレ）のは重いので、**ゲームでは、画面の画像を「背景」として、歪めて読む**方法が**標準**です。

### 手順

画面空間屈折の手順は 3 段階です。不透明な物を、すべて描画します。この時点の画面（HDR カラー）を、別のテクスチャ（`scene_color_copy`）にコピーします。最後に、半透明を描くときに、ガラスの面で `scene_color_copy` を歪んだ UV で読み、背景とします。

**なぜコピーが要るか**：**ガラスを描くレンダー ターゲットを、同時にテクスチャとして読めない**（**読み書きの競合**）ためです。

### UV の歪ませ方

**法線の XY 成分（ビュー空間）に応じて、UV をずらす**のが**簡易**です。

```hlsl
float2 screen_uv = input.position.xy / screen_size;
float3 view_normal = mul(world_normal, (float3x3)view_matrix);
float2 offset = view_normal.xy * refraction_strength;
float3 background = scene_color_copy.Sample(linear_clamp, screen_uv + offset).rgb;
```

歪みのコードの要点です。`view_normal.xy` は、法線が画面の左右・上下にどれだけ傾いているかを表します。`refraction_strength` は歪みの強さで、屈折率や厚みに合わせて調整します（0.02〜0.1）。`linear_clamp` で端をクランプし、画面外を読まないようにします。

**より物理的**には、**`refract` で屈折ベクトルを求め、そのベクトルを使って、「背景の画面位置」を決める**方法もあります。

```hlsl
float3 view_dir = normalize(world_position - camera_position);
float3 refracted = refract(view_dir, world_normal, 1.0 / 1.5);
float3 sample_world = world_position + refracted * thickness;
float4 clip = mul(float4(sample_world, 1.0), view_projection);
float2 refract_uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
float3 background = scene_color_copy.Sample(linear_clamp, refract_uv).rgb;
```

厚みを考慮した版のコードの要点です。`thickness` はガラスの厚みで、屈折した光が進む距離の見積もりです。固定値・テクスチャ・深度差から決めます。`sample_world` は、屈折光がガラスを出たあたりのワールド位置です。`refract_uv` は、その位置を画面に投影した UV で、ここの背景を読みます。

## 考え方：画面のコピーを、ずらして読む

本当の屈折は、**光線を、物体の中で、曲げて、追跡**する必要があり、**重い**です。**画面空間の屈折**は、すでに描いた**シーンの色**を、**テクスチャとして、コピー**し、**屈折する物体の、画素で、読む位置を、ずらす**ことで、**屈折らしい、歪み**を、安く作ります（Sousa、2005）。

```text
① 不透明な物を、すべて描く                       → シーンの色
② シーンの色を、テクスチャにコピーする           （CopyResource）
③ ガラスなどの屈折する物を描く:
     画素ごとに、法線から「ずらし量」を求め、
     コピーしたシーンを、ずらした位置で読んで、ガラスの色にする
```

## 実装

### ① シーンの色を、コピーする

屈折する物は、**画面に、すでに描かれた**、シーンの色を、**読み**ながら、**同じ画面に、描きます**。**読み書きが、同じテクスチャ**だと、衝突する（同時に、読めない）ので、**別のテクスチャに、コピー**します。

```cpp
// 不透明の描画の後、屈折する物を描く前に、シーンの色を、コピーする。
context->CopyResource(scene_copy_tex.Get(), scene_color_tex.Get());
// 屈折する物の描画では、scene_copy_srv を、読み取り元にする。書き込み先は、scene_color_rtv のまま。
```

`CopyResource` は、**同じ大きさと、形式**の、テクスチャ同士を、コピーします。MSAA のレンダー ターゲットを、コピーするには、**先に、リゾルブ**（`ResolveSubresource`）して、**1 サンプルの、テクスチャ**にします。

### ② ピクセル シェーダー

```hlsl
Texture2D<float4> g_scene_copy : register(t0);
Texture2D<float> g_scene_depth : register(t1);

float4 main(PSInput input) : SV_Target {
  float2 screen_uv = input.position.xy * g_inv_screen_size;

  // 法線を、ビュー空間に直して、その xy を「ずらし量」にする。
  float3 view_normal = mul((float3x3)g_view, normalize(input.world_normal));
  float2 offset = view_normal.xy * g_refraction_strength;
  float2 refract_uv = screen_uv + offset * float2(1, -1);          // 画面の y は、下向きなので、反転

  float3 refracted = g_scene_copy.Sample(g_linear_clamp, refract_uv).rgb;
  return float4(refracted * g_tint, 1.0);
}
```

| 要素 | 内容 |
| --- | --- |
| 法線 | **面が、傾いているほど、大きく、ずれる** |
| `g_refraction_strength` | **屈折の強さ**。0.02〜0.1。**屈折率の、違いと、物体の厚み**を、まとめた、調整値 |
| `g_tint` | ガラスの色（色付きガラスなら、透過色） |

## 品質を、高める、工夫

### ① 手前の物を、ずらさない

ずらした先に、**ガラスより、手前にある物**（ガラスの、手前に、立っている人）が、あると、その色を、**読んでしまい**、**人の色が、ガラスに、にじむ**ことがあります。**深度**で、判定します。

```hlsl
float scene_depth = LinearizeDepth(g_scene_depth.Sample(g_point_clamp, refract_uv).r);
float glass_depth = LinearizeDepth(input.position.z);
if (scene_depth < glass_depth) refract_uv = screen_uv;        // ガラスより手前の物は、ずらさない
```

### ② 深度で、ずらし量を、変える

ガラスの**向こうの物**が、**遠いほど**、屈折の、**ずれ**は、大きく見えます（視線が、曲がって、遠くの物を、見るため）。

```hlsl
float behind = max(scene_depth - glass_depth, 0.0);            // ガラスの向こうの、物までの距離
offset *= saturate(behind / g_refraction_distance);              // 近い物は、あまりずらさない
```

### ③ 画面の端

ずらした UV が、**画面の外**になることがあります。**CLAMP** で、端の色を、伸ばすか、**ずらし量を、端で、弱め**ます。

```hlsl
float2 edge = saturate(min(refract_uv, 1.0 - refract_uv) * 10.0);        // 端から 0.1 の幅で、弱める
offset *= min(edge.x, edge.y);
```

### ④ 色の、分散（任意）

RGB を、**わずかに違うずらし量**で読むと、**縁が、虹色**になります（[Dispersion](dispersion.md)）。

## 限界

| 限界 | 内容 |
| --- | --- |
| **画面の外**が、映らない | 屈折で、画面の外の、物が、見える位置に、ずれても、**画面にない**ので、読めない（端の、色を、伸ばす） |
| **ガラスの手前**の物 | 上記の、深度チェックで、**ごまかす**。完全には、正しくない |
| **2 重の、屈折**（ガラス越しの、ガラス） | **コピーが、1 枚**なので、**ガラスの、向こうの、ガラスの、屈折が、反映されない**。ガラスを、**奥から手前**に、描き、**そのたびに、コピー**すると、近似できる（重い） |
| **内部の、反射**（全反射、複数回の、内部反射） | 扱えない |
| **正確さ** | 実際の、光の経路と、違う。**「それらしく、見える」**だけ |

## 向く場面と、向かない場面

| 場面 | 判断 |
| --- | --- |
| 窓ガラス、水面、氷、ガラス瓶（薄い、または、簡易） | **向く** |
| 水晶、宝石、**厚い**ガラスの、塊 | **不足**（内部の、屈折・反射が、重要）。**厚み・色**の、工夫が、必要（[Thin and Thick Glass](thin-thick.md)） |
| 画面の端の、ガラス | 注意（画面外を、読めない） |

## よくあるミス

??? failure "画面の端で、屈折が引き伸ばされる"
    **端でずらす量を弱める**（フェード）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **法線で UV をずらして、画面を読む**

## 参考

- Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005
- Wyman, "An Approximate Image-Space Approach for Interactive Refraction", ACM Transactions on Graphics (SIGGRAPH 2005)
- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Microsoft Learn, "ID3D11DeviceContext::CopyResource"

## 関連ページ

- [Refraction](index.md)
- [Refraction Boundary Problems](boundary.md)
- [Fresnel](fresnel.md)
