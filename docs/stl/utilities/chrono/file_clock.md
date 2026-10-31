---
title: std::chrono::file_clock
summary: "ファイルの更新日時に使われる時計。"
order: 12
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::file_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::filesystem::last_write_time` が返す、ファイルの更新日時は、`system_clock` の時点ではなく、`file_clock` の時点です。OS によってファイル時刻の起点が違う（Windows は 1601 年、Linux は 1970 年）ため、標準が専用の時計として用意しました。C++20 から、`clock_cast` で `system_clock` に直せます。

!!! tip "ポイント"
    - `filesystem::file_time_type` は `file_time<...>` で、この時計の時点
    - 起点は規格で決まっていない。数値を直接見ない
    - `clock_cast<system_clock>(ft)` で、日付や時刻にできる
    - `file_clock::now()` で、現在のファイル時計の時点が取れる

!!! info "このページを読む前に"
    [`system_clock`](system_clock.md) と [`clock_cast`](clock_cast.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::file_clock {#file_clock}

<span class="ver ver-20">C++20</span>

```cpp
class file_clock {
 public:
  using duration = chrono::duration<rep, period>;
  using time_point = chrono::time_point<file_clock>;
  static constexpr bool is_steady = false;

  static time_point now() noexcept;
  template <class Duration>
  static sys_time<...> to_sys(const file_time<Duration>& t);
  template <class Duration>
  static file_time<...> from_sys(const sys_time<Duration>& t);
};
```

起点は処理系が決めます。MSVC では Windows のファイル時刻と同じ 1601 年 1 月 1 日、libstdc++ では、1970 年が基準ではあるものの、細かな違いがあります。時計の数値そのものを保存すると、環境が変わったときに、意味が変わります。

ファイルの更新日時を表示するには、`system_clock` に直してから書式にかけます。

```cpp
auto ft = std::filesystem::last_write_time(path);
auto st = std::chrono::clock_cast<std::chrono::system_clock>(ft);
std::println("{:%F %T}", floor<seconds>(st));
```

C++17 の時代は、この変換の手段がなく、環境依存のコードを書いていました。C++20 でようやく標準的な方法ができました。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // file_clock の現在時刻を、system_clock に直して比べる
  const file_time<file_clock::duration> f = file_clock::now();
  const auto s = clock_cast<system_clock>(f);
  const auto diff = system_clock::now() - s;

  std::println("ほぼ同じ時刻: {}", abs(diff) < 1s);
}
```

```text title="実行結果"
ほぼ同じ時刻: true
```

起点が違っても、`clock_cast` で `system_clock` にそろえると、同じ瞬間になります。

## ゲームでの使いどころ

アセットの更新を検知するホット リロードで、ファイルの更新日時を比べます。保存した更新日時を比べるだけなら、`file_time` どうしで足ります。日付として表示するときに、`clock_cast` を使います。

## よくあるミス

??? failure "file_time の count() を保存する"
    起点が環境で違うので、別の環境で読むと意味が変わります。`system_clock` に直してから保存します。

??? failure "file_time と sys_time を直接比べる"
    型が違い、コンパイルできません。`clock_cast` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_time`](file_time.md) | `file_clock` の時点を表す別名 |
| [`system_clock`](system_clock.md) | 日常の時計 |
| [`clock_cast`](clock_cast.md) | 時計どうしを変換する |
| [`std::filesystem::last_write_time`](../../io/filesystem/last_write_time.md) | ファイルの更新日時を取る |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: file_clock](https://cpprefjp.github.io/reference/chrono/file_clock.html)
- [cppreference: std::chrono::file_clock](https://en.cppreference.com/w/cpp/chrono/file_clock)
