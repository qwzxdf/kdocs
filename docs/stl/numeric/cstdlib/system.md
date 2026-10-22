---
title: std::system
summary: "OS のコマンドを実行する。"
order: 900
tags:
  - 数値
---

# std::system

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

外部のコマンド（`dir` や `ls` など）を実行して、終了コードを受け取ります。ゲームの本編では使いませんが、開発用ツールで使うことがあります。引数の文字列がそのままシェルに渡るので、外部から入力された値を使うと危険です。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::system {#system}

```cpp
int system(const char* command);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `command` | const char* | 実行するコマンド（`nullptr` でシェルの有無を確認） |

- 戻り値: コマンドの終了コード（処理系による）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  // 例: int code = std::system("echo hello");
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 開発ツールからコマンドを呼ぶ |

## よくあるミス

??? failure "入力された文字列をそのまま渡す"
    シェルのコマンドとして解釈されるため、コマンド注入の危険があります。ユーザー入力を直接渡さないでください。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::filesystem`](../../io/filesystem.md) | ファイル操作は専用の API で |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] OS のコマンドを実行する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::system](https://cpprefjp.github.io/reference/cstdlib/system.html)
- [cppreference: std::system](https://en.cppreference.com/w/cpp/c/system)
