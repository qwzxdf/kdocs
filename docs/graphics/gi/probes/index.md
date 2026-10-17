---
title: Probe GI
tags:
  - 描画
---

# Probe GI

**プローブ GI は、空間のあちこちに「プローブ」を置き、そこでの間接光を保存しておいて、物体のシェーディング時に補間して使う手法**です。**動く物体にも使え、軽い**のが**利点**です。このセクションでは、**原理・補間・SH の持ち方・置き方・動的更新・反射プローブとの違い**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **空間にプローブを置き、間接光（SH）を保存**。
    - **周囲の 8 つのプローブから、補間**して使う。
    - **動く物体にも使える**。
    - **反射プローブとは別物**（拡散用）。

## 原理
**プローブの位置 `p_i`** で、**全方向の入射光**を**キャプチャ**（ベイク・または動的に計算）し、<strong>放射照度 E_i(n)</strong>を**SH に投影**して、**係数**として**保存**します。

| 手順 | 内容 |
| --- | --- |
| **① 配置** | **シーンの空間にプローブを置く**（手動・自動・格子） |
| <strong>② 計算（ベイク）</strong> | **各プローブ**で**全方向のレイ**（またはキューブマップのレンダリング）から、**放射照度を SH に** |
| **③ 実行時の補間** | **物体の位置**に応じ、**近くのプローブの SH を、重み付けして補間** |
| **④ 評価** | **補間した SH を物体の法線で評価**して、**間接拡散光** |

```hlsl
float3 sh[9] = InterpolateProbes(world_pos);
float3 irradiance = EvaluateSH9(world_normal, sh);
float3 indirect_diffuse = albedo * irradiance;
```

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Interpolation Methods](interpolation.md) | 周囲のプローブから、値を求める |
| [Storing SH](sh-storage.md) | 係数の保存形式 |
| [置き方](placement.md) | どこに、どの密度で置くか |
| [Dynamic Updates](dynamic-update.md) | 光や物の変化への追従 |
| [Comparison with Reflection Probes and Cost](compare.md) | 用途の違い・長所短所 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **プローブに間接光を保存し、補間して使う**
    - [x] **動く物体にも使える**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [GI](../index.md)
- [DDGI](../ddgi.md)
- [Lightmaps](../lightmaps/index.md)
