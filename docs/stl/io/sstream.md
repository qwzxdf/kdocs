---
title: std::stringstream
tags:
  - 入出力
  - 文字列
---

# std::stringstream

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++98〜</span>
`#include <sstream>`
</div>

`std::stringstream` は、**文字列をファイルや画面の代わりにして `<<` / `>>` を使える型**です。`std::ostringstream` に `<<` で書き込めば文字列ができあがり、`std::istringstream` に文字列を入れれば `>>` や `std::getline` で分解して読めます。ファイルの読み込み処理をテストするときや、1 行の中身を空白で分けて数値に変換するときに便利です。

!!! tip "ポイント"
    - 文字列を**作る**のは C++20 以降なら [`std::format`](../utilities/format.md) のほうが簡単。ostringstream は古いコードで見かける。
    - 文字列を**分解して読む**のは istringstream が今でも便利（`"3 4 5"` → 3, 4, 5）。
    - ファイル用の関数を `std::istream&` で受け取るようにすると、テストで istringstream を渡せる。
    - 作るたびにメモリ確保があるので、毎フレーム大量に使うものではない。

## 主な型

| 型 | 重要度 | 何をする |
| --- | --- | --- |
| `std::istringstream` | <span class="rank rank-sometimes">たまに</span> | 文字列から読む（`>>`、`getline`） |
| `std::ostringstream` | <span class="rank rank-sometimes">たまに</span> | 文字列に書く（`<<`） |
| `std::stringstream` | <span class="rank rank-sometimes">たまに</span> | 両方 |
| `std::spanstream` | <span class="rank rank-rare">知ってるだけ</span> | 既にあるバッファを読み書き（確保しない） <span class="ver ver-23">C++23</span> |

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [コンストラクタ](#constructor) | <span class="rank rank-sometimes">たまに</span> | 文字列を入れて作る |
| [`str`](#str) | <span class="rank rank-sometimes">たまに</span> | 中の文字列を取り出す・入れ替える |
| [`operator>>`](#shift-in) | <span class="rank rank-sometimes">たまに</span> | 空白区切りで値を読む |
| [`operator<<`](#shift-out) | <span class="rank rank-sometimes">たまに</span> | 値を書き込む |
| [`std::getline`](#getline) | <span class="rank rank-sometimes">たまに</span> | 区切り文字まで読む |
| [`view`](#view) | <span class="rank rank-rare">知ってるだけ</span> | 中の文字列をコピーせずに見る <span class="ver ver-20">C++20</span> |
| [`clear`](#clear) | <span class="rank rank-rare">知ってるだけ</span> | エラー状態を消す |

## よくある使い方

### 1. 1 行を分解して読む

```cpp
#include <print>
#include <sstream>
#include <string>

int main() {
  std::string line = "spawn goblin 120 340";
  std::istringstream ss(line);

  std::string command;
  std::string name;
  int x = 0;
  int y = 0;
  ss >> command >> name >> x >> y;
  std::println("{} {} at ({}, {})", command, name, x, y);
}
```

```text title="実行結果"
spawn goblin at (120, 340)
```

### 2. カンマ区切りを分ける

```cpp
#include <print>
#include <sstream>
#include <string>
#include <vector>

int main() {
  std::istringstream ss("sword,shield,potion");
  std::vector<std::string> items;
  std::string item;
  while (std::getline(ss, item, ',')) {
    items.push_back(item);
  }
  std::println("{}", items);
}
```

```text title="実行結果"
["sword", "shield", "potion"]
```

### 3. 読み込み処理をファイル無しでテストする

```cpp
#include <istream>
#include <print>
#include <sstream>
#include <vector>

// ifstream でも istringstream でも受け取れる
std::vector<int> LoadScores(std::istream& in) {
  std::vector<int> scores;
  int s = 0;
  while (in >> s) {
    scores.push_back(s);
  }
  return scores;
}

int main() {
  std::istringstream fake_file("10 20 30");
  std::println("{}", LoadScores(fake_file));
}
```

```text title="実行結果"
[10, 20, 30]
```

## 関数の詳しい説明

### コンストラクタ {#constructor}

```cpp
explicit istringstream(const std::string& str);
explicit ostringstream(std::ios::openmode mode = std::ios::out);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const std::string&` | 読むための中身 |
| `mode` | `openmode` | `std::ios::ate` を付けると、最初の中身の後ろに追記する |

### str {#str}

```cpp
std::string str() const;
void str(const std::string& s);
```

- 引数なしで、中の文字列のコピーを返します。引数ありで、中身を入れ替えます

### operator>> {#shift-in}

```cpp
std::istream& operator>>(int& value);  // 型ごとにある
```

- 空白を飛ばして次の値を読みます。読めなければ失敗状態になります

### operator<< {#shift-out}

```cpp
std::ostream& operator<<(int value);  // 型ごとにある
```

- 値を文字にして後ろに書き足します

```cpp
#include <print>
#include <sstream>

int main() {
  std::ostringstream os;
  os << "HP " << 45 << '/' << 120;
  std::println("[{}]", os.str());
  os.str("");  // 中身を空にして使い回す
  os << "reset";
  std::println("[{}]", os.str());
}
```

```text title="実行結果"
[HP 45/120]
[reset]
```

### std::getline {#getline}

```cpp
std::istream& getline(std::istream& in, std::string& str, char delim = '\n');
```

- `delim` の手前までを読みます。区切り文字を `','` にすると CSV の列を分けられます

### view {#view}

<span class="ver ver-20">C++20</span>

```cpp
std::string_view view() const noexcept;
```

- 中の文字列をコピーせずに見ます。ストリームを変更すると無効になります

### clear {#clear}

```cpp
void clear(std::ios::iostate state = std::ios::goodbit);
```

- エラー状態を消します。**中身は消えません**（中身を空にするのは `str("")`）

```cpp
#include <print>
#include <sstream>
#include <string_view>

int main() {
  std::istringstream in("abc");
  int n = 0;
  in >> n;
  std::println("失敗？ {}", in.fail());
  in.clear();
  std::println("失敗？ {} / 中身 {}", in.fail(), in.view());
}
```

```text title="実行結果"
失敗？ true
失敗？ false / 中身 abc
```

## フラグ・オプション

書式のフラグ（`std::hex`、`std::setprecision` など）は [iostream](iostream.md#フラグオプション書式フラグとマニピュレータ) と同じです。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    std::ostringstream os;
    os << "Lv." << level << " " << name;
    std::string title = os.str();
    ```

=== "今の書き方（C++20）"

    ```cpp
    std::string title = std::format("Lv.{} {}", level, name);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| コマンドの解析 | デバッグコンソールの `spawn goblin 120 340` |
| CSV の 1 行を分ける | `getline(ss, cell, ',')` |
| 読み込み処理のテスト | ファイルの代わりに istringstream を渡す |

## よくあるミス

??? failure "clear で中身が消えると思う"
    `clear()` はエラー状態を消すだけです。中身を空にするのは `str("")` です。

??? failure "文字列を作るのに使い続ける"
    `std::format` のほうが短く、速いことが多いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](../utilities/format.md) | 文字列を作るならこちら |
| [`std::views::split`](../algorithms/views.md#split) | 区切って分けるだけなら速い |
| [`std::from_chars`](charconv.md) | 数値への変換だけなら速くて例外も無い |

## コンパイラ対応

C++98 からある機能です。`view()` は C++20、`spanstream` は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 分解して読むなら istringstream
    - [x] 作るなら std::format
    - [x] 関数を `std::istream&` で受けるとテストしやすい

## 関連ページ

- [std::ifstream / ofstream](fstream.md)
- [cppreference: std::basic_stringstream](https://en.cppreference.com/w/cpp/io/basic_stringstream)
