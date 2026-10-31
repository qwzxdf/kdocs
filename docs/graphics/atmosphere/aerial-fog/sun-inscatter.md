---
title: Sun Inscatter
tags:
  - 描画
---

# Sun Inscatter

<strong>太陽の方向を見るとフォグが明るく黄色っぽく霞みます</strong>。視線と太陽の方向が近いほど、フォグの色を太陽の色に寄せると、自然です。このページでは太陽方向のにじみを説明します。

!!! tip "ポイント"
    - 視線と太陽の内積で、フォグの色を変える。
    - 太陽側は暖色・明るい。
    - 反対側は空の青。
    - ミー散乱の前方散乱に対応。

!!! info "このページを読む前に"
    - [Aerial Perspective and Fog](index.md)（このセクション全体の地図と、読む順番）

## 太陽方向のにじみ
<strong>太陽の方向を見ると霧が明るく・暖色に光ります</strong>（前方散乱）。フォグの色を視線と太陽の角度で変えます。

```hlsl
float sun_amount = saturate(dot(view_dir, sun_dir));
float3 fog_color_dir = lerp(fog_color, sun_fog_color, pow(sun_amount, 8.0));
```

コードの要点です。`pow(.., 8)` は太陽のすぐ周りだけが効くように、角度の広がりを絞ります。より正確にはミー散乱の位相関数である Henyey-Greenstein 関数を使います（[Atmospheric Scattering](../scattering/index.md)）。夕方は太陽側が赤橙に反対側が青紫になります。

### 位相関数による定式化

空気中の粒子（エアロゾル、水滴）による散乱はミー散乱と呼ばれ、強い前方散乱が特徴です。光が進んできた方向のまま散らされやすいので、太陽の方向を見たとき散乱光が最も強くなります。この角度による強さの変化を表す関数が位相関数で、ゲームでは Henyey-Greenstein 関数がよく使われます。

<div class="formula">HG(cosθ, g) = (1 − g²) / (4π · (1 + g² − 2 g cosθ)^(3/2))</div>

g は非対称パラメータ（−1〜1）で、0 なら等方（どの方向にも均等）、1 に近づくほど前方散乱が強くなります。大気中のミー散乱では g が 0.76 前後の値がよく使われます。θ は視線と太陽方向のなす角で、cosθ は `dot(view_dir, sun_dir)` です。上の `pow(sun_amount, 8)` はこの関数を単純化した近似と見なせます。

HG 関数を使うと太陽の方向がどのくらい強く光るかと、広がり方を g で調整できます。これにフォグの色の計算を組み込むと、次のようになります。

```hlsl
float phase = HenyeyGreenstein(dot(view_dir, sun_dir), 0.76);
float3 fog_color_dir = ambient_fog_color + sun_color * phase * sun_inscatter_scale;
```

空の色（青い環境光）に太陽の項を足す形です。足すことで太陽側だけが明るく暖色に染まり、反対側は青いままになります。

## 太陽の方向の霞

太陽の方を見ると <strong>霞が明るく白く</strong>、光ります。霧の中で太陽がまぶしい、あの見た目です。これは霧の粒子（ミー散乱）が光を前方に強く散らすためで太陽の方向の、内向き散乱を足すことで再現できます。

## 内向き散乱を足す

簡易な霧の霧の色に <strong>太陽の方向に応じた項</strong>を足します。

```hlsl
// 太陽に向かって見るほど、霧の色を太陽の色へ寄せる。
float3 FogColorWithSun(float3 view_dir, float3 sun_dir) {
  float sun_amount = saturate(dot(view_dir, sun_dir));             // 視線が太陽の方を向いているほど、1
```

`dot(view_dir, sun_dir)` は 視線と太陽の近さです（1 のとき太陽の、真正面）。

```hlsl
  // 前方散乱の、位相関数（HG）で、太陽の方向を強調する。
  float phase = HenyeyGreenstein(sun_amount, 0.6);                 // g = 0.6: やや、前方に偏る
  float3 sun_glow = g_sun_color * phase;
  return g_fog_color + sun_glow * g_sun_inscatter_strength;
}
```

HG 位相関数（[Phase Functions](../scattering/phase-function.md)）で、太陽の方向に強く偏った、明るさを作ります。`g` が大きい（0.8）ほど太陽の、すぐ近くだけが明るく小さい（0.3）と、広い範囲がぼんやり明るくなります。

## 適用する

```hlsl
float3 ApplyFogWithSun(float3 scene_color, float3 view_dir, float distance) {
  float3 fog_color = FogColorWithSun(view_dir, g_sun_dir);
  float transmittance = exp(-g_fog_density * distance);
  return scene_color * transmittance + fog_color * (1.0 - transmittance);
}
```

<strong>霧の色</strong>が 視線の方向によって、変わるので同じ霧でも太陽の方向と、反対側で色が違う立体的な霧になります。

## 太陽の影を考える

<strong>霧の中</strong>では 太陽の光が遮られた、場所（建物、木の影）は霧も暗くなります。影を考慮しない霧は影の中でも一様に明るいので光の筋（ゴッド レイ）が出ません（[God Rays](../god-rays/index.md)）。

| 方式 | 影の扱い |
| --- | --- |
| この方式（霧の色に太陽を足す） | 影を無視（全体が一様） |
| ボリューム フォグ（froxel） | シャドウ マップを引いて、影の中は暗い（[Volumetric Fog](../volumetric-fog/index.md)） |
| ゴッド レイ（放射状ブラー、レイマーチ） | 影の有無で筋を作る（[God Rays](../god-rays/index.md)） |

簡単な霧に太陽を足す方法は 影を無視する代わりに軽いので遠景の霞に向いています。近景の影つきの霧はボリュームで、作ります。

## 物理ベースでは自動

[Physically Based Aerial Perspective](physical.md) の、<strong>LUT</strong> は 太陽の方向による、内向き散乱を最初から含んでいます（ミー散乱の、位相関数を積分に含めているため）。LUT を使うならこの項を手で、足す必要はありません。

## よくあるミス

??? failure "太陽の方向でも、フォグが青いまま"
    <strong>太陽方向の色</strong>を足す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 太陽の方向で、フォグの色を変える

## 参考

- Henyey, Greenstein, "Diffuse Radiation in the Galaxy", Astrophysical Journal, Vol. 93, 1941
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Aerial Perspective and Fog](index.md)
- [Phase Functions](../scattering/phase-function.md)
