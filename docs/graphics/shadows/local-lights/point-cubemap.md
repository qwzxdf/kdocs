---
title: 点光源：キューブ マップ
tags:
  - 描画
---

# 点光源：キューブ マップ

**点光源は、全方向を照らす**ので、**影を作るには、全方向の深度が必要**です。**キューブ マップ（6 面）に、各方向の深度を描く**のが**標準**で、**サンプルは、ライトから画面の点への方向ベクトルで引く**ので**簡単**です。**ただし、6 回描くので、コストが 6 倍**です。このページでは、**キューブ マップの作り方・方向ベクトルでのサンプル・線形距離の保存・面の境界と PCF**を説明します。

!!! tip "ポイント"
    - **点光源の影 ＝ 6 面のキューブ マップ**（**各面 90° の透視投影**）。
    - **サンプルは、方向ベクトルで引く**（**面を意識しなくてよい**）。
    - **保存は、非線形深度より、ライトからの距離（線形）**が**扱いやすい**。
    - **面の境界で、PCF のサンプルが隣の面に跨ぐ**ので**注意**。

## 点光源：キューブ マップ
**点光源**は**あらゆる方向**に光を出します。**6 方向（±X, ±Y, ±Z）に、視野角 90 度の透視投影**で描けば、**全方向を覆えます**（**キューブ シャドウ マップ**）。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="キューブ シャドウ マップ">
<text x="20" y="24" class="fig-title">点光源から 6 方向へ、視野角 90 度で描く（真上から見た図）</text>
<circle cx="200" cy="140" r="9" fill="rgba(229,170,40,0.9)" stroke="currentColor" stroke-width="2"/><text x="214" y="132" style="font-size:12px">光源</text>
<line x1="200" y1="140" x2="320" y2="40" stroke="currentColor" stroke-dasharray="4 3"/><line x1="200" y1="140" x2="320" y2="240" stroke="currentColor" stroke-dasharray="4 3"/>
<line x1="200" y1="140" x2="80" y2="40" stroke="currentColor" stroke-dasharray="4 3"/><line x1="200" y1="140" x2="80" y2="240" stroke="currentColor" stroke-dasharray="4 3"/>
<text x="326" y="146" style="font-size:12px">+X 面</text><text x="30" y="146" style="font-size:12px">−X 面</text><text x="170" y="40" style="font-size:12px">+Z 面</text><text x="170" y="254" style="font-size:12px">−Z 面</text>
<text x="420" y="90" style="font-size:13px">各面：視野角 90°、アスペクト 1</text>
<text x="420" y="116" style="font-size:13px">±Y 面（上下）も同様に描く（図は省略）</text>
<text x="420" y="152" style="font-size:13px">画素 → ライトからのベクトル v の</text>
<text x="420" y="172" style="font-size:13px">絶対値が最大の成分で、使う面が決まる</text>
</svg>

| 方式 | 内容 |
| --- | --- |
| **6 枚のレンダー ターゲット** | `Texture2DArray` の 6 スライス（または `TextureCube`）に、**6 回**描く |
| **ジオメトリ シェーダーで 1 回** | **`SV_RenderTargetArrayIndex`** で、**1 回の描画で 6 面**へ（環境による。効率は微妙） |
| **ビュー インスタンシング** | 対応環境で、**1 回のドロー**で複数面 |

### サンプル：方向ベクトルで引く

**キューブ マップ**は、**ライトから画素へのベクトル**で、**サンプル**できます。**比較には保存された深度**と<strong>そのベクトルの長さ（または面ごとの深度）</strong>を使います。

```hlsl
float PointShadow(float3 world_pos) {
  float3 v = world_pos - light_position;
  float3 a = abs(v);
  float major = max(a.x, max(a.y, a.z));
  float depth = (light_far * (major - light_near)) / (major * (light_far - light_near));
  return shadow_cube.SampleCmpLevelZero(shadow_sampler, v, depth - bias);
}
```

| 点 | 説明 |
| --- | --- |
| **`major`** | **絶対値が最大の成分**＝**その面の、ビュー空間の z** |
| **`depth`** | **透視投影の深度の式**で**射影後の深度**（0〜1）に変換（左手系の `XMMatrixPerspectiveFovLH` と同じ） |
| **`shadow_cube`** | `TextureCube`（比較サンプラー）。**面の境界もハードウェアが補間** |

### 線形な距離を保存する方法

**射影後の深度**でなく、**ライトからの線形距離**（`length(v) / light_far`）を、**ピクセル シェーダーで書く**方式もあります。**比較は単純**ですが**ハードウェアの深度テスト・Early-Z を使えない**（深度を自分で書く）ので**描画が遅く**なります。**射影後の深度**が一般的です。

### 面の境界と PCF

**面の境界をまたぐ PCF**は、**隣の面のテクセル**を参照する必要があります。**キューブ マップのハードウェア サンプラー**は、**面をまたぐ補間**を**正しく**処理します。**自前で面ごとの 2D テクスチャ配列**を使うと、**境界で PCF が途切れる**ので、**注意**が必要です。

## よくあるミス

??? failure "キューブ マップの面の継ぎ目に線が出る"
    **PCF のサンプルが面を跨ぐ**ので、**方向ベクトルでサンプル**し、**境界の処理**をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **点光源の影 ＝ 6 面のキューブ マップ**
    - [x] **方向ベクトルで引く**。**コストは 6 倍**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [点光源・スポットライトの影](index.md)
- [スポットライト](spot-light.md)
- [デュアル パラボロイド](dual-paraboloid.md)
