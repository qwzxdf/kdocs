---
title: Alpha Testing
tags:
  - 描画
---

# Alpha Testing

**アルファ テストは、アルファ値がしきい値より小さい画素を、捨てる（clip する）手法**で、**葉・フェンス・髪など、「ある・ない」の透明**に使います。**混ぜないので、ソートが不要**ですが、**縁がギザギザになる**のが**欠点**です。このセクションでは、**clip の基本・Alpha to Coverage・ハッシュド アルファ・ディザ・パフォーマンス・方式の比較**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **clip(α − しきい値)** で、**画素を捨てる**。
    - **ソート不要・深度も書ける**のが**利点**。
    - **縁がギザギザ**・**遠くで細る**のが**欠点**。
    - **改善手法：Alpha to Coverage・ハッシュド アルファ**。

## clip による基本のアルファ テスト
**ピクセル シェーダーで、アルファが閾値未満なら、その画素を捨てます**。

```hlsl
float4 PSMain(VsOutput input) : SV_Target {
  float4 color = albedo_texture.Sample(linear_sampler, input.uv);
  clip(color.a - 0.5);
  return color;
}
```

| 点 | 説明 |
| --- | --- |
| **`clip(x)`** | **`x < 0` なら、その画素を捨てる**（`discard` と同じ） |
| **`color.a - 0.5`** | **アルファが 0.5 未満なら、捨てる** |
| **閾値 0.5** | **標準**。**調整可能**（マテリアルごとに） |
| **ブレンドなし** | **通常の不透明描画**として、**色を書く**。**深度も書く** |

**不透明と同じパス**で描け、**ソート不要**です。**葉・草・金網**は、**これで十分**なことが多いです。

## アルファ テストの欠点
### 縁がギザギザ

**アルファの境目を、0 か 1 で切る**ので、**縁が階段状**になります（**エイリアシング**）。**MSAA でも、`clip` の結果は、画素単位**なので、**滑らかになりません**。

### ミップで遠くの葉が薄くなる

**葉のテクスチャを、ミップ マップで縮小**すると、**アルファ チャンネルも平均**されて、**遠くで、アルファが全体に低くなります**。**閾値 0.5 を超える画素が減り、遠くの木が、スカスカ**に見えます。

| 距離 | ミップ | 見た目 |
| --- | --- | --- |
| **近い** | **ミップ 0** | **葉の形が、正しい** |
| **遠い** | **高いミップ** | **アルファが平均されて、0.5 未満の画素が多くなり、葉が消える** |

### 対策：ミップの面積を保つ（カバレッジ保存）

**ミップごとに、アルファの閾値を超える画素の割合（カバレッジ）が、元と同じになる**よう、**アルファを調整**します。

```hlsl
float alpha = albedo_texture.Sample(linear_sampler, input.uv).a;
float mip = albedo_texture.CalculateLevelOfDetail(linear_sampler, input.uv);
alpha *= 1.0 + mip * kMipScale;
clip(alpha - 0.5);
```

| 方法 | 内容 |
| --- | --- |
| **ミップごとのスケール** | **ミップ レベルに応じて、アルファを大きく**する（簡易） |
| **ミップ生成時にカバレッジ保存** | **ミップ チェーンを作るとき、各レベルのアルファの閾値を調整**して、**カバレッジを一定に保つ**（ツール側） |
| **距離でアルファを下げる閾値** | **遠くでは、閾値を下げる** |

**ミップ生成の段階**で**カバレッジを保存**するのが、**正確**です（**テクスチャ ツールのオプション**）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Alpha to Coverage](alpha-to-coverage.md) | MSAA を使って、縁をなめらかに |
| [Hashed Alpha](hashed-alpha.md) | 確率的に捨てて、TAA でなめらかに |
| [Dithered Transparency](dither.md) | 距離・近さで、点々にして消す |
| [パフォーマンス](performance.md) | Early-Z が効かない問題・影のパス |
| [Method Comparison](comparison.md) | どれを選ぶか |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **clip で捨てる。混ぜないのでソート不要**
    - [x] **縁は、A2C・ハッシュドで改善**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Translucency](../index.md)
- [アルファ ブレンド](../blending-sorting/index.md)
- [OIT](../oit/index.md)
