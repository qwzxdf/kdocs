---
title: Sky and Atmosphere
tags:
  - 描画
---

# Sky and Atmosphere

**空の色・遠景の霞・雲・光の筋**は**大気中の光の散乱**という**1 つの現象**から**生まれます**。**昼は青く、夕方は赤く、遠くの山は青白く霞む**のは、**どれも同じ原理**です。このセクションでは、**空のモデル**、**散乱の物理**、**距離フォグ**、**ボリューメトリック フォグ**、**雲**、**光の筋**を**安い方法から物理に忠実な方法へ**と順に説明します。

!!! tip "ポイント"
    - 大気 ＝ <strong>光を散らす・吸う粒の集まり</strong>。<strong>空気の分子（レイリー散乱）と、大きな粒（ミー散乱）</strong>の<strong>2 種類</strong>。
    - <strong>空が青い</strong>のは<strong>短い波長ほど強く散るから</strong>。<strong>夕焼けが赤い</strong>のは<strong>光が大気を長く通り、青が散り尽くすから</strong>。
    - <strong>安い順</strong>：<strong>グラデーション → 解析モデル（Preetham・Hosek）→ LUT による物理計算（Bruneton・Hillaire）</strong>。
    - <strong>遠景の霞</strong>は<strong>距離フォグ</strong>（空気遠近法）。<strong>高さフォグ</strong>で<strong>谷に霧</strong>。
    - <strong>光が見える空間</strong>は<strong>ボリューメトリック フォグ</strong>（froxel）。
    - <strong>雲</strong>は<strong>レイマーチ</strong>。<strong>時間方向に蓄積</strong>して<strong>軽く</strong>する。

## 空と大気の設計

ゲームの空と大気の表現は、「どこまで物理に忠実にするか」を最初に決めることから始まります。

昼夜が固定で、カメラが地面を離れないゲームなら、[グラデーションの空](sky-models/gradient.md)と簡単なフォグで十分です。時刻が変化するなら、[解析的な空のモデル](sky-models/analytic.md)（Preetham・Hosek-Wilkie）が軽くて手軽です。さらに、宇宙から惑星を見る、異なる惑星の大気を表現する、といった自由度が必要なら、[大気散乱](scattering/index.md)を計算する方式（Bruneton・Hillaire）が必要になります。

空の上に重ねるものも、同じ考え方で選べます。遠景のかすみは[空気遠近法とフォグ](aerial-fog/index.md)、霧の中を通る光は[ボリューメトリック フォグ](volumetric-fog/index.md)、空に浮かぶ雲は[雲](clouds/index.md)、光の筋は[ゴッド レイ](god-rays/index.md)です。これらは独立していますが、同じ大気の中で起きる現象なので、色や強さを揃えると、画面全体に一貫性が出ます。たとえば、空気遠近法の色が空の色と一致し、雲のライティングに空と太陽の光を使い、フォグが太陽の方向で明るくなる、といった具合です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Sky Models](sky-models/index.md) | グラデーション・Preetham・Hosek-Wilkie・太陽と月 |
| [Atmospheric Scattering](scattering/index.md) | レイリー・ミー・透過率・Bruneton・Hillaire 2020 |
| [距離フォグ](aerial-fog/index.md) | 空気遠近法・距離フォグ・高さフォグ |
| [Volumetric Fog](volumetric-fog/index.md) | froxel・光の注入・積分・時間蓄積 |
| [Clouds](clouds/index.md) | レイマーチ・ノイズ・Beer-Powder・時間蓄積 |
| [光の筋](god-rays/index.md) | 放射ぼかし・シャドウ マップのレイマーチ |

## 関連ページ

- [描画](../index.md)
- [Global Illumination (GI)](../gi/index.md)
- [Post-Processing](../postprocess/index.md)
- [Water](../water/index.md)
