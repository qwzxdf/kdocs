---
title: コーディング スタイルのまとめ
tags:
  - 設計
---

# コーディング スタイルのまとめ

コーディング スタイルは、**チームで書き方をそろえるためのルール**です。名前の付け方・インクルードの順番・字下げのような、**動作には関係ないが読みやすさに大きく効く**部分を決めます。ここではこのサイトで基準にしている **Google C++ Style Guide** の要点を、実際によく迷う順にまとめます。細かい理由は公式のガイドを見てください。

!!! tip "ポイント"
    - スタイルの<strong>正解は 1 つではない</strong>。大事なのは<strong>プロジェクト全体でそろえる</strong>こと。
    - 迷ったら<strong>Google C++ Style Guide</strong>。このサイトの基準でもある。
    - 整形は<strong>`clang-format` に任せる</strong>。人間がレビューで空白を指摘しない。
    - 名前は<strong>種類ごとに形を変える</strong>（型は `PascalCase`、変数は `snake_case`）。見ただけで種類が分かる。
    - 守るべきなのは<strong>「見た目」より「安全さ」のルール</strong>（`const`・所有権・例外を使うか）。
    - ルールは<strong>文書にして、ツールで強制</strong>する（`clang-format`・`clang-tidy`・CI）。

## 名前の付け方

| 種類 | 形 | 例 |
| --- | --- | --- |
| **クラス・構造体・列挙型・型エイリアス** | `PascalCase` | `PlayerController`、`using EntityList = ...` |
| **関数・メソッド** | `PascalCase` | `UpdateHealth()`、`GetName()` |
| **変数・引数** | `snake_case` | `player_count`、`delta_time` |
| **クラスのメンバ変数** | `snake_case` ＋ 末尾の `_` | `health_`、`name_` |
| **構造体のメンバ変数** | `snake_case`（`_` なし） | `position`、`velocity` |
| **定数**（`constexpr`・`const` の固定値） | `k` ＋ `PascalCase` | `kMaxPlayers`、`kPi` |
| **列挙子** | `k` ＋ `PascalCase` | `kIdle`、`kRunning` |
| **名前空間** | `snake_case` | `game_engine` |
| **マクロ** | `UPPER_SNAKE_CASE` | `MY_ASSERT`（なるべく使わない） |
| **ファイル名** | `snake_case` | `player_controller.h` / `.cc` |

| 点 | 説明 |
| --- | --- |
| **略語は 1 単語として扱う** | `HttpRequest`（`HTTPRequest` ではない）。ただし、チームで決めたなら、それに従う |
| <strong>アクセサ（単純な getter・setter）</strong> | 変数名と同じ小文字でもよい（`int count() const`）。複雑な処理は `PascalCase` |
| **意味のある長さ** | `i` や `n` は短いスコープだけ。**グローバル・メンバは省略しない** |
| **bool の名前** | `is_`・`has_`・`can_` で始めると、`if` の文が読みやすい |
| **ハンガリアン記法は使わない** | 型を名前に入れない（`iCount`・`strName` は不要） |

## ファイルとインクルード

| ルール | 内容 |
| --- | --- |
| **ヘッダ ファイルは自己完結させる** | そのヘッダ単体でコンパイルが通る（必要なものを自分で `#include` する） |
| **インクルード ガード** | `#pragma once`、または `#ifndef PROJECT_PATH_FILE_H_` |
| **インクルードの順番** | ① 対応するヘッダ → ② C のシステム ヘッダ → ③ C++ の標準ライブラリ → ④ 他のライブラリ → ⑤ 自分のプロジェクトのヘッダ（各グループの間に空行。グループ内はアルファベット順） |
| **前方宣言** | ヘッダの依存を減らすために使う。ただし、**テンプレートや継承では使えない**（[ヘッダとソース](../foundations/header-source.md)） |
| **`using namespace` はヘッダで使わない** | 名前の衝突をすべてのインクルード元へ広げてしまう |
| **使うものを直接インクルード** | 他のヘッダ経由で入っているものに頼らない（IWYU） |

## 書式（`clang-format`）

| 項目 | Google スタイルの既定 |
| --- | --- |
| **字下げ** | スペース 2 つ（タブは使わない） |
| **1 行の長さ** | 80 文字（チームで 100〜120 に広げるのも一般的） |
| **波括弧** | 開き括弧は**行末**（K&R 系）。関数も同じ行 |
| **ポインタ・参照の記号** | 型に付ける（`int* p`・`const std::string& s`） |
| **`if` の本文** | 1 行でも `{}` を付けるのが安全（付けない場合は、同じ行に書く） |
| **`public:` などのアクセス指定** | 1 スペース字下げ（クラスの `class` と同じ位置から 1 つ） |
| **コンストラクタの初期化リスト** | 1 行に収まらなければ、`:` の後で改行して 4 スペース |

<strong>設定は `.clang-format` に書いて、リポジトリに置きます。</strong>

```yaml
BasedOnStyle: Google
IndentWidth: 2
ColumnLimit: 100
```

保存時に自動で整形する設定にすると、スタイルの議論がなくなります。

## 宣言と関数

| ルール | 内容 |
| --- | --- |
| **変数は使う直前で宣言する** | 関数の先頭にまとめない |
| **変数はその場で初期化する** | 未初期化のまま宣言しない |
| **`auto` は型が明らかなときだけ** | `auto it = v.begin();` はよいが、`auto x = Compute();` は型が分からない |
| **引数の順番** | 入力引数を先に出力引数を後ろに |
| **出力は戻り値で** | 出力引数（ポインタ）は、なるべく避ける。複数なら構造体・`std::pair` |
| **入力引数** | 小さい型は値渡し（`int`・`float`）。大きい型は `const T&` |
| **短い関数** | 目安は 40 行程度。長ければ分ける |
| **オーバーロード** | 同じ意味のときだけ。意味が違うなら、名前を変える |
| **デフォルト引数** | 仮想関数では使わない（動的な型でなく、静的な型の値が使われる） |

## クラス

| ルール | 内容 |
| --- | --- |
| **データ メンバは `private`** | 構造体（データだけの入れ物）は `public` でよい |
| **宣言の順番** | `public` → `protected` → `private`。その中で型・定数 → コンストラクタ → メソッド → データ |
| **コンストラクタで重い処理をしない** | 失敗しうる処理は `Init()` やファクトリ関数に |
| **1 引数のコンストラクタは `explicit`** | 意図しない暗黙の変換を防ぐ |
| **継承より合成** | 継承は「is-a」のときだけ（[継承より合成](../foundations/composition-vs-inheritance.md)） |
| **コピーとムーブ** | 使うかどうかを明示する（`= default`・`= delete`）（[コピーとムーブ](../../optimize/copy-move.md)） |
| **仮想関数には `override`** | 基底クラスの関数を書き換えるときは必ず付ける |
| **`final`・`override` は片方でよい** | `virtual` と同時には書かない |

## 所有権とポインタ

| ルール | 内容 |
| --- | --- |
| **生の `new` / `delete` を避ける** | `std::make_unique`・`std::make_shared` を使う |
| **所有しているポインタ** | `std::unique_ptr` |
| **所有していないポインタ** | 生ポインタか参照（借りているだけ） |
| **共有所有** | `std::shared_ptr` は、本当に共有が必要なときだけ |
| **`nullptr`** | `NULL` や `0` ではなく、`nullptr` |
| **`const` を付ける** | 変更しないものは、すべて `const`（引数・メソッド・変数） |

詳しくは[所有権](../../basics/ownership.md)・[`const` と受け渡し](../foundations/const-and-passing.md)を見てください。

## C++ の機能の使い方

| 機能 | 方針 |
| --- | --- |
| **例外** | ゲームでは使わないことが多い（Google も使わない）。使う場合もプロジェクトで統一する |
| <strong>RTTI（`dynamic_cast`）</strong> | 少なめに。設計で解決できないか考える |
| **キャスト** | C スタイル（`(int)x`）は使わない。`static_cast` などを使う |
| **整数型** | 符号なしはビット演算以外では避ける。サイズが重要なら `int32_t` など |
| **`++i` と `i++`** | 結果を使わないなら `++i` |
| **ラムダ式** | 短い関数に。キャプチャは `[&]`・`[=]` より、**明示的に**書く |
| **テンプレート・メタプログラミング** | 複雑にしすぎない。可読性を優先 |
| **マクロ** | 避ける。`constexpr`・`inline`・テンプレートで代用 |
| **`#define` の定数** | `constexpr` にする |

## コメント

| 項目 | 内容 |
| --- | --- |
| **Google の方針** | クラス・関数の役割や読み手が分かりにくい意図を書く。コードを読めば分かることは書かない |
| **このサイトのサンプル・プロジェクトの方針** | コードにコメントは書かない。**名前と構造で意味を伝える**。説明はページの本文に書く |
| **TODO** | `// TODO(name): ...` の形で担当者を書く（コメントを書く規約の場合） |

プロジェクトごとに方針が違うので、**チームで決めて、文書に書きます**。

## ツールで強制する

| ツール | 用途 |
| --- | --- |
| **`clang-format`** | 書式の自動整形。保存時・コミット前に実行する |
| **`clang-tidy`** | 命名・危険な書き方・モダンな書き方の検査（`readability-identifier-naming` で命名を強制できる） |
| **`cpplint`** | Google のスタイルの、簡易チェック |
| **CI** | プッシュ時に整形と検査を自動で実行して、違反を弾く |
| **`.editorconfig`** | エディタごとの字下げ・改行コードの違いを抑える |

`clang-tidy` の命名ルールの例:

```yaml
CheckOptions:
  - key: readability-identifier-naming.ClassCase
    value: CamelCase
  - key: readability-identifier-naming.FunctionCase
    value: CamelCase
  - key: readability-identifier-naming.VariableCase
    value: lower_case
  - key: readability-identifier-naming.PrivateMemberSuffix
    value: _
  - key: readability-identifier-naming.ConstexprVariablePrefix
    value: k
```

## よくあるミス

??? failure "スタイルを決めずに、書く人ごとにバラバラ"
    読むときに毎回見た目を解釈する負担が増えます。最初に決めて、ツールで強制します。

??? failure "レビューで、空白や改行の指摘ばかりになる"
    `clang-format` に任せます。レビューは設計と安全さに使います。

??? failure "既存のコードを、一斉に整形して、履歴が読みにくくなる"
    整形だけのコミットを別にして、ほかの変更と混ぜません（`git blame --ignore-revs-file` で無視できる）。

??? failure "規約を、全部は覚えきれない"
    覚えるのは**名前の形**と**インクルードの順番**だけでよい。残りはツールが直します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基準は<strong>Google C++ Style Guide</strong>。<strong>プロジェクトでそろえる</strong>ことが最も大事
    - [x] 名前：<strong>型・関数は `PascalCase`、変数は `snake_case`、メンバは末尾 `_`、定数は `kName`</strong>
    - [x] インクルード：<strong>自己完結・順番・`using namespace` をヘッダで使わない</strong>
    - [x] 書式は<strong>`clang-format`</strong>、検査は<strong>`clang-tidy`</strong>。ツールで強制
    - [x] 安全さ：<strong>`const`・`unique_ptr`・`nullptr`・`override`・`explicit`</strong>

## 関連ページ

- [名前の付け方](../foundations/naming.md)
- [ヘッダとソース](../foundations/header-source.md)
- [`const` と受け渡し](../foundations/const-and-passing.md)
- [所有権](../../basics/ownership.md)
- [ロギングとデバッグ](logging-debug.md)
- [設計](../index.md)
