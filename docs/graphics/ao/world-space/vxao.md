---
title: ボクセル AO（VXAO）
tags:
  - 描画
---

# Voxel AO (VXAO) {#ボクセル-aovxao}

**ボクセル AO は、シーンを 3D のボクセル（立方体の格子）に変換し、そのミップで円錐トレース**して、**遮蔽を求めます**。**ボクセル GI と同じ仕組み**を**AO に使う**もので、**動く物体も、毎フレーム再ボクセル化して扱えます**。このページでは、**ボクセル化・円錐トレースによる AO・コスト**を説明します。

!!! tip "ポイント"
    - **VXAO ＝ シーンをボクセル化し、ミップで円錐トレース**。
    - **動く物体も扱える**（**毎フレーム再ボクセル化**）。
    - **ボクセルの解像度で、細部と範囲が決まる**。
    - **ボクセル GI と、仕組みを共有できる**（[Voxel GI](../../gi/voxel-gi.md)）。

## Voxel AO (VXAO) {#ボクセル-aovxao_1}

シーンをボクセル（3D の小さな箱）の格子に変換し、各ボクセルに<strong>占有度</strong>（どれだけ埋まっているか）を保存します。さらに、ミップマップを作ります。粗いミップのボクセルは、広い範囲の平均の占有度を持ちます。AO は、点から<strong>円錐</strong>に沿って、ミップを上げながら占有度を積み上げることで求めます。

### Voxelization {#ボクセル化}

シーンのメッシュを、3D テクスチャの中に書き込む処理がボクセル化です。典型的な方法は、各三角形を、面積が最も大きくなる軸（法線の主成分）の方向に向けた正射影で、ラスタライズする方法です。三角形をどの軸から見ても、ボクセルに穴が開かないようにするためです。ピクセル シェーダーから 3D テクスチャへ、アトミック操作や UAV への書き込みで、占有度（と、GI なら色）を書き込みます。薄い三角形でボクセルを取りこぼさないように、<strong>保守的ラスタライズ</strong>（三角形が少しでも触れた画素を処理対象にする）を使うこともあります。

動かない背景は、1 回ボクセル化したものを保持しておき、動く物体だけを毎フレーム再ボクセル化して合成すると、コストを抑えられます。さらに、カメラの周りだけを細かく、遠くを粗くする<strong>カスケード</strong>（カメラ中心の入れ子のボリューム）にすると、広い範囲を限られたメモリで扱えます。

### Cone Tracing {#円錐トレース}

AO の積分を、半球の方向をいくつかの<strong>円錐</strong>に分けて近似します。法線を中心に、真上 1 本と周りの 4〜6 本（開き角は 45〜60 度程度）の円錐で、半球を覆うのが一般的です。円錐の断面は、距離が離れるほど広がります。そこで、距離に応じたミップを読みます。近くは細かく、遠くは粗くです。占有度は前から順に合成し、手前の占有度が奥の寄与を隠します。これは、アルファ合成と同じ式です。

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

円錐の直径に応じてミップを選ぶので、`mip = log2(直径 / ボクセル サイズ)` です。距離の減衰を掛けて、遠い遮蔽を弱めます（オブスキュランス。[Obscurance](../theory/obscurance.md)）。`kStartOffset` は、出発点のボクセル自身を数えて自己遮蔽にならないよう、少し進めておく値です。

### Characteristics {#特徴}

利点は、動的なシーンにも使えること（毎フレーム、ボクセル化を更新）、AO だけでなく間接光・反射・影にも同じ構造が使えること（VXGI。[Voxel GI](../../gi/voxel-gi.md)）、レイトレ ハードウェアが不要なことです。

欠点は、ボクセルの解像度が粗いこと（細部や薄い物は潰れる）、ボクセル化のコストと 3D テクスチャのメモリが必要なこと、そして<strong>ライト リーク</strong>（壁の向こうの明るさが漏れる）やブロック状のアーティファクトが出やすいことです。薄い壁は 1 ボクセルより細いので、占有度が薄まって、遮蔽が弱くなります。

### Tricks for Higher Accuracy {#精度を上げる工夫}

占有度を<strong>異方性ボクセル</strong>（6 方向それぞれの占有度）で持つ方法があります。同じボクセルでも、見る方向によって「詰まっている度合い」が違うので、薄い壁を横から見たときと正面から見たときの違いを区別できます。円錐の軸の向きに合わせて、6 方向の値を混ぜて読みます。メモリは 6 倍近くになりますが、ライト リークが大きく減ります。

NVIDIA の VXAO は、この考え方を AO に絞って最適化した実装で、ボクセルに占有度だけを保存し、通常の AO（スクリーン空間）より高品質な接触の暗さを得ています。

## Common Mistakes {#よくあるミス}

??? failure "ボクセルが粗くて、AO がブロック状に見える"
    **ボクセルの解像度を上げる・カスケード**にする。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **ボクセル化 ＋ 円錐トレース**
    - [x] **動く物体も扱えるが、メモリと再ボクセル化のコスト**

## References {#参考}

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## Related Pages {#関連ページ}

- [世界空間 AO](index.md)
- [距離場 AO](dfao.md)
- [Voxel GI](../../gi/voxel-gi.md)
