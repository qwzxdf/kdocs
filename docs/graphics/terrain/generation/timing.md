---
title: When to Generate
tags:
  - 描画
---

# When to Generate

地形をノイズや侵食で作るとき最初に決めるのは「いつ作るか」です。制作中に作って結果を保存すれば、侵食のような重い処理を何千回でも回せますが、ゲームのデータは世界の広さに比例して増えます。プレイ中に作れば世界は無限に広くなりますが、1 フレームの予算で作れるのは軽いノイズだけで、チャンクの境目や再現性にも気を使います。

このページは地形生成のタイミングの選び方と実行時に作るときの落とし穴を説明します。継ぎ目、侵食の余白、フレームを止めない予算、決定性とキャッシュの 4 つは小さなプログラムで数字を確かめました。

!!! tip "ポイント"
    重い処理は事前に済ませて、細部は実行時に足すのが基本です。事前生成は高品質で侵食も使えますが、データが大きくなります。実行時の生成は無限の地形が作れますが、軽いノイズが中心です。ハイブリッドは事前の骨格に実行時の細部を足す形です。シード値と整数のハッシュを使えば、同じ地形を再現できます。

!!! info "このページを読む前に"
    - [Terrain Generation](index.md)（このセクション全体の地図と、読む順番）
    - [fBm](fbm.md)（このページのコードが使うノイズの重ね方）

## 4 つのタイミング

地形の生成（ノイズ、侵食、配置）をいつ実行するかは設計の最初の分かれ道です。次の図は 4 つの方式が制作時、ロード時、プレイ中のどこで動くかを表します。

<svg class="fig flow" viewBox="0 0 680 270" role="img" aria-label="4 つの生成タイミングが、制作時、ロード時、プレイ中のどこで動くか"><defs><marker id="tA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">いつ作るか：制作 → ロード → プレイ中</text><text x="130" y="48" style="font-size:12px;font-weight:600">制作時</text><text x="330" y="48" style="font-size:12px;font-weight:600">ロード時</text><text x="500" y="48" style="font-size:12px;font-weight:600">プレイ中</text><line x1="300" y1="54" x2="300" y2="226" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="470" y1="54" x2="470" y2="226" stroke="#94a3b8" stroke-dasharray="4 4"/><text x="14" y="83" style="font-size:12px;font-weight:600">オフライン</text><rect x="120" y="66" width="170" height="26" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="205.0" y="79" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">生成 + 手直し</text><rect x="310" y="66" width="150" height="26" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="385.0" y="79" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">読み込むだけ</text><text x="14" y="123" style="font-size:12px;font-weight:600">ロード時</text><rect x="310" y="106" width="150" height="26" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="385.0" y="119" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">数秒〜数十秒</text><text x="14" y="163" style="font-size:12px;font-weight:600">ストリーミング</text><rect x="480" y="146" width="190" height="26" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="575.0" y="159" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">近づいた範囲を少しずつ</text><text x="14" y="203" style="font-size:12px;font-weight:600">毎フレーム</text><rect x="480" y="186" width="190" height="26" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="575.0" y="199" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">GPU で毎フレーム</text><text x="14" y="248" style="font-size:12px">右の方式ほど、生成の時間を遅らせる。重い処理は左に寄せる。</text></svg>

### オフライン（ツール）

制作時に World Machine、Gaea、Houdini のような地形ツールや自作ツールで高さマップを作り結果をファイルに保存します。ゲームは読み込むだけです。侵食のような重い処理を何千ステップでも使えアーティストが気に入った形になるまで手で直せます。手作りのステージに向く方式です。代償は地形データの大きさが世界の広さに比例することです。

### ロード時

起動時やステージの開始時に生成します。数秒から数十秒待たせる代わりに保存するのはシード値だけで済みます。毎回違うランダム生成のステージに向きます。ロード時間の都合で侵食は軽いものに限ります。生成後に手で直すことはできません。

### ストリーミング（実行時）

プレイヤーが近づいた範囲だけをその場で生成します。世界の広さは事実上無限で保存するのはシードだけです。マインクラフトやノーマンズ スカイのような巨大あるいは無限の世界に向きます。1 タイルあたり数ミリ秒で終わらせないとフレームが止まるので、重い侵食は使いにくくなります。

### 毎フレーム

毎フレーム GPU で計算します。水面や砂漠の風紋のように動く地形に向きます。軽いノイズだけが対象です。

## 選ぶときの基準

次の表は観点ごとに 3 つの方式を並べたものです。

| 観点 | オフライン | ロード時 | ストリーミング |
| --- | --- | --- | --- |
| 生成の重さ | いくらでも | 数秒〜数十秒 | 1 タイル数 ms |
| 侵食 | 使える | 軽いものだけ | 難しい |
| 再現性 | 完全に同じ | シードから | 決定的な式が要る |
| ディスク | 大きい | 小さい | 小さい |
| 編集 | 手で直せる | 直せない | ルールを直す |
| 世界の広さ | 容量に比例 | メモリの範囲 | 事実上無限 |

生成の重さでほとんどが決まります。侵食を使いたいならオフラインです。侵食は周りの画素に影響されるため、チャンクを独立に作るストリーミングでは、継ぎ目を合わせるのが難しいからです。世界を無限にしたいならストリーミングで、軽いノイズに限ります。

再現性はセーブやマルチプレイの前提です。保存したデータは完全に同じ地形になりますが、シードから作る方式は環境による浮動小数点の差に注意が要ります。後の節で整数のハッシュを使う理由を説明します。

## オフライン生成の流れ

ほとんどの手作りのゲームはこの方式です。ツール側でノイズ、高さの変換、侵食、川、手での修正、配置のルール適用を順に行い高さマップ、スプラット マップ、配置データをバイナリで保存します。ゲームは読み込んで描画するだけです。

```text
ツール:  ノイズ → 高さの変換 → 侵食 → 川 → 手で修正 → 配置のルール適用
              ↓
          保存: 高さマップ、スプラット マップ、配置データ（バイナリ）
              ↓
ゲーム:  読み込んで、描画する
```

利点は 3 つです。品質は重い処理が使えアーティストが何度でも調整できます。起動は読み込むだけで速く環境が違っても結果が変わりません。

## 実行時の生成：落とし穴

### 継ぎ目をなくす

地形をチャンクに分けて作ると、隣のチャンクとの境目で形が食い違いやすくなります。直し方はワールド座標でノイズを引くことです。チャンクごとに座標がずれても、同じ式で同じ値になります。隣り合うチャンクは境界の頂点も同じ値で持ちます。

下のプログラムで確かめた結果は次のとおりです。ワールド座標でノイズを引くと隣り合うチャンクの境界の最大差は 0 です。チャンクごとの 0 から始まる座標で引くと最大差は約 0.61 で、高さの範囲（0 から 1）の半分を超える段差になります。

### 侵食に余白を付ける

侵食や平滑化は周りの画素に影響されます。チャンクを単独で処理すると端の画素は外側の情報が足りず隣のチャンクとの境目がずれます。そこで、チャンクの周りに処理の回数ぶんの余白を足して計算し、余白は捨てます。1 回の処理で影響が 1 画素ぶん広がるなら 8 回の処理には 8 画素の余白が必要です。

<svg class="fig flow" viewBox="0 0 680 270" role="img" aria-label="チャンクの周りに余白を足して侵食を計算し、余白は捨てる"><defs><marker id="tA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">侵食の余白：周りを足して計算し、余白は捨てる</text><rect x="150" y="50" width="260" height="180" rx="6" fill="rgba(229,170,40,0.22)" stroke="#e5aa28" stroke-width="2" stroke-dasharray="6 4"/><rect x="200" y="90" width="160" height="100" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5" stroke-width="2"/><text x="280" y="140" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">チャンク（65 × 65）</text><text x="280" y="68" text-anchor="middle" style="font-size:12px;font-weight:600">余白（侵食の回数ぶん）</text><line x1="150" y1="260" x2="200" y2="260" stroke="currentColor" stroke-width="2" marker-end="url(#tA)"/><text x="175" y="252" text-anchor="middle" style="font-size:11px">8 画素</text><text x="440" y="100" style="font-size:13px;font-weight:600">余白 0 画素</text><text x="540" y="100" style="font-size:13px">最大差 0.0195</text><text x="440" y="134" style="font-size:13px;font-weight:600">余白 4 画素</text><text x="540" y="134" style="font-size:13px">最大差 0.00037</text><text x="440" y="168" style="font-size:13px;font-weight:600">余白 8 画素</text><text x="540" y="168" style="font-size:13px">最大差 0</text><text x="440" y="214" style="font-size:12px">平滑化 8 回なら、余白 8 画素で一致する。</text></svg>

実験では平滑化を 8 回かけて、チャンク 1 枚だけで処理した右端の列と隣まで含めて処理した結果を比べました。余白 0 画素では最大差が約 0.0195、4 画素では約 0.00037、8 画素では 0 になります。余白が処理の回数に届くまで差は残ります。

### フレームを止めない

1 つのチャンクの生成に数十ミリ秒かかると、画面がカクつきます。対策は次のとおりです。

- 非同期で生成する: ワーカー スレッド（CPU）や非同期コンピュート（GPU）で、裏で作る。
- 予算を決める: 1 フレームに生成へ使う時間を制限する。たとえば 2 ms は 60 fps の 1 フレーム 16.7 ms の約 12 % である。
- 細かく分割する: 1 つのチャンクを数フレームに分けて少しずつ作る。
- 先読みする: プレイヤーが近づく前に方向を予測して作り始める。
- 低解像度から作る: 粗い地形を先に出し、後から細かくする（LOD と組み合わせる）。

予算の効果を数字で見積もります。プログラムでは 1 チャンクの仕事量を 65 × 65 頂点 × 6 層 = 25,350 単位、1 フレームの予算を 4,000 単位としました。1 枚あたり 25,350 / 4,000 = 約 6.3 フレームで、9 枚の生成には 9 × 25,350 / 4,000 を切り上げた 58 フレームかかります。60 fps なら約 1 秒です。移動が速いゲームは先読みの距離を長くしないと地形が間に合わず穴が見えます。

### 決定性を守る

実行時に同じ場所が同じ地形にならないとゲームが成り立ちません。セーブしても地形が違うマルチプレイで人によって地形が違うといった問題が起きます。

- 乱数: グローバルな乱数列を使わず座標から種を作る（[Placement Generation](placement.md)）。
- 浮動小数点: GPU が違うと `sin`、`cos`、`pow` の結果がわずかに違うことがある。整数のハッシュと基本的な演算だけを使い重要な値は CPU で計算する。
- 生成の順序: 順序が変わっても同じ結果になること。チャンクが他のチャンクに依存しないこと。
- 変更の保存: プレイヤーが地形を変えたら、元の地形からの差分を保存する。

## キャッシュ

実行時に生成した地形をディスクにキャッシュしておくと 2 回目以降の生成を省けます。キャッシュのキーはシード、チャンクの座標、生成アルゴリズムの版にします。アルゴリズムを変えたら版をキーに含めて古いキャッシュを無効にします。容量には上限を決め古いものから削除します（LRU）。

プログラムではシード、座標 (3, -2)、版を混ぜたハッシュをキーにしました。版 1 は `f3076159`、版 2 は `45be75b1` で版を上げるとキーが変わり古いキャッシュは自然に使われなくなります。

## 実際の組み合わせ

多くのゲームは 1 つの方式だけでなく組み合わせています。

- オフラインと実行時の配置: 地形は手作りで焼いて保存し、草や木の配置は実行時に GPU で生成する（Horizon Zero Dawn のような構成）。
- ロード時の生成と手作りの特別な場所: 全体はシードから生成し、拠点などの重要な場所だけ手作りの地形で上書きする。
- ストリーミングと低解像度の事前計算: 遠景は事前に作った粗い地形にして、近景だけ実行時に細かくする。

## 4 点を確かめるプログラム

ここまでの 4 点を 1 つのプログラムで確かめます。MSVC で `/W4` の警告なしにコンパイルして実行しました。ノイズは整数のハッシュによるバリュー ノイズで、fBm を 6 層重ねます。

### ハッシュとノイズ

```cpp
// terrain_timing.cpp : 実行時の地形生成で問題になる 4 点を、数字で確かめる。
//  1. 継ぎ目  2. 侵食の余白  3. 1 フレームの予算  4. キャッシュのキー
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <print>
#include <vector>

constexpr int kCells = 64;            // チャンク 1 枚のセル数（頂点は 65 × 65）
constexpr int kVerts = kCells + 1;

// 整数のハッシュ（GPU や環境が違っても同じ値になる。sin() は使わない）。
uint32_t Hash(int32_t x, int32_t z, uint32_t seed) {
  uint32_t h = seed ^ (uint32_t(x) * 0x9E3779B1u) ^ (uint32_t(z) * 0x85EBCA77u);
  h ^= h >> 15; h *= 0x2C1B3C6Du; h ^= h >> 12; h *= 0x297A2D39u; h ^= h >> 15;
  return h;
}
float Rand01(int32_t x, int32_t z, uint32_t seed) { return (Hash(x, z, seed) >> 8) * (1.0f / 16777216.0f); }

// バリュー ノイズ。格子点の乱数を、なめらかに補間する。
float ValueNoise(float x, float z, uint32_t seed) {
  int32_t xi = int32_t(std::floor(x)), zi = int32_t(std::floor(z));
  float fx = x - xi, fz = z - zi;
  fx = fx * fx * (3 - 2 * fx); fz = fz * fz * (3 - 2 * fz);       // smoothstep
  float a = Rand01(xi, zi, seed), b = Rand01(xi + 1, zi, seed);
  float c = Rand01(xi, zi + 1, seed), d = Rand01(xi + 1, zi + 1, seed);
  return (a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fz;
}

// fBm: 周波数を 2 倍、振幅を半分にしながら 6 層重ねる。
float Fbm(float wx, float wz, uint32_t seed) {
  float sum = 0, amp = 0.5f, freq = 1.0f / 64.0f;
  for (int o = 0; o < 6; ++o) { sum += amp * ValueNoise(wx * freq, wz * freq, seed + o); amp *= 0.5f; freq *= 2.0f; }
  return sum;
}
```

`Hash` は整数の掛け算とシフトだけで作ったハッシュです。`sin()` を使うハッシュ（シェーダーでよく見るもの）は、GPU や環境で結果がずれることがあるので使いません。`ValueNoise` は格子点の乱数を `smoothstep` で補間します。`Fbm` は周波数を 2 倍、振幅を半分にしながら 6 層重ねます。層ごとにシードを 1 ずつずらして、層どうしの相関を避けています。

### チャンクと継ぎ目

```cpp
using Grid = std::vector<float>;

// チャンク (cx, cz) の高さ。ワールド座標でノイズを引く。local_bug = true は「チャンクごとの 0〜1 座標」で引く誤り。
Grid MakeChunk(int cx, int cz, uint32_t seed, bool local_bug) {
  Grid g(kVerts * kVerts);
  for (int j = 0; j < kVerts; ++j)
    for (int i = 0; i < kVerts; ++i) {
      float wx = local_bug ? float(i) : float(cx * kCells + i);   // 誤り: 隣のチャンクと同じ座標になる
      float wz = local_bug ? float(j) : float(cz * kCells + j);
      g[j * kVerts + i] = Fbm(wx, wz, seed);
    }
  return g;
}

// 右隣のチャンクとの境界（左右の端の列）の最大差。
float SeamError(const Grid& left, const Grid& right) {
  float e = 0;
  for (int j = 0; j < kVerts; ++j) e = std::max(e, std::fabs(left[j * kVerts + kCells] - right[j * kVerts + 0]));
  return e;
}
```

`MakeChunk` はチャンク (cx, cz) の頂点 65 × 65 の高さを作ります。ワールド座標は `cx * 64 + i` で隣のチャンクの左端とこのチャンクの右端が、同じ座標になります。`local_bug` を真にするとチャンクごとに 0 から始まる座標で引く誤りを再現します。`SeamError` は境界の 2 列の最大差を返します。

### 侵食（平滑化）と領域

```cpp
// 簡易な「侵食」: 周囲の平均に近づける平滑化を iters 回。1 回で影響が 1 画素ぶん広がる。
Grid Smooth(const Grid& in, int w, int h, int iters) {
  Grid a = in, b = in;
  for (int t = 0; t < iters; ++t) {
    for (int j = 1; j < h - 1; ++j)
      for (int i = 1; i < w - 1; ++i) {
        float s = 0;
        for (int dj = -1; dj <= 1; ++dj) for (int di = -1; di <= 1; ++di) s += a[(j + dj) * w + i + di];
        b[j * w + i] = s / 9.0f;
      }
    a = b;
  }
  return a;
}

// ワールド座標 [x0, x0+w) × [z0, z0+h) の高さを作る。
Grid MakeRegion(int x0, int z0, int w, int h, uint32_t seed) {
  Grid g(w * h);
  for (int j = 0; j < h; ++j) for (int i = 0; i < w; ++i) g[j * w + i] = Fbm(float(x0 + i), float(z0 + j), seed);
  return g;
}
```

`Smooth` は周囲 3 × 3 の平均を取る平滑化を `iters` 回かけます。端の画素は外側がないのでそのままにします。1 回かけるごとに影響は 1 画素ぶん広がります。`MakeRegion` はワールド座標の範囲を指定して高さを作ります。余白は `x0` と `z0` を負の方向にずらして取ります。

### 実験の本体

```cpp
int main() {
  const uint32_t seed = 2026;

  std::println("1. 継ぎ目（隣り合う境界の最大差）");
  std::println("   ワールド座標: {:.6f}", SeamError(MakeChunk(0, 0, seed, false), MakeChunk(1, 0, seed, false)));
  std::println("   チャンクごとの座標: {:.6f}", SeamError(MakeChunk(0, 0, seed, true), MakeChunk(1, 0, seed, true)));

  std::println("2. 侵食の余白（平滑化 8 回。チャンク 1 枚だけで処理した右端の列と、隣まで含めて処理した結果の最大差）");
  const int iters = 8;
  Grid full = Smooth(MakeRegion(0, 0, 2 * kCells + 1, kVerts, seed), 2 * kCells + 1, kVerts, iters);   // 正解: 2 枚ぶんを一度に
  for (int margin : {0, 4, 8}) {
    const int w = kVerts + 2 * margin, h = kVerts + 2 * margin;
    Grid s = Smooth(MakeRegion(-margin, -margin, w, h, seed), w, h, iters);   // このチャンクの周りに margin 画素を足して処理
    float e = 0;
    for (int j = 9; j < kVerts - 9; ++j)                                       // 上下の端の影響を避ける
      e = std::max(e, std::fabs(s[(j + margin) * w + kCells + margin] - full[j * (2 * kCells + 1) + kCells]));
    std::println("   余白 {} 画素: {:.6f}", margin, e);
  }

  std::println("3. 予算（1 フレーム 4000 単位、チャンク 1 枚 = 65 × 65 × 6 層 = 25350 単位）");
  const int cost = kVerts * kVerts * 6, budget = 4000, chunks = 9;
  int done = 0, frame = 0, spent = 0;
  while (done < chunks) {
    ++frame; int left = budget;
    while (left > 0 && done < chunks) {
      int take = std::min(left, cost - spent); left -= take; spent += take;
      if (spent == cost) { ++done; spent = 0; }
    }
  }
  std::println("   9 枚の生成に {} フレーム（1 枚あたり約 {:.1f} フレーム）", frame, double(frame) / chunks);

  std::println("4. キャッシュのキー（シード・座標・アルゴリズムの版）");
  for (uint32_t ver : {1u, 2u}) std::println("   版 {}: {:08x}", ver, Hash(3, -2, seed ^ (ver * 0x1000193u)));
  return 0;
}
```

```text title="実行結果"
1. 継ぎ目（隣り合う境界の最大差）
   ワールド座標: 0.000000
   チャンクごとの座標: 0.609735
2. 侵食の余白（平滑化 8 回。チャンク 1 枚だけで処理した右端の列と、隣まで含めて処理した結果の最大差）
   余白 0 画素: 0.019525
   余白 4 画素: 0.000373
   余白 8 画素: 0.000000
3. 予算（1 フレーム 4000 単位、チャンク 1 枚 = 65 × 65 × 6 層 = 25350 単位）
   9 枚の生成に 58 フレーム（1 枚あたり約 6.4 フレーム）
4. キャッシュのキー（シード・座標・アルゴリズムの版）
   版 1: f3076159
   版 2: 45be75b1
```

実験 2 では正解として 2 枚ぶんの領域を一度に平滑化した結果を使い余白の違うチャンク単独の結果と、境界の列で比べています。上下の端の影響を避けるため行は 9 から 55 に絞りました。実験 3 の「仕事量の単位」はこのページで決めた目安で、実機の時間ではありません。実機ではチャンク 1 枚の生成にかかる時間を測って、予算を ms で決めてください。

## よくあるミス

??? failure "実行時に侵食を計算して重い"
    侵食は数百から数千のステップを回すのが普通で、1 フレームの予算に入りません。事前に計算して結果を保存するか軽い平滑化に置き換えます。

??? failure "チャンクの境界に段差が出る"
    チャンクごとに 0 から始まる座標でノイズを引いています。ワールド座標で引き境界の頂点を隣と同じ値にします。侵食する場合は処理の回数ぶんの余白を足します。

??? failure "同じシードなのに、環境によって地形が違う"
    `sin` を使ったハッシュは GPU やコンパイラで結果がずれることがあります。整数のハッシュに替え重要な値は CPU で計算します。

??? failure "アルゴリズムを変えたら、古いキャッシュの地形が混ざる"
    キャッシュのキーにアルゴリズムの版を入れていません。版をキーに含めて変更したら上げます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 重い処理は事前、細部は実行時
    - [x] ワールド座標でノイズを引き侵食には処理の回数ぶんの余白を付ける
    - [x] 1 フレームの予算で割って、必要なフレーム数を見積もる
    - [x] 整数のハッシュで再現し、キャッシュのキーに版を入れる

## 参考

このページは同じセクションの各ページ（Terrain Generation、fBm、Placement Generation）と一般的な実装の知識をもとに書きました。次の資料はこのページを書くために読み直していません。実験の数字はこのページのプログラムの出力です。

- Jaap van Muijden, "GPU-Based Run-Time Procedural Placement in Horizon Zero Dawn", Game Developers Conference 2017.
- Eric Galin, Eric Guérin, Adrien Peytavie, Guillaume Cordonnier, Marie-Paule Cani, Bedrich Beneš, James Gain, "A Review of Digital Terrain Modeling", Computer Graphics Forum (Eurographics 2019 STAR).
- David S. Ebert, F. Kenton Musgrave, Darwyn Peachey, Ken Perlin, Steven Worley, "Texturing and Modeling: A Procedural Approach", 3rd Edition, Morgan Kaufmann, 2002.（fBm、マルチフラクタル、リッジ ノイズ）
- Mark Jarzynski, Marc Olano, "Hash Functions for GPU Rendering", Journal of Computer Graphics Techniques, Vol. 9, No. 3, 2020.（整数のハッシュ）

## 関連ページ

- [Terrain Generation](index.md)
- [fBm](fbm.md)
- [Placement Generation](placement.md)
- [Chunking](../heightmap-mesh/chunks.md)
