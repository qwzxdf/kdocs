---
title: std::quoted
summary: "文字列を、引用符で囲んで出力・入力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::quoted

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <iostream>`
</div>

空白を含む文字列を `"a b"` のように引用符で囲んで書き出し、読み込むときは引用符を外して読み戻せます。設定ファイルの書き出しなどに便利です。

!!! tip "ポイント"
    - `"` で囲み、中の `"` は `\` でエスケープする。
    - 入力でも引用符を処理して元に戻す。
    - `<iomanip>` が必要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::quoted {#quoted}

```cpp
template <class CharT, class Traits, class Alloc>
/* 実装定義 */ quoted(const std::basic_string<CharT, Traits, Alloc>& s, CharT delim = '"', CharT escape = '\\');
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | 文字列 | 囲む文字列 |
| `delim` | 文字 | 省略可。囲む文字 |
| `escape` | 文字 | 省略可。エスケープ文字 |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::quoted("a b") << '\n';
}
```

```text title="実行結果"
"a b"
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "入力時に引用符を忘れる"
    `quoted` で読むには、入力側にも引用符が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`getline`](getline.md) | 行を読む |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を引用符で囲んで出力・入力する
    - [x] `"` で囲み、中の `"` は `\` でエスケープする
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::quoted](https://cpprefjp.github.io/reference/ios/quoted.html)
- [cppreference: std::quoted](https://en.cppreference.com/w/cpp/io/manip/quoted)
