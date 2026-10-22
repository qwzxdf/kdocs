---
title: jmp_buf
summary: "setjmp が保存した、実行位置の情報を入れる型。"
order: 900
tags:
  - 入出力・文字列
---

# jmp_buf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <csetjmp>`
</div>

`setjmp` は、「ここに戻ってくる」という実行位置を保存します。その保存先が `jmp_buf` 型です。`longjmp(env, 値)` を呼ぶと、保存した位置まで一気にジャンプして戻れます。C++ では、デストラクタが呼ばれないため危険で、例外を使うのが一般的です。

!!! tip "ポイント"
    - `setjmp(env)` が保存し、`longjmp(env, 値)` で戻る。
    - デストラクタは呼ばれない（C++ では危険）。
    - 新しいコードでは例外を使う。

!!! info "このページを読む前に"
    [`<csetjmp>`](csetjmp.md) の概要を先に読んでください。

## 関数の詳しい説明

### jmp_buf {#jmp_buf}

```cpp
using jmp_buf = /* 配列型 */;
```

- 戻り値: なし（型）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <csetjmp>
#include <print>

int main() {
  std::jmp_buf env;
  if (setjmp(env) == 0) {
    std::longjmp(env, 1);
  } else {
    std::println("jumped");
  }
}
```

```text title="実行結果"
jumped
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （古い C のコードの保守） |

## よくあるミス

??? failure "デストラクタが飛ばされる"
    `longjmp` で飛ぶと、途中のオブジェクトのデストラクタが呼ばれません。リソースがリークします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setjmp` / `longjmp`](csetjmp.md) | ジャンプ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] setjmp が保存した、実行位置の情報を入れる型
    - [x] `setjmp(env)` が保存し、`longjmp(env, 値)` で戻る
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: jmp_buf](https://cpprefjp.github.io/reference/csetjmp/jmp_buf.html)
- [cppreference: jmp_buf](https://en.cppreference.com/w/cpp/utility/program/jmp_buf)
