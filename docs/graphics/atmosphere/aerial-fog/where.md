---
title: Where to Apply Fog
tags:
  - 描画
---

# Where to Apply Fog

**フォグは、屋外では重要ですが、夜や屋内では、使い方を変える必要があります**。このページでは、**フォグを適用する場所と、夜・閉所の扱い**を説明します。

!!! tip "ポイント"
    - **不透明・半透明の両方に、フォグを適用**する。
    - **加算ブレンドは、フォグで黒に近づける**。
    - **夜は、フォグを暗い色に**。
    - **屋内は、フォグを弱める・別設定**にする。

## 適用する場所
| 場所 | 内容 |
| --- | --- |
| **フル スクリーン パス** | **不透明描画後に深度から位置を再構築して一括適用**。**簡単** |
| **マテリアルのシェーダー内** | **各物体のピクセル シェーダーでフォグを適用**。**半透明にも自然に適用** |
| **半透明** | **半透明は深度バッファに無いので、物ごとにシェーダー内で適用**（**パーティクル、ガラス**） |
| **ポストプロセスの前** | **HDR の線形空間** |

**加算ブレンドの物**は、**フォグの色を足さず、透過率だけ掛けます**（**霞の中で光が薄まるだけ**）。**足すと遠くの加算パーティクルが白く浮きます**。

## 夜と閉所
| 状況 | 扱い |
| --- | --- |
| **夜** | **フォグの色を暗く**。**月明かりで少しだけ明るく** |
| **室内** | **フォグを薄くする／区画ごとに変える**（**ボリューム フォグ**） |
| **洞窟・屋内の区画** | **区画（ボリューム）ごとにフォグの設定**を持ち、**境で補間** |
| **ライトの周り** | **点光源の周りだけ霧が光る**（[Volumetric Fog](../volumetric-fog/index.md)） |

## よくあるミス

??? failure "半透明の物だけ、フォグがかかっていない"
    **半透明にも、フォグを適用**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **すべての物にかけ、場所で設定を変える**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Aerial Perspective and Fog](index.md)
- [色を空に合わせる](color-match.md)
