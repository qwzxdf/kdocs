---
title: Choosing a Method
tags:
  - 描画
---

# Choosing a Method

**動的な GI の手法は、品質・コスト・必要なハードウェアで、向き不向きがあります**。このページでは、**手法の選び方の目安と、長所・短所**を説明します。

!!! tip "ポイント"
    - **ハードウェア RT が使える → レイトレ GI ＋ ReSTIR**。
    - **使えない → Lumen 的な方式・DDGI・SSGI**。
    - **2D やステージ制 → Radiance Cascades**。
    - **予算が厳しい → SSGI やプローブ**。

## 手法の選び方（動的 GI）
| 状況 | 方式 |
| --- | --- |
| **HW RT 対応・最高品質** | **レイトレ GI ＋ ReSTIR ＋ デノイズ**、**DDGI** |
| **HW RT なしの一般向け** | **Lumen 的**（距離場 ＋ プローブ）、**SDFGI** |
| **2D ゲーム** | **Radiance Cascades**・**距離場ベースの 2D GI** |
| **モバイル** | **ライトマップ ＋ プローブ**（動的 GI は避ける） |

## 長所と短所
| 長所 | 短所 |
| --- | --- |
| **正確**（ジオメトリそのもの） | **ノイズ** ＋ **デノイズ**が必須 |
| **画面外・裏側**も**反映** | **コストが高い**（レイ・デノイズ・加速構造） |
| **動く物・動くライトに自然に対応** | **HW RT 対応 GPU**（ソフトウェア方式は、品質が劣る） |
| **ReSTIR などで年々、効率が向上** | **実装が複雑**（ReSTIR・デノイザ） |

## よくあるミス

??? failure "最新の手法を選んで、対象機種で動かない"
    **対象のハードウェア**から**逆算して選ぶ**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ハードウェアと予算から、手法を選ぶ**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Ray-Traced GI](index.md)
- [GI の比較](../comparison.md)
- [DDGI](../ddgi.md)
