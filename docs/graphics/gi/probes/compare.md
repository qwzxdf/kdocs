---
title: Comparison with Reflection Probes and Cost
tags:
  - 描画
---

# Comparison with Reflection Probes and Cost

<strong>GI のプローブと、反射プローブは、名前が似ていますが、役割が違います</strong>。<strong>GI のプローブは「拡散の間接光」、反射プローブは「鏡面の反射」</strong>です。このページでは、違いと、コスト・長所短所を説明します。

!!! tip "ポイント"
    - GI プローブ ＝ 拡散・低周波・SH で保存。
    - 反射プローブ ＝ 鏡面・高周波・キューブマップで保存。
    - 両方を、併用するのが普通。
    - GI プローブは、軽く、動く物体にも使える。ただし、細かい影は出ない。

## 反射プローブとの違い
| 項目 | ライト プローブ | 反射プローブ |
| --- | --- | --- |
| 保存するもの | 放射照度（拡散の間接光） | 放射輝度（周囲の画像） |
| 周波数 | 低い | 高い |
| 保存形式 | SH・少数の数値 | キューブマップ |
| 用途 | 拡散反射 | 鏡面反射 |
| 密度 | やや密 | <strong>疎（部屋ごと）</strong> |

<strong>反射プローブ</strong>は、[Reflection Probes](../../reflections/probes/index.md)で説明しています。<strong>両方を置いて</strong>、拡散と鏡面の間接光をそれぞれ賄います。

## コストと利点
| 項目 | 内容 |
| --- | --- |
| 実行時のコスト | 補間 ＋ SH の評価。非常に安い |
| メモリ | プローブ数 × 係数。ライトマップより、はるかに小さい |
| 動く物体への適用 | 自然に対応 |
| 品質の限界 | 低周波のみ。<strong>細かい間接光の影（接触部）</strong>は出ない（AO で補う） |

## 長所と短所
| 長所 | 短所 |
| --- | --- |
| 動く物体に間接光を与えられる | 低周波のみ（細かい間接影が出ない） |
| 安い・小さい | ライト リーク（壁越しの漏れ） |
| ライトマップと併用しやすい | 配置の手間（品質が置き方次第） |
| 動的な更新に拡張できる | ベイクのままでは、光の変化に追従できない |


### どちらをいつ使うか

ライト プローブは、<strong>ほぼすべての 3D ゲームに置く</strong>と考えて構いません。動く物体に自然な陰影を与える最も安い方法だからです。反射プローブは、<strong>つるつるした面が多いシーン</strong>（金属、濡れた床、窓ガラス）で必要になります。マットな素材ばかりのシーンなら、反射プローブは少数で済みます。どちらも、ライトマップと矛盾しない見た目になるよう、同じ光源・同じシーンから作ることが大切です。

### どちらをいつ使うか

ライト プローブは、<strong>ほぼすべての 3D ゲームに置く</strong>と考えて構いません。動く物体に自然な陰影を与える最も安い方法だからです。反射プローブは、<strong>つるつるした面が多いシーン</strong>（金属、濡れた床、窓ガラス）で必要になります。マットな素材ばかりのシーンなら、反射プローブは少数で済みます。どちらも、ライトマップと矛盾しない見た目になるよう、同じ光源・同じシーンから作ることが大切です。

## よくあるミス

??? failure "GI のプローブで、鏡のような反射を出そうとする"
    <strong>鏡面は、反射プローブ・SSR</strong>で扱う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GI は拡散、反射プローブは鏡面
    - [x] 併用するのが普通

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Probe GI](index.md)
- [Reflection Probes](../../reflections/probes/index.md)
- [GI Theory](../theory/index.md)
