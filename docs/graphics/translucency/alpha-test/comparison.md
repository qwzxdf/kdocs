---
title: Method Comparison
tags:
  - 描画
---

# Method Comparison

<strong>アルファ テスト系の方式は縁の品質・コスト・必要な条件が違います</strong>。このページでは <strong>方式の比較と選び方</strong>を説明します。

!!! tip "ポイント"
    - clip のみ：最も軽いが、縁がギザギザ。
    - A2C：MSAA が必要。縁がなめらか。
    - ハッシュド：TAA が必要。遠くでも安定。
    - ディザ：フェード アウト向き。

!!! info "このページを読む前に"
    - [Alpha Testing](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 方式の比較
| 方式 | 縁 | 順序 | 深度 | コスト | 用途 |
| --- | --- | --- | --- | --- | --- |
| <strong>clip（アルファ テスト）</strong> | ギザギザ | 不要 | 書ける | 低〜中 | 草・葉・金網 |
| Alpha to Coverage | 滑らか（MSAA） | 不要 | 書ける | MSAA のコスト | 草・葉（MSAA 使用時） |
| ハッシュド アルファ | 滑らか（TAA） | 不要 | 書ける | 低 | 草・葉・髪（TAA 使用時） |
| ディザ透明 | 網目状 | 不要 | 書ける | 低 | カメラ前の遮蔽物を透かす |
| ブレンド | 滑らか | 必要 | 書かない | 中〜大 | ガラス・煙 |

## 5 つの方式を並べて比べる

| 観点 | アルファ テスト | Alpha to Coverage | ディザ | ハッシュ アルファ | アルファ ブレンド |
| --- | --- | --- | --- | --- | --- |
| 縁 | ジャギー | なめらか | 粒状 | なめらか（TAA で） | なめらか |
| 半透明 | 0 か 1 | 段階的（MSAA の段階） | 確率的 | 確率的 | 連続 |
| 深度の書き込み | 可能 | 可能 | 可能 | 可能 | 不可（普通は） |
| ソート | 不要 | 不要 | 不要 | 不要 | 必要 |
| 前提 | なし | MSAA | なし | TAA（推奨） | なし |
| ノイズ | なし | なし | あり | あり | なし |
| コスト | Early-Z が、効かない | 同左 + MSAA | 同左 | 同左 | ブレンドの帯域 |
| 向く対象 | 柵、金網 | 葉、草（フォワード） | フェード、LOD | 葉、髪（TAA あり） | ガラス、煙、水 |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| まず、動かしたい | アルファ テスト |
| フォワード + MSAA の植生 | Alpha to Coverage |
| ディファード + TAA の植生 | ハッシュ アルファ（または、IGN / ブルー ノイズのディザ） |
| LOD の切り替え近接フェード | ディザ（ブルー ノイズ） |
| 本当の半透明（ガラス、煙） | アルファ ブレンド（[Alpha Blending and Sorting](../blending-sorting/index.md)）、OIT |

## 組み合わせる

1 つだけでなく <strong>組み合わせる</strong>のが、普通です。

| 組み合わせ | 内容 |
| --- | --- |
| A2C + アルファのシャープ化 | 縁を 1 画素幅に保つ（[Alpha to Coverage](alpha-to-coverage.md)） |
| ハッシュ アルファ + TAA | ノイズを時間方向に平均して、なめらかに |
| ディザ + LOD | 2 つの LOD を補い合うパターンで、切り替える |
| Z プリパス + 上のどれか | 隠れた画素の重いシェーダーを省く（[Performance and Shadow Passes](performance.md)） |

## よくあるミス

??? failure "MSAA も TAA も無いのに、A2C やハッシュドを選ぶ"
    <strong>アンチエイリアスの方式に合わせて選ぶ</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] AA の方式に合わせて選ぶ

## 参考

- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Castaño, "Computing Alpha Mipmaps", 2010（ミップごとに、アルファを補正してカバレッジを保つ）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014, Advances in Real-Time Rendering in Games（Interleaved Gradient Noise）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明と、アルファ合成の章）

## 関連ページ

- [Alpha Testing](index.md)
- [Anti-Aliasing](../../postprocess/antialiasing/index.md)
