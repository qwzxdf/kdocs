---
title: 画面空間の屈折
tags:
  - 描画
---

# 画面空間の屈折

**屈折する物体の後ろの景色は、既に描いた画面（不透明パスの結果）に入っています**。**法線に応じて、読み出す位置をずらすだけ**で、**屈折の見た目が得られます**。このページでは、**画面空間の屈折の仕組みと、コード**を説明します。

!!! tip "ポイント"
    - **不透明パスの結果を、テクスチャとしてコピーしておく**。
    - **法線（のXY）に比例して、UV をずらして読む**。
    - **ずらす量 ＝ 屈折の強さ**。
    - **画面の外は読めない**ので、**端で破綻**する。

## 画面空間の屈折
**屈折した光線を、本当に追跡する**（レイトレ）のは重いので、**ゲームでは、画面の画像を「背景」として、歪めて読む**方法が**標準**です。

### 手順

| 手順 | 内容 |
| --- | --- |
| **① 不透明を描く** | **不透明な物を、すべて描画** |
| **② 画像をコピー** | **この時点の画面（HDR カラー）を、別のテクスチャ（`scene_color_copy`）にコピー** |
| **③ 半透明を描く** | **ガラスの面で、`scene_color_copy` を、歪んだ UV で読み、背景とする** |

**なぜコピーが要るか**：**ガラスを描くレンダー ターゲットを、同時にテクスチャとして読めない**（**読み書きの競合**）ためです。

### UV の歪ませ方

**法線の XY 成分（ビュー空間）に応じて、UV をずらす**のが**簡易**です。

```hlsl
float2 screen_uv = input.position.xy / screen_size;
float3 view_normal = mul(world_normal, (float3x3)view_matrix);
float2 offset = view_normal.xy * refraction_strength;
float3 background = scene_color_copy.Sample(linear_clamp, screen_uv + offset).rgb;
```

| 点 | 説明 |
| --- | --- |
| **`view_normal.xy`** | **法線が、画面の左右・上下にどれだけ傾いているか** |
| **`refraction_strength`** | **歪みの強さ**（**屈折率・厚み**に合わせて調整。**0.02〜0.1**） |
| **`linear_clamp`** | **端でクランプ**（**画面外を読まない**） |

**より物理的**には、**`refract` で屈折ベクトルを求め、そのベクトルを使って、「背景の画面位置」を決める**方法もあります。

```hlsl
float3 view_dir = normalize(world_position - camera_position);
float3 refracted = refract(view_dir, world_normal, 1.0 / 1.5);
float3 sample_world = world_position + refracted * thickness;
float4 clip = mul(float4(sample_world, 1.0), view_projection);
float2 refract_uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
float3 background = scene_color_copy.Sample(linear_clamp, refract_uv).rgb;
```

| 点 | 説明 |
| --- | --- |
| **`thickness`** | **ガラスの厚み**（**屈折した光が進む距離の見積もり**）。**固定値・テクスチャ・深度差** |
| **`sample_world`** | **屈折光が、ガラスを出たあたりのワールド位置** |
| **`refract_uv`** | **その位置を、画面に投影した UV**。**ここの背景を読む** |

## よくあるミス

??? failure "画面の端で、屈折が引き伸ばされる"
    **端でずらす量を弱める**（フェード）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **法線で UV をずらして、画面を読む**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [屈折](index.md)
- [境界の問題](boundary.md)
- [フレネル](fresnel.md)
