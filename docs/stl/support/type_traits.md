---
title: <type_traits>（型の性質を調べる）
tags:
  - 型・言語サポート
---

# &lt;type_traits&gt;（型の性質を調べる）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`<type_traits>` は、**コンパイル時に型の性質を調べたり、型を変換したりする道具**をまとめたヘッダです。「この型は整数か」「ポインタか」「コピーできるか」を `std::is_integral_v<T>` のように調べられます。主に[テンプレート](../../basics/template.md)の中で、型によって処理を変えたり（`if constexpr`）、間違った型を弾いたり（`static_assert`）するのに使います。

!!! tip "結論"
    - 調べるのは `std::is_xxx_v<T>`（`bool` の定数）、変換するのは `std::xxx_t<T>`（型）。
    - `if constexpr (std::is_integral_v<T>)` で型ごとに処理を分ける。
    - 構造体をそのまま `memcpy` / ファイルに書いていいかは `std::is_trivially_copyable_v<T>` で確かめる。
    - C++20 以降は、テンプレートの型の条件は [concepts](../../basics/template.md#concepts型に条件を付ける)（`std::integral` など）のほうが読みやすい。

## 調べる（is_ 系）

よく使う順です。

| 名前 | 重要度 | `true` になる型 |
| --- | --- | --- |
| [`std::is_same_v<T, U>`](#is_same) | <span class="rank rank-often">よく使う</span> | T と U が同じ型 |
| [`std::is_integral_v<T>`](#is_integral) | <span class="rank rank-sometimes">たまに</span> | 整数型（bool、char も含む） |
| [`std::is_floating_point_v<T>`](#is_floating_point) | <span class="rank rank-sometimes">たまに</span> | float、double |
| [`std::is_trivially_copyable_v<T>`](#is_trivially_copyable) | <span class="rank rank-sometimes">たまに</span> | memcpy でコピーしてよい型 |
| [`std::is_enum_v<T>`](#is_enum) | <span class="rank rank-sometimes">たまに</span> | enum |
| [`std::is_pointer_v<T>`](#is_pointer) | <span class="rank rank-rare">知ってるだけ</span> | ポインタ |
| [`std::is_base_of_v<Base, D>`](#is_base_of) | <span class="rank rank-rare">知ってるだけ</span> | D が Base を継承している |
| [`std::is_arithmetic_v<T>`](#is_arithmetic) | <span class="rank rank-rare">知ってるだけ</span> | 整数か浮動小数点 |
| [`std::is_const_v<T>`](#is_const) | <span class="rank rank-rare">知ってるだけ</span> | const が付いている |
| [`std::is_default_constructible_v<T>`](#is_default_constructible) | <span class="rank rank-rare">知ってるだけ</span> | 引数なしで作れる |
| [`std::is_copy_constructible_v<T>`](#is_copy_constructible) | <span class="rank rank-rare">知ってるだけ</span> | コピーできる |
| [`std::is_nothrow_move_constructible_v<T>`](#is_nothrow_move_constructible) | <span class="rank rank-rare">知ってるだけ</span> | 例外を投げずにムーブできる |
| [`std::is_aggregate_v<T>`](#is_aggregate) | <span class="rank rank-rare">知ってるだけ</span> | `{}` でメンバを並べて作れる構造体 |

## 変換する（_t 系）

| 名前 | 重要度 | 結果 |
| --- | --- | --- |
| [`std::remove_cvref_t<T>`](#remove_cvref) | <span class="rank rank-sometimes">たまに</span> | const と参照を取り除いた型 <span class="ver ver-20">C++20</span> |
| [`std::underlying_type_t<E>`](#underlying_type) | <span class="rank rank-sometimes">たまに</span> | enum の中身の整数型 |
| [`std::decay_t<T>`](#decay) | <span class="rank rank-rare">知ってるだけ</span> | 値で受け取ったときの型（配列はポインタに） |
| [`std::conditional_t<B, T, F>`](#conditional) | <span class="rank rank-rare">知ってるだけ</span> | B が true なら T、false なら F |
| [`std::common_type_t<T, U>`](#common_type) | <span class="rank rank-rare">知ってるだけ</span> | T と U の両方を表せる型 |
| [`std::make_unsigned_t<T>`](#make_unsigned) | <span class="rank rank-rare">知ってるだけ</span> | 符号なし版の整数型 |
| [`std::invoke_result_t<F, Args...>`](#invoke_result) | <span class="rank rank-rare">知ってるだけ</span> | F を Args で呼んだ戻り値の型 |

## よくある使い方

```cpp
#include <cstring>
#include <print>
#include <string>
#include <type_traits>

// memcpy でそのまま書き出してよい型だけ受け付ける
template <class T>
void WriteRaw(const T& value) {
  static_assert(std::is_trivially_copyable_v<T>, "string や vector を含む型は書けない");
  char buffer[sizeof(T)];
  std::memcpy(buffer, &value, sizeof(T));
  std::println("{} バイト書いた", sizeof(T));
}

struct Header {
  int version;
  float time;
};

int main() {
  WriteRaw(Header{1, 2.5f});
  // WriteRaw(std::string("x"));  // コンパイルエラー（static_assert）
  std::println("{} {}", std::is_trivially_copyable_v<Header>,
               std::is_trivially_copyable_v<std::string>);
}
```

```text title="実行結果"
8 バイト書いた
true false
```

## 詳しい説明

### std::is_same_v {#is_same}

```cpp
template <class T, class U>
inline constexpr bool is_same_v = /* T と U が同じなら true */;
```

- 2 つの型が完全に同じか（`int` と `const int` は違う）

### std::is_integral_v {#is_integral}

```cpp
template <class T>
inline constexpr bool is_integral_v;
```

- 整数型（bool、char、short、int、long、long long、符号なし版）なら true

### std::is_floating_point_v {#is_floating_point}

```cpp
template <class T>
inline constexpr bool is_floating_point_v;
```

- float、double、long double なら true

```cpp
#include <print>
#include <string>
#include <type_traits>

template <class T>
std::string Describe(T value) {
  if constexpr (std::is_integral_v<T>) {
    return "整数 " + std::to_string(value);
  } else if constexpr (std::is_floating_point_v<T>) {
    return "小数 " + std::to_string(value);
  } else {
    return "その他";
  }
}

int main() {
  std::println("{} / {} / {}", Describe(3), Describe(1.5f), Describe("x"));
  std::println("{} {}", std::is_same_v<int, int>, std::is_same_v<int, const int>);
}
```

```text title="実行結果"
整数 3 / 小数 1.500000 / その他
true false
```

### std::is_trivially_copyable_v {#is_trivially_copyable}

```cpp
template <class T>
inline constexpr bool is_trivially_copyable_v;
```

- `memcpy` でビットをそのままコピーしてよい型。int、float、それらだけの構造体は true。string、vector、仮想関数を持つクラスは false

### std::is_enum_v {#is_enum}

```cpp
template <class T>
inline constexpr bool is_enum_v;
```

- enum（enum class 含む）なら true

### std::is_pointer_v {#is_pointer}

- ポインタ型なら true（スマートポインタは false）

### std::is_base_of_v {#is_base_of}

```cpp
template <class Base, class Derived>
inline constexpr bool is_base_of_v;
```

- Derived が Base を継承していれば true。「Component を継承した型だけ AddComponent できる」のチェックに使えます

```cpp
#include <print>
#include <type_traits>

struct Component {};
struct Transform : Component {};
struct NotComponent {};

template <class T>
void AddComponent() {
  static_assert(std::is_base_of_v<Component, T>, "Component を継承していない");
  std::println("追加した");
}

int main() {
  AddComponent<Transform>();
  // AddComponent<NotComponent>();  // コンパイルエラー
  std::println("{} {}", std::is_pointer_v<int*>, std::is_enum_v<int>);
}
```

```text title="実行結果"
追加した
true false
```

### std::is_arithmetic_v {#is_arithmetic}

- 整数か浮動小数点なら true（数値として計算できる型）

### std::is_const_v {#is_const}

- `const` が付いていれば true（`const int&` は参照なので false。`std::remove_reference_t` してから調べる）

### std::is_default_constructible_v {#is_default_constructible}

- `T()` で作れるか

### std::is_copy_constructible_v {#is_copy_constructible}

- コピーできるか。`std::unique_ptr` は false

### std::is_nothrow_move_constructible_v {#is_nothrow_move_constructible}

- ムーブコンストラクタが `noexcept` か。false だと vector の再確保でコピーされてしまうので、自作のクラスの確認に使えます（[ムーブ](../../basics/move.md#noexcept-を付ける理由)）

### std::is_aggregate_v {#is_aggregate}

- `{1, 2}` のようにメンバを並べて作れる構造体（集成体）か

```cpp
#include <memory>
#include <print>
#include <string>
#include <type_traits>

struct Point {
  int x;
  int y;
};

int main() {
  std::println("{} {} {} {} {}", std::is_arithmetic_v<float>, std::is_const_v<const int>,
               std::is_copy_constructible_v<std::unique_ptr<int>>,
               std::is_nothrow_move_constructible_v<std::string>, std::is_aggregate_v<Point>);
  std::println("{}", std::is_default_constructible_v<Point>);
}
```

```text title="実行結果"
true true false true true
true
```

### std::remove_cvref_t {#remove_cvref}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
using remove_cvref_t = /* const・volatile・参照を取り除いた T */;
```

- `const std::string&` → `std::string`。テンプレートで受け取った型を「素の型」にして比べるのに使います

### std::underlying_type_t {#underlying_type}

```cpp
template <class E>
using underlying_type_t = /* enum E の中身の整数型 */;
```

- enum class を整数に変換するときの型。C++23 なら [`std::to_underlying`](utility-misc.md#to_underlying) が簡単です

### std::decay_t {#decay}

- 値渡しで受け取ったときと同じ変換（参照・const を外し、配列・関数をポインタに）をした型

### std::conditional_t {#conditional}

```cpp
template <bool B, class T, class F>
using conditional_t = /* B ? T : F */;
```

- コンパイル時の条件で型を選びます

### std::common_type_t {#common_type}

- 両方の型を表せる型（`int` と `double` なら `double`）

### std::make_unsigned_t {#make_unsigned}

- `int` → `unsigned int` のように符号なし版にします

### std::invoke_result_t {#invoke_result}

```cpp
template <class F, class... Args>
using invoke_result_t = /* F(Args...) の戻り値の型 */;
```

- 関数を呼んだときの戻り値の型

```cpp
#include <cstdint>
#include <print>
#include <string>
#include <type_traits>

enum class Layer : std::uint8_t { kGround, kAir };

int main() {
  std::println("{}", std::is_same_v<std::remove_cvref_t<const std::string&>, std::string>);
  std::println("{}", std::is_same_v<std::underlying_type_t<Layer>, std::uint8_t>);
  std::println("{}", std::is_same_v<std::common_type_t<int, double>, double>);
  std::println("{}", std::is_same_v<std::conditional_t<(sizeof(void*) == 8), long long, int>,
                                    long long>);
  std::println("{}", std::is_same_v<std::make_unsigned_t<int>, unsigned int>);
  auto twice = [](int x) { return x * 2.0; };
  std::println("{}", std::is_same_v<std::invoke_result_t<decltype(twice), int>, double>);
  std::println("{}", std::is_same_v<std::decay_t<const int[3]>, const int*>);
}
```

```text title="実行結果（64 ビット環境）"
true
true
true
true
true
true
true
```

## フラグ・オプション

フラグはありません。`std::is_xxx<T>::value` と書く古い書き方は、`std::is_xxx_v<T>` と同じです。

## ゲームでの使いどころ

| 場面 | 道具 |
| --- | --- |
| バイナリで保存してよい型か確かめる | `is_trivially_copyable_v` + `static_assert` |
| 型ごとに処理を変える汎用の関数（シリアライズ、デバッグ表示） | `is_integral_v` などで `if constexpr` |
| AddComponent<T> の T を確かめる | `is_base_of_v` |
| enum を整数に | `underlying_type_t` |

## よくあるミス

??? failure "参照付きの型で調べて false になる"
    テンプレートの `T&&` で受け取ると、T が `int&` になることがあり、`is_integral_v<T>` が false になります。`std::remove_cvref_t<T>` してから調べます。

## 理解度チェック

!!! question "Q1. `std::is_trivially_copyable_v<std::vector<int>>` は？ なぜ？"
    <div class="spoiler" markdown>

    **答え:** false。vector はヒープへのポインタを持っていて、ビットをそのままコピーすると 2 つの vector が同じ領域を指し、二重解放になるためです。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 調べるのは `is_xxx_v<T>`、変換は `xxx_t<T>`
    - [x] `if constexpr` と `static_assert` と組み合わせる
    - [x] バイナリ保存の前に is_trivially_copyable_v

## 関連ページ

- [テンプレート](../../basics/template.md)
- [cppreference: Type support](https://en.cppreference.com/w/cpp/types)
