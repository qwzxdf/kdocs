# 文字コード

日本語を扱うゲームを作ると必ず**文字化け**に出会います。ソースコードに書いた日本語が `????` になるファイルから読んだ文字が `縺薙ｓ` のようになる、Windows API に渡したら動かない、`std::string` と `std::wstring` のどちらを使えばいいか分からない、などです。原因はほとんどが「**文字をバイトの並びにどう変換するか**（文字コード）が、書く側と読む側で食い違っている」ことです。このカテゴリでは文字コードの基礎から、C++ の文字列型、Windows API、ソースファイルの設定、変換、トラブルシューティングまでをゲーム制作の目線で徹底的に解説します。

## 一番大事な決まり

| 場所 | 文字コード |
| --- | --- |
| **ソースファイル**（`.cpp`、`.h`） | <strong>UTF-8（BOM なし）</strong>。MSVC には `/utf-8` を付ける |
| **データファイル**（JSON、YAML、シナリオ） | <strong>UTF-8（BOM なし）</strong> |
| **プログラムの中の文字列**（`std::string`） | **UTF-8** |
| **Windows API に渡すとき** | **UTF-16**（`std::wstring` / `wchar_t`）に、その場で変換 |
| **改行** | **LF**（Git で統一）。Windows 専用の出力だけ CRLF |

これを守れば**ほとんどの文字化けは起きません**。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [文字コードの基礎](unicode-basics.md) | ASCII、Unicode、UTF-8 / UTF-16 / Shift_JIS、BOM、改行、文字数と幅 |
| [C++ の文字型と文字列型](string-types.md) | `char`、`wchar_t`、`char8_t`、`string`、`wstring`、リテラル |
| [文字コードの変換](conversion.md) | UTF-8 ⇔ UTF-16 ⇔ Shift_JIS。Win32 の関数、ライブラリ |
| [Windows API と文字コード](windows-api.md) | A 版と W 版、`UNICODE`、`wmain`、UTF-8 マニフェスト、どちらを要求されるか |
| [ソースファイルの文字コードと強制](source-files.md) | `/utf-8`、`.editorconfig`、`.gitattributes`、clang-format、CI |
| [コンソールとファイルの入出力](console-file-io.md) | `chcp`、`std::print`、ファイルの読み書き BOM の判定 |
| [文字化けのトラブルシューティング](mojibake.md) | 症状から、原因と直し方を探す |
| [外部ライブラリと文字コード](libraries.md) | ImGui、JSON、SDL、FMOD、DirectX、ICU など何を要求されるか |

## 文字化けはなぜ起きるのか

<div class="anim" data-type="graph" data-label="保存するときと読むときの文字コードが違うと、文字化けする">
n c 文字_あ 0 0
n b バイト列_E3_81_82_(UTF-8) 1 0
n r 文字_あ 2 0
l c b - ①_UTF-8_で保存
l b r - ②_UTF-8_で読む
---
n c 文字_あ 0 0
n b バイト列_82_A0_(Shift_JIS) 1 0
n r 文字化け_(縺_など) 2 0 gone
l c b - ①_Shift_JIS_で保存
l b r - ②_UTF-8_で読む
</div>

<strong>文字化けは書いた文字コードと読む側が想定した文字コードが、違うときに起きます。</strong>データそのものは壊れていません（多くの場合、正しい文字コードで読み直せば、元に戻ります）。

## 関連ページ

- [Visual Studio：文字コードを UTF-8 にしよう](../vs/utf8.md)
- [Visual Studio：よくあるエラー（文字化け）](../vs/errors.md#mojibake)
- [std::string](../stl/containers/string.md)
- [std::string_view](../stl/utilities/string_view.md)
