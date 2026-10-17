---
title: ベイクの流れ
tags:
  - 描画
---

# ベイクの流れ

**ベイクは、シーンの静的な光を、事前に計算して、テクスチャへ書き出す作業**です。**時間がかかるので、設定を段階的に上げながら、確認します**。**法線マップと併用するための「方向情報」も、一緒にベイク**できます。このページでは、**ベイクの流れと、方向情報**を説明します。

!!! tip "ポイント"
    - **手順：UV2 を用意 → 静的なオブジェクトを指定 → ベイク → 確認 → 調整**。
    - **最初は低品質で、全体を確認してから、品質を上げる**。
    - **方向情報を一緒に焼くと、法線マップの凹凸が反映**される。
    - **ベイクは時間がかかる**ので、**自動化・並列化**する。

## ベイクの流れ
| 手順 | 内容 |
| --- | --- |
| **① UV2 の生成・パッキング** | 全メッシュの UV2 を、**ライトマップ アトラス**に配置 |
| **② ベイク** | **各テクセルのワールド位置・法線**から、**パス トレース**で放射照度を計算 |
| **③ デノイズ** | **少ないサンプルで速く**計算し、**デノイザ**でノイズを除去 |
| **④ 圧縮・出力** | <strong>BC6H（HDR）</strong>などに**圧縮** |
| **⑤ 実行時に読み込む** | **シーンと一緒にライトマップ**をストリーミング |

**ベイクには数分〜数時間**かかります。**GPU ベイク**（GPU レイトレース）で、**大幅に短縮**できます。

## 方向情報（法線マップとの併用）
<strong>通常のライトマップは、「その点に届く光の総量（スカラー）」</strong>しか持ちません。**法線マップで細かい凹凸を付けてもライトマップの明るさは、法線に応じて変わらない**ので、**平坦に見えます**。

| 方式 | 内容 |
| --- | --- |
| **スカラーのみ** | **放射照度のみ**。**法線マップが効かない** |
| **Directional ライトマップ** | **主な光の方向**を**もう 1 枚のテクスチャ**に保存。**方向と法線**から、**明るさを補正** |
| **SH ライトマップ** | <strong>L1 SH（4 係数）</strong>を保存。**法線**で、**SH を評価** |
| <strong>Radiosity Normal Mapping（Half-Life 2）</strong> | **3 つの基底方向**（正三角形に配した 3 方向）の、**それぞれの放射照度**を保存し、**法線マップの法線**で**3 方向を補間** |

```hlsl
float3 basis0 = lightmap0.Sample(linear_sampler, uv).rgb;
float3 basis1 = lightmap1.Sample(linear_sampler, uv).rgb;
float3 basis2 = lightmap2.Sample(linear_sampler, uv).rgb;
float3 w = saturate(float3(dot(n_ts, kBasis0), dot(n_ts, kBasis1), dot(n_ts, kBasis2)));
w *= w;
w /= (w.x + w.y + w.z);
float3 irradiance = basis0 * w.x + basis1 * w.y + basis2 * w.z;
```

**方向情報**を持つことで**法線マップの凹凸に応じた、陰影**が**間接光にも**加わります。**テクスチャが 3 枚**に増える（**メモリ**）のが代償です。

## よくあるミス

??? failure "ライトマップが、法線マップの凹凸と合わず、平らに見える"
    **方向情報も一緒にベイク**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **低品質で確認 → 高品質でベイク**
    - [x] **方向情報で、法線マップと併用**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [ライトマップ](index.md)
- [ライトマップ UV](uv2.md)
- [鏡面と動く物体](dynamic-objects.md)
