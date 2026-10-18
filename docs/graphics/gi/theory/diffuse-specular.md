---
title: Diffuse and Specular
tags:
  - 描画
---

# Diffuse and Specular

<strong>間接光は、「拡散（あらゆる方向へ散る）」と「鏡面（特定の方向へ反射する）」の 2 つに分けて考える</strong>と<strong>扱いやすくなります</strong>。拡散の間接光は、なめらかなので安く近似でき、鏡面の間接光は、鋭く、別の手法（反射）で扱います。このページでは、2 つの違いと、手法の分担を説明します。

!!! tip "ポイント"
    - 拡散の間接光 ＝ 低周波。なめらか。
    - 鏡面の間接光 ＝ 高周波。鋭い（[Reflections](../../reflections/index.md)の領域）。
    - GI と呼ぶ時は、主に拡散の間接光を指す。
    - 拡散と鏡面で、別の手法を組み合わせるのが普通。

## 拡散と鏡面

BRDF を拡散と鏡面に分けて考えると、間接光の性質がまったく違うことが分かります。

### 拡散の間接光

ランバート面の BRDF は、ほぼ一定値（albedo / π）です。つまり、入ってくる光がどの方向からでも、同じように全方向へ散らばります。結果として、見る方向に依存せず、見た目の色は法線と周りの光だけで決まります。さらに、前のページで見たように、半球の積分は余弦で畳み込まれて<strong>低周波</strong>になります。粗い情報（プローブ 1 個の SH 係数など）で十分です。

### 鏡面の間接光

鏡面反射の BRDF は、反射方向のまわりに鋭いローブ（山）を持ちます。粗さが小さい（つるつるな）ほど山は鋭く、粗いほど広がります。入ってくる光のうち、反射方向の近くの光だけが効くので、周りの景色が<strong>はっきりと映り込みます</strong>。そして、見る方向を変えれば映り込む場所が変わるので、視線に依存します。情報は<strong>高周波</strong>で、細かい情報が必要です。

### 手法の分担

この違いから、拡散と鏡面は別々の手法で扱うのが普通です。拡散の間接光は、このセクションのライトマップ・プローブ・SSGI・ボクセル・DDGI などが担当します。鏡面の間接光は、[Reflections](../../reflections/index.md) のセクション（平面反射・反射プローブ・SSR・レイトレ反射）が担当します。同じ「他の面から来る光」でも、保存する情報量の違いが、手法を分けています。

ただし、粗さが大きい鏡面は、拡散に近づきます。粗さが十分に高い（マットな）面の鏡面反射は、広いローブになり、低周波になります。その場合は、拡散の手法と同じデータ（プローブなど）をそのまま使っても、見た目の破綻が小さくなります。そのため、実際のエンジンでは、粗い鏡面の間接光を、GI のプローブに任せ、つるつるな面だけを反射の手法で扱う、という分担もよく見られます。

## 同じ「間接光」でも、拡散と鏡面は、まるで違う

<strong>間接光</strong>（他の面から、反射してきて、届く光）は、<strong>面の、反射の性質</strong>で、見え方が、まったく違います。間接光の、計算を、1 つにまとめるのでなく、拡散と鏡面に、分けて、それぞれに、適した方法を、使います。

| | 拡散（ざらざらの、面の反射） | 鏡面（つるつるの、面の反射） |
| --- | --- | --- |
| 反射の、広がり | 全方向に、均等（ランバート） | 反射方向の、まわりだけ（鋭い、ローブ） |
| 間接光の見え方 | なめらか、低周波 | 鋭く、周りの景色が、映る、高周波 |
| 視点への、依存 | なし（どこから見ても、同じ明るさ） | あり（見る角度で、変わる） |
| 必要な、情報 | 法線の向きごとに、1 つの値（放射照度） | 反射方向の、景色（細かい、環境マップ） |
| 適した方法 | ライトマップ、プローブ、SH、SSGI、DDGI、Lumen | 反射プローブ、SSR、平面反射、レイトレーシング（[Reflections](../../reflections/index.md)） |

## 拡散：どこから来た光でも、同じ

ランバート面の、<strong>BRDF</strong> は、<strong>`albedo / π`</strong>（定数）です。入ってくる光が、どの方向から来ても、出ていく光は、同じ配分で、全方向に、散ります。結果、周りの景色の、細かい模様は、平均されて、ぼんやり、なめらかな明るさになります（[Irradiance](irradiance.md)）。拡散の間接光は、低い解像度の、データ（SH、小さなキューブマップ、ライトマップ）で、十分です。

## 鏡面：反射方向の、景色が、映る

<strong>鏡面反射</strong>の、BRDF は、<strong>反射方向</strong>（視線の、鏡像）の、周りに、鋭い、山（ローブ）を、持ちます。粗さが、小さい（つるつる）ほど、山が、細く、ほぼ、1 方向の、景色を、そのまま、映します。周りの景色の、細かい、模様（窓、雲、建物）が、くっきり、映ります。鏡面の間接光には、高解像度の、環境の、情報が、必要です。

```text
粗さ 0.05（つるつる）:  反射方向の、ほぼ 1 点の景色  → くっきり映る
粗さ 0.5 （ざらざら）:  広い範囲の景色が、混ざる   → ぼんやり映る
粗さ 1.0 （マット）  :  全方向から、混ざる        → 拡散とほぼ同じ
```

## 描画での、合成

<strong>PBR</strong>（物理ベース レンダリング）では、<strong>間接光を、拡散と鏡面に、分けて</strong>、足し合わせます。

```hlsl
// 間接光の、合成（IBL: 環境マップによる、ライティング）。
float3 N = normalize(input.world_normal);
float3 V = normalize(g_camera_position - input.world_position);
float3 R = reflect(-V, N);
float n_dot_v = saturate(dot(N, V));
```

<strong>法線 `N`</strong>（拡散で使う）、<strong>視線 `V`</strong>、反射ベクトル `R`（鏡面で使う）を、用意します。

```hlsl
// 拡散の間接光: 放射照度（SH、または、畳み込んだキューブマップ）× albedo。
float3 irradiance = IrradianceFromSH9(g_sh, N);                      // 法線で、放射照度を求める
float3 diffuse_ibl = albedo / 3.14159265 * irradiance;
```

<strong>拡散</strong>は、<strong>法線だけ</strong>で、決まる、放射照度（[Irradiance](irradiance.md)）から、求めます。

```hlsl
// 鏡面の間接光: 反射方向の、環境マップを、粗さに応じた、ぼかしで読み、split-sum の係数を掛ける。
float mip = roughness * (kEnvMipCount - 1);
float3 prefiltered = g_env_specular.SampleLevel(g_linear_clamp, R, mip);          // 粗さに応じて、ぼかした、環境マップ
float2 brdf = g_brdf_lut.SampleLevel(g_linear_clamp, float2(n_dot_v, roughness), 0).xy;   // split-sum の、2 つの係数
float3 specular_ibl = prefiltered * (f0 * brdf.x + brdf.y);
```

<strong>鏡面</strong>は、<strong>反射ベクトル `R`</strong> で、環境マップを、読み、粗さに応じて、ぼかした（ミップを、選ぶ）ものを、使います。split-sum 近似（Karis、2013）で、視線と粗さに、依存する、BRDF の、積分を、2 つの係数（`brdf.x`、`brdf.y`）に、事前に、まとめています（[Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md)）。

```hlsl
// 合成: エネルギー保存のため、鏡面で反射した割合（フレネル F）は、拡散から引く。金属は、拡散がない。
float3 F = FresnelSchlickRoughness(n_dot_v, f0, roughness);
float3 kd = (1.0 - F) * (1.0 - metallic);
float3 indirect = kd * diffuse_ibl + specular_ibl;
```

<strong>入ってきた光</strong>は、<strong>反射する分</strong>（フレネル `F`）と、中へ、入って、散乱する分（拡散）に、分かれるので、拡散の、割合から、`F` を、引きます（エネルギー保存）。金属は、中へ入った光を、吸収し、拡散が、無いので、`(1 − metallic)` を、掛けて、0 にします（[PBR](../../../3d/pbr.md)）。

## 混在させる場合

<strong>1 つの手法</strong>で、拡散と鏡面の、<strong>両方</strong>を、まかなえる場合が、あります。

| 手法 | 拡散 | 鏡面 |
| --- | --- | --- |
| ライトマップ | ○（焼き込み） | ×（鏡面は、別途、反射プローブ） |
| プローブ GI（SH） | ○ | ×（SH は、鏡面に、不向き） |
| SSGI | ○ | △（粗い鏡面は、近似できる） |
| DDGI | ○ | ×（拡散のみ） |
| レイトレーシング | ○ | ○（両方、1 つの仕組みで） |
| Lumen | ○ | ○（粗い鏡面まで。つるつるの、鏡面は、別の反射） |

## 鏡面の、間接光の、例外

<strong>粗さが、大きい</strong>（マットな）面の、鏡面反射は、<strong>拡散に、近づく</strong>ので、拡散の、手法で、近似することも、できます。粗さが、小さい（つるつる）鏡面は、反射の、手法（SSR、プローブ、レイトレーシング）が、必要です。境目は、粗さ 0.5〜0.6 あたりで、手法を、切り替える（ブレンドする）のが、一般的です。

## よくあるミス

??? failure "鏡面の反射も、GI の手法で出そうとして、ぼやける"
    <strong>鏡面は、反射の手法（SSR・プローブ・RT）で扱う</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 拡散は低周波、鏡面は高周波
    - [x] 手法を分担する

## 参考

- Karis, "Real Shading in Unreal Engine 4", SIGGRAPH 2013, Physically Based Shading in Theory and Practice
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014
- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001（放射照度を 9 個の SH 係数で表す）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、放射照度、SH の章）

## 関連ページ

- [GI Theory](index.md)
- [Irradiance](irradiance.md)
- [Reflections](../../reflections/index.md)
