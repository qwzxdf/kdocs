---
title: Distant Shadows
tags:
  - 描画
---

# Distant Shadows

<strong>遠くまでシャドウ マップを広げる</strong>と解像度が足りず、コストも大きいので遠景は別の方法で影を表します。雲の影（地面を流れる雲の影）や、遠くの山の影など大きなスケールの影は、事前計算や専用の簡易な方式で表現します。このページでは遠景の影の扱い・雲の影・距離によるフェードを説明します。

!!! tip "ポイント"
    - シャドウ マップは、距離とともに解像度が落ちる。遠景は別の仕組み。
    - 雲の影：雲の密度テクスチャを、太陽方向から地面へ投影して暗くする。
    - 距離フェード：シャドウ マップの最大距離で、影を滑らかに消す。
    - 遠くの影はベイク・距離場・簡易方式。

## 遠景の影
<strong>カスケードの最大距離</strong>を超えた先は、影がなくなります。遠景の山・建物の大きな影をどう扱うかです。

| 方法 | 内容 |
| --- | --- |
| フェードアウト | 最大距離で影を徐々に消す（[Cascaded Shadow Maps (CSM)](../cascaded.md)） |
| ベイク済みの影 | 静的な遠景はライトマップ・影のマスクにベイク |
| 距離場の影 | 遠景に距離場の影を使う（[Distance Field Shadows](../sdf-shadows.md)） |
| 大きな最後のカスケード | 最後のカスケードを非常に大きく（粗いが遠くの大きな影は捉える） |
| 雲の影 | 雲のテクスチャを地面に投影して、大規模な移動する影を安く表現 |

### 雲の影

雲のアルファ テクスチャを、太陽の方向から地面に投影し、ライティングに乗算します。時間でスクロールさせれば雲の影がゆっくり動く様子になります。

```hlsl
float2 cloud_uv = world_pos.xz * cloud_scale + wind * time;
float cloud_shadow = lerp(1.0, cloud_tex.Sample(linear_sampler, cloud_uv).r, cloud_strength);
lit *= cloud_shadow;
```

## 問題：遠くの影はどうするか

太陽の影は <strong>カスケード</strong>（[CSM](../cascaded.md)）で、カメラの近くを覆います。遠く（数百メートル〜数キロ）まで、シャドウ マップを伸ばすと 1 画素が、巨大になり影がぼやけます。一方、遠景に影が全く無いと山、建物、木が平らに見え距離感が失われます。

| 距離 | 影の必要性 |
| --- | --- |
| 近景（〜50 m） | 細かい影（キャラクター、物） |
| 中景（50〜300 m） | 建物、木の影。形が分かる程度 |
| 遠景（300 m〜） | 山、大きな建物の大きな影。細部は不要 |
| 超遠景（数 km） | 地形の、起伏（山の影が谷に落ちる） |

## 方法 1：カスケードを、遠くまで伸ばす

最も単純な方法です。<strong>最後のカスケード</strong>を 遠くまで、覆います。

| 項目 | 内容 |
| --- | --- |
| 長所 | 仕組みが統一される。特別な処理が不要 |
| 短所 | 遠くのカスケードは、1 画素が数メートルになりぼやけた影。描画範囲が広くコストが高い（遠くの物も、シャドウ パスで描く） |

遠くのカスケードは更新を間引く（数フレームに 1 回）ことで、コストを抑えられます（[CSM](../cascaded.md)）。

## 方法 2：遠景用に事前計算した影

<strong>動かない遠景</strong>（山、大きな建物）の影は 事前に計算して、テクスチャに焼いておきます。

| 方式 | 内容 |
| --- | --- |
| ベイクしたシャドウ マップ | 遠景の、静的な物だけを高解像度、広範囲のシャドウ マップにあらかじめ描いて保存。太陽の位置ごとに複数枚を用意し、時間帯で補間 |
| ライトマップ | 地形・建物の影を、ライトマップに焼き込む（[Lightmaps](../../gi/lightmaps/index.md)）。太陽が動かない場面に向く |
| 地形のシャドウ（高さマップから） | 地形の、高さマップから太陽の方向にレイマーチして影を事前に、計算（[Heightmaps and Meshes](../../terrain/heightmap-mesh/index.md)）。山の影が安く作れる |

### 地形の影を高さマップから

高さマップを太陽の方向に、走査すると各点が影かを事前に、判定できます。

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

高さマップのレイマーチは、簡単で広い範囲を安く扱えます。太陽が動く（時間帯）ので毎フレーム、または数フレームに 1 回、低解像度で再計算する場合もあります。

## 方法 3：距離場（SDF）の影

<strong>メッシュの距離場</strong>（各点から、最も近い面までの距離）を 事前に作り、レイマーチで柔らかい影を安く、遠くまで作ります（[Distance Field Shadows](../sdf-shadows.md)）。シャドウ マップを描かずに遠景の、静的な影を作れます。

## 方法 4：フェード（遠くで影を消す）

<strong>影を遠くで突然、消す</strong>と 境目が見えます。カスケードの最後で影をフェード アウトします。

```hlsl
// 影の有効範囲の、端で、影の強さを、フェードさせる。
float fade = saturate((shadow_distance - view_depth) / fade_range);       // 端で 0、手前で 1
float shadow = lerp(1.0, ShadowFactor(world_pos), fade);                   // フェードの外は、影なし（1.0）
```

| 項目 | 内容 |
| --- | --- |
| フェードの幅 | 最後のカスケードの、10〜20% |
| 遠景の明るさ | 影が消えた遠景は、全体として少し明るく見える。遠景の色（空気遠近法）でごまかす |

## 組み合わせ（実際のゲーム）

| 距離 | 方式 |
| --- | --- |
| 〜50 m | カスケード 0〜1（高解像度、毎フレーム） |
| 50〜300 m | カスケード 2〜3（更新を、間引く） |
| 300 m〜2 km | 事前計算（地形の影、ベイクした建物の影）、または SDF の影 |
| それ以上 | 影なし。空気遠近法（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)）で遠景の、雰囲気を作る |

<strong>近くは動的に遠くは事前計算に、切り替える</strong>のが 大規模なゲームの定番の、構成です。切り替えの境目はフェードでなめらかに、つなぎます。

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
