---
title: std::filesystem::equivalent
summary: "2 つのパスが同じファイルを指すか調べる。"
order: 22
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::equivalent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::equivalent` は、**2 つのパスが同じファイル（実体）を指すか**を調べる関数です。表記が違っても（相対と絶対、リンク経由）、同じものなら `true` です。

!!! tip "ポイント"
    - 両方が実在する必要がある。
    - パスの文字列比較より確実。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### equivalent {#equivalent}

```cpp
bool equivalent(const path& p1, const path& p2);
```

- 2 つのパスが同じファイルを指しているか

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::println("{}", fs::equivalent(".", fs::current_path()));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 同じファイルの重複登録を防ぐ | `fs::equivalent(a, b)` |

## よくあるミス

??? failure "存在しないパスで例外"
    両方が存在しないとエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`canonical`](canonical.md) | 正規化して文字列で比べる |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ実体を指すか
    - [x] 表記が違ってもよい
    - [x] 両方の実在が必要

## 関連ページ

- [cpprefjp: std::filesystem::equivalent](https://cpprefjp.github.io/reference/filesystem/equivalent.html)
- [cppreference: std::filesystem::equivalent](https://en.cppreference.com/w/cpp/filesystem/equivalent)
