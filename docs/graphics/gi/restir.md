---
title: ReSTIR
tags:
  - 描画
---

# ReSTIR

ゲームのシーンには光源が数千個あることがあります。ピクセルごとに全部の光源を調べるのは重すぎるので、普通は光源を 1 つだけ選んでその寄与を計算し、ノイズを覚悟します。ところが、光源を一様に選ぶと暗い光源や遮蔽された光源を選ぶ回数が多く、画面はざらざらです。光源を明るさや距離に応じて賢く選ぶには、光源を木構造に整理する方法がありますが、動的な光源が多いと木の更新が負担になります。

ReSTIR（Reservoir-based Spatio-Temporal Importance Resampling）は、<strong>「良さそうな光源」を隣のピクセルや前のフレームから借りてきて、選び直す</strong>方式です。1 ピクセルあたりのサンプル数を増やさずに周りの画素と過去のフレームが選んだ結果を集めて、実質的な候補の数を何十倍にもします。光源の整理も要りません。

このページは ReSTIR の土台になる RIS、候補を溜めるリザーバー、時間と空間の再利用、履歴の上限を式と数値実験とコードで説明します。最後に、ReSTIR GI と PT がどう拡張しているかも読んだ範囲で書きます。

!!! tip "ポイント"
    土台は重要度に基づくリサンプリング（RIS）です。候補を複数ランダムに選んで重みに従って 1 つに絞ります。絞った結果を持ち運ぶ入れ物がリザーバーで、必要な情報は選ばれたサンプルと重みの合計などです。リザーバーどうしは混ぜられるので、隣のピクセル（空間）と前のフレーム（時間）から借りれば、実質のサンプル数が増えます。借りた候補が今のピクセルで有効かは確認しなければなりません。履歴の長さには上限を設けます。

!!! info "このページを読む前に"
    - [Global Illumination (GI)](index.md)
    - [Ray-Traced GI](rt-gi/index.md)（レイを飛ばして間接光を求める基本と、ノイズ）
    - [Monte Carlo Integration](theory/monte-carlo.md)（サンプルの重み `f / p` で積分を推定する考え方）

## 1 フレームの流れ

ReSTIR は 1 フレームの中で次の 4 つを順に行います。

<svg class="fig flow" viewBox="0 0 680 230" role="img" aria-label="ReSTIR の 1 フレーム。初期候補、時間の再利用、空間の再利用、影レイと積分"><defs><marker id="rsA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">1 フレームの流れ</text><rect x="12" y="50" width="148" height="62" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="86.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">初期候補</text><text x="86.0" y="90.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px">ライトを M 個選び RIS</text><line x1="160" y1="81" x2="179" y2="81" stroke="currentColor" stroke-width="2" marker-end="url(#rsA)"/><rect x="179" y="50" width="148" height="62" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="253.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">時間の再利用</text><text x="253.0" y="90.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px">前フレームの同じ画素</text><line x1="327" y1="81" x2="346" y2="81" stroke="currentColor" stroke-width="2" marker-end="url(#rsA)"/><rect x="346" y="50" width="148" height="62" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="420.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">空間の再利用</text><text x="420.0" y="90.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px">近くの画素から借りる</text><line x1="494" y1="81" x2="513" y2="81" stroke="currentColor" stroke-width="2" marker-end="url(#rsA)"/><rect x="513" y="50" width="148" height="62" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="587.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">積分</text><text x="587.0" y="90.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px">選んだ 1 つに影レイ</text><text x="14" y="150" style="font-size:12px;font-weight:600">各段階で持ち運ぶのは、リザーバー（選ばれたサンプル、重みの合計、confidence、W）だけ。</text><text x="14" y="172" style="font-size:12px">時間と空間の再利用では、相手のリザーバーを自分の目標関数で評価し直して併合する。</text><text x="14" y="194" style="font-size:12px">影レイは重いので、最後に選ばれた 1 つにだけ飛ばす。</text></svg>

まず画素ごとに候補を少数選び RIS で 1 つに絞ります（初期候補）。次に、動きベクトルで前フレームの同じ画素を探し、そのリザーバーと混ぜます（時間）。さらに近くの画素のリザーバーとも混ぜます（空間）。最後に、選ばれた 1 つのサンプルにだけ影レイを飛ばして、色を求めます。影のような重い判定を最後の 1 本にしか使わないのが、少ないレイで済む理由です。

## 重要度に基づくリサンプリング（RIS） {#ris}

RIS は「簡単に引ける分布」から候補を M 個引き重みに比例した確率で 1 つを選ぶ手順です。講義ノート（A Gentle Introduction to ReSTIR）の定義は次の 5 つの手順です。

1. 共通の領域から候補 `X1, …, XM` を取る。
2. 各候補に再サンプリング用の MIS 重み `m_i(X_i)` を求める。
3. 各候補の再サンプリング重みを `w_i = m_i(X_i) · p̂(X_i) · W_Xi` とする。
4. `w_i` に比例する確率で候補の中から `X` を 1 つ選ぶ。
5. 選んだサンプルの不偏の寄与重みを `W_X = (1 / p̂(X)) · Σ w_j` とする。

ここで `p̂` は目標関数です。積分したい関数 `f` に近く安く計算できる関数を選びます。直接光なら BRDF と距離の減衰と光源の明るさを掛けて、影の判定は入れません。`W_Xi` は候補 `X_i` を引いた確率密度の逆数に相当する重みで、一様に引いたなら `1 / p` です。

選ばれた `X` は元の分布よりも `p̂` に比例する分布に近くなります。候補が多いほど近づきます。使うときは選んだ候補の古い重み `W_Xs` ではなく、手順 5 の `W_X` を使います。古い重みを使うと偏りが出ます。サンプリングの過程そのものを重みに反映する必要があるからです。

積分の推定値は `f(X) · W_X` です。これは `p̂` が `f` の値が非零の所で正になり候補が `f` の領域を覆っているなら、期待値が真の積分に一致します（不偏）。`p̂(x) = 0` の場所は選ばれないので `f(x) ≠ 0` なのに `p̂(x) = 0` となるように目標関数を作ってはいけません。全部の重みが 0 で何も選べなかったときは、空のサンプルを返して `W = 0` にします。選び直してはいけません。選び直すと偏ります。

候補が同じ分布から独立に引かれているなら `m_i = 1/M` を使えます。異なる分布の候補（別の画素から借りた候補など）を混ぜるときは、`1/M` では偏るので別の MIS 重みが要ります。ノートの目安は「`1/M` の重みを使ってよいのは、すべての入力が同じ分布のときだけ」です。

## リザーバー {#reservoir}

RIS をそのまま実装すると、M 個の候補を全部メモリに置いてから、2 回目の走査で選ぶことになります。GPU では面倒です。そこで、重み付きリザーバー サンプリング（WRS）を使います。候補を 1 つずつ見ながら「今のところ選ばれているサンプル」を確率的に入れ替えていく方法で、全部を溜めずに 1 回の走査で済みます。

リザーバーが持つ値は次のとおりです。

- 選ばれているサンプル `Y`
- これまでに見た重みの合計 `w_sum`
- 見た候補の数（confidence）`c`
- 不偏の寄与重み `W_Y`

更新は新しい候補 `X_i` の重み `w_i` を `w_sum` に足し、確率 `w_i / w_sum` で `Y` を `X_i` に入れ替えます。ストリームが終わったら `W_Y = w_sum / p̂(Y)` で寄与重みを求めます。講義ノートの Algorithm 2 の流れです。

<svg class="fig flow" viewBox="0 0 680 270" role="img" aria-label="リザーバーの更新。重み 1、3、6 の候補を順に見ると、最後に選ばれている確率は重みに比例する"><text x="14" y="22" class="fig-title">リザーバーの更新（重み 1、3、6 の 3 候補）</text><rect x="14" y="40" width="180" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="104.0" y="62.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">候補 A（重み 1）</text><rect x="214" y="40" width="130" height="44" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="279.0" y="62.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">w_sum = 1</text><text x="364" y="66" style="font-size:12px">Aに入れ替わる確率 1/1 = 100%</text><rect x="14" y="96" width="180" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="104.0" y="118.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">候補 B（重み 3）</text><rect x="214" y="96" width="130" height="44" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="279.0" y="118.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">w_sum = 4</text><text x="364" y="122" style="font-size:12px">Bに入れ替わる確率 3/4 = 75%</text><rect x="14" y="152" width="180" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="104.0" y="174.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">候補 C（重み 6）</text><rect x="214" y="152" width="130" height="44" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="279.0" y="174.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">w_sum = 10</text><text x="364" y="178" style="font-size:12px">Cに入れ替わる確率 6/10 = 60%</text><text x="14" y="222" style="font-size:12px;font-weight:600">最後に残る確率</text><rect x="14" y="232" width="64" height="28" fill="rgba(76,139,245,0.20)" stroke="#4c8bf5" stroke-width="2"/><text x="46" y="251" text-anchor="middle" style="font-size:12px;font-weight:600">A  10%</text><rect x="78" y="232" width="192" height="28" fill="rgba(76,139,245,0.30)" stroke="#4c8bf5" stroke-width="2"/><text x="174" y="251" text-anchor="middle" style="font-size:12px;font-weight:600">B  30%</text><rect x="270" y="232" width="384" height="28" fill="rgba(76,139,245,0.45)" stroke="#4c8bf5" stroke-width="2"/><text x="462" y="251" text-anchor="middle" style="font-size:12px;font-weight:600">C  60%</text></svg>

図は重み 1、3、6 の候補を順に見る様子です。最初の候補 A は必ず入ります（`1/1`）。B が入れ替わる確率は 3/4、C は 6/10 です。最終的に残る確率を計算すると、A は `1/1 × 1/4 × 4/10 = 0.1`、B は `3/4 × 4/10 = 0.3`、C は `0.6` で重みの比 1:3:6 に一致します。この性質のおかげで全部の候補を覚えなくても、重みに比例した選択になります。

## 時間と空間で借りる {#reuse}

リザーバーには 2 つを 1 つに混ぜられる性質があります。リザーバー `s` のサンプルを別の画素 `j` の候補として扱い重みを `p̂_j(Y_s) · W_s · c_s` にして更新するだけです。この性質を使うと前のフレームの同じ画素（時間）や近くの画素（空間）のリザーバーを、自分の候補に足せます。

講義ノートの再利用の流れは次の 4 段階です。

1. 初期候補: 独立した候補から RIS で 1 つ作る。
2. 空間の再利用: 近くの画素（円や四角の範囲から選ぶ）のリザーバーと RIS し直す。繰り返すほど分布は良くなるが、相関も増える。
3. 時間の再利用: 動きベクトルで前フレームの画素を見つけそのリザーバーと RIS する。毎フレーム行うとサンプルが時間をまたいで引き継がれ分布が改善し続ける。
4. 積分: 選ばれたサンプルで `f(X) · W_X` を計算する。

ノートは実装は「初期候補だけで検証 → 空間の再利用 → 時間の再利用（動きなし）」の順に、1 つずつ検証しながら進めるよう勧めています。検証とは静止画を大量に平均して、パス トレーシングの正解に収束することを確かめることです。

借りるときの MIS 重みは一般化バランス ヒューリスティックを勧めています。`m_i(x) = p̂_i(x) / Σ p̂_j(x)` で各画素 j の目標関数（その画素の視線とシェーディング点に依存する）で `x` を評価した値の比です。時間の再利用では前フレームの目標関数が要ります。完全に偏りを消すには前フレームのシーンで可視性を調べる必要があり前フレームの加速構造を保持することになります。

借りる画素を選ぶ判断では 1 つ注意があります。隣の画素をそのリザーバーに入っているサンプルを見て選んではいけません。サンプルの中身で選ぶと偏ります。法線や深度のような G バッファの値で選ぶのは構いません。

## 履歴の長さ {#history}

時間の再利用で前のフレームと新しいサンプルを同じ重みで混ぜると、毎フレーム履歴の約 50 % を失います。そこで、サンプルに confidence `c` を持たせて、MIS 重みを `m_i(x) = c_i · p̂_i(x) / Σ c_j · p̂_j(x)` にします。リザーバーを混ぜたときの confidence は、入力の合計 `c1 + c2` です。実際の実効サンプル数の上限の見積もりですが、より正確な値を求めるのが難しいので、合計を使います。

そのまま足し続けると confidence は指数的に増えます。新しいサンプルの相対的な重みが指数的に小さくなり古い履歴に引きずられて、間違った結果に収束します。そこで、confidence に上限を設けます。ノートによると上限は 5 から 30 程度で、20 から始めるのが良い目安です。上限はノイズと相関のバランスを決める値です。上限を大きくするとノイズは減りますが、相関が増えて残像が出やすくなります。

上限の効果を数字で見積もります。時間の再利用だけを考えて毎フレームの新しいサンプルの confidence を 1、履歴の上限を 20 とします。履歴の重み 20 に新しいサンプルの重み 1 を足すので、新しいサンプルが占める割合は `1 / (20 + 1)` で約 4.8 % です。これは指数移動平均で更新率 α = 0.048 に相当し（ここは、このページでの導出です）、時定数は約 21 フレームです。60 fps なら約 0.35 秒かけて、ライトの変化に追従します。上限を 5 にすると α は約 17 %、時定数は約 6 フレームで変化への追従は速くなりますが、ノイズが減る量は小さくなります。

## 数値実験：偏りなくノイズが減る

RIS とリザーバーの併合が、偏りなくノイズを減らすことを小さなプログラムで確かめます。ライトが 1000 個ありある画素に対する各ライトの寄与 `f` は桁違いにばらつきます。目標関数 `p̂` は遮蔽を知らない安い見積もりで、実際には 7 割のライトが遮蔽されて `f = 0` です。真の積分は `Σ f` で推定値の平均が真値に一致するか標準偏差がどう減るかを見ます。

### 共通の部分

```cpp
// restir_toy.cpp : RIS・リザーバー・リザーバーの併合が、偏りなく分散を減らすことを確かめる。
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <random>
#include <vector>

constexpr int kLights = 1000;

struct Rng {
  std::mt19937_64 gen{12345};
  double Next() { return std::uniform_real_distribution<double>(0.0, 1.0)(gen); }
  int Index(int n) { return static_cast<int>(Next() * n) % n; }
};

// 1 画素から見た各ライトの寄与 f と、安い見積もり p_hat（遮蔽を知らない）。
std::vector<double> f, p_hat;

struct Reservoir {
  int y = -1;           // 選ばれたライト（-1 は空）
  double w_sum = 0.0;   // 重みの合計
  int m = 0;            // 見た候補の数（confidence）
  double w = 0.0;       // 不偏の寄与重み W_Y
  void Update(int x, double weight, Rng* rng) {
    w_sum += weight;
    if (rng->Next() < weight / w_sum) y = x;   // 重みに比例して入れ替える
  }
  void Finish() { w = (y >= 0 && p_hat[y] > 0.0) ? w_sum / p_hat[y] : 0.0; }
};

```

`Reservoir` がリザーバーそのものです。`Update` は重みを足して `w / w_sum` の確率で入れ替えます。`Finish` で `W = w_sum / p̂(Y)` を求め `p̂(Y) = 0` のときは `W = 0` にして 0 割りを避けます。`f` と `p̂` は別の配列で `f` が実際の寄与、`p̂` が候補を選ぶときの安い見積もりです。

### 候補と併合

```cpp
// 一様に M 個のライトを選び、リザーバーに入れる（m_i = 1/M, W_Xi = 1/p = kLights）。
Reservoir Candidates(int m, Rng* rng) {
  Reservoir r;
  for (int i = 0; i < m; ++i) {
    int x = rng->Index(kLights);
    r.Update(x, (1.0 / m) * p_hat[x] * kLights, rng);
  }
  r.m = m;
  r.Finish();
  return r;
}

// 2 つのリザーバーを併合する。m_i = c_i / sum(c)、w_i = m_i * p_hat(Y_i) * W_i（同じ p_hat の場合）。
Reservoir Merge(const Reservoir& a, const Reservoir& b, Rng* rng) {
  Reservoir r;
  const double c = static_cast<double>(a.m + b.m);
  for (const Reservoir* s : {&a, &b}) {
    if (s->y >= 0) r.Update(s->y, (s->m / c) * p_hat[s->y] * s->w, rng);
  }
  r.m = a.m + b.m;
  r.Finish();
  return r;
}

struct Stat { double mean, sd; };
template <class F> Stat Measure(F estimate, int trials) {
  double s = 0, s2 = 0;
  for (int i = 0; i < trials; ++i) { double v = estimate(); s += v; s2 += v * v; }
  double mean = s / trials;
  return {mean, std::sqrt(s2 / trials - mean * mean)};
}

```

`Candidates` は一様にライトを引き `m_i = 1/M`、`W_Xi = kLights`（一様なので確率の逆数）で重みを作ります。`Merge` は 2 つのリザーバーを併合します。`m_i = c_i / Σ c` を使うので `c` の合計が分母に入る点が、1/M とは違います。同じ `p̂` を使う実験なので評価し直しは要りません。実際の ReSTIR では隣の画素の `p̂` は自分の画素と違うので、`p̂_現在(Y)` で評価し直します（HLSL の `Merge` を参照）。

### 実験の本体と結果

```cpp
int main() {
  Rng rng;
  f.resize(kLights); p_hat.resize(kLights);   // 1000 個のライトの、実際の寄与と安い見積もり
  double truth = 0.0;
  for (int k = 0; k < kLights; ++k) {
    // 明るさは e^-3 から e^3 の幅（約 400 倍）でばらつく
    double base = std::exp(2.0 * (rng.Next() - 0.5) * 3.0);   // 明るさは桁違いにばらつく
    p_hat[k] = base;                                          // 安い見積もり: 遮蔽を知らない
    f[k] = (rng.Next() < 0.7) ? 0.0 : base;                   // 実際は 7 割が遮蔽されて寄与 0
    truth += f[k];
  }
  const int trials = 200000;   // 平均と標準偏差を安定させるための試行回数
  // 平均/真値 が 1 なら偏りなし。標準偏差/真値 が小さいほどノイズが少ない。
  auto report = [&](const char* name, Stat s) {
    std::printf("%-28s 平均/真値 %.3f  標準偏差/真値 %.3f\n", name, s.mean / truth, s.sd / truth);
  };
  report("一様 1 個", Measure([&] { return f[rng.Index(kLights)] * kLights; }, trials));
  // RIS: 候補を m 個引いて 1 つに絞る。m が増えるほど p_hat に近い分布になる。
  for (int m : {4, 16, 64}) {
    char name[64]; std::snprintf(name, sizeof name, "RIS M=%d", m);
    report(name, Measure([&] { Reservoir r = Candidates(m, &rng); return r.y >= 0 ? f[r.y] * r.w : 0.0; }, trials));
  }
  // 4 個ずつ引いたリザーバーを 3 回併合する。候補は合計 16 個ぶんになる。
  report("併合 4 x (M=4) = 16", Measure([&] {
    Reservoir r = Candidates(4, &rng);
    for (int i = 0; i < 3; ++i) r = Merge(r, Candidates(4, &rng), &rng);
    return r.y >= 0 ? f[r.y] * r.w : 0.0; }, trials));
  return 0;
}
```

```text title="実行結果"
一様 1 個                 平均/真値 0.996  標準偏差/真値 3.122
RIS M=4                      平均/真値 1.011  標準偏差/真値 2.016
RIS M=16                     平均/真値 1.002  標準偏差/真値 1.605
RIS M=64                     平均/真値 0.999  標準偏差/真値 1.483
併合 4 x (M=4) = 16        平均/真値 1.003  標準偏差/真値 1.603
```

<svg class="fig flow" viewBox="0 0 680 248" role="img" aria-label="標準偏差を真値で割った値。一様 1 個は 3.12、RIS M=16 は 1.61、4 つの併合も 1.60"><text x="14" y="22" class="fig-title">推定値の標準偏差 ÷ 真値（小さいほどノイズが少ない）</text><text x="14" y="57" style="font-size:12px;font-weight:600">一様 1 個</text><rect x="170" y="44" width="321" height="22" rx="4" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="499" y="60" style="font-size:12px">3.12</text><text x="14" y="91" style="font-size:12px;font-weight:600">RIS  M=4</text><rect x="170" y="78" width="207" height="22" rx="4" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="385" y="94" style="font-size:12px">2.02</text><text x="14" y="125" style="font-size:12px;font-weight:600">RIS  M=16</text><rect x="170" y="112" width="165" height="22" rx="4" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="343" y="128" style="font-size:12px">1.60</text><text x="14" y="159" style="font-size:12px;font-weight:600">RIS  M=64</text><rect x="170" y="146" width="152" height="22" rx="4" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="330" y="162" style="font-size:12px">1.48</text><text x="14" y="193" style="font-size:12px;font-weight:600">併合 4 × (M=4)</text><rect x="170" y="180" width="165" height="22" rx="4" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="343" y="196" style="font-size:12px">1.60</text><text x="14" y="236" style="font-size:12px">下の C++ の実行結果（20 万回の平均）。併合した 16 個は、RIS の M=16 とほぼ同じ。</text></svg>

平均が真値の 1 に一致しているので、偏りはありません。標準偏差は一様に 1 個選ぶと真値の 3.12 倍、RIS で M=4 にすると 2.02 倍、M=16 で 1.61 倍に減ります。M=64 でも 1.48 倍までしか下がりません。`p̂` が遮蔽を知らないので 7 割の遮蔽されたライトを選ぶ確率が残るためです。ここが候補を増やしても減らないノイズの下限です。

注目するのは最後の行です。4 個ずつ引いたリザーバーを 4 つ併合した結果は、標準偏差が 1.603 で 16 個を一度に RIS した結果の 1.605 とほぼ同じです。併合は候補を直接増やしたのと同じ効果をリザーバー 4 つ（それぞれ 4 個ずつの安い作業）で得ています。ReSTIR が隣の画素の作業を再利用して、画素あたりの候補を実質的に増やしているのは、これと同じことです。

この実験は全ての画素で `f` と `p̂` が同じという理想的な条件です。実際の画素は、法線や位置が違うので借りたサンプルは自分の `f` に合いません。次の節の借りてよいかの判断が要ります。

## 借りてよい画素の判断 {#reject}

隣の画素のサンプルが自分の画素に有効とは限りません。講義ノートの例はイソギンチャクのように近くの画素の法線がほぼ逆向きになる場所です。両方に寄与する経路の集合がほとんど空なので、借りるとむしろノイズが増えます。借りる画素を除く判断が要ります。

判断の基準は法線、深度、材質が大きく違わないことです。これらの判断はサンプルの中身を見ず G バッファの値だけで行えば、偏りを生みません。サンプルの中身で判断すると条件付き確率の世界に入り偏ります。

この除外は `1/M` の重みを使うときの偏りを減らす近似にもなります。正しい MIS（バランス ヒューリスティック）の計算は `O(M²)` で、M が大きいと重いので `1/M` の重みを使って、除外で偏りを減らす実装があります。ノートはこの除外は Veach のカットオフ ヒューリスティックの近似と見られると説明しています。正しい重みを安く求める方法として、寄与 MIS 重み（選ばれたサンプルの重みだけを評価する方法）などもありますが、このページでは扱いません。

## コンピュート シェーダーの骨組み

ここまでを HLSL のコンピュート シェーダーにします。ライトは点光源だけ影レイは省略した簡易版です。`fxc`（`cs_5_0`）でコンパイルして確かめました。実行はしていません。影レイを飛ばす最後のパスと動きベクトルの生成は含みません。

### データと目標関数

```hlsl
// restir_di.hlsl : ReSTIR DI の骨組み（初期候補 → 時間 → 空間）。点光源だけ・影レイは省略した簡易版。
#define NUM_LIGHTS 4096
#define INITIAL_CANDIDATES 4
#define CONFIDENCE_CAP 20        // 履歴の上限。講義ノートの目安は 5〜30、20 から始めるとよい
#define SPATIAL_NEIGHBORS 4
#define SPATIAL_RADIUS 16.0      // 画素。一例（足した）

struct Light { float3 position; float intensity; float3 color; float pad; };

struct Reservoir {
  uint  light;       // 選ばれたライトの番号（0xFFFFFFFF は空）
  float w_sum;       // 重みの合計
  float confidence;  // c。見た候補の実効的な数（上限あり）
  float w;           // 不偏の寄与重み W_Y
};

StructuredBuffer<Light>       g_lights    : register(t0);
Texture2D<float4>             g_position  : register(t1);  // xyz = ワールド位置、w = 線形深度
Texture2D<float4>             g_normal    : register(t2);  // xyz = 法線
Texture2D<float2>             g_motion    : register(t3);  // 画素単位の動き（現在 → 前フレーム）
StructuredBuffer<Reservoir>   g_prev      : register(t4);  // 前フレームのリザーバー
RWStructuredBuffer<Reservoir> g_cur       : register(u0);
cbuffer Frame : register(b0) { uint2 g_size; uint g_frame; uint g_pad; };

uint Pcg(uint v) { uint s = v * 747796405u + 2891336453u; uint w = ((s >> ((s >> 28u) + 4u)) ^ s) * 277803737u; return (w >> 22u) ^ w; }
float Rand(inout uint state) { state = Pcg(state); return state * (1.0 / 4294967296.0); }

// 目標関数 p_hat: 影を除いた寄与の明るさ（BRDF は Lambert、G は距離の 2 乗の減衰）。
float TargetPdf(uint light, float3 pos, float3 n) {
  Light L = g_lights[light];
  float3 d = L.position - pos;
  float dist2 = max(dot(d, d), 1e-4);
  float n_dot_l = saturate(dot(n, d * rsqrt(dist2)));
  return dot(L.color, float3(0.2126, 0.7152, 0.0722)) * L.intensity * n_dot_l / dist2;
}

void Update(inout Reservoir r, uint light, float weight, inout uint rng) {
  r.w_sum += weight;
  if (Rand(rng) * r.w_sum < weight) r.light = light;   // 重み / 合計 の確率で入れ替える
}

// W = w_sum / p_hat(Y)。併合したあとは、さらに confidence の合計で割る（m_i = c_i / sum(c) の分母）。
void Finish(inout Reservoir r, float3 pos, float3 n, float divisor) {
  float p = (r.light == 0xFFFFFFFFu) ? 0.0 : TargetPdf(r.light, pos, n);
  r.w = (p > 0.0) ? r.w_sum / (p * divisor) : 0.0;
}

```

`Reservoir` は 16 バイトで選ばれたライトの番号、`w_sum`、confidence、`W` を持ちます。`CONFIDENCE_CAP` が履歴の上限です。目標関数 `TargetPdf` は Lambert の BRDF と距離の 2 乗の減衰と明るさで、影を含みません。`Finish` は `divisor` で割るところが肝です。初期候補は `divisor = 1`（重みが `1/M` で既に正規化済み）、併合したあとは confidence の合計です。割り忘れると併合した回数だけ `W` が大きくなり画面が明るくなりすぎます。

### 併合と借りてよいかの判断

```hlsl
// 借りてよい画素か。法線と深度が近いときだけ（リザーバーの中身では判断しない: 偏るため）。
bool Compatible(float3 n0, float d0, float3 n1, float d1) {
  return dot(n0, n1) > 0.9 && abs(d0 - d1) < 0.1 * d0;   // しきい値は一例（足した）
}

// 他のリザーバー s を、現在の画素の目標関数で評価し直して併合する。w_i = c_s * p_hat_現在(Y) * W_s。
void Merge(inout Reservoir acc, Reservoir s, float3 pos, float3 n, inout uint rng) {
  acc.confidence += s.confidence;                        // 空でも、見た候補の数は数える
  if (s.light == 0xFFFFFFFFu) return;
  Update(acc, s.light, s.confidence * TargetPdf(s.light, pos, n) * s.w, rng);
}

```

`Compatible` は法線の内積が 0.9 より大きく、深度の差が 10 % 未満のときだけ借りる判断です。しきい値は一例で足しました。ノートに数字はありません。`Merge` は相手のリザーバー `s` を今の画素の `p̂` で評価し直して、重み `c_s · p̂ · W_s` で更新します。空のリザーバーでも見た候補の数は confidence に足します。

### 初期候補と時間の再利用

```hlsl
[numthreads(8, 8, 1)]
void CSMain(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_size)) return;
  uint idx = id.y * g_size.x + id.x;
  float3 pos = g_position[id.xy].xyz, n = g_normal[id.xy].xyz;
  float depth = g_position[id.xy].w;
  uint rng = Pcg(idx ^ (g_frame * 9781u));

  // 1. 初期候補: ライトを一様に選ぶ（W_X = NUM_LIGHTS、m = 1/M）。
  Reservoir init = (Reservoir)0; init.light = 0xFFFFFFFFu;
  for (uint i = 0; i < INITIAL_CANDIDATES; ++i) {
    uint l = min((uint)(Rand(rng) * NUM_LIGHTS), NUM_LIGHTS - 1);
    Update(init, l, (1.0 / INITIAL_CANDIDATES) * TargetPdf(l, pos, n) * NUM_LIGHTS, rng);
  }
  init.confidence = INITIAL_CANDIDATES;
  Finish(init, pos, n, 1.0);

  Reservoir r = (Reservoir)0; r.light = 0xFFFFFFFFu;     // ここからが併合先
  Merge(r, init, pos, n, rng);

  // 2. 時間の再利用: 動きベクトルで前フレームの画素を探し、条件が合えば併合する。
  int2 prev = int2(id.xy + 0.5 - g_motion[id.xy]);
  if (all(prev >= 0) && all(prev < (int2)g_size)) {
    float4 pp = g_position[prev]; Reservoir s = g_prev[prev.y * g_size.x + prev.x];
    if (Compatible(n, depth, g_normal[prev].xyz, pp.w)) {
      s.confidence = min(s.confidence, CONFIDENCE_CAP);   // 履歴を打ち切る（残像を防ぐ）
      Merge(r, s, pos, n, rng);
    }
  }

```

初期候補は 4 個のライトを一様に選び `1/M` の重みで RIS します。続けてこれを併合先のリザーバー `r` に入れます。時間の再利用では動きベクトルで前フレームの画素を探し、範囲内で `Compatible` を満たすときだけ併合します。併合する前に `s.confidence` を上限で打ち切ります。これで履歴が無限に重くなるのを防ぎます。

### 空間の再利用と書き出し

```hlsl
  // 3. 空間の再利用: 近くの画素から借りる。
  for (uint k = 0; k < SPATIAL_NEIGHBORS; ++k) {
    float a = 6.2831853 * Rand(rng), rad = SPATIAL_RADIUS * sqrt(Rand(rng));
    int2 q = int2(id.xy) + int2(cos(a) * rad, sin(a) * rad);
    if (any(q < 0) || any(q >= (int2)g_size)) continue;
    float4 qp = g_position[q];
    if (!Compatible(n, depth, g_normal[q].xyz, qp.w)) continue;
    Merge(r, g_prev[q.y * g_size.x + q.x], pos, n, rng);   // 簡略化: 前フレームのリザーバーから借りる
  }
  Finish(r, pos, n, r.confidence);                        // 併合した全部の confidence の合計で割る
  r.confidence = min(r.confidence, CONFIDENCE_CAP);       // 次のフレームへ渡す履歴の長さを打ち切る
  g_cur[idx] = r;   // 影レイと最終シェーディングは別のパス（選ばれた 1 つだけに飛ばす）
}
```

近くの 4 画素を円の中からランダムに選びます（半径 16 画素は一例です）。範囲外の画素と `Compatible` でない画素は飛ばします。簡略化のため空間の再利用は前フレームのリザーバーから借りています。最後に `Finish` を併合した confidence の合計で割って呼び次のフレームへ渡す confidence を上限で打ち切ります。

## 応用 {#variants}

ReSTIR は何を再利用するかで分かれます。

- ReSTIR DI: 直接光。多数のライトを少ないレイで扱う。ゲームで最も取り入れやすい。
- ReSTIR GI: 間接光。反射した先の点を選び直す。
- ReSTIR PT: パス全体を借りて、パス トレーシングを効率化する。

DI はサンプルがライト上の点 1 つなので、隣の画素に持っていくのが簡単です。パス全体を別の画素に持っていく GI と PT は、パスの途中の頂点をどう付け替えるかが問題になります。講義ノートはこれを「シフト マッピング」で説明します。別の画素の経路空間へ経路を写す写像です。

最も単純なのが再接続シフトです。始点（視線側の頂点）だけを隣の画素に付け替え 2 番目以降の頂点（x2 以降）はそのまま使います。拡散面や粗い面にはよく効きますが、光沢面や鏡には効きません。理想反射の法則を守らないからです。光沢や屈折に強い方式が ReSTIR PT のハイブリッド シフトです。再接続の頂点とランダム数の種だけを保存し、画素あたり一定のメモリで済みます。再接続できる頂点には前の頂点との距離が `d_min` 以上であることとローブの粗さが `α_min` 以上であることの 2 つの条件があります。

写像でパスを動かすと確率密度が変わります。その変化の倍率がヤコビアン（Jacobian）で、重み `w_i = m_i · p̂ · W · |T'|` のように掛けます。

このページは講義ノートの 4 章までと 5 章のシフト マッピングの導入、6.6 節のハイブリッド シフトの冒頭、7.1 節の冒頭を読みました。ReSTIR GI と PT の各論文とノートのそのほかの節（7.2 節の低レベル最適化、Cyberpunk 2077 での導入）は、読んでいません。

## 弱点 {#weakness}

ノイズを大幅に減らす代わりに時間方向の再利用で、ライトや物体が急に変わると過去のサンプルが合わなくなり残像が出ます。履歴の上限（confidence の cap）を下げると残像は減りますが、ノイズが戻ります。

借りるほど画素どうしのサンプルが似てきます（相関）。画像全体がまだらに見えたりにじんだりするのは、この相関が原因です。ノートは上限を設けることが相関への対策として不可欠だと説明しています。

また、リザーバーの保存、再利用の判定、レイによる確認と実装がやや複雑です。偏りを消そうとすると前フレームの加速構造を持つなど重い処理が要ります。デノイザーと組み合わせて使うのが普通です。

## よくあるミス

??? failure "併合したのに、画面が明るくなりすぎる"
    併合したリザーバーの `W` を confidence の合計で割っていません。`w_sum` は confidence を掛けた重みの合計なので、割らないと併合した回数だけ明るくなります。初期候補では `1/M` で正規化済みなので割りませんが、併合後は割ります。

??? failure "ライトを動かしたあと前の影がしばらく残る"
    履歴の上限が大きすぎるか上限をかけていません。時間の再利用の前に confidence を打ち切ります。上限を 20 から始めて残像が出るなら下げます。

??? failure "壁の角や物の縁が暗く、まだらになる"
    法線や深度が違う画素から借りています。`Compatible` の判定を入れて借りる相手を絞ります。判定にリザーバーの中身を使うと偏るので、G バッファの値だけで決めます。

??? failure "選び直して、画面全体が少し暗い"
    重みが全部 0 だった画素で、空のサンプルを返さず別の候補を引き直しています。引き直すと偏ります。空のサンプルは `W = 0` で返します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 少ない候補から重みに応じて 1 つ選び（RIS）、リザーバーに入れる
    - [x] リザーバーは混ぜられるので、前のフレームと隣のピクセルから借りて、実質のサンプル数を増やせる
    - [x] 併合したら、confidence の合計で割る。履歴は上限（20 が目安）で打ち切る
    - [x] 借りる画素はサンプルではなく G バッファの値で選ぶ

## 参考

- Chris Wyman, Markus Kettunen, Daqi Lin, Benedikt Bitterli, Cem Yuksel, Wojciech Jarosz, Pawel Kozlowski, Giovanni De Francesco, "A Gentle Introduction to ReSTIR: Path Reuse in Real-time", ACM SIGGRAPH 2023 Courses. https://intro-to-restir.cwyman.org/ （コース ノートを読んだ。RIS、リザーバー、時間と空間の再利用、履歴の長さシフト マッピング、ハイブリッド シフト、サンプラーの最適化の冒頭）
- Benedikt Bitterli, Chris Wyman, Matt Pharr, Peter Shirley, Aaron Lefohn, Wojciech Jarosz, "Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting", ACM Transactions on Graphics (SIGGRAPH 2020). https://research.nvidia.com/labs/rtr/publication/bitterli2020spatiotemporal/ （論文の本文は読んでいない。公開ページの要旨だけ。偏りのない版は最新手法より 6 から 60 倍速く、偏りのある版は 35 から 65 倍速い。放射する三角形 340 万個の動的シーンを 1 フレーム 50 ms 未満、画素あたり最大 8 本のレイで扱う）
- Yaobin Ouyang, Shiqiu Liu, Markus Kettunen, Matt Pharr, Jacopo Pantaleoni, "ReSTIR GI: Path Resampling for Real-Time Path Tracing", Computer Graphics Forum (High-Performance Graphics 2021).（読んでいない）
- Daqi Lin, Markus Kettunen, Benedikt Bitterli, Jacopo Pantaleoni, Cem Yuksel, Chris Wyman, "Generalized Resampled Importance Sampling: Foundations of ReSTIR", ACM Transactions on Graphics (SIGGRAPH 2022).（ノートが引用。読んでいない）

## 関連ページ

- [Ray-Traced GI](rt-gi/index.md)
- [Fighting Noise](rt-gi/noise.md)
- [Global Illumination (GI)](index.md)
- [Lumen and Nanite](lumen.md)
