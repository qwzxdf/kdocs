---
title: Refraction Boundary Problems
tags:
  - 描画
---

# Refraction Boundary Problems

<strong>画面をずらして読むと、屈折する物体より「手前にある物」まで、ずれて読んでしまう</strong>ことがあります。<strong>境界でにじむ</strong>ので、深度を見て、手前の物は除くなどの工夫が必要です。このページでは、境界の問題と対策を説明します。

!!! tip "ポイント"
    - 屈折する物体より手前の物が、屈折の中に混ざる。
    - 対策：ずらした先の深度が、手前なら、ずらさない。
    - 境界のにじみは、深度比較で防げる。
    - 完全には直らないので、見た目で許容する。

## 屈折の境界の問題
<strong>画面空間の屈折には、典型的な破綻</strong>があります。

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| 前景の物が、屈折で背景に混ざる | ガラスより手前にある不透明物の画素を、屈折で読んでしまう | 読んだ位置の深度が、ガラスより手前なら、屈折せず元の位置を読む |
| 画面外を読む | 歪んだ UV が、画面の外に出る | クランプ・端でフェード・歪みを弱める |
| 後ろの半透明が写らない | コピーは、不透明のみ | 半透明のソート順で、コピーを取り直す（コスト大）・割り切る |
| ガラスの後ろのガラス | 屈折物どうしが重なる | 1 層のみ対応と割り切る・レイトレ |

### 前景の混入を避ける

```hlsl
float refracted_depth = LinearDepth(depth_texture.Sample(point_clamp, refract_uv).r);
float glass_depth = LinearDepth(input.position.z);
if (refracted_depth < glass_depth) {
  refract_uv = screen_uv;
}
float3 background = scene_color_copy.Sample(linear_clamp, refract_uv).rgb;
```

<strong>屈折先の深度が、ガラスより手前</strong>（＝<strong>ガラスの前の物</strong>を読んでしまう）なら、屈折をやめて、元の位置を読みます。

## 画面空間の、屈折は、境界で、破綻する

屈折を、<strong>画面のコピー</strong>の、<strong>ずらし</strong>で、表現する方法（[Screen-Space Refraction](screen-space.md)）は、簡単で、速い反面、ガラスの、境界（輪郭の、まわり）で、いくつかの、破綻を、起こします。

## 問題 1：手前の物が、にじむ

屈折で、<strong>ずらして、読む位置</strong>が、<strong>ガラスの、手前にある物</strong>（ガラスの前に、立っている人）に、当たると、その色が、ガラスの中に、にじみます。

```text
ガラス（背後を、屈折）
   ┃
 人 ┃    ← 人が、ガラスの、手前にいる
   ┃
ずらした先が、人にかかると、人の色が、ガラスの中に出てくる（本来は、人は、ガラスの前にいるので、ガラスの中には、映らない）
```

### 対策：深度で、チェックする

<strong>ずらした先の、深度</strong>が、<strong>ガラスより、手前</strong>なら、ずらさずに、元の位置を、読みます。

```hlsl
float scene_depth = LinearizeDepth(g_scene_depth.Sample(g_point_clamp, refract_uv).r);
float glass_depth = LinearizeDepth(input.position.z);
if (scene_depth < glass_depth) refract_uv = screen_uv;
```

<strong>完全には、解決しません</strong>。境界の、<strong>1 画素の、幅</strong>で、不連続が、残ります。

### より良い対策：マスクを、持つ

<strong>ガラスの、手前にある物</strong>を、<strong>別の、テクスチャ（マスク）</strong>に、記録しておく方法です。屈折する物を描く前に、ガラスより、手前の物を、ステンシルや、別のレンダー ターゲットに、描いておきます。

| 方法 | 内容 |
| --- | --- |
| 深度の、チェックのみ | 簡単。境界で、少し、にじむ |
| 手前の、物を、マスク | 正確。ただし、描画の順序（手前の物を先に、別に描く）が、複雑 |
| 2 回に、分けて描く | ガラスの奥の物を、描いて、コピーし、ガラスを描いてから、手前の物を、描く（描画順を、変える） |

## 問題 2：画面の端

ずらした UV が、<strong>画面の外</strong>に、出ることがあります。画面の外の、情報は、<strong>無い</strong>ので、端の色が、引き伸ばされた見た目になります。

| 対策 | 内容 |
| --- | --- |
| ずらし量を、端で、弱める | 画面の端に、近づくほど、ずらしを、小さくする |
| 画面より、少し大きく、描く | 画面より、広い範囲を、レンダリングして、端でも、情報が、あるようにする（コストが、増える） |
| 気にしない | 薄い、ガラスは、ずらしが、小さく、ほぼ、目立たない |

```hlsl
// 画面の端（0〜10%）で、ずらし量を、弱める。
float2 edge_dist = min(screen_uv, 1.0 - screen_uv);
float edge_fade = saturate(min(edge_dist.x, edge_dist.y) / 0.1);
offset *= edge_fade;
```

## 問題 3：ガラスの、中の、ガラス（重なり）

<strong>ガラスの向こうに、別のガラス</strong>があると、<strong>コピーが、1 枚</strong>しかないので、向こうの、ガラスの屈折が、手前のガラスの、屈折に、反映されません。向こうの、ガラスは、まだ、描かれていない（または、描かれていても、コピーに、含まれない）ためです。

| 対策 | 内容 |
| --- | --- |
| 奥から手前の順に描く | 奥のガラスを、先に描いて、コピーを更新し、手前のガラスを、描く。ガラスごとに、コピーが、必要（重い） |
| ガラスが、重ならないように、設計する | レベルの、設計で、避ける |
| 不透明の、ガラスとして、近似 | 2 枚目以降は、ブレンド（屈折なし） |

## 問題 4：ガラスの縁の、黒い線・ハロー

屈折で、ずらした先が、<strong>ガラスの、縁</strong>の、<strong>外側</strong>（背景）を、読むとき、縁が、にじむことが、あります。アンチエイリアス（MSAA、TAA）で、縁の画素が、ガラスと背景の、混ざった色になると、屈折の、読み先が、ずれて、縁が、輝いたり、暗くなります。

| 対策 | 内容 |
| --- | --- |
| 縁で、屈折を、弱める | 法線が、視線に、垂直に近い（縁）ほど、ずらし量を、小さくする（`saturate(dot(N, V))` を、掛ける） |
| TAA | 縁の、ちらつきを、時間方向に、平均する |

```hlsl
// 縁（法線が、視線に垂直）では、屈折を弱める。
float facing = saturate(dot(normal, view));
offset *= facing;
```

## 問題 5：水面と、地形が、交わる、境目

水や、ガラスが、<strong>地形（不透明な物）と、交わる線</strong>では、<strong>ずらした先</strong>が、ガラスの、前後の、どちらかで、大きく、違う結果になります。深度の、チェックで、ごまかしますが、境界線が、ギザギザに、なることがあります。

| 対策 | 内容 |
| --- | --- |
| 境界で、アルファを、フェード | 深度の差が、小さい所で、屈折の、強さを、下げる（[Soft Particles](../blending-sorting/soft-particles.md) と同じ考え方） |
| 境界に、泡や、縁の効果を、重ねる | 水の場合、岸の、泡で、境目を、隠す（[Shore Foam: Depth Difference](../../water/shore-foam/shore-depth.md)） |

## まとめ：境界の、扱い

| 境界の、問題 | 対策 |
| --- | --- |
| 手前の物が、にじむ | 深度チェック、マスク |
| 画面の端 | 端で、屈折を、弱める |
| ガラスの中の、ガラス | 奥から手前に描く、ガラスごとに、コピー |
| 縁の、にじみ | 縁で、屈折を、弱める、TAA |
| 地形との、交差 | アルファの、フェード、泡 |

<strong>どれも、完全な解決は、ない</strong>ので、<strong>「目立たないように、ごまかす」</strong>ことが、実際の、仕事です。屈折の、強さを、控えめにする（ずらし量が、小さいほど、破綻も、目立たない）のが、最も、効果が、大きい対策です。

## よくあるミス

??? failure "ガラスの手前の物が、ガラスの中に映り込んで歪む"
    <strong>ずらした先の深度を比較</strong>して、<strong>手前なら無効</strong>にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度を比べて、手前の物は除く

## 参考

- Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005
- Wyman, "An Approximate Image-Space Approach for Interactive Refraction", ACM Transactions on Graphics (SIGGRAPH 2005)
- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（屈折、フレネル、透過の章）

## 関連ページ

- [Refraction](index.md)
- [Screen-Space Refraction](screen-space.md)
