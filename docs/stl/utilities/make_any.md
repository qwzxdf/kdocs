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

`std::make_any<T>(引数...)` は、**型 `T` のオブジェクトをその場で作って `std::any` に入れる**関数です。一時的なオブジェクトを作らずに済むので、コピーやムーブを減らせます。

!!! tip "ポイント"
    - `std::make_any<Vec3>(1.0f, 2.0f, 3.0f)` のように、コンストラクタの引数を渡す。
    - 入れた型は `T`。取り出すときは同じ `T` を指定する。
    - `a.emplace<T>(...)` でも同じことができる。

!!! info "このページを読む前に"
    [`std::any`](any.md) を先に読んでください。

## 関数の詳しい説明

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

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定値の表に、構造体を直接入れる | `std::make_any<Color>(255, 0, 0)` |

## よくあるミス

??? failure "型を省略しようとする"
    `make_any` はテンプレート引数 `T` が必須です。推論されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::any`](any.md) | 本体 |
| [`std::any_cast`](any_cast.md) | 取り出す |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 作りながら `any` に入れる
    - [x] 型 `T` を明示する
    - [x] `emplace` でも同じ

## 関連ページ

- [cpprefjp: std::make_any](https://cpprefjp.github.io/reference/any/make_any.html)
- [cppreference: std::make_any](https://en.cppreference.com/w/cpp/utility/any/make_any)
