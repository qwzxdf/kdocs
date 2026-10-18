---
title: Cost and Roughness
tags:
  - 描画
---

# Cost and Roughness

<strong>SSR は、レイを画素ごとに進めるので、解像度で、コストが大きく変わります</strong>。<strong>半解像度でトレースして、フル解像度に戻す</strong>のが一般的です。粗い面の反射は、本来、ぼやけますが、簡易的に、ぼかしで近似できます。このページでは、解像度とコストの関係・粗さの簡易対応を説明します。

!!! tip "ポイント"
    - コストは、画素数 × ステップ数。
    - 半解像度でトレースすると、およそ 1/4。
    - 粗い面は、反射もぼやける。簡易には、結果をぼかす（ミップを選ぶ）。
    - 本格的な粗さは、[Stochastic SSR](../ssr-stochastic.md)で扱う。

## 解像度とコスト
| 方式 | 内容 |
| --- | --- |
| フル解像度 | 高品質。重い |
| 半分の解像度 | レイを半分の解像度で飛ばし、拡大（バイラテラル）。4 分の 1 のコスト |
| ステップ数の上限 | 32〜64 程度。1 ステップが深度のテクスチャ読み込み 1 回 |
| 歩幅 stride | 大きいと速い（薄い物を飛ぶ）。ジッターで縞を分散 |
| 粗い面はレイを減らす | 粗さがしきい値以上の画素は、SSR をやめる（プローブへ） |
| マスク | 反射しない面（粗さ 1・非金属で粗い）を、ステンシルやタイル分類で除外 |

## 粗さへの簡易対応
<strong>粗い面</strong>の反射は、<strong>ぼやけるべき</strong>です。簡易的には次のようにします。

簡易的な粗さへの対応は、3 通りあります。<strong>色のミップ</strong>（ぼかしピラミッド）は、シーン色のミップを作り、粗さまたはレイの長さに応じてミップを選びます。距離が遠く、粗いほど、ぼけた色になります。<strong>コーン トレース風</strong>の方法は、レイの距離に応じて反射の円錐が広がることを、ミップの選択で表します。<strong>ぼかし</strong>は、反射の画像全体を粗さでぼかす方法ですが、境界ににじみが出ます。

<strong>確率的な方式</strong>（[Stochastic SSR](../ssr-stochastic.md)）は、<strong>GGX の分布からレイをサンプル</strong>して、ぼけを物理的に正しく得ます。

## よくあるミス

??? failure "粗い面にも、鏡のようにくっきりした反射が出る"
    <strong>粗さに応じて、ぼかす</strong>（またはミップを選ぶ）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 半解像度でトレースして、コストを下げる
    - [x] 粗さは、ぼかしで近似

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [SSR Basics](index.md)
- [Stochastic SSR](../ssr-stochastic.md)
- [Color Lookup and Fading](color-fade.md)
