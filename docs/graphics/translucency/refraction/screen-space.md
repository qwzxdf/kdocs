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

## Screen-Space Refraction {#画面空間の屈折}
**屈折した光線を、本当に追跡する**（レイトレ）のは重いので、**ゲームでは、画面の画像を「背景」として、歪めて読む**方法が**標準**です。

### Steps {#手順}

画面空間屈折の手順は 3 段階です。不透明な物を、すべて描画します。この時点の画面（HDR カラー）を、別のテクスチャ（`scene_color_copy`）にコピーします。最後に、半透明を描くときに、ガラスの面で `scene_color_copy` を歪んだ UV で読み、背景とします。

**なぜコピーが要るか**：**ガラスを描くレンダー ターゲットを、同時にテクスチャとして読めない**（**読み書きの競合**）ためです。

### How to Distort the UV {#uv-の歪ませ方}

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

## Common Mistakes {#よくあるミス}

??? failure "画面の端で、屈折が引き伸ばされる"
    **端でずらす量を弱める**（フェード）。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **法線で UV をずらして、画面を読む**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [Refraction](index.md)
- [境界の問題](boundary.md)
- [Fresnel](fresnel.md)
