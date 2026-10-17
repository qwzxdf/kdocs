# 文字コード

日本語を扱うゲームを作ると、必ず**文字化け**に出会います。ソースコードに書いた日本語が `????` になる、ファイルから読んだ文字が `縺薙ｓ` のようになる、Windows API に渡したら動かない、`std::string` と `std::wstring` のどちらを使えばいいか分からない、などです。原因は、ほとんどが「**文字を、バイトの並びにどう変換するか**（文字コード）が、書く側と読む側で食い違っている」ことです。このカテゴリでは、文字コードの基礎から、C++ の文字列型、Windows API、ソースファイルの設定、変換、トラブルシューティングまでを、ゲーム制作の目線で、徹底的に解説します。

!!! tip "ポイント"
    - <strong>内部は、すべて UTF-8 で統一する。</strong>ソースファイル、データファイル（JSON など）、`std::string` の中身、全部 UTF-8。
    - <strong>Windows API に渡すときだけ、UTF-16（`std::wstring`）に変換する。</strong>境界で変換し、内側には持ち込まない。
    - Visual Studio では<strong>`/utf-8` を必ず付ける</strong>。ソースは UTF-8（BOM なし）で保存する。
    - <strong>`std::string` は「ただのバイト列」。</strong>文字コードを知らない。`size()` は文字数ではなくバイト数。
    - 文字コードの決まりは、<strong>設定ファイルと CI で強制</strong>する（`.editorconfig`、`.gitattributes`、チェック スクリプト）。人の注意に頼らない。

## 一番大事な決まり

| 場所 | 文字コード |
| --- | --- |
| **ソースファイル**（`.cpp`、`.h`） | <strong>UTF-8（BOM なし）</strong>。MSVC には `/utf-8` を付ける |
| **データファイル**（JSON、YAML、シナリオ） | <strong>UTF-8（BOM なし）</strong> |
| **プログラムの中の文字列**（`std::string`） | **UTF-8** |
| **Windows API に渡すとき** | **UTF-16**（`std::wstring` / `wchar_t`）に、その場で変換 |
| **改行** | **LF**（Git で統一）。Windows 専用の出力だけ CRLF |

これを守れば、**ほとんどの文字化けは起きません**。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [文字コードの基礎](unicode-basics.md) | Unicode、UTF-8 / UTF-16 / Shift_JIS、BOM、改行、文字数と幅 |
| [C++ の文字型と文字列型](string-types.md) | `char`、`wchar_t`、`char8_t`、`string`、`wstring`、リテラル |
| [文字コードの変換](conversion.md) | UTF-8 ⇔ UTF-16 ⇔ Shift_JIS。Win32 の関数、ライブラリ |
| [Windows API と文字コード](windows-api.md) | A 版と W 版、`UNICODE`、`wmain`、UTF-8 マニフェスト、どちらを要求されるか |
| [ソースファイルの文字コードと強制](source-files.md) | `/utf-8`、`.editorconfig`、`.gitattributes`、clang-format、CI |
| [コンソールとファイルの入出力](console-file-io.md) | `chcp`、`std::print`、ファイルの読み書き、BOM の判定 |
| [文字化けのトラブルシューティング](mojibake.md) | 症状から、原因と直し方を探す |
| [外部ライブラリと文字コード](libraries.md) | ImGui、JSON、SDL、FMOD、DirectX、ICU など、何を要求されるか |

## 文字化けは、なぜ起きるのか

```text
文字 "あ"
  │ ① 保存・変換するとき、どの文字コードで、バイトにするか
  ▼
バイト列  E3 81 82        （UTF-8 の場合）
          82 A0           （Shift_JIS の場合）
  │ ② 読むとき、どの文字コードだと思って、文字に戻すか
  ▼
文字 "あ"   ← ①と②が同じなら、元に戻る
            "縺" など    ← ①と②が違うと、文字化け
```

<strong>文字化けは、書いた文字コードと、読む側が想定した文字コードが、違うときに起きます。</strong>データそのものは壊れていません（多くの場合、正しい文字コードで読み直せば、元に戻ります）。

## 関連ページ

- [Visual Studio：C++23 の設定（/utf-8）](../vs/settings.md#utf8)
- [Visual Studio：よくあるエラー（文字化け）](../vs/errors.md#mojibake)
- [std::string](../stl/containers/string.md)
- [std::string_view](../stl/utilities/string_view.md)
