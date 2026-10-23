---
title: ソースファイルの文字コードと強制
tags:
  - 文字コード
---

# ソースファイルの文字コードと強制

ソースコードのファイルを、**どの文字コードで保存するか**は、チームで開発するとき、必ず決めて、強制しておくべき決まりです。決めていないと、「ある人は Shift_JIS、ある人は UTF-8」になり、Git の差分が全部変わったり、コンパイラが文字化けのままビルドしたり、「自分の PC では動くのに、他の人は化ける」という事故が起きます。人の注意に頼ると必ず誰かが間違えるので、設定ファイル（`.editorconfig`、`.gitattributes`、`.clang-format`）、コンパイラのオプション、CI（自動チェック）で、機械的に強制します。このページでは、その方法を一つずつ説明します。

!!! tip "ポイント"
    - 決まり: <strong>UTF-8（BOM なし）、改行は LF</strong>。MSVC には <strong>`/utf-8`</strong>。
    - `.editorconfig` で、エディターに「保存は UTF-8」と教える（Visual Studio も読む）。
    - `.gitattributes` で、改行を LF に統一する。
    - clang-format は、文字コードを変換・強制しない（UTF-8 を前提に整形する）。強制できるのは、改行（`LineEnding`）と最後の改行（`InsertNewlineAtEOF`）。
    - 文字コードの強制は、MSVC の警告をエラーにする（`/we4819 /we4828`）と、CI のチェック スクリプトで行う。
    - 設定ファイルは、リポジトリに入れる。

## 決まりを決める

| 項目 | 決まり |
| --- | --- |
| 文字コード | <strong>UTF-8（BOM なし）</strong> |
| 改行 | LF（Windows 専用の `.bat` などだけ CRLF） |
| ファイル末尾 | 改行で終わる |
| 字下げ | スペース（Google C++ Style は 2 つ） |
| 末尾の空白 | 削除する |
| MSVC のオプション | `/utf-8` |

## 1. コンパイラ：/utf-8

MSVC は**ソースファイルを既定で ANSI（日本語版は CP932）として読みます**。BOM のない UTF-8 ファイルを、CP932 と誤解して、文字化けしたり、コンパイル エラーになったりします。`/utf-8` は、ソースの文字コードと実行時の文字列の文字コードを、両方 UTF-8 にします。

```text
/utf-8   =   /source-charset:utf-8   +   /execution-charset:utf-8
```

| オプション | 意味 |
| --- | --- |
| `/source-charset:utf-8` | ソースファイルを、UTF-8 として読む |
| `/execution-charset:utf-8` | `"..."` リテラルを、UTF-8 のバイトにする |
| `/utf-8` | 上の 2 つを両方 |

設定場所: プロパティ → C/C++ → コマンド ライン → 追加のオプション に `/utf-8`（すべての構成・すべてのプラットフォームで）。CMake なら:

```cmake
if(MSVC)
  target_compile_options(MyGame PRIVATE /utf-8)
endif()
```

### 文字コードの間違いを、エラーにする

`/utf-8` を付けても、ファイルが Shift_JIS で保存されていると、変換できない部分が出ます。そのときの警告をエラーにして、ビルドを止めます。

| 警告 | 意味 | エラーにする |
| --- | --- | --- |
| C4819 | ファイルは現在のコード ページ（932）で表示できない文字を含んでいます（`/utf-8` なしで、UTF-8 を読んだとき） | `/we4819` |
| C4828 | ファイルに現在のソース文字集合で不正な文字があります（`/utf-8` ありで、UTF-8 でないバイトを読んだとき） | `/we4828` |

```cmake
if(MSVC)
  target_compile_options(MyGame PRIVATE /utf-8 /we4819 /we4828)
endif()
```

UTF-8 でないファイルが混ざると、ビルドが失敗するので人が気づけます。これがコンパイラ側でできる、一番確実な強制です。

## 2. .editorconfig（エディターの設定）

**`.editorconfig`** は、エディターに「このプロジェクトの書き方」を伝える設定ファイルです。Visual Studio（2017 以降）、VS Code、CLion などが読んでくれます。リポジトリの一番上に置きます。

```ini
# .editorconfig
root = true

[*]
# 保存は UTF-8（BOM なし）
charset = utf-8
# 改行は LF
end_of_line = lf
# 最後に改行を入れる
insert_final_newline = true
# 行末の空白を削る
trim_trailing_whitespace = true
# 字下げはスペース
indent_style = space
indent_size = 2

[*.{bat,cmd}]
# Windows のバッチだけ CRLF
end_of_line = crlf

[*.md]
# Markdown は行末の空白が意味を持つことがある
trim_trailing_whitespace = false
```

| 項目 | 値 | 意味 |
| --- | --- | --- |
| `charset` | `utf-8` | UTF-8（BOM なし） |
| | `utf-8-bom` | UTF-8（BOM あり） |
| | `utf-16le` / `utf-16be` / `latin1` | ほかの文字コード |
| `end_of_line` | `lf` / `crlf` / `cr` | 改行コード |
| `insert_final_newline` | `true` | 最後に改行を入れる |
| `trim_trailing_whitespace` | `true` | 行末の空白を消す |
| `indent_style` / `indent_size` | `space` / `2` | 字下げ |

!!! warning "editorconfig の限界"
    `.editorconfig` は、エディターが「新しく保存するとき」に従う設定です。すでに Shift_JIS で保存されているファイルを、勝手には変換しません。また、エディターが対応していないと、無視されます。そのため、`.editorconfig` は「間違いを防ぐ助け」で、強制はコンパイラ（`/we4828`）と CI で行います。

### Visual Studio で既存ファイルを UTF-8 に変換する

| 方法 | 手順 |
| --- | --- |
| 1 ファイルずつ | ファイルを開く → 「ファイル → 名前を付けて保存」の「保存」の横の ▼ → エンコード付きで保存 → Unicode (UTF-8 シグネチャなし) - コードページ 65001 |
| 一括で変換 | 下の「変換スクリプト」（PowerShell / iconv） |
| 事前に確認 | `file -i *.cpp` や、Notepad++ の「エンコード」メニューで今の文字コードを確認する |

Shift_JIS のファイルを、Visual Studio で「UTF-8 として開き直す」と、文字化けしたまま保存されるので、必ず、正しい文字コードで開いてから変換します（「エンコード付きで開く」）。

## 3. .gitattributes（Git の設定）

**`.gitattributes`** は、Git にファイルの扱い（改行の変換など）を教える設定です。

```gitattributes
# .gitattributes
# テキストは、リポジトリでは LF に統一する
* text=auto eol=lf

*.cpp text eol=lf
*.h   text eol=lf
*.hpp text eol=lf
*.json text eol=lf
*.md  text eol=lf

# Windows のバッチは CRLF
*.bat text eol=crlf
# Visual Studio のソリューションは CRLF
*.sln text eol=crlf

# バイナリは、触らない
*.png binary
*.dds binary
*.fbx binary
*.wav binary
```

| 設定 | 意味 |
| --- | --- |
| `text=auto` | Git がテキストかバイナリかを判断する |
| `eol=lf` | チェックアウト時も LF にする（Windows でも） |
| `binary` | 画像や音は改行の変換・差分の対象外 |
| `working-tree-encoding=UTF-16` | 作業フォルダーでは UTF-16、リポジトリでは UTF-8 にする（`.rc` などに使うことがある） |

`.gitattributes` が扱うのは、改行（と、`working-tree-encoding` による変換）です。ファイルが UTF-8 か Shift_JIS かを、検査して止める機能は、ありません。

また、チーム全員で、`git config core.autocrlf` を、`false`（`.gitattributes` に任せる）か、`input` にそろえます。Windows の既定（`true`）のままだと`.gitattributes` と衝突して、混乱します。

## 4. clang-format（整形ツール）

**clang-format** は、ソースを決まった書き方に整形するツールです（Visual Studio は、`.clang-format` ファイルを読んで、Ctrl + K, Ctrl + D などで整形できます）。文字コードを強制・変換する機能は、ありません。clang-format は、ソースが UTF-8 であることを前提に動きます。

### clang-format でできること・できないこと

| 項目 | できるか | 設定 |
| --- | --- | --- |
| 文字コードの変換・強制 | できない | → `.editorconfig`、`/we4828`、CI |
| 改行コード | できる（clang-format 16 以降） | `LineEnding: LF` |
| 最後の改行 | できる（16 以降） | `InsertNewlineAtEOF: true` |
| 字下げ・波括弧・桁数 | できる | `IndentWidth: 2`、`ColumnLimit: 100` |
| 日本語の幅 | 幅を考慮する（全角は 2 桁として、`ColumnLimit` を数える） | 設定不要 |
| 日本語を含む文字列・コメントの整形 | 中身は基本的に変えない | |

```yaml
# .clang-format（Google C++ Style をもとに、改行を LF に統一）
BasedOnStyle: Google
ColumnLimit: 100
IndentWidth: 2
LineEnding: LF                  # clang-format 16 以降。DeriveLF（既存を尊重）もある
InsertNewlineAtEOF: true        # clang-format 16 以降
SortIncludes: CaseSensitive
```

| `LineEnding` の値 | 意味 |
| --- | --- |
| `LF` | 改行をすべて LF にそろえる |
| `CRLF` | すべて CRLF |
| `DeriveLF` | ファイルの中で多い方を使う。同数なら LF |
| `DeriveCRLF` | 同様に同数なら CRLF |

!!! note "古い clang-format では"
    `LineEnding` と `InsertNewlineAtEOF` は、clang-format 16（2023 年）で追加されました。それ以前は、`UseCRLF: false` と `DeriveLineEnding: true` で近いことをしていました。Visual Studio に同梱の clang-format の版は、Visual Studio のバージョンによって違います。古いときは`.editorconfig` と `.gitattributes` に任せます。

### CI で「整形されているか」を検査する

整形し忘れを、CI で止める方法は、clang-format の検査モードです。

```bash
# 整形が必要なファイルがあれば、エラー（終了コード 1）にする
clang-format --dry-run --Werror $(git ls-files '*.cpp' '*.h' '*.hpp')
```

| オプション | 意味 |
| --- | --- |
| `--dry-run`（`-n`） | ファイルを書き換えず、整形が必要な場所だけを報告 |
| `--Werror` | 整形が必要なら、エラーにする |
| `-i` | ファイルをその場で書き換える（手元で整形するとき） |
| `--style=file` | `.clang-format` を使う（既定） |

## 5. CI で文字コードを強制する

**UTF-8 でないファイル、BOM 付きのファイル、CRLF のファイル**を、CI で検出して、マージを止めます。

### チェック スクリプト（bash）

```bash
#!/bin/bash
# tools/check_encoding.sh : UTF-8（BOM なし）、LF であることを確認する
status=0
for f in $(git ls-files '*.cpp' '*.h' '*.hpp' '*.hlsl' '*.json' '*.md' '*.txt' '*.cmake'); do
  # ① UTF-8 として正しいか
  if ! iconv -f UTF-8 -t UTF-8 "$f" > /dev/null 2>&1; then
    echo "UTF-8 ではありません: $f"; status=1
  fi
  # ② BOM が付いていないか（先頭 3 バイトが EF BB BF）
  if [ "$(head -c 3 "$f" | od -An -tx1 | tr -d ' \n')" = "efbbbf" ]; then
    echo "BOM が付いています: $f"; status=1
  fi
  # ③ CRLF が混ざっていないか
  if grep -q $'\r' "$f"; then
    echo "CRLF の改行があります: $f"; status=1
  fi
done
exit $status
```

### GitHub Actions に組み込む

```yaml
# .github/workflows/check.yml
name: check
on: [push, pull_request]
jobs:
  encoding:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check encoding
        run: bash tools/check_encoding.sh
      - name: Check clang-format
        run: |
          sudo apt-get install -y clang-format
          clang-format --dry-run --Werror $(git ls-files '*.cpp' '*.h' '*.hpp')
```

### pre-commit（コミットの前に手元で自動チェック）

pre-commit は、`git commit` の前に、自動でチェック・修正をかけるツールです。

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-byte-order-marker   # UTF-8 の BOM があればエラー
      - id: mixed-line-ending         # 改行の混在を検出（--fix=lf で修正）
        args: [--fix=lf]
      - id: end-of-file-fixer         # 最後に改行を入れる
      - id: trailing-whitespace       # 行末の空白を消す
  - repo: https://github.com/pre-commit/mirrors-clang-format
    rev: v18.1.8
    hooks:
      - id: clang-format              # 整形する
```

`pip install pre-commit` と `pre-commit install` で、有効になります。

## 6. 既存のファイルを、一括で UTF-8 にする

Shift_JIS のファイルが大量にあるときの、変換の手順です。**必ずバックアップ（Git でコミット）してから**行います。

### 確認

```bash
# 文字コードを、一覧で確認する
file --mime-encoding $(git ls-files '*.cpp' '*.h')
# → "charset=utf-8" か "charset=unknown-8bit"（Shift_JIS）などが出る
```

### 変換（iconv）

```bash
# Shift_JIS（CP932）→ UTF-8 に変換して、上書き
for f in $(git ls-files '*.cpp' '*.h'); do
  if ! iconv -f UTF-8 -t UTF-8 "$f" > /dev/null 2>&1; then     # UTF-8 でないものだけ
    iconv -f CP932 -t UTF-8 "$f" > "$f.tmp" && mv "$f.tmp" "$f"
  fi
done
```

### 変換（PowerShell）

```powershell
# Shift_JIS（932）で読んで、UTF-8（BOM なし）で書く
$sjis = [System.Text.Encoding]::GetEncoding(932)
$utf8 = New-Object System.Text.UTF8Encoding($false)    # $false = BOM なし
Get-ChildItem -Recurse -Include *.cpp,*.h | ForEach-Object {
  $text = [System.IO.File]::ReadAllText($_.FullName, $sjis)
  [System.IO.File]::WriteAllText($_.FullName, $text, $utf8)
}
```

!!! warning "UTF-8 のファイルを、もう一度変換しない"
    すでに UTF-8 のファイルを、「Shift_JIS だ」と思って変換すると二重に変換されて、取り返しがつかないほど壊れます。必ず、変換前に文字コードを確認し、UTF-8 のものは飛ばします（上のスクリプトの検査）。

## 7. 追加の設定（Visual Studio）

| 設定 | 場所 | 効果 |
| --- | --- | --- |
| **`.editorconfig` の読み込み** | 自動（プロジェクトのフォルダーにあれば） | 保存時の文字コード・改行・字下げ |
| 改行コードの確認 | 「編集 → 詳細 → 改行コードを統一」 | 混ざっている改行を、LF にそろえる |
| 「保存時にエンコードを確認」 | ツール → オプション → 環境 → ドキュメント | 保存時に文字コードを変換できない文字があると、警告を出す |
| `/utf-8` の確認 | プロパティ → C/C++ → コマンド ライン | 実際に渡されているオプションが見える |

## ゲームでの使いどころ

| 場面 | 方法 |
| --- | --- |
| 新しいリポジトリを作るとき | 最初の コミットで`.editorconfig`、`.gitattributes`、`.clang-format` を入れる |
| チームに、Shift_JIS のファイルが混ざった | `/we4828` と CI で、止める。変換スクリプトで一括変換 |
| 外部のツール・アセットのファイル | 文字コードを確認して、UTF-8 にしてから取り込む |
| シェーダー（`.hlsl`） | <strong>UTF-8（BOM なし）</strong> で保存する。古い `fxc` は、BOM があるとエラーになることがある |
| リソース ファイル（`.rc`） | UTF-8 + `#pragma code_page(65001)`、または UTF-16 |
| JSON・YAML のデータ | UTF-8（BOM なし）。パーサーが、BOM で失敗する |

## よくあるミス

??? failure "「clang-format をかければ、文字コードも直る」と思う"
    clang-format は、文字コードを変換しません。UTF-8 でないファイルを渡すと、整形が壊れたり、エラーになったりします。文字コードは`.editorconfig` とスクリプトで管理します。

??? failure "`/utf-8` を付けたのに、Shift_JIS のファイルがビルドされてしまう"
    ファイルが Shift_JIS のまま、不正な UTF-8 として読まれ、警告 C4828 が出るだけで、ビルドが通ってしまいます。`/we4828` でエラーにします。

??? failure "BOM の有無が、人によってバラバラ"
    Visual Studio の既定の保存と、他のエディターで、BOM の有無が変わります。`.editorconfig` に `charset = utf-8`（BOM なし）と書き、CI で BOM を検出します。

??? failure "Git で、改行が全行変わる"
    `core.autocrlf` の設定が、人によって違うためです。`.gitattributes` で、`* text=auto eol=lf` に統一し、全員で `autocrlf` をそろえます。

??? failure "editorconfig をリポジトリに入れていない"
    自分の PC にだけ置いても、チームには伝わりません。リポジトリのルートにコミットします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 決まり: UTF-8（BOM なし）・LF・`/utf-8`
    - [x] `.editorconfig`（保存の文字コード）+ `.gitattributes`（改行）をリポジトリに入れる
    - [x] clang-format は文字コードを強制しない。強制できるのは改行（`LineEnding`）と整形
    - [x] `/we4828` で、UTF-8 でないソースをビルド エラーにする
    - [x] CI のチェック スクリプトと pre-commit で、BOM・文字コード・改行・整形を検査する
    - [x] 変換は、文字コードを確認してから。UTF-8 を二重に変換しない

## 関連ページ

- [文字コード（目次）](index.md)
- [文字コードの基礎](unicode-basics.md)
- [文字化けのトラブルシューティング](mojibake.md)
- [Visual Studio：C++23 の設定](../vs/settings.md)
- [Visual Studio：便利な機能（editorconfig・clang-format）](../vs/tips.md)
- [命名とコーディング規約](../design/foundations/naming.md)
