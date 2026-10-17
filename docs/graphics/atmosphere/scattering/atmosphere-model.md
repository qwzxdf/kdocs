---
title: 大気のモデル
tags:
  - 描画
---

# 大気のモデル

**大気を、高さごとの密度を持つ層として表します**。**空気分子（レイリー）、エアロゾル（ミー）、オゾンが、それぞれ違う散乱・吸収を持ちます**。このページでは、**大気のモデル**を説明します。

!!! tip "ポイント"
    - **レイリー：高さとともに指数で薄くなる（約 8 km）**。
    - **ミー：低い所に多い（約 1.2 km）**。
    - **オゾン：青を吸収し、夕空の色に効く**。
    - **散乱係数は、波長ごとに持つ**。

## 大気のモデル
**地球の大気は球殻**です。**密度は高さに対して指数的に減ります**。

<div class="formula">ρ(h) = exp( −h / H )　（H：スケール ハイト）</div>

| 成分 | スケール ハイト H | 特徴 |
| --- | --- | --- |
| <strong>レイリー（空気分子）</strong> | **約 8 km** | **青く散る。後ろにも前にも均等に** |
| <strong>ミー（エアロゾル）</strong> | **約 1.2 km** | <strong>ほぼ白く散る。前方に強い（太陽の周りのにじみ）</strong> |
| **オゾン** | **高さ 25 km 付近に層** | **散らさず、吸収する**（**朝夕の空の青みの基**） |

**地球の半径は 6360 km、大気の上端は 6460 km**（高さ 100 km）です。

| 係数 | 意味 |
| --- | --- |
| **散乱係数 σs** | **単位長さあたり、散らされる割合**（RGB で違う） |
| **吸収係数 σa** | **単位長さあたり、吸われる割合** |
| **消散係数 σt = σs + σa** | **減る割合の合計** |

<strong>レイリー散乱係数（海面）</strong> は、**RGB で (5.8, 13.5, 33.1) × 10⁻⁶ /m** 程度（**青が大きい**）、**ミー散乱は (3.9, 3.9, 3.9) × 10⁻⁶ /m** 程度です。

## よくあるミス

??? failure "夕焼けが、赤くならない"
    **オゾンの吸収**と **波長ごとの散乱係数**を**入れる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さごとの密度と、波長ごとの係数**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [大気散乱](index.md)
- [透過率](transmittance.md)
