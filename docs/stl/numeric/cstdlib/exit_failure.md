---
title: EXIT_FAILURE
summary: "失敗を表す終了コードのマクロ。"
order: 900
tags:
  - 数値
---

# EXIT_FAILURE

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`EXIT_FAILURE` は失敗を表す終了コードです（通常 1）。`main` の戻り値や `exit` の引数に使います。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### EXIT_FAILURE {#exit_failure}

```cpp
#define EXIT_FAILURE 1  // 値は実装定義
```

- 戻り値: 失敗を表す整数
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", EXIT_FAILURE);
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | エラーで終了するとき |

## よくあるミス

??? failure "-1 を返す"
    環境によって扱いが違います。`EXIT_FAILURE` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`EXIT_SUCCESS`](exit_success.md) | 成功を表す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 失敗を表す終了コードのマクロ
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: EXIT_FAILURE](https://cpprefjp.github.io/reference/cstdlib/EXIT_FAILURE.html)
- [cppreference: EXIT_FAILURE](https://en.cppreference.com/w/cpp/c/EXIT_FAILURE)
