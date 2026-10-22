---
title: std::variant
summary: "「複数の型のうちどれか 1 つ」を持つ。状態や種類ごとのデータを型安全に持てる。"
order: 54
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
| [`std::get`](#get) | <span class="rank rank-sometimes">たまに</span> | その型として取り出す（違えば例外） |
| [`index`](#index) | <span class="rank rank-sometimes">たまに</span> | 今何番目の型が入っているか |
| [`emplace`](#emplace) | <span class="rank rank-sometimes">たまに</span> | その場で値を作る |
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

### valueless_by_exception {#valueless}

```cpp
constexpr bool valueless_by_exception() const noexcept;
```

- 型を切り替える途中で例外が起きて、どの値も入っていない壊れた状態なら `true`。普通は起きません

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

### swap {#swap}

```cpp
void swap(variant& other);
```

- 計算量: 中身による

中身を入れ替えます。型が違えば、それぞれが相手の型に変わります。

### operator= {#op_assign}

```cpp
variant& operator=(const variant& rhs);
variant& operator=(variant&& rhs);
template <class T> variant& operator=(T&& t);
```

- 計算量: 中身による

別の `variant` または値を代入します。値を代入するときは、`T` に最も合う選択肢が選ばれます。

### operator== {#op_eq}

```cpp
template <class... Types>
bool operator==(const variant<Types...>& a, const variant<Types...>& b);
```

- 計算量: 中身による

同じ選択肢で、値が等しければ `true`。選択肢が違えば `false`。

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
