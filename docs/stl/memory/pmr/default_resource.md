---
title: std::pmr::set_default_resource
summary: "pmr コンテナの既定のメモリリソースを取得・変更する。"
order: 8
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::set_default_resource

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory_resource>`
</div>

`std::pmr::get_default_resource()` と `set_default_resource()` は、**pmr コンテナにリソースを渡さなかったときの既定のメモリリソース**を取得・変更する関数です。プログラム全体の取り先を一度に切り替えたいときに使います。

!!! tip "ポイント"
    - 既定は `new_delete_resource()`。
    - 変更はスレッドセーフだが、プログラム全体に影響する。起動直後に 1 回だけ。
    - 使わずに、リソースを明示して渡すほうが安全。

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### get_default_resource {#get_default_resource}

```cpp
memory_resource* get_default_resource() noexcept;
```

- 戻り値: 今のデフォルトのリソース。最初は `new_delete_resource()`
- リソースを渡さなかった pmr コンテナがこれを使います

### set_default_resource {#set_default_resource}

```cpp
memory_resource* set_default_resource(memory_resource* r) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | `std::pmr::memory_resource*` | 新しいデフォルトのリソース。`nullptr` なら `new_delete_resource()` に戻る |

- 戻り値: 前のデフォルト
- 以降に作る pmr コンテナ（リソースを渡さないもの）が `r` を使うようになります。**プログラム全体に効く**ので、普通は使わず、リソースを明示的に渡します

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>

int main() {
  std::println("{}", std::pmr::get_default_resource() == std::pmr::new_delete_resource());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| プロファイル用に全 pmr コンテナの確保を数える | `set_default_resource(&counting_resource)` |

## よくあるミス

??? failure "途中で変更する"
    変更前に確保したメモリを変更後のリソースで解放してしまうことがあります。起動直後に 1 回だけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`new_delete_resource`](new_delete_resource.md) | 既定の値 |

## コンパイラ対応

C++17 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 既定のリソースの取得・変更
    - [x] プログラム全体に影響
    - [x] 起動直後に 1 回だけ

## 関連ページ

- [cpprefjp: std::pmr::set_default_resource](https://cpprefjp.github.io/reference/memory_resource/default_resource.html)
- [cppreference: std::pmr::set_default_resource](https://en.cppreference.com/w/cpp/memory/default_resource)
