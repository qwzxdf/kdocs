---
title: Using the Sky for Lighting
tags:
  - 描画
---

# Using the Sky for Lighting

<strong>空はシーンを照らす光源でもあります</strong>。空の色を環境マップ（IBL）に焼いて、拡散・鏡面の環境光に使うと、空と地上の色が自然になじみます。このページでは空のライティングを説明します。

!!! tip "ポイント"
    - 空のキューブマップを作って、環境光に使う。
    - 拡散は SH、鏡面はミップ付きキューブマップ。
    - 時間が変わるたびに、更新する。
    - 1 フレームで少しずつ更新して、コストを分散する。

!!! info "このページを読む前に"
    - [Sky Models](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 空をライティングに使う
<strong>空は大きな光源</strong>でもあります。地面や物は空から環境光を受けます。

| 方法 | 内容 |
| --- | --- |
| キューブマップに焼く | 空を 6 面に描画し、ミップで粗さを作る（IBL）。空が変わったら更新 |
| 球面調和関数（SH） | 空の色を SH（L2 の 9 係数）に投影し、拡散の環境光に使う（[法線とライティング](../../../3d/lighting-normals.md)） |
| 更新の頻度 | 時間変化はゆっくりなので、数秒に 1 回、数フレームかけて更新 |
| 太陽は直接光 | 太陽の寄与は環境マップから除き、平行光源として別に扱う（二重に数えない） |

## 空は光源でもある

空は <strong>見えるだけでなく</strong>、シーン全体を照らす光源です。日陰（太陽の光が当たらない所）が、真っ暗にならないのは空全体が、青い光で照らしているためです。この光を環境光（アンビエント ライト）と呼びます。

| 光 | 内容 |
| --- | --- |
| 太陽の光（直接光） | 1 方向からの、強い光。影を作る |
| 空の光（環境光） | 全方向からの弱い、青い光。影の中を照らす |
| 地面からの反射光 | 地面が、照らされて下から物を照らす光 |

昼の日陰が 青っぽく見えるのは、空の青い光が当たっているためです。

## 環境光をどう表すか

<strong>空の光</strong>を シェーディングに、使うにはあらゆる方向からの光を、物の表面の法線に応じて足し合わせる必要があります。これを直接、計算する（全方向を積分）のは、重いので簡略化した表現を使います。

| 方式 | 内容 | 表現力 | コスト |
| --- | --- | --- | --- |
| 単色（定数） | 1 つの色を全面に、足す | 最低（方向性がない） | 最小 |
| 半球ライト（2 色） | 上は空の色、下は地面の色を法線の上下で補間 | 低（上下だけ） | 小 |
| 球面調和関数（SH） | 全方向の光を、9 個の係数（3 次）に圧縮 | 中（ゆるやかな、方向依存） | 小 |
| キューブマップ（IBL） | 環境マップを、ぼかして法線で引く | 高 | 中 |

## 半球ライト

最も <strong>簡単で効果が大きい</strong>方法です。法線が上を向く面は空の色、下を向く面は地面の色で照らします。

```hlsl
// 半球ライト: 法線の上下で、空の色と、地面の色を、補間する。
float3 HemisphereAmbient(float3 normal, float3 sky_color, float3 ground_color) {
  float up = normal.y * 0.5 + 0.5;                      // 0（真下）〜 1（真上）
  return lerp(ground_color, sky_color, up);
}
float3 ambient = albedo * HemisphereAmbient(N, g_sky_ambient, g_ground_ambient);
```

`normal.y * 0.5 + 0.5` で 法線の上下を 0〜1 に直して、補間の重みにします。真上を向く面は空の色、横は中間、真下は地面の色になります。物の上面が青く下面が地面の色になり、立体感が出ます。

## 球面調和関数（SH）

<strong>空全体の光の分布</strong>を 少数の係数で、近似する方法です（Ramamoorthi と Hanrahan、2001）。3 次の SH（9 個の係数 × RGB）で、ゆるやかな環境光（拡散反射）をほぼ正確に、表せます。

```hlsl
// 3 次の SH（9 係数）で、法線方向の、拡散な、環境光（放射照度）を、求める。
float3 EvaluateSH9Irradiance(float3 sh[9], float3 n) {
  // 論文（Ramamoorthi と Hanrahan 2001）の、放射照度の、式（cosine lobe を、畳み込んだ係数を、使う）。
  const float c1 = 0.429043, c2 = 0.511664, c3 = 0.743125, c4 = 0.886227, c5 = 0.247708;
  return c1 * sh[8] * (n.x * n.x - n.y * n.y) + c3 * sh[6] * n.z * n.z + c4 * sh[0] - c5 * sh[6]
       + 2.0 * c1 * (sh[4] * n.x * n.y + sh[7] * n.x * n.z + sh[5] * n.y * n.z)
       + 2.0 * c2 * (sh[3] * n.x + sh[1] * n.y + sh[2] * n.z);
}
```

9 個の係数を 定数バッファに持ち、シェーダーが法線から環境光を、計算します。キューブマップを引くよりはるかに軽く、方向依存の環境光が得られます。SH の詳細は[Spherical Harmonics (SH)](../../gi/theory/spherical-harmonics.md) を、参照してください。

### 空から SH を作る

空をキューブマップに描き（大気散乱の結果）、キューブマップを SH の係数に、投影します（毎フレーム、または空が変わったとき）。

```text
① 空を、キューブマップ（32×32×6 程度の、小さな解像度）に、描く
② キューブマップの、各画素に、SH の、基底関数を掛けて、全画素で、合計する → 9 係数 × RGB
③ 係数を、定数バッファへ
```

```hlsl
// 計算シェーダー: キューブマップの 1 面を、SH の係数に、投影する（概略）。
// 各画素の、方向 d と、立体角 dΩ を求めて、基底関数 Y_lm(d) を、掛けて、合計する。
float3 sky = g_sky_cube.SampleLevel(g_linear_clamp, d, 0).rgb;
sh_coeff[0] += sky * 0.282095 * d_omega;                           // Y_00
sh_coeff[1] += sky * 0.488603 * d.y * d_omega;                     // Y_1-1
sh_coeff[2] += sky * 0.488603 * d.z * d_omega;                     // Y_10
sh_coeff[3] += sky * 0.488603 * d.x * d_omega;                     // Y_11
// ... Y_2m（5 個）も同様 ...
```

小さなキューブマップで 十分です（環境光は、ゆるやかに変わるため）。

## 鏡面反射の環境光（IBL）

<strong>光沢のある面</strong>（金属、水面）は 空の細かい景色を、映します。環境マップ（キューブマップ）を、反射ベクトルで引き粗さに応じて、ぼかしたものを使います（[Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md)）。

| 反射 | 環境光の表現 |
| --- | --- |
| 拡散（ざらざらの面） | SH、またはぼかしたキューブマップ（法線で引く） |
| 鏡面（つるつるの面） | 環境マップ（反射ベクトルで引く）。粗さに応じてミップを選ぶ |

## 空が変わったら環境光も変える

<strong>時刻が進む</strong>（空の色が変わる）、天候が変わると環境光も更新する必要があります。

| 更新の頻度 | 内容 |
| --- | --- |
| 毎フレーム | 小さなキューブマップ（32×32）に、空を描き SH を再計算。軽い |
| 数フレームに 1 回 | 鏡面用の大きな、キューブマップ（128×128、ミップつき）を更新。1 フレームに 1 面ずつなど、分割して更新 |
| 時刻のキーフレームごと | 事前に焼いた、環境マップを補間（固定の時間帯のみ） |

空の更新が遅れると 空は、夕焼けなのに環境光は昼の色、というずれが出ます。少なくとも拡散用の SH は毎フレーム、更新しておくとずれが目立ちません。

## よくあるミス

??? failure "時間が変わっても、地上の明るさが変わらない"
    <strong>環境マップを空に合わせて更新</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空を環境マップにして、光源に使う

## 参考

- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001（球面調和関数による、環境光）
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Karis, "Real Shading in Unreal Engine 4", SIGGRAPH 2013, Physically Based Shading in Theory and Practice（split-sum 近似による、IBL）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Sky Models](index.md)
- [Reflection Probes](../../reflections/probes/index.md)
- [GI Theory](../../gi/theory/index.md)
