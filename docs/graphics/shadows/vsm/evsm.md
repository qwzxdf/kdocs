---
title: EVSM
tags:
  - 描画
---

# EVSM

**EVSM（指数 VSM）**は、**VSM と ESM を組み合わせ、深度を指数で変換してから、VSM の統計（平均と二乗平均）を取る**方式です。**光漏れが少なく、フィルタも使える**ので、**VSM 系で、実用的な選択肢**の**1 つ**です。**保存するデータが多く（4 チャンネル）**、**メモリと帯域は重い**です。このページでは、**EVSM の考え方・保存する値・実装のポイント**を説明します。

!!! tip "ポイント"
    - **EVSM ＝ 深度を `exp(c·d)` と `−exp(−c·d)` に変換し、それぞれ VSM の統計を取る**。
    - **2 つの指数を使う（正と負）ので、4 チャンネル保存**（`R32G32B32A32_FLOAT`）。
    - **光漏れが、VSM より大幅に少ない**。
    - **メモリは、VSM の 2 倍**。

## EVSM（指数 VSM）
**EVSM**（Exponential Variance Shadow Maps）は、**深度を exp でワープしてから、VSM**を行います。**正のワープ `exp(c z)`** と**負のワープ `−exp(−c z)`** を、**それぞれ VSM**にして、**小さい方**（保守的な方）を採用します。

| 項目 | 内容 |
| --- | --- |
| **保存するもの** | `(exp(c₊ z), exp(2 c₊ z), −exp(−c₋ z), exp(−2 c₋ z))`（**4 チャンネル**） |
| **光漏れ** | **VSM より、大幅に減る**（exp で深度の差が強調される） |
| **欠点** | **4 チャンネル**（メモリ・帯域が倍）。**浮動小数点の精度・範囲**に注意（32 ビット推奨） |

## よくあるミス

??? failure "16 ビット浮動小数で保存して、精度が足りず、縞が出る"
    **32 ビット浮動小数**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **EVSM ＝ 指数変換 ＋ VSM の統計**
    - [x] **光漏れが少ないが、メモリが重い**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [VSM と ESM・MSM](index.md)
- [ESM](esm.md)
- [MSM](msm.md)
