---
title: Shadow Techniques Compared
tags:
  - 描画
---

# Shadow Techniques Compared

影の方式はたくさんあります。シャドウ マップ、PCF、PCSS、VSM、カスケード、コンタクト シャドウ、距離場、仮想シャドウ マップ、レイトレース。どれも単独では弱点があり実際のゲームは遠近や静的・動的で方式を切り替えて重ねます。何を基本にして何を補助にすればよいかが分からないとバイアスやちらつきの調整で時間を使い果たします。

このページは影の方式を横に並べ現実の構成を環境ごとに示し、調整の順序を決めます。カスケードの分割とメモリは数字で見積もり太陽の影をまとめる HLSL まで載せます。個々の方式の仕組みは各ページに任せます。

!!! tip "ポイント"
    太陽の影はカスケード シャドウ マップと PCF（ノイズと TAA）が標準です。接触部のコンタクト シャドウ、遠景の距離場やベイクで補います。ハイエンドは仮想シャドウ マップやレイトレース影、モバイルは少数のカスケードとブロブ影です。バイアスとちらつき対策（スナップ）は、どの方式でも必須です。

!!! info "このページを読む前に"
    - [Shadows](index.md)（このセクション全体の地図と読む順番）

## 全方式の比較

次の表は方式を観点ごとに並べた引く用の一覧です。

| 方式 | 精度 | ソフトさ | コスト | 動的な物 | 実装 |
| --- | --- | --- | --- | --- | --- |
| [シャドウ マップ](shadow-map-basics/index.md) | 解像度依存 | ハード | 小 | ○ | 易 |
| [PCF](pcf.md) | 解像度依存 | 一定のぼけ | 小〜中 | ○ | 易 |
| [PCSS](pcss.md) | 解像度依存 | 接触硬化 | 中〜大 | ○ | 中 |
| [VSM / EVSM / MSM](vsm/index.md) | 解像度依存 | 安くソフト | 中 | ○ | 中 |
| [カスケード（CSM）](cascaded.md) | 近いほど細かい | PCF 次第 | 中 | ○ | 中 |
| スポット / キューブ | 解像度依存 | PCF 次第 | 灯の数に比例 | ○ | 中 |
| [コンタクト シャドウ](contact-shadows.md) | 画面空間 | ほぼ硬い | 小 | ○ | 中 |
| [距離場の影](sdf-shadows.md) | 距離場の解像度 | 自然にソフト | 小〜中 | ✕（静的） | 難 |
| [仮想シャドウ マップ](virtual-shadow-maps.md) | 画素に 1 テクセル | PCF 次第 | 中 | ○ | 難 |
| [レイトレース影](ray-traced.md) | 正確 | 物理的に正確 | 大 | ○ | 難 |
| [シャドウ ボリューム](shadow-volumes.md) | 画素単位で正確 | ハード | 大 | ○ | 中 |
| ブロブ / 平面投影 | 低 | ぼかし / ハード | 極小 | ○ | 易 |

太陽の影の土台になるのはカスケードです。ぼかしは PCF が標準で接触するほど影が鋭くなる効果が欲しければ PCSS です。VSM 系は安くソフトになりますが、光漏れに注意が要ります。距離場の影は静的な遠景やカプセル近似のキャラクターに向きます。仮想シャドウ マップとレイトレース影はハイエンド向けで、実装が難しい代わりに画素単位の精度が得られます。

## カスケードを数字で見積もる

標準の構成の中心はカスケードなので、分割距離、テクセルの大きさメモリを掛け算で見積もります。次の図は近い 0.1 m から影を出す 150 m までを 4 つのカスケードに分けた例です。

<svg class="fig flow" viewBox="0 0 680 200" role="img" aria-label="カスケードの分割。C0 は 0.1 から 11.71 m、C3 は 50.63 から 150 m。1 テクセルは 1.3 cm から 17.3 cm"><text x="14" y="22" class="fig-title">カスケードの分割（横軸は距離の平方根）</text><rect x="30.8" y="50" width="164.8" height="60" fill="rgba(229,72,77,0.3)" stroke="#94a3b8" stroke-width="2"/><text x="113.2" y="74" text-anchor="middle" style="font-size:13px;font-weight:700">C0</text><text x="113.2" y="94" text-anchor="middle" style="font-size:11px">1.3 cm / テクセル</text><text x="195.6" y="132" text-anchor="middle" style="font-size:11px">11.71 m</text><rect x="195.6" y="50" width="85.0" height="60" fill="rgba(46,160,67,0.3)" stroke="#94a3b8" stroke-width="2"/><text x="238.1" y="74" text-anchor="middle" style="font-size:13px;font-weight:700">C1</text><text x="238.1" y="94" text-anchor="middle" style="font-size:11px">2.9 cm / テクセル</text><text x="280.6" y="132" text-anchor="middle" style="font-size:11px">25.23 m</text><rect x="280.6" y="50" width="111.1" height="60" fill="rgba(76,139,245,0.3)" stroke="#94a3b8" stroke-width="2"/><text x="336.1" y="74" text-anchor="middle" style="font-size:13px;font-weight:700">C2</text><text x="336.1" y="94" text-anchor="middle" style="font-size:11px">5.8 cm / テクセル</text><text x="391.6" y="132" text-anchor="middle" style="font-size:11px">50.63 m</text><rect x="391.6" y="50" width="272.4" height="60" fill="rgba(229,170,40,0.35)" stroke="#94a3b8" stroke-width="2"/><text x="527.8" y="74" text-anchor="middle" style="font-size:13px;font-weight:700">C3</text><text x="527.8" y="94" text-anchor="middle" style="font-size:11px">17.3 cm / テクセル</text><text x="664.0" y="132" text-anchor="middle" style="font-size:11px">150 m</text><text x="14" y="132" style="font-size:11px">0.1 m</text><text x="14" y="170" style="font-size:12px">近いカスケードほど細かい。1 画素の大きさが距離に比例するので、遠端では 1 テクセル ≒ 1.08 画素になる。</text></svg>

分割には対数分割と等分割を混ぜる方法を使いました（λ = 0.7 は一例）。対数分割は近くを細かく等分割は均等に切ります。混ぜると近くのカスケードが細かすぎず遠くが粗すぎないバランスになります。

テクセルの大きさはカスケードの区間を包む球の直径をシャドウ マップの解像度で割って求めます。画角 60°、16:9、解像度 2048 × 2048 の場合、C0（0.1 から 11.71 m）で 1 テクセル 1.3 cm、C3（50.63 から 150 m）で 17.3 cm です。1080p の画面で 1 画素が表す大きさは、遠端で 1.3 cm から 16.0 cm なので、各カスケードの遠端では 1 テクセルが約 1.08 画素に相当し、ほぼ 1 対 1 です。

近端では事情が違います。画素は距離に比例して小さくなるので、区間の近端ではテクセルが画素より粗くなります。C1 から C3 の近端ではテクセルが画素の約 2 から 3 倍です。カスケードの境目で影の解像度が段階的に変わるのは、このためです。

メモリは 4 枚 × 2048 × 2048 × 4 バイト（D32）で 64 MiB、D16 なら 32 MiB です。点光源のキューブ（6 面、1024 × 1024、D32）は 1 灯で 24 MiB で、ローカル ライトに影を付けるなら数を制限してアトラスにまとめます。PCF のサンプル数は 3 × 3 で 9 回、5 × 5 で 25 回です。比較サンプラーを使うと 1 回で 2 × 2 の双線形が得られ 3 × 3 の 9 回で実質 4 × 4 のなめらかさになります。

### 数値実験の C++

上の数字は次のプログラムの出力です。MSVC で `/W4` の警告なしにコンパイルして実行しました。

```cpp
// csm_budget.cpp : カスケード シャドウ マップの分割距離・テクセルの大きさ・メモリを見積もる。
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <print>

int main() {
  const double fov_y = 60.0 * 3.14159265358979 / 180.0;   // 縦の画角
  const double aspect = 16.0 / 9.0;
  const double near_z = 0.1, shadow_far = 150.0;           // 影を出す距離（一例）
  const int cascades = 4, map_size = 2048, screen_h = 1080;
  const double lambda = 0.7;                               // 対数分割と等分割の混ぜ具合（一例）

  const double ty = std::tan(fov_y / 2), tx = ty * aspect;
  const double t2 = tx * tx + ty * ty;                     // 角までの傾きの 2 乗

  std::println("分割（λ = {}）: 対数と等分割を混ぜる", lambda);
  double prev = near_z;
  for (int i = 1; i <= cascades; ++i) {
```

縦の画角と縦横比から画角の傾き `tan` を求めます。`t2` は画面の角までの傾きの 2 乗で、区間を包む球の半径を求めるときに使います。

```cpp
    double f = static_cast<double>(i) / cascades;
    double log_split = near_z * std::pow(shadow_far / near_z, f);          // 対数: 近くを細かく
    double uni_split = near_z + (shadow_far - near_z) * f;                 // 等分割: 均等
    double split = lambda * log_split + (1 - lambda) * uni_split;

    // 区間 [prev, split] を包む球。中心を軸上の c に置いて、遠い角と近い角までの距離を等しくする。
    double c = std::min((prev + split) * (1 + t2) / 2, split);
    double r_far = std::sqrt(split * split * t2 + (split - c) * (split - c));
    double r_near = std::sqrt(prev * prev * t2 + (prev - c) * (prev - c));
    double r = std::max(r_far, r_near);
    double texel = 2 * r / map_size;                                       // シャドウ マップの 1 テクセルの大きさ（m）
    double pixel = 2 * split * ty / screen_h;                              // 区間の遠端での、画面 1 画素の大きさ（m）
    double pixel_near = 2 * prev * ty / screen_h;                          // 区間の近端での、画面 1 画素の大きさ（m）
    std::println("  C{}: {:6.2f} - {:6.2f} m  球の半径 {:6.2f} m  1 テクセル {:5.1f} cm  1 画素 {:5.1f} cm  比（遠端）{:.2f}  比（近端）{:.1f}",
                 i - 1, prev, split, r, texel * 100, pixel * 100, texel / pixel, texel / pixel_near);
    prev = split;
  }

  const double mib = 1024.0 * 1024.0;
  std::println("メモリ");
  std::println("  CSM {} 枚 {}x{} D32: {:.0f} MiB  D16: {:.0f} MiB", cascades, map_size, map_size,
               cascades * map_size * map_size * 4.0 / mib, cascades * map_size * map_size * 2.0 / mib);
  std::println("  点光源 キューブ 6 面 1024x1024 D32: {:.0f} MiB（1 灯）", 6 * 1024.0 * 1024 * 4 / mib);
  std::println("  PCF のサンプル数: 3x3 = {}、5x5 = {}、ハードウェア比較なら 1 回で 2x2 の双線形", 9, 25);
  return 0;
}
```

```text title="実行結果"
分割（λ = 0.7）: 対数と等分割を混ぜる
  C0:   0.10 -  11.71 m  球の半径  13.79 m  1 テクセル   1.3 cm  1 画素   1.3 cm  比（遠端）1.08  比（近端）125.9
  C1:  11.71 -  25.23 m  球の半径  29.71 m  1 テクセル   2.9 cm  1 画素   2.7 cm  比（遠端）1.08  比（近端）2.3
  C2:  25.23 -  50.63 m  球の半径  59.62 m  1 テクセル   5.8 cm  1 画素   5.4 cm  比（遠端）1.08  比（近端）2.2
  C3:  50.63 - 150.00 m  球の半径 176.65 m  1 テクセル  17.3 cm  1 画素  16.0 cm  比（遠端）1.08  比（近端）3.2
メモリ
  CSM 4 枚 2048x2048 D32: 64 MiB  D16: 32 MiB
  点光源 キューブ 6 面 1024x1024 D32: 24 MiB（1 灯）
  PCF のサンプル数: 3x3 = 9、5x5 = 25、ハードウェア比較なら 1 回で 2x2 の双線形
```

球の中心は軸上で区間の遠端に置いています。この置き方では遠端の比が分割によらず 1.08 になります。球が大きくなるぶん無駄は出ますが、カメラが回っても球の大きさが変わらず影がちらつきません（球フィット）。C0 の近端の比 125.9 は 0.1 m という極端に近い位置の画素が小さいためで、実際の画面ではその範囲はほとんど映りません。

## 現実の構成例

次の図は環境ごとの構成を並べたものです。

<svg class="fig flow" viewBox="0 0 680 270" role="img" aria-label="環境ごとの影の構成"><text x="14" y="22" class="fig-title">環境ごとの影の構成</text><rect x="12" y="40" width="212" height="200" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="118" y="62" text-anchor="middle" style="font-size:13px;font-weight:700">標準の PC・家庭用機</text><text x="22" y="90" style="font-size:11px">太陽: CSM 3〜4 枚 + PCF</text><text x="22" y="120" style="font-size:11px">接触部: コンタクト シャドウ</text><text x="22" y="150" style="font-size:11px">ローカル: スポット/キューブ(数を制限)</text><text x="22" y="180" style="font-size:11px">遠景: 距離場・ベイク</text><text x="22" y="210" style="font-size:11px">環境光の遮蔽: AO</text><rect x="234" y="40" width="212" height="200" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="340" y="62" text-anchor="middle" style="font-size:13px;font-weight:700">ハイエンド</text><text x="244" y="90" style="font-size:11px">太陽・主要ライト: 仮想シャドウ マップ</text><text x="244" y="120" style="font-size:11px">または レイトレース影 + デノイズ</text><text x="244" y="150" style="font-size:11px">多数のライト: キャッシュ・半影のレイ マーチ</text><rect x="456" y="40" width="212" height="200" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="562" y="62" text-anchor="middle" style="font-size:13px;font-weight:700">モバイル</text><text x="466" y="90" style="font-size:11px">太陽: 1〜2 カスケード + 軽い PCF</text><text x="466" y="120" style="font-size:11px">キャラ: ブロブ影</text><text x="466" y="150" style="font-size:11px">ローカル: 影なし・ベイク</text><text x="466" y="180" style="font-size:11px">遠景: ベイク</text></svg>

### 標準的な PC と家庭用機

太陽はカスケード シャドウ マップ（3 から 4 枚）と PCF（ノイズ付き、TAA で平均）にします。接触部の細かい影はコンタクト シャドウ、重要なローカル ライトはスポットやキューブにして数を制限し、アトラスにまとめます。遠景は距離場やベイク、キャラクターは専用のシャドウやカプセルの近似を使えます。環境光の遮蔽は [AO](../ao/index.md) で補います。

### ハイエンド（最新 GPU）

太陽と主要なライトには仮想シャドウ マップと半影のレイ マーチ、あるいはレイトレース影とデノイズを使います。多数のライトはキャッシュや時間方向の再利用でコストを抑えます。

### モバイル

太陽は 1 から 2 カスケードとサンプルを減らした軽い PCF にします。キャラクターはブロブ影、ローカル ライトは影なしかベイク、遠景はベイク済みです。

## 組み合わせの原則

- 遠近で方式を切り替える: 近くは高解像度や PCSS やコンタクトで細かく、遠くは距離場やベイクで粗く安く。
- 動的と静的で分ける: 静的な影はキャッシュやベイクにして、動的な物だけ毎フレーム更新する。
- 重要度で予算を配る: 主ライトと画面の中心に多くのコストを使う。
- 補助で穴を埋める: シャドウ マップの弱点（接触部、細部）をコンタクト シャドウや AO で補う。
- ノイズと時間蓄積: サンプルを減らし、TAA で平均してなめらかにする。

## 調整の順序

影の調整は順序が大切です。上から進めると手戻りが少なくなります。

1. 範囲と解像度: カスケードの数、最大距離、解像度を決める。ここが後ろのすべての前提になる。
2. 投影の安定化: 球フィットとテクセル スナップで、カメラが動いたときのちらつきを止める。
3. バイアス: 定数、傾き法線オフセットを組み合わせアクネとピーター パンニングを両立する（[Shadow Bias](bias/index.md)）。
4. フィルタ: PCF のサンプル数とカーネル、ノイズと TAA を決める。
5. 補助: コンタクト シャドウと AO を足す。
6. 例外処理: アルファ テスト、半透明、キャラクター、遠景を扱う。
7. 最適化: カリング、キャッシュ、更新頻度、LOD を入れる（[Shadow Cost](cost.md)）。

範囲と解像度を決める前にバイアスを調整しても、後で範囲を変えるとバイアスが合わなくなってやり直しになります。

## 太陽の影をまとめる HLSL

調整の順序を 1 本のピクセル シェーダーにしたものです。カスケードの選択、法線オフセットのバイアス、3 × 3 の PCF、境目のブレンド、コンタクト シャドウ、遠景のフェードを含みます。`fxc`（`ps_5_0`）で 2 つの `DEBUG_VIEW` どちらも警告なしでコンパイルして確かめました。実行はしていません。

### 定数とカスケード選択

```hlsl
// shadow_resolve.hlsl : 太陽の影 = カスケード選択 + PCF + コンタクト シャドウ + 遠景フェード。
// DEBUG_VIEW: 0=影の係数 1=カスケードの色分け
#ifndef DEBUG_VIEW
#define DEBUG_VIEW 0
#endif
#define CASCADES 4

Texture2DArray<float>       g_shadow_map : register(t0);   // カスケードの深度（配列の 1 枚 = 1 カスケード）
Texture2D<float>            g_contact    : register(t1);   // コンタクト シャドウの係数（1 = 影なし）
SamplerComparisonState      g_cmp        : register(s0);   // 比較サンプラー（ハードウェアの双線形 PCF）
SamplerState                g_point      : register(s1);   // 通常のサンプラー（コンタクト シャドウ用）

cbuffer ShadowParams : register(b0) {
  float4x4 g_world_to_shadow[CASCADES];   // ワールド → 各カスケードの UV（xy）と深度（z）
  float4   g_splits;                      // 各カスケードの遠端（ビュー深度、m）
  float    g_texel_world[CASCADES];       // 各カスケードの 1 テクセルの大きさ（m）。C++ 側で計算した値
  float    g_map_size;                    // シャドウ マップの 1 辺（テクセル）
  float    g_shadow_far;                  // 影を出す最大距離（m）
  float    g_fade_range;                  // 遠景フェードの幅（m）
  float    g_blend_range;                 // カスケードの境目をブレンドする幅（m）
};

// 深度 depth が属するカスケードを返す。
uint SelectCascade(float depth) {
  uint i = 0;
  [unroll] for (uint k = 0; k < CASCADES - 1; ++k) i += depth > g_splits[k] ? 1u : 0u;
  return i;
}
```

`g_splits` は各カスケードの遠端のビュー深度、`g_texel_world` は各カスケードの 1 テクセルの大きさ（m）で、先ほどの C++ で求めた値を渡します。`SelectCascade` は深度が各分割より大きいかを数えるだけです。分岐でなく加算にしているのは、GPU で分岐を避けるためです。

### PCF とバイアス

```hlsl
// 3x3 の PCF。比較サンプラー 1 回で 2x2 を双線形に混ぜるので、9 回で実質 4x4 のなめらかさになる。
float Pcf3x3(float2 uv, float z, uint cascade) {
  float texel = 1.0 / g_map_size, sum = 0;
  [unroll] for (int y = -1; y <= 1; ++y)
    [unroll] for (int x = -1; x <= 1; ++x)
      sum += g_shadow_map.SampleCmpLevelZero(g_cmp, float3(uv + float2(x, y) * texel, cascade), z);
  return sum / 9.0;
}

float ShadowAt(float3 world_pos, float3 n, float3 l, uint c) {
  // 法線オフセット: 面に近いほど、テクセルの大きさぶん法線方向へずらす（アクネとピーター パンニングを両立）。
  float n_dot_l = saturate(dot(n, l));
  float3 p = world_pos + n * g_texel_world[c] * (1.0 - n_dot_l) * 1.5;   // 係数 1.5 は一例（足した）
  float4 s = mul(float4(p, 1.0), g_world_to_shadow[c]);
  if (any(s.xy < 0.0) || any(s.xy > 1.0) || s.z > 1.0) return 1.0;       // 範囲の外は、影なし
  return Pcf3x3(s.xy, s.z - 0.0005, c);                                  // 定数バイアス 0.0005 は一例（足した）
}
```

`Pcf3x3` は比較サンプラーで 9 回読み平均を返します。`ShadowAt` の法線オフセットはテクセルの大きさに比例して法線方向へずらします。面が光に対して斜めなほど（`n_dot_l` が小さいほど）大きくずらします。係数 1.5 と定数バイアス 0.0005 は一例で、ここで足した値です。範囲の外は影なしにします。

### 合成

```hlsl
float4 main(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float3 world_pos = float3(0, 0, 0), n = float3(0, 1, 0), l = normalize(float3(0.3, 0.8, 0.5));   // 実際は G バッファから
  float depth = 10.0;                                        // 実際はビュー深度

  uint c = SelectCascade(depth);
  float shadow = ShadowAt(world_pos, n, l, c);

  // 境目のブレンド: 次のカスケードの手前 blend_range の間だけ、次のカスケードの値と混ぜる。
  if (c < CASCADES - 1) {
    float t = saturate((depth - (g_splits[c] - g_blend_range)) / g_blend_range);
    if (t > 0.0) shadow = lerp(shadow, ShadowAt(world_pos, n, l, c + 1), t);
  }

  shadow = min(shadow, g_contact.SampleLevel(g_point, uv, 0));    // 接触部の細かい影を重ねる（足した）
  float fade = saturate((g_shadow_far - depth) / g_fade_range);          // 遠くへ向けて影を消す
  shadow = lerp(1.0, shadow, fade);

#if DEBUG_VIEW == 1
  const float3 colors[CASCADES] = {float3(1, 0.3, 0.3), float3(0.3, 1, 0.3), float3(0.3, 0.3, 1), float3(1, 1, 0.3)};
  return float4(colors[c] * (0.5 + 0.5 * shadow), 1);
#else
  return float4(shadow.xxx, 1);
#endif
}
```

カスケードの境目では次のカスケードの手前 `g_blend_range` の間だけ次の値と混ぜます。これで境目の段差が見えにくくなります。コンタクト シャドウは `min` で重ねます。影が濃い方を採用するのでシャドウ マップで取りこぼした接触部の暗さが足されます。遠景は `g_fade_range` の幅でフェードして、影の最大距離で急に消えるのを避けます。`DEBUG_VIEW == 1` はカスケードを色分けして、どのカスケードを使っているかを確かめます。

## デバッグ

- 面にしま模様（アクネ）が出る: バイアス、法線オフセット、受け手平面バイアスを見直す（[Shadow Bias](bias/index.md)）。
- 影が物から浮く: バイアスが大きすぎる。コンタクト シャドウで補う。
- 影の縁がギザギザ: PCF のサンプル数かシャドウ マップの解像度を上げる。
- カメラの動きで影がちらつく: テクセル スナップと球フィットを入れる。
- カスケードの境目が見える: ブレンドの幅を足し、PCF をテクセルの大きさに合わせる。
- 影が欠ける: 視錐台の外にある遮蔽物を深度クランプとカリングの設定で含める。
- 遠くの影が突然消える: フェードを入れるか遠景を別の方式にする。
- 葉の影が四角: シャドウ パスでもアルファ テストをする。

見分けやすくするための可視化も用意します。カスケードの色分け（上の `DEBUG_VIEW == 1`）、シャドウ マップそのものを画面の隅に表示、影の係数だけの表示、バイアスをスライダーにして比べるの 4 つです。

## よくあるミス

??? failure "カスケードの境目で、影の濃さが段階的に変わる"
    カスケードの境目のブレンドが無いか狭すぎます。`g_blend_range` を広げ各カスケードの 1 テクセルの大きさに合わせた PCF にします。

??? failure "バイアスを調整したあとに範囲を変えて、またアクネが出る"
    調整の順序が逆です。範囲と解像度を先に決め安定化のあとにバイアスを合わせます。

??? failure "ローカル ライトすべてに影を付けて、メモリが足りない"
    点光源のキューブは 1 灯で 24 MiB（1024 × 1024、D32）です。影を付けるライトの数を制限し、アトラスにまとめます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 太陽はカスケードと PCF（ノイズ、TAA）が標準。ローカル ライトは数を制限する
    - [x] 補助はコンタクト シャドウ、AO、距離場
    - [x] ハイエンドは仮想シャドウ マップやレイトレース影、モバイルは軽いカスケードとブロブ
    - [x] 調整は範囲、安定化、バイアス、フィルタ、補助、例外、最適化の順

## 参考

このページは同じセクションの各ページ（Cascaded Shadow Maps、PCF、Shadow Bias、Shadow Cost など）と一般的な実装の知識をもとに書きました。次の資料はこのページを書くために読み直していません。カスケードの数字はこのページの C++ の出力でλ、画角、解像度、バイアスの係数は一例です。

- William T. Reeves, David H. Salesin, Robert L. Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987.（PCF）
- Rouslan Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007.
- William Donnelly, Andrew Lauritzen, "Variance Shadow Maps", Symposium on Interactive 3D Graphics and Games 2006.
- Daniel Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015, Advances in Real-Time Rendering in Games.
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018.

## 関連ページ

- [Shadows](index.md)
- [Shadow Map Basics](shadow-map-basics/index.md)
- [Cascaded Shadow Maps (CSM)](cascaded.md)
- [PCF](pcf.md)
- [Ray-Traced Shadows](ray-traced.md)
- [Shadow Cost](cost.md)
