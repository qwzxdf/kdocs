---
title: std::xxx
tags:
  - コンテナ
---

<!--
記事テンプレート（このファイル自体はサイトに出ません）。見本は stl/containers/vector.md

書き方のルール
- WIKI ではなく「学生のノート」。全部を同じ熱量で書かない
- 「9割はこう使う」「これはあまり使わない」「ここでハマる」を必ず書く
- 一覧は「よく使う順」。アルファベット順にしない
- 関数は 1 つずつ見出しを分けて、引数・戻り値・計算量を必ず書く（「a / b」のようにまとめない）
- 速さはクラス（型）にだけ付ける。関数には付けない（関数ごとの速さは使い分けで決まるため）
- 速さを比べるのは、複数のクラスを並べる表（一覧ページなど）だけ
- フラグ・オプションがあるものは全部書く（よく使う順）
- サンプルコードは C++23、Google C++ Style、コメントあり
- 出力があるサンプルは int main まで書いた完全なプログラムにして、直後に実行結果を載せる
  （int main があると「Compiler Explorer で実行」リンクが自動で付く）
- 実装によって結果が違うものは「実行結果（GCC / Clang）」のようにタイトルに書き、違いを本文で説明する
- 動きが目で見えると分かりやすいもの（メモリの並び、詰める、引っ越すなど）は図解を入れる
- 該当しない見出しは消してよい（フラグがない、など）

重要度ランク
  <span class="rank rank-must">必須</span>
  <span class="rank rank-often">よく使う</span>
  <span class="rank rank-sometimes">たまに</span>
  <span class="rank rank-rare">知ってるだけ</span>

速さ（クラスのページ上部にだけ付ける。基準は how-to-read.md）
  <span class="perf perf-4">◎ 速い</span>
  <span class="perf perf-3">○ 普通</span>
  <span class="perf perf-2">△ やや重い</span>
  <span class="perf perf-1">× 重い</span>

バージョンバッジ
  <span class="ver ver-11">C++11</span> ver-14 / ver-17 / ver-20 / ver-23 / ver-26
  関数の見出しに付けるときは、見出しの右に書いて目次用のラベルを指定する:
  ### append_range <span class="ver ver-23">C++23</span> {#append_range data-toc-label="append_range"}

図解（メモリのマス目）
  <div class="mem">
  <div class="mem-step"><span class="mem-label">ラベル</span><span class="mem-cells"><span>10</span><span class="gone">20</span><span class="move">30</span><span class="new">40</span><span class="free">　</span></span><span class="mem-note">説明</span></div>
  </div>
  span のクラス: なし=使用中 / free=空き / gone=消えた / move=動いた / new=追加した
  凡例が要るときは <div class="mem-legend"> を足す（vector.md の「再確保のしくみ」参照）
-->

# std::xxx

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++11</span>
`#include <xxx>`
</div>

`std::xxx` は、**一言で何か**です。どういうしくみで、何がうれしいのかを 2〜3 文で。

!!! tip "ポイント"
    - 迷ったらこれを使う / 使わない
    - 9 割はこう書く、というパターン
    - ここだけは必ず覚えておく、という注意

!!! info "このページを読む前に"
    [参照](basics/reference.md)、[テンプレート](basics/template.md) が分かると読みやすいです。

## 宣言

```cpp
template <class T>
class xxx;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 要素の型 | 必ず |

### コンストラクタ

| 書き方 | 重要度 | 結果 |
| --- | --- | --- |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`f`](#f) | <span class="rank rank-must">必須</span> | | O(1) |

## よくある使い方

上の関数を実際にどう組み合わせるかの例です。

### 1. パターン名

```cpp
#include <print>

int main() {
}
```

```text title="実行結果"
```

## 関数の詳しい説明

### f {#f}

```cpp
void f(const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` | |

- 戻り値:
- 計算量:
- 例外:

```cpp
#include <print>

int main() {
}
```

```text title="実行結果"
```

!!! note "実際は"
    ここに「本当はこう使う」「これは要らない」を書く。

## フラグ・オプション

指定できる値をすべて、よく使う順に書く。

| 値 | 重要度 | 意味 | 使う場面 |
| --- | --- | --- | --- |

## 計算量まとめ

| 操作 | 計算量 |
| --- | --- |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    ```

=== "今の書き方（C++23）"

    ```cpp
    ```

## ゲームでの使いどころ

## パフォーマンス

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |

## よくあるミス

??? failure "ミスの見出し"
    説明とコード

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 3〜5 行で
    - [x]
    - [x]

## 関連ページ

- [cpprefjp](https://cpprefjp.github.io/)
- [cppreference](https://en.cppreference.com/)
