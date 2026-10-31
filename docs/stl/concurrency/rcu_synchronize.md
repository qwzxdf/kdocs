---
title: std::rcu_synchronize
summary: "読み取り中のスレッドがいなくなるまで待つ。"
order: 900
tags:
  - 並行処理
---

# std::rcu_synchronize

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <rcu>`
</div>

RCU で古いデータを解放するには、「その古いデータを読んでいた読み手が、全員読み終えた」ことを確かめる必要があります。`std::rcu_synchronize()` は、呼んだ時点で区間にいる全読み手が、区間を出るまで待ちます。待ったあとなら、古いデータを、安全に解放できます。

!!! tip "ポイント"
    - 呼んだ時点で区間にいる読み手が、全員出るまで待つ
    - その後に始まった読み手は、待たない
    - 呼び出し側が止まる。長くかかることがある
    - ブロックしたくなければ `rcu_retire`

!!! info "このページを読む前に"
    [`rcu_domain`](rcu_domain.md) を先に読んでください。

## 関数の詳しい説明

### std::rcu_synchronize {#rcu_synchronize}

<span class="ver ver-26">C++26</span>

```cpp
void rcu_synchronize(std::rcu_domain& dom = std::rcu_default_domain()) noexcept;
```

書き手は、(1) 新しいデータに差し替える、(2) `rcu_synchronize` で、古いデータの読み手が消えるのを待つ、(3) 古いデータを解放する、の順に進めます。

読み手の区間の中で、`rcu_synchronize` を呼んではいけません。自分自身を待って、デッドロックします。

待たずに済ませたいなら、解放を予約する `rcu_retire` を使います。予約された解放は、別のスレッドが実行します。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
void Update(std::atomic<Config*>& slot, Config* fresh) {
  Config* old = slot.exchange(fresh);   // 新しいデータに差し替える
  std::rcu_synchronize();               // 古いデータの読み手が消えるのを待つ
  delete old;                           // 安全に解放できる
}
```

## ゲームでの使いどころ

設定の更新のように、まれに起きる更新で、古いデータを確実に解放するときに使います。

## よくあるミス

??? failure "読み手の区間の中で呼ぶ"
    デッドロックします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rcu_retire`](rcu_retire.md) | 待たずに解放を予約する |
| [`rcu_barrier`](rcu_barrier.md) | 予約した解放の完了を待つ |
| [`rcu_domain`](rcu_domain.md) | ドメイン |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::rcu_synchronize](https://cpprefjp.github.io/reference/rcu/rcu_synchronize.html)
- [cppreference: std::rcu_synchronize](https://en.cppreference.com/w/cpp/thread/rcu_synchronize)
