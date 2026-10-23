---
title: Bruneton Precomputed Scattering
tags:
  - 描画
---

# Bruneton Precomputed Scattering

<strong>Bruneton の手法は、散乱の結果を高さ・視線の角度・太陽の角度の 4 次元のテーブルに、事前計算しておく</strong>ものです。実行時はテーブルを引くだけで、高品質ですがメモリが大きいです。このページでは Bruneton の事前計算を説明します。

!!! tip "ポイント"
    - 4D のテーブル（高さ・視線・太陽・太陽と視線）を事前計算。
    - 実行時はテーブルを読むだけ。
    - 品質が高い。メモリが大きい。
    - 大気の設定を変えると、再計算が必要。

## Bruneton の事前計算
<strong>Bruneton & Neyret（2008）</strong>は、単散乱・多重散乱をすべて 4D のテーブルに事前計算し、実行時は表引きで空を描きます。

| 項目 | 内容 |
| --- | --- |
| 4 つの次元 | 観測者の高さ・視線の天頂角・太陽の天頂角・視線と太陽の方位角差 |
| 3D テクスチャに詰める | 4D を 3D テクスチャに展開（方位角を横に並べる） |
| 利点 | 実行時は数回のサンプルだけ。多重散乱込みで正確 |
| 欠点 | 事前計算が重い。時刻や大気の組成を変えると計算し直し（太陽の位置は表の次元にあるので動かせるが、大気の密度は固定） |
| 用途 | 地上〜宇宙まで、大気の組成が固定のゲーム |

### 原典と仕組み

原典は Bruneton と Neyret の論文 "Precomputed Atmospheric Scattering"（Eurographics Symposium on Rendering 2008）です。同じ著者による 2017 年の "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models" に、改良された実装と他のモデルとの比較が載っています。

この方式の中心は「散乱を次数ごとに事前計算して、足し合わせる」ことです。まず 1 次散乱（光が 1 回だけ散乱する）を、4D のテーブルとして計算します。次に、このテーブルの値を光源とみなして 2 次散乱を計算し、テーブルに足します。これを何次か繰り返すと多重散乱を含んだテーブルが完成します。実行時は視点の高さ・視線の向き・太陽の角度から、テーブルを引くだけで多重散乱込みの空の色が得られます。

## 考え方：散乱を丸ごと事前計算する

Bruneton と Neyret（2008）の方式は、<strong>大気の散乱の積分をすべて事前に、計算してテクスチャに保存</strong>します。実行時はテクスチャを引くだけです。多重散乱も事前計算の中で正確に、反復して含められます。

| | Bruneton（2008） | Hillaire（2020） |
| --- | --- | --- |
| 事前計算 | 非常に大きい（散乱の、4 次元のテクスチャ。数秒〜数十秒） | 小さい（透過率と、多重散乱の LUT のみ） |
| 実行時 | テクスチャを、引く（安い） | LUT を、毎フレーム、更新（安いが計算がある） |
| 多重散乱 | 正確（反復計算） | 近似（等方性の仮定） |
| 大気の変更 | 事前計算を、やり直し（重い）。動的な天候に不向き | リアルタイムに、対応 |
| 太陽の位置 | テクスチャの軸として、持つ（変化に対応） | LUT に、太陽の角度を軸として持つ |
| 精度 | 高い（参照用に、使える） | 十分（見た目を、重視） |

## 散乱テクスチャ

Bruneton の方式の核心は、<strong>大気の散乱を 4 つの変数</strong>の、関数として テクスチャに保存することです。

```text
S(r, μ, μ_s, ν)        r: 高度、μ: 視線の天頂角の cos、μ_s: 太陽の天頂角の cos、ν: 視線と太陽の、間の角度の cos
```

| 変数 | 意味 |
| --- | --- |
| `r` | カメラの高度（惑星の中心からの、距離） |
| `μ` | 視線の天頂角の cos |
| `μ_s` | 太陽の天頂角の cos |
| `ν` | 視線と太陽の間の、角度の cos（位相関数がこれに、依存する） |

4 次元は 3D テクスチャに、詰めて保存します（例：256×128×32 の 3D テクスチャを、`ν` の分割数だけ横に並べる）。実行時は 4 つの変数からテクスチャ座標を求め、4 次元の線形補間（3D テクスチャの、2 回の読み込みを補間）で散乱を、読み取ります。

```hlsl
// 4 変数 (r, mu, mu_s, nu) から、3D テクスチャの、座標を求め、2 回読んで、nu 方向に、補間する。
float3 GetScattering(float r, float mu, float mu_s, float nu) {
  float4 uvwz = GetScatteringTextureUvwzFromRMuMuSNu(r, mu, mu_s, nu);   // 参照実装の関数
  float tex_coord_x = uvwz.x * (kNuSize - 1);
  float tex_x = floor(tex_coord_x);
  float lerp_factor = tex_coord_x - tex_x;
  float3 uvw0 = float3((tex_x + uvwz.y) / kNuSize, uvwz.z, uvwz.w);
  float3 uvw1 = float3((tex_x + 1.0 + uvwz.y) / kNuSize, uvwz.z, uvwz.w);
  return g_scattering.SampleLevel(g_linear_clamp, uvw0, 0).rgb * (1.0 - lerp_factor)
       + g_scattering.SampleLevel(g_linear_clamp, uvw1, 0).rgb * lerp_factor;
}
```

`GetScatteringTextureUvwzFromRMuMuSNu` は 非線形な座標の割り当てです。地平線の近くを細かく取るための、参照実装（Bruneton の、公開コード）が詳しい式を持っています。自分で導出せず参照実装を移植するのが、現実的です。

## 事前計算の流れ

多重散乱を <strong>正確に</strong>、計算するために 散乱の次数を、反復して足します。

```text
① 透過率テクスチャ T を、計算
② 直接の、地面の、照度（irradiance）を、計算
③ 1 回散乱 S₁ を、計算（レイリーと、ミーを、別々のテクスチャに）
④ 次数 k = 2, 3, 4 について:
     (a) 「前の次数の、散乱光」から、各点の、**入射光の分布**を、計算
     (b) その入射光が、散乱する、**次の次数の、散乱** S_k を、計算
     (c) S_k を、合計 S に、足す
⑤ 完成した、S を、保存
```

3〜4 次まで反復すれば ほぼ、収束します（それ以降の寄与は、小さい）。各次数で計算シェーダー（またはピクセル シェーダー）を数回、実行します。

## 実行時の使い方

```hlsl
// 空の色: 視線の方向から、(r, mu, mu_s, nu) を求め、散乱テクスチャを引くだけ。
float3 SkyRadiance(float3 camera, float3 view_ray, float3 sun_dir) {
  float r = length(camera);
  float rmu = dot(camera, view_ray);
  float mu = rmu / r;
  float mu_s = dot(camera, sun_dir) / r;
  float nu = dot(view_ray, sun_dir);
  float3 rayleigh_scattering = GetScattering(r, mu, mu_s, nu);          // レイリー + 多重散乱
  float3 mie_scattering = GetMieScattering(r, mu, mu_s, nu);            // ミー（別テクスチャ）
  return rayleigh_scattering * RayleighPhase(nu) + mie_scattering * MiePhase(nu, kMieG);
}
```

<strong>レイリーとミーを別々</strong>に保存する理由は、位相関数が違うためです。実行時に位相関数を掛けて足すことで、ミー散乱の `g` を変えたり位相関数を、差し替えられます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 実行時のコストが非常に、小さい（テクスチャの読み込みのみ） |
| 長所 | 多重散乱が正確 |
| 長所 | 参照実装が公開されている（検証に、使える） |
| 短所 | 事前計算が重い（大気の係数を、変えるたびにやり直し）。動的な天候（霞の濃さ時々刻々）に、不向き |
| 短所 | メモリ（4 次元のテクスチャ）が、大きい（数十 MB） |
| 短所 | 実装が複雑（非線形な、座標の割り当て反復計算） |
| 短所 | 雲、地形の影、volumetric な効果との、組み合わせが難しい（空間的に、均一な大気を前提） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| 大気の条件が固定（地球の、標準的な空）、正確さを重視 | Bruneton |
| 動的な天候（霞、湿度の変化）、カメラの高度が大きく変わる（地上から宇宙） | Hillaire（[Hillaire 2020: Four LUTs](hillaire.md)） |
| 参照（正解）として自分の実装を、検証したい | Bruneton の、参照実装 |

## よくあるミス

??? failure "大気のパラメータを変えても、空が変わらない"
    <strong>テーブルを再計算</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 4D テーブルに事前計算して、引くだけ

## 参考

- Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)
- Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models", IEEE Transactions on Visualization and Computer Graphics, Vol. 23, No. 12, 2017
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Nishita, Sirai, Tadamura, Nakamae, "Display of the Earth Taking into Account Atmospheric Scattering", SIGGRAPH 1993

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Hillaire 2020](hillaire.md)
