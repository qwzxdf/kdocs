---
title: std::owner_equal
summary: "shared_ptr / weak_ptr が、同じ持ち主（制御ブロック）かを比べる。"
order: 900
tags:
  - メモリ
---

# std::owner_equal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <memory>`
</div>

`shared_ptr` を `==` で比べると「指している先が同じか」です。ところが、同じ持ち主を共有しつつ別の場所を指す（エイリアス）場合は、持ち主が同じかどうかを別に調べたくなります。`owner_equal` が、持ち主基準の比較を `shared_ptr` と `weak_ptr` の間でもできるようにします。

!!! tip "ポイント"
    - `shared_ptr` と `weak_ptr` を混ぜて比べられる。
    - [`owner_hash`](owner_hash.md) とセットで、連想コンテナのキーに使う。

!!! info "このページを読む前に"
    [`std::shared_ptr`](../utilities/shared_ptr.md) を先に読んでください。

## 関数の詳しい説明

### std::owner_equal {#owner_equal}

```cpp
struct owner_equal {
  template <class T, class U> bool operator()(const shared_ptr<T>&, const shared_ptr<U>&) const noexcept;
  template <class T, class U> bool operator()(const weak_ptr<T>&, const weak_ptr<U>&) const noexcept;
  using is_transparent = void;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a, b` | shared_ptr / weak_ptr | 比べる 2 つ |

- 戻り値: 同じ持ち主なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  auto a = std::make_shared<int>(1);
  std::weak_ptr<int> w = a;
  auto b = std::make_shared<int>(1);
  std::println("{}", std::owner_equal{}(a, w));
  std::println("{}", std::owner_equal{}(a, b));
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `weak_ptr` が指していた持ち主かを調べる | `std::owner_equal{}(shared, weak)` |

## よくあるミス

??? failure "`==` と取り違える"
    `==` は指している先、`owner_equal` は持ち主です。エイリアスのときに結果が変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`owner_less`](owner_less.md) | 持ち主基準の順序 |
| [`owner_hash`](owner_hash.md) | 持ち主基準のハッシュ |

## コンパイラ対応

C++26 の機能です。新しい標準ライブラリで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 持ち主基準の等しさ
    - [x] shared_ptr と weak_ptr で比べられる
    - [x] owner_hash とセット

## 関連ページ

- [cpprefjp: std::owner_equal](https://cpprefjp.github.io/reference/memory/owner_equal.html)
- [cppreference: std::owner_equal](https://en.cppreference.com/w/cpp/memory/owner_equal)
