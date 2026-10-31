---
title: std::syncbuf
summary: "書き込みを溜めておき、emit でまとめて出力先に書くストリームバッファ。"
order: 900
tags:
  - 入出力・文字列
---

# std::syncbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <syncstream>`
</div>

ワーカー スレッドが 4 本あって、それぞれが `std::cout << "敵 " << id << " を倒した\n";` とログを出すと、行が途中で混ざります。`<<` を 1 回ずつ実行する間に、他のスレッドの出力が割り込めるからです。データ競合にはなりませんが、読めないログになります。

`syncbuf` は、書き込みをいったん自分のバッファに溜めておき、`emit()` を呼んだ瞬間に、出力先へまとめて書きます。まとめて書く間は、他のスレッドの出力が割り込みません。`std::osyncstream` の内部にある部品で、普段は `osyncstream` を使います。

!!! tip "ポイント"
    - `emit()` を呼ぶまで、書き込みは出力先に出ない。デストラクターでも `emit()` される
    - 同じ出力先に書く `syncbuf` の `emit()` どうしは、順番に実行される。出力が混ざらない
    - 出力先は、渡した `streambuf*`。`cout` なら `cout.rdbuf()`
    - 普段は `osyncstream` を使う

!!! info "このページを読む前に"
    [`std::osyncstream`](osyncstream.md) を先に読んでください。使い方はそちらが基本です。

## 関数の詳しい説明

### std::syncbuf {#syncbuf}

<span class="ver ver-20">C++20</span>

```cpp
template <class CharT, class Traits = std::char_traits<CharT>,
          class Allocator = std::allocator<CharT>>
class basic_syncbuf;
using syncbuf = basic_syncbuf<char>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obuf` | `std::streambuf*` | 最終的な出力先のバッファ。`cout.rdbuf()` など |
| `alloc` | `Allocator` | 溜めるためのメモリの確保に使う。省略できる |

内部に溜める文字列は、アロケーターで確保されます。溜めた量が多いと、そのぶんメモリを使います。

### emit {#emit}

```cpp
bool emit();
```

溜めた内容を、出力先にまとめて書き込みます。成功すれば `true`、失敗すれば `false` を返します。

同じ出力先に対する `emit` は、内部のロックで順番に処理されます。ある `syncbuf` が `emit` で書き込んでいる間、別の `syncbuf` の `emit` は、終わるまで待たされます。それぞれの `emit` の内容は、他の出力と混ざることなく、1 まとまりで出力先に届きます。

デストラクターは、まだ `emit` されていない内容があれば、`emit` を呼びます。`emit` を書き忘れても出力は消えませんが、出るタイミングは、`syncbuf` が破棄される時になります。

### set_emit_on_sync {#set_emit_on_sync}

```cpp
void set_emit_on_sync(bool b) noexcept;
```

`true` にすると、`flush`（`endl` や `std::flush`）が呼ばれたときに、自動で `emit` されます。既定は `false` で、`flush` を呼んでも、溜めるだけです。`osyncstream` では、`std::flush_emit` の操作子が、この `emit_on_flush` の設定と組になっています。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <syncstream>

int main() {
  std::ostringstream target;       // 出力先（画面の代わり）
  std::syncbuf sb(target.rdbuf());
  std::ostream os(&sb);

  os << "hello\n";
  std::println("emit 前: {:?}", target.str());  // まだ空

  sb.emit();
  std::println("emit 後: {:?}", target.str());
}
```

```text title="実行結果"
emit 前: ""
emit 後: "hello\n"
```

`emit` を呼ぶまで、`target` に何も届いていないのが分かります。`emit` で初めて、溜めた内容がまとめて書かれました。

## ゲームでの使いどころ

ワーカー スレッドのログを、`cout` に混ぜずに出したいときの部品です。ただし、`syncbuf` を自分で組み立てるより、使い捨ての `osyncstream` を作るほうが簡単です。

```cpp
std::osyncstream(std::cout) << "敵 " << id << " を倒した\n";  // 行の最後で自動的に emit される
```

一時オブジェクトが文の終わりで破棄され、そのときに `emit` が呼ばれます。1 回の書き込みが 1 まとまりで出ます。

## よくあるミス

??? failure "emit を呼ばず、出る時機が遅れる"
    デストラクターで `emit` されますが、長く生きる `syncbuf` では、いつまでも出ません。ログを出したいところで `emit` を呼びます。

??? failure "別の出力先に書いたものが同期されると思う"
    同期されるのは、同じ出力先に対する `emit` どうしだけです。`cout` と `cerr` に別々に書いたものが、混ざらないわけではありません。

??? failure "cout に直接書いたものは混ざる"
    `syncbuf` を使わず、`std::cout << ...` で直接書いているスレッドがあると、そちらの出力は、割り込めます。そのスレッドも、`osyncstream` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::osyncstream`](osyncstream.md) | `syncbuf` を使いやすくしたラッパー。普段はこちら |
| [`std::emit_on_flush`](emit_on_flush.md) | `flush` で `emit` するかを切り替える操作子 |
| [`std::flush_emit`](flush_emit.md) | `flush` と `emit` を同時に行う操作子 |
| [`std::mutex`](../concurrency/mutex.md) | ログ全体を排他制御する、別の方法 |

## コンパイラ対応

C++20 の機能です。MSVC、GCC、Clang とも対応しています。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `syncbuf` は、書き込みを溜めて、`emit` でまとめて出力先に書く
    - [x] 同じ出力先への `emit` は順番に行われ、行が混ざらない
    - [x] 普段は `osyncstream` を使う

## 関連ページ

- [cpprefjp: std::syncbuf](https://cpprefjp.github.io/reference/syncstream/basic_syncbuf.html)
- [cppreference: std::syncbuf](https://en.cppreference.com/w/cpp/io/basic_syncbuf)
