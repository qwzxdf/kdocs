---
title: 時間蓄積
tags:
  - 描画
---

# 時間蓄積

**1 フレームのサンプル数が少なくても、毎フレーム違うサンプルで計算して、過去のフレームの結果と混ぜれば、時間をかけて、サンプルが蓄積されます**。これが**時間蓄積**です。**カメラや物が動くと、過去の結果は位置がずれるので、速度（動きのベクトル）で再投影**し、**合わなければ捨てます**。このページでは、**再投影・履歴の拒否・ブレンド率・ゴースト対策**を説明します。

!!! tip "ポイント"
    - **毎フレーム違うサンプル ＋ 前フレームの結果と混ぜる**＝**サンプルが蓄積**。
    - **速度バッファで、前フレームの位置を求める**（[速度バッファ](../../postprocess/motion-blur/velocity-buffer.md)）。
    - **深度・法線が合わない履歴は拒否**（**ゴースト対策**）。
    - **ブレンド率は 0.05〜0.1**（**履歴 90〜95 %**）。

## 時間方向のフィルタ（時間蓄積）
**過去のフレームの AO を、再利用**して、**1 フレームあたりのサンプル数を、実質的に増やします**（[TAA・アップスケーラ](../../../rendering/taa-upscaling.md)と同じ発想）。

### 手順

| 手順 | 内容 |
| --- | --- |
| **① 再投影** | **今の画素の位置**を**前フレームの画面の位置**に変換（**動きベクトル**、または**深度とカメラ行列**から） |
| **② 履歴を読む** | 前フレームの AO を、その位置から読む |
| **③ 履歴の検証** | **深度・法線が今と近い**か。<strong>違えば、履歴は別の物（隠れていたものが現れた）</strong> → 捨てる |
| **④ 混ぜる** | `AO = lerp(履歴, 今, α)`。**α は 0.05〜0.2**（小さいほど滑らかだが遅れる） |

```hlsl
float TemporalAO(float2 uv, float current_ao) {
  float2 history_uv = Reproject(uv);
  float history_ao = history_tex.SampleLevel(linear_sampler, history_uv, 0).r;
  float history_z = history_depth_tex.SampleLevel(point_sampler, history_uv, 0).r;

  float depth_diff = abs(LinearDepth(uv) - history_z) / LinearDepth(uv);
  bool valid = all(saturate(history_uv) == history_uv) && depth_diff < 0.05;

  float alpha = valid ? 0.1 : 1.0;
  return lerp(history_ao, current_ao, alpha);
}
```

| 点 | 説明 |
| --- | --- |
| **画面外の履歴** | `history_uv` が、0〜1 の外なら、履歴なし（α = 1） |
| **深度の比較** | 相対的な差で**別の物体**を検出 |
| **α を信頼度で変える** | 履歴が**古い**ほど、**今の寄与を小さく**する（フレーム数を数えて、`α = 1/(n+1)` で平均） |
| **動くオブジェクト** | **動きベクトル**が無いと<strong>残像（ゴースト）</strong>が出る。**カメラの動きだけ**なら、深度とカメラ行列で再投影できる |

### ゴーストと対策

| 問題 | 対策 |
| --- | --- |
| **動く物体の残像** | 動きベクトルで再投影、または**履歴を深度・法線で拒否** |
| **ライトの変化への遅れ** | AO はライトに依存しないので、ほぼ問題なし。**形が変わる**とき（ドア・動く物）に遅れる |
| **カメラの急な動き** | 履歴を捨てる（α を大きく） |
| **履歴が使えない画素のノイズ** | **空間フィルタを強める**（履歴が無い画素だけ、ぼかしを大きくする） |

### 分散のクランプ

**スカラー AO**でも**周囲の画素の最小・最大**（または平均と分散）で、<strong>履歴を制限（クランプ）</strong>すると**古い履歴の暴走**を防げます（TAA の近傍クランプと同じ）。

## よくあるミス

??? failure "動く物の後ろに、AO の残像（ゴースト）が出る"
    **深度・法線で、履歴を拒否**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **毎フレーム違うサンプルを、時間で蓄積**
    - [x] **履歴の拒否で、ゴーストを防ぐ**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [AO のフィルタ](index.md)
- [ノイズ パターン](noise-pattern.md)
- [TAA](../../postprocess/antialiasing/taa.md)
