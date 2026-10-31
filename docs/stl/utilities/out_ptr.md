---
title: std::out_ptr
summary: "C のAPI が「ポインターのポインター」で返すオブジェクトを、スマートポインターで受け取る。"
order: 76
tags:
  - ユーティリティ
---

# std::out_ptr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <memory>`
</div>

C 言語の API には、`void Create(Thing** out)` のように、生成したオブジェクトのポインタを、ポインタのポインタ（出力引数）で返すものが多くあります。これを `std::unique_ptr<Thing>` で受けたいとき、`Thing* raw; Create(&raw); ptr.reset(raw);` と、生ポインタを経由する手間と、書き忘れによるリークの危険があります。`std::out_ptr(ptr)` は、スマート ポインタを、`T**` として渡せる形に変換して、API の呼び出しが終わったら、自動で `reset` します。

!!! tip "ポイント"
    - `Create(std::out_ptr(ptr))` のように、C の API の出力引数に渡す
    - 式の終わりに、受け取ったポインタが `ptr` に入る（`reset`）
    - 古い値は先に解放される。`ptr` が持っていたものは、`Create` の前に破棄される
    - C++23

!!! info "このページを読む前に"
    [`std::unique_ptr`](unique_ptr.md) と、カスタム デリーターを先に読んでください。

## 関数の詳しい説明

### std::out_ptr {#out_ptr}

<span class="ver ver-23">C++23</span>

```cpp
template <class Pointer = void, class Smart, class... Args>
auto out_ptr(Smart& s, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | スマート ポインタ | 受け取り先 |
| `args` | 任意 | `reset` に追加で渡す引数（`shared_ptr` のデリーターなど） |

戻り値は、`Pointer*`（既定では `s` の `pointer` 型へのポインタ）に暗黙変換できる、アダプターです。呼び出しの前に、`s` が持っていた対象は解放されます。C の関数が書き込んだポインタが、アダプターの破棄時（式の終わり）に、`s.reset(ptr, args...)` で入ります。

`std::inout_ptr` との違いは、API が既存の値を読むかどうかです。`out_ptr` は、API が新しい値を書くだけで、古い値は先に捨てます。`inout_ptr` は、API が古い値を読み、解放して置き換える場合です。

デリーターは、`unique_ptr` の型で決まります。C のライブラリが確保したものは、そのライブラリの解放関数を、デリーターに設定した `unique_ptr` で受けます。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <memory>
#include <print>

// C 風の API: 確保して、ポインタを出力引数で返す
int CreateBuffer(int** out) {
  *out = static_cast<int*>(std::malloc(sizeof(int)));
  **out = 42;
  return 0;
}

// 解放関数をデリーターにする
struct FreeDeleter {
  void operator()(int* p) const { std::free(p); }
};

int main() {
  std::unique_ptr<int, FreeDeleter> p;
  CreateBuffer(std::out_ptr(p));  // 式が終わると p に入る
  std::println("{}", *p);
}
```

```text title="実行結果"
42
```

`CreateBuffer` が書き込んだポインタが、式の終わりに `p` に入り、`p` の破棄時に `free` で解放されます。

## ゲームでの使いどころ

ゲーム エンジンが使う C のライブラリ（画像、サウンド、物理）の出力引数を受けるときに使います。COM の `CreateXxx(&ptr)` の形にも、`ComPtr` の `GetAddressOf` のような専用の方法があるので、そちらを使います。

## よくあるミス

??? failure "式の途中で ptr を使う"
    アダプターが破棄されるまで（式の終わりまで）、`ptr` には値が入りません。同じ式の中で `*p` を使わないようにします。

??? failure "デリーターを設定し忘れる"
    解放関数が違うと、`delete` で解放しようとして、壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`inout_ptr`](inout_ptr.md) | API が古い値を読む場合 |
| `unique_ptr::reset` | 手動で入れ替える |
| `ComPtr::GetAddressOf` | COM の同様の仕組み |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::out_ptr](https://cpprefjp.github.io/reference/memory/out_ptr.html)
- [cppreference: std::out_ptr](https://en.cppreference.com/w/cpp/memory/out_ptr_t)
