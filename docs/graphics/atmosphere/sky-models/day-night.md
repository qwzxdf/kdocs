---
title: 昼夜のサイクル
tags:
  - 描画
---

# 昼夜のサイクル

**時間が進むと、太陽が動き、空の色・光の色・影の向きが変わります**。**これらを 1 つの「時刻」から連動させる**と、**管理が楽**です。このページでは、**昼夜のサイクル**を説明します。

!!! tip "ポイント"
    - **時刻 → 太陽の位置 → 空・光・影、が連動**。
    - **日の出・日没は、色が大きく変わる**（オレンジ）。
    - **夜は、月と星**。
    - **時間経過のコスト（環境マップの更新）に注意**。

## 昼夜のサイクル
**時刻から太陽の方向を決める**と、**すべてが連動します**。

```cpp
float time_of_day = std::fmod(game_hours, 24.0f) / 24.0f;
float angle = time_of_day * 2.0f * 3.14159265f - 3.14159265f * 0.5f;
Vector3 sun_direction(std::cos(angle) * 0.3f, std::sin(angle), std::cos(angle) * 0.95f);
sun_direction.Normalize();
```

| 連動する物 | 内容 |
| --- | --- |
| **空の色** | **太陽の方向から自動で** |
| **太陽光の色と強さ** | **高さで赤く・弱く**。**地平線の下で 0** |
| **環境光** | **空から更新** |
| **影の向き** | **平行光源の向き** |
| **月と星** | **夜に現れる** |
| **フォグの色** | **空の色に合わせる**（[距離フォグ](../aerial-fog/index.md)） |

## よくあるミス

??? failure "日没で、影が長くならない・向きが変わらない"
    **太陽の向きを、時刻から計算**して、**影**に使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **時刻から、すべてを連動させる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [空のモデル](index.md)
- [太陽・月・星](celestial.md)
