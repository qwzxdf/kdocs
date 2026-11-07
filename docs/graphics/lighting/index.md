---
title: Lighting
tags:
  - 描画
---

# Lighting

画面の中の光を、どのような順番と構造で計算するか。ライトが 1 つなら、物を描くときにそのまま計算すれば済みますが、ライトが数十、数百と増えると、「どの画素にどのライトを当てるか」を整理しないと、計算が爆発します。このセクションは、その整理の仕方を扱います。物を描きながらライティングする Forward、先に情報を貯めてからライティングする Deferred、ライトをタイルやセルに振り分ける Tiled と Clustered、G-Buffer を三角形の ID だけにする Visibility Buffer です。

影・AO・GI・反射のような、光の効果そのものを作る手法は、それぞれの分野で扱います。ここは、それらの効果を積み上げる**土台の構造**です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Forward and Deferred](forward-deferred.md) | ライティングの基本の 2 方式。何が改善するのか |
| [Tiled and Clustered](light-culling.md) | ライトをタイル・3 次元のセルに分ける |
| [Visibility Buffer](visibility-buffer.md) | G-Buffer を三角形の ID だけにする |

## 光の効果を作る分野

- [Shadows](../shadows/index.md)
- [Ambient Occlusion (AO)](../ao/index.md)
- [Global Illumination (GI)](../gi/index.md)
- [Reflections](../reflections/index.md)

## 関連ページ

- [Draw Call](../draw-call/index.md)
- [Optimization](../optimization/index.md)
- [法線とライティング](../../3d/lighting-normals.md)
- [PBR](../../3d/pbr.md)
