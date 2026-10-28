---
title: Point and Spot Light Shadows
tags:
  - 描画
---

# Point and Spot Light Shadows

<strong>太陽のような平行光は 1 枚のシャドウ マップ（またはカスケード）で足ります</strong>が、<strong>点光源やスポットライトは数が多く、影の向きも多様</strong>です。ライトごとにシャドウ マップを作ると、数が増えるほど描画が重くなります。このセクションではスポットライトの影・点光源のキューブ マップ・デュアル パラボロイド・多数のライトの管理とキャッシュを 1 つずつ別のページで説明します。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Spot Lights](spot-light.md) | 透視投影 1 枚で、円錐の影 |
| [Point Lights: Cube Maps](point-cubemap.md) | 6 方向のマップ・サンプル・面の境 |
| [Dual Paraboloid](dual-paraboloid.md) | 2 枚で全方向を覆う方法 |
| [Shadows for Many Lights](many-lights.md) | アトラス・解像度の割り当て・キャッシュ・バイアス |

## 点光源・スポットライトの影の特徴

<strong>太陽</strong>は <strong>平行光源</strong>で 1 枚の、正射影シャドウ マップで足ります。点光源（電球、たいまつ）とスポットライト（懐中電灯、街灯）は位置を持ち光が広がります。そのため、影の作り方が違います。

| 光 | 光の広がり | シャドウ マップ | ページ |
| --- | --- | --- | --- |
| スポットライト | 円錐（片側に向かう） | 透視投影の 1 枚 | [Spot Lights](spot-light.md) |
| 点光源 | 全方向（球） | キューブマップ（6 枚）、または放物面マップ（2 枚） | [Point Lights: Cube Maps](point-cubemap.md)、[Dual Paraboloid](dual-paraboloid.md) |
| 多数の光 | — | コスト管理が必須 | [Shadows for Many Lights](many-lights.md) |

## 光の数とコスト

影を落とす光が 1 つ増えるごとに、<strong>シーンをもう一度、描く</strong>必要があります。

| 光 | シャドウ パスの、描画回数 |
| --- | --- |
| 太陽（CSM、4 カスケード） | 4（カスケードごと） |
| スポットライト 1 つ | 1 |
| 点光源 1 つ（キューブマップ） | 6（各面） |
| 点光源 1 つ（放物面） | 2 |

<strong>点光源 10 個</strong>（キューブマップ）で、<strong>60 回</strong>のシーンの描画になります。影を落とす光の数を制限し範囲外の光の影は省き更新を間引く、といった管理が不可欠です（[Shadows for Many Lights](many-lights.md)）。

## 実装の共通点

| 項目 | 内容 |
| --- | --- |
| 射影 | 透視投影（深度が非線形）。バイアスは距離で変わる |
| 光の範囲 | 光の到達距離（range）。ファー面 = range。範囲外は描かない |
| 深度の形式 | 距離（光からの、実際の距離）を保存する方法もある（透視投影の、非線形性を避ける） |
| カリング | 光の範囲球と物の、バウンディングで範囲外の物をシャドウ パスから外す |

### 距離を保存する

<strong>透視投影</strong>の深度は <strong>非線形</strong>で、バイアスが距離で変わり扱いにくいです。光からの実際の距離をピクセル シェーダーで、計算して保存する方法です。

```hlsl
// 点光源のシャドウ パス: 光からの距離（0〜1 に、正規化）を書き出す。
float main(PSInput input) : SV_Target {
  float dist = length(input.world_position - g_light_position);
  return dist / g_light_range;                    // 0〜1
}

// メイン パス: 同じ式で、画素の距離を求めて、保存された距離と、比べる。
float3 to_pixel = world_pos - g_light_position;
float dist = length(to_pixel) / g_light_range;
float stored = g_shadow_cube.SampleLevel(g_linear_clamp, to_pixel, 0);      // 方向ベクトルで、キューブを読む
float lit = (dist - kBias <= stored) ? 1.0 : 0.0;
```

距離を保存すると <strong>バイアスが距離に依存せず線形</strong>になり <strong>扱いやすい</strong>。ただし、ピクセル シェーダーが必要で、ハードウェアの深度比較（比較サンプラー、PCF）が使えません。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ローカル ライトは、スポット ＝ 1 枚、点 ＝ 6 枚
    - [x] 多数のライトは、管理とキャッシュが鍵

## 参考

- Brabec, Annen, Seidel, "Shadow Mapping for Hemispherical and Omnidirectional Light Sources", Advances in Modelling, Animation and Rendering (Computer Graphics International 2002)（放物面マッピング）
- Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading", High-Performance Graphics 2012
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"

## 関連ページ

- [Shadows](../index.md)
- [Cascaded Shadow Maps (CSM)](../cascaded.md)
- [Tiled と Clustered](../../../rendering/light-culling.md)
