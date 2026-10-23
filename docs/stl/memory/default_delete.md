---
title: std::default_delete
summary: "unique_ptr が既定で使う、`delete` を呼ぶだけの削除関数。"
order: 24
tags:
  - メモリ
---

# std::default_delete

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::default_delete<T>` は、**`std::unique_ptr` が何も指定しなかったときに使う、`delete` を呼ぶだけの削除用の関数オブジェクト**です。`unique_ptr<T>` は、実は `unique_ptr<T, default_delete<T>>` です。C のライブラリの解放関数を呼ばせたいときは、これを自作の削除関数に置き換えます。

!!! tip "ポイント"
    - `std::unique_ptr<T>` の第 2 テンプレート引数の既定値。
    - 配列版 `default_delete<T[]>` は `delete[]` を呼ぶ。
    - 自作の削除関数に置き換えて、`fclose` などを呼べる。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [所有権（誰が消すのか）](../../basics/ownership.md)（所有権の考え方）

## 関数の詳しい説明

### std::default_delete {#default_delete}

```cpp
template <class T>
struct default_delete {
  void operator()(T* p) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `T*` | 解放するポインター |

- 戻り値: （なし）。`delete p` を呼ぶ
- 計算量: O(1)

```cpp
#include <memory>
#include <print>

int main() {
  int* raw = new int(3);
  std::default_delete<int> deleter;
  std::println("{}", *raw);
  deleter(raw);  // delete raw と同じ
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のライブラリの解放関数を、unique_ptr に任せる | `std::unique_ptr<FILE, decltype(&fclose)>` |

## よくあるミス

??? failure "new[] で作ったものに default_delete<T> を使う"
    `T[]` 版を使います（`unique_ptr<T[]>` なら自動）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::unique_ptr`](../utilities/unique_ptr.md) | 既定で使っている |
| [`make_unique`](../utilities/make_unique.md) | 作る側 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `delete` を呼ぶ削除関数
    - [x] unique_ptr の既定の第 2 引数
    - [x] 自作の削除関数に置き換えられる

## 関連ページ

- [cpprefjp: std::default_delete](https://cpprefjp.github.io/reference/memory/default_delete.html)
- [cppreference: std::default_delete](https://en.cppreference.com/w/cpp/memory/default_delete)
