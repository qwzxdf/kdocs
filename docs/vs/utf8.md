---
title: 文字コードを UTF-8 にしよう
tags:
  - Visual Studio
  - 文字コード
---

# 文字コードを UTF-8 にしよう

日本語のコメントや文字列をソースに書くと、Visual Studio では「エディターでは読めるのに、実行すると文字化けする」「`warning C4819` が出る」といったことが起きます。原因はほとんどの場合、<strong>ファイルが UTF-8 で保存されているのに、コンパイラは Shift_JIS（CP932）として読んでいる</strong>ことです。このページでは、**コンパイラ（`/utf-8`）・エディター（`.editorconfig`）・Git（`.gitattributes`）・実行時のコンソール**の 4 か所を、順に UTF-8 にそろえます。

!!! tip "ポイント"
    - 文字コードは、<strong>「ファイルを保存する人」「コンパイラ」「実行する画面」の 3 者</strong>がそろわないと化ける。1 か所でも違うと化ける
    - コンパイラには <strong>`/utf-8`</strong> を付ける（C/C++ → コマンド ライン → 追加のオプション）。これでソースの読み方と、文字列リテラルの中身が、どちらも UTF-8 になる
    - 保存するときは <strong>UTF-8（BOM なし）</strong>。`.editorconfig` に `charset = utf-8` と書くと、Visual Studio が保存時にそろえてくれる
    - 改行は LF にそろえておくと、Git で差分が荒れない。`.gitattributes` で決める
    - 正しく設定できたか、`static_assert(sizeof("あ") == 4)` で確かめられる

## このページを読む前に

- [C++23 を使えるようにする設定](settings.md)（プロパティ画面の開き方、「すべての構成」に切り替える理由）
- [インストールとプロジェクトの作成](setup.md)

文字コードそのもの（Unicode、UTF-8 と UTF-16 の違い、Windows API の A と W、変換）は、[文字コード](../encoding/index.md) のカテゴリで詳しく解説しています。このページは、Visual Studio の画面で、手を動かして設定する側に絞っています。

## 何が起きているのか：3 者の食い違い {#why}

画面に日本語が出るまでに、文字コードが関わる場面は 3 つあります。

| 場面 | 誰が決めるか | 食い違うと |
| --- | --- | --- |
| ① ソースファイルを<strong>保存</strong>する | エディター（Visual Studio の保存設定、`.editorconfig`） | 保存時のコードと、コンパイラの想定がずれる |
| ② ソースファイルを<strong>読む</strong>、文字列リテラルをバイト列にする | コンパイラ（`/source-charset`、`/execution-charset`） | リテラルの中身（バイト列）が、思ったものと違う |
| ③ バイト列を<strong>画面に出す</strong> | コンソールの設定（コード ページ）、または出力先のアプリ | 画面で文字化けする |

**MSVC は、何も指定しないと、ソースファイルを「Windows のシステム コードページ」で読みます。** 日本語の Windows では、それが CP932（Shift_JIS の仲間）です。ところが、いまのエディターや Git は、新しいファイルを UTF-8 で保存することが多いです。

ここで、紛らわしい点があります。

<strong>Visual Studio のエディターは、BOM（ファイルの先頭に付く目印）が無い UTF-8 のファイルでも、中身を見て UTF-8 と推測して、正しく表示します。</strong>ですから、エディターで見る限りは何も問題が無いように見えます。ところがコンパイラは、推測をしません。BOM が無ければ、決まりどおりに CP932 として読みます。そのため、「画面では日本語に見えるのに、実行すると化ける」ことになります。

つまり、見た目で判断してはいけません。コンパイラに「UTF-8 で読め」と、はっきり指示する必要があります。

## ① コンパイラに UTF-8 を指示する（`/utf-8`） {#compiler}

### 設定する場所

1. ソリューション エクスプローラーで、プロジェクトを右クリック → **プロパティ**
2. 左上で、構成を<strong>すべての構成</strong>、プラットフォームを<strong>すべてのプラットフォーム</strong>に切り替える
3. **C/C++ → コマンド ライン → 追加のオプション** に、`/utf-8` を足す
4. 適用 → OK

「すべての構成」に切り替えずに設定すると、Debug だけに入って、Release で化けます（[C++23 を使えるようにする設定](settings.md#open)）。

### `/utf-8` が決めること

`/utf-8` は、次の 2 つをまとめた省略形です。

| オプション | 決めること | 意味 |
| --- | --- | --- |
| `/source-charset:utf-8` | ソースファイルを読むときの文字コード | BOM が無くても、UTF-8 として読む |
| `/execution-charset:utf-8` | 文字列リテラルを、実行ファイルに入れるときの文字コード | `"こんにちは"` が、UTF-8 のバイト列になる |

さらに `/utf-8` を付けると、`/validate-charset` が有効になります。これは、**UTF-8 として正しくないバイトがソースに混ざっていたら、`warning C4828` で知らせてくれる**機能です。Shift_JIS のファイルが 1 つ紛れ込んだとき、気づけるようになります。

!!! note "片方だけ指定することもできる"
    たとえば、ソースは UTF-8 のまま、実行時の文字コードだけを変えたいとき（古い Windows API に、CP932 の文字列を渡したいときなど）は、`/source-charset:utf-8 /execution-charset:shift_jis` のように、別々に指定します。ただし、普通はそろえておくほうが、間違えにくいです。

### 設定が効いたか確かめる

次のコードを 1 行入れて、ビルドしてみてください。

```cpp
// "あ" は UTF-8 なら 3 バイト、終端の '\0' を足して 4 バイト。
// CP932 なら 2 バイト + 1 = 3 バイトになる。
static_assert(sizeof("あ") == 4, "/utf-8 が効いていません");
```

効いていなければ、ビルドが止まって、メッセージが出ます。設定の確認に、実行も要りません。

!!! warning "このチェックが通っても、ソースが UTF-8 で保存されているとは限らない"
    `/utf-8` を付けたとき、`static_assert` が通るのは、「**ソースを UTF-8 として読んで、UTF-8 で出す**」状態になったときです。ソースが Shift_JIS で保存されていると、`/validate-charset` が `warning C4828` を出します。ビルドの警告も、必ず見てください。

### CMake のとき

CMake でプロジェクトを作っている場合は、`CMakeLists.txt` に書きます。

```cmake
if(MSVC)
  add_compile_options(/utf-8)
endif()
```

### 複数のプロジェクトにまとめて入れる（`Directory.Build.props`）

プロジェクトが増えると、1 つずつ設定するのが面倒です。ソリューション フォルダーに、`Directory.Build.props` という名前のファイルを置くと、<strong>その下のすべてのプロジェクトに、自動で設定が足されます</strong>（MSBuild の機能です。[プロパティ シート](settings.md#property_sheet)の代わりにもなります）。

```xml
<!-- MyGame/Directory.Build.props -->
<Project>
  <ItemDefinitionGroup>
    <ClCompile>
      <AdditionalOptions>/utf-8 %(AdditionalOptions)</AdditionalOptions>
    </ClCompile>
  </ItemDefinitionGroup>
</Project>
```

`%(AdditionalOptions)` を末尾に付けるのは、**プロジェクト側にすでにあるオプションを、上書きせず、そのまま残す**ためです。

## ② エディターの保存設定をそろえる（`.editorconfig`） {#editorconfig}

コンパイラの側をそろえたら、次は<strong>保存するときの文字コード</strong>です。人が増えると、「誰かの環境だけ Shift_JIS で保存された」ことが起きます。そこで、設定をファイルに書いて、リポジトリに入れます。

### `.editorconfig` とは

`.editorconfig` は、エディターが保存するときの決まりを書くファイルです。Visual Studio、VS Code、JetBrains の各種 IDE など、多くのエディターが読みます。<strong>書いた場所のフォルダーと、その下のすべてのフォルダーに効きます。</strong>

ソリューション フォルダー（`.sln` と同じ場所）に、次の内容で作ります。Visual Studio では、ソリューション エクスプローラーでソリューションを右クリック → **追加 → 新しい項目 → エディターの構成ファイル（.editorconfig）** でも作れます。

```ini
# MyGame/.editorconfig
# 一番上のフォルダーであることを示す（これより上の .editorconfig は読まない）
root = true

[*]
# 文字コードは UTF-8（BOM なし）
charset = utf-8
# 改行は LF
end_of_line = lf
# ファイルの最後に、改行を 1 つ入れる
insert_final_newline = true
# 行末の余計な空白を消す
trim_trailing_whitespace = true
# 字下げは、スペース 2 個（Google C++ Style）
indent_style = space
indent_size = 2

# Visual Studio のソリューションや、Windows のバッチは CRLF のままにする
[*.{sln,slnx,bat,cmd}]
end_of_line = crlf

# Markdown は、行末の空白が意味を持つことがあるので、削らない
[*.md]
trim_trailing_whitespace = false
```

| 設定 | 値 | 意味 |
| --- | --- | --- |
| `charset` | `utf-8` | 保存するとき、UTF-8（BOM なし）にする |
| `charset` | `utf-8-bom` | UTF-8 だが、先頭に BOM を付ける |
| `end_of_line` | `lf` / `crlf` | 保存するときの改行を決める |
| `insert_final_newline` | `true` | ファイルの最後の行にも、改行を付ける |
| `trim_trailing_whitespace` | `true` | 行末のスペースを消す |

### BOM は付ける？ 付けない？

BOM は、UTF-8 のファイルの先頭に付く 3 バイト（`EF BB BF`）の目印です。付いていれば、MSVC は `/utf-8` が無くても、UTF-8 として読んでくれます。それでも、このサイトは<strong>BOM なし</strong>をすすめます。

| | BOM なし | BOM あり |
| --- | --- | --- |
| 標準的か | Web、Linux、GitHub、ほとんどのツールでの標準 | Windows の古いツールの慣習 |
| 困ること | `/utf-8` が無いと、MSVC が CP932 として読む | シェル スクリプトの先頭が壊れる、ツールが先頭 3 バイトを文字として扱う |
| 対策 | `/utf-8` を必ず付ける | — |

BOM に頼ると、**別の環境（Linux の CI、Clang、GCC）に持っていったとき**に、困ることがあります。`/utf-8` と BOM なしの組み合わせが、いちばん移しやすいです。

### `.editorconfig` が効いているか

- `.editorconfig` を置いたあと、**ファイルを開き直して、保存し直す**と反映されます。ファイルを開いただけでは、文字コードは変わりません
- Visual Studio の下の枠（ステータス バー）に、改行の種類（LF / CRLF）や、インデントの種類が表示されます。`.editorconfig` が効いているファイルでは、そこをクリックすると、設定どおりにそろえる操作ができます
- `.editorconfig` が効かないときは、フォルダーの階層を確認します。**ソースファイルより上のフォルダーに、置かれている**必要があります

!!! note "Visual Studio の設定より、`.editorconfig` が優先される"
    「ツール → オプション → テキスト エディター」にも、インデントなどの設定がありますが、`.editorconfig` があれば、そちらが優先されます。チームで設定をそろえるには、`.editorconfig` が確実です。

## 既存のファイルを UTF-8 にする {#convert}

### 1 ファイルずつ、Visual Studio で変える

1. そのファイルを開く
2. **ファイル → 名前を付けて保存 → 保存の右の ▼ → エンコード付きで保存**
3. 文字コードの一覧から、**Unicode (UTF-8、シグネチャなし) - コードページ 65001** を選ぶ
4. 上書き保存する

「シグネチャなし」が、BOM なしのことです。

### たくさんのファイルを、まとめて変える

ファイルが多いときは、スクリプトで変えます。PowerShell 7 以降の場合です。

```powershell
# src の下のすべての .cpp / .h を、CP932 から UTF-8（BOM なし）へ
Get-ChildItem src -Recurse -Include *.cpp,*.h | ForEach-Object {
  $text = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::GetEncoding(932))
  [System.IO.File]::WriteAllText($_.FullName, $text, (New-Object System.Text.UTF8Encoding($false)))
}
```

!!! danger "すでに UTF-8 のファイルを、CP932 として読むと、壊れる"
    変換前に必ず**コミットしておいて**、変換後に差分を確認します。「CP932 のファイルだけ」を対象にしてください。UTF-8 のファイルに同じ変換をかけると、**日本語が壊れて、元に戻せなくなります**。どちらか分からないときは、1 ファイルを `git diff` で確かめてから、まとめて変えます。

## ③ Git の設定（`.gitattributes`） {#gitattributes}

エディターの設定をそろえても、Git が途中で改行を変えてしまうことがあります。Windows 版の Git は、インストール時の既定で、**取り出すときに LF を CRLF へ変える**（`core.autocrlf=true`）ことがあるからです。そうすると、同じファイルなのに、人によって改行が違う状態になります。

リポジトリに `.gitattributes` を置くと、**人の設定に関係なく、同じ規則**で扱えます。

```text
# MyGame/.gitattributes
# テキストは、リポジトリの中では LF にそろえる
* text=auto eol=lf

# Visual Studio のソリューションと、Windows のバッチは、CRLF のまま
*.sln  text eol=crlf
*.slnx text eol=crlf
*.bat  text eol=crlf
*.cmd  text eol=crlf

# バイナリは、触らない
*.png binary
*.jpg binary
*.dds binary
*.fbx binary
*.dll binary
*.lib binary
```

| 書き方 | 意味 |
| --- | --- |
| `* text=auto eol=lf` | テキストファイルと判断したものは、LF にそろえる |
| `*.sln text eol=crlf` | その拡張子は、CRLF にする |
| `*.png binary` | 中身を変えない（画像、モデル、DLL などは必須） |

改行の状態は、次のコマンドで確かめられます。

```bash
# 各ファイルの、作業フォルダーとインデックス（Git に入っている側）の改行を表示
git ls-files --eol
```

`i/lf   w/crlf` のように、インデックス側（`i/`）と作業フォルダー側（`w/`）で食い違っているものがあれば、そのファイルに別々の改行が入っています。

## ④ 実行するとき：コンソールの文字化け {#console}

ここまでで、「ソースの中の文字列が UTF-8 のバイト列になる」ところまで来ました。最後は、そのバイト列を画面で正しく読ませる番です。

### コンソールの文字コード（コード ページ）

Windows のコンソール（黒い画面）は、**出力されたバイト列を、そのときのコード ページで解釈**します。日本語の Windows では、既定が CP932 です。そこに UTF-8 のバイト列を出すと、化けます。

| 方法 | 内容 | 向いている場面 |
| --- | --- | --- |
| `chcp 65001` | その画面のコード ページを UTF-8 にする | コマンド プロンプトで手早く試す |
| Windows Terminal を使う | UTF-8 を扱いやすい | 普段使い |
| `SetConsoleOutputCP(CP_UTF8)` | プログラムの中で、コード ページを切り替える | 自分のプログラムだけ直したい |
| アプリケーション マニフェストで `activeCodePage` を UTF-8 に | プロセス全体を UTF-8 モードにする（Windows 10 1903 以降） | A 系の Windows API も UTF-8 にしたい |

```cpp
#include <windows.h>

#include <print>

int main() {
  // このプログラムが出力するコンソールを、UTF-8 として扱う
  SetConsoleOutputCP(CP_UTF8);
  std::println("文字コードを UTF-8 にしました");
}
```

`std::println` は、`/utf-8` を付けてあると、出力先がコンソールのとき、Unicode の API で書き出す実装になっています。この場合は、`SetConsoleOutputCP` を呼ばなくても読めることが多いです。それでも、`std::cout` で出力するとき、またはファイルへリダイレクトしたときには、上の表の対策が要ります。

### `u8` の文字列は C++20 から型が違う

C++20 から、`u8"あ"` の型は `const char8_t[]` になりました。`std::string` や `std::println` には、そのまま渡せません。**`/utf-8` を付けて、普通の `"…"` を使うのが、いちばん簡単です。** `u8` を付けなくても、中身は UTF-8 です。

古いコードで `u8""` を使っていて、`char` のままにしたいときは、`/Zc:char8_t-`（`char8_t` を無効にする）を付ける手もあります。ただし、新しく書くコードでは、使わないほうがいいです。

### ファイルに書く

`std::ofstream` は、渡されたバイト列を、そのまま書きます。`/utf-8` の文字列を書けば、UTF-8（BOM なし）のファイルになります。

- メモ帳は、いまは UTF-8（BOM なし）を標準で読めます
- Excel で CSV を開くときは、UTF-8 の BOM が無いと、日本語が化けることがあります。その場合のみ、書き出すときに BOM（`EF BB BF`）を先頭に足します

## 化けたときの切り分け {#debug}

| 症状 | 原因の見当 | 直し方 |
| --- | --- | --- |
| `warning C4819`（現在のコード ページで表示できない文字） | ソースが UTF-8 なのに、コンパイラが CP932 で読んでいる | `/utf-8` を付ける |
| `warning C4828`（現在の文字セットで不正な文字） | ソースが UTF-8 ではないバイトを含んでいる | そのファイルを UTF-8 に変換する |
| エディターでは読めるが、実行すると `繧ｳ繝ｳ…` のような文字 | リテラルは UTF-8 だが、コンソールが CP932 | `chcp 65001`、Windows Terminal、`SetConsoleOutputCP` |
| 実行すると `ｺﾝﾆﾁﾊ` のような半角カナ | リテラルが CP932 なのに、コンソールが UTF-8 | `/utf-8` を付けて、リテラルを UTF-8 にそろえる |
| `?` が並ぶ | コンソールのフォントが、その文字を持っていない | フォントを変える（MS ゴシックなど） |
| 別の人の環境だけ化ける | 保存したときの文字コードが、人によって違う | `.editorconfig` と `.gitattributes` を入れる |
| ビルドが `C2001: 定数が改行を含んでいます`（文字列の途中で切れる） | CP932 として読むと、日本語の 2 バイト目が `\` や `"` と同じになる | `/utf-8` を付ける |

!!! failure "`ソ`、`表`、`能` などの文字の後ろで、ビルドが壊れる"
    CP932 には、2 バイト目が `\`（0x5C）になる文字があります。`ソ`、`表`、`能`、`構` などです。UTF-8 のファイルを CP932 として読むと、これらがあるところで、直後の `"` や改行が打ち消されて、「文字列が閉じない」エラーになります。**日本語の途中でビルドが壊れたら、まず文字コードを疑ってください。**

## まとめ：初めに入れる 3 つのファイル

新しくプロジェクトを作ったら、次の 3 つを最初に用意します。

| 何を | どこに | 内容 |
| --- | --- | --- |
| コンパイラの設定 | `Directory.Build.props`、またはプロジェクトの追加のオプション | `/utf-8` |
| エディターの設定 | `.editorconfig`（ソリューション フォルダー） | `charset = utf-8` ほか |
| Git の設定 | `.gitattributes`（リポジトリの一番上） | `* text=auto eol=lf` ほか |

さらに、チームで進めるなら、次のページに進みます。

- clang-format、CI での検査、`/we4828`（文字コードの間違いをエラーにする）は、[ソースファイルの文字コードと強制](../encoding/source-files.md) で解説しています
- 文字化けの原因を、もっと詳しく調べたいときは、[文字化け](../encoding/mojibake.md)

## これだけ覚える

!!! abstract "まとめ"
    - [x] 化ける原因は、「保存」「コンパイラ」「画面」の 3 者の食い違い
    - [x] コンパイラに `/utf-8` を付ける。エディターは見かけだけでは分からない
    - [x] 保存は UTF-8（BOM なし）にして、`.editorconfig` と `.gitattributes` で、全員そろえる
    - [x] `static_assert(sizeof("あ") == 4)` で、設定を確かめる
    - [x] コンソールが化けたら、`chcp 65001`、Windows Terminal、`SetConsoleOutputCP`

## 関連ページ

- [C++23 を使えるようにする設定](settings.md)
- [ソースファイルの文字コードと強制](../encoding/source-files.md)
- [文字化け](../encoding/mojibake.md)
- [コンソールとファイル入出力](../encoding/console-file-io.md)
- [よくあるエラー](errors.md)
- [Visual Studio の目次](index.md)
