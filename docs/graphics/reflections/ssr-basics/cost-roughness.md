---
title: Cost and Roughness
tags:
  - 描画
---

# Cost and Roughness

<strong>SSR はレイを画素ごとに進めるので、解像度でコストが大きく変わります</strong>。半解像度でトレースしてフル解像度に戻すのが一般的です。粗い面の反射は本来、ぼやけますが簡易的にぼかしで近似できます。このページでは解像度とコストの関係・粗さの簡易対応を説明します。

!!! tip "ポイント"
    - コストは画素数 × ステップ数。
    - 半解像度でトレースすると、およそ 1/4。
    - 粗い面は反射もぼやける。簡易には結果をぼかす（ミップを選ぶ）。
    - 本格的な粗さは[Stochastic SSR](../ssr-stochastic.md)で扱う。

!!! info "このページを読む前に"
    - [SSR Basics](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 解像度とコスト
| 方式 | 内容 |
| --- | --- |
| フル解像度 | 高品質。重い |
| 半分の解像度 | レイを半分の解像度で飛ばし、拡大（バイラテラル）。4 分の 1 のコスト |
| ステップ数の上限 | 32〜64 程度。1 ステップが深度のテクスチャ読み込み 1 回 |
| 歩幅 stride | 大きいと速い（薄い物を飛ぶ）。ジッターで縞を分散 |
| 粗い面はレイを減らす | 粗さがしきい値以上の画素は、SSR をやめる（プローブへ） |
| マスク | 反射しない面（粗さ 1・非金属で粗い）を、ステンシルやタイル分類で除外 |

## 粗さへの簡易対応
<strong>粗い面</strong>の反射は ぼやけるべきです。簡易的には次のようにします。

簡易的な粗さへの対応は 3 通りあります。色のミップ（ぼかしピラミッド）は、シーン色のミップを作り粗さまたはレイの長さに応じてミップを選びます。距離が遠く粗いほどぼけた色になります。コーン トレース風の方法は、レイの距離に応じて反射の円錐が広がることを、ミップの選択で表します。ぼかしは反射の画像全体を粗さでぼかす方法ですが、境界ににじみが出ます。

確率的な方式（[Stochastic SSR](../ssr-stochastic.md)）は、GGX の分布からレイをサンプルして、ぼけを物理的に正しく得ます。

## 粗さと SSR の関係

<strong>SSR のレイ</strong>は 反射方向に、1 本飛ばして当たった色を読みます。これは粗さ 0（完全な鏡）の、反射です。粗い面は反射がぼやけ（周りの、広い範囲が混ざる）ので 1 本の、レイでは足りません。

| 粗さ | 反射の見え方 | SSR で、必要なこと |
| --- | --- | --- |
| 0（鏡） | くっきり | レイ 1 本で、よい |
| 0.2〜0.4 | 少し、ぼやける | ぼかしまたは複数のレイ |
| 0.5〜0.7 | かなり、ぼやける | 多数のレイ、または大きなぼかし |
| 0.8 以上 | ほぼ拡散（景色が、判別できない） | SSR はやめて、反射プローブ（ミップでぼかした）に、任せる |

## 方法 1：反射をぼかす

<strong>くっきり 1 本のレイ</strong>で 反射を取り、粗さに応じてぼかします。安いが偽物（距離によるぼけの変化が、出ない）です。

```hlsl
// SSR の結果（反射色）を、粗さに応じて、ぼかす。画面（色）のミップマップを、使う。
float mip = roughness * g_max_blur_mip;                                      // 粗さ → ミップ（粗いほど、ぼやける）
float3 reflected = g_lit_scene_mips.SampleLevel(g_linear_clamp, hit_uv, mip).rgb;
```

当たった画素の位置で 画面の色の、ミップマップを読む（粗いほど、高いミップ）と当たった点の周りがぼけて反射が、ぼやけます。1 回のテクスチャ読み込みで、安いです。

### 距離によるぼけの変化

現実の反射は 反射する物が、遠いほどぼけが大きくなります（反射の円錐が、広がるため）。レイの長さに応じてミップを上げるとこれを、近似できます。

```hlsl
float cone_radius = ray_length * tan(roughness_to_cone_angle(roughness));    // レイの長さに、比例して、円錐が広がる
float mip = log2(cone_radius * g_screen_size_pixels / pixel_world_size);      // 円錐の広がりに合う、ミップ
```

レイが長い（遠くの物が映る）ほど、ぼけが大きくなります。コーン トレーシングの考え方です（[Hi-Z SSR](../ssr-hiz.md) の、Uludag の方法）。

## 方法 2：確率的に複数のレイ

<strong>粗さに応じた分布</strong>で 反射方向を、ランダムに（GGX の重点サンプリング）、数本飛ばし平均します（確率的 SSR、Stachowiak と Uludag、2015）。本物のぼけが得られますがノイズが、出るので時間蓄積と空間フィルタが、必要です（[Stochastic SSR](../ssr-stochastic.md)）。

```hlsl
// 粗さに応じて、反射方向を、GGX の分布で、ランダムに、ずらす（重点サンプリング）。
float3 H = LocalToWorld(ImportanceSampleGGX(Random2(pixel, g_frame_index), roughness), normal_vs);
float3 R = reflect(view_dir_vs, H);                                           // 法線を、H に、ずらして、反射
```

GGX の分布に従って 法線を、ずらしたもの（ハーフ ベクトル `H`）で、反射させます。粗い面ほど大きくずれるので周りの、広い範囲をサンプルします。

## コストの内訳

| 処理 | コスト（1080p、目安） |
| --- | --- |
| レイマーチ（画素ごと 16〜32 ステップ） | 0.5〜2 ms（最大の、コスト） |
| 反射色の読み込み + ぼかし | 0.1〜0.3 ms |
| 時間蓄積・空間フィルタ（確率的 SSR の場合） | 0.3〜1 ms |
| プローブとの合成 | 0.1 ms |

<strong>SSR のコスト</strong>の 大部分は、レイマーチです。

## コストを下げる

| 工夫 | 効果 |
| --- | --- |
| 半分の解像度でトレースして、アップサンプル | 約 1/4 のコスト。反射が少しぼける |
| 粗さが大きい（0.7 以上）画素は、スキップ | 多くの画素をスキップ（プローブに、任せる） |
| 反射しない面（粗さが高い、非金属で反射が弱い）をスキップ | 反射が、見えない画素のレイマーチを省く |
| レイの最大距離を短く | ステップ数が、減る |
| Hi-Z（[Hi-Z SSR](../ssr-hiz.md)） | 同品質で数倍、速い |

```hlsl
// 反射が、ほぼ見えない画素は、レイマーチを、スキップする。
float fresnel_scale = 0.04 + metallic * 0.96;                                 // 非金属は、約 4% しか、反射しない
if (roughness > 0.7 || fresnel_scale * (1.0 - roughness) < 0.01) return float4(0, 0, 0, 0);   // SSR なし → プローブに、任せる
```

<strong>非金属</strong>（反射率 4%）で、粗い面は反射がほとんど見えません。レイマーチを省いて反射プローブに、任せます。画素の多くをスキップできるので大きな節約に、なります。

## よくあるミス

??? failure "粗い面にも、鏡のようにくっきりした反射が出る"
    <strong>粗さに応じてぼかす</strong>（またはミップを選ぶ）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 半解像度でトレースして、コストを下げる
    - [x] 粗さはぼかしで近似

## 参考

- Stachowiak, Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Frostbite の SSR）
- Uludag, "Hi-Z Screen-Space Cone-Traced Reflections", GPU Pro 5, 2014
- Heitz, "Sampling the GGX Distribution of Visible Normals", Journal of Computer Graphics Techniques, Vol. 7, No. 4, 2018
- Walter, Marschner, Li, Torrance, "Microfacet Models for Refraction through Rough Surfaces", Eurographics Symposium on Rendering 2007
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（反射、IBL の章）

## 関連ページ

- [SSR Basics](index.md)
- [Stochastic SSR](../ssr-stochastic.md)
- [Color Lookup and Fading](color-fade.md)
