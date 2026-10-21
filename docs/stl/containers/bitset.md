---
title: std::bitset
summary: "固定長のビット列。フラグをまとめて持つ。1 ビットずつのオン・オフを少ないメモリで。"
order: 15
tags:
  - コンテナ
---

# std::bitset

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++98〜</span>
`#include <bitset>`
</div>

`std::bitset` は、**決まった個数の on / off（ビット）をまとめて持つ型**です。`bool` を N 個並べるのと同じことを、1 個 1 ビットに詰めてコンパクトに持ちます。ビット演算（`&`, `|`, `^`）で全部まとめて操作でき、「何個 on か」もすぐ数えられます。

!!! tip "ポイント"
    - <strong>個数が決まっているフラグの集まりに使う。</strong> 押されているキー、取得済みアイテム（ID が小さい整数）、当たり判定のレイヤーなど。
    - 書き方は `std::bitset<64> flags;` → `flags.set(3)` / `flags.test(3)` / `flags.reset(3)`。
    - `&` `|` でまとめて判定できる（「必要なフラグが全部立っているか」など）。
    - 個数が実行時に決まるなら `std::vector<bool>` か `std::vector<char>`。

!!! info "このページを読む前に"
    2 進数とビット演算（`&`, `|`, `^`, `~`）を知っていると読みやすいです。

## 宣言

```cpp
template <std::size_t N>
class bitset;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `N` | ビット数。コンパイル時の定数 | 必ず |

### 作り方

| 書き方 | 重要度 | 結果 |
| --- | --- | --- |
| `std::bitset<8> b;` | <span class="rank rank-must">必須</span> | 全部 0 |
| `std::bitset<8> b(0b1010);` | <span class="rank rank-sometimes">たまに</span> | 整数から（下位ビットから入る） |
| `std::bitset<8> b("1010");` | <span class="rank rank-sometimes">たまに</span> | 文字列から（右端がビット 0） |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`set`](#set) | <span class="rank rank-must">必須</span> | ビットを 1 にする | O(1) |
| [`test`](#test) | <span class="rank rank-must">必須</span> | ビットが 1 か（範囲チェックあり） | O(1) |
| [`reset`](#reset) | <span class="rank rank-must">必須</span> | ビットを 0 にする | O(1) |
| [`operator[]`](#operator) | <span class="rank rank-often">よく使う</span> | 読み書き（範囲チェックなし） | O(1) |
| [`operator&`](#and) | <span class="rank rank-often">よく使う</span> | 両方 1 のビットだけ 1 | O(N/64) |
| [`operator\|`](#or) | <span class="rank rank-often">よく使う</span> | どちらかが 1 なら 1 | O(N/64) |
| [`count`](#count) | <span class="rank rank-often">よく使う</span> | 1 の個数 | O(N/64) |
| [`any`](#any) | <span class="rank rank-often">よく使う</span> | どれか 1 つでも 1 か | O(N/64) |
| [`none`](#none) | <span class="rank rank-often">よく使う</span> | 全部 0 か | O(N/64) |
| [`all`](#all) | <span class="rank rank-often">よく使う</span> | 全部 1 か | O(N/64) |
| [`operator~`](#not) | <span class="rank rank-sometimes">たまに</span> | 全ビット反転した新しい bitset | O(N/64) |
| [`operator^`](#xor) | <span class="rank rank-sometimes">たまに</span> | 違うビットだけ 1 | O(N/64) |
| [`flip`](#flip) | <span class="rank rank-sometimes">たまに</span> | ビットを反転 | O(1) |
| [`size`](#size) | <span class="rank rank-sometimes">たまに</span> | ビット数（= N） | O(1) |
| [`to_ullong`](#to_ullong) | <span class="rank rank-sometimes">たまに</span> | 整数に変換（セーブ用） | O(1) |
| [`to_string`](#to_string) | <span class="rank rank-sometimes">たまに</span> | `"0101..."` に変換（デバッグ用） | O(N) |
| [`to_ulong`](#to_ulong) | <span class="rank rank-rare">知ってるだけ</span> | unsigned long に変換 | O(1) |
| [`operator<<`](#shl) | <span class="rank rank-rare">知ってるだけ</span> | 左シフト | O(N/64) |
| [`operator>>`](#shr) | <span class="rank rank-rare">知ってるだけ</span> | 右シフト | O(N/64) |
| [`operator==`](#eq) | <span class="rank rank-rare">知ってるだけ</span> | 等しいか | O(N/64) |

## よくある使い方

### 1. フラグを立てて調べる

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<8> items;  // アイテム ID 0〜7 を持っているか
  items.set(1);
  items.set(4);
  items.set(6);

  std::println("ID 4 を持っている？ {}", items.test(4));
  std::println("持っている数: {}", items.count());

  items.reset(4);  // 使った
  std::println("{}", items.to_string());
}
```

```text title="実行結果"
ID 4 を持っている？ true
持っている数: 3
01000010
```

`to_string` は**右端がビット 0** です。

### 2. 必要なフラグが全部そろっているか

```cpp
#include <bitset>
#include <print>

enum Key { kRedKey, kBlueKey, kGreenKey, kKeyCount };

int main() {
  std::bitset<kKeyCount> have;
  have.set(kRedKey);
  have.set(kGreenKey);

  std::bitset<kKeyCount> door_needs;
  door_needs.set(kRedKey);
  door_needs.set(kBlueKey);

  // 必要なものを全部持っているか: (持ち物 & 必要) == 必要
  bool can_open = (have & door_needs) == door_needs;
  std::println("開けられる？ {}", can_open);

  // 足りないもの
  std::println("足りない: {}", (door_needs & ~have).to_string());
}
```

```text title="実行結果"
開けられる？ false
足りない: 010
```

## 関数の詳しい説明

### set {#set}

```cpp
bitset& set() noexcept;
bitset& set(std::size_t pos, bool value = true);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| （なし） | | 全部 1 にする |
| `pos` | `std::size_t` | ビットの位置（0 始まり） |
| `value` | `bool` | 入れる値。`false` を渡すと 0 になる |

- 例外: `pos >= N` なら `std::out_of_range`

<div class="anim" data-label="b.set(2)">
0 0 0 0 # b（右から 0 番目）
0 +1 0 0 # 2 番目のビットを 1 にする
</div>

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<8> b;
  b.set(0);
  b.set(3);
  b.set(5, false);  // 0 にする
  std::println("{}", b.to_string());
  b.set();  // 全部 1
  std::println("{}", b.to_string());
}
```

```text title="実行結果"
00001001
11111111
```

### test {#test}

```cpp
bool test(std::size_t pos) const;
```

- 戻り値: `pos` 番目が 1 なら `true`
- 例外: `pos >= N` なら `std::out_of_range`

<div class="anim" data-label="b.test(2)">
0 1 0 1 # b
0 *1 0 1 # 2 番目が 1 なら true
</div>

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<4> b("0100");
  std::println("{} {}", b.test(2), b.test(0));
}
```

```text title="実行結果"
true false
```

### reset {#reset}

```cpp
bitset& reset() noexcept;
bitset& reset(std::size_t pos);
```

- 引数なしで全部 0、`pos` を指定するとそのビットだけ 0

<div class="anim" data-label="b.reset(2)">
0 1 0 0 # b
0 x1 0 0 # 2 番目のビットを 0 にする
0 0 0 0 # 完了
</div>

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<4> b("1111");
  b.reset(1);
  std::println("{}", b.to_string());
  b.reset();
  std::println("{}", b.to_string());
}
```

```text title="実行結果"
1101
0000
```

### operator[] {#operator}

```cpp
bool operator[](std::size_t pos) const;
reference operator[](std::size_t pos);
```

- 読み書きできます。**範囲チェックなし**（範囲外は未定義動作）

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<4> b;
  b[2] = true;
  std::println("{} {}", static_cast<bool>(b[2]), b.to_string());
}
```

```text title="実行結果"
true 0100
```

### operator& {#and}

```cpp
bitset operator&(const bitset& lhs, const bitset& rhs) noexcept;
bitset& operator&=(const bitset& rhs) noexcept;
```

- 両方 1 のビットだけ 1 になります。「共通部分」「マスク」に使います

### operator| {#or}

```cpp
bitset operator|(const bitset& lhs, const bitset& rhs) noexcept;
bitset& operator|=(const bitset& rhs) noexcept;
```

- どちらかが 1 なら 1 になります。「まとめて立てる」に使います

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<4> a("1100");
  std::bitset<4> b("1010");
  std::println("& = {} / | = {}", (a & b).to_string(), (a | b).to_string());
}
```

```text title="実行結果"
& = 1000 / | = 1110
```

### count {#count}

```cpp
std::size_t count() const noexcept;
```

- 1 のビットの数。CPU の専用命令で一気に数えるので速いです

<div class="anim" data-label="b.count()">
1 0 1 1 # b
*1 0 *1 *1 # 1 のビットを数える（3）
</div>

### any {#any}

```cpp
bool any() const noexcept;
```

- どれか 1 つでも 1 なら `true`

### none {#none}

```cpp
bool none() const noexcept;
```

- 全部 0 なら `true`

### all {#all}

```cpp
bool all() const noexcept;
```

- 全部 1 なら `true`

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<3> keys("101");
  std::println("count {} / any {} / none {} / all {}", keys.count(), keys.any(),
               keys.none(), keys.all());
}
```

```text title="実行結果"
count 2 / any true / none false / all false
```

### operator~ {#not}

```cpp
bitset operator~() const noexcept;
```

- 全ビットを反転した**新しい** bitset を返します（自分は変わらない）

<div class="anim" data-label="~b">
1 0 1 1 # b
>0 >1 >0 >0 # 反転した新しい bitset
</div>

### operator^ {#xor}

```cpp
bitset operator^(const bitset& lhs, const bitset& rhs) noexcept;
```

- 違うビットだけ 1。「前のフレームから変化したフラグ」を調べるのに使えます

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<4> prev("0110");
  std::bitset<4> now("0011");
  std::println("変化 {} / 押された {} / 離された {}", (prev ^ now).to_string(),
               (now & ~prev).to_string(), (prev & ~now).to_string());
}
```

```text title="実行結果"
変化 0101 / 押された 0001 / 離された 0100
```

!!! note "実際は"
    入力処理で「今フレーム押された」「今フレーム離された」を作る定番の書き方です。

### flip {#flip}

```cpp
bitset& flip() noexcept;
bitset& flip(std::size_t pos);
```

- 引数なしで全部反転、`pos` を指定するとそのビットだけ反転（自分が変わる）

<div class="anim" data-label="b.flip()">
1 0 1 1 # b
>0 >1 >0 >0 # すべてのビットを反転する
</div>

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<4> lights("0001");
  lights.flip(3);  // スイッチを押すたびに切り替わる
  std::println("{}", lights.to_string());
}
```

```text title="実行結果"
1001
```

### size {#size}

```cpp
constexpr std::size_t size() const noexcept;
```

- ビット数。常に `N`

### to_ullong {#to_ullong}

```cpp
unsigned long long to_ullong() const;
```

- 整数に変換します。例外: 64 ビットに入りきらない 1 があると `std::overflow_error`

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<16> flags;
  flags.set(0);
  flags.set(4);
  unsigned long long saved = flags.to_ullong();  // セーブデータに保存
  std::bitset<16> loaded(saved);                 // 読み込み
  std::println("{} {}", saved, loaded == flags);
}
```

```text title="実行結果"
17 true
```

### to_string {#to_string}

```cpp
std::string to_string(char zero = '0', char one = '1') const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `zero` / `one` | `char` | 0 と 1 に使う文字 |

- **右端がビット 0** です

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<8> row("10110001");
  std::println("{}", row.to_string('.', '#'));
}
```

```text title="実行結果"
#.##...#
```

### to_ulong {#to_ulong}

```cpp
unsigned long to_ulong() const;
```

- `to_ullong` の unsigned long 版。Windows では 32 ビットなので、`to_ullong` を使うほうが安全です

### operator<< {#shl}

```cpp
bitset operator<<(std::size_t pos) const noexcept;
bitset& operator<<=(std::size_t pos) noexcept;
```

- 全体を `pos` ビット**左**（上位ビット側）にずらします。はみ出したビットは消え、空いた所は 0 になります

### operator>> {#shr}

```cpp
bitset operator>>(std::size_t pos) const noexcept;
bitset& operator>>=(std::size_t pos) noexcept;
```

- 全体を `pos` ビット**右**（下位ビット側）にずらします

```cpp
#include <bitset>
#include <print>

int main() {
  std::bitset<4> b("0011");
  std::println("{} {}", (b << 1).to_string(), (b >> 1).to_string());
}
```

```text title="実行結果"
0110 0001
```

### operator== {#eq}

```cpp
bool operator==(const bitset& rhs) const noexcept;
```

- 全ビットが同じなら `true`

## フラグ・オプション

フラグはありません。

## 計算量まとめ

1 ビットの操作は O(1)、全体の操作は O(N/64)（64 ビットずつまとめて処理）です。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 押されているキー | `std::bitset<256>`（キーコードを添字に） |
| 取得済み・達成済み | 実績、宝箱、ステージクリア |
| 当たり判定のレイヤー | 「プレイヤーの弾は敵とだけ当たる」をマスクで判定 |
| ECS のコンポーネント構成 | どのコンポーネントを持っているかをビットで持つ |

## パフォーマンス

- `bool` 1 個は 1 バイトですが、bitset なら 1 ビットなので 8 分の 1 のメモリで済みます。
- ヒープを使いません。
- 「全部」「どれか」の判定がとても速いです。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 範囲外の `[]` | 未定義動作 |
| 範囲外の `set` / `reset` / `test` | `std::out_of_range` 例外 |
| `to_ulong` で入りきらない | `std::overflow_error` 例外 |

## よくあるミス

??? failure "to_string の向きを逆に読む"
    `std::bitset<4>(0b0001).to_string()` は `"0001"` です。右端がビット 0 なので、配列の添字とは見た目の順番が逆です。

??? failure "個数を実行時に決めようとする"
    `std::bitset<n>` の `n` は定数でないといけません。実行時に決まるなら `std::vector<bool>` を使います。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| `std::vector<bool>` | 個数が実行時に変わる。ビット演算はない | 個数が決まっていない |
| [`std::unordered_set<int>`](unordered_set.md) | 値の範囲が大きくても使える | ID が大きい・まばら |
| `enum class` + 整数のビット演算 | 自分でマスクを書く | API にそのまま渡すフラグ |
| [`std::array<bool, N>`](array.md) | 1 要素 1 バイト。参照が取れる | 要素ごとの参照・ポインタが欲しい |

## コンパイラ対応

C++98 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 決まった個数のフラグをビットで持つ
    - [x] `set` / `test` / `reset`、まとめて `&` `|`
    - [x] `count` / `any` / `all` で一気に判定
    - [x] `to_string` は右端がビット 0

## 関連ページ

- [cpprefjp: std::bitset](https://cpprefjp.github.io/reference/bitset/bitset.html)
- [cppreference: std::bitset](https://en.cppreference.com/w/cpp/utility/bitset)
