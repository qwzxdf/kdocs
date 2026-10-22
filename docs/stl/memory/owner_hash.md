---
title: std::owner_hash
summary: "shared_ptr / weak_ptr を、持ち主（制御ブロック）で数えたハッシュ値を作る。"
order: 900
tags:
  - メモリ
---

# std::owner_hash

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <memory>`
</div>

`shared_ptr` を `unordered_map` のキーにするとき、普通のハッシュは**指している先のアドレス**で決まります。同じ持ち主でも、別のポインタ（エイリアス）を指すと別のキー扱いになります。`owner_hash` は**持ち主（制御ブロック）**を基準にハッシュを作ります。

!!! tip "ポイント"
    - `shared_ptr` と `weak_ptr` の両方に使え、同じ持ち主なら同じ値になる。
    - `unordered_map` のキーに `weak_ptr` を使うときに、[`owner_equal`](owner_equal.md) とセットで使う。

!!! info "このページを読む前に"
    [`std::shared_ptr`](../utilities/shared_ptr.md) を先に読んでください。

## 関数の詳しい説明

### std::owner_hash {#owner_hash}

```cpp
struct owner_hash {
  template <class T> size_t operator()(const shared_ptr<T>&) const noexcept;
  template <class T> size_t operator()(const weak_ptr<T>&) const noexcept;
  using is_transparent = void;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | shared_ptr / weak_ptr | ハッシュを作りたいポインタ |

- 戻り値: 持ち主に対して決まる `size_t`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  auto a = std::make_shared<int>(1);
  std::weak_ptr<int> w = a;
  std::println("{}", std::owner_hash{}(a) == std::owner_hash{}(w));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `weak_ptr` をキーにした表 | `std::unordered_map<std::weak_ptr<T>, V, std::owner_hash, std::owner_equal>` |

## よくあるミス

??? failure "通常の `hash` と取り違える"
    `std::hash<std::shared_ptr<T>>` は指している先のアドレスで決まります。持ち主基準にしたいときに限って `owner_hash` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`owner_less`](owner_less.md) | 持ち主基準の順序 |
| [`owner_equal`](owner_equal.md) | 持ち主基準の比較 |

## コンパイラ対応

C++26 の機能です。新しい標準ライブラリで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 持ち主基準のハッシュ
    - [x] shared_ptr と weak_ptr で同じ値
    - [x] owner_equal とセット

## 関連ページ

- [cpprefjp: std::owner_hash](https://cpprefjp.github.io/reference/memory/owner_hash.html)
- [cppreference: std::owner_hash](https://en.cppreference.com/w/cpp/memory/owner_hash)
