---
title: 毎フレームのヒープ確保を避ける
tags:
  - 最適化
---

# 毎フレームのヒープ確保を避ける

ゲームのループ（更新・描画）の中では、**ヒープ確保（`new`・`malloc`・`std::vector` や `std::string` の内部確保）を、基本的にしない**のが鉄則です。1 回の確保は数十〜数百ナノ秒でも、ばらつきが大きく、<strong>たまに遅いフレーム（カクつき）</strong>を作ります。しかも、確保は**目に見えない所**（文字列の連結、ラムダの保存、`push_back`）で起きます。このページは、**どこで確保が起きるか**、**どう見つけるか**、**どう避けるか**を、まとめます（仕組みは [メモリ確保](allocation.md)）。

!!! tip "ポイント"
    - <strong>毎フレーム実行される処理の中では、ヒープ確保をしない。</strong>初期化・ロード時に確保して、ループでは使い回す。
    - 隠れた確保に注意：<strong>`std::string` の作成・連結、`std::to_string`、`std::vector` の `push_back` / 作成、`std::function`、`make_shared`、`std::map` の挿入</strong>。
    - 避け方：<strong>`reserve` + `clear()` で使い回す</strong>、<strong>固定長（`std::array`・固定バッファ）</strong>、<strong>フレーム用アリーナ</strong>、<strong>プール</strong>、<strong>`string_view`</strong>。
    - <strong>`operator new` を差し替えて、フレームごとの確保回数を数える</strong>と、見つかる。
    - ロード中や、メニューなど、<strong>落ち着いた場面の確保は許される</strong>。<strong>1 フレームごとに繰り返す所だけ</strong>が、問題。

## なぜ避けるのか

| 理由 | 説明 |
| --- | --- |
| **時間が一定でない** | 空き領域を探す時間は、ヒープの状態で変わる。たまに桁違いに遅い（カクつき） |
| **ロックの待ち** | 標準のヒープは、スレッド間で共有。ジョブが同時に確保すると、待たされる |
| **断片化** | 確保と解放を繰り返すと、細かい空きが増えて、遅く・足りなくなる |
| **キャッシュに優しくない** | 確保した場所が散らばる（[メモリとキャッシュ](memory-cache.md)） |
| **解放も遅い** | `delete` も管理情報を更新する。一度に大量に解放すると、カクつく |

## 隠れた確保の見つけ方

<strong>コードに `new` と書いていなくても、確保は起きます。</strong>

### std::string

```cpp
void Update() {
  std::string name = "enemy_" + std::to_string(id);
  log(name + " moved");
}
```

| 操作 | 確保が起きるか |
| --- | --- |
| 短い文字列（約 15 文字以下）の作成 | **起きない**（SSO：小さな文字列は、オブジェクト内に収まる） |
| 長い文字列の作成・コピー | **起きる** |
| `+` による連結 | **起きる**（一時オブジェクトが、いくつも） |
| `std::to_string` | 短ければ起きない（SSO）。結果を連結すると起きる |
| `std::format` で `std::string` を返す | **起きる**（長ければ） |
| `std::ostringstream` | **起きる**（しかも重い） |
| `substr`、`std::string(sv)` | 長ければ起きる |

SSO の閾値は、実装依存です（MSVC は 15 文字、libstdc++ も 15 文字）。**境界の少し上の長さで、突然遅くなる**ことがあります。

### std::vector

```cpp
void Update() {
  std::vector<Enemy*> nearby;
  for (Enemy& e : enemies) {
    if (IsNear(e)) nearby.push_back(&e);
  }
}
```

| 操作 | 確保が起きるか |
| --- | --- |
| **ローカル変数の `vector` に `push_back`** | **起きる**（毎フレーム作る→確保。しかも、容量を増やすたびに再確保） |
| `reserve` なしの `push_back` | 容量が足りなくなるたびに、再確保 |
| `clear()` | **確保は解放されない**（容量が残る）→ 使い回せる |
| コピー（値渡し・代入） | **起きる** |
| `resize` / `insert` | 容量が足りなければ、起きる |

### そのほか

| 場所 | 確保 |
| --- | --- |
| **`std::function`** | 呼び出し可能なものが大きい（キャプチャが多い）と、**ヒープ確保**。小さければ、内部に収まる |
| **`std::make_shared` / `shared_ptr`** | 作るたびに確保（制御ブロック）。コピーは確保しないが、参照カウントの原子操作が重い |
| **`std::map` / `std::set` / `std::list`** | **要素ごとに確保**。挿入・削除のたびに |
| **`std::unordered_map`** | 要素ごとに確保 + 再ハッシュ |
| **`std::any` / `std::variant` に大きな型** | `any` は、大きいと確保。`variant` は確保しない |
| <strong>例外（`throw`）</strong> | 例外オブジェクトの確保 + 展開の処理（非常に遅い） |
| **`std::deque`** | ブロックごとに確保 |
| **ラムダ式を `std::function` に代入** | 上の `std::function` と同じ |
| **仮想関数を持つ、ポリモーフィックなオブジェクトの生成** | `new` + 派生クラス |

## 見つけ方

### グローバルの `operator new` を数える

```cpp
#include <atomic>
#include <cstdlib>
#include <new>

namespace {
std::atomic<size_t> g_alloc_count{0};
}

void* operator new(size_t size) {
  g_alloc_count.fetch_add(1, std::memory_order_relaxed);
  if (void* p = std::malloc(size)) return p;
  throw std::bad_alloc();
}

void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, size_t) noexcept { std::free(p); }

size_t AllocCount() { return g_alloc_count.load(std::memory_order_relaxed); }
```

```cpp
size_t before = AllocCount();
Update();
size_t after = AllocCount();
if (after != before) {
  log("このフレームの確保: %zu 回", after - before);
}
```

**ゲームのループの中で、確保が 0 回**になるのが、理想です。1 回でもあれば、**ブレークポイントを `operator new` に置いて**、呼び出し履歴から、原因を見つけます。

### プロファイラーで見る

Visual Studio の**メモリ使用量**ツール（スナップショット）や、**パフォーマンス プロファイラー**で、`operator new` / `malloc` を、呼んでいる場所を調べます（[プロファイラー](../vs/profiler.md)）。Tracy などは、確保の記録に対応しています。

!!! warning "ライブラリの中の確保"
    自分のコードに `new` がなくても、<strong>ライブラリ（ImGui、JSON、物理エンジン）</strong>の中で、確保しているかもしれません。上のカウンターは、ライブラリの確保も数えるので、見つけられます。

## 避け方

### 使い回す（reserve + clear）

```cpp
class EnemyManager {
 public:
  EnemyManager() { nearby_.reserve(256); }

  void Update() {
    nearby_.clear();
    for (Enemy& e : enemies_) {
      if (IsNear(e)) nearby_.push_back(&e);
    }
  }

 private:
  std::vector<Enemy*> nearby_;
};
```

**メンバにして、`reserve` しておき、毎フレーム `clear()`** します。`clear()` は容量を残すので、**2 フレーム目以降は確保が起きません**。

### 固定長にする

```cpp
std::array<Enemy*, 64> nearby;
int count = 0;
for (Enemy& e : enemies) {
  if (IsNear(e) && count < nearby.size()) nearby[count++] = &e;
}
```

**最大数が決まっている**なら、スタック上の `std::array` と個数で、確保なしに書けます。あふれたときの扱い（無視する・assert）を、決めておきます。

標準にはない**固定容量の `vector`**（`boost::static_vector`、C++26 の `std::inplace_vector`）も、便利です。

### フレーム用アリーナ

**フレームの中だけ使う一時データ**は、フレームの頭に位置を戻す、積むだけのメモリにします。

```cpp
std::pmr::monotonic_buffer_resource frame_arena(buffer, sizeof(buffer));
std::pmr::vector<Enemy*> nearby(&frame_arena);

frame_arena.release();
```

`std::pmr` を使うと、**`vector` や `string` をそのまま**アリーナに乗せられます（[std::pmr](../stl/memory/pmr.md)、[メモリ確保](allocation.md)）。

### 文字列を避ける

| やりたいこと | 確保しない方法 |
| --- | --- |
| 引数に文字列を渡す | **`std::string_view`**（コピーしない）。`const std::string&` より柔軟 |
| 文字列を作って、ログ・表示に使う | **`std::format_to` / `std::format_to_n`** で、固定バッファに書く |
| 文字列の比較・キー | <strong>ハッシュ値や ID（整数）</strong>にする（[文字列とハッシュ](strings-hash.md)） |
| 数値を文字列にする | `std::to_chars` で、バッファに書く |
| UI（ImGui）の表示 | `ImGui::Text("%d", n)` のような、**書式付き**。`std::string` を作らない |

```cpp
char buffer[64];
auto result = std::format_to_n(buffer, sizeof(buffer) - 1, "HP: {} / {}", hp, max_hp);
*result.out = '\0';
ImGui::TextUnformatted(buffer);
```

### std::function を避ける

| 方法 | 説明 |
| --- | --- |
| **テンプレート引数**にする | `template <typename F> void ForEach(F&& f)`。インライン化もされる |
| **関数ポインタ** | キャプチャなしなら、これで十分 |
| `std::move_only_function`（C++23） | ムーブ専用。確保は、同じく大きいときに起きる |
| **小さいキャプチャにする** | 内部に収まる大きさ（ポインタ 1〜2 個）なら、確保しない |

### shared_ptr を避ける

毎フレーム `make_shared` するなら、**プール**にするか、**所有者を 1 つ**にして、ほかは生のポインタや、ハンドルにします（[ハンドル](../engine/handle.md)、[所有権](../basics/ownership.md)）。

### プールにする

敵・弾・エフェクトのように、**作っては消す**ものは、**あらかじめ確保したプール**から借りて、返します（[オブジェクトプール](../design/patterns/object-pool.md)）。

### 例外を使わない

ループの中での例外は、**非常に遅い**ので、**エラーは戻り値**（`std::optional`、`std::expected`）で扱います（[エラー処理の方針](../design/foundations/error-handling.md)）。

## 許されるもの

| 場面 | 確保 |
| --- | --- |
| **起動時・ロード時** | OK。まとめて確保する |
| **シーン切り替え・メニュー** | OK（フレームの落ち込みが目立たない） |
| **エディター・ツール** | OK。速さが、最優先ではない |
| **まれにしか起きない処理** | 使う頻度を見て判断（毎フレームでなければ） |

**ルール**：<strong>「毎フレーム・毎エンティティ」で実行される所だけ、確保なしにする</strong>。それ以外は、読みやすさを優先します。

<!-- fig:arena-bump:begin -->

<svg class="fig illust motion" data-fig="arena-bump" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-arena-bump" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">フレーム アロケータ: ポインタを進めるだけで確保し、フレーム末に巻き戻す</text>
<rect x="70" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="110" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="190" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="230" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="270" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="310" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="350" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="390" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="430" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="470" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="510" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="550" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="590" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="630" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="670" y="150" width="38" height="44" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="67" y="128" width="6" height="18" fill="#e5484d"><animate attributeName="x" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0581;0.0968;0.2065;0.2452;0.3548;0.3935;0.5032;0.5419;0.7097;0.7613;1.0000" values="67;67;147;147;307;307;347;347;467;467;67;67"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0965;0.0968;0.7094;0.7097;1.0000" values="0;0;1;1;0;0"/><rect x="70" y="150" width="78" height="44" fill="#2563eb" opacity="0.9"/>
<text x="110.0" y="178" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">A (2)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2449;0.2452;0.7094;0.7097;1.0000" values="0;0;1;1;0;0"/><rect x="150" y="150" width="158" height="44" fill="#2ea043" opacity="0.9"/>
<text x="230.0" y="178" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">B (4)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3933;0.3935;0.7094;0.7097;1.0000" values="0;0;1;1;0;0"/><rect x="310" y="150" width="38" height="44" fill="#e5aa28" opacity="0.9"/>
<text x="330.0" y="178" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">C (1)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5417;0.5419;0.7094;0.7097;1.0000" values="0;0;1;1;0;0"/><rect x="350" y="150" width="118" height="44" fill="#7c3aed" opacity="0.9"/>
<text x="410.0" y="178" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">D (3)</text>
</g>
<text x="70" y="116" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">先頭からの使用量(赤い印 = 次に確保する位置)</text>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">最初に大きな領域を 1 つ確保しておく(16 マス)<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0965;0.0968;1.0000" values="1;1;0;0"/></text>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">A を確保: 印を 2 マス進めるだけ<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0965;0.0968;0.2449;0.2452;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">B を確保: 4 マス進める<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2449;0.2452;0.3933;0.3935;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">C, D も同様。確保 1 回につき、足し算 1 回だけ<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3933;0.3935;0.5417;0.5419;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">合計 10 マス使用<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5417;0.5419;0.7094;0.7097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="290" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム末: 印を先頭に戻す。解放は 1 回だけで、個別の free は不要<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7094;0.7097;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:arena-bump:end -->

## よくあるミス

??? failure "ループの中で、ローカルの `std::vector` を作っている"
    毎フレーム確保します。**メンバにして、`reserve` + `clear()`** で使い回します。

??? failure "`clear()` の代わりに、新しい `vector` を代入する"
    容量が捨てられ、また確保します。`clear()` を使います。

??? failure "ログ用に毎フレーム `std::string` を作って連結している"
    ログのレベルを確認してから、文字列を作ります。固定バッファに書きます。

??? failure "`const std::string&` に、文字列リテラルを渡して、一時 `string` ができる"
    `std::string_view` を受け取れば、確保しません。

??? failure "`std::function` のキャプチャが大きく、毎フレーム確保している"
    テンプレート引数・関数ポインタにするか、小さなキャプチャにします。

??? failure "`shared_ptr` を、一時的な参照のために、値渡しする"
    参照カウントの原子操作が、毎回かかります。`const&` か生ポインタで渡します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>毎フレーム実行される所では、ヒープ確保をしない。</strong>確保は、初期化・ロード時に
    - [x] 隠れた確保：<strong>`std::string` の連結・作成、ローカル `vector`、`std::function`、`make_shared`、`map` の挿入</strong>
    - [x] <strong>`reserve` + `clear()` で使い回す</strong>。<strong>固定長・アリーナ・プール</strong>も使う
    - [x] <strong>`operator new` を数える</strong>と、見つかる。ループ中は、<strong>0 回</strong>が理想
    - [x] 文字列は<strong>`string_view`・ID・`format_to`</strong>。エラーは<strong>例外でなく戻り値</strong>

## 関連ページ

- [最適化の進め方](index.md)
- [メモリ確保](allocation.md)
- [文字列とハッシュ](strings-hash.md)
- [フレーム時間の設計](frame-budget.md)
- [std::pmr](../stl/memory/pmr.md)
- [オブジェクトプール](../design/patterns/object-pool.md)
- [プロファイラー（Visual Studio）](../vs/profiler.md)
- [フレームアロケータ](allocators/frame.md)
- [リニアアロケータ](allocators/linear.md)
