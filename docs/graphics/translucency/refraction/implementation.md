---
title: 実装の全体像とコスト
tags:
  - 描画
---

# 実装の全体像とコスト

**屈折を実装する手順を、全体として見ます**。**不透明の描画 → 画面のコピー → 屈折物体の描画**の順で、**フレネル・厚み・色を組み合わせます**。このページでは、**実装の流れと、コスト・限界**を説明します。

!!! tip "ポイント"
    - **手順：不透明パス → 画面のコピー → 屈折物体 → 半透明**。
    - **画面のコピー ＝ 1 回の帯域コスト**。
    - **屈折物体同士の重なりは、扱えない**（片方の層のみ）。
    - **限界：画面外・重なり・手前の物**。

## 実装の全体像
```hlsl
float4 PSGlass(VsOutput input) : SV_Target {
  float3 n = normalize(input.normal);
  float3 v = normalize(camera_position - input.world_position);
  float2 screen_uv = input.position.xy / screen_size;

  float3 refracted = refract(-v, n, 1.0 / ior);
  float2 uv = ScreenUvFromWorld(input.world_position + refracted * thickness);
  uv = ValidateUv(uv, screen_uv, input.position.z);

  float3 background = scene_color_copy.SampleLevel(linear_clamp, uv, roughness * kMaxMip).rgb;
  background *= exp(-absorption * thickness);

  float3 reflection = SampleEnvironment(reflect(-v, n), roughness);
  float fresnel = Fresnel(saturate(dot(n, v)), 0.04);
  float3 color = lerp(background, reflection, fresnel);
  return float4(color, 1.0);
}
```

**出力アルファは 1**（**背景を、自分で混ぜている**ため）。<strong>ブレンドは、不要（上書き）</strong>です。

## 屈折のコストと限界
| 項目 | 内容 |
| --- | --- |
| **背景のコピー** | **フル解像度の HDR カラー 1 枚**（**帯域**） |
| **半透明の重なり** | **コピーは不透明のみ**。**重なるガラスは、別途** |
| **画面空間の限界** | **画面外・裏側の物は、屈折で写らない** |
| **レイトレの屈折** | **正確**（画面外・多重屈折も OK）。**HW RT が必要**（[RT 反射](../../reflections/rt-reflections/index.md)） |

## よくあるミス

??? failure "屈折物体の重なりが、正しく表示されない"
    **重なりは、1 層だけ屈折**とし、**OIT** などで補う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **不透明 → コピー → 屈折の順**
    - [x] **重なりと画面外が限界**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [屈折](index.md)
- [画面空間の屈折](screen-space.md)
- [OIT](../oit/index.md)
