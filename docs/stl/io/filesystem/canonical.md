---
title: std::filesystem::canonical
summary: "パスを正規化する（`..` やリンクを解決する）。"
order: 21
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::canonical

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

パスは、同じファイルを指すのに、いくらでも書き方があります。`data/../data/./hero.png` も `data/hero.png` も、同じファイルです。ログに出す、重複を調べる、キャッシュのキーにする、という場面では、1 つの決まった形にそろえたくなります。

`std::filesystem::canonical` は、パスを<strong>絶対パスにして、`.` と `..` を取り除き、シンボリックリンクをたどった先の本当の場所</strong>に直して返します。

!!! tip "ポイント"
    - 結果は、必ず絶対パスで、`.`、`..`、シンボリックリンクを含まない
    - パスが実在していないとエラーになる。存在しない部分があるなら `weakly_canonical`
    - ファイルシステムに問い合わせるので、`lexically_normal` のような文字列だけの処理より遅い
    - 同じファイルを指すパスは、同じ `canonical` の結果になる。キーとして使いやすい

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### canonical {#canonical}

<span class="ver ver-17">C++17</span>

```cpp
path canonical(const path& p);
path canonical(const path& p, const path& base);
path canonical(const path& p, std::error_code& ec);
path canonical(const path& p, const path& base, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 正規化するパス。実在している必要がある |
| `base` | `const path&` | `p` が相対パスのときの基準。省略するとカレント ディレクトリ |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`p` が相対パスなら、`base / p` として扱います。そのうえで、`.` を消し、`..` を 1 つ上のフォルダーに解決し、途中にシンボリックリンクがあれば、指し先に置き換えます。

[`absolute`](absolute.md) との違いは、`absolute` が文字列の上で絶対パスにするだけで、ファイルシステムに問い合わせず、`..` も消さないことです。`canonical` は、実際にフォルダーをたどるので、<strong>パスの途中が 1 つでも存在しなければ失敗</strong>します。存在しない部分を含むパスを正規化したいときは、[`weakly_canonical`](weakly_canonical.md) を使います。

Windows では、大文字と小文字が違う書き方（`DATA` と `data`）も、実際のフォルダー名に合わせた綴りに直るのがふつうです。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directory("data");
  std::ofstream("data/hero.png") << "x";

  // 回りくどい書き方でも、同じ実体なら canonical は同じ結果になる
  fs::path a = fs::canonical("data/../data/./hero.png");
  fs::path b = fs::canonical("data/hero.png");
  std::println("同じ結果: {}", a == b);
  std::println("絶対パス: {}", a.is_absolute());
  std::println("ファイル名: {}", a.filename().string());

  // 存在しないパスはエラー
  std::error_code ec;
  fs::path c = fs::canonical("data/none.png", ec);
  std::println("存在しない: 空={} エラー={}", c.empty(), static_cast<bool>(ec));
}
```

```text title="実行結果"
同じ結果: true
絶対パス: true
ファイル名: hero.png
存在しない: 空=true エラー=true
```

## ゲームでの使いどころ

アセットのキャッシュのキーに使います。`textures/hero.png`、`./textures/hero.png`、`textures/../textures/hero.png` のように、読み込みの呼び出しごとに表記が違っても、`canonical` を通せば同じ文字列になるので、`unordered_map` のキーとして使えます。

ログに、読み込んだファイルの本当の場所を出したいときや、ユーザーが指定した出力先が、ゲームのインストール フォルダーの中かどうかを調べるときにも使います。

存在しないファイル（これから作る保存先など）を扱うなら、`weakly_canonical` です。

## よくあるミス

??? failure "これから作るファイルを渡して、例外になる"
    `canonical` は実在しないパスを受け付けません。保存先のようにまだ無いものには、`weakly_canonical`、または親フォルダーに `canonical` を使います。

??? failure "毎フレーム呼んで、重くなる"
    ファイルシステムに問い合わせるので、ホット パスでは呼びません。読み込み時に 1 回だけ正規化して、結果を持っておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weakly_canonical`](weakly_canonical.md) | 存在しない部分があってもよい版 |
| [`absolute`](absolute.md) | 文字列の上で絶対パスにするだけ。問い合わせず、`..` も消さない |
| [`equivalent`](equivalent.md) | 2 つのパスが同じ実体かを調べる |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 絶対パスにして `.` `..` とリンクを解決する
    - [x] 実在しないとエラー
    - [x] キャッシュのキーにしやすい

## 関連ページ

- [cpprefjp: std::filesystem::canonical](https://cpprefjp.github.io/reference/filesystem/canonical.html)
- [cppreference: std::filesystem::canonical](https://en.cppreference.com/w/cpp/filesystem/canonical)
