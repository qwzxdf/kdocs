---
title: ボクセル AO（VXAO）
tags:
  - 描画
---

# ボクセル AO（VXAO）

**ボクセル AO は、シーンを 3D のボクセル（立方体の格子）に変換し、そのミップで円錐トレース**して、**遮蔽を求めます**。**ボクセル GI と同じ仕組み**を**AO に使う**もので、**動く物体も、毎フレーム再ボクセル化して扱えます**。このページでは、**ボクセル化・円錐トレースによる AO・コスト**を説明します。

!!! tip "ポイント"
    - **VXAO ＝ シーンをボクセル化し、ミップで円錐トレース**。
    - **動く物体も扱える**（**毎フレーム再ボクセル化**）。
    - **ボクセルの解像度で、細部と範囲が決まる**。
    - **ボクセル GI と、仕組みを共有できる**（[ボクセル GI](../../gi/voxel-gi.md)）。

## ボクセル AO（VXAO）
**シーンをボクセル（3D の小さな箱）の格子に変換**し、各ボクセルに**占有度**（どれだけ埋まっているか）を保存します。**ミップマップ**を作り、**粗いレベルは広い範囲の平均の占有度**を持ちます。AO は**円錐に沿って、ミップを上げながら、占有度を積み上げる**ことで求めます。

### 円錐トレース

**円錐の断面は距離が離れるほど広がる**ので、**距離に応じたミップ**を読みます（近くは細かく、遠くは粗く）。**占有度を前から順に合成**します。

<div class="formula">occ ← occ + (1 − occ) · α(位置)　、　（α：その位置のボクセル占有度）</div>

```hlsl
float ConeOcclusion(float3 origin, float3 dir, float aperture) {
  float occlusion = 0.0;
  float t = kStartOffset;
  while (t < max_distance && occlusion < 1.0) {
    float diameter = 2.0 * aperture * t;
    float mip = log2(diameter / voxel_size);
    float alpha = voxel_tex.SampleLevel(linear_sampler, WorldToVoxel(origin + dir * t), mip).a;
    occlusion += (1.0 - occlusion) * alpha * DistanceFalloff(t);
    t += diameter * 0.5;
  }
  return 1.0 - occlusion;
}
```

| 点 | 説明 |
| --- | --- |
| **`mip`** | 円錐の直径に応じて、ボクセルのミップを選ぶ |
| **前から合成** | 手前の占有度が奥の寄与を隠す（アルファ合成と同じ） |
| **距離の減衰** | 遠い遮蔽を弱める（オブスキュランス） |

### 特徴

| 利点 | 欠点 |
| --- | --- |
| **動的なシーンにも使える**（毎フレーム、ボクセル化を更新） | **ボクセルの解像度が粗い**。**細部・薄い物は潰れる** |
| **AO だけでなく、間接光・反射・影**にも同じ構造が使える（**VXGI**。[GI](../../index.md)） | **ボクセル化のコスト**と**メモリ**（3D テクスチャ） |
| **レイトレ ハードウェア不要** | <strong>漏れ（ライト リーク）</strong>・**ブロック状のアーティファクト** |

## よくあるミス

??? failure "ボクセルが粗くて、AO がブロック状に見える"
    **ボクセルの解像度を上げる・カスケード**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ボクセル化 ＋ 円錐トレース**
    - [x] **動く物体も扱えるが、メモリと再ボクセル化のコスト**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [世界空間 AO](index.md)
- [距離場 AO](dfao.md)
- [ボクセル GI](../../gi/voxel-gi.md)
