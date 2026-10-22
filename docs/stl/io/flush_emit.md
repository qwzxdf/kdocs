---
title: std::flush_emit
summary: "osyncstream の出力を確定して、フラッシュする。"
order: 900
tags:
  - 入出力・文字列
---

# std::flush_emit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iostream>`
</div>

`osyncstream` に溜めた出力を、いまこの時点で確定（`emit`）してフラッシュします。複数のスレッドが書いても、行が混ざらずに出力されます。

!!! tip "ポイント"
    - `out << "..." << std::flush_emit;` と書く。
    - `emit()` と `flush()` を一度に行う。
    - C++20 の同期出力の部品。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::flush_emit {#flush_emit}

```cpp
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& flush_emit(std::basic_ostream<CharT, Traits>& os);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `os` | ostream& | 対象のストリーム |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iostream>
#include <syncstream>

int main() {
  std::osyncstream out(std::cout);
  out << "hi\n" << std::flush_emit;
}
```

```text title="実行結果"
hi
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "`osyncstream` 以外に使う"
    普通のストリームに使っても、フラッシュだけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`osyncstream`](osyncstream.md) | 同期出力 |
| [`emit_on_flush`](emit_on_flush.md) | フラッシュのたびに確定 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] osyncstream の出力を確定して、フラッシュする
    - [x] `out << "..." << std::flush_emit;` と書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::flush_emit](https://cpprefjp.github.io/reference/ios/flush_emit.html)
- [cppreference: std::flush_emit](https://en.cppreference.com/w/cpp/io/manip/flush_emit)
