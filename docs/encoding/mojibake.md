---
title: 文字化けのトラブルシューティング
tags:
  - 文字コード
---

# 文字化けのトラブルシューティング

文字化けは**見た目のパターンから、原因をかなり絞り込める**不具合です。「縺」が並ぶ「ã」が混ざる「?」になる「�」が出るのように化け方には、原因ごとの特徴があります。このページは症状から原因と直し方を探すためのトラブルシューティングです。基本は「どこでどの文字コードで書かれどこで、どの文字コードとして読まれたか」を順にたどって、食い違いを見つけることです。

!!! tip "ポイント"
    - 化け方の<strong>パターン</strong>で、原因を絞れる（下の表）。
    - まず<strong>データの流れを書き出す</strong>（ソース → コンパイラ → 実行 → API → 画面）。どの段階で食い違ったかを探す。
    - バイト列を見る（16 進数ダンプ）。`E3 81 82` なら UTF-8 の「あ」、`82 A0` なら Shift_JIS の「あ」。
    - データは壊れていないことが多い。読む側の文字コードを直せば、元に戻る。
    - 一度 `?` や `�` になったら、元には戻らない（情報が失われている）。変換元に戻って直す。

## 症状から探す

文字化けは文字が**どう壊れたか**で原因がほぼ決まります。たとえば「縺」「繧」が並ぶのは、UTF-8 のバイト列を Shift_JIS として読んだときの典型的な形です。逆に `?` が並んでいるなら変換先に存在しない文字を変換する段階で、すでに情報が失われています。この違いは重要で前者は読み方を直せば元に戻り後者は元のデータに戻って変換をやり直すしかありません。

まず下の表で、見た目から原因の候補を絞ってください。

| 見た目 | 例 | 原因 | 直し方 |
| --- | --- | --- | --- |
| 「縺」「繧」「繝」「ｳ」が並ぶ | `縺薙ｓ縺ｫ縺｡縺ｯ` | UTF-8 のバイトを、Shift_JIS（CP932）として読んだ | 読む側を UTF-8 にする（`/utf-8`、コンソールを 65001、エディターで UTF-8 として開く） |
| 「ã」「â」「ã€」などが混ざる | `ã“ã‚“ã«ã¡ã¯` | UTF-8 のバイトを、Latin-1 / Windows-1252 として読んだ | 読む側を UTF-8 に（Web なら `<meta charset="utf-8">`、HTTP ヘッダー） |
| `�`（黒いひし形に「?」） | `���` | 不正なバイトを UTF-8 として読んだ。置換文字（U+FFFD）に置き換わった | Shift_JIS のデータを UTF-8 として読んだ可能性大。CP932 として読み直す。元データが壊れていることも |
| `?` になる | `????` | 変換先の文字コードで表せない文字を、`?` に置き換えた（Shift_JIS ⇔ UTF-16 の変換など） | 変換前に戻る。`?` になった時点で元の文字は失われている。変換先を UTF-8 にする |
| 文字が消える・短くなる | `こんにちは` → `こん` | 途中の不正バイト、`\0` の誤解、バイト数と文字数の取り違え | 長さの指定（バイト数 / 文字数）を確認 |
| 半角カタカナが混ざる（`ｱｲｳ`） | `ｺﾝﾆﾁﾊ` | UTF-8 のバイトを、Shift_JIS として読んだとき `A1〜DF` が半角カタカナに | 同上（「縺」と同じ原因のことが多い） |
| 漢字が別の見知らぬ漢字になる | 「文字化け」→「譁�ｭ怜喧縺�」 | UTF-8 → Shift_JIS 解釈（よく見る形） | 同上 |
| 記号だけが化ける（`～` `〜` `－` `−`） | 波ダッシュ・マイナス | Shift_JIS と CP932 の対応の違い（U+301C と U+FF5E） | UTF-8 に統一する。CP932 として扱う |
| 丸数字・特殊文字が `?` | `①` `㈱` | Shift_JIS（JIS 規格）にはなく、CP932 の拡張にある文字 | CP932 として扱う。UTF-8 に統一 |
| `□`（四角）や空白になる | 画面に四角 | フォントにその文字がない（文字コードは正しい） | 日本語フォントを使う（ImGui なら、日本語のグリフ範囲を読み込む） |
| `\` が `¥` に見える | `C:¥Users¥` | 日本語フォントの表示上の違い（データは `\` のまま） | 問題なし。バックスラッシュが `5C` であることをダンプで確認 |

## 場面別に探す

症状から原因が絞れない場合は**文字列がどこで化けたか**で探します。文字列はソースファイル → コンパイラ → 実行時の変数 → API → 画面（またはファイル）の順に流れ、化ける場所はこの流れのどこか 1 か所です。以下の表はその場所ごとによくある症状と直し方を並べています。

### コンパイラ・ソース

| 症状 | 原因 | 直し方 |
| --- | --- | --- |
| 警告 C4819（現在のコード ページで表示できない文字） | UTF-8 のファイルを、`/utf-8` なしで CP932 として読んだ | `/utf-8` を付ける |
| 警告 C4828（不正な文字） | `/utf-8` ありで、UTF-8 でない（Shift_JIS の）ファイルを読んだ | ファイルを UTF-8 に変換する |
| エラー C2001（定数に改行があります）、C2143 など意味不明な構文エラー | UTF-8 の日本語を、CP932 として読んだときバイトの途中の `5C`（`\`）などが、文字列を壊した | `/utf-8`。ファイルを BOM 付き UTF-8 にして、一時的に確認 |
| 文字列リテラルが ImGui などで化ける | `/utf-8` がなく、`"こんにちは"` が CP932 のバイトになっている | `/utf-8` を付けてリビルド（全ファイルを再ビルド） |
| 一部のファイルだけ化ける | そのファイルだけ Shift_JIS で保存されている | そのファイルを UTF-8 に変換 |
| Visual Studio で開くと化ける | BOM なし UTF-8 を、ANSI と判断した（エディターの設定） | `.editorconfig` に `charset = utf-8`。「エンコード付きで開く」 |

### 実行時：画面・コンソール

| 症状 | 原因 | 直し方 |
| --- | --- | --- |
| `std::cout` の日本語がコンソールで化ける | プログラムは UTF-8、コンソールは CP932 | `SetConsoleOutputCP(CP_UTF8)`、`chcp 65001`、または `std::println` |
| `std::println` で化ける | `/utf-8` がない、または古い MSVC | `/utf-8`、MSVC 17.7 以降 |
| Visual Studio の出力ウィンドウで化ける | `OutputDebugStringA`（ANSI）に UTF-8 を渡した | `OutputDebugStringW` に変換して渡す |
| MessageBox の文字が化ける | `MessageBoxA`（ANSI）に UTF-8 を渡した | `MessageBoxW` + 変換（[Windows API](windows-api.md)） |
| ウィンドウ タイトルが化ける | 同上（`SetWindowTextA`） | `SetWindowTextW` |

### 実行時：ファイル

| 症状 | 原因 | 直し方 |
| --- | --- | --- |
| 日本語のファイル名・パスが開けない | `char*` の API（`fopen`、`ifstream("...")`）に UTF-8 を渡した。ANSI として解釈された | `std::filesystem::path`（`u8` から）か `_wfopen`、`CreateFileW` |
| 日本語のユーザー名の PC で、保存できない | 同上（`C:\Users\山田\...`） | 同上。日本語のユーザーでテストする |
| ファイルから読んだ日本語が化ける | ファイルが Shift_JIS だった / BOM が先頭に付いている | 文字コードを確認。BOM を取り除く。CP932 → UTF-8 に変換 |
| メモ帳で開くと化ける | 古いメモ帳が、BOM なし UTF-8 を ANSI と判断 | 新しいメモ帳、VS Code で確認する |
| Excel で CSV が化ける | BOM なし UTF-8 を、Excel が ANSI と判断 | BOM を付ける。または「データ → テキスト/CSV から」で、文字コードを選ぶ |
| セーブ データが別の PC で化ける | `wchar_t`（Windows と Linux で大きさ違い）、ANSI（PC ごとに違う）で保存した | UTF-8 で保存する |

### 外部ライブラリ

| 症状 | 原因 | 直し方 |
| --- | --- | --- |
| ImGui で `?` や四角 | 日本語フォントを読み込んでいない（文字コードは正しい） | 日本語のフォントと、グリフ範囲を読み込む |
| ImGui で化ける | 渡した文字列が UTF-8 でない | `/utf-8` |
| JSON の `dump()` で例外（type_error.316） | UTF-8 でない文字列が入っている | 入力を UTF-8 に。`error_handler_t::replace` で置き換える |
| JSON を読んだら先頭でエラー | BOM が付いている | BOM を取り除く |
| stb_image で、日本語のパスの画像が読めない | `stbi_load` が内部で `fopen`（ANSI）を使う | ファイルをメモリに読んで `stbi_load_from_memory` |
| FMOD / SDL で、日本語のファイル名が開けない | UTF-8 を期待するのに、ANSI を渡した（またはその逆） | 各ライブラリの仕様を確認（[外部ライブラリと文字コード](libraries.md)） |

## 調べ方

原因が推測できないときは推測を重ねず**実際のバイト列を見ます**。文字コードはバイト列の約束事にすぎないので、バイト列を見ればどの文字コードで書かれているかがほぼ判断できます。手順はバイトを見る → バイトから文字コードを判断する → 流れをたどる、の 3 段階です。

### 1. バイトを見る

文字化けを調べる一番確実な方法は実際のバイトを 16 進数で見ることです。

| 見るもの | 方法 |
| --- | --- |
| ファイル | VS Code の拡張機能（Hex Editor）、`xxd file`、`certutil -encodehex file out.txt`（Windows）、PowerShell の `Format-Hex file` |
| 文字列（メモリ上） | Visual Studio のメモリ ウィンドウ（デバッグ中）、ウォッチで `str,s8`（UTF-8 として見る）、`str,su`（UTF-16） |
| ファイルの文字コードの推定 | `file -i file`（Git Bash など）、VS Code の右下、Notepad++ のメニュー |

### 2. バイトから文字コードを判断する

| バイト | 意味 |
| --- | --- |
| `E3 81 82` | UTF-8 の「あ」 |
| `82 A0` | Shift_JIS（CP932）の「あ」 |
| `42 30` | UTF-16 リトル エンディアン（Windows の `wchar_t`）の「あ」（U+3042 が、下位バイトから並ぶ） |
| 先頭 `EF BB BF` | UTF-8 の BOM |
| 先頭 `FF FE` | UTF-16 LE の BOM |
| `E3` `E4` `E5` `E6` `E7` `E8` `E9` が多い | UTF-8 の日本語（ひらがな・カタカナは `E3`、漢字の多くは `E4`〜`E9`） |
| `82` `83` `88`〜`9F` `E0`〜`EA` が、2 バイトずつ | Shift_JIS の日本語 |

### 3. 流れをたどる

データがどこを通って画面に出るか1 段階ずつ確認します。

```text
① ソースファイルの保存形式（UTF-8？ Shift_JIS？） 
② コンパイラの読み方（/utf-8 の有無）
③ 実行時の文字列のバイト（デバッガーで確認）
④ API・ライブラリに渡すとき（A / W、UTF-8 / UTF-16）
⑤ 画面・ファイルへの出力（コンソールのコード ページ、フォント）
```

途中のどこで最初におかしくなるかを見つけて、そこを直します。

### 4. 最小の再現を作る

```cpp
#include <print>
#include <string>

int main() {
  std::string s = "あ";
  // バイトを、16 進数で表示する
  for (unsigned char c : s) {
    std::print("{:02X} ", c);
  }
  std::println("({} バイト)", s.size());
}
```

| 出力 | 意味 |
| --- | --- |
| `E3 81 82 (3 バイト)` | UTF-8（`/utf-8` が効いている） |
| `82 A0 (2 バイト)` | Shift_JIS（`/utf-8` が効いていない） |

これだけでソースとコンパイラの設定が、正しいか分かります。

## チェックリスト（上から順に）

1. [ ] **`/utf-8`** が、全構成・全プラットフォームで設定されているか（コマンド ラインで確認）
2. [ ] ソースがUTF-8（`.editorconfig`、`/we4828` で確認）か
3. [ ] ファイルの読み書きは、UTF-8・バイナリ モードか。BOM を扱っているか
4. [ ] Windows API は、`W` 版を呼び UTF-8 → UTF-16 の変換をしているか
5. [ ] 日本語のパスは、`std::filesystem::path`（`u8` から）か `W` 版か
6. [ ] コンソールは`std::println` か `SetConsoleOutputCP(CP_UTF8)` か
7. [ ] ライブラリがUTF-8 を期待しているか（ImGui、JSON、SDL）、`wchar_t*` か（DirectX）
8. [ ] フォントにその文字があるか（ImGui）
9. [ ] 開発 PC 以外（別の地域設定、日本語のユーザー名）で確認したか

## ゲームでの使いどころ

| 場面 | 方法 |
| --- | --- |
| 新しい環境で初めて日本語を出す | 上の「最小の再現」で、UTF-8 のバイトを確認する |
| 配布前のテスト | **日本語のユーザー名**、日本語のインストール先で起動・セーブ・ロードを試す |
| 他人のファイル（MOD、アセット）の取り込み | 文字コードを検証して、UTF-8 に変換してから使う |
| ログに化けた日本語が出た | ログの該当バイトを 16 進数で確認する |

<!-- fig:mojibake-decode:begin -->

<svg class="fig illust motion" data-fig="mojibake-decode" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-mojibake-decode" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">同じバイト列でも、読み方を間違えると別の文字になる</text>
<text x="70" y="90" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">ファイルに入っているバイト列（UTF-8 で保存した「こんにちは」）</text>
<rect x="70" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="89" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">E3</text>
<rect x="112" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="131" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">81</text>
<rect x="154" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="173" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">93</text>
<rect x="196" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="215" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">E3</text>
<rect x="238" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="257" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">82</text>
<rect x="280" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="299" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">93</text>
<rect x="322" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="341" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">E3</text>
<rect x="364" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="383" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">81</text>
<rect x="406" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="425" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">AB</text>
<rect x="448" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="467" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">E3</text>
<rect x="490" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="509" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">81</text>
<rect x="532" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="551" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">A1</text>
<rect x="574" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="593" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">E3</text>
<rect x="616" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="635" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">81</text>
<rect x="658" y="105" width="38" height="32" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="677" y="127" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">AF</text>
<text x="70" y="205" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2ea043" opacity="0">UTF-8 として読む → こんにちは<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;1.0000" values="0;0;1;1"/></text>
<text x="70" y="235" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">正しい。ソースも保存形式も UTF-8 なら、こう読まれる<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;1.0000" values="0;0;1;1"/></text>
<text x="70" y="300" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">Shift_JIS (CP932) として読む → 縺薙ｓ縺ｫ縺｡縺ｯ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000" values="0;0;1;1"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">バイトは同じ。読む側の文字コードが違うだけで、文字化けになる(データは壊れていない)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000" values="0;0;1;1"/></text>
</svg>

<!-- fig:mojibake-decode:end -->

## よくあるミス

??? failure "化けた文字を手で直して、原因を放置する"
    その場しのぎで保存し直すと別の場所でまた化けます。流れをたどって**食い違いの原因**を直します。

??? failure "`?` になったデータを直そうとする"
    `?` や `�` になった時点で、元の情報は失われています。変換する前のデータに戻って、変換の仕方を直します。

??? failure "文字コードをエディターの表示だけで判断する"
    エディターが自動で「それらしい」文字コードを選んで、正しく見えることがあります。バイトを見るか複数のツールで確認します。

??? failure "自分の PC では動くので、問題ないと思う"
    日本語版 Windows の既定（CP932）に偶然合っているだけのことがあります。別のロケール、日本語のユーザー名の PC で、壊れます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>化け方のパターン</strong>で、原因を絞る（「縺」＝ UTF-8 を Shift_JIS で読んだ）
    - [x] バイトを見る（`E3 81 82` ＝ UTF-8、`82 A0` ＝ Shift_JIS）
    - [x] データの流れ（ソース → コンパイラ → 実行 → API → 画面）を、1 段階ずつ確認
    - [x] `?` / `�` になったら、元には戻らない。変換前に戻って直す
    - [x] 日本語のユーザー名・別の PC でテストする

## 関連ページ

- [文字コード（目次）](index.md)
- [文字コードの基礎](unicode-basics.md)
- [ソースファイルの文字コードと強制](source-files.md)
- [Windows API と文字コード](windows-api.md)
- [Visual Studio：よくあるエラー](../vs/errors.md#mojibake)
