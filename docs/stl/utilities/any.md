---
title: std::any
tags:
  - ユーティリティ
---

# std::any

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-17">C++17</span>
`#include <any>`
</div>

`std::any` は、**どんな型の値でも 1 つ入れておける箱**です。入れるときに型を決める必要がなく、取り出すときに「この型のはず」と指定して `std::any_cast` で取り出します。型が合わなければ失敗します。何でも入る代わりに、間違いがコンパイル時に見つからず、大きな値はヒープに置かれます。

!!! tip "ポイント"
    - <strong>ほとんど使わない。</strong> 入る型の候補が決まっているなら [`std::variant`](variant.md) のほうが安全で速い。
    - 使うとしたら「エディタのプロパティ」「汎用のイベント引数」など、型をあとから決めたい仕組みくらい。
    - 取り出すときは `std::any_cast<T>(&a)`（ポインタ版）で、失敗したら nullptr をチェックする。

## 宣言

```cpp
class any;
```

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [代入](#assign) | <span class="rank rank-often">よく使う</span> | 何でも入れる |
| [`std::any_cast`](#any_cast) | <span class="rank rank-often">よく使う</span> | 型を指定して取り出す |
| [`has_value`](#has_value) | <span class="rank rank-sometimes">たまに</span> | 何か入っているか |
| [`type`](#type) | <span class="rank rank-sometimes">たまに</span> | 入っている型の情報 |
| [`reset`](#reset) | <span class="rank rank-rare">知ってるだけ</span> | 空にする |
| [`emplace`](#emplace) | <span class="rank rank-rare">知ってるだけ</span> | その場で作って入れる |
| [`std::make_any`](#make_any) | <span class="rank rank-rare">知ってるだけ</span> | 作って any にする |

## よくある使い方

```cpp
#include <any>
#include <print>
#include <string>
#include <unordered_map>

int main() {
  // 名前 → 何かの値（エディタのプロパティのようなもの）
  std::unordered_map<std::string, std::any> props;
  props["speed"] = 3.5f;
  props["name"] = std::string("Hero");

  if (auto* speed = std::any_cast<float>(&props["speed"])) {
    std::println("speed {}", *speed);
  }
  if (std::any_cast<int>(&props["name"]) == nullptr) {
    std::println("name は int ではない");
  }
}
```

```text title="実行結果"
speed 3.5
name は int ではない
```

## 関数の詳しい説明

### 代入 {#assign}

```cpp
template <class T>
any& operator=(T&& value);
```

- どんな型（コピーできるもの）でも入れられます。前の値は消えます

### std::any_cast {#any_cast}

```cpp
template <class T>
T any_cast(const any& operand);          // 失敗すると例外
template <class T>
const T* any_cast(const any* operand) noexcept;  // 失敗すると nullptr
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `operand` | `any` / `any*` | 取り出す元。ポインタを渡すとポインタ版になる |

- 型が**ぴったり**合わないと失敗します（`int` を入れて `long` で取り出すのも失敗）
- 参照版は失敗すると `std::bad_any_cast` 例外

```cpp
#include <any>
#include <print>

int main() {
  std::any a = 10;
  std::println("{}", std::any_cast<int>(a));
  try {
    std::any_cast<long>(a);
  } catch (const std::bad_any_cast&) {
    std::println("long では取り出せない");
  }
}
```

```text title="実行結果"
10
long では取り出せない
```

### has_value {#has_value}

```cpp
bool has_value() const noexcept;
```

- 何か入っていれば `true`

### type {#type}

```cpp
const std::type_info& type() const noexcept;
```

- 入っている型の情報（`typeid` と比べられる）。空なら `typeid(void)`

```cpp
#include <any>
#include <print>
#include <typeinfo>

int main() {
  std::any a;
  std::println("{}", a.has_value());
  a = 1.5;
  std::println("{} {}", a.has_value(), a.type() == typeid(double));
}
```

```text title="実行結果"
false
true true
```

### reset {#reset}

```cpp
void reset() noexcept;
```

- 空にします

<div class="anim" data-label="a.reset()">
5 # 何かを持っている
x5 # 破棄する
_ # 空
</div>

### emplace {#emplace}

```cpp
template <class T, class... Args>
std::decay_t<T>& emplace(Args&&... args);
```

- `T` をその場で作って入れます

<div class="anim" data-label="a.emplace<float>(2.5)">
5 # int を持っている
x5 # 今の値を破棄する
+2.5 # float をその場で作る
</div>

### std::make_any {#make_any}

```cpp
template <class T, class... Args>
std::any make_any(Args&&... args);
```

- `T` を作って入れた any を返します

```cpp
#include <any>
#include <print>
#include <string>

int main() {
  std::any a = std::make_any<std::string>(3, 'a');
  a.emplace<int>(7);
  std::println("{}", std::any_cast<int>(a));
  a.reset();
  std::println("{}", a.has_value());
}
```

```text title="実行結果"
7
false
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| エディタのプロパティ | インスペクタに表示する値（型がいろいろ） |
| 汎用のメッセージ引数 | 種類の決まっていないイベントのデータ |

どちらも、型の候補が決まっているなら `std::variant` で書けます。

## パフォーマンス

- 小さい値（ポインタ数個ぶんまで）は中に直接入りますが、大きい値は**ヒープに確保**されます。
- 取り出すたびに型のチェックがあります。

## よくあるミス

??? failure "型が少し違って取り出せない"
    `a = "abc";` で入るのは `const char*` です。`std::any_cast<std::string>(a)` は失敗します。

??? failure "variant で済むのに any を使う"
    any は「何が入っているか分からない」ので、取り出す側で全部の型を試す必要が出てきます。候補が決まっているなら variant + visit のほうが安全です。

## 類似クラス

| 名前 | 違い |
| --- | --- |
| [`std::variant`](variant.md) | 入る型の候補が決まっている。安全で速い |
| `void*` | 型の情報すら無い。使わない |

## コンパイラ対応

C++17 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 何でも入る箱。ほぼ使わない
    - [x] 候補が決まっているなら variant

## 関連ページ

- [cpprefjp: std::any](https://cpprefjp.github.io/reference/any/any.html)
- [cppreference: std::any](https://en.cppreference.com/w/cpp/utility/any)
