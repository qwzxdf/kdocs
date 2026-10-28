---
title: GitHub Actions で自動ビルド
tags:
  - Visual Studio
---

# GitHub Actions で自動ビルド

「自分の PC ではビルドが通ったのに、他の人の PC では通らない」「push した後で、ビルドが壊れていたと気づいた」は、チーム開発で何度も起きます。原因は、ファイルの入れ忘れや、自分の環境にだけある設定です。

GitHub Actions は、push や PR のたびに、<strong>まっさらな Windows の機械でビルドとテストを自動で走らせる</strong>仕組みです。壊れたコミットがその場で分かり、「自分の環境でだけ動く」問題も見つかります。

!!! tip "ポイント"
    - 設定は `.github/workflows/` 以下の YAML ファイル。リポジトリに入れれば動く
    - Windows の機械（`windows-latest`）には Visual Studio が入っている。MSBuild でそのままビルドできる
    - 失敗したら PR に赤いバツが付く。ブランチ保護と組み合わせると、壊れたものを `main` に入れられなくなる
    - ライブラリは vcpkg で入れる。キャッシュを使うと、2 回目以降が速い

!!! info "このページを読む前に"
    - [GitHub を使う](../git/github.md)（push、プルリクエスト）
    - [外部ライブラリの入れ方](libraries.md)（vcpkg）
    - [チーム開発の進め方](../git/team.md)

## 最小のワークフロー {#minimal}

次の内容を `.github/workflows/build.yml` として置き、push します。

```yaml title=".github/workflows/build.yml"
name: build

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
      - uses: microsoft/setup-msbuild@v2
      - name: Build
        run: msbuild MyGame.sln /p:Configuration=Release /p:Platform=x64
```

`on` は、いつ動かすかです。`main` への push と、すべての PR で動かしています。`runs-on` は機械の種類で、Windows と Visual Studio が入ったものを選びます。

`actions/checkout` で、リポジトリを取ってきます。`lfs: true` は、[Git LFS](../git/git-lfs.md) の本体も取ってくる指定です。LFS を使っていなければ要りません。

`setup-msbuild` は、`msbuild` コマンドを使えるようにします。`run` に、ふだん手元で打つのと同じコマンドを書きます。

## vcpkg を使う {#vcpkg}

`vcpkg.json`（マニフェスト）を置いたプロジェクトは、ビルド時に vcpkg が自動で必要なライブラリを入れます。GitHub の機械には vcpkg が入っているので、統合を有効にします。

```yaml
      - name: vcpkg の統合
        run: vcpkg integrate install
      - name: Build
        run: msbuild MyGame.sln /p:Configuration=Release /p:Platform=x64
```

毎回ライブラリをビルドし直すと、数十分かかることがあります。`actions/cache` で、vcpkg のバイナリキャッシュを保存すると、2 回目以降は数分に縮みます。

```yaml
      - uses: actions/cache@v4
        with:
          path: ~\AppData\Local\vcpkg\archives
          key: vcpkg-${{ hashFiles('vcpkg.json') }}
```

`key` に `vcpkg.json` のハッシュを入れているので、ライブラリの構成を変えたときだけ、キャッシュが作り直されます。

## テストを走らせる {#test}

ビルドの後にテストの実行ファイルを動かします。

```yaml
      - name: Test
        run: x64\Release\MyGameTests.exe
```

実行ファイルが 0 以外の値を返すと、ステップが失敗して、PR に赤いバツが付きます。テストの書き方は、[単体テスト](unit-test.md) にあります。

## PR を守る設定 {#protect}

ワークフローを作っただけでは、失敗しても `main` に入れられます。GitHub の「Settings → Branches → Branch protection rules」で、次を設定します。

- 「Require a pull request before merging」: PR を必須にする
- 「Require status checks to pass」: `build` が成功しないと、合体できなくする

これで、ビルドが通らないコードが `main` に入ることはなくなります。

## 文字コードの検査 {#encoding}

[文字コード](../encoding/index.md) のページで紹介した検査（BOM の有無や、混在の確認）も、ここに足せます。「ソースが UTF-8 でないとビルドが失敗する」仕組みを CI に置くと、個人の設定に頼らずに済みます。

## よくあるミス {#mistakes}

??? failure "ワークフローが動かない"
    ファイルの場所が違う可能性があります。`.github/workflows/` の下で、拡張子は `.yml` か `.yaml` です。YAML は字下げが意味を持つので、タブを使わず、スペースにそろえてください。

??? failure "手元では通るのに CI で失敗する"
    手元の環境にだけあるファイル（`.gitignore` で除外した設定など）に依存しているのが典型的な原因です。CI が見つけてくれた不具合なので、ファイルを正しく追加します。

??? failure "実行時間（無料枠）を使い切った"
    プライベートのリポジトリは、無料枠が限られます。Windows の機械は、Linux の約 2 倍に数えられます。不要な動かし方（すべての枝の push など）を絞ります。

## これだけ覚える {#summary}

- `.github/workflows/*.yml` を置くと、push のたびにビルドが動く
- `windows-latest` に `setup-msbuild` を足して、手元と同じコマンドを書く
- vcpkg のキャッシュを使うと速い。ブランチ保護と組み合わせて、壊れたコードを止める

## 関連ページ

- [チーム開発の進め方](../git/team.md)
- [単体テスト](unit-test.md)
- [clang-tidy と静的解析](clang-tidy.md)
