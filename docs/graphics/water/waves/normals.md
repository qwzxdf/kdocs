---
title: 法線の計算
tags:
  - 描画
---

# 法線の計算

**波の見た目は、法線で決まります**。**頂点の位置を動かしても、法線を更新しないと、光の当たり方が変わらず、のっぺりします**。**解析的に（式を微分して）法線を求める**方法と、**法線マップを重ねて細かい凹凸を足す**方法があります。このページでは、**法線の求め方**を説明します。

!!! tip "ポイント"
    - **法線 ＝ 高さ関数の傾きから求める**。
    - **解析的な微分は、速く、正確**。
    - **法線マップを 2 枚、逆向きに流して重ねる**と、**細かい波が出る**。
    - **遠くは、法線マップの効果を弱める**（ちらつき防止）。

## 法線の計算
**波の法線**は**頂点位置の偏微分**から**求められます**。**Gerstner 波は、解析的な式**があります。

```hlsl
float3 GerstnerNormal(float2 position, GerstnerWave wave, float time) {
  float k = 2.0 * 3.14159265 / wave.wavelength;
  float phase = k * dot(wave.direction, position) + time * wave.speed * k;
  float wa = k * wave.amplitude;
  float c = cos(phase);
  float s = sin(phase);
  return float3(-wave.direction.x * wa * c,
                1.0 - wave.steepness * wa * s,
                -wave.direction.y * wa * c);
}

float3 normal = float3(0, 1, 0);
for (int i = 0; i < kWaveCount; ++i) {
  float3 n = GerstnerNormal(position, waves[i], time);
  normal += float3(n.x, n.y - 1.0, n.z);
}
normal = normalize(normal);
```

| 点 | 説明 |
| --- | --- |
| **解析的な法線** | **頂点を動かした後の正しい法線**。**メッシュの三角形から再計算しない** |
| **ピクセル シェーダーで計算** | **頂点の法線を補間**するより、**ピクセル ごとに計算**すると**滑らか**（**頂点が粗くても波の凹凸が出る**） |
| **`y` 成分** | **水平を向く基準が `1`**。**各波で、1 からのずれを足す** |

**数値微分**（隣の点との高さの差）でも**法線は求められます**が、**解析式のほうが安く正確**です。

## 細かい凹凸：法線マップの重ね
**メッシュの頂点密度は限られる**ので、<strong>細かい波（さざ波）</strong>は、**法線マップ**で**表現**します。**2 枚以上の法線マップを、違う向き・速さで流して重ねる**と**周期性が目立たず、動きが生まれます**。

```hlsl
float2 uv1 = world_position.xz * 0.05 + time * float2(0.03, 0.01);
float2 uv2 = world_position.xz * 0.11 - time * float2(0.02, 0.04);
float3 n1 = normal_map.Sample(linear_wrap, uv1).xyz * 2.0 - 1.0;
float3 n2 = normal_map.Sample(linear_wrap, uv2).xyz * 2.0 - 1.0;
float3 detail = normalize(float3(n1.xy + n2.xy, n1.z * n2.z));
float3 final_normal = normalize(float3(wave_normal.xz + detail.xy * detail_strength, wave_normal.y).xzy);
```

| 点 | 説明 |
| --- | --- |
| **UV の拡大率を変える** | **大きさの違う 2 層**（**スケールが異なる**ので**繰り返しが見えない**） |
| **逆向きに流す** | **互いに違う方向へ動く**ので、**波が複雑に見える** |
| **法線の合成** | **XY を足し、Z は掛ける**（**Whiteout・Reoriented Normal Mapping** などの正確な合成法もある） |
| **ワールド座標の UV** | **カメラが動いても波が水面に貼りつく** |

## よくあるミス

??? failure "水面がのっぺりして、波が見えない"
    **法線を、波の式から計算し直す**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **法線は、微分で求める**
    - [x] **法線マップを重ねて、細部を足す**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水面の波](index.md)
- [Gerstner 波](gerstner.md)
- [水の質感](../shading/index.md)
