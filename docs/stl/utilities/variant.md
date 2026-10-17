---
title: std::variant
tags:
  - ユーティリティ
---

# std::variant

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`std::variant<A, B, C>` は、**A・B・C のうち、どれか 1 つの型の値を持つ型**です（型安全な共用体）。「今どの型が入っているか」を自分で覚えていてくれるので、間違った型として読み出す事故が起きません。中身に応じた処理は `std::visit` でまとめて書けます。継承と仮想関数を使わずに「いろいろな種類のもの」を 1 つの型で扱えます。

!!! tip "ポイント"
    - <strong>種類が決まっていて少ない「どれか」を表すのに使う。</strong> イベントの種類、コマンドの種類、ステート、設定値（int か float か文字列か）。
    - 中身に応じた処理は `std::visit` + overloaded パターン（[よくある使い方 2](#2-種類ごとに処理を書き分けるoverloaded)）。
    - どの型か調べるなら `std::holds_alternative<T>(v)`、取り出すなら `std::get_if<T>(&v)`。
    - ヒープを使わない。大きさは「一番大きい型 + 少し」。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md) と [ラムダ式](../../basics/lambda.md) を先に読むと分かりやすいです。

## 宣言

```cpp
template <class... Types>
class variant;

struct monostate {};  // 「何も入っていない」を表す空の型
```

| テンプレート引数 | 意味 |
| --- | --- |
| `Types...` | 入れられる型の候補。最初の型がデフォルト値になる |

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [代入](#assign) | <span class="rank rank-must">必須</span> | 候補のどれかの型の値を入れる |
| [`std::visit`](#visit) | <span class="rank rank-must">必須</span> | 今の中身に応じて関数を呼ぶ |
| [`std::holds_alternative`](#holds_alternative) | <span class="rank rank-often">よく使う</span> | 今その型が入っているか |
| [`std::get_if`](#get_if) | <span class="rank rank-often">よく使う</span> | その型ならポインタ、違えば nullptr |
| [`std::get`](#get) | <span class="rank rank-sometimes">たまに</span> | その型として取り出す（違えば例外） |
| [`index`](#index) | <span class="rank rank-sometimes">たまに</span> | 今何番目の型が入っているか |
| [`emplace`](#emplace) | <span class="rank rank-sometimes">たまに</span> | その場で値を作る |
| [`std::monostate`](#monostate) | <span class="rank rank-rare">知ってるだけ</span> | 「空」を表す候補 |
| [`valueless_by_exception`](#valueless) | <span class="rank rank-rare">知ってるだけ</span> | 例外で壊れた状態か |
| [`std::variant_size`](#variant_size) | <span class="rank rank-rare">知ってるだけ</span> | 候補の数 |

## よくある使い方

### 1. どれかの型の値を持つ

```cpp
#include <print>
#include <string>
#include <variant>

int main() {
  std::variant<int, float, std::string> setting = 60;  // int が入る
  std::println("int？ {}", std::holds_alternative<int>(setting));

  setting = std::string("高画質");  // string に入れ替わる
  if (auto* s = std::get_if<std::string>(&setting)) {
    std::println("文字列: {}", *s);
  }
}
```

```text title="実行結果"
int？ true
文字列: 高画質
```

### 2. 種類ごとに処理を書き分ける（overloaded）

```cpp
#include <print>
#include <variant>
#include <vector>

struct Move {
  int dx;
  int dy;
};
struct Attack {
  int target;
};
struct Wait {};

using Command = std::variant<Move, Attack, Wait>;

// ラムダをまとめて 1 つの関数オブジェクトにする定番の書き方
template <class... Fs>
struct Overloaded : Fs... {
  using Fs::operator()...;
};

int main() {
  std::vector<Command> commands = {Move{1, 0}, Attack{3}, Wait{}};
  for (const auto& cmd : commands) {
    std::visit(Overloaded{
                   [](const Move& m) { std::println("移動 ({}, {})", m.dx, m.dy); },
                   [](const Attack& a) { std::println("敵 {} を攻撃", a.target); },
                   [](const Wait&) { std::println("待機"); },
               },
               cmd);
  }
}
```

```text title="実行結果"
移動 (1, 0)
敵 3 を攻撃
待機
```

!!! note "実際は"
    どれかの型の処理を書き忘れると**コンパイルエラー**になるので、新しいコマンドを追加したときに対応漏れが起きません。switch 文や仮想関数より安全です。

## 関数の詳しい説明

### 代入 {#assign}

```cpp
template <class T>
variant& operator=(T&& t);
```

- 候補の型の値を入れると、その型に切り替わります（前の値のデストラクタが呼ばれる）
- 何も入れずに作ると、**最初の候補の型**のデフォルト値が入ります

<div class="anim" data-label="v = 1.5">
5 # int を持っている
x5 # 今の値を破棄する
+1.5 # double に切り替わる
</div>

### std::visit {#visit}

```cpp
template <class Visitor, class... Variants>
constexpr decltype(auto) visit(Visitor&& vis, Variants&&... vars);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `vis` | 関数オブジェクト | **すべての候補の型**を受け取れる関数（ラムダの `auto` 引数か、overloaded） |
| `vars` | variant | 対象の variant（複数渡すと全組み合わせ） |

- 戻り値: `vis` の戻り値（すべての型で同じ型を返す必要がある）

```cpp
#include <print>
#include <string>
#include <variant>

int main() {
  std::variant<int, std::string> v = 42;
  // auto 引数のラムダなら全部の型を受け取れる
  std::visit([](const auto& x) { std::println("中身: {}", x); }, v);
  v = "text";
  std::visit([](const auto& x) { std::println("中身: {}", x); }, v);
}
```

```text title="実行結果"
中身: 42
中身: text
```

### std::holds_alternative {#holds_alternative}

```cpp
template <class T, class... Types>
constexpr bool holds_alternative(const std::variant<Types...>& v) noexcept;
```

- 今 `T` が入っていれば `true`

### std::get_if {#get_if}

```cpp
template <class T, class... Types>
constexpr std::add_pointer_t<T> get_if(std::variant<Types...>* pv) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pv` | variant の**ポインタ** | `&v` を渡す |

- 今 `T` が入っていればそのポインタ、違えば `nullptr`。例外を使わずに安全に取り出せます

```cpp
#include <print>
#include <variant>

int main() {
  std::variant<int, float> v = 1.5f;
  if (auto* f = std::get_if<float>(&v)) {
    std::println("float {}", *f);
  }
  std::println("int？ {}", std::get_if<int>(&v) != nullptr);
}
```

```text title="実行結果"
float 1.5
int？ false
```

### std::get {#get}

```cpp
template <class T, class... Types>
constexpr T& get(std::variant<Types...>& v);
template <std::size_t I, class... Types>
constexpr auto& get(std::variant<Types...>& v);
```

- 型（または番号）を指定して取り出します。**違う型が入っていると `std::bad_variant_access` 例外**

```cpp
#include <print>
#include <variant>

int main() {
  std::variant<int, float> v = 3;
  std::println("{}", std::get<int>(v));
  try {
    std::get<float>(v);
  } catch (const std::bad_variant_access&) {
    std::println("float ではない");
  }
}
```

```text title="実行結果"
3
float ではない
```

### index {#index}

```cpp
constexpr std::size_t index() const noexcept;
```

- 今何番目の候補が入っているか（0 始まり）。セーブデータに「どの型か」を保存するときに使えます

```cpp
#include <print>
#include <string>
#include <variant>

int main() {
  std::variant<int, float, std::string> v = 2.0f;
  std::println("{}", v.index());
}
```

```text title="実行結果"
1
```

### emplace {#emplace}

```cpp
template <class T, class... Args>
T& emplace(Args&&... args);
```

- `T` の値をその場で作って入れます

<div class="anim" data-label="v.emplace<double>(1.5)">
5 # int を持っている
x5 # 今の値を破棄する
+1.5 # double をその場で作る
</div>

```cpp
#include <print>
#include <string>
#include <variant>

int main() {
  std::variant<int, std::string> v;
  v.emplace<std::string>(3, 'z');
  std::println("{}", std::get<std::string>(v));
}
```

```text title="実行結果"
zzz
```

### std::monostate {#monostate}

```cpp
struct monostate {};
```

- 候補の最初に置くと「まだ何も入っていない」状態を表せます。最初の型にデフォルトコンストラクタが無いときにも使います

```cpp
#include <print>
#include <variant>

int main() {
  std::variant<std::monostate, int> v;
  std::println("空？ {}", std::holds_alternative<std::monostate>(v));
}
```

```text title="実行結果"
空？ true
```

### valueless_by_exception {#valueless}

```cpp
constexpr bool valueless_by_exception() const noexcept;
```

- 型を切り替える途中で例外が起きて、どの値も入っていない壊れた状態なら `true`。普通は起きません

### std::variant_size {#variant_size}

```cpp
template <class T>
struct variant_size;  // std::variant_size_v<T>
```

- 候補の数をコンパイル時に取得します

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    enum class Type { kInt, kFloat };
    struct Value {
      Type type;
      union {
        int i;
        float f;
      };
    };
    // type を見間違えると壊れた値を読む
    ```

=== "今の書き方（C++17）"

    ```cpp
    using Value = std::variant<int, float>;
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| コマンド / イベント | `variant<Move, Attack, UseItem>` を queue に入れる |
| ステートマシン | `variant<Idle, Walking, Jumping>`（状態ごとのデータも持てる） |
| 設定値・スクリプトの値 | `variant<int, float, bool, std::string>` |
| ネットワークのメッセージ | 受信した種類ごとに visit で処理 |

## パフォーマンス

- ヒープを使わず、一番大きい候補の大きさ + 番号ぶんだけです。
- `std::visit` はジャンプテーブルになり、仮想関数呼び出しと同じくらい速いです。
- 候補の 1 つだけがとても大きいと、全部がその大きさになります。大きいものは `unique_ptr` にして入れます。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 違う型を `std::get` | `std::bad_variant_access` 例外 |
| 壊れた（valueless）状態で `std::visit` | `std::bad_variant_access` 例外 |

## よくあるミス

??? failure "文字列リテラルが bool になる"
    `std::variant<bool, std::string> v = "abc";` は古いコンパイラだと bool になることがありました（C++20 で修正）。不安なら `std::string("abc")` と書きます。

??? failure "get_if に variant そのものを渡す"
    `std::get_if<int>(v)` ではなく `std::get_if<int>(&v)`（ポインタ）です。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| 継承 + 仮想関数 | 種類をあとから自由に増やせる。ヒープを使う | 種類が多い・プラグインのように増える |
| [`std::any`](any.md) | どんな型でも入る。型安全性が低い | ほぼ使わない |
| [`std::optional`](optional.md) | 1 種類の型か「無し」 | 候補が 1 つ |
| [`std::expected`](expected.md) | 成功か失敗か | エラー処理 |

## コンパイラ対応

C++17 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 決まった型のどれか 1 つを持つ
    - [x] 処理を分けるのは `std::visit` + overloaded
    - [x] 安全に取り出すなら `std::get_if<T>(&v)`

## 関連ページ

- [cpprefjp: std::variant](https://cpprefjp.github.io/reference/variant/variant.html)
- [cppreference: std::variant](https://en.cppreference.com/w/cpp/utility/variant)
