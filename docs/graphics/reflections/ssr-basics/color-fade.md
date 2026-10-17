---
title: Color Lookup and Fading
tags:
  - 描画
---

# Color Lookup and Fading

**当たりが見つかったら、その画素の「前フレームまたは現フレームの色」を持ってきます**。**ただし、画面の端や、カメラに向かう反射は、信頼できないので、フェード（徐々に弱める）が必要**です。このページでは、**どの色を使うか・フェードの掛け方**を説明します。

!!! tip "ポイント"
    - **当たった画素の色**を、**反射色**として使う。
    - **前フレームの色を使うと、反射の中の反射も映る**（ただし、ずれに注意）。
    - **画面の端・カメラ向きの反射・粗い面は、フェードで弱める**。
    - **信頼度 ＝ 端からの距離 × 向き × 距離 × 粗さ**を**掛け合わせる**。
    - **フェードした分は、フォールバックで補う**。

## 色の取得
**当たった画素の色**を反射として使います。**どの画像から取るか**が重要です。

| 取得元 | 利点 | 欠点 |
| --- | --- | --- |
| **今のフレームの、SSR を除いたシーン色** | 最新 | **SSR を適用する前の画像**が必要（**反射のパスの前**の色を残す） |
| **前フレームの最終画像** | 手軽（すでに反射・ポストが乗っている） | **1 フレーム遅れる**（動く物にずれ）。**反射の反射**が入る（二重） |
| **前フレームを動きベクトルで再投影** | 遅れの補正 | 動きベクトルが必要 |

**多くの実装は前フレームの最終画像**（**ブルーム前**の HDR）を使い、**動きベクトルで再投影**します。

## フェード：信頼できない反射を弱める
SSR は**画面にあるものしか映せません**。**信頼できない反射**は、**フェード**して、**フォールバック**（[フォールバック](../ssr-fallback.md)）に任せます。

| 要因 | 内容 |
| --- | --- |
| **画面端** | 当たりが**画面の端に近い**ほど、弱める（`edge_fade = saturate((0.5 − |uv − 0.5|) / margin)`） |
| **レイの長さ** | 遠いほど、弱める（遠くの当たりは不確か） |
| **粗さ** | 粗いほど、弱める（SSR はくっきりした反射が得意） |
| **向き** | **反射がカメラの方へ戻る**（`R·V` が負で大きい）場合は**画面に映っていない面**を指す。弱める |
| **厚みの検証** | 当たった場所の**深度差**が、不自然なら、弱める |
| **当たらなかった** | 信頼度 0（フォールバックのみ） |

```hlsl
float SSRConfidence(float2 hit_uv, float ray_length, float roughness, float3 R_vs) {
  float2 d = abs(hit_uv - 0.5) * 2.0;
  float edge = 1.0 - smoothstep(0.8, 1.0, max(d.x, d.y));
  float distance_fade = 1.0 - saturate(ray_length / max_distance);
  float rough_fade = 1.0 - saturate(roughness / max_roughness);
  float facing = saturate(1.0 + R_vs.z * 4.0);
  return edge * distance_fade * rough_fade * facing;
}
```

## よくあるミス

??? failure "画面の端で、反射が急に消える"
    **端からの距離で、フェード**を掛ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **当たった画素の色を持ってくる**
    - [x] **信頼できない所は、フェードで弱める**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [SSR Basics](index.md)
- [フォールバック](../ssr-fallback.md)
- [Cost and Roughness](cost-roughness.md)
