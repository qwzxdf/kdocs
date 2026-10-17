---
title: std::hash
tags:
  - ユーティリティ
  - ハッシュ
---

# std::hash

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++11〜</span>
`#include <functional>`
</div>

<strong>ハッシュ（hash）</strong> とは、**任意のデータを、決まった大きさの整数（ハッシュ値）に変える計算**です。同じデータからは必ず同じ値が出て、違うデータからは（ほとんどの場合）違う値が出ます。`std::hash<T>` は、その計算を行う標準の関数オブジェクトで、`std::hash<std::string>{}("enemy")` のように呼ぶと整数が返ります。[`std::unordered_map`](../containers/unordered_map.md) と [`std::unordered_set`](../containers/unordered_set.md) は、**キーをハッシュ値に変えて、その値で「どの箱（バケット）に入れるか」を決める**ことで、検索を平均 O(1) で行っています。そのため、`unordered_map` のキーに自作の型を使いたいときは、**`std::hash` を自分で用意する**必要があります。

!!! tip "ポイント"
    - **整数・文字列・ポインタ・enum は、そのまま `unordered_map` のキーにできる**（標準が `std::hash` を用意している）。
    - <strong>自作の構造体をキーにするには、`std::hash<T>` の特殊化（と `operator==`）を書く。</strong>
    - 複数のメンバを混ぜるときは **`hash_combine`**（標準にはないので自分で書く）。
    - `std::hash` は**同じプログラムの中で同じ値を返す**だけ。実行ごと・環境ごとの値は保証されない。**ファイルに保存したり、ネットワークで送ったりしてはいけない**。
    - 暗号用のハッシュ（SHA-256 など）ではない。**安全のためには使えない**。
    - 「名前の文字列 → ID」の固定のハッシュが欲しいなら、**FNV-1a** を `constexpr` で自作する。

!!! info "このページを読む前に"
    [std::unordered_map](../containers/unordered_map.md) を先に読んでください。[テンプレート](../../basics/template.md) の特殊化と、[計算量](../../basics/big-o.md)（O(1)）も関係します。

## ハッシュとは

<svg class="fig flow" viewBox="0 0 1156 112" role="img" aria-label="ハッシュで、入れる箱を決める"><defs><marker id="fl43647" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ハッシュで、入れる箱を決める</text><line x1="111.0" y1="64.0" x2="169.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43647)"/><line x1="285.0" y1="64.0" x2="343.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43647)"/><line x1="544.0" y1="64.0" x2="602.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43647)"/><text x="573.0" y="58.0" text-anchor="middle" style="font-size:12px">余りを取る</text><line x1="853.0" y1="64.0" x2="911.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43647)"/><rect x="28.0" y="44.0" width="80" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="68.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">"enemy"</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="172.0" y="44.0" width="110" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="227.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ハッシュ関数</text><circle cx="174.0" cy="46.0" r="10" fill="#2ea043"/><text x="174.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="346.0" y="44.0" width="195" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="443.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">大きな整数 0x5A3C9E71…</text><circle cx="348.0" cy="46.0" r="10" fill="#e5a828"/><text x="348.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="605.0" y="44.0" width="245" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="727.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">バケット数で割る （たとえば 8）</text><circle cx="607.0" cy="46.0" r="10" fill="#e5484d"/><text x="607.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="914.0" y="44.0" width="214" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="1021.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">箱 [5] に入れる / から探す</text><circle cx="916.0" cy="46.0" r="10" fill="#9664e6"/><text x="916.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text></svg>

| 性質 | 意味 |
| --- | --- |
| **決定的** | 同じ入力からは、いつも同じ値が出る |
| **速い** | 計算が軽い。キーを探すたびに呼ばれるため |
| **ばらける** | 似た入力からも、かけ離れた値が出る。偏ると同じ箱に集まって遅くなる |
| **衝突する** | 違う入力が同じ値になることがある。`unordered_map` は、同じ箱の中を `==` で比べて区別する |
| **元に戻せない** | ハッシュ値から、元のデータは取り出せない |

「衝突（collision）」は避けられません。`unordered_map` は、衝突しても正しく動きます（遅くなるだけ）。ただし、**キーの `==` とハッシュは矛盾してはいけません**。「`a == b` なら、必ず `hash(a) == hash(b)`」である必要があります。

## 標準で対応している型

| 型 | ハッシュ |
| --- | --- |
| `int`、`long`、`char`、`bool` などの整数 | 値そのまま（実装による）。**ばらけない**ことがある |
| `float`、`double` | ビット列から計算（`-0.0` と `0.0` は同じ値） |
| `enum`、`enum class` | 中身の整数と同じ（C++14 以降） |
| `T*`（ポインタ） | アドレスから計算 |
| `std::string`、`std::string_view` など | 文字列の中身から計算（`string` と `string_view` は同じ値） |
| `std::unique_ptr<T>`、`std::shared_ptr<T>` | 持っているポインタのハッシュ |
| `std::optional<T>` | 中の値のハッシュ（空は決まった値） |
| `std::bitset<N>`、`std::vector<bool>` | 中身から計算 |
| `std::error_code`、`std::thread::id`、`std::type_index` | あり |
| **`std::pair`、`std::tuple`、`std::array`、`std::vector<T>`** | **ない**（自分で用意する） |

!!! warning "pair や tuple、vector はキーにできない"
    `std::unordered_map<std::pair<int, int>, int>` は、そのままではコンパイルエラーです。`std::hash<std::pair<int, int>>` が標準に無いからです。次の「自作のハッシュ」で対応します（座標 `(x, y)` をキーにする、は定番です）。

## 関数一覧

| 名前 | 重要度 | 何をする |
| --- | --- | --- |
| [ハッシュ値を計算する](#call) | <span class="rank rank-often">よく使う</span> | ハッシュ値を計算する |
| [`std::hash` の特殊化](#specialization) | <span class="rank rank-often">よく使う</span> | 自作の型にハッシュを用意する |
| [`hash_combine`](#hash_combine) | <span class="rank rank-often">よく使う</span> | 複数のハッシュ値を混ぜる（自作） |
| [ハッシュ関数オブジェクトを渡す](#custom_hasher) | <span class="rank rank-sometimes">たまに</span> | `unordered_map` に別のハッシュを使わせる |
| [透過的ハッシュ](#transparent) <span class="ver ver-20">C++20</span> | <span class="rank rank-sometimes">たまに</span> | `string_view` で、`string` をキーにした表を引く |
| [FNV-1a](#fnv1a) | <span class="rank rank-sometimes">たまに</span> | 文字列から固定の ID を作る（コンパイル時にも） |
| [`bucket_count` と `load_factor`](#bucket_load) | <span class="rank rank-sometimes">たまに</span> | 箱の数と、詰まり具合 |
| [`std::hash` が返す型 `size_t`](#size_t) | <span class="rank rank-rare">知ってるだけ</span> | ハッシュ値の型 |

## よくある使い方

```cpp
#include <functional>
#include <print>
#include <string>

int main() {
  std::hash<std::string> hasher;
  std::println("{}", hasher("enemy") == hasher("enemy"));  // 同じ入力は同じ値
  std::println("{}", hasher("enemy") == hasher("player"));  // 違う入力は（ほぼ）違う値
  std::println("{}", hasher("enemy") == std::hash<std::string_view>{}("enemy"));
}
```

```text title="実行結果"
true
false
true
```

ハッシュ値そのもの（数字）は、環境によって違うので、**表示して使うことは普通ありません**。「同じか違うか」だけを見ます。

## 関数・仕組みの詳しい説明

### ハッシュ値を計算する {#call data-toc-label="ハッシュ値の計算"}

```cpp
template <class T>
struct hash {
  std::size_t operator()(const T& value) const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` | ハッシュを計算する値 |

- 戻り値: `std::size_t` のハッシュ値
- 計算量: 値の大きさに比例（文字列なら長さに比例 O(n)、整数なら O(1)）
- 実行する環境・コンパイラ・プログラムの実行ごとに、**値が変わることがあります**。ファイルに保存した値を、次の実行で使ってはいけません

### `std::hash` の特殊化 {#specialization data-toc-label="std::hash の特殊化"}

自作の型を `unordered_map` / `unordered_set` のキーにするには、**`std::hash<自作の型>` を特殊化**します。あわせて `operator==` も必要です。

```cpp
#include <cstddef>
#include <functional>
#include <print>
#include <unordered_map>

struct GridPos {
  int x;
  int y;
  bool operator==(const GridPos&) const = default;  // == も必要（キーが同じかの判定）
};

// std 名前空間に、GridPos 用の hash を追加する
template <>
struct std::hash<GridPos> {
  std::size_t operator()(const GridPos& p) const noexcept {
    std::size_t h = std::hash<int>{}(p.x);
    h ^= std::hash<int>{}(p.y) + 0x9e3779b9 + (h << 6) + (h >> 2);  // y を混ぜる
    return h;
  }
};

int main() {
  std::unordered_map<GridPos, int> cost;
  cost[{2, 3}] = 10;
  cost[{4, 1}] = 20;
  std::println("(2, 3) のコスト = {}", cost[{2, 3}]);
  std::println("(9, 9) はある？ {}", cost.contains({9, 9}));
}
```

```text title="実行結果"
(2, 3) のコスト = 10
(9, 9) はある？ false
```

!!! warning "ハッシュの書き方のルール"
    - **`a == b` なら、必ず `hash(a) == hash(b)`**。`==` で比べるメンバだけをハッシュに入れます（比べないメンバを入れると、同じ扱いのキーが別の箱に入って、見つからなくなります）。
    - `operator()` は **`const`** と **`noexcept`** にします。
    - 特殊化は `std` 名前空間に書きます（`template <> struct std::hash<GridPos>` と書くのが簡単）。

### hash_combine {#hash_combine}

標準には、複数のハッシュ値を混ぜる関数がありません（Boost の `hash_combine` が有名です）。自分で書きます。

```cpp
#include <cstddef>
#include <functional>

// 既にあるハッシュ値 seed に、value のハッシュを混ぜる
template <class T>
void HashCombine(std::size_t& seed, const T& value) {
  seed ^= std::hash<T>{}(value) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
}

// 使い方：複数のメンバを順に混ぜる
struct Tile {
  int x;
  int y;
  int layer;
  bool operator==(const Tile&) const = default;
};

template <>
struct std::hash<Tile> {
  std::size_t operator()(const Tile& t) const noexcept {
    std::size_t seed = 0;
    HashCombine(seed, t.x);
    HashCombine(seed, t.y);
    HashCombine(seed, t.layer);
    return seed;
  }
};
```

| 部分 | 意味 |
| --- | --- |
| `0x9e3779b9` | 黄金比から作られた数。ビットをばらけさせるための定数 |
| `(seed << 6) + (seed >> 2)` | これまでの値をずらして混ぜる。順番が違えば結果も違う |
| `^=` | 排他的論理和で混ぜる |

- 単純に `x ^ y` とすると、`(1, 2)` と `(2, 1)` が同じ値になるなど、**衝突しやすく**なります。`hash_combine` のように、ずらしてから混ぜます
- 順番が結果に影響するので、`operator==` と矛盾しないよう、必ず**同じ順番**で混ぜます

### ハッシュ関数オブジェクトを渡す {#custom_hasher data-toc-label="ハッシュ関数オブジェクトを渡す"}

```cpp
template <class Key, class T,
          class Hash = std::hash<Key>,
          class KeyEqual = std::equal_to<Key>,
          class Allocator = std::allocator<std::pair<const Key, T>>>
class unordered_map;
```

| 引数 | 意味 |
| --- | --- |
| `Hash` | ハッシュを計算する関数オブジェクトの型 |
| `KeyEqual` | キーが同じかを調べる関数オブジェクトの型 |

- 標準の型（`std::pair` など）をキーにしたいが、`std::hash` の特殊化を `std` に追加したくないときに使います

```cpp
struct PairHash {
  std::size_t operator()(const std::pair<int, int>& p) const noexcept {
    std::size_t seed = 0;
    HashCombine(seed, p.first);
    HashCombine(seed, p.second);
    return seed;
  }
};

std::unordered_map<std::pair<int, int>, int, PairHash> grid;  // 3 つ目の引数で渡す
grid[{1, 2}] = 5;
```

### 透過的ハッシュ（string_view で引く） <span class="ver ver-20">C++20</span> {#transparent data-toc-label="透過的ハッシュ"}

`std::unordered_map<std::string, int>` を、`std::string_view` や `const char*` で引くと、**毎回 `std::string` を作って<strong>から探します（メモリ確保が起きて遅い）。C++20 では、</strong>透過的（transparent）なハッシュ**を指定すると、`string_view` のまま引けます。

```cpp
#include <functional>
#include <print>
#include <string>
#include <string_view>
#include <unordered_map>

struct StringHash {
  using is_transparent = void;  // これが「透過的」の印
  std::size_t operator()(std::string_view s) const noexcept {
    return std::hash<std::string_view>{}(s);
  }
};

int main() {
  std::unordered_map<std::string, int, StringHash, std::equal_to<>> scores;
  scores["Alice"] = 100;

  std::string_view name = "Alice";
  auto it = scores.find(name);  // std::string を作らずに探せる（C++20）
  std::println("{}", it != scores.end() ? it->second : -1);
}
```

```text title="実行結果"
100
```

- 3 つ目の引数にハッシュ（`is_transparent` 付き）、4 つ目に `std::equal_to<>`（中身を指定しない版）を渡します
- 文字列で何度も引く、ゲームのアセット名・設定名の検索で効果が出ます

### FNV-1a {#fnv1a data-toc-label="FNV-1a（固定の ID）"}

`std::hash<std::string>` は、実行ごとに値が変わることがあるので、<strong>「アセット名 → ID」をファイルに保存する</strong>ような用途には使えません。この用途には、**値が固定の、自作のハッシュ**を使います。シンプルで速い **FNV-1a** が定番です。`constexpr` にすると、**コンパイル時に計算**でき、`switch` の `case` にも使えます。

```cpp
#include <cstdint>
#include <print>
#include <string_view>

// FNV-1a（32 ビット）：文字ごとに XOR して、素数を掛ける
constexpr std::uint32_t Fnv1a(std::string_view text) {
  std::uint32_t hash = 2166136261u;  // 決まった初期値
  for (char c : text) {
    hash ^= static_cast<std::uint8_t>(c);
    hash *= 16777619u;  // 決まった素数
  }
  return hash;
}

constexpr std::uint32_t operator""_id(const char* text, std::size_t length) {
  return Fnv1a(std::string_view(text, length));
}

int main() {
  constexpr std::uint32_t kPlayer = "player"_id;  // コンパイル時に計算される
  std::println("{}", Fnv1a("player") == kPlayer);

  switch (Fnv1a("enemy")) {
    case "player"_id: std::println("プレイヤー"); break;
    case "enemy"_id: std::println("敵"); break;
    default: break;
  }
}
```

```text title="実行結果"
true
敵
```

| 用途 | ハッシュ |
| --- | --- |
| `unordered_map` のキー | `std::hash`（標準でよい） |
| ファイルやネットワークで使う「名前 → ID」 | FNV-1a など、**値が固定のハッシュ**を自作 |
| ファイルの改ざん・破損のチェック | CRC32 / xxHash（速い）、または SHA-256（安全が必要なとき） |
| パスワード・署名 | SHA-256、bcrypt など**暗号用**（`std::hash` や FNV は使えない） |

!!! warning "ID は衝突する"
    32 ビットのハッシュは、数万個の名前があると衝突の可能性が出てきます。**開発中に、ハッシュ値の重複を検出する**チェック（別の名前が同じ ID になっていないか）をビルド時に入れておきます。

### bucket_count と load_factor {#bucket_load data-toc-label="bucket_count と load_factor"}

```cpp
std::size_t bucket_count() const noexcept;
float load_factor() const noexcept;
float max_load_factor() const noexcept;
void rehash(std::size_t count);
```

| 名前 | 意味 |
| --- | --- |
| `bucket_count()` | 箱（バケット）の数 |
| `load_factor()` | 平均の詰まり具合（`size() / bucket_count()`） |
| `max_load_factor()` | `load_factor` がこの値（デフォルト 1.0）を超えると、箱を増やして**全部入れ直す** |
| `rehash(n)` | 箱の数を `n` 以上にして、入れ直す |

- 箱が足りなくなると、全要素のハッシュを使って<strong>入れ直し（rehash）</strong> が起きます。これは <strong>O(n)</strong> で、`vector` の再確保のように、そのときだけ重くなります
- 入れる数が分かっているなら、先に `reserve(n)`（`rehash` と似ている）で箱を用意します。→ [`unordered_map::reserve`](../containers/unordered_map.md#reserve)

### std::hash が返す型 size_t {#size_t data-toc-label="戻り値の型 size_t"}

- 戻り値の型は `std::size_t` で、**環境によって 32 ビットか 64 ビット**です。同じ文字列でも、環境が違えば値が違います（保存に使えない理由の 1 つです）。

## 速さの特徴

| 項目 | 特徴 |
| --- | --- |
| 整数のハッシュ | ほぼ O(1)（値をそのまま返すこともある） |
| 文字列のハッシュ | 長さに比例 O(n)。長い文字列のキーは、ハッシュだけで時間がかかる |
| 偏ったハッシュ | 同じ箱に集まり、検索が O(n) に近づく（最悪） |
| 整数をそのまま返す実装 | 下位ビットだけが同じキー（`16` の倍数など）が同じ箱に集まりやすい |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| 座標（`GridPos`）をキーにしたマップ | `std::hash` の特殊化 + `hash_combine` |
| アセット名で検索する表 | 透過的ハッシュで `string_view` のまま引く |
| 名前 → ID をファイルに保存 | FNV-1a など、値が固定のハッシュ |
| 文字列の `switch` | `constexpr` のハッシュ + `case "name"_id:` |
| 重複チェック（同じ設定を 2 回読み込まない） | `unordered_set` |

## よくあるミス

??? failure "ハッシュ値をファイルに保存して、次の実行で使う"
    `std::hash` の値は、実行ごと・環境ごとに変わることがあります。保存や通信には、値が固定の FNV-1a や CRC32 を使います。

??? failure "`==` とハッシュが矛盾している"
    `operator==` が `x` だけを比べるのに、ハッシュが `x` と `y` を混ぜていると、「同じキー」が別の箱に入って、見つからなくなります。比べるメンバとハッシュに混ぜるメンバを一致させます。

??? failure "`x ^ y` だけのハッシュ"
    `(1, 2)` と `(2, 1)`、`(5, 5)` と `(0, 0)` が同じ値になり、衝突が増えて遅くなります。`hash_combine` のように混ぜます。

??? failure "キーを書き換える"
    `unordered_map` に入れたあと、キーのメンバを変えると、ハッシュ値が変わり、正しい箱から探せなくなります。キーは入れたら変えません（`const` で持たれています）。

??? failure "`std::hash` を暗号の代わりに使う"
    安全性はありません。パスワードの保存、署名には、SHA-256 など暗号用のハッシュを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::unordered_map`](../containers/unordered_map.md) | ハッシュを使う表 |
| [`std::map`](../containers/map.md) | ハッシュを使わない。`operator<` で順序付き。キーに `<` があればよい（ハッシュ不要） |
| [`std::equal_to`](../support/functional.md) | キーが等しいかの判定 |
| CRC32 / xxHash / SHA-256 | 用途別のハッシュ。誤り検出・改ざん検出・暗号など |

## コンパイラ対応

| 機能 | GCC | Clang (libc++) | MSVC |
| --- | --- | --- | --- |
| `std::hash`（C++11） | 4.x〜 | 3.x〜 | VS2012〜 |
| 透過的な `unordered_map` の検索（C++20） | 11〜 | 12〜 | VS2019 16.x〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] ハッシュ ＝ データを整数に変える計算。`unordered_map` がキーの検索に使う
    - [x] 整数・文字列・ポインタ・enum は標準で対応。`pair` や自作の構造体は自分で用意
    - [x] `a == b` なら `hash(a) == hash(b)`。比べるメンバと混ぜるメンバをそろえる
    - [x] 複数のメンバは `hash_combine` で混ぜる（`x ^ y` だけにしない）
    - [x] 保存・通信する ID は、値が固定の FNV-1a などを使う。`std::hash` は使わない
    - [x] 暗号には使えない

## 関連ページ

- [std::unordered_map](../containers/unordered_map.md)
- [std::unordered_set](../containers/unordered_set.md)
- [<functional>](../support/functional.md)
- [計算量](../../basics/big-o.md)
- [cppreference: std::hash](https://en.cppreference.com/w/cpp/utility/hash)
