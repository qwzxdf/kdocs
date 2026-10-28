---
title: clang-tidy と静的解析
tags:
  - Visual Studio
---

# clang-tidy と静的解析

コンパイラは、文法が正しければ通してくれます。「初期化していない変数を読んでいる」「`std::move` した後の変数を使っている」「ムーブできるのに毎回コピーしている」のような、文法は正しいが怪しい書き方は、実行して初めて不具合として出ます。

静的解析は、<strong>プログラムを動かさずにソースを読んで、怪しい書き方を見つける</strong>ツールです。Visual Studio には Code Analysis と clang-tidy が入っています。バグの種類は多いので、最初は警告の数が多く見えますが、種類を絞って慣れていくと、レビューの前に機械が見つけてくれる数が増えます。

!!! tip "ポイント"
    - Visual Studio は、プロジェクトのプロパティで「Code Analysis」と「clang-tidy」を有効にできる
    - `.clang-tidy` ファイルに有効にするチェックを書く。リポジトリに入れて共有する
    - 最初は少数のチェック（`bugprone-*`、`performance-*`）から。全部を有効にすると、警告で埋まる
    - 誤検出もある。無視したい場所には `// NOLINT` を付けるが、理由を添える

!!! info "このページを読む前に"
    - [Visual Studio の設定](settings.md)（プロジェクトのプロパティ）
    - [チーム開発の進め方](../git/team.md)（整形ツールとの組み合わせ）

## Visual Studio での有効化 {#enable}

プロジェクトのプロパティで「Code Analysis」を開きます。

- 「Microsoft Code Analysis を有効にする」: ビルドのたびに、MSVC の静的解析が走る。ルールセットは「Microsoft ネイティブ推奨規則」から始める
- 「Clang-Tidy を有効にする」: ビルドのたびに、clang-tidy が走る。設定は `.clang-tidy` ファイル、またはプロパティの欄に書く

警告は「エラー一覧」に出ます。クリックすると該当の行へ飛べます。

## .clang-tidy の書き方 {#config}

リポジトリの一番上に置きます。

```yaml title=".clang-tidy"
Checks: >
  -*,
  bugprone-*,
  performance-*,
  modernize-use-nullptr,
  modernize-use-override,
  readability-container-size-empty
WarningsAsErrors: ''
```

`Checks` は、有効にするチェックの一覧です。`-*` で全部を一度無効にして、必要なものを足します。`bugprone-*` は、バグになりやすい書き方の検出で、まず入れる価値があります。`performance-*` は、不要なコピーなど、速度に関わる指摘です。

`modernize-*` は、古い書き方を新しい書き方に変える提案で、数が多いです。全部入れずに、個別に選びます。

`WarningsAsErrors` に、チェック名を書くと、そのチェックの警告をエラー扱いにできます。慣れないうちは空にして、警告のままにします。

## よく出る指摘 {#common}

| チェック | 指摘する内容 |
| --- | --- |
| `bugprone-use-after-move` | `std::move` したあとの変数を使っている |
| `bugprone-unused-return-value` | 戻り値を無視している（`[[nodiscard]]` のあるもの） |
| `performance-unnecessary-value-param` | 重い型を値渡ししている。`const&` にすれば足りる |
| `performance-for-range-copy` | 範囲 for の変数がコピーになっている |
| `modernize-use-nullptr` | `NULL` や `0` の代わりに `nullptr` を使うよう提案 |
| `modernize-use-override` | 仮想関数の上書きに `override` が付いていない |

たとえば `performance-for-range-copy` は、次のような書き方を指摘します。

```cpp
for (auto e : enemies) {   // Enemy がコピーされる
  e.Update();              // しかも、コピーを更新して終わる
}
```

`auto&` にすれば、コピーせず、元の要素を更新できます。ゲームでは、毎フレーム回るループの中のコピーが効くので、この種の指摘は役に立ちます。

## 誤検出と NOLINT {#nolint}

解析は完璧ではなく、問題ない書き方に警告が出ることもあります。その行だけ抑制するときは、コメントで書きます。

```cpp
int* p = GetRaw();  // NOLINT(bugprone-unused-return-value): 使わずに捨てて問題ない
```

抑制は、必ず<strong>チェック名と理由</strong>を書きます。理由のない `NOLINT` が増えると、後で意味が分からなくなります。

## CI に組み込む {#ci}

手元だけで走らせると、見落とされやすくなります。[GitHub Actions](github-actions.md) に、解析のステップを足すと、PR のたびに自動で確認されます。ただし、はじめから `WarningsAsErrors` にすると、既存のコードで全部が落ちます。最初は警告にとどめ、新しい指摘が増えないようにしていきます。

## ほかのツール {#others}

- Visual Studio の Code Analysis（`/analyze`）: MSVC 標準。メモリ関連の指摘が得意
- Cppcheck: 無料。誤検出が比較的少ない
- AddressSanitizer: 静的ではなく、実行時に検出する。[ASan](asan.md) に詳しい

静的解析は、動かさないと見えない不具合までは見つけません。実行時の検出と併用します。

## よくあるミス {#mistakes}

??? failure "最初から全部のチェックを有効にして、警告に埋もれた"
    数千件の警告は、誰も見なくなります。少数のチェックから始め、警告が 0 になったら次を足します。

??? failure "警告を消すために、意味もなく NOLINT を増やした"
    指摘の内容を理解してから、直すか、抑制するかを決めます。

## これだけ覚える {#summary}

- 静的解析は、動かす前に怪しい書き方を見つける
- `.clang-tidy` に少数のチェックを書いて共有する。まず `bugprone-*` と `performance-*`
- 誤検出は `NOLINT(チェック名)` と理由で抑える

## 関連ページ

- [ASan（AddressSanitizer）](asan.md)
- [チーム開発の進め方](../git/team.md)
- [単体テスト](unit-test.md)
