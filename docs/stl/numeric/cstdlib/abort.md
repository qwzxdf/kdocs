---
title: std::abort
summary: "プログラムを異常終了する（後片付けなし）。"
order: 6
group: <cstdlib> の関数
tags:
  - 数値
---

# std::abort

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

`std::abort()` は、**プログラムを異常終了させる**関数です。後片付けをせず、すぐに終わります。`assert` が失敗したときに呼ばれます。クラッシュダンプを出すためのシグナル（`SIGABRT`）も出ます。

!!! tip "ポイント"
    - `assert` の失敗は `abort` を呼ぶ。
    - 戻らない（`[[noreturn]]`）。
    - デバッガーが付いていれば、ここで止まる。

## 関数の詳しい説明

### std::abort {#abort}

```cpp
[[noreturn]] void abort() noexcept;
```

- 戻り値: 戻らない
- 計算量: O(1)

```cpp
// 呼ぶとプログラムが異常終了するので、実行結果は書けません。
#include <cstdlib>

int main() {
  bool fatal = false;   // 致命的なエラーが起きたら
  if (fatal) {
    std::abort();
  }
}
```

```text title="実行結果"
（何も出ない。fatal が true なら異常終了する）
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 回復できないエラーでの即時停止 | `std::abort()` |

## よくあるミス

??? failure "後片付けを期待する"
    何も呼ばれません。ログは先に flush します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exit`](exit.md) | 後片付けをして終了 |
| `assert` | デバッグ用の確認 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 異常終了
    - [x] 後片付けなし
    - [x] assert が内部で使う

## 関連ページ

- [cpprefjp: std::abort](https://cpprefjp.github.io/reference/cstdlib/abort.html)
- [cppreference: std::abort](https://en.cppreference.com/w/cpp/utility/program/abort)
