---
title: std::unitbuf
summary: "出力のたびに、バッファをフラッシュする。"
order: 900
tags:
  - 入出力・文字列
---

# std::unitbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

出力はふつうバッファに貯められて、まとめて書き出されます。`unitbuf` を設定すると、`<<` のたびに書き出されます。`cerr` が既定でこの設定です。クラッシュ直前のログを確実に残したいときに使いますが、遅くなります。

!!! tip "ポイント"
    - `cerr` は既定でオン。
    - `nounitbuf` で解除する。
    - 遅くなるので、必要な場面だけ。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::unitbuf {#unitbuf}

```cpp
std::ios_base& unitbuf(std::ios_base& str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | ios_base& | 対象のストリーム |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << std::unitbuf << "x\n";
}
```

```text title="実行結果"
x
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "速度を気にしない"
    毎回フラッシュするので、大量の出力が遅くなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`flush`](flush.md) | 手動でフラッシュ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力のたびに、バッファをフラッシュする
    - [x] `cerr` は既定でオン
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::unitbuf](https://cpprefjp.github.io/reference/ios/unitbuf.html)
- [cppreference: std::unitbuf](https://en.cppreference.com/w/cpp/io/manip/unitbuf)
