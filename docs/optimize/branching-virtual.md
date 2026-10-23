---
title: 分岐と仮想関数のコスト
tags:
  - 最適化
---

# 分岐と仮想関数のコスト

`if` や仮想関数の呼び出しは、**1 回ではほとんど気にならない**コストです。しかし、毎フレーム何万回もバラバラの結果で実行されると、CPU の先読みが外れて、数十サイクルの無駄が積み重なります。このページは分岐予測の仕組み、仮想関数の呼び出しのコスト、減らす方法（データを型ごとにまとめる、`variant`、CRTP）をまとめます。

!!! tip "ポイント"
    - CPU は、<strong>分岐の結果を予測して、先に進む</strong>。<strong>予測が外れると先読みが無駄になり、約 10〜20 サイクル</strong>失う。
    - 結果が規則的（いつも同じ・交互）なら、ほぼ当たる。ランダムな結果が危険。
    - 仮想関数のコストは、呼び出しそのものより、インライン化できない・間接ジャンプの予測が外れる・キャッシュに乗らないこと。
    - 対策：データを種類ごとにまとめて処理する（バッチ）。ソートして、分岐を規則的にする。
    - 測る前に書き換えない。多くの `if` や仮想関数は、ほとんど影響しない。

!!! info "このページを読む前に"
    - [optimize/index.md](index.md)（このセクション全体の地図と、読む順番）
    - [計測（プロファイリング）](measure.md)（測ってから直す、という進め方）

## 分岐予測

CPU は命令を**先読みして、パイプライン**で処理します。`if` の結果が決まる前に、どちらに進むかを予測して、先に進みます。

```text
予測が当たった：  先読みした命令が、そのまま使える（ほぼ無料）
予測が外れた：    先読みを捨てて、やり直す（約 10〜20 サイクルの損）
```

### 予測しやすい・しにくい

| 結果のパターン | 予測 |
| --- | --- |
| いつも同じ（ほとんど `true`） | ほぼ当たる |
| 規則的（交互、一定の周期） | 当たる（CPU が覚える） |
| ランダム（半分ずつ、不規則） | 約半分外れる |
| データの並びに依存 | 並びがソート済みなら当たる。バラバラなら外れる |

### 有名な例：ソート済みの配列

```cpp
long long sum = 0;
for (int x : data) {
  if (x >= 128) sum += x;
}
```

`data` がランダムだと、`x >= 128` がでたらめに変わって、予測が外れ続けます。ソートしてから回すと、「最初は偽、途中から真」で、ほぼ当たり、数倍速くなることがあります（ソートの時間は、別にかかります）。

## 分岐を減らす

### 早期リターンと、まれな処理を分ける

```cpp
void Update(Enemy& e) {
  if (!e.active) return;
  ...
}
```

**ほとんどの要素が同じ側に行く**条件は、予測が当たるので安く済みます。

### 条件を式にする（ブランチレス）

```cpp
int Clamp(int v, int lo, int hi) {
  return std::min(std::max(v, lo), hi);
}

int Select(bool cond, int a, int b) {
  return cond ? a : b;
}
```

`std::min` / `std::max`、三項演算子はコンパイラが分岐なしの命令（条件付き移動：`cmov`）にすることがあります。ランダムな結果の `if` は、こうなると速いです。ただし、コンパイラの判断なので、確かめるにはアセンブリを見るか、測ります（[コンパイラの最適化](compiler.md)）。

| 方法 | 説明 |
| --- | --- |
| `std::min` / `max` / `clamp` | 分岐なしになりやすい |
| ビット演算・算術 | `x & mask`、`(cond ? 1 : 0) * value` など |
| テーブル引き | `if` の連続を配列の添字に |
| SIMD のマスク | 条件をベクトルのマスクにして、全要素を同時に処理（[SIMD](simd.md)） |

!!! warning "ブランチレスは、いつも速いわけではない"
    予測が当たる分岐は、安いのでブランチレスにするとかえって遅くなることがあります（両方の計算をするため）。ランダムな結果の分岐だけが、対象です。測ってから直します。

### ヒント（[[likely]] / [[unlikely]]）

```cpp
if (error) [[unlikely]] {
  HandleError();
}
```

C++20 の `[[likely]]` / `[[unlikely]]` は、コンパイラへのヒントです。コードの配置が変わり、まれな側が遠くに置かれます。効果は小さいことが多く、測って効くときだけ使います。

## 仮想関数のコスト

```cpp
for (Entity* e : entities) {
  e->Update();
}
```

| コスト | 説明 |
| --- | --- |
| **間接呼び出し** | vtable（仮想関数の表）を読んでそこから飛ぶ。1 回はわずか |
| インライン化できない | 呼び先が実行時まで決まらないので、コンパイラが展開できない。小さい関数では、これが一番大きい |
| 予測が外れる | 種類がバラバラの並びだと、間接ジャンプの予測が外れる（上の分岐予測と同じ） |
| キャッシュ | オブジェクトが散らばっていると、vtable とデータの読み込みが遅い |
| ベクトル化の阻害 | ループの中に仮想関数があると、SIMD にできない |

仮想関数が悪いのではありません。数万回/フレームの細かい関数で問題になります。数十〜数百回/フレームの、大きな処理では、気にしなくて大丈夫です。

### 影響が大きい場面

| 場面 | 影響 |
| --- | --- |
| 数千〜数万のエンティティの `Update()` | 大きい |
| 細かい関数（`GetX()`、`IsAlive()`）を、仮想にしている | 大きい（インライン化されない） |
| UI の 100 個のウィジェットの描画 | ほぼなし |
| 数個のシステム（`Renderer`、`Audio`）の呼び出し | なし |

## 減らす方法

### 1. 種類ごとにまとめる（バッチ）

最も効く方法です。**同じ型のものを連続して並べて、まとめて処理**します。

```cpp
for (Goblin& g : goblins) g.Update();
for (Dragon& d : dragons) d.Update();
```

型が決まっているので仮想呼び出しがなく、インライン化され、キャッシュにも優しい（連続した配列）。ECS が速い理由の 1 つです（[ECS](../design/patterns/ecs.md)、[データ指向設計](../design/patterns/data-oriented.md)）。

### 2. 呼び出しの回数を減らす

1 つずつ呼ぶのをやめて、配列を渡して、中でループします。

```cpp
struct IUpdater {
  virtual void UpdateAll(std::span<Particle> particles, float dt) = 0;
};
```

仮想呼び出しが 1 回で、中はループ（インライン・SIMD になる）。

### 3. variant（閉じた種類）

```cpp
using Shape = std::variant<Circle, Box, Capsule>;

float Area(const Shape& s) {
  return std::visit([](const auto& v) { return v.Area(); }, s);
}
```

| 項目 | 仮想関数 | `variant` |
| --- | --- | --- |
| 種類の追加 | 簡単（派生クラスを足す） | 型の一覧を変える |
| ヒープ確保 | 必要（ポインタ） | 不要（値で持てる） |
| 呼び出し | 間接ジャンプ | `switch`（インライン化されやすい） |
| メモリ | ポインタ + vtable | 連続して並べられる |

種類が決まっている（閉じている）なら、`variant` が速いです（[std::variant](../stl/utilities/variant.md)）。

### 4. CRTP（コンパイル時に決める）

```cpp
template <typename Derived>
struct Entity {
  void Update(float dt) { static_cast<Derived*>(this)->UpdateImpl(dt); }
};
```

コンパイル時に呼び先が決まるので、インライン化されます。ただし、型ごとに別のコンテナが必要です（異なる型を、1 つの配列に混ぜられない）（[CRTP](../design/patterns/crtp-policy.md)）。

### 5. final を付ける

```cpp
class Goblin final : public Enemy {
  void Update(float dt) override;
};
```

`final` を付けると、コンパイラが「これ以上、派生しない」と分かるので仮想呼び出しを直接呼び出しにできることがあります（デバーチャライゼーション）。手軽に試せる方法です。

### 6. ソートして、並びを揃える

仮想関数のまま、同じ型が隣り合うように、型で並べ替えると予測が当たりやすくなります。

## 選び方

| 状況 | 方法 |
| --- | --- |
| 数が少ない（数百まで）・拡張が大事 | **仮想関数のまま**でよい |
| 数が多い・種類が決まっている | 種類ごとにまとめる・`variant` |
| 数が多い・種類が増える | 配列ごとに処理するインターフェース（`UpdateAll`） |
| 細かい関数が毎フレーム数万回 | 仮想にしない（インライン可能に） |
| 実験したい | `final` を付ける |

## 測り方

| 方法 | 説明 |
| --- | --- |
| **プロファイラー** | 仮想関数の呼び出し（`Entity::Update` の自己時間）、分岐予測ミス（CPU カウンター）を見る（[プロファイラー](../vs/profiler.md)） |
| ベンチマーク | 仮想版とまとめ版を同じ条件で比べる（[計測](measure.md)） |
| アセンブリ | 呼び出しが、`call [rax+..]`（間接）か、直接かを見る |

<!-- fig:branch-predict:begin -->

<svg class="fig illust motion" data-fig="branch-predict" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-branch-predict" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">分岐予測: 結果が揃っていると当たり、バラバラだと外れる</text>
<text x="70" y="88" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">並べ替えなし（バラバラ）</text>
<rect x="70" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="99" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="128" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="126" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1026;0.1029;1.0000" values="0;0;1;1"/></rect>
<rect x="157" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="155" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1255;0.1257;1.0000" values="0;0;1;1"/></rect>
<rect x="186" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="184" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1483;0.1486;1.0000" values="0;0;1;1"/></rect>
<rect x="215" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="244" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="273" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="271" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2171;1.0000" values="0;0;1;1"/></rect>
<rect x="302" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="331" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="329" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2626;0.2629;1.0000" values="0;0;1;1"/></rect>
<rect x="360" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="358" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2855;0.2857;1.0000" values="0;0;1;1"/></rect>
<rect x="389" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="387" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3083;0.3086;1.0000" values="0;0;1;1"/></rect>
<rect x="418" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="416" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3312;0.3314;1.0000" values="0;0;1;1"/></rect>
<rect x="447" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="445" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3541;0.3543;1.0000" values="0;0;1;1"/></rect>
<rect x="476" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="505" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="503" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/></rect>
<rect x="534" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="532" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4226;0.4229;1.0000" values="0;0;1;1"/></rect>
<rect x="563" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="561" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4455;0.4457;1.0000" values="0;0;1;1"/></rect>
<rect x="592" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="590" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4683;0.4686;1.0000" values="0;0;1;1"/></rect>
<rect x="621" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="619" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4912;0.4914;1.0000" values="0;0;1;1"/></rect>
<rect x="650" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="648" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5141;0.5143;1.0000" values="0;0;1;1"/></rect>
<rect x="679" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="708" y="100" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="737" y="100" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="735" y="98" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5826;0.5829;1.0000" values="0;0;1;1"/></rect>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;1.0000" values="1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.0798;0.0800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.1026;0.1029;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1026;0.1029;0.1255;0.1257;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1255;0.1257;0.1483;0.1486;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1483;0.1486;0.1712;0.1714;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1712;0.1714;0.1941;0.1943;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;0.2169;0.2171;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2171;0.2398;0.2400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2398;0.2400;0.2626;0.2629;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2626;0.2629;0.2855;0.2857;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2855;0.2857;0.3083;0.3086;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">7<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3083;0.3086;0.3312;0.3314;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3312;0.3314;0.3541;0.3543;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3541;0.3543;0.3769;0.3771;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3769;0.3771;0.3998;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">10<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;0.4226;0.4229;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">11<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4226;0.4229;0.4455;0.4457;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4455;0.4457;0.4683;0.4686;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">13<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4683;0.4686;0.4912;0.4914;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">14<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4912;0.4914;0.5141;0.5143;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5141;0.5143;0.5369;0.5371;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5369;0.5371;0.5598;0.5600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5598;0.5600;0.5826;0.5829;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="166" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5826;0.5829;1.0000" values="0;0;1;1"/></text>
<text x="108" y="166" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">回、予測を外した（赤い枠）</text>
<text x="70" y="248" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">並べ替えあり（true が先に固まる）</text>
<rect x="70" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="99" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="128" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="157" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="186" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="215" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="244" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="273" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="302" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="331" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="360" y="260" width="26" height="26" fill="#2563eb" stroke="#94a3b8" stroke-width="1"/>
<rect x="389" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="387" y="258" width="30" height="30" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3083;0.3086;1.0000" values="0;0;1;1"/></rect>
<rect x="418" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="447" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="476" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="505" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="534" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="563" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="592" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="621" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="650" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="679" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="708" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<rect x="737" y="260" width="26" height="26" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;1.0000" values="1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.0798;0.0800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.1026;0.1029;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1026;0.1029;0.1255;0.1257;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1255;0.1257;0.1483;0.1486;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1483;0.1486;0.1712;0.1714;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1712;0.1714;0.1941;0.1943;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.1941;0.1943;0.2169;0.2171;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2171;0.2398;0.2400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2398;0.2400;0.2626;0.2629;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2626;0.2629;0.2855;0.2857;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2855;0.2857;0.3083;0.3086;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3083;0.3086;0.3312;0.3314;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3312;0.3314;0.3541;0.3543;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3541;0.3543;0.3769;0.3771;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3769;0.3771;0.3998;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;0.4226;0.4229;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4226;0.4229;0.4455;0.4457;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4455;0.4457;0.4683;0.4686;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4683;0.4686;0.4912;0.4914;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.4912;0.4914;0.5141;0.5143;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5141;0.5143;0.5369;0.5371;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5369;0.5371;0.5598;0.5600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5598;0.5600;0.5826;0.5829;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="326" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5826;0.5829;1.0000" values="0;0;1;1"/></text>
<text x="108" y="326" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">回、予測を外した（赤い枠）</text>
<text x="70" y="400" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">予測のルール: 「前回と同じ結果」になると決め打ち。青 = true、灰 = false</text>
</svg>

<!-- fig:branch-predict:end -->

## よくあるミス

??? failure "測らずに、すべての仮想関数をテンプレートに書き換える"
    **読みにくくなる**だけでほとんど効果がありません。プロファイラーで遅い場所だけを直します。

??? failure "ランダムなデータで、分岐が多い所を放置する"
    ソート・ブランチレス・バッチ化で改善することがあります。

??? failure "ブランチレスにして、かえって遅くなる"
    予測が当たる分岐は、安いです。測って確かめます。

??? failure "`[[likely]]` を、あちこちに付ける"
    効果は小さく、間違った予測は、逆効果です。測って効いたときだけにします。

??? failure "細かい関数 `GetX()` を、仮想関数にしている"
    インライン化されず、遅くなります。仮想にする必要があるかを、考えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>分岐は、予測が当たれば安い</strong>。ランダムな結果が外れて、約 10〜20 サイクル失う
    - [x] 仮想関数の本当のコストは、インライン化できない・予測が外れる・キャッシュ
    - [x] 一番効くのは「型ごとにまとめて処理」。`variant`・CRTP・`final` も使える
    - [x] 数が少ない所は、気にしない。測ってから直す

## 関連ページ

- [最適化の進め方](index.md)
- [メモリとキャッシュ](memory-cache.md)
- [SIMD](simd.md)
- [コンパイラの最適化](compiler.md)
- [仮想関数（基礎）](../basics/virtual.md)
- [ECS](../design/patterns/ecs.md)
- [CRTP とポリシーベース設計](../design/patterns/crtp-policy.md)
- [std::variant](../stl/utilities/variant.md)
