---
title: std::set_terminate
summary: "プログラムが異常終了する直前に呼ばれる関数を設定する。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::set_terminate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <exception>`
</div>

`catch` されない例外が出ると、`std::terminate` が呼ばれて終了します。その直前に、ログを書いたり、クラッシュレポートを出したりしたいときは、`set_terminate` で自分の関数を設定します。設定した関数は、最後にプログラムを終了させる必要があります。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::set_terminate {#set_terminate}

```cpp
std::terminate_handler set_terminate(std::terminate_handler f) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 関数ポインタ | `void()` の関数 |

- 戻り値: それまでのハンドラ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <exception>
#include <print>

void Handler() {
  std::abort();
}

int main() {
  std::set_terminate(Handler);
  std::println("{}", std::get_terminate() == Handler);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | クラッシュ時にログを書き出す |

## よくあるミス

??? failure "ハンドラから戻る"
    ハンドラは戻ってはいけません。`std::abort()` などで終了させます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_terminate`](get_terminate.md) | 現在のハンドラを取る |
| [`terminate`](terminate.md) | 終了する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] プログラムが異常終了する直前に呼ばれる関数を設定する
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::set_terminate](https://cpprefjp.github.io/reference/exception/set_terminate.html)
- [cppreference: std::set_terminate](https://en.cppreference.com/w/cpp/error/set_terminate)
