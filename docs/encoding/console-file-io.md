---
title: コンソールとファイルの入出力
tags:
  - 文字コード
---

# コンソールとファイルの入出力

プログラムの**外とのやり取り**（画面への出力、ファイルの読み書き）は、文字コードの問題が一番表に出る場所です。`std::println` で日本語を出したら化けた、ファイルに書いた日本語をメモ帳で開いたら化けた、Shift_JIS のテキストを読んだら化けた、といった問題です。ここでは、コンソール（黒い画面）とファイルで、文字コードがどう決まるのかと、安全な読み書きの方法をまとめます。

!!! tip "ポイント"
    - <strong>ファイルは、UTF-8（BOM なし）で書く。</strong>バイナリ モードで書く（`std::ios::binary`）。
    - <strong>読むときは、BOM と不正バイトを確認</strong>。UTF-8 でなければ、CP932 などから変換する。
    - コンソールは、`/utf-8` + `std::println`（C++23） が一番簡単（Windows Terminal がおすすめ）。
    - 古い方法は、`SetConsoleOutputCP(CP_UTF8)`（または `chcp 65001`）。
    - テキスト モードは、`\n` を CRLF に変換する。文字コードの変換はしない。
    - メモ帳で開いて化けるのは、メモ帳の既定の判断のこともある。VS Code などで確認する。

!!! info "このページを読む前に"
    - [encoding/index.md](index.md)（このセクション全体の地図と、読む順番）
    - [文字コードの基礎](unicode-basics.md)（文字コードの基礎）

## コンソール（画面への出力）

### 何が起きているか

<svg class="fig flow" viewBox="0 0 939 112" role="img" aria-label="コンソールへの出力：バイトを送り、コンソールが解釈する"><defs><marker id="fl31342" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">コンソールへの出力：バイトを送り、コンソールが解釈する</text><line x1="216.0" y1="64.0" x2="274.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl31342)"/><line x1="390.0" y1="64.0" x2="448.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl31342)"/><line x1="754.0" y1="64.0" x2="812.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl31342)"/><rect x="28.0" y="44.0" width="185" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="120.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">std::string （UTF-8）</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="277.0" y="44.0" width="110" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="332.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">バイトを送る</text><circle cx="279.0" cy="46.0" r="10" fill="#2ea043"/><text x="279.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="451.0" y="44.0" width="300" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="601.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">コンソール （自分のコードページで解釈）</text><circle cx="453.0" cy="46.0" r="10" fill="#e5a828"/><text x="453.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="815.0" y="44.0" width="96" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="863.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">文字を描く</text><circle cx="817.0" cy="46.0" r="10" fill="#e5484d"/><text x="817.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

文字化けは、**プログラムが送るバイトの文字コード**と、コンソールが想定している文字コード（コード ページ）が違うときに起きます。

| コンソールの種類 | 既定のコード ページ |
| --- | --- |
| 日本語版 Windows のコマンド プロンプト（conhost） | 932（Shift_JIS） |
| Windows Terminal | コンソール アプリの出力に従う（同じく既定は 932 のことが多い） |
| Visual Studio の「外部コンソール」 | 同上 |
| Visual Studio の「出力」ウィンドウ | `OutputDebugStringW`（UTF-16）。`std::cout` の出力は、別（ここには出ない） |

### 方法 1：std::println（C++23）+ /utf-8（おすすめ）

```cpp
#include <print>

int main() {
  std::println("こんにちは、世界");   // /utf-8 の環境で、日本語も正しく出る
}
```

| 条件 | 説明 |
| --- | --- |
| コンパイラが `<print>` に対応 | MSVC 17.7 以降 |
| `/utf-8` を付けてビルドする | リテラルが UTF-8 のバイトになる |
| 出力先がコンソール | 対応した MSVC の `std::print` は、UTF-8 をコンソールに正しく出す（内部で UTF-16 に変換して `WriteConsoleW` を使う） |
| 出力先がファイル・パイプ | UTF-8 のバイトをそのまま書く |

コンソールのコード ページにほぼ左右されず、日本語が出ます。ただし、フォントが日本語に対応している必要があります（Windows Terminal の既定フォントは対応）。

### 方法 2：SetConsoleOutputCP（std::cout を使う）

`std::cout` で UTF-8 を出すには、コンソールのコード ページを 65001（UTF-8）に変える必要があります。

```cpp
#include <windows.h>

#include <iostream>

int main() {
  ::SetConsoleOutputCP(CP_UTF8);   // 出力を UTF-8 として解釈させる
  ::SetConsoleCP(CP_UTF8);         // 入力も UTF-8（必要なら）

  std::cout << "こんにちは、世界\n";   // /utf-8 でビルドしていれば、UTF-8 のバイトが出る
}
```

| 方法 | 説明 |
| --- | --- |
| `SetConsoleOutputCP(CP_UTF8)` | プログラムの中で、コンソールのコード ページを変える |
| `chcp 65001`（コマンド プロンプト） | 実行前に手で切り替える。そのウィンドウだけ有効 |
| Windows Terminal + UTF-8 の設定 | 「プロファイル」の設定で、既定にもできる |

### 方法 3：wcout（UTF-16）

```cpp
#include <fcntl.h>
#include <io.h>

#include <iostream>

int main() {
  _setmode(_fileno(stdout), _O_U16TEXT);   // 標準出力を UTF-16 モードにする
  std::wcout << L"こんにちは\n";
  // この後、std::cout は使えない（混ぜると壊れる）
}
```

`wcout` と `cout` を混ぜると壊れるので、一方に決めます。ゲームでは、UTF-8 の `println` が簡単です。

### コンソールの入力

| 状況 | 注意 |
| --- | --- |
| `std::cin` / `std::getline` | コンソールのコード ページのバイトをそのまま読む。UTF-8 にしたいなら、`SetConsoleCP(CP_UTF8)` |
| 日本語入力（IME） | Windows Terminal は、問題が少ない。古い conhost は、UTF-8 入力に不具合があった |
| 確実に取りたい | `ReadConsoleW`（UTF-16）で読み、UTF-8 に変換する |

ゲームは、コンソールからの入力をほとんど使わないので、出力（ログ）だけ考えれば十分です。

## ファイルの書き込み

```cpp
#include <fstream>
#include <string>

// UTF-8（BOM なし）で書く。バイナリ モードで、改行を LF のままにする
void SaveText(const std::filesystem::path& path, const std::string& utf8) {
  std::ofstream file(path, std::ios::binary);
  file.write(utf8.data(), static_cast<std::streamsize>(utf8.size()));
}
```

| 項目 | 説明 |
| --- | --- |
| **`std::ios::binary`** | バイナリ モード。`\n` を CRLF に変換しない。バイトをそのまま書く |
| テキスト モード（既定） | Windows では、`\n` が `\r\n` に変換される（文字コードは変換しない） |
| `std::string` を書く | UTF-8 のバイトをそのまま書く |
| BOM を書かない | 何もしなければ、付かない |
| `std::wofstream` | ワイド文字をロケールの文字コード（ANSI）に変換して書く。意図しない結果になるので使わない |

BOM を付けたい（付けるべき）場合: `.rc` ファイルや、BOM を要求する古いツール、Excel で開く CSV（BOM なしだと文字化けする）は、BOM を書きます。

```cpp
constexpr unsigned char kUtf8Bom[] = {0xEF, 0xBB, 0xBF};
file.write(reinterpret_cast<const char*>(kUtf8Bom), sizeof(kUtf8Bom));
file.write(utf8.data(), static_cast<std::streamsize>(utf8.size()));
```

## ファイルの読み込み

```cpp
#include <fstream>
#include <iterator>
#include <string>

// ファイルの中身をバイト列のまま全部読む
std::string ReadAll(const std::filesystem::path& path) {
  std::ifstream file(path, std::ios::binary);
  return std::string(std::istreambuf_iterator<char>(file), {});
}
```

### 読んだあとに確認すること

| 確認 | 方法 |
| --- | --- |
| **BOM の有無** | 先頭が `EF BB BF` なら、UTF-8 の BOM（取り除く）。`FF FE` / `FE FF` なら UTF-16 |
| UTF-8 として正しいか | `MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, ...)` が成功するか。または、simdutf の `validate_utf8` |
| 正しくなければ | CP932 かもしれない → [CP932 から UTF-8 に変換](conversion.md) |
| 改行 | `\r\n` が混ざっていれば、必要に応じて `\n` にそろえる |

```cpp
// 読み込んだバイト列を UTF-8 の文字列にそろえる（BOM の除去 + CP932 のフォールバック）
std::string NormalizeToUtf8(std::string bytes) {
  // ① UTF-8 の BOM を取り除く
  if (bytes.size() >= 3 && static_cast<unsigned char>(bytes[0]) == 0xEF &&
      static_cast<unsigned char>(bytes[1]) == 0xBB && static_cast<unsigned char>(bytes[2]) == 0xBF) {
    bytes.erase(0, 3);
  }
  // ② UTF-8 として正しければ、そのまま使う
  if (IsValidUtf8(bytes)) {            // 自作または simdutf::validate_utf8
    return bytes;
  }
  // ③ 違えば、CP932（Shift_JIS）だと仮定して変換する
  return Cp932ToUtf8(bytes);           // conversion.md の関数
}
```

文字コードの自動判定（BOM なしで、UTF-8 か Shift_JIS か）は、100% は無理です。UTF-8 として正しいか検査し、正しければ UTF-8、違えば CP932 と仮定するのが、日本語環境では実用的です。短い文章では、偶然どちらにも読めることがありますが、まれです。

## メモ帳・エクセルで開いたとき

| 相手 | 注意 |
| --- | --- |
| **メモ帳**（Windows 10 1903 以降） | 既定で UTF-8（BOM なし）を正しく認識する。古いメモ帳は、BOM なしを ANSI と誤解して化ける |
| Excel（CSV） | BOM なしの UTF-8 の CSV は、文字化けする。ダブル クリックで開くと、ANSI と思う。BOM を付けるか、「データ → テキスト/CSV から」で、文字コードを選ぶ |
| VS Code | 右下に文字コードが表示され、変更できる。確認に便利 |
| ブラウザー | HTML は `<meta charset="utf-8">`。JSON は UTF-8 が標準 |

## ログ ファイル

| 方針 | 説明 |
| --- | --- |
| **UTF-8（BOM なし）で書く** | 日本語のメッセージも、そのまま |
| 追記モード（`std::ios::app`） | 先頭に BOM を重ねて書かない |
| 改行は LF | バイナリ モードで書く |
| ファイル名に日本語を使わない（ログのファイル名） | パスの問題を避ける |
| flush のタイミング | クラッシュ前の最後のログが残るよう、重要なログは `flush()` する |

## ゲームでの使いどころ

| 場面 | 方法 |
| --- | --- |
| デバッグの `println` | `/utf-8` + `std::println`。Windows Terminal で見る |
| ログ ファイル | UTF-8（BOM なし）、バイナリ モード、追記 |
| セーブ・設定（JSON） | UTF-8（BOM なし）。読むときに BOM を取り除く |
| 古い CSV・シナリオ（Shift_JIS）の読み込み | 読み込み時に UTF-8 に変換して、以降は UTF-8 |
| Excel で開く CSV を出力する | BOM を付ける（Excel 専用の出力だけ） |
| ユーザーが作った MOD のテキスト | UTF-8 として検証し、違えば CP932 を試す |

## よくあるミス

??? failure "コンソールで、日本語が `????` や `縺薙ｓ` になる"
    プログラムが出す文字コードと、コンソールのコード ページが違います。`std::println` + `/utf-8`、または `SetConsoleOutputCP(CP_UTF8)` を使います（[トラブルシューティング](mojibake.md)）。

??? failure "テキスト モードで書いて、改行が CRLF になる"
    Windows のテキスト モード（既定）は、`\n` を CRLF にします。LF で書きたいなら、`std::ios::binary` を付けます。

??? failure "`std::wofstream` で書いて、ANSI になる"
    `wofstream` は、`wchar_t` をロケールの文字コード（日本語版は CP932）に変換して書きます。UTF-8 で書きたいなら、`std::ofstream` + UTF-8 の `std::string` です。

??? failure "BOM 付きファイルをそのまま JSON パーサーに渡す"
    先頭の `EF BB BF` が、文字として読まれて、エラーになります。読み込み時に BOM を取り除きます。

??? failure "Excel で、UTF-8 の CSV が文字化けする"
    BOM がないと、Excel は ANSI と判断します。Excel 専用の出力には、BOM を付けます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルは <strong>UTF-8（BOM なし）</strong>、バイナリ モードで読み書き
    - [x] 読むときは、BOM を取り除き、UTF-8 として正しいかを確認。違えば CP932 を試す
    - [x] コンソールは`/utf-8` + `std::println`（または `SetConsoleOutputCP(CP_UTF8)`）
    - [x] `wofstream` / `wcout` は使わない。`cout` と混ぜない
    - [x] Excel の CSV だけは、BOM を付ける

## 関連ページ

- [文字コード（目次）](index.md)
- [文字コードの変換](conversion.md)
- [文字化けのトラブルシューティング](mojibake.md)
- [ファイル入出力（基礎）](../basics/file-io.md)
- [fstream](../stl/io/fstream.md)
- [std::format / println](../stl/utilities/format.md)
