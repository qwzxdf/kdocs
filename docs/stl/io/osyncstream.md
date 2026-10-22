---
title: std::osyncstream
summary: "複数のスレッドが同時に出力しても、行が混ざらないようにする出力ストリーム。"
order: 93
tags:
  - 入出力・文字列
---

# std::osyncstream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <syncstream>`
</div>

`std::osyncstream` は、**複数のスレッドが同時に `cout` に出力しても、出力が文字単位で混ざらないようにする**出力ストリームです。一時的に出力をため込み、破棄されるときにまとめて出力します。マルチスレッドのデバッグ用のログ出力に便利です。

!!! tip "ポイント"
    - `std::osyncstream(std::cout) << "…" << "\n";` のように、一時オブジェクトで使う。
    - 破棄された時点でまとめて出力され、他のスレッドの出力と混ざらない。
    - ログが多いなら、専用のログ機構のほうが速い。

## 関数の詳しい説明

### std::osyncstream {#osyncstream}

```cpp
class osyncstream : public std::ostream {
 public:
  explicit osyncstream(std::ostream& out);
  void emit();
};
```

- 戻り値: （クラス）
- 計算量: O(出力量) + ロック

```cpp
#include <iostream>
#include <syncstream>

int main() {
  // 一行ずつ、混ざらずに出力される（複数のスレッドから呼んでも安全）
  std::osyncstream(std::cout) << "ロード開始" << '\n';
}
```

```text title="実行結果"
ロード開始
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 複数のスレッドのデバッグログを、混ざらずに出す | `std::osyncstream(std::cout) << msg << "\n";` |

## よくあるミス

??? failure "1 行を複数回の << に分けて出す"
    osyncstream の一時オブジェクトが生きている間は、まとまって出力されます。一時オブジェクトを使い回さないように注意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::cout`](cout.md) | 混ざる可能性がある |
| [`std::println`](../utilities/print.md) | 1 回の呼び出しは混ざらないことが多い |

## コンパイラ対応

C++20 の機能です。GCC 11 / MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 混ざらない出力ストリーム
    - [x] 破棄時にまとめて出力
    - [x] 複数スレッドのログに

## 関連ページ

- [cpprefjp: std::osyncstream](https://cpprefjp.github.io/reference/syncstream/basic_osyncstream.html)
- [cppreference: std::osyncstream](https://en.cppreference.com/w/cpp/io/basic_osyncstream)
