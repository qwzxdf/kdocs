---
title: Floating Objects
tags:
  - 描画
---

# Floating Objects

<strong>船や浮き輪を波に合わせて動かすには、波の高さを CPU 側でも求める必要があります</strong>。頂点シェーダーの波の式を CPU に同じ形で実装するのが簡単です。このページでは浮力のための高さの取得を説明します。

!!! tip "ポイント"
    - 波の式を GPU と CPU の両方に実装する。
    - 物体の数点で高さを取り、位置と傾きを決める。
    - FFT の場合は、GPU から読み戻すか CPU で近似する。
    - 浮力の物理は[Water Interaction](../interaction/index.md)を参照。

!!! info "このページを読む前に"
    - [Water Waves](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 物を水に浮かせる
<strong>ボートや浮き</strong>を波に合わせて動かすには、CPU 側でも同じ波の高さを計算する必要があります。

波の高さを CPU 側で得る方法は 3 つです。同じ式を CPU で計算する方法は、Gerstner 波ならシェーダーと同じ式を C++ で実装し、複数点をサンプルして傾きと高さを決めます。GPU から読み戻す方法は FFT の高さマップを読み戻してサンプルしますが、数フレーム遅れます。簡易な近似として大きな波だけを CPU で計算し、細かい波は無視する方法もあります。

浮力（アルキメデスの原理）で、水に浸かった体積に応じた力を与えると、物理的に浮く動きになります。

### 浮力の考え方

船が波に浮かぶ動きは物体のいくつかの点（船体の四隅など）で水面の高さを調べ、そこから浮力を決めて作ります。各点について水面の高さと点の高さを比べて、点が水面より下にあればその深さに比例した上向きの力を加えます。複数の点に別々の力が加わるので、波の傾きに応じて船が傾いたり揺れたりします。

注意が必要なのは Gerstner 波では頂点が水平にも動くため、「ある位置 (x, z) の水面の高さ」を求めるには、逆変換が必要なことです。簡単な方法は反復法で元の位置 P₀ を推定し、その位置で波のずれを計算し結果の位置とのずれを補正する、という計算を数回繰り返して収束させます。ゲームでは 2〜3 回の反復で十分です。

## CPU でも水面の高さが、必要になる

船、浮き輪、樽、プレイヤーの泳ぎを波に合わせるには、<strong>CPU（ゲームのロジックや、物理）が</strong>、水面の高さを知る必要があります。水面は GPU の頂点シェーダーで、動いているので CPU が同じ式で、計算するか GPU から結果を取り出します。

| 方法 | 内容 | 向く波 |
| --- | --- | --- |
| 同じ式を CPU で計算する | シェーダーの式を C++ で書き直す。時間も同じ値を使う | サイン波、Gerstner 波 |
| GPU の結果を読み戻す | 浮かぶ物の位置だけ高さを GPU で計算してステージング バッファで、CPU へ返す。数フレーム遅れる | FFT |
| 低解像度の近似を CPU で持つ | 大きな波（低周波のカスケード）だけを CPU で計算する | FFT（大きなうねりだけで船が動くなら十分） |

## 「元の位置」を逆算する

Gerstner 波では頂点が<strong>水平にも動く</strong>ので、「`(x, z)` の位置の水面の高さ」は、単純に式に `(x, z)` を代入しても、求まりません。式の入力は動く前の位置 `P₀` で、見えている位置 `P` は動いた後だからです。

```text
P = P₀ + D(P₀)         ← D は、水平の動き。P が、与えられたとき、P₀ を求めたい
```

不動点反復で近似的に解けます。

```cpp
// 位置 p（見えている位置）に対応する、動く前の位置 p0 を反復で求める。
float2 FindUndisplacedPosition(float2 p, float time, int iterations = 4) {
  float2 p0 = p;                                  // 最初の推定: 動いていないとする
  for (int i = 0; i < iterations; ++i) {
    const float2 d = HorizontalDisplacement(p0, time);   // 推定した p0 での、水平の動き
    p0 = p - d;                                    // p = p0 + d を p0 について解く
  }
  return p0;
}

float WaterHeightAt(float2 p, float time) {
  const float2 p0 = FindUndisplacedPosition(p, time);
  return Height(p0, time);                         // 求めた p0 で、高さを計算
}
```

反復は 3〜4 回でほぼ収束します。急峻さが小さい（`Q` が小さい）ほど、速く収束します。

## 浮力：簡単な方法（点サンプリング）

物体の何点か（船体の四隅や底の複数点）で、水面の高さを調べ <strong>「水面より、下にある分だけ上向きの力をかける」</strong>という方法です。

```cpp
struct FloatPoint { float3 local_position; };       // 物体のローカル座標での、浮力点

void ApplyBuoyancy(RigidBody& body, const std::vector<FloatPoint>& points, float time) {
  const float rho = 1000.0f;                         // 水の密度 (kg/m³)
  const float g = 9.81f;
  const float point_volume = body.volume / points.size();   // 各点が受け持つ体積の目安

  for (const FloatPoint& fp : points) {
    const float3 world = body.LocalToWorld(fp.local_position);
    const float surface_y = WaterHeightAt({world.x, world.z}, time);
    const float depth = surface_y - world.y;         // 水面の下にある深さ（正なら、水の中）
    if (depth <= 0.0f) continue;                      // 水面より上: 力なし

    // 浮力: 沈んでいる体積の、水の重さ。深く沈むほど、強い（ただし、点の体積が上限）
    const float submerged = std::clamp(depth / point_height, 0.0f, 1.0f);
    const float3 buoyancy = {0.0f, rho * g * point_volume * submerged, 0.0f};
    body.ApplyForceAtPoint(buoyancy, world);

    // 水の抵抗（動きを減衰させる）
    const float3 v = body.VelocityAtPoint(world);
    body.ApplyForceAtPoint(-v * drag_coefficient * submerged, world);
  }
}
```

| 項目 | 内容 |
| --- | --- |
| 点の数 | 4〜16 点。多いほど傾きの表現が正確 |
| 抵抗 | 速度に比例した力をかけて揺れを収束させる。ないと跳ね続ける |
| 回転 | 点で力をかけると、トルク（回転力）も自然に生じ、波の傾きに合わせて傾く |
| 安定性 | 浮力が強すぎると、物理が発振する。抵抗と物体の質量で調整する |

## 浮力：より現実的な方法

Kerner（2015）は船の、水との相互作用を <strong>船体の三角形ごとに</strong>、扱う方法を整理しています。

| 力 | 内容 |
| --- | --- |
| 静水圧（浮力） | 水面の下の、三角形ごとに水深に比例した圧力を法線の向きにかける |
| 粘性抗力 | 水と船体の、相対速度に比例した摩擦。三角形ごと |
| 圧力抗力 | 船体が水を押しのける力。進行方向を向いた三角形が強く受ける |
| スラミング（衝撃） | 船体が水面に叩きつけられたときの衝撃の力 |

点サンプリングより 計算は重いですが、船の動きがはるかに自然です。水に浸かっている三角形を求める処理（水面と三角形の、切り取り）が必要になります。

## FFT 海面での高さ

FFT の海面は頂点シェーダーがテクスチャから高さを読んでいます。CPU で同じ高さを知るには

| 方法 | 内容 |
| --- | --- |
| 読み戻し | 高さのテクスチャをステージング テクスチャにコピーして、CPU が読む。1〜3 フレーム遅れる。遅れを許容できるほどゆっくりした動き（船）なら、問題ない |
| 低周波だけを CPU で計算する | 大きなカスケードの、高さマップを CPU 側にも持ち、双線形補間で読む |
| 数点だけ GPU で計算する | 浮力点の位置だけを計算シェーダーでサンプリングして、小さなバッファへ書き読み戻す |

```cpp
// 高さのテクスチャを読み戻す（非同期）。
context->CopyResource(staging.Get(), height_texture.Get());
// 次のフレーム（以降）に Map して読む。すぐに Map すると、GPU の完了を待ってしまう。
D3D11_MAPPED_SUBRESOURCE m;
if (SUCCEEDED(context->Map(staging_prev.Get(), 0, D3D11_MAP_READ, D3D11_MAP_FLAG_DO_NOT_WAIT, &m))) {
  // CPU 側のコピーを更新する
  context->Unmap(staging_prev.Get(), 0);
}
```

`D3D11_MAP_FLAG_DO_NOT_WAIT` を指定すると <strong>GPU が、まだ終わっていないとき待たずに、失敗を返す</strong>のでフレームを止めません。失敗したら次のフレームにもう一度、試します。

## 時間をそろえる

GPU の見た目と CPU の浮力の、<strong>時間の値</strong>がずれると 船が波と合わずに浮きます。

| 注意点 | 内容 |
| --- | --- |
| 同じ時間を使う | シェーダーに渡す `time` と、CPU の波の計算の `time` を同じ変数から作る |
| 時間の折り返し | 折り返す（`fmod`）なら両方で、同じ周期を使う（[Wave Animation Tricks](animation-tricks.md)） |
| 読み戻しの遅れ | 1〜3 フレーム遅れた高さを使うなら遅れた時間の波として、扱う（その時間に読み戻した値だから） |

## よくあるミス

??? failure "船が見た目の波と合わずに浮く"
    <strong>GPU と同じ式・同じ時間</strong>で、CPU 側も計算する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] CPU 側でも、波の高さを求める

## 参考

- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015（船の浮力・抗力・水しぶき）
- Finch, "Effective Water Simulation from Physical Models", GPU Gems, Chapter 1, 2004（サイン波と Gerstner 波の、GPU 実装）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（FFT による海面の合成。ほとんどの FFT 海面の出発点）
- Microsoft Learn, "D3D11_MAP_FLAG"（`D3D11_MAP_FLAG_DO_NOT_WAIT`）

## 関連ページ

- [Water Waves](index.md)
- [Water Interaction](../interaction/index.md)
