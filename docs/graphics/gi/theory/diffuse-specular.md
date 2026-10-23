---
title: Diffuse and Specular
tags:
  - 描画
---

# Diffuse and Specular

<strong>間接光は「拡散（あらゆる方向へ散る）」と「鏡面（特定の方向へ反射する）」の 2 つに分けて考える</strong>と扱いやすくなります。拡散の間接光はなめらかなので安く近似でき、鏡面の間接光は鋭く別の手法（反射）で扱います。このページでは 2 つの違いと、手法の分担を説明します。

!!! tip "ポイント"
    - 拡散の間接光 ＝ 低周波。なめらか。
    - 鏡面の間接光 ＝ 高周波。鋭い（[Reflections](../../reflections/index.md)の領域）。
    - GI と呼ぶ時は、主に拡散の間接光を指す。
    - 拡散と鏡面で別の手法を組み合わせるのが普通。

## 拡散と鏡面

BRDF を拡散と鏡面に分けて考えると、間接光の性質がまったく違うことが分かります。

### 拡散の間接光

ランバート面の BRDF は、ほぼ一定値（albedo / π）です。つまり、入ってくる光がどの方向からでも、同じように全方向へ散らばります。結果として、見る方向に依存せず見た目の色は法線と周りの光だけで決まります。さらに、前のページで見たように半球の積分は余弦で畳み込まれて<strong>低周波</strong>になります。粗い情報（プローブ 1 個の SH 係数など）で十分です。

### 鏡面の間接光

鏡面反射の BRDF は反射方向のまわりに鋭いローブ（山）を持ちます。粗さが小さい（つるつるな）ほど山は鋭く、粗いほど広がります。入ってくる光のうち反射方向の近くの光だけが効くので、周りの景色がはっきりと映り込みます。そして、見る方向を変えれば映り込む場所が変わるので、視線に依存します。情報は高周波で細かい情報が必要です。

### 手法の分担

この違いから拡散と鏡面は別々の手法で扱うのが普通です。拡散の間接光はこのセクションのライトマップ・プローブ・SSGI・ボクセル・DDGI などが担当します。鏡面の間接光は[Reflections](../../reflections/index.md) のセクション（平面反射・反射プローブ・SSR・レイトレ反射）が担当します。同じ「他の面から来る光」でも、保存する情報量の違いが手法を分けています。

ただし、粗さが大きい鏡面は拡散に近づきます。粗さが十分に高い（マットな）面の鏡面反射は、広いローブになり低周波になります。その場合は拡散の手法と同じデータ（プローブなど）をそのまま使っても、見た目の破綻が小さくなります。そのため、実際のエンジンでは粗い鏡面の間接光を、GI のプローブに任せつるつるな面だけを反射の手法で扱う、という分担もよく見られます。

## 同じ「間接光」でも拡散と鏡面は、まるで違う

<strong>間接光</strong>（他の面から反射してきて、届く光）は 面の反射の性質で、見え方がまったく違います。間接光の計算を 1 つにまとめるのでなく、拡散と鏡面に分けてそれぞれに、適した方法を使います。

| | 拡散（ざらざらの面の反射） | 鏡面（つるつるの、面の反射） |
| --- | --- | --- |
| 反射の広がり | 全方向に、均等（ランバート） | 反射方向の、まわりだけ（鋭いローブ） |
| 間接光の見え方 | なめらか、低周波 | 鋭く周りの景色が映る、高周波 |
| 視点への依存 | なし（どこから見ても、同じ明るさ） | あり（見る角度で、変わる） |
| 必要な情報 | 法線の向きごとに、1 つの値（放射照度） | 反射方向の、景色（細かい環境マップ） |
| 適した方法 | ライトマップ、プローブ、SH、SSGI、DDGI、Lumen | 反射プローブ、SSR、平面反射、レイトレーシング（[Reflections](../../reflections/index.md)） |

## 拡散：どこから来た光でも同じ

ランバート面の <strong>BRDF</strong> は、`albedo / π`（定数）です。入ってくる光がどの方向から来ても、出ていく光は同じ配分で全方向に、散ります。結果、周りの景色の細かい模様は平均されて、ぼんやりなめらかな明るさになります（[Irradiance](irradiance.md)）。拡散の間接光は低い解像度のデータ（SH、小さなキューブマップ、ライトマップ）で十分です。

## 鏡面：反射方向の景色が映る

<strong>鏡面反射</strong>の BRDF は 反射方向（視線の、鏡像）の周りに鋭い山（ローブ）を、持ちます。粗さが小さい（つるつる）ほど山が細くほぼ、1 方向の景色をそのまま映します。周りの景色の細かい模様（窓、雲、建物）がくっきり映ります。鏡面の間接光には高解像度の環境の情報が、必要です。

```text
粗さ 0.05（つるつる）:  反射方向の、ほぼ 1 点の景色  → くっきり映る
粗さ 0.5 （ざらざら）:  広い範囲の景色が、混ざる   → ぼんやり映る
粗さ 1.0 （マット）  :  全方向から、混ざる        → 拡散とほぼ同じ
```

## 描画での合成

<strong>PBR</strong>（物理ベース レンダリング）では、間接光を拡散と鏡面に分けて、足し合わせます。

```hlsl
// 間接光の、合成（IBL: 環境マップによる、ライティング）。
float3 N = normalize(input.world_normal);
float3 V = normalize(g_camera_position - input.world_position);
float3 R = reflect(-V, N);
float n_dot_v = saturate(dot(N, V));
```

法線 `N`（拡散で使う）、視線 `V`、反射ベクトル `R`（鏡面で使う）を、用意します。

```hlsl
// 拡散の間接光: 放射照度（SH、または、畳み込んだキューブマップ）× albedo。
float3 irradiance = IrradianceFromSH9(g_sh, N);                      // 法線で、放射照度を求める
float3 diffuse_ibl = albedo / 3.14159265 * irradiance;
```

拡散は 法線だけで決まる、放射照度（[Irradiance](irradiance.md)）から、求めます。

```hlsl
// 鏡面の間接光: 反射方向の、環境マップを、粗さに応じた、ぼかしで読み、split-sum の係数を掛ける。
float mip = roughness * (kEnvMipCount - 1);
float3 prefiltered = g_env_specular.SampleLevel(g_linear_clamp, R, mip);          // 粗さに応じて、ぼかした、環境マップ
float2 brdf = g_brdf_lut.SampleLevel(g_linear_clamp, float2(n_dot_v, roughness), 0).xy;   // split-sum の、2 つの係数
float3 specular_ibl = prefiltered * (f0 * brdf.x + brdf.y);
```

鏡面は 反射ベクトル `R` で、環境マップを読み粗さに応じて、ぼかした（ミップを選ぶ）ものを、使います。split-sum 近似（Karis、2013）で視線と粗さに依存する、BRDF の積分を 2 つの係数（`brdf.x`、`brdf.y`）に事前にまとめています（[Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md)）。

```hlsl
// 合成: エネルギー保存のため、鏡面で反射した割合（フレネル F）は、拡散から引く。金属は、拡散がない。
float3 F = FresnelSchlickRoughness(n_dot_v, f0, roughness);
float3 kd = (1.0 - F) * (1.0 - metallic);
float3 indirect = kd * diffuse_ibl + specular_ibl;
```

入ってきた光は 反射する分（フレネル `F`）と中へ入って、散乱する分（拡散）に分かれるので拡散の、割合から `F` を引きます（エネルギー保存）。金属は中へ入った光を吸収し拡散が、無いので `(1 − metallic)` を掛けて 0 にします（[PBR](../../../3d/pbr.md)）。

## 混在させる場合

<strong>1 つの手法</strong>で拡散と鏡面の、両方をまかなえる場合があります。

| 手法 | 拡散 | 鏡面 |
| --- | --- | --- |
| ライトマップ | ○（焼き込み） | ×（鏡面は別途、反射プローブ） |
| プローブ GI（SH） | ○ | ×（SH は鏡面に、不向き） |
| SSGI | ○ | △（粗い鏡面は、近似できる） |
| DDGI | ○ | ×（拡散のみ） |
| レイトレーシング | ○ | ○（両方、1 つの仕組みで） |
| Lumen | ○ | ○（粗い鏡面まで。つるつるの鏡面は別の反射） |

## 鏡面の間接光の例外

<strong>粗さが大きい</strong>（マットな）面の、鏡面反射は 拡散に近づくので拡散の手法で、近似することもできます。粗さが小さい（つるつる）鏡面は反射の、手法（SSR、プローブ、レイトレーシング）が必要です。境目は粗さ 0.5〜0.6 あたりで手法を、切り替える（ブレンドする）のが、一般的です。

## よくあるミス

??? failure "鏡面の反射も、GI の手法で出そうとしてぼやける"
    <strong>鏡面は反射の手法（SSR・プローブ・RT）で扱う</strong>。

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
