---
title: std::filesystem::directory_entry
summary: "フォルダを回して得られる、1 つの項目（パスと情報）。"
order: 7
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::directory_entry

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

フォルダの中のファイルを順に調べながら、それぞれがファイルかフォルダか、サイズはどれくらいか、といった情報も知りたい。パスだけを受け取って、毎回 `file_size(path)` や `is_directory(path)` を呼ぶと、そのたびにファイルシステムへ問い合わせることになります。`std::filesystem::directory_entry` は、フォルダを回したときの 1 つの項目で、パスのほかに、種類やサイズなどをキャッシュして持っています。

!!! tip "ポイント"
    - `path()` でパス、`is_regular_file()` `is_directory()` で種類、`file_size()` でサイズ。
    - 情報はキャッシュされるので、別途 `fs::file_size` を呼ぶより速いことがある。

!!! info "このページを読む前に"
    [`directory_iterator`](directory_iterator.md) を先に読んでください。`directory_entry` は、そのイテレーターが返す要素です。

## 関数の詳しい説明

### directory_entry {#directory_entry}

```cpp
class directory_entry;
```

| メンバ | 何をする |
| --- | --- |
| `path()` | パス |
| `is_regular_file()` / `is_directory()` | 種類 |
| `file_size()` | 大きさ |
| `last_write_time()` | 更新日時 |
| `exists()` | まだあるか |

- フォルダを回したときに取れる情報をまとめて持っているので、`fs::file_size(entry.path())` より `entry.file_size()` のほうが速いことがあります

### assign {#assign}

```cpp
void assign(const path& p);
```

- 計算量: 定数

別のパスを割り当てて、キャッシュをクリアします。

### replace_filename {#replace_filename}

```cpp
void replace_filename(const path& p);
```

- 計算量: 定数

ファイル名を置き換えて、キャッシュをクリアします。

### refresh {#refresh}

```cpp
void refresh();
```

- 計算量: OS に依存

キャッシュしている状態（サイズ・更新時刻など）をいま調べ直します。走査のあとでファイルが変わった可能性があるときに使います。

### path {#path}

```cpp
const path& path() const noexcept;
operator const path&() const noexcept;
```

- 計算量: 定数

エントリのパスを返します。`directory_iterator` で回したときに、ファイルの名前を取り出すのに使います。

### exists {#exists}

```cpp
bool exists() const;
```

- 計算量: キャッシュがあれば定数

存在するか。走査中に取得した情報のキャッシュを使うので、`fs::exists(p)` より速いことがあります。

### is_regular_file {#is_regular_file}

```cpp
bool is_regular_file() const;
```

- 計算量: キャッシュがあれば定数

通常のファイルか。

### is_directory {#is_directory}

```cpp
bool is_directory() const;
```

- 計算量: キャッシュがあれば定数

フォルダか。再帰的に走査するときの判定に使います。

### is_symlink {#is_symlink}

```cpp
bool is_symlink() const;
```

- 計算量: キャッシュがあれば定数

シンボリックリンクか。

### is_other {#is_other}

```cpp
bool is_other() const;
```

- 計算量: キャッシュがあれば定数

通常ファイル・フォルダ・リンクのどれでもない特殊なファイルか。

### file_size {#file_size}

```cpp
std::uintmax_t file_size() const;
```

- 計算量: キャッシュがあれば定数

ファイルの大きさ（バイト）。走査中のキャッシュを使うことがあります。

### hard_link_count {#hard_link_count}

```cpp
std::uintmax_t hard_link_count() const;
```

- 計算量: OS に依存

ハードリンクの数。

### last_write_time {#last_write_time}

```cpp
file_time_type last_write_time() const;
```

- 計算量: キャッシュがあれば定数

最後に書き込まれた時刻。

### status {#status}

```cpp
file_status status() const;
```

- 計算量: キャッシュがあれば定数

ファイルの種類と権限（リンクをたどる）。

### symlink_status {#symlink_status}

```cpp
file_status symlink_status() const;
```

- 計算量: キャッシュがあれば定数

ファイルの種類と権限（リンクをたどらない）。

### operator== {#op_eq}

```cpp
bool operator==(const directory_entry& rhs) const noexcept;
```

- 計算量: O(長さ)

パスが等しければ `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
auto operator<=>(const directory_entry& rhs) const noexcept;
```

- 計算量: O(長さ)

パスで比べる三方比較。

## しくみ

`directory_iterator` で回すと、各項目が `directory_entry` として返ります。OS によっては、フォルダの一覧を取る時点で、ファイルの種類や、サイズなどの一部の情報も一緒に取れるので、それをキャッシュして持っています。

`is_regular_file()`、`is_directory()`、`file_size()` などは、このキャッシュを使って答えます。別途 `fs::file_size(path)` を呼ぶより、システムへの問い合わせが減ります。ただし、キャッシュは取得した時点の情報なので、その後ファイルが変わっても反映されません。最新にするには `refresh()` を呼びます。

`directory_entry` は、パスに暗黙に変換できます。`fs::path p = entry;` と書けるので、`path` を受け取る関数にそのまま渡せます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("de_demo");
  std::ofstream("de_demo/a.txt") << "x";
  for (const auto& e : fs::directory_iterator("de_demo")) {
    std::println("{} {}", e.path().filename().generic_string(), e.is_regular_file());
  }
  fs::remove_all("de_demo");
}
```

```text title="実行結果"
a.txt true
```

## ゲームでの使いどころ

アセットフォルダの内容を調べるときに使います。

```cpp
for (const auto& entry : fs::directory_iterator("assets")) {
  if (entry.is_regular_file() && entry.path().extension() == ".png") {
    // 画像ファイルとして読み込む
  }
}
```

ファイルの更新時刻を調べて、ホットリロード（ファイルが変わったら読み直す）に使うこともあります。`entry.last_write_time()` で更新時刻を取り、前回の値と比べます。

サイズが大きいファイルを先に調べたり、容量の合計を出したりするときも、`file_size()` を使います。

## よくあるミス

??? failure "キャッシュが古くて、最新の情報と違う"
    `entry` が持つ情報は、取得した時点のものです。ファイルが書き換えられても、自動では更新されません。最新の値が必要なら `refresh()` を呼びます。

??? failure "ファイルとフォルダを区別せずに開こうとする"
    フォルダを `ifstream` で開こうとして失敗します。`entry.is_regular_file()` で、ファイルだけを対象にします。

??? failure "例外で落ちる"
    権限のないファイルの情報を取ろうとすると、例外が投げられます。`std::error_code` を渡す版を使うと、例外なしで結果を受け取れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`directory_iterator`](directory_iterator.md) | フォルダの直下を回す。この項目を返す |
| [`recursive_directory_iterator`](recursive_directory_iterator.md) | サブフォルダも含めて回す |
| [`path`](path.md) | パスだけを持つ。`entry.path()` で取り出せる |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダを回して得られる 1 つの項目。パスと情報を持つ。
    - [x] 種類やサイズはキャッシュされる。最新にするには `refresh()`。
    - [x] `path` にそのまま変換できる。

## 関連ページ

- [cpprefjp: std::filesystem::directory_entry](https://cpprefjp.github.io/reference/filesystem/directory_entry.html)
- [cppreference: std::filesystem::directory_entry](https://en.cppreference.com/w/cpp/filesystem/directory_entry)
