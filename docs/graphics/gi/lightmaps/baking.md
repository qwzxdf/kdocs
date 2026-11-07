---
title: Baking Workflow
tags:
  - 描画
---

# Baking Workflow

ライトマップのベイクは設定を変えるたびに数分から数時間待たされる作業です。サンプルを増やせばノイズは減りますが、半分にするには 4 倍の時間がかかります。バウンスを増やせば明るくなりますが、白い部屋では 3 回でも足りません。UV2 の余白が足りないと遠くから見たときだけ黒い線が出ます。このページではベイクの流れを追いながら、これらの「時間と品質の関係」を数字で確かめます。実際に、パス トレーシングで放射照度を推定する小さなベイカーを書いて走らせノイズの減り方とバウンスの打ち切りを検証します。そのうえで、法線マップと併用するための方向情報（Radiosity Normal Mapping）の基底を調べ、ライトマップを読むシェーダーと BC6H のテクスチャの作成までをまとめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。ベイクの時間はレイの速さを仮定した見積もりで、実測ではありません。HLSL は `fxc`（`ps_5_0`）に通し、D3D11 のコードは `g++ -fsyntax-only`（mingw の `<d3d11.h>`）で構文を確かめただけです。描画した結果は確かめていません。末尾の資料は今回は読んでいません。以前のページは同じ段落が 3 回重複していたので、1 つにまとめました。

!!! tip "ポイント"
    - サンプル数 N を 4 倍にすると、ノイズ（相対標準偏差）は半分になります。N = 16 で 0.248、64 で 0.126、256 で 0.063、16384 で 0.0077 でした。
    - 反射率 ρ の部屋で k 回までバウンスを追うと無限に反射した明るさの `1 − ρ^(k+1)` を得ます。ρ = 0.5 なら 3 回で 93.8%、ρ = 0.8 では 3 回で 59.0%、6 回で 79.0% です。「2〜3 回で足りる」は反射率が低い場合の話です。
    - 面積 10,000 m²、1 m あたり 10 テクセル、512 サンプル、バウンス 3 回ならレイは約 2.05 Gray です。レイの速さを CPU 20 Mray/s、GPU 500 Mray/s と仮定すると、それぞれ 1.7 分と 0.1 分です。
    - 双線形補間の範囲は 1 テクセルなので、ミップ k でも色が漏れないための余白は、元の解像度で `2^k` テクセルです。ミップ 3 まで使うなら 8 テクセル必要です。
    - 方向情報は基底ごとに別のテクスチャが要ります。BC6H で 100 万テクセルなら 1 枚 0.95 MiB、3 枚で 2.86 MiB です。

!!! info "このページを読む前に"
    - [Lightmaps](index.md)（このセクション全体の地図と読む順番）

## ベイクの流れ {#flow}

ベイクはシーンの静的な光を制作時に計算して、テクスチャへ書き出す作業です。実行時のゲームでは重すぎる計算（何度もの反射、やわらかい影）を時間をかけて行えます。手順は次のとおりです。

1. UV2 を用意します。静的なメッシュに重ならない 2 つ目の UV を作りライトマップのアトラスに配置します（[Lightmap UVs (UV2)](uv2.md)）。
2. 静的なライトをベイク対象に設定します。
3. ベイカーを実行します。アトラスの各テクセルが指す面上の位置と法線から、パス トレーシングで放射照度を求めます。
4. ノイズを除去（デノイズ）します。サンプルを少なくして速く計算し、あとでデノイザーで取り除くのが、いまの標準的な使い方です。
5. 圧縮して出力します。HDR 向けの BC6H などを使います。
6. 実行時にシーンと一緒にライトマップを読み込みます。

確認は最初は低い品質で全体を回して、構図と配置の間違いを見つけ最後だけ品質を上げます。ベイクには数分から数時間かかるので、1 回の失敗が高くつきます。GPU でレイトレースするベイカーを使うと CPU より大幅に速くなります。

## 光のシミュレーション {#simulation}

### 1 テクセルの放射照度 {#texel}

ライトマップの各テクセルは面上の 1 点（位置 `p`、法線 `n`）に対応します。その点に届く放射照度を半球上の方向を選びながら、モンテカルロで推定します。方向は余弦に比例した確率（pdf = `cos θ / π`）で選びます。拡散面の反射では BRDF（`ρ / π`）に余弦を掛けて pdf で割ると `ρ` だけが残るので、1 回のバウンスの重みは反射率そのものになります。そのため、次のような簡単な再帰で書けます。

```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>
#include <random>

struct Float3 { double x, y, z; };
Float3 operator+(Float3 a, Float3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
Float3 operator-(Float3 a, Float3 b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
Float3 operator*(Float3 a, double s) { return {a.x * s, a.y * s, a.z * s}; }
double Dot(Float3 a, Float3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
Float3 Cross(Float3 a, Float3 b) { return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x}; }
Float3 Normalize(Float3 v) { const double l = std::sqrt(Dot(v, v)); return {v.x / l, v.y / l, v.z / l}; }

const double kPi = std::numbers::pi;

std::mt19937_64 g_rng(12345);                                   // 固定シード。毎回同じ結果になる
double Rand() { return std::uniform_real_distribution<double>(0.0, 1.0)(g_rng); }

// 法線 n の半球から、余弦に比例した確率(pdf = cos / π)で方向を選ぶ。
// 円盤から一様に点を取り(半径 √u1、角 2π u2)、半球へ持ち上げる(Malley の方法)。
Float3 CosineSampleHemisphere(Float3 n, double u1, double u2) {
  const double r = std::sqrt(u1), phi = 2.0 * kPi * u2;
  const double x = r * std::cos(phi), y = r * std::sin(phi), z = std::sqrt(std::max(0.0, 1.0 - u1));   // 局所座標(z が法線)
  const Float3 up = std::abs(n.z) < 0.999 ? Float3{0, 0, 1} : Float3{1, 0, 0};
  const Float3 t = Normalize(Cross(up, n)), b = Cross(n, t);                                           // n に直交する 2 本
  return t * x + b * y + n * z;
}

// ---- 検証用のシーン: 半径 R の球の内側。全面の反射率 rho、全面が一様に Le を放射する(白い炉テスト)。
struct Furnace { double radius, rho, emit; };

// 球の内側の点 p から方向 dir へ飛ばしたレイが、球面に当たる点を返す。
Float3 HitSphereFromInside(const Furnace& s, Float3 p, Float3 dir) {
  const double b = Dot(p, dir);
  const double c = Dot(p, p) - s.radius * s.radius;               // 内側なので負
  const double t = -b + std::sqrt(b * b - c);                     // 遠い方の交点が球面
  return p + dir * t;
}

// パス トレーシング: 点 p から dir の向きに来る放射輝度を、最大 bounces 回の反射まで追って推定する。
double TracePath(const Furnace& s, Float3 p, Float3 dir, int bounces) {
  const Float3 hit = HitSphereFromInside(s, p, dir);
  double radiance = s.emit;                                        // 当たった面が自分で出す光
  if (bounces > 0) {
    const Float3 n = hit * (-1.0 / s.radius);                       // 球の内側へ向く法線
    const Float3 next = CosineSampleHemisphere(n, Rand(), Rand());  // 余弦重みで次の方向を選ぶ
    // 拡散の反射: BRDF = rho / π、確率密度 = cos / π、余弦 = cos。これらを掛けて割ると rho だけが残る。
    radiance += s.rho * TracePath(s, hit, next, bounces - 1);
  }
  return radiance;
}

// ---- 壁で半分が遮られた点: 面積の無限に広い垂直な壁のそばの点(法線は上)。空は一様 L = 1 の放射。
//      壁の向こう半分の半球は見えない。余弦重みづけでの見える割合は、ちょうど 0.5。
double VisibleSkyOnce(Float3 n) {
  const Float3 d = CosineSampleHemisphere(n, Rand(), Rand());
  return d.x > 0.0 ? 1.0 : 0.0;                                    // x > 0 の側だけ空が見える(x < 0 は壁)
}

int main() {
  // 1. 白い炉テスト。L_K = Le * (1 - rho^(K+1)) / (1 - rho) になるはず。
  std::printf("-- furnace test (Le = 1, 200000 paths)\n");
  const Furnace base = {10.0, 0.0, 1.0};
  for (double rho : {0.2, 0.5, 0.8}) {
    Furnace s = base;
    s.rho = rho;
    for (int k : {0, 1, 2, 3, 4, 6}) {
      double sum = 0.0;
      const int n = 200000;
      for (int i = 0; i < n; ++i) {
        const Float3 p = {1.0, 2.0, -3.0};                                    // 球の内側の適当な点
        const Float3 dir = CosineSampleHemisphere(Normalize(Float3{0.3, 0.5, 0.8}), Rand(), Rand());
        sum += TracePath(s, p, dir, k);
      }
      const double est = sum / n;
      const double exact = (1.0 - std::pow(rho, k + 1)) / (1.0 - rho);
      std::printf("rho %.1f, bounces %d: estimate %.4f, exact %.4f, captured %.1f%% of the infinite series\n", rho, k, est, exact,
                  exact * (1.0 - rho) * 100.0);
    }
  }

  // 2. ノイズは 1 / sqrt(N)。壁で半分隠れた点の見える割合を推定し、試行 4000 回の相対標準偏差を測る。
  //    理論: 二項分布で、見える割合 p = 0.5 の相対標準偏差 = sqrt((1 - p) / (p N))。
  std::printf("-- noise vs samples (p = 0.5)\n");
  for (int n : {16, 64, 256, 1024, 4096, 16384}) {
    const int trials = 4000;
    double mean = 0.0, sq = 0.0;
    for (int t = 0; t < trials; ++t) {
      double v = 0.0;
      for (int i = 0; i < n; ++i) v += VisibleSkyOnce({0, 0, 1});
      v /= n;
      mean += v; sq += v * v;
    }
    mean /= trials;
    const double sd = std::sqrt(std::max(0.0, sq / trials - mean * mean));
    std::printf("N = %5d: mean %.4f, relative std dev %.4f, theory %.4f\n", n, mean, sd / mean, std::sqrt(0.5 / (0.5 * n)));
  }

  // 3. ベイク時間のモデル。テクセル数 = 表面積 × 密度^2、レイ数 = テクセル × サンプル × (1 + バウンス)(影のレイは別に数えない)。
  //    レイの速さは仮定(CPU 20 Mray/s、GPU 500 Mray/s)。実測ではない。
  std::printf("-- bake cost model (area 10000 m2)\n");
  for (double density : {5.0, 10.0, 20.0}) {
    const double texels = 10000.0 * density * density;
    for (int samples : {128, 512, 2048}) {
      const double rays = texels * samples * 4.0;                  // バウンス 3 → 4 本のレイ
      std::printf("density %4.0f texel/m: %9.0f texels, %5d samples: %8.2f Grays -> CPU %8.1f min, GPU %6.1f min\n", density, texels, samples,
                  rays / 1e9, rays / 20e6 / 60.0, rays / 500e6 / 60.0);
    }
  }

  // 4. 保存形式と方向情報による容量。1 つのライトマップ(テクセル 1,000,000)。
  std::printf("-- lightmap memory for 1,000,000 texels\n");
  struct Fmt { const char* name; double bytes_per_texel; };
  for (const Fmt& f : {Fmt{"BC6H (4x4 -> 16 B)", 1.0}, Fmt{"R8G8B8A8 (RGBM etc.)", 4.0}, Fmt{"R16G16B16A16_FLOAT", 8.0}}) {
    std::printf("%-22s: 1 map %6.2f MiB, 2 maps (directional) %6.2f MiB, 3 maps (radiosity normal mapping) %6.2f MiB\n", f.name,
                1e6 * f.bytes_per_texel / 1048576.0, 2e6 * f.bytes_per_texel / 1048576.0, 3e6 * f.bytes_per_texel / 1048576.0);
  }

  // 5. UV2 の余白。ミップ level k では、1 テクセルが元の 2^k テクセル。双線形補間の範囲は 1 テクセルなので、
  //    隣のチャート(別の面)の色が入らないためには、元の解像度で 2^k テクセル以上の余白が要る。
  std::printf("-- padding needed so that mip level k does not bleed\n");
  for (int k = 0; k <= 5; ++k) {
    std::printf("mip %d: padding >= %2d texels at full resolution\n", k, 1 << k);
  }

  // 6. Radiosity Normal Mapping の基底(接空間)。互いに直交する単位ベクトル 3 本で、z からの角度は同じ。
  //    よく知られた配置と記憶している値で、一次資料では確かめていない。性質(直交・単位・同じ角度)はここで数える。
  std::printf("-- radiosity normal mapping basis (tangent space)\n");
  const Float3 basis[3] = {{-1.0 / std::sqrt(6.0), 1.0 / std::sqrt(2.0), 1.0 / std::sqrt(3.0)},
                           {-1.0 / std::sqrt(6.0), -1.0 / std::sqrt(2.0), 1.0 / std::sqrt(3.0)},
                           {std::sqrt(2.0 / 3.0), 0.0, 1.0 / std::sqrt(3.0)}};
  for (int i = 0; i < 3; ++i) {
    std::printf("b%d = (%.4f, %.4f, %.4f), |b| = %.4f, angle from z = %.2f deg\n", i, basis[i].x, basis[i].y, basis[i].z,
                std::sqrt(Dot(basis[i], basis[i])), std::acos(basis[i].z) * 180.0 / kPi);
  }
  std::printf("b0.b1 = %.4f, b0.b2 = %.4f, b1.b2 = %.4f\n", Dot(basis[0], basis[1]), Dot(basis[0], basis[2]), Dot(basis[1], basis[2]));
  // 直交基底なら、法線 n に対して (n.b0)^2 + (n.b1)^2 + (n.b2)^2 = |n|^2 = 1。3 つとも正のとき、重み w_i = (n.b_i)^2 の和がちょうど 1。
  std::printf("weights w_i = saturate(n.b_i)^2 for tilted normals (sum = 1 when all dots >= 0):\n");
  for (double tilt : {0.0, 20.0, 40.0, 60.0, 80.0}) {
    for (double az : {0.0, 90.0}) {
      const double t = tilt * kPi / 180.0, a = az * kPi / 180.0;
      const Float3 n = {std::sin(t) * std::cos(a), std::sin(t) * std::sin(a), std::cos(t)};
      double w[3], sum = 0.0;
      for (int i = 0; i < 3; ++i) { const double d = std::max(0.0, Dot(n, basis[i])); w[i] = d * d; sum += w[i]; }
      std::printf("tilt %4.0f az %3.0f: w = (%.4f, %.4f, %.4f), sum %.4f\n", tilt, az, w[0], w[1], w[2], sum);
    }
  }
}
```

`CosineSampleHemisphere` は円盤に一様に点を取り（半径 `√u1`、角度 `2π u2`）、半球へ持ち上げます。`u1` から高さを `√(1 − u1)` とすると、方向の確率が余弦に比例します。`TracePath` は当たった面の発光 `emit` に反射率を掛けた次のバウンスを足します。`bounces` が 0 になったらそれ以上追いません。この例の面は球の内側（反射率と発光が一様）に限っていますが、実際のベイカーではここがシーンとの交差判定になります。

### 検証：白い炉 {#furnace}

この実装が正しいかを白い炉テストで確かめます。半径 10 の球の内側が一様に発光 `Le = 1` し、反射率 `ρ` で反射するとします。k 回までバウンスを追ったときの明るさは、等比級数の和で `Le × (1 − ρ^(k+1)) / (1 − ρ)` になるはずです。20 万本のパスで推定した結果と厳密な値を並べました。

- ρ = 0.2、k = 0: 推定 1.0000、厳密 1.0000
- ρ = 0.2、k = 3: 1.2480、1.2480
- ρ = 0.5、k = 4: 1.9375、1.9375
- ρ = 0.8、k = 6: 3.9514、3.9514

すべての組み合わせで推定と厳密が一致しました。この場面は 1 本のパスの値が毎回同じ（分散がゼロ）になるので、一致はノイズを確かめたことにはなりません。確かめたのはバウンスの数え方と反射率の重みのかけ方に間違いがないことです。

## ノイズとサンプル数 {#noise}

### 1/√N で減る {#sqrt-n}

推定値のばらつきはサンプル数 `N` の平方根に反比例して減ります。壁で半分が隠れた点（余弦重みでの見える割合が 0.5）を推定し、4000 回の試行で相対標準偏差を測りました。理論値は二項分布の `√((1 − p) / (p N))` で `p = 0.5` なら `√(1 / N)` です。

<svg class="fig flow" viewBox="0 0 680 300" role="img" aria-label="ノイズとサンプル数"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">サンプル数とノイズ</text><line x1="80" y1="250" x2="560" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="80" y1="250" x2="80" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="currentColor" stroke-dasharray="5 4" stroke-width="1.5" points="80.0,70.8 92.0,74.7 104.0,78.7 116.0,82.7 128.0,86.7 140.0,90.6 152.0,94.6 164.0,98.6 176.0,102.5 188.0,106.5 200.0,110.5 212.0,114.5 224.0,118.4 236.0,122.4 248.0,126.4 260.0,130.4 272.0,134.3 284.0,138.3 296.0,142.3 308.0,146.2 320.0,150.2 332.0,154.2 344.0,158.2 356.0,162.1 368.0,166.1 380.0,170.1 392.0,174.0 404.0,178.0 416.0,182.0 428.0,186.0 440.0,189.9 452.0,193.9 464.0,197.9 476.0,201.8 488.0,205.8 500.0,209.8 512.0,213.8 524.0,217.7 536.0,221.7 548.0,225.7 560.0,229.6"/><text x="394.43584569839567" y="150.84926089460544" text-anchor="start" style="font-size:12px;font-weight:400">理論 1/√N</text><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="80.0,71.2 176.0,102.4 272.0,134.0 368.0,166.0 464.0,198.5 560.0,230.3"/><circle cx="80.0" cy="71.2" r="4" fill="#e5484d"/><text x="86.0" y="63.159699952285536" text-anchor="start" style="font-size:11px;font-weight:700">0.2479</text><circle cx="176.0" cy="102.4" r="4" fill="#e5484d"/><text x="182.0" y="94.36538449708846" text-anchor="start" style="font-size:11px;font-weight:700">0.1255</text><circle cx="272.0" cy="134.0" r="4" fill="#e5484d"/><text x="278.0" y="125.9584975576775" text-anchor="start" style="font-size:11px;font-weight:700">0.0630</text><circle cx="368.0" cy="166.0" r="4" fill="#e5484d"/><text x="374.0" y="158.02587548120823" text-anchor="start" style="font-size:11px;font-weight:700">0.0313</text><circle cx="464.0" cy="198.5" r="4" fill="#e5484d"/><text x="470.0" y="190.53947946726225" text-anchor="start" style="font-size:11px;font-weight:700">0.0154</text><circle cx="560.0" cy="230.3" r="4" fill="#e5484d"/><text x="566.0" y="222.31486789846028" text-anchor="start" style="font-size:11px;font-weight:700">0.0077</text><text x="80.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">16</text><text x="176.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">64</text><text x="272.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">256</text><text x="368.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1,024</text><text x="464.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">4,096</text><text x="560.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">16,384</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">サンプル数 N(1 テクセルあたり。対数軸)</text><text x="84" y="52" text-anchor="start" style="font-size:12px;font-weight:400">見える割合 0.5 の推定の相対標準偏差(対数軸)</text></svg>

- N = 16: 測定 0.2479、理論 0.2500
- 64: 0.1255、0.1250
- 256: 0.0630、0.0625
- 1,024: 0.0313、0.0312
- 4,096: 0.0154、0.0156
- 16,384: 0.0077、0.0078

測定と理論は 4 桁近くで一致しました。ノイズを半分にするにはサンプルを 4 倍にします。N が 16 から 16,384 へ 1024 倍になっても、ノイズは 32 分の 1 にしかなりません。サンプルを無限に増やす方向は時間の割に効果が薄くなります。そこでデノイザーを使いサンプルは少なめに保ちます。

### 時間の見積もり {#cost}

ベイクの時間はテクセルの数、サンプル数、バウンス数の積に比例します。テクセルの数は面積 × 密度² です。レイの本数はテクセル × サンプル × （1 + バウンス）で、影のレイは別に数えません。レイの速さは CPU で 20 Mray/s、GPU で 500 Mray/s と仮定しました（実測ではありません）。面積 10,000 m² で数えました。

- 密度 5 テクセル/m（25 万テクセル）、512 サンプル: 0.51 Gray、CPU 0.4 分、GPU 0.0 分
- 密度 10（100 万テクセル）、128 サンプル: 0.51 Gray、CPU 0.4 分
- 密度 10、512 サンプル: 2.05 Gray、CPU 1.7 分、GPU 0.1 分
- 密度 10、2048 サンプル: 8.19 Gray、CPU 6.8 分、GPU 0.3 分
- 密度 20（400 万テクセル）、2048 サンプル: 32.77 Gray、CPU 27.3 分、GPU 1.1 分

密度を 2 倍にするとテクセルの数は 4 倍になります。サンプルを 4 倍にすると時間も 4 倍で、ノイズは半分です。バウンスを 3 から 6 に増やすとレイは 4 本から 7 本に 1.75 倍になります。この仮定の速さが実際より遅いことも速いこともありますが、掛け算の構造はそのまま使えます。シーンが大きいほどまず密度を下げて確認する意味が大きくなります。

## バウンスの数 {#bounces}

以前のページは「2〜3 バウンスで足りる」と書いていましたが、この値は反射率に依存します。反射率 ρ の閉じた空間で k 回までバウンスを追ったときの無限に反射した明るさに対する割合は `1 − ρ^(k+1)` です（先の白い炉テストの厳密値と一致します）。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="バウンスの累計"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">バウンス回数と明るさ</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="70.0,98.0 132.5,67.6 195.0,61.5 257.5,60.3 320.0,60.1 382.5,60.0 445.0,60.0 507.5,60.0 570.0,60.0"/><circle cx="70.0" cy="98.0" r="4" fill="#2e9e5b"/><text x="78.0" y="114.0" text-anchor="start" style="font-size:11px;font-weight:700">80.0%</text><circle cx="257.5" cy="60.3" r="4" fill="#2e9e5b"/><text x="265.5" y="52.304" text-anchor="start" style="font-size:11px;font-weight:700">99.8%</text><text x="576" y="64.00009727999998" text-anchor="start" style="font-size:11px;font-weight:700">ρ = 0.2</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,155.0 132.5,107.5 195.0,83.8 257.5,71.9 320.0,65.9 382.5,63.0 445.0,61.5 507.5,60.7 570.0,60.4"/><circle cx="70.0" cy="155.0" r="4" fill="#4c8bf5"/><text x="78.0" y="171.0" text-anchor="start" style="font-size:11px;font-weight:700">50.0%</text><circle cx="257.5" cy="71.9" r="4" fill="#4c8bf5"/><text x="265.5" y="63.875" text-anchor="start" style="font-size:11px;font-weight:700">93.8%</text><text x="576" y="64.37109375" text-anchor="start" style="font-size:11px;font-weight:700">ρ = 0.5</text><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,212.0 132.5,181.6 195.0,157.3 257.5,137.8 320.0,122.3 382.5,109.8 445.0,99.8 507.5,91.9 570.0,85.5"/><circle cx="70.0" cy="212.0" r="4" fill="#e5484d"/><text x="78.0" y="228.0" text-anchor="start" style="font-size:11px;font-weight:700">20.0%</text><circle cx="257.5" cy="137.8" r="4" fill="#e5484d"/><text x="265.5" y="129.824" text-anchor="start" style="font-size:11px;font-weight:700">59.0%</text><text x="576" y="89.50136832000001" text-anchor="start" style="font-size:11px;font-weight:700">ρ = 0.8</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="132.5" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">2</text><text x="257.5" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">3</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">4</text><text x="382.5" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">5</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">6</text><text x="507.5" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">7</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">8</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0%</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">50%</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">100%</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">バウンスの回数 k(0 = 光源から直接)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">無限に反射したときの明るさに対する割合 1 − ρ^(k+1)</text></svg>

- ρ = 0.2（暗い）: 0 回で 80.0%、1 回で 96.0%、3 回で 99.8%
- ρ = 0.5（中くらい）: 0 回で 50.0%、1 回で 75.0%、3 回で 93.8%、6 回で 99.2%
- ρ = 0.8（白い）: 0 回で 20.0%、1 回で 36.0%、3 回で 59.0%、6 回で 79.0%

暗い部屋は 1 回の反射でほぼ終わりです。白い部屋は 3 回でも 59% しか集まりません。効果が頭打ちになる回数はその空間の反射率で決まります。ただし、この式はすべての光が同じ反射率の面にだけ当たる単純な空間の話です。実際の部屋では窓から光が逃げるので、収束はこれより速くなります。見た目に差が出なくなる回数を実際のシーンでベイクして確かめます。

## 方向情報（法線マップとの併用） {#directional}

### なぜ必要か {#why-directional}

通常のライトマップはその点に届く光の総量（スカラー）だけを持ちます。法線マップで細かい凹凸を付けても、ライトマップの明るさは法線に応じて変わらないので、間接光の陰影が平坦に見えます。レンガの壁に凹凸を付けても出っ張りと引っ込みの間接光が同じ明るさになります。これを解決するのが光の来る方向の情報です。

方式は主に 4 つあります。スカラーのみは最も軽いですが、法線マップが間接光に効きません。Directional は主な光の方向を別のテクスチャに持ち法線との内積で明るさを補正します。SH ライトマップは L1 の球面調和関数（4 係数）を持ち法線で評価します。Radiosity Normal Mapping（Valve が『Half-Life 2』で使った方式）は、3 つの基底方向の放射照度を持ちます。以下では最後のものを調べます。

### 3 つの基底 {#basis}

接空間（z が法線）に互いに直交する 3 本の単位ベクトルを置きます。z からの角度はどれも同じで、`acos(1/√3) = 54.74°` です。配置は次の値でこの配置は Valve の方式で知られているものと記憶していますが、一次資料では確かめていません。数えたのは性質のほうです。

- 基底 0: (−0.4082, +0.7071, 0.5774)
- 基底 1: (−0.4082, −0.7071, 0.5774)
- 基底 2: (+0.8165, 0.0000, 0.5774)

長さはどれも 1.0000 で、互いの内積は 0.0000（直交）、z からの角度は 54.74° でした。直交しているので法線 `n` に対して `(n·b0)² + (n·b1)² + (n·b2)² = |n|² = 1` が成り立ちます。3 つの内積がすべて正のときは重み `w_i = (n·b_i)²` の和がちょうど 1 で、正規化は要りません。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="基底の重み"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">法線の向きと基底の重み</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,243.9 76.9,240.8 83.9,236.9 90.8,232.2 97.8,226.6 104.7,220.1 111.7,212.8 118.6,204.7 125.6,195.9 132.5,186.5 139.4,176.5 146.4,166.2 153.3,155.6 160.3,145.0 167.2,134.5 174.2,124.3 181.1,114.6 188.1,105.5 195.0,97.2 201.9,89.9 208.9,83.7 215.8,78.8 222.8,75.2 229.7,73.0 236.7,72.3 243.6,73.0 250.6,75.2 257.5,78.8 264.4,83.7 271.4,89.9 278.3,97.2 285.3,105.5 292.2,114.6 299.2,124.3 306.1,134.5 313.1,145.0 320.0,155.6 326.9,166.2 333.9,176.5 340.8,186.5 347.8,195.9 354.7,204.7 361.7,212.8 368.6,220.1 375.6,226.6 382.5,232.2 389.4,236.9 396.4,240.8 403.3,243.9 410.3,246.2 417.2,247.9 424.2,249.0 431.1,249.7 438.1,250.0 445.0,250.0 451.9,250.0 458.9,250.0 465.8,250.0 472.8,250.0 479.7,250.0 486.7,250.0 493.6,250.0 500.6,250.0 507.5,250.0 514.4,250.0 521.4,250.0 528.3,250.0 535.3,250.0 542.2,249.7 549.2,249.0 556.1,247.9 563.1,246.2 570.0,243.9"/><text x="576" y="225.5" text-anchor="start" style="font-size:11px;font-weight:700">基底 0</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,243.9 76.9,246.2 83.9,247.9 90.8,249.0 97.8,249.7 104.7,250.0 111.7,250.0 118.6,250.0 125.6,250.0 132.5,250.0 139.4,250.0 146.4,250.0 153.3,250.0 160.3,250.0 167.2,250.0 174.2,250.0 181.1,250.0 188.1,250.0 195.0,250.0 201.9,250.0 208.9,249.7 215.8,249.0 222.8,247.9 229.7,246.2 236.7,243.9 243.6,240.8 250.6,236.9 257.5,232.2 264.4,226.6 271.4,220.1 278.3,212.8 285.3,204.7 292.2,195.9 299.2,186.5 306.1,176.5 313.1,166.2 320.0,155.6 326.9,145.0 333.9,134.5 340.8,124.3 347.8,114.6 354.7,105.5 361.7,97.2 368.6,89.9 375.6,83.7 382.5,78.8 389.4,75.2 396.4,73.0 403.3,72.3 410.3,73.0 417.2,75.2 424.2,78.8 431.1,83.7 438.1,89.9 445.0,97.2 451.9,105.5 458.9,114.6 465.8,124.3 472.8,134.5 479.7,145.0 486.7,155.6 493.6,166.2 500.6,176.5 507.5,186.5 514.4,195.9 521.4,204.7 528.3,212.8 535.3,220.1 542.2,226.6 549.2,232.2 556.1,236.9 563.1,240.8 570.0,243.9"/><text x="576" y="197.0" text-anchor="start" style="font-size:11px;font-weight:700">基底 1</text><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="70.0,72.3 76.9,73.0 83.9,75.2 90.8,78.8 97.8,83.7 104.7,89.9 111.7,97.2 118.6,105.5 125.6,114.6 132.5,124.3 139.4,134.5 146.4,145.0 153.3,155.6 160.3,166.2 167.2,176.5 174.2,186.5 181.1,195.9 188.1,204.7 195.0,212.8 201.9,220.1 208.9,226.6 215.8,232.2 222.8,236.9 229.7,240.8 236.7,243.9 243.6,246.2 250.6,247.9 257.5,249.0 264.4,249.7 271.4,250.0 278.3,250.0 285.3,250.0 292.2,250.0 299.2,250.0 306.1,250.0 313.1,250.0 320.0,250.0 326.9,250.0 333.9,250.0 340.8,250.0 347.8,250.0 354.7,250.0 361.7,250.0 368.6,250.0 375.6,249.7 382.5,249.0 389.4,247.9 396.4,246.2 403.3,243.9 410.3,240.8 417.2,236.9 424.2,232.2 431.1,226.6 438.1,220.1 445.0,212.8 451.9,204.7 458.9,195.9 465.8,186.5 472.8,176.5 479.7,166.2 486.7,155.6 493.6,145.0 500.6,134.5 507.5,124.3 514.4,114.6 521.4,105.5 528.3,97.2 535.3,89.9 542.2,83.7 549.2,78.8 556.1,75.2 563.1,73.0 570.0,72.3"/><text x="576" y="168.5" text-anchor="start" style="font-size:11px;font-weight:700">基底 2</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">90°</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">180°</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">270°</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">360°</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0.0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">1.0</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">法線の向き(傾き 40° のまま、方位角を回す)</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">各基底の重み w = saturate(n·b)²</text></svg>

法線の傾きを変えて重みを数えました。

- 傾き 0°（真上）: 3 つとも 0.3333
- 20°、方位 0°: (0.1623, 0.1623, 0.6753)、和 1.0000
- 40°、方位 90°: (0.8042, 0.0000, 0.1956)、和 0.9999
- 60°、方位 90°: (0.8119, 0.0000, 0.0833)、和 0.8952
- 80°、方位 90°: (0.6346, 0.0000, 0.0101)、和 0.6447

傾きが 40° までは和がほぼ 1 ですが、60° を超えると内積が負になる基底が `saturate` で 0 に切られ和が 1 未満になります。80° では 0.6447 です。そのため、シェーダーでは重みの和で割って正規化します。

## 保存の形式と容量 {#format}

ライトマップの形式は明るさの範囲（HDR）と容量のトレードオフです。1,000,000 テクセル（1 m あたり 10 テクセルで 10,000 m² 相当）で数えました。

- BC6H: 4×4 のブロックを 16 バイトに圧縮します（1 テクセル 1 バイト）。1 枚 0.95 MiB、2 枚 1.91 MiB、3 枚 2.86 MiB
- `R8G8B8A8`（RGBM などで HDR を詰める）: 1 枚 3.81 MiB、2 枚 7.63 MiB、3 枚 11.44 MiB
- `R16G16B16A16_FLOAT`: 1 枚 7.63 MiB、2 枚 15.26 MiB、3 枚 22.89 MiB

方向情報で 3 枚に増えると、メモリと読み込み回数が 3 倍になります。モバイルなどでは Directional（2 枚）やスカラー 1 枚で妥協する選択もあります。HDR のライトマップには BC6H が向いています（`R16G16B16A16_FLOAT` の 1/8 の容量）。BC6H は DirectX 11 で使えます。

## ベイクの落とし穴 {#pitfalls}

### 継ぎ目の黒い線と余白 {#padding}

UV2 のチャート（面のまとまり）の間に余白が足りないと双線形補間で隣のチャートの色が混ざり、遠くから見たときに黒い線が出ます。ミップ k では 1 テクセルが元の `2^k` テクセルに相当します。補間の範囲は 1 テクセルなので、ミップ k で色が漏れないためには元の解像度で `2^k` テクセル以上の余白が必要です。

- ミップ 0: 1 テクセル
- ミップ 1: 2
- ミップ 2: 4
- ミップ 3: 8
- ミップ 4: 16
- ミップ 5: 32

ミップを使う距離は画面上でライトマップが縮小される量で決まります。どこまで使うかを決め余白を確保します。余白の領域には隣のチャートの縁の色を広げて埋めます（ブリード）。余白を広く取るとアトラスの使用率が下がります。

### その他 {#other}

- 真っ黒な面: メッシュの法線が反転している、面が重なっているなどです。法線の向きと UV2 の重なりを確認します。
- 光漏れ: 壁のすき間（メッシュが壁を閉じていない）から光が入ります。メッシュを閉じ壁に厚みを持たせます。
- ノイズ: サンプルが少ないときです。サンプルを増やすかデノイズします。
- ベイクが遅い: まず低品質で確認し、最終だけ高品質にします。

## ベイカーの種類 {#bakers}

- エンジン内蔵（Unity の Progressive Lightmapper、Unreal の Lightmass）: 設定が簡単です。
- 外部ツール（Blender の Cycles、V-Ray、Arnold など）: DCC ツールのレンダラーでベイクして、テクスチャとして書き出します。
- 自作（DXR など）: GPU レイトレーシングで、ライトマップの各テクセルからレイを飛ばします。独自のエンジンに組み込みやすい方法です（[Ray-Traced GI](../rt-gi/index.md)）。

## コード：ライトマップを読む {#shader}

ここからコードを数行ずつ見ます。最初は定数とテクスチャです。

```hlsl
cbuffer ObjectCB : register(b0) {
  float4x4 gWorldViewProj;     // ワールド × ビュー × 射影
  float4   gLightmapScaleOffset;  // xy = UV2 の倍率、zw = オフセット。アトラス内でこの物体が占める矩形
};

Texture2D    gLightmap0 : register(t0);   // 基底 0 方向の放射照度（リニア、HDR。BC6H など）
Texture2D    gLightmap1 : register(t1);   // 基底 1
Texture2D    gLightmap2 : register(t2);   // 基底 2
Texture2D    gNormalMap : register(t3);   // 接空間の法線マップ（xyz を 0〜1 に詰めたもの）
Texture2D    gAlbedo    : register(t4);   // アルベド（sRGB テクスチャ。読むとリニアになる）
SamplerState gLinear    : register(s0);   // 双線形 + ミップ。クランプ（アトラスの端で回り込まない）
```

`gLightmapScaleOffset` は UV2 をアトラス内の矩形に変換する値です。`xy` が倍率、`zw` がオフセットです。ライトマップは基底ごとに別のテクスチャです。サンプラーはクランプにしてアトラスの端で反対側の色が回り込まないようにします。

基底と UV の変換です。

```hlsl
// 接空間の基底方向。互いに直交する単位ベクトルで、z（法線）からの角度はどれも約 54.74°。
// 配置は Radiosity Normal Mapping で知られているものと記憶しているが、一次資料では確かめていない。
static const float3 kBasis0 = float3(-0.40824829, 0.70710678, 0.57735027);   // (-1/√6, +1/√2, 1/√3)
static const float3 kBasis1 = float3(-0.40824829, -0.70710678, 0.57735027);  // (-1/√6, -1/√2, 1/√3)
static const float3 kBasis2 = float3(0.81649658, 0.0, 0.57735027);           // (√(2/3), 0, 1/√3)

// 物体の UV2（0〜1）を、ライトマップ アトラス内の UV に直す。
float2 LightmapUv(float2 uv2) {
  return uv2 * gLightmapScaleOffset.xy + gLightmapScaleOffset.zw;   // 倍率で縮め、オフセットで置く
}
```

基底は前の節の値です。オブジェクト 1 つ分の UV2（0 から 1）を倍率で縮めオフセットで移動して、アトラス内の位置にします。

スカラーのライトマップを読みます。

```hlsl
// スカラーのライトマップ。方向情報なし。法線マップの凹凸は間接光に効かない。
float3 IndirectScalar(float2 uv2) {
  return gLightmap0.Sample(gLinear, LightmapUv(uv2)).rgb;           // 放射照度 ÷ π（アルベドは掛けていない）
}
```

方向情報がないので法線マップの凹凸は間接光に影響しません。

Radiosity Normal Mapping です。

```hlsl
// Radiosity Normal Mapping。法線マップの法線 n_ts に応じて、3 方向の放射照度を混ぜる。
float3 IndirectRnm(float2 uv2, float3 n_ts) {
  float2 uv = LightmapUv(uv2);
  float3 e0 = gLightmap0.Sample(gLinear, uv).rgb;                    // 基底 0 から来る放射照度
  float3 e1 = gLightmap1.Sample(gLinear, uv).rgb;
  float3 e2 = gLightmap2.Sample(gLinear, uv).rgb;
  float3 w = saturate(float3(dot(n_ts, kBasis0), dot(n_ts, kBasis1), dot(n_ts, kBasis2)));  // 法線と各基底の余弦。裏向きは 0
  w *= w;                                                            // 2 乗。直交基底なら、3 つが正のとき合計がちょうど 1
  w /= max(w.x + w.y + w.z, 1e-4);                                   // 傾きが大きいと合計が 1 未満になるので、正規化（ゼロ除算に下限）
  return e0 * w.x + e1 * w.y + e2 * w.z;
}
```

法線マップの法線 `n_ts` と 3 つの基底の内積を取ります。裏向き（負）は `saturate` で 0 にします。2 乗して重みを鋭くし合計で割って正規化します。`max(…, 1e-4)` は足した処理で合計が 0 になるごく傾いた法線でのゼロ除算を避けます。3 つの放射照度を重みで混ぜると、法線マップの向きに応じた間接光になります。

ピクセル シェーダーでアルベドを掛けます。

```hlsl
float4 LitPS(float4 pos : SV_Position, float2 uv : TEXCOORD0, float2 uv2 : TEXCOORD1) : SV_Target {
  float3 n_ts = normalize(gNormalMap.Sample(gLinear, uv).xyz * 2.0 - 1.0);   // 0〜1 を -1〜1 に戻す
  float3 albedo = gAlbedo.Sample(gLinear, uv).rgb;                   // sRGB テクスチャなので、リニアで返る
  float3 indirect = IndirectRnm(uv2, n_ts);                          // ベイクされた間接光
  return float4(albedo * indirect, 1.0);                             // 拡散の間接光 = アルベド × 放射照度 ÷ π。ここでは ÷ π 済み
}
```

法線マップは 0 から 1 に詰めてあるので、2 倍して 1 を引いて元に戻します。アルベドの sRGB テクスチャは読むとリニアになります。拡散の間接光はアルベド × 放射照度 ÷ π です。この例のライトマップは ÷ π 済みの値を持つものとして、アルベドだけを掛けました。

## コード：BC6H のテクスチャを作る {#cpp}

圧縮済みのライトマップからシェーダー リソース ビューを作ります。構文は確かめましたが実行はしていません。

```cpp
#include <cstdint>
#include <vector>

#include <d3d11.h>
#include <wrl/client.h>

using Microsoft::WRL::ComPtr;

// BC6H で圧縮済みのライトマップから、シェーダー リソース ビューを作る。
// BC6H は 4×4 のブロックが 16 バイト(1 テクセル = 1 バイト)。幅と高さは 4 の倍数でなければならない。
// mips は、圧縮済みの各ミップの先頭ポインターを、大きい順に並べたもの。
ComPtr<ID3D11ShaderResourceView> CreateLightmapBc6h(ID3D11Device* device, UINT width, UINT height,
                                                    const std::vector<const void*>& mips) {
  if (width % 4 != 0 || height % 4 != 0) return nullptr;               // BC6H はブロック単位
  D3D11_TEXTURE2D_DESC desc = {};
  desc.Width = width;
  desc.Height = height;
  desc.MipLevels = static_cast<UINT>(mips.size());                     // ミップを全部持つ(遠くで縮小されるため)
  desc.ArraySize = 1;
  desc.Format = DXGI_FORMAT_BC6H_UF16;                                 // 符号なしの 16 ビット浮動小数点の RGB。ライトマップは負にならない
  desc.SampleDesc.Count = 1;
  desc.Usage = D3D11_USAGE_IMMUTABLE;                                  // 読み込んだら変更しない。最も速く読める
  desc.BindFlags = D3D11_BIND_SHADER_RESOURCE;

  std::vector<D3D11_SUBRESOURCE_DATA> init(mips.size());
  UINT w = width, h = height;
  for (size_t i = 0; i < mips.size(); ++i) {
    const UINT blocks_x = (w + 3) / 4, blocks_y = (h + 3) / 4;         // ブロックの数(4×4 単位、切り上げ)
    init[i].pSysMem = mips[i];
    init[i].SysMemPitch = blocks_x * 16;                               // 1 行のブロック分のバイト数(1 ブロック 16 バイト)
    init[i].SysMemSlicePitch = blocks_x * blocks_y * 16;               // 2D では使われないが、ミップ全体のバイト数を入れておく
    w = (w > 1) ? w / 2 : 1;
    h = (h > 1) ? h / 2 : 1;
  }

  ComPtr<ID3D11Texture2D> tex;
  if (FAILED(device->CreateTexture2D(&desc, init.data(), &tex))) return nullptr;
  ComPtr<ID3D11ShaderResourceView> srv;
  if (FAILED(device->CreateShaderResourceView(tex.Get(), nullptr, &srv))) return nullptr;
  return srv;
}
```

BC6H は 4×4 のブロックが 16 バイトなので、幅と高さが 4 の倍数でなければなりません。`SysMemPitch` は 1 行のブロックのバイト数で、`ブロック数 × 16` です。`DXGI_FORMAT_BC6H_UF16` は符号なしの 16 ビット浮動小数点で、ライトマップは負にならないので、これを選びます。`D3D11_USAGE_IMMUTABLE` は読み込んだ後に変更しない設定で、最も速く読めます。ミップは全部持ちます。遠くで縮小されるときに必要で、前の節の余白もミップに対して決めています。

## よくあるミス {#mistakes}

??? failure "ライトマップが法線マップの凹凸と合わず平らに見える"
    原因は方向情報のないスカラーのライトマップを使っていることです。法線マップは間接光の明るさに効きません。方向情報（Radiosity Normal Mapping など）も一緒にベイクします。

??? failure "遠くで、チャートの継ぎ目に黒い線が出る"
    原因は UV2 の余白が、使うミップに対して足りないことです。ミップ 3 まで使うなら元の解像度で 8 テクセル必要です。余白を広げ縁の色を広げて埋めます。

??? failure "白い部屋が思ったより暗い"
    原因はバウンスの数が足りないことです。反射率 0.8 では 3 回で 59% しか集まりません。バウンスを増やすか窓から逃げる光を考えて、実際のシーンで確かめます。

??? failure "ベイクを重ねるたびに時間が足りなくなる"
    原因は密度とサンプルを同時に上げていることです。密度を 2 倍にすると 4 倍、サンプルを 4 倍にすると 4 倍の時間で、ノイズは半分です。まず密度を下げて全体を確かめ最後だけ上げます。

??? failure "真っ黒な面や壁のすき間からの光漏れがある"
    原因は法線の反転、面の重なり壁が閉じていないことです。法線の向きと UV2 の重なりを確認し、壁に厚みを持たせます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] ノイズは `1/√N`。半分にするにはサンプル 4 倍。デノイズと組み合わせる
    - [x] バウンスで集まる割合は `1 − ρ^(k+1)`。白い部屋（ρ = 0.8）は 3 回で 59%
    - [x] ベイクの時間はテクセル × サンプル × バウンスの積。密度は 2 乗で効く
    - [x] 方向情報は直交する 3 基底（z から 54.74°）の重みで混ぜる。傾きが大きいと和が 1 未満になるので正規化する
    - [x] UV2 の余白は、使うミップ k に対して `2^k` テクセル。BC6H は 1 テクセル 1 バイト

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>
#include <random>

struct Float3 { double x, y, z; };
Float3 operator+(Float3 a, Float3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
Float3 operator-(Float3 a, Float3 b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
Float3 operator*(Float3 a, double s) { return {a.x * s, a.y * s, a.z * s}; }
double Dot(Float3 a, Float3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
Float3 Cross(Float3 a, Float3 b) { return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x}; }
Float3 Normalize(Float3 v) { const double l = std::sqrt(Dot(v, v)); return {v.x / l, v.y / l, v.z / l}; }

const double kPi = std::numbers::pi;

std::mt19937_64 g_rng(12345);                                   // 固定シード。毎回同じ結果になる
double Rand() { return std::uniform_real_distribution<double>(0.0, 1.0)(g_rng); }

// 法線 n の半球から、余弦に比例した確率(pdf = cos / π)で方向を選ぶ。
// 円盤から一様に点を取り(半径 √u1、角 2π u2)、半球へ持ち上げる(Malley の方法)。
Float3 CosineSampleHemisphere(Float3 n, double u1, double u2) {
  const double r = std::sqrt(u1), phi = 2.0 * kPi * u2;
  const double x = r * std::cos(phi), y = r * std::sin(phi), z = std::sqrt(std::max(0.0, 1.0 - u1));   // 局所座標(z が法線)
  const Float3 up = std::abs(n.z) < 0.999 ? Float3{0, 0, 1} : Float3{1, 0, 0};
  const Float3 t = Normalize(Cross(up, n)), b = Cross(n, t);                                           // n に直交する 2 本
  return t * x + b * y + n * z;
}

// ---- 検証用のシーン: 半径 R の球の内側。全面の反射率 rho、全面が一様に Le を放射する(白い炉テスト)。
struct Furnace { double radius, rho, emit; };

// 球の内側の点 p から方向 dir へ飛ばしたレイが、球面に当たる点を返す。
Float3 HitSphereFromInside(const Furnace& s, Float3 p, Float3 dir) {
  const double b = Dot(p, dir);
  const double c = Dot(p, p) - s.radius * s.radius;               // 内側なので負
  const double t = -b + std::sqrt(b * b - c);                     // 遠い方の交点が球面
  return p + dir * t;
}

// パス トレーシング: 点 p から dir の向きに来る放射輝度を、最大 bounces 回の反射まで追って推定する。
double TracePath(const Furnace& s, Float3 p, Float3 dir, int bounces) {
  const Float3 hit = HitSphereFromInside(s, p, dir);
  double radiance = s.emit;                                        // 当たった面が自分で出す光
  if (bounces > 0) {
    const Float3 n = hit * (-1.0 / s.radius);                       // 球の内側へ向く法線
    const Float3 next = CosineSampleHemisphere(n, Rand(), Rand());  // 余弦重みで次の方向を選ぶ
    // 拡散の反射: BRDF = rho / π、確率密度 = cos / π、余弦 = cos。これらを掛けて割ると rho だけが残る。
    radiance += s.rho * TracePath(s, hit, next, bounces - 1);
  }
  return radiance;
}

// ---- 壁で半分が遮られた点: 面積の無限に広い垂直な壁のそばの点(法線は上)。空は一様 L = 1 の放射。
//      壁の向こう半分の半球は見えない。余弦重みづけでの見える割合は、ちょうど 0.5。
double VisibleSkyOnce(Float3 n) {
  const Float3 d = CosineSampleHemisphere(n, Rand(), Rand());
  return d.x > 0.0 ? 1.0 : 0.0;                                    // x > 0 の側だけ空が見える(x < 0 は壁)
}

int main() {
  // 1. 白い炉テスト。L_K = Le * (1 - rho^(K+1)) / (1 - rho) になるはず。
  std::printf("-- furnace test (Le = 1, 200000 paths)\n");
  const Furnace base = {10.0, 0.0, 1.0};
  for (double rho : {0.2, 0.5, 0.8}) {
    Furnace s = base;
    s.rho = rho;
    for (int k : {0, 1, 2, 3, 4, 6}) {
      double sum = 0.0;
      const int n = 200000;
      for (int i = 0; i < n; ++i) {
        const Float3 p = {1.0, 2.0, -3.0};                                    // 球の内側の適当な点
        const Float3 dir = CosineSampleHemisphere(Normalize(Float3{0.3, 0.5, 0.8}), Rand(), Rand());
        sum += TracePath(s, p, dir, k);
      }
      const double est = sum / n;
      const double exact = (1.0 - std::pow(rho, k + 1)) / (1.0 - rho);
      std::printf("rho %.1f, bounces %d: estimate %.4f, exact %.4f, captured %.1f%% of the infinite series\n", rho, k, est, exact,
                  exact * (1.0 - rho) * 100.0);
    }
  }

  // 2. ノイズは 1 / sqrt(N)。壁で半分隠れた点の見える割合を推定し、試行 4000 回の相対標準偏差を測る。
  //    理論: 二項分布で、見える割合 p = 0.5 の相対標準偏差 = sqrt((1 - p) / (p N))。
  std::printf("-- noise vs samples (p = 0.5)\n");
  for (int n : {16, 64, 256, 1024, 4096, 16384}) {
    const int trials = 4000;
    double mean = 0.0, sq = 0.0;
    for (int t = 0; t < trials; ++t) {
      double v = 0.0;
      for (int i = 0; i < n; ++i) v += VisibleSkyOnce({0, 0, 1});
      v /= n;
      mean += v; sq += v * v;
    }
    mean /= trials;
    const double sd = std::sqrt(std::max(0.0, sq / trials - mean * mean));
    std::printf("N = %5d: mean %.4f, relative std dev %.4f, theory %.4f\n", n, mean, sd / mean, std::sqrt(0.5 / (0.5 * n)));
  }

  // 3. ベイク時間のモデル。テクセル数 = 表面積 × 密度^2、レイ数 = テクセル × サンプル × (1 + バウンス)(影のレイは別に数えない)。
  //    レイの速さは仮定(CPU 20 Mray/s、GPU 500 Mray/s)。実測ではない。
  std::printf("-- bake cost model (area 10000 m2)\n");
  for (double density : {5.0, 10.0, 20.0}) {
    const double texels = 10000.0 * density * density;
    for (int samples : {128, 512, 2048}) {
      const double rays = texels * samples * 4.0;                  // バウンス 3 → 4 本のレイ
      std::printf("density %4.0f texel/m: %9.0f texels, %5d samples: %8.2f Grays -> CPU %8.1f min, GPU %6.1f min\n", density, texels, samples,
                  rays / 1e9, rays / 20e6 / 60.0, rays / 500e6 / 60.0);
    }
  }

  // 4. 保存形式と方向情報による容量。1 つのライトマップ(テクセル 1,000,000)。
  std::printf("-- lightmap memory for 1,000,000 texels\n");
  struct Fmt { const char* name; double bytes_per_texel; };
  for (const Fmt& f : {Fmt{"BC6H (4x4 -> 16 B)", 1.0}, Fmt{"R8G8B8A8 (RGBM etc.)", 4.0}, Fmt{"R16G16B16A16_FLOAT", 8.0}}) {
    std::printf("%-22s: 1 map %6.2f MiB, 2 maps (directional) %6.2f MiB, 3 maps (radiosity normal mapping) %6.2f MiB\n", f.name,
                1e6 * f.bytes_per_texel / 1048576.0, 2e6 * f.bytes_per_texel / 1048576.0, 3e6 * f.bytes_per_texel / 1048576.0);
  }

  // 5. UV2 の余白。ミップ level k では、1 テクセルが元の 2^k テクセル。双線形補間の範囲は 1 テクセルなので、
  //    隣のチャート(別の面)の色が入らないためには、元の解像度で 2^k テクセル以上の余白が要る。
  std::printf("-- padding needed so that mip level k does not bleed\n");
  for (int k = 0; k <= 5; ++k) {
    std::printf("mip %d: padding >= %2d texels at full resolution\n", k, 1 << k);
  }

  // 6. Radiosity Normal Mapping の基底(接空間)。互いに直交する単位ベクトル 3 本で、z からの角度は同じ。
  //    よく知られた配置と記憶している値で、一次資料では確かめていない。性質(直交・単位・同じ角度)はここで数える。
  std::printf("-- radiosity normal mapping basis (tangent space)\n");
  const Float3 basis[3] = {{-1.0 / std::sqrt(6.0), 1.0 / std::sqrt(2.0), 1.0 / std::sqrt(3.0)},
                           {-1.0 / std::sqrt(6.0), -1.0 / std::sqrt(2.0), 1.0 / std::sqrt(3.0)},
                           {std::sqrt(2.0 / 3.0), 0.0, 1.0 / std::sqrt(3.0)}};
  for (int i = 0; i < 3; ++i) {
    std::printf("b%d = (%.4f, %.4f, %.4f), |b| = %.4f, angle from z = %.2f deg\n", i, basis[i].x, basis[i].y, basis[i].z,
                std::sqrt(Dot(basis[i], basis[i])), std::acos(basis[i].z) * 180.0 / kPi);
  }
  std::printf("b0.b1 = %.4f, b0.b2 = %.4f, b1.b2 = %.4f\n", Dot(basis[0], basis[1]), Dot(basis[0], basis[2]), Dot(basis[1], basis[2]));
  // 直交基底なら、法線 n に対して (n.b0)^2 + (n.b1)^2 + (n.b2)^2 = |n|^2 = 1。3 つとも正のとき、重み w_i = (n.b_i)^2 の和がちょうど 1。
  std::printf("weights w_i = saturate(n.b_i)^2 for tilted normals (sum = 1 when all dots >= 0):\n");
  for (double tilt : {0.0, 20.0, 40.0, 60.0, 80.0}) {
    for (double az : {0.0, 90.0}) {
      const double t = tilt * kPi / 180.0, a = az * kPi / 180.0;
      const Float3 n = {std::sin(t) * std::cos(a), std::sin(t) * std::sin(a), std::cos(t)};
      double w[3], sum = 0.0;
      for (int i = 0; i < 3; ++i) { const double d = std::max(0.0, Dot(n, basis[i])); w[i] = d * d; sum += w[i]; }
      std::printf("tilt %4.0f az %3.0f: w = (%.4f, %.4f, %.4f), sum %.4f\n", tilt, az, w[0], w[1], w[2], sum);
    }
  }
}
```

```text title="実行結果"
-- furnace test (Le = 1, 200000 paths)
rho 0.2, bounces 0: estimate 1.0000, exact 1.0000, captured 80.0% of the infinite series
rho 0.2, bounces 1: estimate 1.2000, exact 1.2000, captured 96.0% of the infinite series
rho 0.2, bounces 2: estimate 1.2400, exact 1.2400, captured 99.2% of the infinite series
rho 0.2, bounces 3: estimate 1.2480, exact 1.2480, captured 99.8% of the infinite series
rho 0.2, bounces 4: estimate 1.2496, exact 1.2496, captured 100.0% of the infinite series
rho 0.2, bounces 6: estimate 1.2500, exact 1.2500, captured 100.0% of the infinite series
rho 0.5, bounces 0: estimate 1.0000, exact 1.0000, captured 50.0% of the infinite series
rho 0.5, bounces 1: estimate 1.5000, exact 1.5000, captured 75.0% of the infinite series
rho 0.5, bounces 2: estimate 1.7500, exact 1.7500, captured 87.5% of the infinite series
rho 0.5, bounces 3: estimate 1.8750, exact 1.8750, captured 93.8% of the infinite series
rho 0.5, bounces 4: estimate 1.9375, exact 1.9375, captured 96.9% of the infinite series
rho 0.5, bounces 6: estimate 1.9844, exact 1.9844, captured 99.2% of the infinite series
rho 0.8, bounces 0: estimate 1.0000, exact 1.0000, captured 20.0% of the infinite series
rho 0.8, bounces 1: estimate 1.8000, exact 1.8000, captured 36.0% of the infinite series
rho 0.8, bounces 2: estimate 2.4400, exact 2.4400, captured 48.8% of the infinite series
rho 0.8, bounces 3: estimate 2.9520, exact 2.9520, captured 59.0% of the infinite series
rho 0.8, bounces 4: estimate 3.3616, exact 3.3616, captured 67.2% of the infinite series
rho 0.8, bounces 6: estimate 3.9514, exact 3.9514, captured 79.0% of the infinite series
-- noise vs samples (p = 0.5)
N =    16: mean 0.4983, relative std dev 0.2479, theory 0.2500
N =    64: mean 0.4974, relative std dev 0.1255, theory 0.1250
N =   256: mean 0.4999, relative std dev 0.0630, theory 0.0625
N =  1024: mean 0.4997, relative std dev 0.0313, theory 0.0312
N =  4096: mean 0.4998, relative std dev 0.0154, theory 0.0156
N = 16384: mean 0.5001, relative std dev 0.0077, theory 0.0078
-- bake cost model (area 10000 m2)
density    5 texel/m:    250000 texels,   128 samples:     0.13 Grays -> CPU      0.1 min, GPU    0.0 min
density    5 texel/m:    250000 texels,   512 samples:     0.51 Grays -> CPU      0.4 min, GPU    0.0 min
density    5 texel/m:    250000 texels,  2048 samples:     2.05 Grays -> CPU      1.7 min, GPU    0.1 min
density   10 texel/m:   1000000 texels,   128 samples:     0.51 Grays -> CPU      0.4 min, GPU    0.0 min
density   10 texel/m:   1000000 texels,   512 samples:     2.05 Grays -> CPU      1.7 min, GPU    0.1 min
density   10 texel/m:   1000000 texels,  2048 samples:     8.19 Grays -> CPU      6.8 min, GPU    0.3 min
density   20 texel/m:   4000000 texels,   128 samples:     2.05 Grays -> CPU      1.7 min, GPU    0.1 min
density   20 texel/m:   4000000 texels,   512 samples:     8.19 Grays -> CPU      6.8 min, GPU    0.3 min
density   20 texel/m:   4000000 texels,  2048 samples:    32.77 Grays -> CPU     27.3 min, GPU    1.1 min
-- lightmap memory for 1,000,000 texels
BC6H (4x4 -> 16 B)    : 1 map   0.95 MiB, 2 maps (directional)   1.91 MiB, 3 maps (radiosity normal mapping)   2.86 MiB
R8G8B8A8 (RGBM etc.)  : 1 map   3.81 MiB, 2 maps (directional)   7.63 MiB, 3 maps (radiosity normal mapping)  11.44 MiB
R16G16B16A16_FLOAT    : 1 map   7.63 MiB, 2 maps (directional)  15.26 MiB, 3 maps (radiosity normal mapping)  22.89 MiB
-- padding needed so that mip level k does not bleed
mip 0: padding >=  1 texels at full resolution
mip 1: padding >=  2 texels at full resolution
mip 2: padding >=  4 texels at full resolution
mip 3: padding >=  8 texels at full resolution
mip 4: padding >= 16 texels at full resolution
mip 5: padding >= 32 texels at full resolution
-- radiosity normal mapping basis (tangent space)
b0 = (-0.4082, 0.7071, 0.5774), |b| = 1.0000, angle from z = 54.74 deg
b1 = (-0.4082, -0.7071, 0.5774), |b| = 1.0000, angle from z = 54.74 deg
b2 = (0.8165, 0.0000, 0.5774), |b| = 1.0000, angle from z = 54.74 deg
b0.b1 = 0.0000, b0.b2 = 0.0000, b1.b2 = 0.0000
weights w_i = saturate(n.b_i)^2 for tilted normals (sum = 1 when all dots >= 0):
tilt    0 az   0: w = (0.3333, 0.3333, 0.3333), sum 1.0000
tilt    0 az  90: w = (0.3333, 0.3333, 0.3333), sum 1.0000
tilt   20 az   0: w = (0.1623, 0.1623, 0.6753), sum 1.0000
tilt   20 az  90: w = (0.6152, 0.0904, 0.2943), sum 1.0000
tilt   40 az   0: w = (0.0323, 0.0323, 0.9353), sum 1.0000
tilt   40 az  90: w = (0.8042, 0.0000, 0.1956), sum 0.9999
tilt   60 az   0: w = (0.0000, 0.0000, 0.9916), sum 0.9916
tilt   60 az  90: w = (0.8119, 0.0000, 0.0833), sum 0.8952
tilt   80 az   0: w = (0.0000, 0.0000, 0.8178), sum 0.8178
tilt   80 az  90: w = (0.6346, 0.0000, 0.0101), sum 0.6447
```

## 参考資料 {#references}

このページの数字は C++ で数え直したものです。以下の資料は**今回は読んでいません**。Radiosity Normal Mapping の基底の配置は、記憶に基づく値で一次資料では確かめていません（性質は数えて確かめました）。

- Cindy M. Goral, Kenneth E. Torrance, Donald P. Greenberg, Bennett Battaile, "Modeling the Interaction of Light Between Diffuse Surfaces", SIGGRAPH 1984（ラジオシティ）
- Michael F. Cohen, John R. Wallace, "Radiosity and Realistic Image Synthesis", Academic Press, 1993
- Michał Iwanicki, Peter-Pike Sloan, "Precomputed Lighting in Call of Duty: Infinite Warfare", SIGGRAPH 2017, Advances in Real-Time Rendering in Games
- Matt Pharr, Wenzel Jakob, Greg Humphreys, "Physically Based Rendering: From Theory to Implementation", 4th Edition, MIT Press, 2023
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、ライトマップ、プローブの章）

## 関連ページ {#related}

- [Lightmaps](index.md)
- [Lightmap UVs (UV2)](uv2.md)
- [Specular and Dynamic Objects](dynamic-objects.md)
- [Monte Carlo Integration](../theory/monte-carlo.md)
- [Visual Effect](../theory/visual-effect.md)
