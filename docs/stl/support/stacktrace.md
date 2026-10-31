---
title: std::stacktrace
summary: "呼び出し履歴（スタックトレース）を取得する。"
order: 2
tags:
  - 型・言語サポート
---

# std::stacktrace

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-23">C++23</span>
`#include <stacktrace>`
</div>

想定外のエラーが起きたとき、「この関数はどこから呼ばれたのか」を、ログに残したいことがあります。デバッガーをつないでいない、利用者の手元のクラッシュ調査では特にそうです。`std::stacktrace` は、今の呼び出し履歴（どの関数がどの関数を呼んだか）を取得して、保存・表示できるクラスです。

!!! tip "ポイント"
    - `std::stacktrace::current()` で、今の履歴を取得する
    - 取得のコストは大きい（数十マイクロ秒以上）ので、毎フレーム取らない
    - 行番号や関数名は、デバッグ情報（PDB など）があるときだけ意味のある値になる
    - 最適化でインライン展開された関数は、履歴に現れないことがある

!!! info "このページを読む前に"
    [`std::source_location`](source_location.md)（呼び出し位置を表す型）を先に読んでおくと、行番号やファイル名の話が分かりやすくなります。

## 関数の詳しい説明

### current {#current}

<span class="ver ver-23">C++23</span>

```cpp
static basic_stacktrace current(const allocator_type& alloc = allocator_type()) noexcept;
static basic_stacktrace current(size_type skip, const allocator_type& alloc = allocator_type()) noexcept;
static basic_stacktrace current(size_type skip, size_type max_depth, const allocator_type& alloc = allocator_type()) noexcept;
```

| 引数 | 意味 |
| --- | --- |
| `skip` | 履歴の先頭（今の関数）から、読み飛ばす個数 |
| `max_depth` | 取得する履歴の最大の個数。深い再帰で、履歴が長くなりすぎるのを防ぐ |
| `alloc` | 履歴を保存するメモリを確保するアロケーター |

`current()` を呼んだ関数が、履歴の 0 番目です。その呼び出し元が 1 番目、さらにその呼び出し元が 2 番目、と続き、一番外側（`main` を呼んだランタイムの関数など）で終わります。

`skip` は、ログを出す専用の関数の中で `current()` を呼ぶときに便利です。ログ関数自身は履歴に要らないので、`current(1)` と書いて、飛ばします。

`max_depth` は、履歴を保存する量の上限です。深い再帰の中で取ると、履歴が数千段になり、ログが読めず、取得も重くなります。

履歴を取得する関数は `noexcept` ですが、メモリを確保できなかったときや、取得に失敗したときは、空の履歴が返ります。

### size と empty {#size}

```cpp
size_type size() const noexcept;
bool empty() const noexcept;
size_type max_size() const noexcept;
```

履歴の段数を返します。取得に失敗したときは、`empty()` が `true` になります。ログに出す前に、`empty()` を確認すると、空のログを防げます。

### operator[] と at {#at}

```cpp
const_reference operator[](size_type i) const;
const_reference at(size_type i) const;
```

`i` 番目の段を、[`stacktrace_entry`](stacktrace_entry.md) として返します。`operator[]` は範囲を検査せず、`at` は範囲外で `std::out_of_range` を投げます。

### begin と end {#begin}

```cpp
const_iterator begin() const noexcept;
const_iterator end() const noexcept;
```

履歴を、範囲 for で順にたどれます。要素は `stacktrace_entry` です。逆向き（`rbegin` / `rend`）や、`cbegin` / `cend` もあります。

### to_string と println {#to_string}

```cpp
std::string to_string(const basic_stacktrace& st);   // <stacktrace>
```

履歴を、1 段ごとに改行した文字列にします。`std::println("{}", trace)` のように、書式指定の `{}` にそのまま渡すこともできます（C++23）。

### operator== と hash {#compare}

```cpp
bool operator==(const basic_stacktrace& a, const basic_stacktrace& b) noexcept;
template <> struct std::hash<std::stacktrace>;
```

2 つの履歴が、すべての段で等しいかを比べます。`std::hash` もあるので、`unordered_map` のキーにして、「同じ場所から呼ばれたエラーを数える」ような使い方ができます。

## 実際に動かしてみる

```cpp
#include <print>
#include <stacktrace>
#include <string>

// n 段の再帰の底で、履歴の段数を数える
std::size_t Depth(int n) {
  if (n == 0) return std::stacktrace::current().size();
  return Depth(n - 1);
}

int main() {
  std::stacktrace now = std::stacktrace::current();
  std::println("履歴は空ではない: {}", !now.empty());

  // 3 段深く呼ぶと、履歴も 3 段増える
  std::println("3 段深いと 3 段増える: {}", Depth(3) == Depth(0) + 3);

  // skip で先頭 (今の関数) を飛ばす
  std::stacktrace skipped = std::stacktrace::current(1);
  std::println("skip=1 で 1 段減る: {}", skipped.size() + 1 == now.size());

  // max_depth で上限を決める
  std::stacktrace limited = std::stacktrace::current(0, 2);
  std::println("max_depth=2 で 2 段まで: {}", limited.size() == 2);

  // 範囲 for で段数を数える
  std::size_t count = 0;
  for (const std::stacktrace_entry& e : now) {
    (void)e;
    ++count;
  }
  std::println("範囲 for の段数が size と同じ: {}", count == now.size());

  std::println("文字列にできる: {}", !std::to_string(now).empty());
  std::println("同じ履歴は等しい: {}", now == now);
}
```

```text title="実行結果"
履歴は空ではない: true
3 段深いと 3 段増える: true
skip=1 で 1 段減る: true
max_depth=2 で 2 段まで: true
範囲 for の段数が size と同じ: true
文字列にできる: true
同じ履歴は等しい: true
```

## ゲームでの使いどころ

想定外の状態（`assert` が外れた、不正なデータを読んだ）を見つけたときに、履歴をログに残して、あとで原因を追えるようにします。利用者の手元のクラッシュ報告に添えると、再現できない不具合の手がかりになります。

## よくあるミス

??? failure "毎フレーム取得する"
    取得は重い処理です。エラーが起きたときだけ取ります。

??? failure "デバッグ情報なしで行番号を期待する"
    行番号やファイル名は、PDB などのデバッグ情報が必要です。リリース ビルドでも情報を残す設定が要ります。

??? failure "最適化後の履歴を、ソースの呼び出しと同じと思う"
    インライン展開や末尾呼び出しの最適化で、履歴から関数が消えることがあります。

??? failure "GCC でリンクを忘れる"
    GCC は `-lstdc++exp`（GCC 13 / 14）か `-lstdc++`（GCC 15 以降）のリンクが要ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stacktrace_entry`](stacktrace_entry.md) | 履歴の 1 段 |
| [`basic_stacktrace`](basic_stacktrace.md) | アロケーターを変えられる版 |
| [`source_location`](source_location.md) | コンパイル時の呼び出し位置 |

## コンパイラ対応

C++23 です。MSVC は Visual Studio 2022 17.4 以降、GCC 12 以降（リンクの設定が要る）、Clang は標準ライブラリの対応状況に依存します。

## 関連ページ

- [cpprefjp: std::stacktrace](https://cpprefjp.github.io/reference/source_location/stacktrace.html)
- [cppreference: std::stacktrace](https://en.cppreference.com/w/cpp/utility/stacktrace)
