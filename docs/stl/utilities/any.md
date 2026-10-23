---
title: std::any
summary: "どんな型でも入る箱。型を実行時に確かめて取り出す。使う場面は少ない。"
order: 57
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

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 宣言

```cpp
class any;
```

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [代入](#assign) | <span class="rank rank-often">よく使う</span> | 何でも入れる |
| [`has_value`](#has_value) | <span class="rank rank-sometimes">たまに</span> | 何か入っているか |
| [`type`](#type) | <span class="rank rank-sometimes">たまに</span> | 入っている型の情報 |
| [`reset`](#reset) | <span class="rank rank-rare">知ってるだけ</span> | 空にする |
| [`emplace`](#emplace) | <span class="rank rank-rare">知ってるだけ</span> | その場で作って入れる |

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

## フラグ・オプション

フラグはありません。

### swap {#swap}

```cpp
void swap(any& other) noexcept;
```

- 計算量: 定数

中身を入れ替えます。

### operator= {#op_assign}

```cpp
any& operator=(const any& rhs);
any& operator=(any&& rhs) noexcept;
template <class T> any& operator=(T&& value);
```

- 計算量: 中身による

別の `any` または値を代入します。中の型は、代入した値の型に変わります。

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
