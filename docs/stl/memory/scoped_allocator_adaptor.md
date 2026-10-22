---
title: std::scoped_allocator_adaptor
summary: "入れ子のコンテナの全体に、同じアロケータを渡してくれる。"
order: 900
tags:
  - メモリ
---

# std::scoped_allocator_adaptor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

`vector<string>` のように入れ子のコンテナで、外側の `vector` に渡したアロケータは、中の `string` には自動では渡りません。`scoped_allocator_adaptor` で包むと、**外側のアロケータを中の要素にも自動で渡して**くれます。

!!! tip "ポイント"
    - 外側のアロケータで、中の要素もまとめて管理したいときに使う。
    - pmr の `polymorphic_allocator` は、この伝播が最初から入っている。
    - ふつうのゲームのコードでは、pmr を使うほうが簡単。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::scoped_allocator_adaptor {#scoped_allocator_adaptor}

```cpp
template <class OuterAlloc, class... InnerAllocs>
class scoped_allocator_adaptor;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `OuterAlloc` | アロケータ | 外側のアロケータ |
| `InnerAllocs...` | アロケータ | 省略可。内側のアロケータ |

- 戻り値: アロケータとして使う
- 計算量: 確保は外側のアロケータに依存


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <scoped_allocator>
#include <string>
#include <vector>

int main() {
  using Alloc = std::scoped_allocator_adaptor<std::allocator<std::string>>;
  std::vector<std::string, Alloc> v;
  v.emplace_back("a");
  std::println("{}", v[0]);
}
```

```text title="実行結果"
a
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 入れ子の vector / string を同じ領域で確保する | `std::vector<std::string, std::scoped_allocator_adaptor<MyAlloc<std::string>>>` |

## よくあるミス

??? failure "pmr を使えば足りる場面で使う"
    pmr のコンテナなら、同じ目的を [`pmr`](../memory/pmr.md) だけで書けて簡単です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`polymorphic_allocator`](pmr/polymorphic_allocator.md) | 最初から伝播する |
| [`allocator`](allocator.md) | 普通のアロケータ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入れ子の要素にもアロケータを渡す
    - [x] pmr のほうが簡単
    - [x] <scoped_allocator>

## 関連ページ

- [cpprefjp: std::scoped_allocator_adaptor](https://cpprefjp.github.io/reference/scoped_allocator/scoped_allocator_adaptor.html)
- [cppreference: std::scoped_allocator_adaptor](https://en.cppreference.com/w/cpp/memory/scoped_allocator_adaptor)
