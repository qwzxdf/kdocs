---
title: 空と大気
tags:
  - 描画
---

# 空と大気

**空の色・遠景の霞・雲・光の筋**は**大気中の光の散乱**という**1 つの現象**から**生まれます**。**昼は青く、夕方は赤く、遠くの山は青白く霞む**のは、**どれも同じ原理**です。このセクションでは、**空のモデル**、**散乱の物理**、**距離フォグ**、**ボリューメトリック フォグ**、**雲**、**光の筋**を**安い方法から物理に忠実な方法へ**と順に説明します。

!!! tip "ポイント"
    - 大気 ＝ <strong>光を散らす・吸う粒の集まり</strong>。<strong>空気の分子（レイリー散乱）と、大きな粒（ミー散乱）</strong>の<strong>2 種類</strong>。
    - <strong>空が青い</strong>のは<strong>短い波長ほど強く散るから</strong>。<strong>夕焼けが赤い</strong>のは<strong>光が大気を長く通り、青が散り尽くすから</strong>。
    - <strong>安い順</strong>：<strong>グラデーション → 解析モデル（Preetham・Hosek）→ LUT による物理計算（Bruneton・Hillaire）</strong>。
    - <strong>遠景の霞</strong>は<strong>距離フォグ</strong>（空気遠近法）。<strong>高さフォグ</strong>で<strong>谷に霧</strong>。
    - <strong>光が見える空間</strong>は<strong>ボリューメトリック フォグ</strong>（froxel）。
    - <strong>雲</strong>は<strong>レイマーチ</strong>。<strong>時間方向に蓄積</strong>して<strong>軽く</strong>する。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [空のモデル](sky-models.md) | グラデーション・Preetham・Hosek-Wilkie・太陽と月 |
| [大気散乱](scattering.md) | レイリー・ミー・透過率・Bruneton・Hillaire 2020 |
| [距離フォグ](aerial-fog.md) | 空気遠近法・距離フォグ・高さフォグ |
| [ボリューメトリック フォグ](volumetric-fog.md) | froxel・光の注入・積分・時間蓄積 |
| [雲](clouds.md) | レイマーチ・ノイズ・Beer-Powder・時間蓄積 |
| [光の筋](god-rays.md) | 放射ぼかし・シャドウ マップのレイマーチ |

## 関連ページ

- [描画](../index.md)
- [間接光（GI）](../gi/index.md)
- [ポストプロセス](../postprocess/index.md)
- [水](../water/index.md)
