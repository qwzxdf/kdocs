---
title: Windows API と文字コード
tags:
  - 文字コード
  - Windows
---

# Windows API と文字コード

Windows の API は**文字列を扱う関数が 2 種類**あります。末尾が `A` の関数（`CreateFileA`、`MessageBoxA`）と末尾が `W` の関数（`CreateFileW`、`MessageBoxW`）です。`A` は ANSI（日本語版 Windows では Shift_JIS 系の CP932）、`W` は Wide（UTF-16）を受け取ります。しかも普段書く `CreateFile` や `MessageBox` は実はマクロで、プロジェクトの設定によって A か W に置き換わります。この仕組みを知らないと「`std::string` を渡したら、日本語が文字化けする」「ファイルが開けない」といった問題が起きます。このページではWindows API では、どの文字コードが要求されるのか、どう呼び分けるのかを徹底的に整理します。

!!! tip "ポイント"
    - <strong>Windows の API は、内部が UTF-16。`W` 版が本物</strong>で `A` 版は「ANSI → UTF-16 に変換して、`W` 版を呼ぶ」ラッパー。
    - <strong>`W` 版を明示的に呼ぶ</strong>（`CreateFileW`、`MessageBoxW`）。`A` 版・マクロの `CreateFile` は使わない。
    - `UNICODE` / `_UNICODE` を定義する（Visual Studio の「文字セット：Unicode を使用する」が既定）。
    - ゲームの文字列は UTF-8 の `std::string`。API を呼ぶ直前に UTF-16（`std::wstring`）に変換する。
    - 新しい Windows（10 バージョン 1903 以降）では、マニフェストで UTF-8 を有効にすると、`A` 版も UTF-8 を受け取る。
    - `TCHAR` / `_T()` はもう使わない。

!!! info "このページを読む前に"
    - [encoding/index.md](index.md)（このセクション全体の地図と、読む順番）
    - [文字コードの基礎](unicode-basics.md)（文字コードの基礎）

## A 版と W 版

| 版 | 末尾 | 引数の文字列型 | 文字コード | 例 |
| --- | --- | --- | --- | --- |
| **A**（ANSI） | `A` | `const char*`（`LPCSTR`） | その PC の ANSI（日本語版は CP932） | `CreateFileA`、`MessageBoxA` |
| W（Wide） | `W` | `const wchar_t*`（`LPCWSTR`） | UTF-16 | `CreateFileW`、`MessageBoxW` |

```cpp
// A 版：char* を受け取る。文字コードは ANSI（CP932）として解釈される
::MessageBoxA(nullptr, "こんにちは", "タイトル", MB_OK);   // /utf-8 のソースだと、UTF-8 が ANSI と誤解されて化ける

// W 版：wchar_t* を受け取る。UTF-16
::MessageBoxW(nullptr, L"こんにちは", L"タイトル", MB_OK);   // 常に正しく表示される
```

### 普段書く名前（マクロ）

`MessageBox`、`CreateFile` のような`A` も `W` も付かない名前は、マクロです。`<windows.h>` が次のように置き換えています。

```cpp
#ifdef UNICODE
#define MessageBox MessageBoxW
#else
#define MessageBox MessageBoxA
#endif
```

| 設定 | `MessageBox` の正体 |
| --- | --- |
| `UNICODE` が定義されている（Visual Studio の既定） | `MessageBoxW` |
| 定義されていない（マルチバイト文字セット） | `MessageBoxA` |

プロジェクトのプロパティ → 構成プロパティ → 詳細 → 文字セット が、「Unicode 文字セットを使用する」なら `UNICODE` と `_UNICODE` が定義されます。

!!! warning "マクロの落とし穴"
    `UNICODE` の有無で同じコードが `A` 版にも `W` 版にもなるので、意図せず別の関数を呼ぶことがあります。さらに、自分で作った関数名がマクロに置き換えられる事故もあります（`GetObject`、`CreateWindow`、`SendMessage`、`min` / `max` など）。`W` 版を明示的に呼ぶのが安全です。

## どの関数が何を要求するか

### Windows API

| 関数・機能 | 引数 | 文字コード |
| --- | --- | --- |
| `CreateFileW`、`DeleteFileW`、`MoveFileW`、`GetFileAttributesW` | `LPCWSTR` | UTF-16 |
| `MessageBoxW`、`SetWindowTextW`、`CreateWindowExW`、`RegisterClassW` | `LPCWSTR` | UTF-16 |
| `OutputDebugStringW`（Visual Studio の出力に表示） | `LPCWSTR` | UTF-16 |
| `GetModuleFileNameW`、`GetCurrentDirectoryW`、`SHGetKnownFolderPath` | `wchar_t*` | UTF-16（取得も） |
| `GetCommandLineW`、`CommandLineToArgvW` | `wchar_t*` | UTF-16 |
| `LoadLibraryW`、`GetEnvironmentVariableW` | `LPCWSTR` | UTF-16 |
| `WriteConsoleW` | `wchar_t*` | UTF-16（コンソールに正しく出せる） |
| `MultiByteToWideChar` / `WideCharToMultiByte` | 両方 | 変換用（[文字コードの変換](conversion.md)） |
| **`A` 版すべて** | `const char*` | ANSI（CP932）。マニフェストで UTF-8 にもできる（後述） |

### C / C++ のランタイム

| 関数 | 文字コード |
| --- | --- |
| `fopen`、`std::ifstream("path")`（`char*` のパス） | ANSI（日本語版は CP932）。UTF-8 のパスを渡すと日本語のファイルが開けない（マニフェストを設定しないと） |
| `_wfopen`、`_wopen`、`std::ifstream(std::filesystem::path)` | UTF-16（`wchar_t`）。日本語のパスはこれで |
| `printf` / `std::cout` | 現在のコンソールのコード ページ / ロケールに従う（[コンソール](console-file-io.md)） |
| `main(int argc, char argv)` の `argv` | ANSI**（CP932）。UTF-8 にならない |
| `wmain(int argc, wchar_t argv)`** | UTF-16 |
| `std::filesystem::path` | 内部は UTF-16（Windows）。下で説明 |

### ライブラリ

| ライブラリ | 要求 |
| --- | --- |
| DirectX（`D3DCompileFromFile`、DirectXTex、DirectXTK の `CreateDDSTextureFromFile`） | **`wchar_t*`（UTF-16）** のパス |
| ImGui、SDL、GLFW、FMOD、nlohmann/json | **`char*`（UTF-8）** |
| stb_image（`stbi_load`） | `char*` だが、内部で `fopen`（ANSI）。日本語パスは失敗する → `stbi_load_from_memory` か wchar 用の関数 |
| OpenGL（シェーダー文字列、ウィンドウ名） | ASCII（シェーダー）、UTF-8（ウィンドウ名は GLFW が変換） |

詳しくは [外部ライブラリと文字コード](libraries.md) を見てください。

## 推奨のやり方

```cpp
// ゲームの文字列は UTF-8。API を呼ぶ直前に W 版に渡せる形に変換する

void ShowError(const std::string& message_utf8) {
  std::wstring wide = Utf8ToWide(message_utf8);                    // 変換の関数は、conversion.md
  ::MessageBoxW(nullptr, wide.c_str(), L"エラー", MB_OK | MB_ICONERROR);
}

HANDLE OpenForRead(const std::string& path_utf8) {
  std::wstring wide = Utf8ToWide(path_utf8);
  return ::CreateFileW(wide.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
                       OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
}
```

| ルール | 理由 |
| --- | --- |
| **ゲームの中は UTF-8 の `std::string`** | ライブラリのほとんどが UTF-8 前提。`wstring` に統一すると変換だらけ |
| API を呼ぶ関数を 1 か所にまとめる（プラットフォーム層） | 変換をそこに閉じ込める。ほかのコードは UTF-8 だけ |
| `W` 版を明示的に呼ぶ | マクロの置き換えに左右されない |
| 変換した `wstring` はすぐ捨てる | 長く持つと 2 種類の文字列を管理する羽目に |
| `TCHAR`、`_T("...")`、`_tcslen` などは使わない | `A` / `W` の両対応のための古い仕組み。今は Unicode だけ |

## std::filesystem::path（Windows）

`std::filesystem::path` は <strong>Windows では内部で UTF-16（`wchar_t`）</strong>を保持します。ファイル名の変換を自動でやってくれるので、日本語のパスでも安全です。

```cpp
#include <filesystem>
#include <fstream>

std::filesystem::path path = std::filesystem::path(u8"data/テクスチャ.png");   // C++20：u8string から
std::ifstream file(path, std::ios::binary);                                     // path を渡すと、UTF-16 で開く
std::string utf8 = path.string();   // ← Windows では ANSI（CP932）の文字列になる！UTF-8 ではない
```

| 操作 | Windows での挙動 |
| --- | --- |
| `path(std::string)` | ANSI（CP932）として、UTF-16 に変換する。UTF-8 の文字列を渡すと化ける |
| `path(std::u8string)` / `path(u8"...")`（C++20） | UTF-8 として扱う。正しい |
| `path::string()` | ANSIに変換して返す。日本語以外の文字で例外や `?` |
| `path::wstring()` | UTF-16（`std::wstring`）。Windows API に渡すのに便利 |
| `path::u8string()`（C++20） | UTF-8（`std::u8string`）。`std::string` に直すには `reinterpret_cast` |
| `std::filesystem::u8path(...)`（C++17） | UTF-8 から path を作る。C++20 で非推奨 |

```cpp
// UTF-8 の std::string から、path を作る（C++20 以降）
std::filesystem::path FromUtf8(const std::string& utf8) {
  return std::filesystem::path(std::u8string_view(
      reinterpret_cast<const char8_t*>(utf8.data()), utf8.size()));
}

// path から、UTF-8 の std::string を取り出す
std::string ToUtf8(const std::filesystem::path& p) {
  std::u8string s = p.u8string();
  return std::string(reinterpret_cast<const char*>(s.data()), s.size());
}
```

詳しくは [filesystem](../stl/io/filesystem.md) を見てください。

## UTF-8 をアプリ全体の ANSI にする（マニフェスト）

**Windows 10 バージョン 1903 以降**は、アプリのマニフェストに「このアプリの ANSI は UTF-8 にする」と書けます。すると、`A` 版の API、`fopen`、`argv`、`std::ifstream("path")` などが UTF-8 を受け取るようになります。

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <activeCodePage xmlns="http://schemas.microsoft.com/SMI/2019/WindowsSettings">UTF-8</activeCodePage>
    </windowsSettings>
  </application>
</assembly>
```

Visual Studio ではこのファイルを `app.manifest` として作りプロジェクトのプロパティ → マニフェスト ツール → 入力と出力 → 追加のマニフェスト ファイル に指定します。

| 項目 | 内容 |
| --- | --- |
| 効果 | `char*` の API・`fopen`・`argv` が UTF-8 になる。`A` 版を UTF-8 で使える |
| 必要な Windows | Windows 10 1903（2019 年 5 月）以降 |
| 古い Windows | 設定が無視されて、ANSI のまま。古い OS をサポートするなら使えない |
| 全部が UTF-8 になる | 使っている DLL・ライブラリの `A` 版の動きも変わる。多くは問題ないが確認が必要 |
| おすすめか | 便利だが、`W` 版を明示的に呼ぶほうが確実。ゲームの配布先が新しい Windows だけなら併用してよい |

### 「Beta: ワールドワイド言語サポートで Unicode UTF-8 を使用」（システム設定）

Windows の設定（地域 → 管理者用の言語の設定 → システム ロケールの変更）にシステム全体を UTF-8 にするチェックがあります。ユーザーの PC の設定なので、配るアプリが前提にしてはいけません（古いアプリが壊れることがあるため、既定はオフです）。

## main、wmain、WinMain、wWinMain

| 関数 | 引数の文字列 | 文字コード |
| --- | --- | --- |
| `int main(int argc, char** argv)` | `char*` | **ANSI**（マニフェストで UTF-8 にできる） |
| `int wmain(int argc, wchar_t argv)`** | `wchar_t*` | UTF-16 |
| `int WINAPI WinMain(..., LPSTR cmd, ...)` | `char*` | ANSI |
| `int WINAPI wWinMain(..., LPWSTR cmd, ...)` | `wchar_t*` | UTF-16 |

コマンド ライン引数に日本語を使うならどの形式でも `GetCommandLineW()` + `CommandLineToArgvW()` で、UTF-16 の引数を取れます。それを UTF-8 に変換して、ゲームに渡します。

```cpp
int main() {
  int argc = 0;
  wchar_t** argv = ::CommandLineToArgvW(::GetCommandLineW(), &argc);   // UTF-16 で取得
  for (int i = 0; i < argc; ++i) {
    std::string arg = WideToUtf8(argv[i]);                             // UTF-8 に
    // ...
  }
  ::LocalFree(argv);   // CommandLineToArgvW の結果は、LocalFree で解放する
}
```

## リソース ファイル（.rc）とダイアログ

| 項目 | 注意 |
| --- | --- |
| **`.rc` ファイル**（アイコン、バージョン情報、メニュー） | 文字コードの扱いが特殊。UTF-8 で保存し先頭に `#pragma code_page(65001)` と書くか UTF-16 で保存する |
| バージョン情報の文字列 | 日本語を入れるならコード ページの指定に注意 |
| メニュー・ダイアログの文字列 | `W` 版（`CreateWindowExW`）なら UTF-16 で、そのまま |

## ゲームでの使いどころ

| 場面 | 方法 |
| --- | --- |
| ウィンドウのタイトル（日本語） | `SetWindowTextW(hwnd, Utf8ToWide(title).c_str())` |
| エラー ダイアログ | `MessageBoxW` |
| デバッグ出力 | `OutputDebugStringW`（Visual Studio の出力に出る）。または `std::println` |
| ファイルのパス（日本語を含む） | `std::filesystem::path`（UTF-8 から作る）か `CreateFileW` |
| 設定の保存先（`%APPDATA%`） | `SHGetKnownFolderPath`（UTF-16）→ UTF-8 に変換。ユーザー名が日本語のことがある |
| 画像・音の読み込み（外部ライブラリ） | ライブラリごとに確認（`wchar_t*` か `char*`） |
| コマンド ライン引数 | `GetCommandLineW` + `CommandLineToArgvW` |

## よくあるミス

??? failure "ユーザー名が日本語の PC で、保存先が開けない"
    `C:\Users\山田\AppData\...` のようなパスを `char*` の API（`fopen` など）に渡すと ANSI として解釈されて、開けません。**`std::filesystem::path` か `W` 版**を使います。開発 PC のユーザー名が英語だと気づきません。日本語のユーザー名でテストします。

??? failure "`path.string()` で、日本語以外の文字が `?` になる"
    Windows の `string()` は ANSI に変換するので、ANSI で表せない文字が失われます。`u8string()` か `wstring()` を使います。

??? failure "UTF-8 の `std::string` をそのまま `CreateFileA` に渡す"
    ANSI として解釈されて、ファイルが見つかりません。`CreateFileW` + 変換にします。

??? failure "`UNICODE` を定義しているのに、`char*` を渡す"
    `CreateFile`（= `CreateFileW`）に `const char*` を渡すとコンパイル エラーになります（エラーの意味が分かりにくい）。`W` 版を明示して `wchar_t*` を渡します。

??? failure "`_T("...")` や `TCHAR` を使い続ける"
    古い資料に出てきますが、今は不要です。`L"..."` と `wchar_t`、または UTF-8 の `char` + 変換で書きます。

??? failure "マニフェストで UTF-8 にしたのに、古い Windows で動かない"
    Windows 10 1903 より前では、無視されます。対象の OS を決めて必要なら `W` 版 + 変換で書きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Windows の API は <strong>`A`（ANSI = CP932）</strong>と `W`（UTF-16）。本物は W
    - [x] `W` 版を明示的に呼ぶ。UTF-8 の `std::string` から直前に変換する
    - [x] `UNICODE` を定義。`TCHAR` / `_T()` は使わない
    - [x] `std::filesystem::path` は UTF-16 を内部に持つ。`u8string()` / `wstring()` で取り出し `string()` は使わない
    - [x] 新しい Windows なら マニフェストの `activeCodePage` = UTF-8 も使える
    - [x] 日本語のユーザー名・パスでテストする

## 関連ページ

- [文字コード（目次）](index.md)
- [文字コードの変換](conversion.md)
- [C++ の文字型と文字列型](string-types.md)
- [外部ライブラリと文字コード](libraries.md)
- [filesystem](../stl/io/filesystem.md)
