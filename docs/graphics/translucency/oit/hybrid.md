---
title: Hybrid Approaches and Choosing
tags:
  - 描画
---

# Hybrid Approaches and Choosing

窓ガラス、水、髪の毛、煙、粒子。これらは全部「半透明」ですが、1 つの OIT の方式ですべてをうまく描くことはできません。PPLL はどんな重なりも正確に描けますが、メモリが大きく重い方式です。WBOIT は軽くて粒子に強いのですが、色が近い物の重なりしか近似できません。そこで実際のゲームは半透明を種類で分けて、物ごとに方式を割り当てます。

このページは OIT の方式の選び方と混ぜて使うハイブリッド構成を説明します。まず種類ごとの描く順番を図で見て、方式ごとのメモリを数字で見積もります。最後に、描く順番とメモリの見積もりを C++ の完全なプログラムにします。

!!! tip "ポイント"
    重要で数が少ない半透明（ガラス）はソートと 2 パス、煙や粒子は WBOIT、葉や草はアルファ テスト系に分けます。ほとんどのゲームはソートに WBOIT を足せば十分です。PPLL やデプス ピーリングは正確さが必要な少数の物にだけ使います。まず測って、問題が出た部分だけ重い方式にします。

!!! info "このページを読む前に"
    - [Order-Independent Transparency (OIT)](index.md)（このセクション全体の地図と、読む順番）
    - [WBOIT](wboit.md)、[PPLL](ppll.md)（このページが並べる 2 つの方式）

## 種類ごとに方式を分ける

1 つの方式ですべてをまかなうのは難しいので、物の種類で使い分けます。

窓ガラスや車の窓は重要で数が少ない半透明です。ソートしてアルファ ブレンドにします。ガラスの内側で表と裏が見える物は裏面、表面の 2 パスに分けます。

煙、霧、魔法のパーティクルは大量に重なります。WBOIT にして別のレンダー ターゲットに描いてから最後に合成します。

木の葉と草は縁を切り抜く物です。アルファ テスト系（[Alpha Testing](../alpha-test/index.md)）にして、半透明のパスには入れません。

髪の毛はハッシュド アルファと TAA、あるいは PPLL で手前の数層だけを描きます（[Hair Transparency](../../skin-hair/hair/transparency.md)）。

水面は専用の水のシェーダー（[Water](../../water/index.md)）で描きます。

### 描く順番

種類ごとにパスを分けると描く順番は次の図のとおりです。

<svg class="fig flow" viewBox="0 0 680 250" role="img" aria-label="半透明を種類で分けた描画の順番"><defs><marker id="oA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">描く順番：種類ごとにパスを分ける</text><rect x="12" y="52" width="124" height="58" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="74.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">0 不透明</text><text x="74.0" y="90.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">深度を書く</text><line x1="136" y1="81" x2="146" y2="81" stroke="currentColor" stroke-width="2" marker-end="url(#oA)"/><rect x="146" y="52" width="124" height="58" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="208.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">1 アルファ テスト</text><text x="208.0" y="90.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">葉・草・柵</text><line x1="270" y1="81" x2="280" y2="81" stroke="currentColor" stroke-width="2" marker-end="url(#oA)"/><rect x="280" y="52" width="124" height="58" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="342.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">2 水</text><text x="342.0" y="90.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">専用シェーダー</text><line x1="404" y1="81" x2="414" y2="81" stroke="currentColor" stroke-width="2" marker-end="url(#oA)"/><rect x="414" y="52" width="124" height="58" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="476.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">3 ガラス</text><text x="476.0" y="90.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">奥 → 手前にソート</text><line x1="538" y1="81" x2="548" y2="81" stroke="currentColor" stroke-width="2" marker-end="url(#oA)"/><rect x="548" y="52" width="124" height="58" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="610.0" y="72.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">4 煙・粒子</text><text x="610.0" y="90.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:400">WBOIT → 合成</text><text x="14" y="146" style="font-size:12px;font-weight:600">前後関係は、描く順番で決まる</text><text x="14" y="168" style="font-size:12px;font-weight:400">・煙の合成は最後なので、煙は常にガラスの手前に重なる。</text><text x="14" y="188" style="font-size:12px;font-weight:400">・ガラスの向こうの煙は、ガラスより先に描く必要がある（本文の「混ざる場面」）。</text><text x="14" y="214" style="font-size:12px;font-weight:400">・ポストプロセスは、5 つの後（全部が合成された画像）に掛ける。</text></svg>

各方式の結果は順に画面へ重なります。方式の間の前後関係は描く順番だけで決まります。たとえば、図の順では煙の合成が最後なので、煙は必ずガラスの手前に重なります。ガラスの向こうにある煙を正しく見せるには、その煙をガラスより先に描く必要があります。1 つの場面に混ざるときは全体の順番を先に設計します。

## 手前だけ正確に

画面の手前の数層は見た目への影響が大きく、奥の層は小さいという性質を使うハイブリッドがあります。手前の数層（たとえば 4 層）を PPLL かデプス ピーリングで正確に描き、奥の残りは WBOIT で 1 つの層にまとめて近似します。

Salvi らの Adaptive Transparency（2011）と Multi-Layer Alpha Blending（2014）は、少数の層で近似する考え方です。層の数を固定できるのでメモリの上限が決まります。PPLL のようにバッファが溢れることがありません。

## 方式の一覧

次の表は方式を並べた引く用の一覧です。

| 方式 | 正確さ | パス数 | メモリ | 速さ |
| --- | --- | --- | --- | --- |
| ソート + アルファ ブレンド | 物体単位 | 1 | 小 | 速い |
| デプス ピーリング | 正確 | 層の数 | 中 | 遅い |
| PPLL | 正確（上限まで） | 2 | 大 | 中 |
| WBOIT | 近似 | 2 | 小 | 速い |
| 確率的透明 | 期待値が正しい | 1 | 中（MSAA） | 速い |
| アルファ テスト系 | 縁を切り抜く | 1 | 小 | 速い |

ソートは物体どうしの前後は正しくなりますが、1 つの物体の中や物体が交差する場所は正しくなりません。デプス ピーリングは層を 1 枚ずつ剥がすので、層の数だけパスが増えます。PPLL は構築と解決の 2 パスですが、メモリは重なりの数で決まります。WBOIT は 2 枚のレンダー ターゲットだけで済みます。確率的透明は期待値が正しい代わりに TAA か MSAA でノイズを平均する前提です。

## 選び方

次の順に質問して最初に当てはまった方式にします。

1. 半透明の物が少数（数個）ならソートとアルファ ブレンドです。物体の内側に問題があれば裏面、表面の 2 パスにします。
2. 縁を切り抜く物（葉・草・髪）ならアルファ テスト系（A2C、ハッシュド アルファと TAA）です。
3. ぼんやりした物（煙・霧・粒子）なら WBOIT です。
4. 正確さが必要な物（ガラス・水中の物）が多数重なるなら PPLL か少数層のデプス ピーリングです。
5. 粒子が大量で加算で済むなら加算ブレンドにします。加算は順序に依存しないので OIT が要りません。

## 数字で見積もる

方式を選ぶ前にメモリを掛け算で見ます。フル HD（1920 × 1080 = 2,073,600 画素）を例にします。

WBOIT は累積用の `R16G16B16A16_FLOAT`（8 バイト）と透過度用の `R8_UNORM`（1 バイト）の 2 枚です。1 画素 9 バイトなので約 17.8 MiB です。

PPLL はヘッド ポインタが 1 画素 4 バイトで、約 7.9 MiB です。ノードは色 4 バイト、深度 4 バイト、次の番号 4 バイトの 12 バイトです。重なりの平均が 8 層なら画素数 × 8 × 12 バイトで約 190 MiB になり、合計は約 198 MiB です。16 層だと約 388 MiB です。PPLL のメモリは画面の解像度に比例し、重なりの数にも比例します。

デプス ピーリング（4 層）は層ごとの色を RGBA8（4 バイト）で 4 枚と、深度を 2 枚（ピンポン、4 バイト × 2）の想定で、1 画素 24 バイトです。約 47.5 MiB です。パスが層の数だけ増えるのでメモリより時間が問題になります。

<svg class="fig flow" viewBox="0 0 680 218" role="img" aria-label="1080p での OIT のメモリ。WBOIT は約 18 MiB、PPLL は平均 8 層で約 198 MiB"><text x="14" y="22" class="fig-title">1080p のメモリ（MiB）</text><text x="14" y="57" style="font-size:12px;font-weight:600">WBOIT</text><rect x="190" y="44" width="14" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="212" y="60" style="font-size:12px">17.8</text><text x="14" y="91" style="font-size:12px;font-weight:600">ピーリング 4 層</text><rect x="190" y="78" width="39" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="237" y="94" style="font-size:12px">47.5</text><text x="14" y="125" style="font-size:12px;font-weight:600">PPLL（平均 8 層）</text><rect x="190" y="112" width="163" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="361" y="128" style="font-size:12px">197.8</text><text x="14" y="159" style="font-size:12px;font-weight:600">PPLL（平均 16 層）</text><rect x="190" y="146" width="320" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="518" y="162" style="font-size:12px">387.6</text><text x="14" y="206" style="font-size:12px;font-weight:400">下の C++ の見積もり関数の出力。PPLL の層数は、重なりの平均で決まる。</text></svg>

PPLL の層数は実際のシーンの重なりで決まります。重なりが平均 8 層でも煙の塊の中心では平均よりずっと多くの層が重なります。バッファが足りないと溢れたフラグメントは捨てられ画面に欠けが出ます。層数の上限を決めて溢れたら捨てる設計にします。

## 描く順番とメモリを見積もる C++

ここまでの内容を完全なプログラムにします。描画物を種類ごとにパスへ割り当て、ガラスだけを奥から手前に並べ方式ごとのメモリを見積もります。MSVC で `/W4` の警告なしにコンパイルして、実行結果を確かめました。実際の描画は含みません。

### 種類とパス

```cpp
// oit_plan.cpp : 半透明の描画物を種類で分け、描く順番と OIT のメモリを見積もる。
#include <algorithm>
#include <cstdint>
#include <print>
#include <string>
#include <vector>

enum class Kind { kOpaque, kAlphaTest, kWater, kGlass, kParticle };

struct DrawItem {
  std::string name;
  Kind kind;
  float distance;  // カメラからの距離（ワールド単位）
};

// パスの番号。小さいほど先に描く。
int PassOf(Kind kind) {
  switch (kind) {
    case Kind::kOpaque:    return 0;  // 深度を書く
    case Kind::kAlphaTest: return 1;  // 葉・草・柵（A2C かハッシュド アルファ）
    case Kind::kWater:     return 2;  // 水面（専用のシェーダー）
    case Kind::kGlass:     return 3;  // ソートしたガラス（奥 → 手前）
    case Kind::kParticle:  return 4;  // WBOIT の煙・粒子（別ターゲット → 合成）
  }
  return 0;
}
```

`PassOf` は図の順番をそのまま番号にした関数です。`Kind` に値を足したときに `switch` の網羅漏れを `/W4` が警告してくれるように `default` を書きません。

### 並べ替え

```cpp
// 描く順に並べる。同じパスでは、ガラスだけを遠い順（奥 → 手前）にする。
void SortForDrawing(std::vector<DrawItem>* items) {
  std::stable_sort(items->begin(), items->end(), [](const DrawItem& a, const DrawItem& b) {
    if (PassOf(a.kind) != PassOf(b.kind)) return PassOf(a.kind) < PassOf(b.kind);
    if (a.kind == Kind::kGlass) return a.distance > b.distance;  // 遠い物が先（奥から手前へ重ねる）
    return false;  // それ以外は、元の順を保つ
  });
}
```

`std::stable_sort` にするのは同じパスの中で元の順を保つためです。不透明や葉は描く順序が結果に影響しないので、並べ替えるとかえって状態の切り替えが増えます。ガラスだけは `distance` が大きい（遠い）順にして、奥から手前へ重ねます。距離は本来はオブジェクトの中心ではなく、重ねる単位の代表点で測ります。ここでは簡単に 1 つの値にしました。

### メモリの見積もり

```cpp
// 1 画素あたりのバイト数 × 画素数 を MiB で返す。
double MiB(uint64_t bytes) { return static_cast<double>(bytes) / (1024.0 * 1024.0); }

// WBOIT: 累積 R16G16B16A16_FLOAT（8 バイト）+ 透過度 R8_UNORM（1 バイト）。
uint64_t WboitBytes(uint32_t w, uint32_t h) { return static_cast<uint64_t>(w) * h * (8 + 1); }

// PPLL: ヘッド ポインタ（4 バイト/画素）+ ノード（色 4 + 深度 4 + 次 4 = 12 バイト）× 平均の層数。
uint64_t PpllBytes(uint32_t w, uint32_t h, uint32_t avg_layers) {
  uint64_t pixels = static_cast<uint64_t>(w) * h;
  return pixels * 4 + pixels * avg_layers * 12;
}

// デプス ピーリング: 層ごとの色（RGBA8 = 4 バイト）+ 深度 2 枚（ピンポン。4 バイト × 2）という想定。
uint64_t PeelingBytes(uint32_t w, uint32_t h, uint32_t layers) {
  return static_cast<uint64_t>(w) * h * (layers * 4 + 8);
}
```

どの関数も掛け算の前に `uint64_t` へ広げています。4K（8,294,400 画素）に PPLL の 16 層を掛けると 32 ビットを超えるからです。ピーリングの深度 2 枚は前の層の深度を読みながら次の層の深度を書くために、入れ替えて使う想定です。実装によって構成が変わるので、この数字は一例です。

### 実行する

```cpp
int main() {
  std::vector<DrawItem> items = {
      {"smoke", Kind::kParticle, 12.0f},   {"window_far", Kind::kGlass, 20.0f},
      {"rock", Kind::kOpaque, 5.0f},       {"window_near", Kind::kGlass, 6.0f},
      {"grass", Kind::kAlphaTest, 8.0f},   {"lake", Kind::kWater, 30.0f},
  };
  SortForDrawing(&items);
  std::println("描く順:");
  for (const DrawItem& it : items) {
    std::println("  pass {}  {}", PassOf(it.kind), it.name);
  }

  const uint32_t w = 1920, h = 1080;
  std::println("\n1080p のメモリ（MiB）:");
  std::println("  WBOIT              {:7.1f}", MiB(WboitBytes(w, h)));
  std::println("  PPLL (平均 8 層)   {:7.1f}", MiB(PpllBytes(w, h, 8)));
  std::println("  PPLL (平均 16 層)  {:7.1f}", MiB(PpllBytes(w, h, 16)));
  std::println("  ピーリング 4 層    {:7.1f}", MiB(PeelingBytes(w, h, 4)));
  return 0;
}
```

```text title="実行結果"
描く順:
  pass 0  rock
  pass 1  grass
  pass 2  lake
  pass 3  window_far
  pass 3  window_near
  pass 4  smoke

1080p のメモリ（MiB）:
  WBOIT                 17.8
  PPLL (平均 8 層)     197.8
  PPLL (平均 16 層)    387.6
  ピーリング 4 層       47.5
```

描く順はパス番号の順に並びます。パス 3 のガラスは遠い `window_far`（20）が先、近い `window_near`（6）が後です。奥から手前へ重ねる順番です。メモリは WBOIT が約 17.8 MiB で、PPLL（平均 8 層）の約 11 分の 1 です。

## 実装の現実

まず測ります。半透明のオーバードローが実際に何層あるかを調べ問題が起きていなければ、単純な方式で十分です。

単純な方式から始めます。ソートとアルファ ブレンドで問題が出た部分だけ他の方式に替えます。

品質設定を用意します。PPLL や WBOIT の層の数と解像度は、設定で変えられるようにしておきます。

対応環境も確認します。PPLL はピクセル シェーダーから UAV へ書く必要があり DX11 では機能レベル 11_0 以上です。

## よくあるミス

??? failure "すべてを PPLL にして、重くなる"
    煙や粒子まで PPLL に入れると、平均の層数が大きくなりノードのバッファが数百 MiB になって、構築パスも重くなります。バッファが溢れた画素は欠けて見えます。重要で少数の物だけを PPLL にし、粒子は WBOIT に回します。

??? failure "WBOIT の結果をガラスの前後に正しく重ねられない"
    WBOIT は合成が 1 回なので、煙の中に別の物が入るような前後関係は表せません。ガラスの向こうの煙はガラスより先に描き手前の煙は後ろで合成します。それでも足りなければ煙を深度で 2 グループに分けて 2 回合成する回避策がありますが、このセクションの資料では扱っていないので、効果は自分のシーンで確かめてください。

??? failure "描く順番を設計せず半透明が不透明の前に描かれる"
    半透明は不透明の深度を読んで描くので、不透明の後でなければ正しく隠れません。パスの番号を決めて上のコードのように並べます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 半透明は種類で分けて、方式を割り当てる
    - [x] ほとんどのゲームは、ソートと WBOIT で足りる
    - [x] 前後関係は描く順番で決まる
    - [x] メモリは掛け算で見積もる。PPLL は重なりの数に比例する

## 参考

このページは同じセクションの各ページ（WBOIT、PPLL、Depth Peeling、Stochastic Transparency）をもとに使い分けとしてまとめたものです。次の資料はこのページを書くために読み直していません。メモリの見積もりはこのページの想定（バッファの形式と層数）で計算した一例です。

- Chris Wyman, "Exploring and Expanding the Continuum of OIT Algorithms", High-Performance Graphics 2016.
- Marco Salvi, Jefferson Montgomery, Aaron Lefohn, "Adaptive Transparency", High-Performance Graphics 2011.
- Marco Salvi, Karthik Vaidyanathan, "Multi-Layer Alpha Blending", Symposium on Interactive 3D Graphics and Games 2014.
- Morgan McGuire, Louis Bavoil, "Weighted Blended Order-Independent Transparency", Journal of Computer Graphics Techniques, Vol. 2, No. 2, 2013.
- Cedrick Münstermann, Stefan Krumpen, Reinhard Klein, Christoph Peters, "Moment-Based Order-Independent Transparency", High-Performance Graphics 2018.

## 関連ページ

- [OIT](index.md)
- [WBOIT](wboit.md)
- [PPLL](ppll.md)
- [Depth Peeling](depth-peeling.md)
- [Stochastic Transparency](stochastic.md)
