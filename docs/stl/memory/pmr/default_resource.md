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

リソースを指定せずに作った `pmr` コンテナは、プログラムで 1 つの「既定のリソース」から確保します。`std::pmr::get_default_resource()` で今の既定を取得し、`std::pmr::set_default_resource(r)` で差し替えます。何も設定しなければ、`new_delete_resource()` です。

!!! tip "ポイント"
    - `get_default_resource()` で現在の既定を得る
    - `set_default_resource(r)` で差し替え、直前の値を返す
    - `nullptr` を渡すと、`new_delete_resource()` に戻る
    - 差し替えは、プログラム全体に効く。テスト以外では、あまり使わない

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::pmr::get_default_resource / set_default_resource {#default_resource}

<span class="ver ver-17">C++17</span>

```cpp
std::pmr::memory_resource* get_default_resource() noexcept;
std::pmr::memory_resource* set_default_resource(std::pmr::memory_resource* r) noexcept;
```

`set_default_resource` は、直前の既定を返します。差し替えたら、あとで必ず元に戻します。

既定のリソースは、リソースを渡さずに作ったコンテナや、`polymorphic_allocator` の既定の構築が参照します。すでに作ったコンテナは、作ったときのリソースを覚えているので、あとから `set_default_resource` で変えても、影響を受けません。

どちらの関数も、スレッド セーフです。ただし、差し替えのタイミングと、他のスレッドのコンテナの作成が競合すると、どちらのリソースを使うかは不定です。

ゲームでは、起動時に 1 回、全体用のプールを既定にする、といった使い方をします。差し替えが全体に効く性質は、便利ですが、どこから確保しているかが分かりにくくなります。重要なコンテナには、明示的にリソースを渡すほうが、読みやすくなります。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>
#include <vector>

int main() {
  std::pmr::memory_resource* original = std::pmr::get_default_resource();
  std::println("最初は new_delete_resource: {}", original == std::pmr::new_delete_resource());

  std::byte buffer[256];
  std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));

  // 既定を差し替える
  std::pmr::memory_resource* old = std::pmr::set_default_resource(&pool);
  std::println("直前の値が返る: {}", old == original);

  std::pmr::vector<int> v;  // リソースを渡していないが、pool から確保される
  v.push_back(1);
  std::println("pool から確保: {}", v.get_allocator().resource() == &pool);

  v.clear();
  v.shrink_to_fit();
  std::pmr::set_default_resource(old);  // 元に戻す
  std::println("戻した: {}", std::pmr::get_default_resource() == original);
}
```

```text title="実行結果"
最初は new_delete_resource: true
直前の値が返る: true
pool から確保: true
戻した: true
```

## ゲームでの使いどころ

テストで、すべての `pmr` コンテナを検査用のリソースに向けて、確保の回数を数えるときに使います。

## よくあるミス

??? failure "差し替えたあと、元に戻さない"
    以降のコンテナが、消えたリソースを使って壊れます。

??? failure "作成済みのコンテナに効くと思う"
    効きません。作った時点のリソースを使い続けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`new_delete_resource`](new_delete_resource.md) | 既定の値 |
| [`null_memory_resource`](null_memory_resource.md) | 指定し忘れの検出に使う |
| [`polymorphic_allocator`](polymorphic_allocator.md) | 既定のリソースを参照する |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::pmr::set_default_resource](https://cpprefjp.github.io/reference/memory_resource/default_resource.html)
- [cppreference: std::pmr::set_default_resource](https://en.cppreference.com/w/cpp/memory/default_resource)
