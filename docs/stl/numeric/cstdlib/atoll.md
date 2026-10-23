---
title: std::atoll
summary: "文字列を long long に変換する。"
order: 900
tags:
  - 数値
---

# std::atoll

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`std::atoi` の、戻り値の型違いの仲間です。`std::atoll` は、文字列を`long long`に変換します。`atoi` と同じ欠点（失敗しても 0 を返し、区別できない）を持つので、検査が必要な場面では `strtol` / `strtoll` を使います。

!!! tip "ポイント"
    - `std::atoll("5000000000")` は 5000000000
    - 数字でない文字列は 0 を返す
    - 範囲を超えると未定義動作
    - 検査が要るなら `strtol` / `strtoll`、新しいコードは `from_chars`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::atoll {#atoll}

```cpp
long long atoll(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 数値を表す、null で終わる文字列 |

戻り値は、文字列の先頭から読み取れた整数で、型は long long です。先頭の空白を飛ばし、符号と数字を読みます。数字でない文字に出会うと、そこで止めて、それまでの値を返します。

失敗を検出できません。`"abc"` の 0 と `"0"` の 0 は区別できず、範囲を超えると未定義動作です。`atoi` / `atol` / `atoll` の違いは、戻り値の型の幅だけです。Windows では `long` が 32 ビットなので、`atol` は `atoi` と同じ範囲です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("atoll(\"5000000000\") = {}", std::atoll("5000000000"));
  std::println("atoll(\"abc\") = {}", std::atoll("abc"));   // 失敗しても 0
}
```

```text title="実行結果"
atoll("5000000000") = 5000000000
atoll("abc") = 0
```

## ゲームでの使いどころ

簡単なツールで、必ず正しい数字の文字列を読むだけの場面に使います。ユーザーの入力には、失敗を検出できる `strtol` / `from_chars` を使います。

## よくあるミス

??? failure "失敗した 0 と本当の 0 を区別できない"
    `strtol` / `from_chars` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atoi`](atoi.md) | `int` を返す |
| [`strtol`](strtol.md) | 失敗が分かる |
| [`strtoll`](strtoll.md) | `long long` で失敗が分かる |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `atoll` は文字列を`long long`に変換する
    - [x] 失敗しても 0 を返し、区別できない
    - [x] 検査が要るなら `strto*` か `from_chars`

## 関連ページ

- [cpprefjp: std::atoll](https://cpprefjp.github.io/reference/cstdlib/atoll.html)
- [cppreference: std::atoll](https://en.cppreference.com/w/cpp/c/atoll)
