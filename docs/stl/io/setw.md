---
title: std::setw
summary: "次に出す値の「幅」を決める（右寄せでそろえる）。"
order: 76
tags:
  - 入出力・文字列
---

# std::setw

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <iomanip>`
</div>

ステータス画面を文字で表示するとき、名前と数値を縦にそろえて並べたい。文字数の違う名前を、同じ幅の欄に収めたい。次の出力の「最小の幅」を指定するのが `std::setw` です。

!!! tip "ポイント"
    - `std::setw(10)` で、次の 1 つの出力を、10 文字分の幅の欄に入れる
    - <strong>次の 1 回の出力にしか効かない</strong>。毎回指定し直す
    - 既定では、右にそろえる。左にそろえるなら `std::left`
    - 幅より長い文字列は、切り詰められず、はみ出す

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::setw {#setw}

```cpp
/* 未規定 */ setw(int n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `int` | 次の出力の最小の幅（文字数） |

次の出力が `n` 文字に満たなければ、足りない分を詰め物（既定では空白）で埋めます。詰め物は [`setfill`](setfill.md) で変えられ、どちら側に埋めるかは [`left`](left.md)、[`right`](right.md)、[`internal`](internal.md) で決まります。

他の操作子と違って、<strong>幅の指定は、1 回の出力で解除されます</strong>。`std::cout << std::setw(5) << a << b` と書くと、`a` は幅 5 で出ますが、`b` は幅の指定なしで出ます。表を作るときは、各欄の前に毎回 `setw` を書きます。

幅より長い内容は、切り詰められません。欄をはみ出して、そのまま出ます。

日本語の全角文字は、幅としては 1 文字と数えられ、画面上の見た目では 2 文字分の幅を取ります。`setw` は文字数で数えるので、日本語を含む表は、そろいません。表示幅の計算は、別に自前で行う必要があります。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::left;                    // 左にそろえる
  std::cout << std::setw(8) << "name" << std::setw(5) << "hp" << '|' << '\n';
  std::cout << std::setw(8) << "hero" << std::setw(5) << 100 << '|' << '\n';
  std::cout << std::setw(8) << "slime" << std::setw(5) << 7 << '|' << '\n';

  // 幅は 1 回の出力で解除される
  std::cout << std::right << std::setw(5) << 1 << 2 << '\n';

  // 幅より長いと、はみ出す
  std::cout << std::setw(2) << "long" << '\n';
}
```

```text title="実行結果"
name    hp   |
hero    100  |
slime   7    |
    12
long
```

## ゲームでの使いどころ

コンソール ツールのログや、デバッグ表示で、表の形に並べるときに使います。ステータス、アセット名とサイズの一覧、プロファイラーの結果などです。

C++20 以降は、`std::format("{:<8}{:>5}", name, hp)` のように、書式の中で幅とそろえを指定できます。設定が残らない点で、`setw` より扱いやすいので、新しいコードではそちらを選びます。

## よくあるミス

??? failure "幅の指定が続くと思って、2 つ目以降がそろわない"
    毎回 `setw` を書きます。

??? failure "日本語を含む表がずれる"
    文字数と表示幅が違います。表示幅を別に計算するか、日本語を含まない欄でそろえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setfill`](setfill.md) | 詰め物の文字を指定する |
| [`left`](left.md) | 左にそろえる |
| [`right`](right.md) | 右にそろえる |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 次の 1 回の出力の最小の幅を決める
    - [x] 毎回指定する
    - [x] はみ出す分は切らない

## 関連ページ

- [cpprefjp: std::setw](https://cpprefjp.github.io/reference/iomanip/setw.html)
- [cppreference: std::setw](https://en.cppreference.com/w/cpp/io/manip/setw)
