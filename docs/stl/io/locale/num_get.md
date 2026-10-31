---
title: std::num_get
summary: "文字列から数値を読み込む処理を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::num_get

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`std::cin >> n` が、入力された `"42"` という文字を数値の 42 に直しているのは、ロケールの部品である `std::num_get` です。進数（`hex`）の設定、桁区切り、小数点の規則を見ながら、数値として読めるところまで読み取ります。

`num_put` の逆の働きで、直接使うことはほとんどありません。

!!! tip "ポイント"
    - `operator>>` は、内部で `num_get::get` を呼んでいる
    - 読めなかったときは、`err` に `failbit` を立てる。終端に達したら `eofbit`
    - 読み込み元は、入力イテレータの範囲
    - 戻り値は、読み終えた位置を指す入力イテレータ

!!! info "このページを読む前に"
    [`std::num_put`](num_put.md) と [`std::numpunct`](numpunct.md) を先に読んでください。

## 関数の詳しい説明

### std::num_get {#num_get}

```cpp
template <class CharT, class InIt = std::istreambuf_iterator<CharT>>
class num_get {
 public:
  InIt get(InIt in, InIt end, std::ios_base& str,
           std::ios_base::iostate& err, long& v) const;
  // bool, unsigned long, long long, double, long double, void* にも
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `in`, `end` | `InIt` | 読み込み元の範囲 |
| `str` | `std::ios_base&` | 書式の設定（進数など）を持つストリーム |
| `err` | `std::ios_base::iostate&` | エラーの状態を受け取る |
| `v` | 数値の参照 | 読んだ値を入れる変数 |

`in` から `end` までの文字を、数値として読みます。`str` が `hex` の設定なら 16 進として、`dec` なら 10 進として読みます。`oct` / `dec` / `hex` のどれも設定されていなければ、先頭の `0x` や `0` で判定します。

読めたら `v` に値を入れ、`err` を `goodbit` のままにします。数値として読めない文字（`abc`）に当たると、`v` は 0 になり、`err` に `failbit` が立ちます。範囲が終わるまで読み切った場合は、`eofbit` も立ちます。`err` は、呼ぶ側で `goodbit` に初期化しておきます。

数値の型の範囲を超えたとき（`int` に 99999999999 を読ませたときなど）は、`v` に型の最大値か最小値が入り、`failbit` が立ちます。

戻り値は、読み終えた位置を指すイテレータです。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>

int main() {
  const auto& ng = std::use_facet<std::num_get<char>>(std::locale::classic());

  // 正常に読める場合
  std::istringstream in("42 rest");
  std::istreambuf_iterator<char> b(in);
  std::istreambuf_iterator<char> e;
  std::ios_base::iostate err = std::ios_base::goodbit;
  long v = 0;
  ng.get(b, e, in, err, v);
  std::println("値: {} 失敗: {}", v, (err & std::ios_base::failbit) != 0);

  // 数値でない文字から始まる場合
  std::istringstream bad("abc");
  std::istreambuf_iterator<char> b2(bad);
  err = std::ios_base::goodbit;
  long w = 99;
  ng.get(b2, e, bad, err, w);
  std::println("値: {} 失敗: {}", w, (err & std::ios_base::failbit) != 0);
}
```

```text title="実行結果"
値: 42 失敗: false
値: 0 失敗: true
```

`abc` は数値として読めないので、`failbit` が立ち、変数 `w` は 0 に書き換わりました。

## ゲームでの使いどころ

自作の入力ストリームに、特殊な数値の書式を読ませるときに使えます。数値を文字列から読むだけなら、`std::from_chars` が速くて、ロケールにも依存せず、エラーの扱いも簡単です。

## よくあるミス

??? failure "err を初期化せずに渡す"
    `err` は、結果を足していくビットの集まりです。`goodbit` に初期化してから渡します。

??? failure "範囲を超えた値で failbit が立つのを知らない"
    `int` の最大値より大きな値を読むと、`failbit` が立ち、値は最大値になります。入力の検査では、`failbit` を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`num_put`](num_put.md) | 逆方向。数値を文字にする |
| [`numpunct`](numpunct.md) | 小数点や桁区切りの規則 |
| `std::from_chars` | ロケールに依存せず、文字列から数値を読む |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `num_get` は、`>>` の裏で文字を数値にする部品
    - [x] 失敗は `err` の `failbit`。呼ぶ前に `goodbit` に初期化する
    - [x] 数値の変換だけなら `std::from_chars`

## 関連ページ

- [cpprefjp: num_get](https://cpprefjp.github.io/reference/locale/num_get.html)
- [cppreference: std::num_get](https://en.cppreference.com/w/cpp/locale/num_get)
