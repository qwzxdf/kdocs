---
title: std::atexit
summary: "プログラム終了時に呼ぶ関数を登録する。"
order: 900
tags:
  - 数値
---

# std::atexit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

後始末（ログのクローズなど）を、どこから終了しても確実に行いたいときに、`atexit` で関数を登録します。登録した順の**逆**に呼ばれます。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::atexit {#atexit}

```cpp
int atexit(void (*func)());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `func` | 関数ポインタ | 終了時に呼ぶ関数 |

- 戻り値: 成功なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::atexit([] { std::println("bye"); });
  std::println("main");
}
```

```text title="実行結果"
main
bye
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 終了時の後始末 |

## よくあるミス

??? failure "後始末を静的デストラクタとの順序に頼る"
    静的オブジェクトの破棄との順序は、登録の前後で決まります。重要な後始末は明示的に呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exit`](exit.md) | 終了する |
| [`quick_exit`](quick_exit.md) | 後始末を最小限に |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] プログラム終了時に呼ぶ関数を登録する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atexit](https://cpprefjp.github.io/reference/cstdlib/atexit.html)
- [cppreference: std::atexit](https://en.cppreference.com/w/cpp/c/atexit)
