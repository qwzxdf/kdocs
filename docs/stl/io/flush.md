---
title: std::flush
summary: "出力のバッファにたまった中身を、すぐ書き出す。"
order: 75
tags:
  - 入出力・文字列
---

# std::flush

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ostream>`
</div>

`std::flush` は、**出力のバッファにたまっている中身を今すぐ書き出す**マニピュレーターです。改行は付きません。ログを確実にファイルへ出したいとき、クラッシュに備えたいときに使います。

!!! tip "ポイント"
    - `std::cout << "処理中..." << std::flush;` のように、改行なしで出したいときに便利。
    - `ofstream` では `out.flush()` とも書ける。
    - 頻繁に呼ぶと遅くなる。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::flush {#flush}

```cpp
std::ostream& flush(std::ostream& os);
```

- 改行せずに、たまった出力をすぐ書き出します

## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << "処理中..." << std::flush;  // 改行なしで、すぐ書き出す
  std::cout << "完了\n";
}
```

```text title="実行結果"
処理中...完了
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| クラッシュしても残したいログ | `log << msg << std::flush;` |

## よくあるミス

??? failure "毎回 flush して遅い"
    ディスクへの書き込みは遅いので、本当に必要な箇所だけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::endl`](endl.md) | 改行 + flush |
| [`std::ofstream`](ofstream.md) | `flush()` メンバ関数 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バッファの中身をすぐ書き出す
    - [x] 改行は付かない
    - [x] 頻繁に呼ばない

## 関連ページ

- [cpprefjp: std::flush](https://cpprefjp.github.io/reference/ostream/flush.html)
- [cppreference: std::flush](https://en.cppreference.com/w/cpp/io/manip/flush)
