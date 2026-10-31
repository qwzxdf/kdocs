---
title: std::chrono::reload_tzdb
summary: "タイムゾーンのデータベースを、最新のものに読み込み直す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::reload_tzdb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

OS が新しいタイムゾーンのデータベースを配布していても、実行中のプログラムは、起動時の古い版を使い続けます。長期間動かすサーバーが、最新の規則を取り込むには、`std::chrono::reload_tzdb` を呼びます。更新があれば、新しい版が `tzdb_list` の先頭に足されます。

!!! tip "ポイント"
    - OS の最新版が現在の版より新しければ、読み込んで一覧に足す
    - 戻り値は、更新後の最新の `tzdb` への参照
    - 更新がなければ、何もしない
    - 古い版は消えず、以前の参照は有効なまま

!!! info "このページを読む前に"
    [`tzdb_list`](tzdb_list.md) と [`remote_version`](remote_version.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::reload_tzdb {#reload_tzdb}

<span class="ver ver-20">C++20</span>

```cpp
const tzdb& reload_tzdb();
```

OS の最新のデータベースの版（`remote_version()` が返すもの）と、現在の版（`get_tzdb().version`）を比べます。違えば、新しく読み込み、`tzdb_list` の先頭に追加して、その参照を返します。同じなら、現在の版の参照を、そのまま返します。

呼び出しは、重い処理です。ディスクやネットワークの入出力が起きることがあります。ゲームのメイン スレッドでなく、別のスレッドや、起動時と定期的なタイミングで呼びます。

`reload_tzdb` は、`get_tzdb_list()` を通してアクセスされる一覧を更新するだけで、すでに作った `zoned_time` の中のゾーンの情報は、古い版を指したままです。更新を反映するには、`zoned_time` を作り直します。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const tzdb& before = get_tzdb();
  const tzdb& after = reload_tzdb();

  // 更新があってもなくても、最新の版は空でない
  std::println("版がある: {}", !after.version.empty());

  // 更新がなければ同じ版
  std::println("版は同じか新しい: {}", after.version >= before.version);
}
```

```text title="実行結果"
版がある: true
版は同じか新しい: true
```

実行のたびに OS の状況が違うので、更新があったかは表示していません。

## ゲームでの使いどころ

何週間も動かすオンライン ゲームのサーバーで、定期的に呼びます。夏時間の規則の変更が、ゲーム内のイベントの時刻に響かないようにします。

## よくあるミス

??? failure "メイン スレッドのフレーム内で呼ぶ"
    入出力で止まる可能性があります。別のスレッドで呼びます。

??? failure "更新後も古い zoned_time を使う"
    以前に作ったものは、古い版を指しています。作り直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_tzdb`](get_tzdb.md) | 現在の版を取る（読み直さない） |
| [`remote_version`](remote_version.md) | OS の最新版の名前だけ調べる |
| [`tzdb_list`](tzdb_list.md) | 版の履歴 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: reload_tzdb](https://cpprefjp.github.io/reference/chrono/reload_tzdb.html)
- [cppreference: std::chrono::reload_tzdb](https://en.cppreference.com/w/cpp/chrono/reload_tzdb)
