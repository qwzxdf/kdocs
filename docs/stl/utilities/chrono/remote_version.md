---
title: std::chrono::remote_version
summary: "OS が持つ、最新のタイムゾーンデータベースの版を返す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::remote_version

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

いま使っているデータベースより新しい版があるかを、読み込む前に知りたいことがあります。`remote_version()` は、OS 側にある最新の版の文字列を返します。`get_tzdb().version` と比べて違えば、`reload_tzdb()` で読み込み直せます。

!!! tip "ポイント"
    - 戻り値は版を表す文字列（例: `2024a`）。
    - 現在の版は `get_tzdb().version`。
    - 違えば `reload_tzdb()` を呼ぶ。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::remote_version {#remote_version}

```cpp
std::string remote_version();
```

- 戻り値: OS が持つ最新の版の文字列
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  std::println("{}", !std::chrono::remote_version().empty());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 更新があるときだけ読み直す | `if (remote_version() != get_tzdb().version) reload_tzdb();` |

## よくあるミス

??? failure "読み直しをしても反映されない"
    OS 側のデータが更新されていないと、同じ版のままです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`reload_tzdb`](reload_tzdb.md) | 読み直す |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最新の版を返す
    - [x] get_tzdb().version と比べる
    - [x] 更新確認に使う

## 関連ページ

- [cpprefjp: std::chrono::remote_version](https://cpprefjp.github.io/reference/chrono/remote_version.html)
- [cppreference: std::chrono::remote_version](https://en.cppreference.com/w/cpp/chrono/tzdb_functions)
