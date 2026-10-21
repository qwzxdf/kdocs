---
title: std::optional
summary: "値が「あるかもしれない・ないかもしれない」を表す。見つからないことを `nullptr` なしで示せる。"
order: 46
tags:
  - ユーティリティ
---

# std::optional

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-17">C++17</span>
`#include <optional>`
</div>

`std::optional<T>` は、<strong>「T の値が 1 つあるか、何も無いか」のどちらかを表す型</strong>です。「見つからなかった」「まだ決まっていない」を、`-1` や `nullptr` のような特別な値を使わずに表せます。中身は値そのものを直接持っているので、ヒープ確保は起きません。

!!! tip "ポイント"
    - <strong>「失敗するかもしれない関数」の戻り値に使う。</strong> 探す関数、パースする関数など。
    - 値があるかは `if (opt)` か `opt.has_value()`、取り出しは `*opt` か `opt->`。
    - 無いときの代わりの値を使うなら `opt.value_or(デフォルト)`。
    - 「なぜ失敗したか」も伝えたいなら [`std::expected`](expected.md)。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md) が分かると読みやすいです。

## 宣言

```cpp
template <class T>
class optional;

inline constexpr std::nullopt_t nullopt;  // 「値なし」を表す定数
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 持つかもしれない値の型（参照は不可） | 必ず |

### 作り方

| 書き方 | 重要度 | 結果 |
| --- | --- | --- |
| `return value;`（戻り値の型が optional） | <span class="rank rank-must">必須</span> | 値あり |
| `return std::nullopt;` | <span class="rank rank-must">必須</span> | 値なし |
| `std::optional<int> o;` | <span class="rank rank-often">よく使う</span> | 値なし |
| `std::optional<int> o = 5;` | <span class="rank rank-often">よく使う</span> | 値あり |
| `std::make_optional(5)` | <span class="rank rank-rare">知ってるだけ</span> | 値あり（型を推論） |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`operator bool`](#bool) | <span class="rank rank-must">必須</span> | 値があるか | O(1) |
| [`operator*`](#deref) | <span class="rank rank-must">必須</span> | 値を取り出す（チェックなし） | O(1) |
| [`operator->`](#arrow) | <span class="rank rank-must">必須</span> | 値のメンバにアクセス | O(1) |
| [`value_or`](#value_or) | <span class="rank rank-must">必須</span> | 値があればそれ、無ければ代わりの値 | O(1) |
| [`has_value`](#has_value) | <span class="rank rank-often">よく使う</span> | 値があるか（`bool` と同じ） | O(1) |
| [`value`](#value) | <span class="rank rank-sometimes">たまに</span> | 値を取り出す（無ければ例外） | O(1) |
| [`reset`](#reset) | <span class="rank rank-sometimes">たまに</span> | 値なしにする | O(1) |
| [`emplace`](#emplace) | <span class="rank rank-sometimes">たまに</span> | その場で値を作る | O(1) |
| [`and_then`](#and_then) | <span class="rank rank-sometimes">たまに</span> | 値があれば optional を返す関数をつなぐ <span class="ver ver-23">C++23</span> | O(1) |
| [`transform`](#transform) | <span class="rank rank-sometimes">たまに</span> | 値があれば変換する <span class="ver ver-23">C++23</span> | O(1) |
| [`or_else`](#or_else) | <span class="rank rank-rare">知ってるだけ</span> | 値が無ければ関数を呼ぶ <span class="ver ver-23">C++23</span> | O(1) |
| [`operator==`](#eq) | <span class="rank rank-rare">知ってるだけ</span> | 比較 | O(1) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 交換 | O(1) |

## よくある使い方

### 1. 見つからないかもしれない検索

```cpp
#include <optional>
#include <print>
#include <string>
#include <vector>

struct Enemy {
  int id;
  std::string name;
};

std::optional<Enemy> FindEnemy(const std::vector<Enemy>& enemies, int id) {
  for (const auto& e : enemies) {
    if (e.id == id) {
      return e;  // 値あり
    }
  }
  return std::nullopt;  // 値なし
}

int main() {
  std::vector<Enemy> enemies = {{1, "スライム"}, {2, "ゴブリン"}};

  if (auto found = FindEnemy(enemies, 2)) {
    std::println("見つかった: {}", found->name);
  }
  if (!FindEnemy(enemies, 9)) {
    std::println("9 番はいない");
  }
}
```

```text title="実行結果"
見つかった: ゴブリン
9 番はいない
```

### 2. 無ければデフォルト値

```cpp
#include <optional>
#include <print>

std::optional<int> LoadVolumeSetting() { return std::nullopt; }  // 設定ファイルに無かった

int main() {
  int volume = LoadVolumeSetting().value_or(80);
  std::println("音量 {}", volume);
}
```

```text title="実行結果"
音量 80
```

### 3. 「まだ決まっていない」メンバ

```cpp
#include <optional>
#include <print>

struct Unit {
  std::optional<int> target_id;  // 攻撃対象が決まっていないこともある
};

int main() {
  Unit unit;
  std::println("対象あり？ {}", unit.target_id.has_value());
  unit.target_id = 42;
  std::println("対象 {}", *unit.target_id);
  unit.target_id.reset();  // 対象を外す
  std::println("対象あり？ {}", unit.target_id.has_value());
}
```

```text title="実行結果"
対象あり？ false
対象 42
対象あり？ false
```

## 関数の詳しい説明

### operator bool {#bool}

```cpp
constexpr explicit operator bool() const noexcept;
```

- 値があれば `true`。`if (opt)` の形で使います

### operator* {#deref}

```cpp
constexpr T& operator*() & noexcept;
constexpr const T& operator*() const& noexcept;
```

- 値の参照を返します。**値が無いとき未定義動作**（チェックしない）

### operator-> {#arrow}

```cpp
constexpr T* operator->() noexcept;
```

- 値のメンバにアクセスします。**値が無いとき未定義動作**

```cpp
#include <optional>
#include <print>
#include <string>

int main() {
  std::optional<std::string> name = "Alice";
  if (name) {
    std::println("{} は {} 文字", *name, name->size());
  }
}
```

```text title="実行結果"
Alice は 5 文字
```

### value_or {#value_or}

```cpp
template <class U>
constexpr T value_or(U&& default_value) const&;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `default_value` | `T` に変換できる値 | 値が無いときに返す値 |

- 戻り値: 値があればそのコピー、無ければ `default_value`

<div class="anim" data-label="o.value_or(9)">
_ # 空
*9 # 空なので 9 を返す（o は空のまま）
</div>

```cpp
#include <optional>
#include <print>

int main() {
  std::optional<int> a = 5;
  std::optional<int> b;
  std::println("{} {}", a.value_or(0), b.value_or(0));
}
```

```text title="実行結果"
5 0
```

### has_value {#has_value}

```cpp
constexpr bool has_value() const noexcept;
```

- 値があれば `true`。`if (opt)` と同じ意味ですが、意図をはっきり書きたいときに使います

### value {#value}

```cpp
constexpr T& value() &;
constexpr const T& value() const&;
```

- 値の参照を返します。**値が無ければ `std::bad_optional_access` 例外**

```cpp
#include <optional>
#include <print>

int main() {
  std::optional<int> empty;
  try {
    std::println("{}", empty.value());
  } catch (const std::bad_optional_access&) {
    std::println("値が無い");
  }
}
```

```text title="実行結果"
値が無い
```

!!! note "実際は"
    例外を使わないゲームでは、`if (opt)` で確認してから `*opt` を使うのが普通です。

### reset {#reset}

```cpp
constexpr void reset() noexcept;
```

- 値なしにします。持っていた値のデストラクタが呼ばれます。`opt = std::nullopt;` と同じです

<div class="anim" data-label="o.reset()">
5 # 値を持っている
x5 # 値を破棄する
_ # 空（std::nullopt）
</div>

### emplace {#emplace}

```cpp
template <class... Args>
constexpr T& emplace(Args&&... args);
```

- 今の値を消して、`args` で新しい値をその場で作ります

<div class="anim" data-label="o.emplace(5)">
_ # 空
+5 # その場で値を作る
</div>

```cpp
#include <optional>
#include <print>
#include <string>

int main() {
  std::optional<std::string> message;
  message.emplace(3, '!');  // std::string(3, '!')
  std::println("{}", *message);
}
```

```text title="実行結果"
!!!
```

### and_then <span class="ver ver-23">C++23</span> {#and_then data-toc-label="and_then"}

```cpp
template <class F>
constexpr auto and_then(F&& f) &;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 関数 | 値を受け取り、**optional を返す**関数 |

- 値があれば `f(値)` の結果を、無ければ空の optional を返します。失敗するかもしれない処理を次々つなぐときに使います

### transform <span class="ver ver-23">C++23</span> {#transform data-toc-label="transform"}

```cpp
template <class F>
constexpr auto transform(F&& f) &;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 関数 | 値を受け取り、**普通の値**を返す関数 |

- 値があれば `f(値)` を optional に包んで返し、無ければ空の optional を返します

### or_else <span class="ver ver-23">C++23</span> {#or_else data-toc-label="or_else"}

```cpp
template <class F>
constexpr optional or_else(F&& f) const&;
```

- 値があればそのまま、無ければ `f()`（optional を返す関数）の結果を返します

```cpp
#include <optional>
#include <print>
#include <string>

std::optional<int> ParseLevel(const std::string& s) {
  if (s.empty()) {
    return std::nullopt;
  }
  return std::stoi(s);
}

std::optional<int> ClampLevel(int lv) {
  if (lv < 1 || lv > 99) {
    return std::nullopt;
  }
  return lv;
}

int main() {
  auto title = ParseLevel("12")
                   .and_then(ClampLevel)                                // 範囲チェック
                   .transform([](int lv) { return "Lv." + std::to_string(lv); })
                   .value_or("不明");
  auto bad = ParseLevel("")
                 .or_else([] { return std::optional<int>(1); })  // 無ければ 1
                 .value();
  std::println("{} / {}", title, bad);
}
```

```text title="実行結果"
Lv.12 / 1
```

### operator== {#eq}

- optional 同士、または optional と値を比べられます。値が無いもの同士は等しく、値が無いものと値があるものは等しくありません

### swap {#swap}

```cpp
constexpr void swap(optional& other);
```

- 中身を交換します

## フラグ・オプション

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `std::nullopt` | <span class="rank rank-must">必須</span> | 「値なし」 |
| `std::in_place` | <span class="rank rank-rare">知ってるだけ</span> | コンストラクタで「この引数で値を作って」という目印 |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    // -1 を「見つからない」に使う
    int FindIndex(int id);

    // 出力引数と bool
    bool TryGetSetting(const std::string& key, int* out);
    ```

=== "今の書き方（C++17）"

    ```cpp
    std::optional<int> FindIndex(int id);

    std::optional<int> GetSetting(const std::string& key);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 検索 | 「ID の敵」「近くのアイテム」を探す関数の戻り値 |
| 設定の読み込み | 項目が無いかもしれない |
| 当たり判定 | 交差点があれば位置を返す `std::optional<Vec2> Raycast(...)` |
| 状態 | 攻撃対象、選択中のユニット |

## パフォーマンス

- 値を直接持ち、加えて「あるかどうか」の bool を 1 つ持つだけです。ヒープは使いません。
- そのぶん `sizeof(std::optional<T>)` は `T` より少し大きくなります（パディングで 2 倍近くになることも）。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 値が無いのに `*opt` / `opt->` | 未定義動作 |
| 値が無いのに `opt.value()` | `std::bad_optional_access` 例外 |

## よくあるミス

??? failure "確認せずに * で取り出す"
    ```cpp
    auto e = FindEnemy(enemies, 9);
    std::println("{}", e->name);  // 見つからなければ未定義動作
    ```

??? failure "optional<bool> を if で判定して混乱する"
    `std::optional<bool> flag = false;` のとき、`if (flag)` は **true**（値があるので）です。中身を見るなら `if (flag && *flag)` か `flag.value_or(false)`。

??? failure "参照を入れようとする"
    `std::optional<Enemy&>` は C++23 では作れません。参照したいだけならポインタ（`Enemy*`、無ければ `nullptr`）を使います。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::expected<T, E>`](expected.md) | 失敗の理由（エラー）も持てる <span class="ver ver-23">C++23</span> | なぜ失敗したかを伝えたい |
| [`std::unique_ptr<T>`](unique_ptr.md) | ヒープに持つ。ポリモーフィズムができる | 派生クラスを持ちたい |
| `T*`（nullptr あり） | 持ち主ではない | 既にあるものを指すだけ |
| [`std::variant`](variant.md) | 複数の型のどれか | 「A か B か C」 |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::optional` <span class="ver ver-17">C++17</span> | ○ | ○ | ○ |
| `and_then` / `transform` / `or_else` <span class="ver ver-23">C++23</span> | VS 2022 17.6〜 | 12〜 | 14〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「あるか無いか」は `std::optional<T>`。無いときは `std::nullopt`
    - [x] `if (opt)` で確認してから `*opt` / `opt->`
    - [x] 代わりの値は `value_or`

## 関連ページ

- [cpprefjp: std::optional](https://cpprefjp.github.io/reference/optional/optional.html)
- [cppreference: std::optional](https://en.cppreference.com/w/cpp/utility/optional)
