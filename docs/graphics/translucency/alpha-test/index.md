---
title: Alpha Testing
tags:
  - 描画
---

# Alpha Testing

<strong>アルファ テストはアルファ値がしきい値より小さい画素を捨てる（clip する）手法</strong>で、葉・フェンス・髪など「ある・ない」の透明に使います。混ぜないのでソートが不要ですが、縁がギザギザになるのが欠点です。このセクションでは clip の基本・Alpha to Coverage・ハッシュド アルファ・ディザ・パフォーマンス・方式の比較を 1 つずつ別のページで説明します。

## clip による基本のアルファ テスト
<strong>ピクセル シェーダーでアルファが閾値未満ならその画素を捨てます</strong>。

```hlsl
float4 PSMain(VsOutput input) : SV_Target {
  float4 color = albedo_texture.Sample(linear_sampler, input.uv);
  clip(color.a - 0.5);
  return color;
}
```

| 点 | 説明 |
| --- | --- |
| `clip(x)` | `x < 0` ならその画素を捨てる（`discard` と同じ） |
| `color.a - 0.5` | アルファが 0.5 未満なら捨てる |
| 閾値 0.5 | 標準。調整可能（マテリアルごとに） |
| ブレンドなし | 通常の不透明描画として、色を書く。深度も書く |

不透明と同じパスで描け ソート不要です。葉・草・金網はこれで十分なことが多いです。

## アルファ テストの欠点
### 縁がギザギザ

<strong>アルファの境目を 0 か 1 で切る</strong>ので、縁が階段状になります（エイリアシング）。MSAA でも `clip` の結果は画素単位なので、滑らかになりません。

### ミップで遠くの葉が薄くなる

葉のテクスチャをミップ マップで縮小すると、アルファ チャンネルも平均されて遠くで、アルファが全体に低くなります。閾値 0.5 を超える画素が減り遠くの木がスカスカに見えます。

葉のテクスチャをミップで縮小すると、アルファ チャンネルも平均されます。近いときはミップ 0 で葉の形が正しく見えます。遠いときは高いミップでアルファが平均されて、0.5 未満の画素が多くなり葉が消えます。

### 対策：ミップの面積を保つ（カバレッジ保存）

ミップごとにアルファの閾値を超える画素の割合（カバレッジ）が元と同じになるよう アルファを調整します。

```hlsl
float alpha = albedo_texture.Sample(linear_sampler, input.uv).a;
float mip = albedo_texture.CalculateLevelOfDetail(linear_sampler, input.uv);
alpha *= 1.0 + mip * kMipScale;
clip(alpha - 0.5);
```

ミップの罠への対策は 3 つです。ミップ レベルに応じてアルファを大きくする、ミップごとのスケール（簡易）。ミップ チェーンを作るときに各レベルのアルファの閾値を調整して、カバレッジを一定に保つ方法（ツール側）。遠くでは閾値を下げる距離でアルファを調整する方法です。

ミップ生成の段階でカバレッジを保存するのが、正確です（テクスチャ ツールのオプション）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Alpha to Coverage](alpha-to-coverage.md) | MSAA を使って、縁をなめらかに |
| [Hashed Alpha](hashed-alpha.md) | 確率的に捨てて、TAA でなめらかに |
| [Dithered Transparency](dither.md) | 距離・近さで、点々にして消す |
| [Performance and Shadow Passes](performance.md) | Early-Z が効かない問題・影のパス |
| [Method Comparison](comparison.md) | どれを選ぶか |

## これだけ覚える

!!! abstract "まとめ"
    - [x] clip で捨てる。混ぜないのでソート不要
    - [x] 縁は A2C・ハッシュドで改善

## 参考

- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Castaño, "Computing Alpha Mipmaps", 2010（ミップごとに、アルファを補正してカバレッジを保つ）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明と、アルファ合成の章）
- Microsoft Learn, "D3D11_BLEND_DESC"（`AlphaToCoverageEnable`、`D3D11_RENDER_TARGET_BLEND_DESC`）

## 関連ページ

- [Translucency](../index.md)
- [Alpha Blending and Sorting](../blending-sorting/index.md)
- [OIT](../oit/index.md)
