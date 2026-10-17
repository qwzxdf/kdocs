---
title: Cloud Temporal Reprojection
tags:
  - 描画
---

# Cloud Temporal Reprojection

**雲のレイマーチは重いので、毎フレーム全画素を計算せず、一部だけ更新して、前フレームと合成**します。**4×4 画素のうち、毎フレーム 1 画素だけ更新**する**方式**が**よく使われます**。このページでは、**時間蓄積による高速化**を説明します。

!!! tip "ポイント"
    - **4×4 の中の 1 画素だけ、毎フレーム更新**（16 フレームで全体）。
    - **他の画素は、前フレームを再投影**。
    - **低解像度で計算して、アップサンプル**。
    - **動きが速いと、ゴーストに注意**。

## 高速化：時間蓄積
**雲のレイマーチは重い**ので、**画面全体を毎フレーム描かず、1/4 の画素だけ描いて、時間をかけて埋めます**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="雲の時間蓄積">
<text x="20" y="24" class="fig-title">4×4 のうち 1 ピクセルだけ毎フレーム更新して、16 フレームで全体が埋まる</text>
<g transform="translate(40,50)">
<g stroke="currentColor" stroke-opacity="0.4" fill="none"><rect x="0" y="0" width="128" height="128"/>
<line x1="32" y1="0" x2="32" y2="128"/><line x1="64" y1="0" x2="64" y2="128"/><line x1="96" y1="0" x2="96" y2="128"/>
<line x1="0" y1="32" x2="128" y2="32"/><line x1="0" y1="64" x2="128" y2="64"/><line x1="0" y1="96" x2="128" y2="96"/></g>
<rect x="32" y="64" width="32" height="32" fill="#e5484d" fill-opacity="0.6"/>
<text x="64" y="156" text-anchor="middle" style="font-size:12px">今のフレームで描く位置</text>
</g>
<g font-size="12">
<text x="240" y="82" style="font-weight:700">手順</text>
<text x="240" y="106">① 1/4 解像度（または 4×4 に 1 画素）だけレイマーチ</text>
<text x="240" y="130">② 前フレームの結果を、カメラの動きで再投影して持ってくる</text>
<text x="240" y="154">③ 新しく描いた画素だけ置き換える</text>
<text x="240" y="178">④ 動く物の裏など、履歴が使えない所は新しい結果を優先</text>
<text x="240" y="212" style="font-weight:700">コスト：1/16 〜 1/4 に。ただしゴースト（残像）に注意</text>
</g>
</svg>

| 工夫 | 内容 |
| --- | --- |
| **低解像度で描く** | **半分／1/4 の解像度**で**レイマーチ**し、**アップサンプル** |
| **ブルー ノイズ ジッター** | **フレームごとに開始位置を変えて、平均で滑らか** |
| **履歴の再投影** | **前フレームの雲をカメラ移動分だけ動かす**（雲は遠いので回転だけで近似できる） |
| **層の距離を使う** | **雲までの距離（深度）を持って、再投影の精度を上げる** |
| **早期の打ち切り** | **透過率が低ければ打ち切る** |

## よくあるミス

??? failure "カメラを動かすと、雲がちらつく"
    **再投影の精度**を**上げ**、**履歴の拒否**をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **一部の画素だけ更新して、重ねる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Clouds](index.md)
- [レイマーチ](raymarch.md)
- [TAA](../../postprocess/antialiasing/taa.md)
