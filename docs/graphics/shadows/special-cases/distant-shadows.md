---
title: Distant Shadows
tags:
  - 描画
---

# Distant Shadows

<strong>遠くまで、シャドウ マップを広げる</strong>と<strong>解像度が足りず、コストも大きい</strong>ので、遠景は別の方法で影を表します。雲の影（地面を流れる雲の影）や、遠くの山の影など、大きなスケールの影は、事前計算や、専用の簡易な方式で表現します。このページでは、遠景の影の扱い・雲の影・距離によるフェードを説明します。

!!! tip "ポイント"
    - シャドウ マップは、距離とともに解像度が落ちる。遠景は別の仕組み。
    - 雲の影：雲の密度テクスチャを、太陽方向から地面へ投影して暗くする。
    - 距離フェード：シャドウ マップの最大距離で、影を滑らかに消す。
    - 遠くの影は、ベイク・距離場・簡易方式。

## 遠景の影
<strong>カスケードの最大距離</strong>を超えた先は、<strong>影がなくなります</strong>。遠景の山・建物の大きな影をどう扱うかです。

| 方法 | 内容 |
| --- | --- |
| フェードアウト | 最大距離で影を徐々に消す（[Cascaded Shadow Maps (CSM)](../cascaded.md)） |
| ベイク済みの影 | 静的な遠景はライトマップ・影のマスクにベイク |
| 距離場の影 | 遠景に距離場の影を使う（[Distance Field Shadows](../sdf-shadows.md)） |
| 大きな最後のカスケード | 最後のカスケードを非常に大きく（粗いが遠くの大きな影は捉える） |
| 雲の影 | 雲のテクスチャを地面に投影して、大規模な、移動する影を安く表現 |

### 雲の影

<strong>雲のアルファ テクスチャ</strong>を、<strong>太陽の方向</strong>から地面に投影し、ライティングに乗算します。時間でスクロールさせれば、雲の影がゆっくり動く様子になります。

```hlsl
float2 cloud_uv = world_pos.xz * cloud_scale + wind * time;
float cloud_shadow = lerp(1.0, cloud_tex.Sample(linear_sampler, cloud_uv).r, cloud_strength);
lit *= cloud_shadow;
```

## 問題：遠くの影は、どうするか

太陽の影は、<strong>カスケード</strong>（[CSM](../cascaded.md)）で、<strong>カメラの近く</strong>を、覆います。遠く（数百メートル〜数キロ）まで、シャドウ マップを、伸ばすと、1 画素が、巨大になり、影が、ぼやけます。一方、遠景に、影が、全く無いと、山、建物、木が、平らに見え、距離感が、失われます。

| 距離 | 影の、必要性 |
| --- | --- |
| 近景（〜50 m） | 細かい影（キャラクター、物） |
| 中景（50〜300 m） | 建物、木の、影。形が、分かる程度 |
| 遠景（300 m〜） | 山、大きな建物の、大きな影。細部は、不要 |
| 超遠景（数 km） | 地形の、起伏（山の影が、谷に、落ちる） |

## 方法 1：カスケードを、遠くまで、伸ばす

最も、単純な、方法です。<strong>最後のカスケード</strong>を、<strong>遠くまで</strong>、覆います。

| 項目 | 内容 |
| --- | --- |
| 長所 | 仕組みが、統一される。特別な、処理が、不要 |
| 短所 | 遠くの、カスケードは、1 画素が、数メートルになり、ぼやけた影。描画範囲が、広く、コストが、高い（遠くの物も、シャドウ パスで、描く） |

<strong>遠くのカスケードは、更新を、間引く</strong>（数フレームに 1 回）ことで、コストを、抑えられます（[CSM](../cascaded.md)）。

## 方法 2：遠景用に、事前計算した、影

<strong>動かない、遠景</strong>（山、大きな建物）の影は、<strong>事前に、計算して</strong>、テクスチャに焼いておきます。

| 方式 | 内容 |
| --- | --- |
| ベイクした、シャドウ マップ | 遠景の、静的な物だけを、高解像度、広範囲の、シャドウ マップに、あらかじめ描いて保存。太陽の、位置ごとに、複数枚を、用意し、時間帯で、補間 |
| ライトマップ | 地形・建物の、影を、ライトマップに、焼き込む（[Lightmaps](../../gi/lightmaps/index.md)）。太陽が、動かない場面に、向く |
| 地形の、シャドウ（高さマップから） | 地形の、高さマップから、太陽の方向に、レイマーチして、影を、事前に、計算（[Heightmaps and Meshes](../../terrain/heightmap-mesh/index.md)）。山の影が、安く作れる |

### 地形の、影を、高さマップから

<strong>高さマップ</strong>を、太陽の方向に、<strong>走査</strong>すると、各点が、影かを、事前に、判定できます。

```hlsl
// 高さマップを、太陽の方向に、レイマーチして、影を求める（計算シェーダー、事前計算、または、毎フレーム）。
float TerrainShadow(float2 xz, float h, float3 sun_dir_to_light) {
  const int kSteps = 128;
  float2 step_xz = normalize(sun_dir_to_light.xz) * g_step_length;
  float rise = sun_dir_to_light.y / max(length(sun_dir_to_light.xz), 1e-4);   // 水平 1 あたりの、上昇
  float2 p = xz;
  float ray_h = h;
  for (int i = 0; i < kSteps; ++i) {
    p += step_xz;
    ray_h += rise * g_step_length;
    float terrain_h = SampleHeight(p);
    if (terrain_h > ray_h) return 0.0;               // 地形が、レイより高い → 影
  }
  return 1.0;
}
```

<strong>高さマップの、レイマーチ</strong>は、<strong>簡単で、広い範囲</strong>を、安く、扱えます。太陽が、動く（時間帯）ので、毎フレーム、または、数フレームに 1 回、低解像度で、再計算する場合もあります。

## 方法 3：距離場（SDF）の影

<strong>メッシュの、距離場</strong>（各点から、最も近い面までの、距離）を、<strong>事前に</strong>作り、レイマーチで、柔らかい影を、安く、遠くまで作ります（[Distance Field Shadows](../sdf-shadows.md)）。シャドウ マップを、描かずに、遠景の、静的な影を、作れます。

## 方法 4：フェード（遠くで、影を、消す）

<strong>影を、遠くで、突然、消す</strong>と、<strong>境目が、見えます</strong>。カスケードの、最後で、影を、フェード アウトします。

```hlsl
// 影の有効範囲の、端で、影の強さを、フェードさせる。
float fade = saturate((shadow_distance - view_depth) / fade_range);       // 端で 0、手前で 1
float shadow = lerp(1.0, ShadowFactor(world_pos), fade);                   // フェードの外は、影なし（1.0）
```

| 項目 | 内容 |
| --- | --- |
| フェードの幅 | 最後のカスケードの、10〜20% |
| 遠景の、明るさ | 影が、消えた、遠景は、全体として、少し、明るく見える。遠景の、色（空気遠近法）で、ごまかす |

## 組み合わせ（実際のゲーム）

| 距離 | 方式 |
| --- | --- |
| 〜50 m | カスケード 0〜1（高解像度、毎フレーム） |
| 50〜300 m | カスケード 2〜3（更新を、間引く） |
| 300 m〜2 km | 事前計算（地形の影、ベイクした、建物の影）、または、SDF の影 |
| それ以上 | 影なし。空気遠近法（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)）で、遠景の、雰囲気を作る |

<strong>近くは、動的に、遠くは、事前計算に、切り替える</strong>のが、<strong>大規模な、ゲームの、定番の、構成</strong>です。切り替えの、境目は、フェードで、なめらかに、つなぎます。

## よくあるミス

??? failure "シャドウ マップの最大距離で、影が急に消える"
    <strong>最大距離の手前から、滑らかにフェード</strong>させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 遠景は別の方法で影を表す
    - [x] 雲の影・距離フェードが定番

## 参考

- Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007
- Engel, "Cascaded Shadow Maps", ShaderX5, 2006
- Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Special Cases](index.md)
- [Cascaded Shadow Maps (CSM)](../cascaded.md)
- [Clouds](../../atmosphere/clouds/index.md)
