---
title: Sky and Atmosphere
tags:
  - 描画
---

# Sky and Atmosphere

**空の色・遠景の霞・雲・光の筋**は**大気中の光の散乱**という**1 つの現象**から**生まれます**。**昼は青く、夕方は赤く、遠くの山は青白く霞む**のは、**どれも同じ原理**です。このセクションでは、**空のモデル**、**散乱の物理**、**距離フォグ**、**ボリューメトリック フォグ**、**雲**、**光の筋**を**安い方法から物理に忠実な方法へ**と順に説明します。

## 空と大気の設計

ゲームの空と大気の表現は、「どこまで物理に忠実にするか」を最初に決めることから始まります。

昼夜が固定で、カメラが地面を離れないゲームなら、[グラデーションの空](sky-models/gradient.md)と簡単なフォグで十分です。時刻が変化するなら、[解析的な空のモデル](sky-models/analytic.md)（Preetham・Hosek-Wilkie）が軽くて手軽です。さらに、宇宙から惑星を見る、異なる惑星の大気を表現する、といった自由度が必要なら、[大気散乱](scattering/index.md)を計算する方式（Bruneton・Hillaire）が必要になります。

空の上に重ねるものも、同じ考え方で選べます。遠景のかすみは[空気遠近法とフォグ](aerial-fog/index.md)、霧の中を通る光は[ボリューメトリック フォグ](volumetric-fog/index.md)、空に浮かぶ雲は[雲](clouds/index.md)、光の筋は[ゴッド レイ](god-rays/index.md)です。これらは独立していますが、同じ大気の中で起きる現象なので、色や強さを揃えると、画面全体に一貫性が出ます。たとえば、空気遠近法の色が空の色と一致し、雲のライティングに空と太陽の光を使い、フォグが太陽の方向で明るくなる、といった具合です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Sky Models](sky-models/index.md) | グラデーション・Preetham・Hosek-Wilkie・太陽と月 |
| [Atmospheric Scattering](scattering/index.md) | レイリー・ミー・透過率・Bruneton・Hillaire 2020 |
| [Aerial Perspective and Fog](aerial-fog/index.md) | 空気遠近法・距離フォグ・高さフォグ |
| [Volumetric Fog](volumetric-fog/index.md) | froxel・光の注入・積分・時間蓄積 |
| [Clouds](clouds/index.md) | レイマーチ・ノイズ・Beer-Powder・時間蓄積 |
| [God Rays](god-rays/index.md) | 放射ぼかし・シャドウ マップのレイマーチ |

## 関連ページ

- [描画](../index.md)
- [Global Illumination (GI)](../gi/index.md)
- [Post-Processing](../postprocess/index.md)
- [Water](../water/index.md)
