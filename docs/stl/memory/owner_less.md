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

`std::owner_less` は、**`shared_ptr` や `weak_ptr` を、指す先ではなく「管理ブロック（持ち主）」で比べる**関数オブジェクトです。`std::set<std::weak_ptr<T>, std::owner_less<>>` のように、`weak_ptr` を `set` や `map` のキーにするときに使います。同じオブジェクトを管理する `weak_ptr` どうしは、等しいとみなされます。

!!! tip "ポイント"
    - `weak_ptr` は `<` で比べられないので、`set` のキーにするには `owner_less` が必要。
    - `std::owner_less<>`（型の省略）が使いやすい。
    - 同じ持ち主を指す `weak_ptr` は、重複せず 1 つになる。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [所有権（誰が消すのか）](../../basics/ownership.md)（所有権の考え方）

## 関数の詳しい説明

### std::owner_less {#owner_less}

```cpp
template <class T = void>
struct owner_less;
```

- 戻り値: （比較用の関数オブジェクト）
- 計算量: O(1)

```cpp
#include <memory>
#include <print>
#include <set>

int main() {
  auto sp = std::make_shared<int>(1);
  std::weak_ptr<int> a = sp;
  std::weak_ptr<int> b = sp;  // 同じオブジェクトを管理する

  std::set<std::weak_ptr<int>, std::owner_less<>> observers;
  observers.insert(a);
  observers.insert(b);
  std::println("{}", observers.size());
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| オブザーバー（観測者）を weak_ptr で重複なく登録する | `std::set<std::weak_ptr<Listener>, std::owner_less<>>` |

## よくあるミス

??? failure "owner_less を付け忘れる"
    `weak_ptr` に `<` が無いので、コンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::weak_ptr`](../utilities/weak_ptr.md) | 比べる対象 |
| [`std::set`](../containers/set.md) | キーに使う |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 持ち主で比べる
    - [x] weak_ptr を set のキーにする
    - [x] `owner_less<>` が簡単

## 関連ページ

- [cpprefjp: std::owner_less](https://cpprefjp.github.io/reference/memory/owner_less.html)
- [cppreference: std::owner_less](https://en.cppreference.com/w/cpp/memory/owner_less)
