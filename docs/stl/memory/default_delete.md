---
title: std::default_delete
summary: "unique_ptr が既定で使う、`delete` を呼ぶだけの削除関数。"
order: 24
tags:
  - メモリ
---

# std::default_delete

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::unique_ptr<T>` は、破棄のとき、何かに頼んで中身を解放します。その既定の担当が `std::default_delete<T>` です。`delete p` を呼ぶだけの関数オブジェクトで、配列用の `default_delete<T[]>` は `delete[] p` を呼びます。

!!! tip "ポイント"
    - `unique_ptr` の既定のデリーター
    - `operator()(T* p)` で `delete p`
    - 配列用の特殊化 `default_delete<T[]>` は `delete[] p`
    - 自作のデリーターが要らないなら、指定しない

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::default_delete {#default_delete}

<span class="ver ver-11">C++11</span>

```cpp
template <class T> struct default_delete {
  constexpr default_delete() noexcept = default;
  void operator()(T* ptr) const;
};
template <class T> struct default_delete<T[]> {
  template <class U> void operator()(U* ptr) const;
};
```

状態を持たない空の型なので、`unique_ptr` の大きさが増えません（空基底の最適化）。

`unique_ptr<T, 独自のデリーター>` では、デリーターの型が `unique_ptr` の型に入ります。ファイルの `fclose` や、ハンドルの解放関数を指定するときに、独自のデリーターを書きます。

不完全型に対しても使えますが、`operator()` の呼び出し時点で完全型でないと、`static_assert` に失敗します。`unique_ptr` を前方宣言の型で持つ（pImpl）ときは、デストラクターを `.cpp` に書きます。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  ~Tracer() { --alive; }
};

int main() {
  // 手で呼ぶと、delete と同じ
  Tracer* p = new Tracer;
  std::println("作った: {}", Tracer::alive);
  std::default_delete<Tracer>()(p);
  std::println("解放した: {}", Tracer::alive);

  // 配列用は delete[]
  Tracer* arr = new Tracer[3];
  std::println("作った: {}", Tracer::alive);
  std::default_delete<Tracer[]>()(arr);
  std::println("解放した: {}", Tracer::alive);

  std::println("大きさが増えない: {}", sizeof(std::unique_ptr<int>) == sizeof(int*));
}
```

```text title="実行結果"
作った: 1
解放した: 0
作った: 3
解放した: 0
大きさが増えない: true
```

## ゲームでの使いどころ

普段は意識しません。独自のデリーターの書き方の見本として知っておきます。

## よくあるミス

??? failure "unique_ptr<T> に new T[n] を渡す"
    `delete` で解放されて壊れます。`unique_ptr<T[]>` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unique_ptr`](../utilities/unique_ptr.md) | 使う側 |
| `std::make_unique` | 作る関数 |
| `std::shared_ptr` のデリーター | 型に含まれない |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::default_delete](https://cpprefjp.github.io/reference/memory/default_delete.html)
- [cppreference: std::default_delete](https://en.cppreference.com/w/cpp/memory/default_delete)
