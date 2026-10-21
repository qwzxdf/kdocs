---
title: std::filesystem::weakly_canonical
summary: "存在しない部分を含むパスも正規化する（canonical の緩い版）。"
order: 29
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::weakly_canonical

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::weakly_canonical` は、[`canonical`](canonical.md) の**存在しない部分があっても使える版**です。存在する部分だけを正規化（`..` やリンクを解決）し、残りは字句的に整えます。これから作るファイルのパスを、絶対パスに整えるときに使います。

!!! tip "ポイント"
    - `canonical` は存在しないと例外、こちらは例外にならない。
    - 保存先など「まだ無いパス」の正規化に向く。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::filesystem::weakly_canonical {#weakly_canonical}

```cpp
path weakly_canonical(const path& p);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 正規化するパス |

- 戻り値: 正規化したパス
- 計算量: パスの深さに比例

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  auto p = fs::weakly_canonical("no_such_dir/../save.dat");   // 存在しなくても OK
  std::println("{}", p.filename().generic_string());
}
```

```text title="実行結果"
save.dat
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| まだ無い保存先を絶対パスにする | `fs::weakly_canonical(save_dir / name)` |

## よくあるミス

??? failure "同じファイルかの比較に使う"
    存在しない部分は字句的な整理だけなので、同一性の判定は `equivalent` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`canonical`](canonical.md) | 存在が必要 |
| [`absolute`](absolute.md) | 絶対パスにするだけ |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 存在しなくても正規化できる
    - [x] canonical の緩い版
    - [x] 保存先の整形に

## 関連ページ

- [cpprefjp: std::filesystem::weakly_canonical](https://cpprefjp.github.io/reference/filesystem/weakly_canonical.html)
- [cppreference: std::filesystem::weakly_canonical](https://en.cppreference.com/w/cpp/filesystem/canonical)
