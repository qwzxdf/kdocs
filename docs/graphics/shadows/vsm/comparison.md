---
title: Comparison with PCF
tags:
  - 描画
---

# Comparison with PCF

**VSM 系は、方式ごとに、光漏れ・メモリ・計算のバランスが違います**。**PCF と比べても、得意な場面が違う**ので、**用途で使い分けます**。このページでは、**VSM 系の比較表・PCF との使い分け**を説明します。

!!! tip "ポイント"
    - **VSM**：**安い・光漏れあり**。**ESM**：**簡単・数値に注意**。**EVSM**：**光漏れ少・重い**。**MSM**：**光漏れほぼなし・複雑**。
    - **PCF は、深度の比較を正しく行うので、光漏れがない**が、**大きなぼかしは重い**。
    - **VSM 系は、大きなぼかしが安い**が、**光漏れ・メモリ**。
    - **柔らかい影が主役なら VSM 系、安定・単純さなら PCF**。

## Comparing the VSM Family {#vsm-系の比較}
| 項目 | VSM | ESM | EVSM | MSM |
| --- | --- | --- | --- | --- |
| **チャンネル数** | 2 | 1 | 4（または 2） | 4 |
| **光漏れ** | <strong>あり（大）</strong> | 小（接触部で薄い） | **小** | **最小** |
| **精度の要求** | F32 | F32（オーバーフロー注意） | F32 | F16 でも可（工夫） |
| **計算コスト** | 小 | 最小 | 中 | 中〜大 |
| **フィルタ可能** | ○ | ○ | ○ | ○ |
| **実装の簡単さ** | ○ | ○ | △ | × |

## Choosing Between It and PCF {#pcf-との使い分け}
| 状況 | おすすめ |
| --- | --- |
| **広いソフト シャドウを、安く** | VSM・EVSM（**シャドウ マップをぼかすだけ**） |
| **精度・光漏れを避けたい** | **PCF**（扱いが素直） |
| **接触硬化が欲しい** | PCSS・レイトレ |
| **メモリ・帯域が厳しい** | PCF（深度 1 チャンネル）・ESM |
| **多くのライト** | VSM 系（**ぼかしが、1 回**） |

**現代のゲームでは、PCF（＋ ノイズ ＋ TAA）が、主流**です。VSM 系は**光漏れ・精度・メモリ**の問題から、**限定的**に使われます（**スポットライト・遠景・UI や特殊な効果**など）。

## Common Mistakes {#よくあるミス}

??? failure "VSM 系を選んだのに、光漏れの調整に時間がかかる"
    **最初から、EVSM・MSM を検討**する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **方式ごとに光漏れ・メモリ・複雑さが違う**
    - [x] **PCF は安定、VSM 系は大きなぼかしが安い**

## References {#参考}

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## Related Pages {#関連ページ}

- [VSM, ESM and MSM](index.md)
- [PCF](../pcf.md)
- [PCSS](../pcss.md)
