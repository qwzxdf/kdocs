---
title: レイトレース AO（RTAO）
tags:
  - 描画
---

# レイトレース AO（RTAO）

**レイトレース AO は、シェーディングする点から、半球にレイを何本か飛ばし、一定距離以内に当たった割合を数えて、AO を求めます**。**ハードウェア レイトレーシングを使えば、画面外や薄い物も含めて、正確な AO** が**得られます**。**レイ数が少ないとノイズが多い**ので、**デノイズが必須**です。このページでは、**仕組み・実装・レイ数とデノイズ・コスト**を説明します。

!!! tip "ポイント"
    - **RTAO ＝ 半球にレイを飛ばし、半径内で当たったら遮蔽**。
    - **レイは、コサイン重みで分布**させる。
    - **1 ピクセル 1〜2 レイ ＋ デノイズ**が**実用的**。
    - **画面外・薄い物の裏側も正しい**。

## レイトレース AO（RTAO）
**DXR**（DirectX Raytracing）などのレイトレーシングで、**三角形に実際にレイを飛ばして**、AO を求めます。

### 手順

| 手順 | 内容 |
| --- | --- |
| **① 画素の位置と法線を得る** | G-Buffer から |
| **② レイの方向を作る** | **法線の側の半球**に**コサイン分布**で |
| **③ レイを飛ばす** | **最大距離 R**（影響半径）まで。**any-hit は不要**（当たったかだけ分かればよい） |
| **④ 当たったか** | 当たれば V = 0、当たらなければ V = 1 |
| **⑤ 平均する** | `AO = 平均(V)` |

[理論](../theory/index.md)のとおり、**コサイン分布でサンプルすれば、`AO = V の平均`**です。

```hlsl
[shader("raygeneration")]
void RtaoRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 p = WorldPosition(pixel);
  float3 n = WorldNormal(pixel);

  float3 dir = CosineSampleHemisphere(n, Random2(pixel, frame_index));

  RayDesc ray;
  ray.Origin = p + n * kRayBias;
  ray.Direction = dir;
  ray.TMin = 0.0;
  ray.TMax = ao_radius;

  AoPayload payload;
  payload.hit = 1.0;
  TraceRay(scene, RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH | RAY_FLAG_SKIP_CLOSEST_HIT_SHADER,
           0xFF, 0, 0, 0, ray, payload);

  ao_output[pixel] = payload.hit;
}
```

| 点 | 説明 |
| --- | --- |
| **`ACCEPT_FIRST_HIT_AND_END_SEARCH`** | **最初に当たった時点で終了**。最も近い交点は不要なので、**速い** |
| **`SKIP_CLOSEST_HIT_SHADER`** | 当たった後のシェーダーを省略 |
| **ミス シェーダーで `hit = 0`** | 当たらなければ、可視（payload の初期値を 1 にして、ミスで 0 にする、などの規約） |
| **`ray.TMax = R`** | **半径 R**。これが、AO の影響範囲 |
| **レイのバイアス** | 自己交差を避けるため、**法線方向に少し浮かせる** |

### 特徴

| 利点 | 欠点 |
| --- | --- |
| **正確**（画面外・隠れた物・薄い物も正しく遮蔽） | **1 画素 1〜2 本**のレイでは、**ノイズが大きい** |
| **ハローなどのアーティファクトが無い** | **ノイズ除去（デノイザー）が必須**（[フィルタ](../filtering/index.md)） |
| **コサイン重みが自然に入る** | **レイトレーシング対応の GPU** が必要。**BVH の構築・更新**のコスト |
| **半径の大きさに強い** | 動く物体が多いと、**BVH の更新**が重い |

### デノイズ

レイは**画素あたり 1 本**程度なので、**ノイズだらけ**です。<strong>空間（バイラテラル）と時間（再投影）</strong>で平均します。<strong>AO は 1 チャンネル（スカラー）</strong>で、他のレイトレ効果（反射・GI）より、**デノイズが軽い**です。

## よくあるミス

??? failure "レイ数が少なくて、ノイズだらけ"
    **時間蓄積と空間フィルタ（デノイズ）**を使う（[フィルタ](../filtering/index.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **RTAO ＝ 半球レイで遮蔽を数える**
    - [x] **正確だが、レイ数とデノイズが課題**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [世界空間 AO](index.md)
- [距離場 AO](dfao.md)
- [フィルタ](../filtering/index.md)
