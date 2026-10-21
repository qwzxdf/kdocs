---
title: std::filesystem::canonical
summary: "パスを正規化する（`..` やリンクを解決する）。"
order: 21
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::canonical

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::canonical` は、**パスを正規の絶対パスにする**関数です。`.` や `..`、シンボリックリンクを解決します。**パスが実在しないと失敗**します。同じファイルを指しているかの比較に使います。

!!! tip "ポイント"
    - 存在しないパスは例外。
    - 存在しなくてもよいなら `weakly_canonical`。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### canonical {#canonical}

```cpp
path canonical(const path& p);
```

- `..` やシンボリックリンクを解決した正式な絶対パス。**ファイルが無いと例外**

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::println("{}", fs::canonical(".") == fs::canonical(fs::current_path()));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 同じファイルの二重読み込みを防ぐ | `canonical` したパスをキーにする |

## よくあるミス

??? failure "存在しないパスに使う"
    例外になります。`weakly_canonical` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`absolute`](absolute.md) | 存在確認なし |
| [`equivalent`](equivalent.md) | 同じ実体か比べる |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 正規の絶対パス
    - [x] 実在が必要
    - [x] 存在しなくていいなら weakly_canonical

## 関連ページ

- [cpprefjp: std::filesystem::canonical](https://cpprefjp.github.io/reference/filesystem/canonical.html)
- [cppreference: std::filesystem::canonical](https://en.cppreference.com/w/cpp/filesystem/canonical)
