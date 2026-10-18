---
title: Floating Objects
tags:
  - 描画
---

# Floating Objects

<strong>船や浮き輪を、波に合わせて動かすには、波の高さを、CPU 側でも求める必要があります</strong>。<strong>頂点シェーダーの波の式を、CPU に同じ形で実装</strong>するのが簡単です。このページでは、浮力のための高さの取得を説明します。

!!! tip "ポイント"
    - 波の式を、GPU と CPU の両方に実装する。
    - 物体の数点で高さを取り、位置と傾きを決める。
    - FFT の場合は、GPU から読み戻すか、CPU で近似する。
    - 浮力の物理は、[Water Interaction](../interaction/index.md)を参照。

## 物を水に浮かせる
<strong>ボートや浮き</strong>を<strong>波に合わせて動かす</strong>には、CPU 側でも同じ波の高さを計算する必要があります。

波の高さを CPU 側で得る方法は 3 つです。同じ式を CPU で計算する方法は、Gerstner 波ならシェーダーと同じ式を C++ で実装し、複数点をサンプルして傾きと高さを決めます。GPU から読み戻す方法は、FFT の高さマップを読み戻してサンプルしますが、数フレーム遅れます。簡易な近似として、大きな波だけを CPU で計算し、細かい波は無視する方法もあります。

<strong>浮力（アルキメデスの原理）</strong>で、<strong>水に浸かった体積に応じた力</strong>を<strong>与える</strong>と、物理的に浮く動きになります。

### 浮力の考え方

船が波に浮かぶ動きは、物体のいくつかの点（船体の四隅など）で水面の高さを調べ、そこから浮力を決めて作ります。各点について、水面の高さと点の高さを比べて、点が水面より下にあれば、その深さに比例した上向きの力を加えます。複数の点に別々の力が加わるので、波の傾きに応じて、船が傾いたり揺れたりします。

注意が必要なのは、Gerstner 波では頂点が水平にも動くため、「ある位置 (x, z) の水面の高さ」を求めるには、逆変換が必要なことです。簡単な方法は、反復法で、元の位置 P₀ を推定し、その位置で波のずれを計算し、結果の位置とのずれを補正する、という計算を数回繰り返して収束させます。ゲームでは 2〜3 回の反復で十分です。

## CPU でも、水面の高さが、必要になる

船、浮き輪、樽、プレイヤーの泳ぎを、波に合わせるには、<strong>CPU（ゲームのロジックや、物理）が</strong>、水面の高さを、知る必要があります。水面は、GPU の頂点シェーダーで、動いているので、<strong>CPU が、同じ式で、計算</strong>するか、GPU から、結果を、取り出します。

| 方法 | 内容 | 向く波 |
| --- | --- | --- |
| 同じ式を、CPU で、計算する | シェーダーの式を、C++ で、書き直す。時間も、同じ値を、使う | サイン波、Gerstner 波 |
| GPU の結果を、読み戻す | 浮かぶ物の位置だけ、高さを、GPU で、計算して、ステージング バッファで、CPU へ返す。数フレーム遅れる | FFT |
| 低解像度の、近似を、CPU で持つ | 大きな波（低周波のカスケード）だけを、CPU で、計算する | FFT（大きなうねりだけで、船が、動くなら十分） |

## 「元の位置」を、逆算する

Gerstner 波では、頂点が<strong>水平にも動く</strong>ので、「`(x, z)` の位置の水面の高さ」は、<strong>単純に、式に `(x, z)` を代入しても、求まりません</strong>。式の入力は、動く前の位置 `P₀` で、見えている位置 `P` は、動いた後だからです。

```text
P = P₀ + D(P₀)         ← D は、水平の動き。P が、与えられたとき、P₀ を求めたい
```

<strong>不動点反復</strong>で、近似的に、解けます。

```cpp
// 位置 p（見えている位置）に対応する、動く前の位置 p0 を、反復で求める。
float2 FindUndisplacedPosition(float2 p, float time, int iterations = 4) {
  float2 p0 = p;                                  // 最初の推定: 動いていないとする
  for (int i = 0; i < iterations; ++i) {
    const float2 d = HorizontalDisplacement(p0, time);   // 推定した p0 での、水平の動き
    p0 = p - d;                                    // p = p0 + d を、p0 について解く
  }
  return p0;
}

float WaterHeightAt(float2 p, float time) {
  const float2 p0 = FindUndisplacedPosition(p, time);
  return Height(p0, time);                         // 求めた p0 で、高さを計算
}
```

反復は、<strong>3〜4 回</strong>で、ほぼ収束します。急峻さが小さい（`Q` が小さい）ほど、速く収束します。

## 浮力：簡単な方法（点サンプリング）

物体の、何点か（船体の、四隅や、底の複数点）で、水面の高さを調べ、<strong>「水面より、下にある分だけ、上向きの力を、かける」</strong>という方法です。

```cpp
struct FloatPoint { float3 local_position; };       // 物体のローカル座標での、浮力点

void ApplyBuoyancy(RigidBody& body, const std::vector<FloatPoint>& points, float time) {
  const float rho = 1000.0f;                         // 水の密度 (kg/m³)
  const float g = 9.81f;
  const float point_volume = body.volume / points.size();   // 各点が、受け持つ体積の目安

  for (const FloatPoint& fp : points) {
    const float3 world = body.LocalToWorld(fp.local_position);
    const float surface_y = WaterHeightAt({world.x, world.z}, time);
    const float depth = surface_y - world.y;         // 水面の下にある深さ（正なら、水の中）
    if (depth <= 0.0f) continue;                      // 水面より上: 力なし

    // 浮力: 沈んでいる体積の、水の重さ。深く沈むほど、強い（ただし、点の体積が、上限）
    const float submerged = std::clamp(depth / point_height, 0.0f, 1.0f);
    const float3 buoyancy = {0.0f, rho * g * point_volume * submerged, 0.0f};
    body.ApplyForceAtPoint(buoyancy, world);

    // 水の抵抗（動きを、減衰させる）
    const float3 v = body.VelocityAtPoint(world);
    body.ApplyForceAtPoint(-v * drag_coefficient * submerged, world);
  }
}
```

| 項目 | 内容 |
| --- | --- |
| 点の数 | 4〜16 点。多いほど、傾きの表現が、正確 |
| 抵抗 | 速度に比例した力を、かけて、揺れを、収束させる。ないと、跳ね続ける |
| 回転 | 点で力をかけると、トルク（回転力）も、自然に生じ、波の傾きに、合わせて、傾く |
| 安定性 | 浮力が、強すぎると、物理が発振する。抵抗と、物体の質量で、調整する |

## 浮力：より、現実的な方法

Kerner（2015）は、船の、水との相互作用を、<strong>船体の三角形ごとに</strong>、扱う方法を、整理しています。

| 力 | 内容 |
| --- | --- |
| 静水圧（浮力） | 水面の下の、三角形ごとに、水深に比例した圧力を、法線の向きに、かける |
| 粘性抗力 | 水と、船体の、相対速度に比例した、摩擦。三角形ごと |
| 圧力抗力 | 船体が、水を、押しのける力。進行方向を向いた、三角形が、強く受ける |
| スラミング（衝撃） | 船体が、水面に、叩きつけられたときの、衝撃の力 |

点サンプリングより、<strong>計算は、重い</strong>ですが、船の動きが、はるかに自然です。<strong>水に浸かっている三角形を、求める</strong>処理（水面と三角形の、切り取り）が、必要になります。

## FFT 海面での、高さ

FFT の海面は、頂点シェーダーが、テクスチャから、高さを読んでいます。CPU で、同じ高さを知るには、

| 方法 | 内容 |
| --- | --- |
| 読み戻し | 高さのテクスチャを、ステージング テクスチャにコピーして、CPU が読む。1〜3 フレーム遅れる。遅れを、許容できるほど、ゆっくりした動き（船）なら、問題ない |
| 低周波だけを、CPU で、計算する | 大きなカスケードの、高さマップを、CPU 側にも持ち、双線形補間で読む |
| 数点だけ、GPU で、計算する | 浮力点の位置だけを、計算シェーダーで、サンプリングして、小さなバッファへ書き、読み戻す |

```cpp
// 高さのテクスチャを、読み戻す（非同期）。
context->CopyResource(staging.Get(), height_texture.Get());
// 次のフレーム（以降）に、Map して読む。すぐに Map すると、GPU の完了を待ってしまう。
D3D11_MAPPED_SUBRESOURCE m;
if (SUCCEEDED(context->Map(staging_prev.Get(), 0, D3D11_MAP_READ, D3D11_MAP_FLAG_DO_NOT_WAIT, &m))) {
  // CPU 側のコピーを、更新する
  context->Unmap(staging_prev.Get(), 0);
}
```

`D3D11_MAP_FLAG_DO_NOT_WAIT` を指定すると、<strong>GPU が、まだ終わっていないとき、待たずに、失敗を返す</strong>ので、フレームを、止めません。失敗したら、次のフレームに、もう一度、試します。

## 時間を、そろえる

GPU の見た目と、CPU の浮力の、<strong>時間の値</strong>が、ずれると、<strong>船が、波と合わずに、浮きます</strong>。

| 注意点 | 内容 |
| --- | --- |
| 同じ時間を、使う | シェーダーに渡す `time` と、CPU の波の計算の `time` を、同じ変数から、作る |
| 時間の折り返し | 折り返す（`fmod`）なら、両方で、同じ周期を、使う（[Wave Animation Tricks](animation-tricks.md)） |
| 読み戻しの遅れ | 1〜3 フレーム遅れた高さを、使うなら、遅れた時間の、波として、扱う（その時間に、読み戻した値だから） |

## よくあるミス

??? failure "船が、見た目の波と合わずに浮く"
    <strong>GPU と同じ式・同じ時間</strong>で、<strong>CPU 側も計算</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] CPU 側でも、波の高さを求める

## 参考

- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015（船の浮力・抗力・水しぶき）
- Finch, "Effective Water Simulation from Physical Models", GPU Gems, Chapter 1, 2004（サイン波と Gerstner 波の、GPU 実装）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（FFT による海面の合成。ほとんどの FFT 海面の、出発点）
- Microsoft Learn, "D3D11_MAP_FLAG"（`D3D11_MAP_FLAG_DO_NOT_WAIT`）

## 関連ページ

- [Water Waves](index.md)
- [Water Interaction](../interaction/index.md)
