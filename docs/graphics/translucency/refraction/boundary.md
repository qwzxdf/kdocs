---
title: Refraction Boundary Problems
tags:
  - 描画
---

# Refraction Boundary Problems

<strong>画面をずらして読むと屈折する物体より「手前にある物」まで、ずれて読んでしまう</strong>ことがあります。<strong>境界でにじむ</strong>ので深度を見て、手前の物は除くなどの工夫が必要です。このページでは境界の問題と対策を説明します。

!!! tip "ポイント"
    - 屈折する物体より手前の物が、屈折の中に混ざる。
    - 対策：ずらした先の深度が、手前ならずらさない。
    - 境界のにじみは深度比較で防げる。
    - 完全には直らないので、見た目で許容する。

## 屈折の境界の問題
<strong>画面空間の屈折には典型的な破綻</strong>があります。

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| 前景の物が屈折で背景に混ざる | ガラスより手前にある不透明物の画素を、屈折で読んでしまう | 読んだ位置の深度が、ガラスより手前なら屈折せず元の位置を読む |
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

<strong>屈折先の深度がガラスより手前</strong>（＝<strong>ガラスの前の物</strong>を読んでしまう）なら、屈折をやめて元の位置を読みます。

## 画面空間の屈折は境界で、破綻する

屈折を <strong>画面のコピー</strong>の <strong>ずらし</strong>で、表現する方法（[Screen-Space Refraction](screen-space.md)）は簡単で、速い反面、ガラスの境界（輪郭のまわり）で、いくつかの破綻を起こします。

## 問題 1：手前の物がにじむ

屈折で <strong>ずらして読む位置</strong>が、<strong>ガラスの手前にある物</strong>（ガラスの前に、立っている人）に当たるとその色が、ガラスの中ににじみます。

```text
ガラス（背後を、屈折）
   ┃
 人 ┃    ← 人が、ガラスの、手前にいる
   ┃
ずらした先が、人にかかると、人の色が、ガラスの中に出てくる（本来は、人は、ガラスの前にいるので、ガラスの中には、映らない）
```

### 対策：深度でチェックする

<strong>ずらした先の深度</strong>が <strong>ガラスより、手前</strong>ならずらさずに元の位置を、読みます。

```hlsl
float scene_depth = LinearizeDepth(g_scene_depth.Sample(g_point_clamp, refract_uv).r);
float glass_depth = LinearizeDepth(input.position.z);
if (scene_depth < glass_depth) refract_uv = screen_uv;
```

<strong>完全には解決しません</strong>。境界の <strong>1 画素の幅</strong>で不連続が、残ります。

### より良い対策：マスクを持つ

<strong>ガラスの手前にある物</strong>を <strong>別の、テクスチャ（マスク）</strong>に記録しておく方法です。屈折する物を描く前にガラスより、手前の物をステンシルや別のレンダー ターゲットに、描いておきます。

| 方法 | 内容 |
| --- | --- |
| 深度のチェックのみ | 簡単。境界で少しにじむ |
| 手前の物をマスク | 正確。ただし、描画の順序（手前の物を先に別に描く）が、複雑 |
| 2 回に分けて描く | ガラスの奥の物を描いて、コピーしガラスを描いてから手前の物を、描く（描画順を変える） |

## 問題 2：画面の端

ずらした UV が <strong>画面の外</strong>に、出ることがあります。画面の外の情報は <strong>無い</strong>ので、端の色が引き伸ばされた見た目になります。

| 対策 | 内容 |
| --- | --- |
| ずらし量を端で弱める | 画面の端に、近づくほどずらしを小さくする |
| 画面より少し大きく描く | 画面より、広い範囲をレンダリングして端でも情報が、あるようにする（コストが増える） |
| 気にしない | 薄いガラスは、ずらしが小さくほぼ目立たない |

```hlsl
// 画面の端（0〜10%）で、ずらし量を、弱める。
float2 edge_dist = min(screen_uv, 1.0 - screen_uv);
float edge_fade = saturate(min(edge_dist.x, edge_dist.y) / 0.1);
offset *= edge_fade;
```

## 問題 3：ガラスの中の、ガラス（重なり）

<strong>ガラスの向こうに別のガラス</strong>があると、<strong>コピーが 1 枚</strong>しかないので、向こうのガラスの屈折が手前のガラスの屈折に、反映されません。向こうのガラスはまだ描かれていない（または、描かれていてもコピーに含まれない）ためです。

| 対策 | 内容 |
| --- | --- |
| 奥から手前の順に描く | 奥のガラスを、先に描いてコピーを更新し手前のガラスを描く。ガラスごとにコピーが必要（重い） |
| ガラスが重ならないように、設計する | レベルの設計で、避ける |
| 不透明のガラスとして近似 | 2 枚目以降は、ブレンド（屈折なし） |

## 問題 4：ガラスの縁の、黒い線・ハロー

屈折でずらした先が <strong>ガラスの縁</strong>の、<strong>外側</strong>（背景）を読むとき縁が、にじむことがあります。アンチエイリアス（MSAA、TAA）で縁の画素がガラスと背景の、混ざった色になると屈折の読み先がずれて縁が、輝いたり暗くなります。

| 対策 | 内容 |
| --- | --- |
| 縁で屈折を弱める | 法線が視線に、垂直に近い（縁）ほどずらし量を、小さくする（`saturate(dot(N, V))` を掛ける） |
| TAA | 縁のちらつきを、時間方向に平均する |

```hlsl
// 縁（法線が、視線に垂直）では、屈折を弱める。
float facing = saturate(dot(normal, view));
offset *= facing;
```

## 問題 5：水面と地形が交わる境目

水やガラスが <strong>地形（不透明な物）と、交わる線</strong>では <strong>ずらした先</strong>が、ガラスの前後のどちらかで大きく、違う結果になります。深度のチェックでごまかしますが、境界線がギザギザになることがあります。

| 対策 | 内容 |
| --- | --- |
| 境界でアルファをフェード | 深度の差が、小さい所で屈折の強さを下げる（[Soft Particles](../blending-sorting/soft-particles.md) と同じ考え方） |
| 境界に泡や縁の効果を重ねる | 水の場合、岸の泡で境目を隠す（[Shore Foam: Depth Difference](../../water/shore-foam/shore-depth.md)） |

## まとめ：境界の扱い

| 境界の問題 | 対策 |
| --- | --- |
| 手前の物がにじむ | 深度チェック、マスク |
| 画面の端 | 端で屈折を、弱める |
| ガラスの中のガラス | 奥から手前に描く、ガラスごとにコピー |
| 縁のにじみ | 縁で屈折を弱める、TAA |
| 地形との交差 | アルファの、フェード、泡 |

<strong>どれも完全な解決はない</strong>ので、<strong>「目立たないようにごまかす」</strong>ことが実際の、仕事です。屈折の強さを控えめにする（ずらし量が、小さいほど破綻も目立たない）のが最も効果が、大きい対策です。

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
