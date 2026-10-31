---
title: std::filesystem::space
summary: "ディスクの空き容量を取得する。"
order: 23
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::space

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

セーブ データを書き込む前に、ディスクの空きが足りるか確かめたい。ダウンロードしたアセットを展開する前に、容量を調べたい。書き込みの途中でディスクが一杯になると、壊れたセーブ ファイルが残ってしまうからです。

`std::filesystem::space` は、パスが乗っているボリューム（ドライブやパーティション）の<strong>全体の容量、空き容量、現在のユーザーが使える空き容量</strong>を、`space_info` として返します。

!!! tip "ポイント"
    - パスに指定するのは、調べたいボリューム上の既存のパス。ファイルでもフォルダーでもよい
    - 返る `space_info` は、`capacity`（全体）、`free`（空き）、`available`（使える空き）の 3 つ
    - ユーザーごとの容量制限（クォータ）があると、`available` は `free` より小さくなる
    - 調べた後に書き込むまでの間に、空きは変わりうる。結果は目安で、保証ではない

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### space {#space}

<span class="ver ver-17">C++17</span>

```cpp
space_info space(const path& p);
space_info space(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べたいボリューム上に実在するパス。そのボリュームのルート（`C:\` など）でも、中のファイルでもよい |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先。渡すと例外を投げない |

戻り値の [`space_info`](space_info.md) は、バイト数を `std::uintmax_t` で持つ 3 つのメンバーです。`capacity` はボリュームの総容量、`free` は空きの合計、`available` は<strong>今のプロセスが使える</strong>空きです。ふつうのデスクトップの単独ユーザーでは、`free` と `available` はほぼ同じ値になります。

保存前の判定には、`free` ではなく `available` を使います。サーバーや共有マシンのように、ユーザーごとに容量制限が掛かる環境では、`free` が十分あっても、書き込めないことがあるからです。

パスが存在しないときは、例外（または `ec` のエラー）になります。ネットワーク ドライブなど、情報を取れないボリュームでは、各メンバーが `static_cast<std::uintmax_t>(-1)` になることがあります。この値は「不明」を表すので、そのまま「とても大きい空き」と受け取らないでください。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::space_info info = fs::space(fs::current_path());

  // 値はマシンごとに違うので、関係だけを確かめる
  std::println("全体 >= 空き: {}", info.capacity >= info.free);
  std::println("空き >= 使える空き: {}", info.free >= info.available);

  // 100 MB 以上の空きがあれば保存してよい、という判定
  const std::uintmax_t need = 100ull * 1024 * 1024;
  std::println("保存してよい: {}", info.available >= need);
}
```

```text title="実行結果"
全体 >= 空き: true
空き >= 使える空き: true
保存してよい: true
```

## ゲームでの使いどころ

大きなセーブ データやスクリーンショットを保存する前に、`available` が必要な量より大きいかを確かめ、足りなければ「ディスクの空きが足りません」とプレイヤーに知らせます。何も言わずに書き込みを失敗させるより、ずっと親切です。

ダウンロード コンテンツの展開や、シェーダー キャッシュの作成の前にも使えます。必要量は、展開後の合計サイズに余裕（1 割程度）を足しておきます。

ただし、確認してから書き込むまでの間に、他のプログラムが容量を使うことがあります。この判定は「ほぼ大丈夫」の確認で、書き込み自体の失敗は、別に処理します。

## よくあるミス

??? failure "`free` を見て保存したのに、容量制限で失敗した"
    `free` はボリューム全体の空きです。現在のユーザーが使える量は `available` なので、保存可否の判定にはこちらを使います。

??? failure "存在しないフォルダーを渡して例外になる"
    保存先のフォルダーを先に作ってから調べるか、存在する親フォルダーを渡します。ボリュームが同じなら、結果は同じです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`space_info`](space_info.md) | この関数が返す構造体。3 つのメンバーの意味はこちら |
| [`file_size`](file_size.md) | ファイル 1 つの大きさ。ボリュームの容量ではない |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボリュームの容量と空きを調べる
    - [x] 保存の判定には `available` を使う
    - [x] 調べた後に変わりうる

## 関連ページ

- [cpprefjp: std::filesystem::space](https://cpprefjp.github.io/reference/filesystem/space.html)
- [cppreference: std::filesystem::space](https://en.cppreference.com/w/cpp/filesystem/space)
