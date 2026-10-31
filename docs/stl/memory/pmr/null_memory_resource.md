---
title: std::pmr::null_memory_resource
summary: "確保しようとすると必ず失敗するメモリリソース。"
order: 6
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::null_memory_resource

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory_resource>`
</div>

`std::pmr::null_memory_resource()` は、確保を要求されると、必ず `std::bad_alloc` を投げるリソースを返します。一見、役に立たなさそうですが、「ここからはもう確保させない」という守りになります。固定バッファの `monotonic_buffer_resource` の上流に置けば、バッファを使い切った瞬間に、必ず検出できます。

!!! tip "ポイント"
    - `allocate` は常に `std::bad_alloc` を投げる
    - `deallocate` は何もしない
    - 固定バッファ（ヒープ禁止）の設計を、強制するために使う
    - `set_default_resource` に渡せば、うっかり既定のリソースから確保するのを見つけられる

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::pmr::null_memory_resource {#null_memory_resource}

<span class="ver ver-17">C++17</span>

```cpp
std::pmr::memory_resource* null_memory_resource() noexcept;
```

`new_delete_resource` と同じく、いつも同じオブジェクトを返します。

使い方は主に 2 つです。1 つは、固定バッファのリソースの上流にして、バッファに収まる設計であることを強制します。ゲーム機のように、実行中にヒープを使いたくない環境で、収まらなければ即座に分かります。

もう 1 つは、既定のリソースにして、「リソースを指定し忘れた `pmr` コンテナ」を見つけることです。`set_default_resource(null_memory_resource())` をテストで呼ぶと、リソースを渡さずに作ったコンテナが、確保した瞬間に例外になります。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>
#include <vector>

int main() {
  std::pmr::memory_resource* r = std::pmr::null_memory_resource();

  try {
    r->allocate(8);
  } catch (const std::bad_alloc&) {
    std::println("確保は必ず失敗する");
  }

  // 既定のリソースにして、指定し忘れを検出する
  std::pmr::memory_resource* old = std::pmr::set_default_resource(r);
  try {
    std::pmr::vector<int> forgot;  // リソースを渡していない
    forgot.push_back(1);
  } catch (const std::bad_alloc&) {
    std::println("リソースの指定し忘れを検出");
  }
  std::pmr::set_default_resource(old);
}
```

```text title="実行結果"
確保は必ず失敗する
リソースの指定し忘れを検出
```

## ゲームでの使いどころ

ヒープを使わない設計のモジュールのテストで、`pmr` コンテナのリソースの指定漏れを見つけます。

## よくあるミス

??? failure "既定のリソースにしたまま戻さない"
    以降の確保がすべて失敗します。`set_default_resource(old)` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`new_delete_resource`](new_delete_resource.md) | 通常のリソース |
| [`monotonic_buffer_resource`](monotonic_buffer_resource.md) | 上流に置く |
| [`default_resource`](default_resource.md) | 既定のリソース |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::pmr::null_memory_resource](https://cpprefjp.github.io/reference/memory_resource/null_memory_resource.html)
- [cppreference: std::pmr::null_memory_resource](https://en.cppreference.com/w/cpp/memory/null_memory_resource)
