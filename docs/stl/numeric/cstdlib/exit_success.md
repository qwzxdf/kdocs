---
title: EXIT_SUCCESS
summary: "成功を表す終了コードのマクロ。"
order: 900
tags:
  - 数値
---

# EXIT_SUCCESS

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`main` の戻り値や `exit` の引数に、成功と失敗を表す名前付きの定数を使うと、読みやすくなります。`EXIT_SUCCESS` は成功（通常 0）です。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### EXIT_SUCCESS {#exit_success}

```cpp
#define EXIT_SUCCESS 0  // 値は実装定義
```

- 戻り値: 成功を表す整数
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", EXIT_SUCCESS);
}
```

```text title="実行結果"
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | main の戻り値 |

## よくあるミス

??? failure "0 と書く"
    意味は同じですが、名前のほうが意図が伝わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`EXIT_FAILURE`](exit_failure.md) | 失敗を表す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 成功を表す終了コードのマクロ
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: EXIT_SUCCESS](https://cpprefjp.github.io/reference/cstdlib/EXIT_SUCCESS.html)
- [cppreference: EXIT_SUCCESS](https://en.cppreference.com/w/cpp/c/EXIT_SUCCESS)
