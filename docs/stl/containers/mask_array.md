---
title: std::mask_array
summary: "valarray から、bool の配列（マスク）で選んだ要素への参照。"
order: 900
tags:
  - コンテナ
---

# std::mask_array

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <valarray>`
</div>

`std::valarray` の要素のうち、条件に合うものだけを書き換えたい。たとえば「3 より大きい要素を 0 にする」。`v[v > 3] = 0` と書けて、`v > 3` が `valarray<bool>` を作り、それを添字にすると、真の位置だけが選ばれます。その結果が `std::mask_array` です。

!!! tip "ポイント"
    - `v[bool の valarray]` で、真の位置の要素を選ぶ
    - 代入すると、選ばれた要素だけが更新される
    - `v > 3` のように、比較から作れる
    - 選んだ要素を取り出すと、新しい `valarray` になる

!!! info "このページを読む前に"
    [`std::valarray`](valarray.md) を先に読んでください。

## 関数の詳しい説明

### std::mask_array {#mask_array}

```cpp
template <class T> class mask_array;
```

直接作らず、`valarray<T>::operator[](const valarray<bool>&)` の戻り値として得ます。

使える操作は、代入（`=`）と、複合代入（`+=`、`*=` など）です。右辺は、スカラー（`= 0`）か、選ばれた個数と同じ長さの `valarray` で、選ばれた要素だけに適用されます。

選ばれた要素を取り出すには、`const` の `valarray` に `[mask]` を使うと、新しい `valarray` が返ります。

`mask` の大きさは、元の `valarray` と同じでなければなりません。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <valarray>
#include <vector>

int main() {
  std::valarray<int> v = {1, 2, 3, 4, 5, 6};

  // 3 より大きい要素を 0 にする
  v[v > 3] = 0;
  std::println("{}", std::vector<int>(std::begin(v), std::end(v)));

  // 選ばれた要素に、別の valarray の値を順に入れる
  std::valarray<int> w = {10, 20, 30, 40};
  const std::valarray<bool> mask = {true, false, true, false};
  w[mask] = std::valarray<int>{7, 8};
  std::println("{}", std::vector<int>(std::begin(w), std::end(w)));
}
```

```text title="実行結果"
[1, 2, 3, 0, 0, 0]
[7, 20, 8, 40]
```

## ゲームでの使いどころ

大量の数値に、条件つきの一括処理をかけるときに使います。ゲームでは `std::ranges` のフィルターが主です。

## よくあるミス

??? failure "mask の大きさが違う"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirect_array`](indirect_array.md) | 添字の列で選ぶ |
| [`slice`](slice.md) | 等間隔で選ぶ |
| [`valarray`](valarray.md) | 対象 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::mask_array](https://cpprefjp.github.io/reference/valarray/mask_array.html)
- [cppreference: std::mask_array](https://en.cppreference.com/w/cpp/numeric/valarray/mask_array)
