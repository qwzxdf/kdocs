---
title: std::terminate
summary: "処理されなかった例外などで呼ばれる、プログラムの強制終了。"
order: 17
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::terminate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <exception>`
</div>

`std::terminate` は、**どこでも `catch` されなかった例外などの致命的な状況で呼ばれる、プログラムの強制終了**です。既定では `std::abort` を呼びます。`std::set_terminate` で、終了する前に呼ばれる関数を登録すれば、ログやクラッシュダンプを残せます。

!!! tip "ポイント"
    - `noexcept` の関数から例外が出ると呼ばれる。
    - `std::thread` を `join` せずに破棄しても呼ばれる。
    - 登録した関数は、必ずプログラムを終了させる（戻ってはいけない）。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::terminate {#terminate}

```cpp
[[noreturn]] void terminate() noexcept;
terminate_handler set_terminate(terminate_handler f) noexcept;
```

- 戻り値: （例外クラス）。`what()` でメッセージ
- 計算量: O(1)

```cpp
#include <cstdlib>
#include <exception>
#include <print>

int main() {
  std::set_terminate([] {
    std::println("terminate!");
    std::exit(1);
  });
  throw 1;  // どこでも捕まえられない例外 → terminate が呼ばれる
}
```

```text title="実行結果"
terminate!
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| クラッシュ直前にログとダンプを残す | `std::set_terminate([] { WriteCrashDump(); std::abort(); })` |

## よくあるミス

??? failure "ハンドラーから戻る"
    戻ると未定義動作です。必ず終了させます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception_ptr`](exception_ptr.md) | 例外を運ぶ |
| [`std::jthread`](../../concurrency/jthread.md) | 破棄時に自動で join する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 致命的な状況で呼ばれる終了
    - [x] set_terminate でログを残す
    - [x] ハンドラーは戻らない

## 関連ページ

- [cpprefjp: std::terminate](https://cpprefjp.github.io/reference/exception/terminate.html)
- [cppreference: std::terminate](https://en.cppreference.com/w/cpp/error/terminate)
