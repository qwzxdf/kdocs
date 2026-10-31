---
title: std::make_any
summary: "値を作りながら any に入れる。"
order: 61
tags:
  - ユーティリティ
---

# std::make_any

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <any>`
</div>

`std::any` に値を入れて作るとき、`std::any(std::string("Hero"))` だと、一時的な `std::string` を作ってから `any` に入れる、という手順になります。`std::make_any<T>(引数...)` は、`T` を引数から直接作って、`any` に入れる関数です。コピーやムーブの手間が減ります。

!!! tip "ポイント"
    - `std::make_any<T>(args...)` は、`T` を引数から直接 `any` の中で作る
    - 型 `T` は明示する。推論はされない
    - `std::any a = 5;` のように、そのまま代入する書き方もある
    - 中身を取り出すのは `std::any_cast<T>`

!!! info "このページを読む前に"
    [`std::any`](any.md) を先に読んでください。

## 関数の詳しい説明

### std::make_any {#make_any}

<span class="ver ver-17">C++17</span>

```cpp
template <class T, class... Args>
std::any make_any(Args&&... args);

template <class T, class U, class... Args>
std::any make_any(std::initializer_list<U> il, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | `any` に入れる型 |
| `args` | コンストラクターの引数 | `T` を作るための引数 |

`T` をコピー可能な型にする必要があります。コピーできない型（`std::unique_ptr` など）は、`any` に入れられません。

`std::any(std::in_place_type<T>, args...)` と同じ意味です。`make_any` のほうが、短く書けます。

## 実際に動かしてみる

```cpp
#include <any>
#include <print>
#include <string>

int main() {
  // T を引数から直接作る
  std::any a = std::make_any<std::string>(3, 'x');  // string(3, 'x')
  std::println("{}", std::any_cast<std::string>(a));

  std::any b = std::make_any<int>(42);
  std::println("{}", std::any_cast<int>(b));

  // initializer_list からも作れる
  std::any c = std::make_any<std::string>({'a', 'b', 'c'});
  std::println("{}", std::any_cast<std::string>(c));
}
```

```text title="実行結果"
xxx
42
abc
```

## ゲームでの使いどころ

設定値の集まりを `std::map<std::string, std::any>` で持つときに、値の型を明示して入れます。型が決まっている場面では、`variant` のほうが安全です。

## よくあるミス

??? failure "T を省略して推論させようとする"
    `make_any(5)` はコンパイルできません。`make_any<int>(5)` と書きます。

??? failure "コピーできない型を入れる"
    `std::unique_ptr` などは入れられません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::any_cast`](any_cast.md) | 中身を取り出す |
| [`std::any`](any.md) | 本体 |
| [`std::variant`](variant.md) | 型を限定した、安全な代わり |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::make_any](https://cpprefjp.github.io/reference/any/make_any.html)
- [cppreference: std::make_any](https://en.cppreference.com/w/cpp/utility/any/make_any)
