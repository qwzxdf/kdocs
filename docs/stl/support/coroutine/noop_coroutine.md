---
title: std::noop_coroutine
summary: "何もしないコルーチンのハンドルを返す。"
order: 900
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# std::noop_coroutine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

コルーチンが終わるとき、次に実行するコルーチンを返す「対称転送」で、「次はなし」を表したいことがあります。`noop_coroutine()` は、`resume()` しても何も起きないコルーチンのハンドルを返します。

!!! tip "ポイント"
    - `resume()` しても何も起こらない。
    - `await_suspend` の戻り値として「何もしない」を表すときに使う。
    - `done()` は常に `false`。

!!! info "このページを読む前に"
    [`coroutine_handle`](coroutine_handle.md) を先に読んでください。

## 関数の詳しい説明

### std::noop_coroutine {#noop_coroutine}

```cpp
noop_coroutine_handle noop_coroutine() noexcept;
```

- 戻り値: 何もしないコルーチンのハンドル
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <coroutine>
#include <print>

int main() {
  std::coroutine_handle<> h = std::noop_coroutine();
  h.resume();
  std::println("{}", h.done());
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `await_suspend` で次の実行先がないとき | `return std::noop_coroutine();` |

## よくあるミス

??? failure "`destroy()` を呼ぶ"
    ハンドルは共有された 1 つの実体です。`destroy()` を呼んでも意味はありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`coroutine_handle`](coroutine_handle.md) | コルーチンの操作 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 何もしないコルーチン
    - [x] resume しても何も起こらない
    - [x] 対称転送の「次なし」に使う

## 関連ページ

- [cpprefjp: std::noop_coroutine](https://cpprefjp.github.io/reference/coroutine/noop_coroutine.html)
- [cppreference: std::noop_coroutine](https://en.cppreference.com/w/cpp/coroutine/noop_coroutine)
