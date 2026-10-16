---
title: std::span
tags:
  - コンテナ
---

# std::span

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-20">C++20</span>
`#include <span>`
</div>

`std::span` は、**どこかにある連続した配列を「借りて見る」ための窓**です。自分では中身を持たず、「先頭のポインタ」と「個数」の 2 つだけを持っています。`std::vector` でも `std::array` でも C の配列でも、同じ `std::span` で受け取れるのが一番の利点です。

!!! tip "結論"
    - **関数の引数で配列を受け取るときに使う。** `const std::vector<T>&` の代わりに `std::span<const T>`。
    - 読むだけなら `std::span<const T>`、書き換えるなら `std::span<T>`。
    - コピーしても中身はコピーされない（ポインタと個数だけ）。**値渡しで OK**。
    - **借りているだけ**なので、元の配列が消えたり再確保されたりすると壊れる。メンバ変数に保存しない。

!!! info "このページを読む前に"
    [`std::vector`](vector.md)、[参照](../../basics/reference.md) が分かると読みやすいです。

## 宣言

```cpp
inline constexpr std::size_t dynamic_extent = std::numeric_limits<std::size_t>::max();

template <class T, std::size_t Extent = std::dynamic_extent>
class span;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 要素の型。読むだけなら `const T` | 必ず |
| `Extent` | 個数。省略すると実行時に決まる | **ほぼしない** |

<div class="mem">
<div class="mem-step"><span class="mem-label">vector の中身</span><span class="mem-cells"><span>10</span><span class="move">20</span><span class="move">30</span><span class="move">40</span><span>50</span></span></div>
<div class="mem-step"><span class="mem-label">span（data, size = 3）</span><span class="mem-note">20 を指すポインタと「3 個」という数字を持つだけ。中身は vector のまま</span></div>
</div>

### 作り方

| 書き方 | 重要度 | 結果 |
| --- | --- | --- |
| 関数の引数に vector / array / C 配列を渡す | <span class="rank rank-must">必須</span> | 自動で span になる |
| `std::span<const int> s = v;` | <span class="rank rank-often">よく使う</span> | `v` 全体 |
| `std::span s(ptr, count);` | <span class="rank rank-sometimes">たまに</span> | ポインタと個数から |
| `std::span<int, 4> s = arr;` | <span class="rank rank-rare">知ってるだけ</span> | 個数がコンパイル時に固定の span |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`operator[]`](#operator) | <span class="rank rank-must">必須</span> | i 番目にアクセス（範囲チェックなし） | O(1) |
| [`size`](#size) | <span class="rank rank-must">必須</span> | 要素数 | O(1) |
| [`begin`](#begin) | <span class="rank rank-must">必須</span> | 先頭のイテレータ（範囲 for で使われる） | O(1) |
| [`end`](#end) | <span class="rank rank-must">必須</span> | 最後の次のイテレータ | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`subspan`](#subspan) | <span class="rank rank-often">よく使う</span> | 途中の一部分を切り出した span | O(1) |
| [`first`](#first) | <span class="rank rank-often">よく使う</span> | 先頭 n 個の span | O(1) |
| [`last`](#last) | <span class="rank rank-often">よく使う</span> | 末尾 n 個の span | O(1) |
| [`data`](#data) | <span class="rank rank-sometimes">たまに</span> | 先頭のポインタ | O(1) |
| [`front`](#front) | <span class="rank rank-sometimes">たまに</span> | 先頭の要素 | O(1) |
| [`back`](#back) | <span class="rank rank-sometimes">たまに</span> | 末尾の要素 | O(1) |
| [`size_bytes`](#size_bytes) | <span class="rank rank-sometimes">たまに</span> | バイト数（`size() * sizeof(T)`） | O(1) |
| [`std::as_bytes`](#as_bytes) | <span class="rank rank-rare">知ってるだけ</span> | `const std::byte` の span として見る | O(1) |
| [`std::as_writable_bytes`](#as_writable_bytes) | <span class="rank rank-rare">知ってるだけ</span> | `std::byte` の span として見る | O(1) |
| [`rbegin`](#rbegin) | <span class="rank rank-rare">知ってるだけ</span> | 逆順の先頭 | O(1) |
| [`rend`](#rend) | <span class="rank rank-rare">知ってるだけ</span> | 逆順の終わり | O(1) |
| [`at`](#at) | <span class="rank rank-rare">知ってるだけ</span> | 範囲チェックあり（C++26） | O(1) |

`push_back` など**要素数を変える関数はありません**。借りているだけなので増やせません。

## よくある使い方

### 1. どの配列でも受け取れる関数

```cpp
#include <array>
#include <print>
#include <span>
#include <vector>

// 読むだけなので const int
int Sum(std::span<const int> values) {
  int total = 0;
  for (int v : values) {
    total += v;
  }
  return total;
}

int main() {
  std::vector<int> a = {1, 2, 3};
  std::array<int, 2> b = {10, 20};
  int c[] = {100, 200, 300, 400};

  std::println("{} {} {}", Sum(a), Sum(b), Sum(c));
}
```

```text title="実行結果"
6 30 1000
```

### 2. 書き換える

```cpp
#include <print>
#include <span>
#include <vector>

void Halve(std::span<float> values) {
  for (float& v : values) {
    v *= 0.5f;
  }
}

int main() {
  std::vector<float> volumes = {1.0f, 0.8f, 0.4f};
  Halve(volumes);
  std::println("{}", volumes);
}
```

```text title="実行結果"
[0.5, 0.4, 0.2]
```

### 3. 一部分だけ渡す

```cpp
#include <print>
#include <span>
#include <vector>

void PrintAll(std::span<const int> values) { std::println("{}", values); }

int main() {
  std::vector<int> v = {0, 1, 2, 3, 4, 5, 6, 7};
  std::span<const int> all = v;

  PrintAll(all.first(3));       // 先頭 3 個
  PrintAll(all.last(2));        // 末尾 2 個
  PrintAll(all.subspan(2, 4));  // 添字 2 から 4 個
}
```

```text title="実行結果"
[0, 1, 2]
[6, 7]
[2, 3, 4, 5]
```

コピーは一切起きていません。

## 関数の詳しい説明

### operator[] {#operator}

```cpp
constexpr reference operator[](size_type idx) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `idx` | `size_type` | 0 始まりの位置 |

- 戻り値: 要素の参照（`span<const T>` なら書き換え不可、`span<T>` なら書き換え可）
- 範囲外は未定義動作

```cpp
#include <print>
#include <span>
#include <vector>

void DoubleFirst(std::span<int> values) { values[0] *= 2; }

int main() {
  std::vector<int> v = {5, 6, 7};
  DoubleFirst(v);
  std::println("{}", v);  // 元の vector が書き換わる
}
```

```text title="実行結果"
[10, 6, 7]
```

### size {#size}

```cpp
constexpr size_type size() const noexcept;
```

- 戻り値: 要素数

### begin {#begin}

```cpp
constexpr iterator begin() const noexcept;
```

- 先頭のイテレータ。範囲 for や `std::ranges::` のアルゴリズムで使われます

### end {#end}

```cpp
constexpr iterator end() const noexcept;
```

- 最後の次のイテレータ

```cpp
#include <algorithm>
#include <print>
#include <span>

int Max(std::span<const int> values) {
  // ranges のアルゴリズムに span をそのまま渡せる（中で begin / end を使う）
  return *std::ranges::max_element(values);
}

int main() {
  int scores[] = {40, 90, 75};
  std::println("{} 個中の最高点: {}", std::span(scores).size(), Max(scores));
}
```

```text title="実行結果"
3 個中の最高点: 90
```

### empty {#empty}

```cpp
constexpr bool empty() const noexcept;
```

- 戻り値: 要素が 0 個なら `true`

```cpp
#include <print>
#include <span>
#include <vector>

void PrintFirst(std::span<const int> values) {
  if (values.empty()) {
    std::println("空です");
    return;
  }
  std::println("{}", values.front());
}

int main() {
  PrintFirst(std::vector<int>{});
  PrintFirst(std::vector<int>{3, 4});
}
```

```text title="実行結果"
空です
3
```

### subspan {#subspan}

```cpp
constexpr span<T> subspan(size_type offset, size_type count = dynamic_extent) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `offset` | `size_type` | 開始位置 |
| `count` | `size_type` | 個数。省略すると最後まで |

- 戻り値: 同じ中身の一部分を指す新しい span（コピーは起きない）
- 範囲外を指定すると未定義動作

```cpp
#include <print>
#include <span>
#include <vector>

int main() {
  std::vector<int> v = {0, 1, 2, 3, 4, 5, 6, 7};
  std::span<const int> all = v;
  std::println("{}", all.subspan(2, 4));  // 添字 2 から 4 個
  std::println("{}", all.subspan(5));     // 添字 5 から最後まで
}
```

```text title="実行結果"
[2, 3, 4, 5]
[5, 6, 7]
```

!!! note "実際は"
    パーティクルを「前半だけこのスレッド、後半だけ別のスレッド」と分けて処理する、といった使い方ができます。

### first {#first}

```cpp
constexpr span<T> first(size_type count) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `count` | `size_type` | 先頭から何個か |

- 戻り値: 先頭 `count` 個を指す span。`count > size()` だと未定義動作

```cpp
#include <print>
#include <span>
#include <vector>

int main() {
  std::vector<int> ranking = {980, 870, 860, 700, 650};
  std::println("トップ 3: {}", std::span(ranking).first(3));
}
```

```text title="実行結果"
トップ 3: [980, 870, 860]
```

### last {#last}

```cpp
constexpr span<T> last(size_type count) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `count` | `size_type` | 末尾から何個か |

- 戻り値: 末尾 `count` 個を指す span

```cpp
#include <print>
#include <span>
#include <vector>

int main() {
  std::vector<float> frame_times = {16.6f, 16.7f, 33.3f, 16.6f, 16.5f};
  std::println("直近 2 フレーム: {}", std::span(frame_times).last(2));
}
```

```text title="実行結果"
直近 2 フレーム: [16.6, 16.5]
```

### data {#data}

```cpp
constexpr pointer data() const noexcept;
```

- 先頭のポインタ。C の API に渡すときに使います

### front {#front}

```cpp
constexpr reference front() const;
```

- 先頭の要素。空のとき未定義動作

### back {#back}

```cpp
constexpr reference back() const;
```

- 末尾の要素。空のとき未定義動作

```cpp
#include <print>
#include <span>

int main() {
  int path[] = {3, 8, 12, 20};
  std::span<const int> s = path;
  std::println("スタート {} / ゴール {}", s.front(), s.back());
}
```

```text title="実行結果"
スタート 3 / ゴール 20
```

### size_bytes {#size_bytes}

```cpp
constexpr size_type size_bytes() const noexcept;
```

- 戻り値: `size() * sizeof(T)`

```cpp
#include <print>
#include <span>
#include <vector>

struct Vertex {
  float x, y, z;
};

int main() {
  std::vector<Vertex> vertices(100);
  std::span<const Vertex> s = vertices;
  // GPU のバッファを作るときに必要なバイト数
  std::println("{} バイト", s.size_bytes());
}
```

```text title="実行結果"
1200 バイト
```

### std::as_bytes {#as_bytes}

```cpp
template <class T, std::size_t N>
std::span<const std::byte> as_bytes(std::span<T, N> s) noexcept;
```

- どんな型の span も、**読み取り専用のバイト列**として見られるようにします

```cpp
#include <print>
#include <span>

int main() {
  int values[] = {1, 2};
  auto bytes = std::as_bytes(std::span(values));
  std::println("{} バイト", bytes.size());
}
```

```text title="実行結果"
8 バイト
```

!!! note "実際は"
    ファイルに書き出す、ネットワークに送る、GPU に渡すなど、「型は気にせずバイト列として扱いたい」関数の引数を `std::span<const std::byte>` にしておくと便利です。

### std::as_writable_bytes {#as_writable_bytes}

```cpp
template <class T, std::size_t N>
std::span<std::byte> as_writable_bytes(std::span<T, N> s) noexcept;
```

- 書き込み可能なバイト列として見ます。ファイルからの読み込み先に使えます

### rbegin {#rbegin}

```cpp
constexpr reverse_iterator rbegin() const noexcept;
```

- 最後の要素を指す逆向きのイテレータ

### rend {#rend}

```cpp
constexpr reverse_iterator rend() const noexcept;
```

- 最初の要素の 1 つ前を指す逆向きのイテレータ。後ろから回すなら `std::views::reverse` のほうが読みやすいです

### at {#at}

```cpp
constexpr reference at(size_type idx) const;  // C++26
```

- 範囲外なら `std::out_of_range`。C++26 の機能なので、まだ使えないことが多いです

## フラグ・オプション

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `std::dynamic_extent` | <span class="rank rank-rare">知ってるだけ</span> | 「個数は実行時に決まる」を表す。`Extent` のデフォルト |

## 計算量まとめ

すべての操作が O(1) です。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    // ポインタと個数を別々に渡す。間違えやすい
    void Draw(const Vertex* vertices, int count);
    Draw(v.data(), static_cast<int>(v.size()));

    // vector 専用になる
    void Draw(const std::vector<Vertex>& vertices);
    ```

=== "今の書き方（C++20）"

    ```cpp
    void Draw(std::span<const Vertex> vertices);
    Draw(v);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 描画・物理の関数の引数 | `void DrawSprites(std::span<const Sprite> sprites)` |
| GPU へのアップロード | `void Upload(std::span<const std::byte> data)` |
| 配列の一部だけ処理 | パーティクルの前半だけ更新する |
| 自作コンテナから中身を見せる | `std::span<const Enemy> Enemies() const` |

## パフォーマンス

- ポインタ + 個数の 16 バイト（64bit 環境）しかないので、**値渡しが一番速い**です。`const std::span<T>&` にする必要はありません。
- 中身へのアクセスは C の配列と同じ速さです。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 範囲外の `[]` / `subspan` | 未定義動作 |
| 元の vector が再確保・破棄されたあとに span を使う | 未定義動作 |
| 一時オブジェクトから span を作って保存する | 未定義動作 |

## よくあるミス

??? failure "span をメンバ変数に保存して、元の vector が伸びる"
    ```cpp
    class Renderer {
     public:
      void SetSprites(std::span<const Sprite> s) { sprites_ = s; }
     private:
      std::span<const Sprite> sprites_;  // 借りたまま持っている
    };

    renderer.SetSprites(sprites);
    sprites.push_back(Sprite{});  // 再確保で sprites_ が壊れる
    ```

    span は「関数を呼んでいる間だけ借りる」ものだと考えます。

??? failure "一時的な vector を span で受ける"
    ```cpp
    std::span<const int> s = GetScores();  // GetScores() が返した vector はこの行で消える
    std::println("{}", s[0]);              // 未定義動作
    ```

??? failure "読むだけなのに const を付け忘れる"
    `std::span<int>` で受けると、`const std::vector<int>` を渡せません。読むだけなら必ず `std::span<const int>` にします。

## 理解度チェック

!!! question "Q1. `void F(std::span<const int> s);` に渡せるのはどれ？"
    `std::vector<int>`、`std::array<int, 3>`、`int[5]`、`std::list<int>`

    <div class="spoiler" markdown>

    **答え:** `std::list<int>` 以外すべて。span は**メモリが連続している**ものしか受け取れません。list は要素がバラバラに置かれているので無理です。

    </div>

!!! question "Q2. span の引数は `const std::span<const T>&` と `std::span<const T>` のどちらが良い？"
    <div class="spoiler" markdown>

    **答え:** `std::span<const T>`（値渡し）。span 自体が 16 バイトしかないので、参照にすると逆に間接参照が増えます。

    </div>

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::vector`](vector.md) | 中身を持っている（所有） | データを持つ側 |
| [`std::string_view`](../utilities/string_view.md) | 文字列専用の span のようなもの | 文字列を借りる |
| [`std::mdspan`](mdspan.md) | 多次元版 <span class="ver ver-23">C++23</span> | 1 次元の配列を 2 次元として見る |
| ポインタ + 個数 | 同じことを手で書く | C の API との境目 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。`at`（範囲チェック付き）は C++26 なので、まだ使えないことが多いです。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 関数の引数で配列を受け取るなら `std::span<const T>`
    - [x] vector / array / C 配列を全部同じ型で受けられる
    - [x] 値渡しで OK（中身はコピーされない）
    - [x] 借りているだけ。保存しない

## 関連ページ

- [cpprefjp: std::span](https://cpprefjp.github.io/reference/span/span.html)
- [cppreference: std::span](https://en.cppreference.com/w/cpp/container/span)
