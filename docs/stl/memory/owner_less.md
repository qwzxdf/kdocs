---
title: std::owner_less
summary: "shared_ptr / weak_ptr を、「管理の持ち主」で並べ替える比較。"
order: 23
tags:
  - メモリ
---

# std::owner_less

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::shared_ptr` を `std::map` のキーにしたい。`shared_ptr` の `<` は、指す先のポインターの大小で比べますが、`weak_ptr` には `<` がありません。`std::owner_less` は、ポインターの値ではなく、<strong>制御ブロック（所有権）の大小</strong>で比べる比較関数オブジェクトで、`shared_ptr` と `weak_ptr` の両方を、キーにできます。

!!! tip "ポイント"
    - 所有権（制御ブロック）の大小で比べる
    - 同じ所有権を共有する `shared_ptr` と `weak_ptr` は、等価
    - `std::map<std::weak_ptr<T>, V, std::owner_less<>>` のように使う
    - エイリアシング コンストラクターで作ったポインターも、同じ所有権なら等価

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::owner_less {#owner_less}

<span class="ver ver-11">C++11</span>

```cpp
template <class T = void> struct owner_less;
```

`owner_less<>`（透過的な比較）が、`shared_ptr` と `weak_ptr` のどの組み合わせでも比べられます。

通常の `shared_ptr` の `<` は、`get()` が返すポインターで比べます。エイリアシング コンストラクターで、別のアドレスを指す `shared_ptr` を作ると、同じ所有権を共有していても、`<` では別物として扱われます。`owner_less` なら同じ物です。

`weak_ptr` は期限切れになっても、制御ブロックの順序は変わらないので、キーとして安全です。ポインターの値で比べると、期限切れの扱いが問題になります。

## 実際に動かしてみる

```cpp
#include <map>
#include <memory>
#include <print>

int main() {
  auto a = std::make_shared<int>(1);
  auto b = std::make_shared<int>(2);

  // weak_ptr をキーにした map
  std::map<std::weak_ptr<int>, const char*, std::owner_less<>> names;
  names[a] = "a";
  names[b] = "b";
  std::println("要素数: {}", names.size());

  // 同じ所有権の shared_ptr でも検索できる
  std::println("a の名前: {}", names.find(a)->second);

  // 同じ所有権を共有していれば、等価
  std::shared_ptr<int> a2 = a;
  std::println("等価: {}", !std::owner_less<>()(a, a2) && !std::owner_less<>()(a2, a));
}
```

```text title="実行結果"
要素数: 2
a の名前: a
等価: true
```

## ゲームでの使いどころ

オブジェクトを `weak_ptr` で管理する表（オブジェクトから付随情報を引く）を作るときに使います。

## よくあるミス

??? failure "weak_ptr をそのままキーにする"
    `<` がないのでコンパイルできません。`owner_less` を指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`owner_hash`](owner_hash.md) | ハッシュ版（C++26） |
| [`owner_equal`](owner_equal.md) | 等値版（C++26） |
| [`shared_ptr`](../utilities/shared_ptr.md) | 対象 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::owner_less](https://cpprefjp.github.io/reference/memory/owner_less.html)
- [cppreference: std::owner_less](https://en.cppreference.com/w/cpp/memory/owner_less)
