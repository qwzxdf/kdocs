---
title: Comparison with Reflection Probes and Cost
tags:
  - 描画
---

# Comparison with Reflection Probes and Cost

ゲームのシーンに「プローブ」を置くと言うとき 2 種類の別物があります。1 つは動く物体に拡散の間接光を与えるライト プローブ（GI プローブ）で、もう 1 つはつるつるした面に周りの景色を映すための反射プローブです。名前が同じなので混同しやすく、一方で全部をまかなおうとして失敗しがちです。

このページは 2 種類のプローブの違いを保存するものコスト、使い分けの 3 点で並べます。違いの根っこにある拡散は低周波で SH で足り鏡面は高周波で足りないという事実は、数値実験で確かめます。最後に、両方を読んで間接光を作る HLSL を載せます。

!!! tip "ポイント"
    GI プローブは拡散の低周波な光で、SH で保存します。反射プローブは鏡面の高周波な景色で、キューブマップで保存します。両方を併用するのが普通です。GI プローブは小さく軽く動く物体にも使えますが、細かい影は出ません。反射プローブは 1 つが大きいので、数を絞って置きます。

!!! info "このページを読む前に"
    - [Probe GI](index.md)（このセクション全体の地図と読む順番）
    - [Diffuse and Specular](../theory/diffuse-specular.md)（拡散と鏡面の間接光の違い）

## 2 種類のプローブ

次の図は同じ部屋に置いた 2 種類のプローブです。

<svg class="fig flow" viewBox="0 0 680 270" role="img" aria-label="ライト プローブは格子状に密、反射プローブは部屋ごとに疎"><text x="14" y="22" class="fig-title">同じ部屋に、2 種類のプローブ</text><rect x="20" y="44" width="290" height="190" rx="8" fill="none" stroke="#94a3b8" stroke-width="2"/><circle cx="50" cy="76" r="5" fill="#4c8bf5"/><circle cx="50" cy="116" r="5" fill="#4c8bf5"/><circle cx="50" cy="156" r="5" fill="#4c8bf5"/><circle cx="50" cy="196" r="5" fill="#4c8bf5"/><circle cx="96" cy="76" r="5" fill="#4c8bf5"/><circle cx="96" cy="116" r="5" fill="#4c8bf5"/><circle cx="96" cy="156" r="5" fill="#4c8bf5"/><circle cx="96" cy="196" r="5" fill="#4c8bf5"/><circle cx="142" cy="76" r="5" fill="#4c8bf5"/><circle cx="142" cy="116" r="5" fill="#4c8bf5"/><circle cx="142" cy="156" r="5" fill="#4c8bf5"/><circle cx="142" cy="196" r="5" fill="#4c8bf5"/><circle cx="188" cy="76" r="5" fill="#4c8bf5"/><circle cx="188" cy="116" r="5" fill="#4c8bf5"/><circle cx="188" cy="156" r="5" fill="#4c8bf5"/><circle cx="188" cy="196" r="5" fill="#4c8bf5"/><circle cx="234" cy="76" r="5" fill="#4c8bf5"/><circle cx="234" cy="116" r="5" fill="#4c8bf5"/><circle cx="234" cy="156" r="5" fill="#4c8bf5"/><circle cx="234" cy="196" r="5" fill="#4c8bf5"/><circle cx="280" cy="76" r="5" fill="#4c8bf5"/><circle cx="280" cy="116" r="5" fill="#4c8bf5"/><circle cx="280" cy="156" r="5" fill="#4c8bf5"/><circle cx="280" cy="196" r="5" fill="#4c8bf5"/><text x="165" y="256" text-anchor="middle" style="font-size:12px;font-weight:600">ライト プローブ：格子状に密（SH）</text><rect x="370" y="44" width="290" height="190" rx="8" fill="none" stroke="#94a3b8" stroke-width="2"/><rect x="480" y="110" width="70" height="60" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="515" y="140" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">キューブ</text><text x="515" y="256" text-anchor="middle" style="font-size:12px;font-weight:600">反射プローブ：部屋に 1〜2 個（キューブマップ）</text></svg>

ライト プローブは部屋に格子状に密に置きます。1 つの点で全方向から来る拡散の光を放射照度（法線ごとの明るさ）として保存します。放射照度は方向に対してなめらかに変わるので、SH 係数 27 個（L2、RGB）の数百バイトで足ります。動く物体は自分の位置の周りのプローブを補間して、法線で放射照度を求めます。

反射プローブは部屋に 1 から 2 個だけ置きます。1 つの点で周りの景色を画像として保存します。保存するのは放射輝度のキューブマップで、128 × 128 × 6 面のようなサイズです。鏡面では景色がそのまま映るので、方向ごとの細かさが必要になります。読むときは反射ベクトルでキューブマップを引き粗さでミップを選びます。

数が違うのは保存の大きさが違うからです。ライト プローブは小さいので数千個を格子状に置けます。反射プローブは大きいので数十個を部屋ごとエリアごとに置いて、近い 1 つか影響範囲が重なる 2 から 3 個をブレンドして使います。

## なぜ拡散は SH で足り鏡面は足りないのか

放射照度は周りの明るさに「法線とのなす角の余弦」を掛けて半球で積分した値です。この積分は細かい変化をならしてしまいます。そのため、少ない係数の SH で表せます。鏡面は景色の細かさがそのまま見えるので、SH では足りません。

この違いを小さなプログラムで確かめます。環境は空のグラデーションと小さく明るい太陽（空より約 20 倍明るい）の組み合わせです。方向を格子で積分して SH の係数を求め L0、L1、L2 で放射照度を復元した結果を直接積分した本当の値と比べます。

### 環境と基底

```cpp
// probe_sh.cpp : ライト プローブ（SH）と反射プローブ（キューブマップ）の違いを、数字で確かめる。
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <print>
#include <vector>

constexpr double kPi = 3.14159265358979323846;

struct Vec { double x, y, z; };
double Dot(Vec a, Vec b) { return a.x * b.x + a.y * b.y + a.z * b.z; }

// 環境の明るさ L(ω)。空のグラデーション + 小さく明るい太陽。
double Env(Vec w) {
  const Vec sun = {0.5, 0.7, 0.5099};                       // おおよそ単位ベクトル（下で正規化）
  double len = std::sqrt(Dot(sun, sun));
  double s = std::max(0.0, Dot(w, {sun.x / len, sun.y / len, sun.z / len}));
  return 0.2 + 0.8 * (w.y * 0.5 + 0.5) + 20.0 * std::pow(s, 64.0);
}

// 実数の球面調和関数 Y_lm の l = 0..2（9 個）。
void Basis(Vec n, double y[9]) {
  y[0] = 0.282095;
  y[1] = 0.488603 * n.y; y[2] = 0.488603 * n.z; y[3] = 0.488603 * n.x;
  y[4] = 1.092548 * n.x * n.y; y[5] = 1.092548 * n.y * n.z;
  y[6] = 0.315392 * (3 * n.z * n.z - 1); y[7] = 1.092548 * n.x * n.z;
  y[8] = 0.546274 * (n.x * n.x - n.y * n.y);
}
```

`Env` は空のグラデーションと太陽の方向に鋭く立つ明るい山（`pow(s, 64)`）の和です。`Basis` は実数の球面調和関数の l = 0 から 2 の 9 個の基底関数です。L0 は 1 個、L1 は 3 個、L2 は 5 個の基底を持ちます。

### 係数と放射照度の誤差

```cpp
int main() {
  // 方向を θ-φ の格子で積分する（面積要素 sinθ dθ dφ）。
  const int nt = 256, np = 512;
  std::vector<Vec> dirs; std::vector<double> weight, radiance;
  for (int i = 0; i < nt; ++i) for (int j = 0; j < np; ++j) {
    double th = (i + 0.5) / nt * kPi, ph = (j + 0.5) / np * 2 * kPi;
    Vec w = {std::sin(th) * std::cos(ph), std::cos(th), std::sin(th) * std::sin(ph)};
    dirs.push_back(w); weight.push_back(std::sin(th) * (kPi / nt) * (2 * kPi / np)); radiance.push_back(Env(w));
  }
  // SH 係数 L_lm = ∫ L(ω) Y_lm(ω) dω
  double coef[9] = {};
  for (size_t k = 0; k < dirs.size(); ++k) { double y[9]; Basis(dirs[k], y); for (int b = 0; b < 9; ++b) coef[b] += radiance[k] * y[b] * weight[k]; }

  // 放射照度 E(n) の誤差。畳み込みの係数 A0 = π、A1 = 2π/3、A2 = π/4。
  const double A[3] = {kPi, 2 * kPi / 3, kPi / 4};
  const int band_of[9] = {0, 1, 1, 1, 2, 2, 2, 2, 2};
  double max_err[3] = {};
  for (int t = 0; t < 400; ++t) {
    double th = (t % 20 + 0.5) / 20 * kPi, ph = (t / 20 + 0.5) / 20 * 2 * kPi;
    Vec n = {std::sin(th) * std::cos(ph), std::cos(th), std::sin(th) * std::sin(ph)};
    double e = 0; for (size_t k = 0; k < dirs.size(); ++k) e += radiance[k] * std::max(0.0, Dot(n, dirs[k])) * weight[k];
    double y[9]; Basis(n, y);
    for (int maxl = 0; maxl < 3; ++maxl) {
      double r = 0; for (int b = 0; b < 9; ++b) if (band_of[b] <= maxl) r += A[band_of[b]] * coef[b] * y[b];
      max_err[maxl] = std::max(max_err[maxl], std::fabs(r - e) / e);
    }
  }
  std::println("放射照度 E(n) の最大の相対誤差（拡散）");
  for (int l = 0; l < 3; ++l) std::println("  SH L{}: {:.1f} %", l, max_err[l] * 100);
```

球面を 256 × 512 の θ-φ 格子で積分して、各基底の係数 `L_lm` を求めます。面積要素に `sinθ` を掛ける点に注意してください。掛けないと極の近くが過剰に重くなります。放射照度は法線ごとに本当の値を直接積分して、SH の復元と比べます。SH からの復元ではバンド l ごとに畳み込みの係数（A0 = π、A1 = 2π/3、A2 = π/4）を掛けます。これは余弦ローブをバンドごとに減衰させる係数で、高い次数ほど小さく細かい変化が効きません。

### 鏡面とメモリ

```cpp

  // 鏡面: 太陽の方向を L2 の SH で復元した放射輝度と、本当の値を比べる。
  double len = std::sqrt(0.5 * 0.5 + 0.7 * 0.7 + 0.5099 * 0.5099);
  Vec sun = {0.5 / len, 0.7 / len, 0.5099 / len};
  double y[9]; Basis(sun, y); double rec = 0; for (int b = 0; b < 9; ++b) rec += coef[b] * y[b];
  std::println("太陽の方向の放射輝度（鏡面で映る値）");
  std::println("  本当の値: {:.2f}  SH L2 で復元: {:.2f}", Env(sun), rec);

  // メモリ。
  const double sh = 27 * 2.0;                                       // SH L2、RGB、16 ビット
  const double cube = 128.0 * 128 * 6 * 8 * 4 / 3;                  // 128² × 6 面、RGBA16F、ミップ込み
  const double bc6h = 128.0 * 128 * 6 * 1 * 4 / 3;                  // BC6H（1 テクセル 1 バイト）
  std::println("メモリ");
  std::println("  GI プローブ 1 個: {:.0f} バイト、4096 個: {:.0f} KiB", sh, sh * 4096 / 1024);
  std::println("  反射プローブ 1 個: {:.0f} KiB（RGBA16F）、{:.0f} KiB（BC6H）", cube / 1024, bc6h / 1024);
  std::println("  反射プローブ 32 個: {:.0f} MiB（RGBA16F）、{:.0f} MiB（BC6H）", cube * 32 / 1048576, bc6h * 32 / 1048576);
  return 0;
}
```

```text title="実行結果"
放射照度 E(n) の最大の相対誤差（拡散）
  SH L0: 125.6 %
  SH L1: 37.6 %
  SH L2: 8.4 %
太陽の方向の放射輝度（鏡面で映る値）
  本当の値: 20.88  SH L2 で復元: 2.22
メモリ
  GI プローブ 1 個: 54 バイト、4096 個: 216 KiB
  反射プローブ 1 個: 1024 KiB（RGBA16F）、128 KiB（BC6H）
  反射プローブ 32 個: 32 MiB（RGBA16F）、4 MiB（BC6H）
```

<svg class="fig flow" viewBox="0 0 680 200" role="img" aria-label="放射照度の最大の相対誤差。L0 は 125.6 %、L1 は 37.6 %、L2 は 8.4 %"><text x="14" y="22" class="fig-title">放射照度の最大の相対誤差（%）：拡散は L2 でほぼ足りる</text><text x="14" y="57" style="font-size:12px;font-weight:600">SH L0（1 係数）</text><rect x="190" y="44" width="318" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="516" y="60" style="font-size:12px">125.6</text><text x="14" y="91" style="font-size:12px;font-weight:600">SH L1（4 係数）</text><rect x="190" y="78" width="95" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="293" y="94" style="font-size:12px">37.6</text><text x="14" y="125" style="font-size:12px;font-weight:600">SH L2（9 係数）</text><rect x="190" y="112" width="21" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="219" y="128" style="font-size:12px">8.4</text><text x="14" y="164" style="font-size:12px">鏡面（太陽の映り込み）は、本当の値 20.88 に対して SH L2 の復元は 2.22。</text><text x="14" y="184" style="font-size:12px">下の C++ の実行結果。太陽を含む環境で、400 方向の法線の最大値。</text></svg>

拡散の放射照度は L0（平均の明るさだけ）では最大で 125.6 % ずれますが、L1 で 37.6 %、L2 で 8.4 % まで下がります。太陽という明るい点を含む厳しい環境でも L2 の最大誤差は 8.4 % です。

一方、鏡面で映る太陽の方向の値は本当は 20.88 ですが、SH L2 で復元すると 2.22 で、約 10 分の 1 です。太陽の映り込みは SH では表せません。鏡面をキューブマップで持つのは、このためです。

## コスト

メモリはプログラムの計算結果のとおりです。GI プローブ 1 個は SH L2（27 係数 × 16 ビット）で 54 バイトで、4096 個置いても 216 KiB です。反射プローブ 1 個は 128 × 128 × 6 面の RGBA16F（1 テクセル 8 バイト）にミップを足すと 1 MiB（1024 KiB）です。32 個置くと 32 MiB になります。BC6H に圧縮すると 1 テクセル 1 バイトなので 8 分の 1、1 個 128 KiB、32 個で 4 MiB です。

つまり、4096 個の GI プローブと 32 個の反射プローブでは、GI プローブのほうが 150 分の 1 ほど小さいメモリで数が 128 倍です。GI プローブは密に置けますが、反射プローブは数を絞らないとメモリが足りません。

描画時のコストはどちらも軽い読み出しです。GI プローブは周りの 8 個を補間して SH を評価します。反射プローブはキューブマップを 1 から 2 回読みます。更新が重いのは反射プローブです。動的に更新するなら GI プローブは SH を再計算するだけですが、反射プローブはキューブマップを再レンダリングして、ミップを作り直します。ベイク自体はどちらも短時間で済みます。

## 同じ場所に 2 種類を置く

部屋の中に GI プローブ（格子状、数十個）と反射プローブ（1 から 2 個）を同時に置き描画で両方を読みます。拡散と鏡面の間接光を別のプローブでまかないます。

次の HLSL がその読み方です。`fxc`（`ps_5_0`）でコンパイルして確かめました。実行はしていません。SH のパッキング（3D テクスチャ 7 枚に 27 係数）の詳細は [Storing SH](sh-storage.md) にあります。

### 入力

```hlsl
// probe_combine.hlsl : ライト プローブ（拡散）と反射プローブ（鏡面）から、間接光を求める。

Texture3D<float4>   g_sh_tex[7] : register(t0);   // SH L2 を 3D テクスチャ 7 枚に詰めたもの（RGBA16F）。t0〜t6
TextureCube<float4> g_reflection : register(t8);  // 反射プローブ（ミップ付き。ミップが粗いほど粗い反射）
Texture2D<float2>   g_brdf_lut   : register(t9);  // split-sum の LUT（x = スケール、y = バイアス）
SamplerState g_linear            : register(s0);

cbuffer ProbeParams : register(b0) {
  float3 g_grid_origin;   // プローブ格子の原点（ワールド）
  float  g_cell;          // 格子 1 マスの大きさ（ワールド単位）
  float3 g_grid_size;     // 格子の個数（x, y, z）
  float  g_max_mip;       // 反射プローブの最大ミップ番号（128² なら 7）
};

// SH L2 の 9 係数（RGB）。3D テクスチャ 7 枚から読んだ 28 個の値を、27 個に展開して使う（パッキングは SH 保存のページ）。
struct Sh9 { float3 c[9]; };

Sh9 LoadSh(float3 world_pos) {
  float3 uvw = (world_pos - g_grid_origin) / (g_cell * g_grid_size);   // 格子の中での位置 0〜1
  float4 t[7];
  [unroll] for (int i = 0; i < 7; ++i) t[i] = g_sh_tex[i].SampleLevel(g_linear, uvw, 0);   // トライリニア補間は、サンプラーが行う
  Sh9 s;
  s.c[0] = t[0].rgb;
  s.c[1] = float3(t[0].a, t[1].rg);  s.c[2] = float3(t[1].ba, t[2].r);  s.c[3] = float3(t[2].gba);
  s.c[4] = t[3].rgb;                 s.c[5] = float3(t[3].a, t[4].rg);  s.c[6] = float3(t[4].ba, t[5].r);
  s.c[7] = float3(t[5].gba);         s.c[8] = t[6].rgb;
  return s;
}
```

SH は 3D テクスチャ 7 枚（28 個の枠）に 27 係数を詰めたものです。3D テクスチャにしておくとサンプラーが格子の周りのプローブをトライリニア補間してくれます。反射プローブはミップ付きのキューブマップで、ミップが粗いほど粗い反射になります。

### 放射照度の評価

```hlsl
// 法線 n の放射照度 E(n) を SH L2 から求める（Ramamoorthi and Hanrahan 2001 の式）。
// 畳み込みの係数 A0 = π、A1 = 2π/3、A2 = π/4 は、基底の定数に掛け込んである。
float3 IrradianceFromSh9(Sh9 s, float3 n) {
  const float c1 = 0.429043, c2 = 0.511664, c3 = 0.743125, c4 = 0.886227, c5 = 0.247708;
  return c1 * s.c[8] * (n.x * n.x - n.y * n.y) + c3 * s.c[6] * n.z * n.z + c4 * s.c[0] - c5 * s.c[6]
       + 2.0 * c1 * (s.c[4] * n.x * n.y + s.c[7] * n.x * n.z + s.c[5] * n.y * n.z)
       + 2.0 * c2 * (s.c[3] * n.x + s.c[1] * n.y + s.c[2] * n.z);
}
```

係数 9 個から法線方向の放射照度を求める式は、Ramamoorthi と Hanrahan の式です。畳み込みの係数 A0、A1、A2 は定数 `c1` から `c5` に掛け込んであります。式の中の `2.0 *` は対称な項（xy と xz と yz、x と y と z）が 2 回出てくることを表します。

### 拡散と鏡面を合計する

```hlsl
float3 IndirectLight(float3 world_pos, float3 n, float3 v, float3 albedo, float3 f0, float roughness) {
  // 拡散: ライト プローブ。放射照度 E を π で割った値に albedo を掛ける。
  float3 e = max(IrradianceFromSh9(LoadSh(world_pos), n), 0.0);   // SH の負の値（リンギング）を 0 に切る
  float3 diffuse = albedo / 3.14159265 * e;

  // 鏡面: 反射プローブ。反射ベクトルでキューブマップを読み、粗さでミップを選ぶ。
  float3 r = reflect(-v, n);
  float3 prefiltered = g_reflection.SampleLevel(g_linear, r, roughness * g_max_mip).rgb;
  float2 brdf = g_brdf_lut.SampleLevel(g_linear, float2(saturate(dot(n, v)), roughness), 0);
  float3 specular = prefiltered * (f0 * brdf.x + brdf.y);

  float3 kd = 1.0 - f0;     // エネルギー保存の簡易版。鏡面に回った分を拡散から引く
  return kd * diffuse + specular;
}

float4 main(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float3 c = IndirectLight(float3(0, 1, 0), float3(0, 1, 0), float3(0, 0, -1), float3(0.5, 0.5, 0.5), float3(0.04, 0.04, 0.04), 0.5);
  return float4(c, 1);
}
```

拡散は放射照度 `e` を π で割って、albedo を掛けます。SH はリンギングで負の値を返すことがあるので、`max(…, 0.0)` で 0 に切ります。鏡面は反射ベクトルでキューブマップを読み粗さにミップ番号を比例させ split-sum の LUT の値を掛けます。`kd = 1 - f0` は鏡面に回ったエネルギーを拡散から引く簡易版です。厳密な式ではないのでプロジェクトで使うシェーディング モデルに合わせて置き換えてください。

## 使い分けの目安

- 動く物の拡散の環境光: GI プローブ。
- 床や水たまりの反射、金属の鏡面: 反射プローブ。
- 屋外の環境光（空）: 空の SH を 1 つ空のキューブマップを 1 つ。
- 室内の環境光: GI プローブを部屋ごとに密に反射プローブを部屋ごとに 1 つ。

エンジンによっては 1 つのプローブが SH とキューブマップの両方を持ち、同じ位置にまとめる作りになっています。ただし、置く密度は別々に決めるのが普通です。

## 長所と短所

GI プローブの長所は動く物体に間接光を与えられることです。小さく軽くライトマップと併用しやすく、動的な更新にも拡張できます。

短所は 4 つです。低周波だけで細かい間接光の影（接触部の暗さ）は出ません。それは AO で補います。壁越しに光が漏れるライト リークがあります。配置の手間がかかり置き方で品質が決まります。ベイクのままでは光の変化に追従できません。

## よくあるミス

??? failure "GI プローブで、鏡のような反射を出そうとする"
    SH L2 では太陽のような鋭い映り込みは、本当の値の約 10 分の 1 にしかなりません。鏡面は反射プローブや SSR で扱います。

??? failure "反射プローブを GI プローブと同じ密度で置いて、メモリが足りない"
    反射プローブは 1 個が約 1 MiB（128 × 128 × 6、RGBA16F、ミップ込み）です。格子状に数千個は置けません。部屋ごとに数を絞り圧縮（BC6H）も検討します。

??? failure "SH を評価して、暗い部分が負の色になる"
    SH L2 の復元はリンギングで負の値を返すことがあります。評価した放射照度を `max(…, 0.0)` で切ります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GI プローブは拡散・低周波・SH、反射プローブは鏡面・高周波・キューブマップ
    - [x] 放射照度は SH L2 で最大 8.4 % 程度の誤差。鏡面は SH では表せない
    - [x] メモリは GI プローブが桁違いに小さく、反射プローブは数を絞る
    - [x] 併用するのが普通

## 参考

このページは同じセクションの各ページ（Probe GI、Storing SH、Probe Placement、Interpolation Methods）と一般的な実装の知識をもとに書きました。次の資料はこのページを書くために読み直していません。誤差とメモリの数字はこのページの C++ の出力です。放射照度の式は Ramamoorthi と Hanrahan の論文の式を使いましたが、論文の本文とは照合していません。

- Gene Greger, Peter Shirley, Philip M. Hubbard, Donald P. Greenberg, "The Irradiance Volume", IEEE Computer Graphics and Applications, Vol. 18, No. 2, 1998.（プローブ GI の原点）
- Ravi Ramamoorthi, Pat Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001.（放射照度の SH 表現）
- Sébastien Lagarde, Charles de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014.
- Jason Mitchell, Gary McTaggart, Chris Green, "Shading in Valve's Source Engine", SIGGRAPH 2006, Advanced Real-Time Rendering in 3D Graphics and Games.（アンビエント キューブ）
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018.（大域照明、ライトマップ、プローブの章）

## 関連ページ

- [Probe GI](index.md)
- [Storing SH](sh-storage.md)
- [Reflection Probes](../../reflections/probes/index.md)
- [GI Theory](../theory/index.md)
