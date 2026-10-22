---
title: std::cout
summary: "標準出力。画面に文字や値を出す（<< でつなぐ）。"
order: 70
tags:
  - 入出力・文字列
---

# std::cout

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <iostream>`
</div>

`std::cout` は、**標準出力（画面）に文字や値を出す**ストリームです。`std::cout << "HP " << hp << "\n";` のように、`<<` で値をつなげて出します。C++23 では [`std::println`](../utilities/print.md) のほうが書きやすく、型の安全も高いので、新しく書くコードではそちらを使います。

!!! tip "ポイント"
    - 改行は `"\n"` を使う。`std::endl` は毎回 `flush` するので遅い。
    - 桁数や幅は [`setw`](setw.md) / [`setprecision`](setprecision.md) で指定する。
    - 新しいコードでは `std::println`。`cout` は古いコードを読むために知っておく。

## 関数の詳しい説明

### std::cout {#cout}

```cpp
extern std::ostream cout;
```

- 標準出力（コンソール画面）。`<<` で値を流し込みます

### operator<< {#shift-out}

```cpp
std::ostream& operator<<(std::ostream& os, int value);  // 型ごとにある
```

- 値を文字にして出力します。戻り値が同じストリームなので、`<<` を続けて書けます
- 自作の型も `operator<<` を定義すれば出力できます

```cpp
#include <iostream>

struct Vec2 {
  float x;
  float y;
};

std::ostream& operator<<(std::ostream& os, const Vec2& v) {
  return os << '(' << v.x << ", " << v.y << ')';
}

int main() {
  std::cout << Vec2{1.5f, -2.0f} << '\n';
}
```

```text title="実行結果"
(1.5, -2)
```

### std::wcout {#wcout}

```cpp
extern std::wostream wcout;
```

- 戻り値: `wostream`（`wchar_t` の標準出力）
- 計算量: 操作による

`wcout` は、`cout` の `wchar_t` 版です。`wchar_t` の文字列（`L"..."`）を扱うときに使います。1 つのプログラムで `cout` と `wcout` を混ぜて使うと、文字化けや動作不良の原因になることがあります。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| デバッグ表示（C++20 以前のコード） | `std::cout << x << "\n";` |

## よくあるミス

??? failure "endl を多用して遅くなる"
    `std::endl` は改行と `flush` を毎回行います。大量に出すときは `"\n"` にします。

??? failure "printf と混ぜて順序が乱れる"
    `std::ios::sync_with_stdio(false)` にすると、`printf` との順序が保証されなくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../utilities/print.md) | 書式つき出力。新しいコードはこちら |
| [`std::cerr`](cerr.md) | エラー出力 |
| [`std::cin`](cin.md) | 標準入力 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準出力のストリーム
    - [x] `<<` でつなげて出す
    - [x] 新しいコードは `println`

## 関連ページ

- [cpprefjp: std::cout](https://cpprefjp.github.io/reference/iostream/cout.html)
- [cppreference: std::cout](https://en.cppreference.com/w/cpp/io/cout)
