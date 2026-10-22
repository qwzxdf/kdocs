---
title: std::const_pointer_cast
summary: "shared_ptr の指す先から const を外す（持ち主は共有）。"
order: 900
tags:
  - ユーティリティ
---

# std::const_pointer_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

`shared_ptr<const T>` から const を外したいとき、`const_cast` で生ポインタを取り出して作り直すと別の持ち主になります。`const_pointer_cast` は持ち主を共有したまま const を外します。

!!! tip "ポイント"
    - 持ち主（制御ブロック）は共有される。
    - 生ポインタで作り直すと別の持ち主になり、二重解放になる。
    - `dynamic_pointer_cast` は実行時に型を確かめる。

!!! info "このページを読む前に"
    [`std::shared_ptr`](shared_ptr.md) を先に読んでください。

## 関数の詳しい説明

### std::const_pointer_cast {#const_pointer_cast}

```cpp
template <class T, class U>
shared_ptr<T> const_pointer_cast(const shared_ptr<U>& r) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 変換後の型 |
| `r` | shared_ptr<U> | 変換元 |

- 戻り値: 変換後の `shared_ptr<T>`（持ち主は共有）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  std::shared_ptr<const int> c = std::make_shared<int>(1);
  auto m = std::const_pointer_cast<int>(c);
  *m = 5;
  std::println("{}", *c);
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| const の外し方を持ち主を保ったまま | `std::const_pointer_cast<T>(p);` |

## よくあるミス

??? failure "本当に const なオブジェクトを書き換える"
    元のオブジェクトが const で作られていると、書き換えは未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`dynamic_pointer_cast`](dynamic_pointer_cast.md) | 実行時に型を確かめる |
| [`shared_ptr`](shared_ptr.md) | 共有所有のスマートポインタ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 持ち主を共有したまま型を変える
    - [x] 生ポインタで作り直さない
    - [x] use_count が増える

## 関連ページ

- [cpprefjp: std::const_pointer_cast](https://cpprefjp.github.io/reference/memory/const_pointer_cast.html)
- [cppreference: std::const_pointer_cast](https://en.cppreference.com/w/cpp/memory/const_pointer_cast)
