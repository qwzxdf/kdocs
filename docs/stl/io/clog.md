---
title: std::clog
summary: "標準のログ出力（cerr と同じ出力先で、バッファあり）。"
order: 900
tags:
  - 入出力・文字列
---

# std::clog

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`cerr` は、書くたびに送り出されるので、ログを大量に出すと遅くなります。`std::clog` は、`cerr` と同じ標準エラー出力に出ますが、バッファに溜めてから送り出します。エラーではないが標準出力にも混ぜたくない、診断用のログを出すためのストリームです。

!!! tip "ポイント"
    - `cerr` と同じ標準エラー出力に出る。バッファあり（`unitbuf` がオフ）
    - `cout` や `cerr` と違い、画面に出るのが遅れることがある。落ちる直前の出力は残らないことがある
    - `cout` と結び付いていない（`tie` がない）
    - 残したいメッセージには、`cerr` か、`std::flush` を使う

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::clog {#clog}

```cpp
extern std::ostream clog;
```

`<iostream>` を読み込むと使える、グローバルなストリームです。出力先は `cerr` と同じ C の `stderr` で、設定が違います。

| | `cout` | `cerr` | `clog` |
| --- | --- | --- | --- |
| 出力先 | 標準出力 | 標準エラー出力 | 標準エラー出力 |
| `unitbuf` | オフ | **オン** | オフ |
| `tie`（先に `cout` を送り出す） | なし | **あり** | なし |

`clog` に書いた内容は、バッファがいっぱいになるか、`flush` を呼ぶか、プログラムが正常に終わるときに送り出されます。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  std::println("clog: unitbuf={} tie={}",
               (std::clog.flags() & std::ios::unitbuf) != 0, std::clog.tie() != nullptr);

  // 出力先を差し替えて、書いた内容を取り出す
  std::ostringstream captured;
  auto* old = std::clog.rdbuf(captured.rdbuf());
  std::clog << "warn: テクスチャが大きすぎる\n";
  std::clog.rdbuf(old);
  std::print("取り出した: {}", captured.str());
}
```

```text title="実行結果"
clog: unitbuf=false tie=false
取り出した: warn: テクスチャが大きすぎる
```

`unitbuf` も `tie` もないのは、`cout` と同じです。出力先が標準エラー出力であることだけが、`cout` と違います。

## ゲームでの使いどころ

デバッグ ビルドの診断ログ（読み込んだアセットの数、フレームの時間など）を出すときです。通常の出力（`cout`）に混ぜずに、リダイレクトで分けられます。1 回ごとに送り出さないので、`cerr` よりログを大量に出せます。

ただし、クラッシュすると、バッファに溜まっていた最後の数行が失われます。クラッシュの調査に使うログは、`clog` ではなく、ファイル ストリームに `unitbuf` を付けるか、`cerr` に出します。

## よくあるミス

??? failure "クラッシュする直前のログが、画面に出ていない"
    `clog` はバッファに溜めるので、落ちる前に送り出されませんでした。重要な行のあとで、`std::flush` を流すか、`cerr` を使います。

??? failure "`cout` と `clog` を混ぜたら、出力の順番が入れ替わった"
    `clog` には `tie` がなく、`cout` のバッファとは別に溜まります。順番を保ちたいなら、`cerr`（`cout` を先に送り出す）を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cerr`](cerr.md) | 同じ出力先で、書くたびに送り出す |
| [`cout`](cout.md) | 標準出力に出る |
| [`wclog`](wclog.md) | `wchar_t` 版 |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `clog` は、`cerr` と同じ標準エラー出力に出る、バッファありのストリーム
    - [x] `unitbuf` も `tie` もないので、大量のログに向くが、落ちる直前の分は失われうる
    - [x] 確実に残したいメッセージは、`cerr` か `flush` で出す

## 関連ページ

- [cpprefjp: std::clog](https://cpprefjp.github.io/reference/iostream/clog.html)
- [cppreference: std::clog](https://en.cppreference.com/w/cpp/io/clog)
