---
title: Probe GI
tags:
  - 描画
---

# Probe GI

**プローブ GI は、空間のあちこちに「プローブ」を置き、そこでの間接光を保存しておいて、物体のシェーディング時に補間して使う手法**です。**動く物体にも使え、軽い**のが**利点**です。このセクションでは、**原理・補間・SH の持ち方・置き方・動的更新・反射プローブとの違い**を、**1 つずつ別のページ**で説明します。

## Principle {#原理}
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

### History and Actual Practice {#歴史と実際の姿}

「空間の点に間接光を保存し、補間して使う」という発想は、Greger らの<strong>Irradiance Volume</strong>（1998）に遡ります。ゲームでの広い採用は、Valve の Source エンジンが使った<strong>アンビエント キューブ</strong>（6 方向の色で拡散光を表す方式）や、Sloan らの SH を使った Precomputed Radiance Transfer（2002）の流れから来ています。いまの Unity のライト プローブや、Unreal Engine の Volumetric Lightmap は、この系統です。

プローブの利点を一言で言えば、<strong>ライトマップの届かない部分を、小さなコストで埋められること</strong>です。ライトマップはメッシュの表面にしか貼れないので、キャラクターや乗り物のような動く物体には使えません。プローブなら、動く物体がどこにいても、その位置の周りの 8 個（あるいは四面体の 4 個）のプローブから間接光を補間できます。木の葉や草のように、ライトマップを作りにくい小さな物体にも、プローブはよく使われます。

代償は、<strong>低周波しか持てない</strong>ことです。プローブ 1 個が表すのは、その点の周りの滑らかな明るさだけです。床と壁の接触部分の細かい暗さ（接触影）は、プローブには入りません。これは AO や[コンタクト シャドウ](../../shadows/contact-shadows.md)で補います。

## Page List {#ページ一覧}

| ページ | 内容 |
| --- | --- |
| [Interpolation Methods](interpolation.md) | 周囲のプローブから、値を求める |
| [Storing SH](sh-storage.md) | 係数の保存形式 |
| [置き方](placement.md) | どこに、どの密度で置くか |
| [Dynamic Updates](dynamic-update.md) | 光や物の変化への追従 |
| [Comparison with Reflection Probes and Cost](compare.md) | 用途の違い・長所短所 |

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **プローブに間接光を保存し、補間して使う**
    - [x] **動く物体にも使える**

## References {#参考}

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## Related Pages {#関連ページ}

- [GI](../index.md)
- [DDGI](../ddgi.md)
- [Lightmaps](../lightmaps/index.md)
