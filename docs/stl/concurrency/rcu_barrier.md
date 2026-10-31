---
title: std::rcu_barrier
summary: "予約された破棄が、すべて終わるまで待つ。"
order: 900
tags:
  - 並行処理
---

# std::rcu_barrier

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <rcu>`
</div>

`rcu_retire` で予約した解放は、別のスレッドが後で実行します。プログラムの終了前や、モジュールの入れ替えの前に、予約した解放が、全部終わったことを確かめたい。`std::rcu_barrier()` は、それまでに予約された解放が、すべて実行されるまで待ちます。

!!! tip "ポイント"
    - 呼んだ時点までに予約された解放が、全部完了するまで待つ
    - 終了処理や、動的ライブラリのアンロード前に使う
    - 読み手の区間の中で呼んではいけない
    - C++26

!!! info "このページを読む前に"
    [`rcu_retire`](rcu_retire.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_barrier {#rcu_barrier}

<span class="ver ver-26">C++26</span>

```cpp
void rcu_barrier(std::rcu_domain& dom = std::rcu_default_domain()) noexcept;
```

`rcu_synchronize` は、読み手の終了を待ちます。`rcu_barrier` は、予約された解放の関数の実行完了まで待ちます。違いは、解放のデリーターが、実際に走り終えたかどうかです。

デリーターが、動的ライブラリ（DLL）の中のコードなら、ライブラリをアンロードする前に、`rcu_barrier` で、予約された解放をすべて終わらせます。終わらせないと、アンロード後にそのコードを呼んでしまいます。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
void Shutdown() {
  // 予約された解放が、すべて終わるのを待つ
  std::rcu_barrier();
  // これ以降は、DLL をアンロードしてもよい
}
```

## ゲームでの使いどころ

ゲームの終了処理や、プラグインのアンロードの前に、予約済みの解放を終わらせるときに使います。

## よくあるミス

??? failure "barrier を呼ばずにアンロードする"
    予約された解放が、消えたコードを呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_retire`](rcu_retire.md) | 解放を予約する |
| [`rcu_synchronize`](rcu_synchronize.md) | 読み手の終了を待つ |
| [`rcu_domain`](rcu_domain.md) | ドメイン |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::rcu_barrier](https://cpprefjp.github.io/reference/rcu/rcu_barrier.html)
- [cppreference: std::rcu_barrier](https://en.cppreference.com/w/cpp/thread/rcu_barrier)
