---
title: .editorconfig（エディターの設定をそろえる）
tags:
  - Visual Studio
---

# .editorconfig（エディターの設定をそろえる）

`.editorconfig` は <strong>エディターがファイルを開いたり保存したりするときの決まりを、テキストファイル 1 つに書いておく</strong>仕組みです。文字コード、改行、字下げ行末の空白などをプロジェクトのフォルダーに置いておくと <strong>誰が、どのエディターで開いても同じ決まり</strong>で扱われます。Visual Studio は、標準で対応しています。

!!! tip "ポイント"
    - `.editorconfig` はリポジトリに入れる、ただのテキストファイル。書いた場所とその下のフォルダーに効く
    - 先頭に `root = true`、そのあとに `[*]` のようなセクションを書き、セクションごとに設定を並べる
    - 設定できるのは文字コード・改行・字下げ・行末の空白・最終行の改行。Visual Studio には、C++ 用の独自の設定もある
    - <strong>下のセクションが、上のセクションを上書きする</strong>。近いフォルダーの `.editorconfig` が遠いものを上書きする
    - 行の途中にコメント（`# …`）を書いてはいけない。コメントは行頭だけ
    - 反映されるのは <strong>保存したとき</strong>（ファイルを開いただけでは、中身は変わらない）

## このページを読む前に

- [文字コードを UTF-8 にしよう](utf8.md)（`charset = utf-8` だけを書く、最小の例）

## .editorconfig で、何が解決するのか {#why}

チームで開発すると次のような、小さな食い違いが積もっていきます。

| 起きること | 原因 |
| --- | --- |
| 差分に変更していない行が、大量に出る | 人によって改行（CRLF と LF）が違う |
| コードの字下げが行ごとに、ばらばら | タブとスペースが、混ざっている。人によって字下げの幅が違う |
| 日本語が人によって化ける | 保存した文字コードが、人によって違う |
| 行末の空白で差分が汚れる | 人によって、保存時の空白の扱いが違う |
| 最後の行に改行がなく `\ No newline at end of file` が出る | エディターによって、最後の改行の扱いが違う |

「<strong>設定は人のエディターに任せず、リポジトリに書いて共有する</strong>」というのが、`.editorconfig` の考え方です。コードの書き方を言葉で伝える代わりに、<strong>エディターに守らせます</strong>。

## 最小の書き方 {#basic}

```ini
# MyGame/.editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2
```

| 部分 | 意味 |
| --- | --- |
| `# …` | コメント。<strong>行の先頭</strong>にだけ書ける |
| `root = true` | このファイルが一番上であることを示す。これより上のフォルダーの `.editorconfig` は、探さない |
| `[*]` | セクション。`[...]` の中は <strong>ファイル名のパターン</strong>。`*` はすべてのファイル |
| `キー = 値` | そのセクションに、当てはまるファイルへの設定 |

ファイルの置き場所はソリューションと同じフォルダー（Git の、一番上のフォルダー）が一般的です。Visual Studio では、ソリューション エクスプローラーで、ソリューションを右クリック → <strong>追加 → 新しい項目 →「エディターの構成ファイル（.editorconfig）」</strong>でも作れます。

## 設定できる項目 {#properties}

| キー | 値 | 意味 |
| --- | --- | --- |
| `root` | `true` | 一番上の `.editorconfig` であること（ファイルの先頭に、1 回） |
| `charset` | `utf-8`、`utf-8-bom`、`utf-16le`、`utf-16be`、`latin1` | 保存するときの文字コード |
| `end_of_line` | `lf`、`crlf`、`cr` | 改行の種類 |
| `insert_final_newline` | `true`、`false` | ファイルの最後の行にも、改行を入れるか |
| `trim_trailing_whitespace` | `true`、`false` | 行末の空白を消すか |
| `indent_style` | `space`、`tab` | 字下げにスペースを使うか、タブを使うか |
| `indent_size` | 数（`2`、`4`）、または `tab` | 字下げの幅 |
| `tab_width` | 数 | タブの表示の幅（既定は、`indent_size`） |
| `max_line_length` | 数、または `off` | 1 行の最大の長さ（エディターによって、使われ方が違う。目安として書く） |

値の大文字と小文字は区別されません（`LF` でも `lf` でも同じ）。

### charset

| 値 | 意味 | このサイトの推奨 |
| --- | --- | --- |
| `utf-8` | UTF-8（BOM なし） | <strong>ソース、シェーダー、設定ファイルはこれ</strong> |
| `utf-8-bom` | UTF-8（BOM あり） | CSV を Excel で開くなど、特別な場合だけ |
| `utf-16le` | UTF-16（リトル エンディアン） | `.rc` ファイルなど、必要なものだけ |

### end_of_line

| 値 | 意味 | 使いどころ |
| --- | --- | --- |
| `lf` | `\\n` | Git のリポジトリの中の標準。Linux・macOS・CI |
| `crlf` | `\\r\\n` | Windows の、バッチ ファイル（`.bat`、`.cmd`）、`.sln` |
| `cr` | `\\r` | ほぼ使わない（古い Mac） |

### indent_style と indent_size

| 組み合わせ | 動き |
| --- | --- |
| `indent_style = space`、`indent_size = 2` | Tab キーを押すと、スペースが 2 つ入る。このサイトの Google C++ Style |
| `indent_style = space`、`indent_size = 4` | スペース 4 つ |
| `indent_style = tab`、`indent_size = tab`、`tab_width = 4` | タブ文字を入れる。表示の幅は 4 |

<strong>Makefile はタブが必須</strong>です（スペースだと、動きません）。ファイルの種類ごとの書き分けで、`[Makefile]` だけ `indent_style = tab` にします（次の節）。

## セクション：ファイルの種類ごとに、書き分ける {#sections}

`[...]` の中に <strong>ファイル名のパターン</strong>を書きます。パターンに当てはまるファイルだけに、設定が効きます。

```ini
root = true

# すべてのファイル
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# C++ のソースと、ヘッダー
[*.{cpp,h,hpp,inl}]
indent_style = space
indent_size = 2

# シェーダー
[*.{hlsl,hlsli,fx}]
indent_style = space
indent_size = 2

# JSON、YAML、XML（Visual Studio のプロジェクト ファイルも）
[*.{json,yml,yaml,xml,vcxproj,props,targets,filters}]
indent_size = 2

# Windows のバッチと、ソリューションは CRLF
[*.{bat,cmd,sln,slnx}]
end_of_line = crlf

# Markdown は、行末の空白が意味を持つことがある（行末の 2 つのスペース = 改行）
[*.md]
trim_trailing_whitespace = false

# Makefile は、タブが必須
[Makefile]
indent_style = tab
```

### パターンの書き方

| パターン | 意味 | 例 |
| --- | --- | --- |
| `*` | `/` 以外の任意の文字列 | `*.cpp`（すべての `.cpp`） |
| `**` | `/` も含む任意の文字列（フォルダーをまたぐ） | `**/Generated/*.cpp` |
| `?` | 任意の 1 文字 | `file?.txt` |
| `[abc]` | `a`、`b`、`c` のどれか 1 文字 | `[Mm]akefile` |
| `{a,b,c}` | `a`、`b`、`c` のどれか | `*.{cpp,h}` |
| `{1..5}` | 1 から 5 までの数 | `log{1..5}.txt` |

注意点です。

- パターンの <strong>`{ }` の中でカンマの後ろに、スペースを入れない</strong>（`*.{cpp, h}` は、`h` の前にスペースが付いた別の名前になる）
- パス区切りは `/` だけ（Windows でも、`\\` を使わない）
- `/` を含まないパターン（`*.cpp`）は、<strong>その `.editorconfig` の下のすべてのフォルダー</strong>の、ファイルに当てはまる。`/` を含むパターン（`src/*.cpp`）は `.editorconfig` の位置から、見た相対パスとして当てはめる

### 上書きの規則

- <strong>1 つのファイルの中では、下のセクションが上のセクションを、上書き</strong>します（同じキーについて）
- 複数のセクションに当てはまるファイルは、<strong>当てはまるすべての設定が順に適用</strong>され、同じキーでは最後に書かれたものが勝つ
- そのため、<strong>一般的なものを上に特別なものを、下に</strong>並べる

```ini
[*]
indent_size = 4           # すべてのファイルは、4

[*.{cpp,h}]
indent_size = 2           # ↑ これは、コメントではなく、値の一部になってしまう！（下の注意を見る）
```

!!! failure "行の途中に、コメントを書かない"
    `indent_size = 2   # 注意` のように <strong>値の後ろに、コメントを書くと `#` 以降も値の一部</strong>として扱われます（仕様の、新しい版で行の途中のコメントは、廃止されました）。値が `2   # 注意` という文字列になって、設定が無効になります。<strong>コメントは必ず独立した行に書きます。</strong>

## フォルダーごとの階層 {#hierarchy}

`.editorconfig` は <strong>複数のフォルダーに置けます</strong>。エディターは開いたファイルの、フォルダーから <strong>上へ向かって順に</strong>、`.editorconfig` を探し <strong>`root = true` を持つファイルに当たったら、そこで探すのをやめます</strong>。

```text
MyGame/
├── .editorconfig               ← root = true。全体の決まり
├── Game/
│   └── player.cpp              ← MyGame/.editorconfig が、効く
└── ThirdParty/
    ├── .editorconfig           ← このフォルダー用の、上書き
    └── lib/
        └── foo.cpp             ← ThirdParty/.editorconfig と MyGame/.editorconfig の両方
```

| ルール | 内容 |
| --- | --- |
| 近いものが勝つ | `ThirdParty/.editorconfig` の設定は `MyGame/.editorconfig` の、同じキーを上書きする |
| `root = true` で止まる | ファイルの先頭に、`root = true` と書いてあるとそれより上の `.editorconfig` は、読まれない |
| 一番上だけ `root = true` | 下のフォルダーの `.editorconfig` には、`root = true` を書かない（書くと上の設定が、効かなくなる） |

### 外部ライブラリを触らないようにする

`ThirdParty` に <strong>ほかの人が書いたコード</strong>（外部ライブラリ）を、置くことが多いです。自分たちの決まり（字下げ行末の空白）で、勝手に整形すると <strong>ライブラリを更新するたびに、差分が増えます</strong>。そのフォルダーでは設定を解除（`unset`）します。

```ini
# MyGame/ThirdParty/.editorconfig
# root は書かない（上の設定を、引き継いだうえで、一部を解除する）

[*]
indent_style = unset
indent_size = unset
end_of_line = unset
trim_trailing_whitespace = unset
insert_final_newline = unset
```

`unset` は「その設定を取り消して、<strong>エディターの既定に戻す</strong>」という意味です。

## Visual Studio の C++ 独自の設定 {#cpp}

`.editorconfig` の標準の項目に加えて Visual Studio は、<strong>C++ のコードの整形</strong>に関する、独自の設定を読みます。名前が `cpp_` で始まります。

| キー | 値 | 意味 |
| --- | --- | --- |
| `cpp_indent_braces` | `true`、`false` | 波括弧 `{ }` を字下げするか |
| `cpp_indent_case_contents` | `true`、`false` | `switch` の `case` の中身を字下げするか |
| `cpp_indent_case_labels` | `true`、`false` | `case` ラベル自体を `switch` から字下げするか |
| `cpp_indent_access_specifiers` | `true`、`false` | `public:` などをクラスから字下げするか |
| `cpp_indent_namespace_contents` | `true`、`false` | `namespace` の中身を字下げするか |

Google C++ Style に合わせた例です（`namespace` の中は、字下げしない）。

```ini
[*.{cpp,h,hpp,inl}]
indent_style = space
indent_size = 2
cpp_indent_namespace_contents = false
cpp_indent_case_contents = true
cpp_indent_case_labels = false
cpp_indent_access_specifiers = false
```

!!! note "C++ の整形は、.clang-format が優先されることがある"
    Visual Studio は、プロジェクトの近くに <strong>`.clang-format`</strong> があると、C++ の整形にそれを使います（ClangFormat のサポートが、有効なとき）。この場合、`cpp_` で始まる設定や `indent_size` は <strong>整形（Ctrl + K, Ctrl + D）では、使われなくなる</strong>ことがあります。`.editorconfig` は <strong>文字コード・改行・最終行の改行</strong>を `.clang-format` は、<strong>コードの見た目の整形</strong>をそれぞれ担当させると役割が、分かれて衝突しません（[ソースファイルの文字コードと強制](../encoding/source-files.md)）。

### 設定から `.editorconfig` を作る

Visual Studio には、いま使っているエディターの設定から、`.editorconfig` を<strong>書き出す</strong>機能があります。メニューの「ツール → オプション → テキスト エディター → C/C++ → コード スタイル」のあたりにあります（バージョンによって、場所と名前が違います）。自分の好みに合わせた初期の `.editorconfig` が欲しいときの、出発点になります。

## 効いているか確かめる {#check}

| 方法 | 内容 |
| --- | --- |
| 保存して確かめる | ファイルを、少し編集して保存する。`git diff` で行末の空白や改行がそろったか見る |
| ステータス バー | Visual Studio の下の枠（ステータス バー）に、<strong>字下げ（SPC / TAB）と、改行（CRLF / LF）</strong>が、表示される。`.editorconfig` が効いていれば設定どおりの表示になる |
| `git ls-files --eol` | Git に入っている改行と、作業フォルダーの改行を一覧表示する |
| `editorconfig` コマンド | 公式のコマンド ライン ツール。`editorconfig path/to/file.cpp` でそのファイルに効いている設定が、表示される |

```bash
# ファイルに、実際に効く設定を表示する（editorconfig コマンド ライン ツールを入れたとき）
editorconfig Game/player.cpp
```

### 効かないとき

| 症状 | 見るところ |
| --- | --- |
| まったく効かない | `.editorconfig` の置き場所。ソースファイルの <strong>上のフォルダー</strong>にあること |
| 一部のファイルだけ効かない | セクションの、パターンが合っているか（`{ }` の中の、カンマの後のスペース） |
| 設定が無視される | 行の途中に、コメントがないか。`キー = 値` の書き方の間違い（`=` の前後は、スペースがあってもよい） |
| 上のフォルダーの設定が効かない | 下のフォルダーの `.editorconfig` に、`root = true` が書かれていないか |
| 開いただけでは変わらない | 仕様です。<strong>保存したとき</strong>に文字コードなどが、そろう |
| 設定をまったく無視する | Visual Studio の、「ツール → オプション → テキスト エディター → 全般」にある、<strong>プロジェクトのコーディング規約に従う</strong>（Follow project coding conventions）が、<strong>オフ</strong>になっている |

## 既存のファイルをそろえる {#apply-existing}

`.editorconfig` を後から入れたとき <strong>すでにあるファイル</strong>は、自動では変わりません。次の方法でそろえます。

| 方法 | 内容 |
| --- | --- |
| 開いて保存し直す | 1 ファイルずつ。少ないときはこれで十分 |
| 整形スクリプト | まとめて、改行・行末の空白・最終行の改行を、直す |
| `.gitattributes` で改行をそろえる | 改行だけは、Git の側で一括してそろえられる（[文字コードを UTF-8 にしよう](utf8.md#gitattributes)） |

<strong>一括で変えるときは先にコミット</strong>しておき、<strong>1 つの専用のコミット</strong>にします。文字コードや改行を変えるコミットと、機能を変えるコミットを混ぜるとあとで、差分が読めなくなります。

!!! tip "整形だけの、コミットを `git blame` から外す"
    大量の整形をした後、`git blame` がすべてそのコミットになってしまうのが、困ります。<strong>`.git-blame-ignore-revs`</strong> ファイルに整形コミットの ID を書いて、`git config blame.ignoreRevsFile .git-blame-ignore-revs` を設定すると `git blame` がそのコミットを、飛ばします（GitHub も、このファイルを認識します）。

## CI で守らせる {#ci}

`.editorconfig` は <strong>エディターが守る</strong>ものです。エディターが対応していない人や設定を、オフにした人のファイルはそのまま、入ってしまいます。そこで、<strong>CI（自動ビルド）で検査</strong>します。

| ツール | 内容 |
| --- | --- |
| `editorconfig-checker` | `.editorconfig` の設定に <strong>ファイルが、従っているか</strong>を検査するコマンド（Go 製の、実行ファイル 1 つ） |
| `git diff --check` | 行末の空白など基本的な、空白の問題を見つける（Git に、標準で付いている） |

```yaml
# .github/workflows/lint.yml（抜粋）
- name: .editorconfig の検査
  uses: editorconfig-checker/action-editorconfig-checker@main
- run: editorconfig-checker
```

文字コード（UTF-8、BOM なし）の検査と `clang-format` による整形の検査は、[ソースファイルの文字コードと強制](../encoding/source-files.md) で説明しています。

## Visual Studio 以外のエディターで

`.editorconfig` は特定のエディターの機能ではなく、<strong>共通の規格</strong>です。

| エディター | 対応 |
| --- | --- |
| Visual Studio | 標準で、対応（C++ の独自設定も） |
| Visual Studio Code | <strong>拡張機能「EditorConfig for VS Code」</strong>を、入れると対応する |
| JetBrains（CLion、Rider など） | 標準で、対応 |
| Vim、Emacs、Sublime Text など | プラグインで、対応 |

チームの全員が同じエディターを、使っていなくても <strong>同じ決まり</strong>で、保存できます。

## 実際の `.editorconfig` の例（ゲームのリポジトリ） {#example}

```ini
# MyGame/.editorconfig
root = true

# すべてのファイル: UTF-8（BOM なし）、LF、最終行に改行、行末の空白を削る
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

# C++（Google C++ Style）
[*.{cpp,h,hpp,inl}]
cpp_indent_namespace_contents = false
cpp_indent_case_contents = true
cpp_indent_case_labels = false
cpp_indent_access_specifiers = false

# シェーダー
[*.{hlsl,hlsli,fx}]
indent_size = 2

# CMake
[{CMakeLists.txt,*.cmake}]
indent_size = 2

# Windows のファイルは CRLF
[*.{bat,cmd,sln,slnx}]
end_of_line = crlf

# Visual Studio のプロジェクト ファイルは、Visual Studio が書き換える。CRLF のまま
[*.{vcxproj,props,targets,filters}]
end_of_line = crlf
indent_size = 2

# Markdown は、行末の空白が、意味を持つ
[*.md]
trim_trailing_whitespace = false

# Makefile は、タブが必須
[Makefile]
indent_style = tab
```

## よくあるミス

??? failure "`.editorconfig` を置いたのに、既存のファイルが変わらない"
    `.editorconfig` は <strong>保存するとき</strong>に、効きます。開いただけでは中身は変わりません。まとめてそろえるなら整形スクリプトを使うか、`.gitattributes` で改行をそろえます。

??? failure "値の後ろに、コメントを書いたら設定が無視された"
    行の途中に書いた `# …` は、コメントとして扱われません。値の一部になります。コメントは行の先頭に書きます。

??? failure "Markdown の行末の、2 つのスペース（改行）が消えた"
    `trim_trailing_whitespace = true` が Markdown にも、効いています。`[*.md]` のセクションで `false` にします。

??? failure "`.sln` や `.vcxproj` が、保存のたびに差分になる"
    Visual Studio は、これらのファイルを CRLF で、書き出します。`[*]` の `end_of_line = lf` がこれらにも効いていると改行が、行き来して差分が出ます。`[*.{sln,vcxproj,props,targets,filters}]` で `end_of_line = crlf` を指定します。

??? failure "外部ライブラリを、整形してしまった"
    `ThirdParty` などのフォルダーに、`.editorconfig` を置いて設定を `unset` にします。または、そのフォルダーを整形の対象から、外します。

??? failure "ほかのフォルダーの `.editorconfig` が、効かなくなった"
    下のフォルダーの `.editorconfig` に `root = true` が、書いてあります。上の設定を引き継ぎたいなら `root = true` を、消します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `.editorconfig` はエディターの保存の決まりを、ファイルに書いて共有する仕組み
    - [x] `root = true` の下に `[パターン]` と、`キー = 値` を並べる
    - [x] 設定できるのは `charset`、`end_of_line`、`indent_style`、`indent_size`、`trim_trailing_whitespace`、`insert_final_newline`
    - [x] ファイルの種類ごとに、セクションで書き分ける。下が上を上書きする
    - [x] コメントは、行頭だけ。値の後ろに書かない
    - [x] 保存したときに効く。CI でも検査する

## 関連ページ

- [文字コードを UTF-8 にしよう](utf8.md)
- [便利な機能とショートカット](tips.md)
- [ソースファイルの文字コードと強制](../encoding/source-files.md)
- [Visual Studio の目次](index.md)
