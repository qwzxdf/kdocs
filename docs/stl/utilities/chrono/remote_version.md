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

`reload_tzdb` は重い処理なので、むやみに呼びたくありません。更新があるかどうかを、軽く先に確かめたいときに、`std::chrono::remote_version` を使います。OS が持つ最新のデータベースの版を、文字列だけで返し、データの読み込みはしません。

!!! tip "ポイント"
    - OS の最新版の名前（`2025b` など）を `std::string` で返す
    - 現在の版は `get_tzdb().version`。比べて違えば、更新がある
    - 読み込みはしない。`reload_tzdb` より軽い
    - 版の形式は実装による

!!! info "このページを読む前に"
    [`reload_tzdb`](reload_tzdb.md) と [`get_tzdb`](get_tzdb.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::remote_version {#remote_version}

<span class="ver ver-20">C++20</span>

```cpp
std::string remote_version();
```

引数はありません。OS（または、ランタイムが参照する配布元）にあるデータベースの版を、文字列で返します。IANA の版は `2025b` のような形ですが、MSVC のように、別の仕組み（ICU）を使う実装では、形が違うことがあります。

現在の版と比べて、違えば `reload_tzdb` を呼ぶ、という使い方をします。

```cpp
if (std::chrono::remote_version() != std::chrono::get_tzdb().version) {
  std::chrono::reload_tzdb();
}
```

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const std::string remote = remote_version();
  std::println("OS の版がある: {}", !remote.empty());

  // 現在の版と比べて、更新が必要かを判定する（結果は環境しだい）
  const bool needs_update = remote != get_tzdb().version;
  if (needs_update) reload_tzdb();
  std::println("更新後も版がある: {}", !get_tzdb().version.empty());
}
```

```text title="実行結果"
OS の版がある: true
更新後も版がある: true
```

更新が必要かどうかは環境で変わるので、結果は表示していません。

## ゲームでの使いどころ

サーバーの起動時や定期の処理で、更新の有無を確かめてから、`reload_tzdb` を呼ぶかどうかを決めます。

## よくあるミス

??? failure "版の文字列を数として比べる"
    `2025b` のような形式は、辞書順で新旧を比べられますが、実装によって形式が違います。等しいか違うかだけを判断します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`reload_tzdb`](reload_tzdb.md) | 実際に読み込み直す |
| [`get_tzdb`](get_tzdb.md) | 現在の版を取る |
| [`tzdb`](tzdb.md) | `version` を持つ |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: remote_version](https://cpprefjp.github.io/reference/chrono/remote_version.html)
- [cppreference: std::chrono::remote_version](https://en.cppreference.com/w/cpp/chrono/remote_version)
