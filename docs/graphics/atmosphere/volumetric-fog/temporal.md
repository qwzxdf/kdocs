---
title: Temporal Accumulation
tags:
  - 描画
---

# Temporal Accumulation

**froxel の解像度は低いので、ノイズや段が出ます**。**毎フレーム、サンプルの位置をずらして、前フレームと混ぜる**と、**実質の解像度が上がり、なめらか**になります。このページでは、**時間蓄積**を説明します。

!!! tip "ポイント"
    - **毎フレーム、サンプル位置を少しずらす（ジッタ）**。
    - **前フレームの結果を、再投影して混ぜる**。
    - **動く物体の周りで、ゴーストに注意**。
    - **TAA と同じ考え方**。

## 時間蓄積（TAA 風）
**froxel の解像度が低く、サンプルが少ない**ので**そのままだとノイズや縞が出ます**。**前フレームの結果を再利用して、時間方向に平均します**。

| 工夫 | 内容 |
| --- | --- |
| **ジッター** | **毎フレーム、froxel 内のサンプル位置を少しずらす**（ブルー ノイズなど） |
| **履歴の再投影** | **前フレームの froxel の位置を、カメラの動きで求めて、その値を混ぜる** |
| **ブレンド率** | **新 5〜10 %、履歴 90〜95 %** |
| **履歴の拒否** | **ライトが動いたとき／急な変化は、履歴を弱める** |

```hlsl
float3 previous_uvw = ReprojectFroxel(world_position, previous_view_projection);
float4 history = history_volume.SampleLevel(linear_clamp, previous_uvw, 0);
float4 current = float4(scattering, extinction);
float blend = IsValidHistory(previous_uvw) ? 0.05 : 1.0;
float4 result = lerp(history, current, blend);
```

### 効果とその仕組み

ジッターを入れて時間蓄積すると、実質的な解像度が上がります。毎フレーム、セル内のサンプル位置（セルの中心でなく、少しずれた位置）を変えて計算し、その結果を平均すると、セルの内側の構造が、時間をかけて少しずつ埋まっていくからです。TAA が、画素の中のサブピクセル位置をずらして平均し、エッジを滑らかにするのと同じ原理です。

注意点は、ライトや霧の密度が急に変わった場合です。履歴をそのまま混ぜると、変化に対する追従が遅れて、残像として見えます。ライトの強さや位置が大きく変わったフレームでは、ブレンド率を一時的に上げて（履歴を軽視する）、新しい値へ素早く切り替えます。また、動く物体（キャラクター）が通ったとき、その通り道の霧が乱される表現を入れる場合は、動く物体の周りの履歴を捨てる処理も必要です。

再投影した位置が froxel の範囲外（画面の外から入ってきたセル）の場合、履歴は存在しないので、ブレンド率を 1（新しい値だけ）にします。コードの `IsValidHistory` がその判定です。

## よくあるミス

??? failure "霧が、動くと尾を引く"
    **履歴の拒否**・**ブレンド率の調整**をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ジッタと再投影で、実質の解像度を上げる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Volumetric Fog](index.md)
- [TAA](../../postprocess/antialiasing/taa.md)
