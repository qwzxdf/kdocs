---
title: AO Filtering
tags:
  - 描画
---

# AO Filtering

**AO は、少ないサンプルで計算するので、そのままでは、ノイズが多い**です。**ノイズを消すために、空間方向のぼかし（バイラテラル ブラー）と、時間方向の平均（時間蓄積）**を**組み合わせます**。**さらに、低解像度で計算して、アップサンプルで戻す**と**安くなります**。このセクションでは、**ノイズの原因・バイラテラル ブラー・アップサンプル・ノイズ パターン・時間蓄積・典型のパイプライン**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **ノイズ ＝ サンプル数が少ないため**。
    - **空間フィルタ**：**エッジを保つバイラテラル ブラー**。
    - **時間フィルタ**：**前フレームの結果を再投影して混ぜる**。
    - **低解像度で計算し、深度を見ながらアップサンプル**。
    - **ノイズ パターン（ブルー ノイズ）の選び方**で**フィルタの効きが変わる**。

## なぜノイズが出るのか
| 原因 | 説明 |
| --- | --- |
| **サンプルが少ない** | モンテカルロの誤差は、`1/√N`。N が 8 なら、**誤差は約 35%** |
| **画素ごとに違う向きを使う** | 規則的な縞（バンディング）を避けるため、わざとランダムにする（**縞をノイズに変える**） |
| **ノイズの方が消しやすい** | **規則的な縞はぼかしても消えない**。ランダムなノイズは、**平均で減る** |

つまり、<strong>「ノイズを出して、ぼかして消す」</strong>のがサンプル数を減らす定石です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Bilateral Blur](bilateral-blur.md) | 深度・法線でエッジを保つぼかし |
| [Upsampling](upsample.md) | 低解像度から、深度を見て戻す |
| [Noise Patterns](noise-pattern.md) | サンプルの回転・ブルー ノイズ |
| [Temporal Accumulation](temporal.md) | 前フレームの再投影・履歴の拒否 |
| [Typical Pipeline](pipeline.md) | 組み合わせ・パラメータの目安 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **AO のノイズは、空間と時間のフィルタで消す**
    - [x] **低解像度 ＋ アップサンプルで安く**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [Ambient Occlusion (AO)](../index.md)
- [Hemisphere SSAO](../ssao-hemisphere.md)
- [TAA](../../postprocess/antialiasing/taa.md)
