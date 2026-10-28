---
title: Ninja（高速なビルド ツール）
tags:
  - Visual Studio
  - CMake
---

# Ninja（高速なビルド ツール）

**Ninja**（ニンジャ）は、ビルドを速く実行することだけに特化した、小さなビルド ツールです。[CMake](cmake.md) は「何をどうビルドするか」を書いた設計図（`CMakeLists.txt`）から、実際にビルドを行う道具用の指示書を作ります。その「実行する道具」に Visual Studio の MSBuild や、Unix の Make の代わりに、Ninja を使えるのです。Ninja は、変更したファイルだけを素早く判断して、コンパイルを並列に走らせることが得意で、ビルドの開始が速く、大きなプロジェクトでは MSBuild より速いことがよくあります。Visual Studio の「フォルダーを開く」で CMake を使うときも、既定で Ninja が使われています。

!!! tip "ポイント"
    - Ninja は<strong>CMake の「ジェネレーター」の 1 つ</strong>。`cmake -G Ninja` で選ぶ。自分でルールは書かない（CMake が `build.ninja` を作る）。
    - Visual Studio の「フォルダーを開く」+ CMake では、<strong>既定で Ninja が使われる</strong>。インストール済み（Visual Studio に同梱）。
    - コマンド ラインで使うときは、Developer Command Prompt（vcvars）の環境で実行する。普通のターミナルだと、`cl.exe` が見つからない。
    - Ninja は並列ビルドが既定で有効（CPU のコア数ぶん）。`/MP` のような設定は不要。
    - `compile_commands.json` を出力すると、clang-tidy や VS Code などの解析ツールが使える。
    - 複数の構成（Debug と Release）を 1 つのフォルダーでビルドしたいときは、`Ninja Multi-Config`。

!!! info "このページを読む前に"
    - [vs/index.md](index.md)（このセクション全体の地図と、読む順番）
    - [インストールとプロジェクトの作成](setup.md)（Visual Studio の準備）

## Ninja とは

<svg class="fig flow" viewBox="0 0 360 280" role="img" aria-label="CMake が指示書を作り、Ninja が実行する"><defs><marker id="fl9196" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">CMake が指示書を作り、Ninja が実行する</text><line x1="162.0" y1="87.0" x2="162.0" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl9196)"/><text x="162.0" y="100.0" text-anchor="middle" style="font-size:12px">cmake が読んで作る</text><line x1="162.0" y1="171.0" x2="162.0" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl9196)"/><text x="162.0" y="184.0" text-anchor="middle" style="font-size:12px">ninja が必要なものだけを並列に実行</text><rect x="28.0" y="44.0" width="268" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="162.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">CMakeLists.txt （人が書く設計図）</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="30.5" y="128.0" width="263" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="162.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">build.ninja （Ninja 用の指示書）</text><circle cx="32.5" cy="130.0" r="10" fill="#2ea043"/><text x="32.5" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="105.5" y="212.0" width="113" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="162.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲームの.exe</text><circle cx="107.5" cy="214.0" r="10" fill="#e5a828"/><text x="107.5" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

| 道具 | 特徴 |
| --- | --- |
| **Ninja** | 速さ重視。指示書は人が書かず、CMake などが生成する。どの OS でも同じように動く |
| MSBuild（Visual Studio の `.vcxproj`） | Visual Studio の標準。GUI で設定できる。`.sln` を生成する |
| Make（Unix） | 昔からある。Linux / Mac で標準。Windows ではあまり使わない |
| CMake | これは「ビルド ツール」ではなく、ビルド ツール用の指示書を作る道具 |

### なぜ速いのか

| 理由 | 説明 |
| --- | --- |
| 起動が軽い | 依存関係の判断が速く、変更がないときは、ほぼ一瞬で終わる |
| 無駄な処理がない | ルールが最小限。指示書の解析も速い |
| 並列がうまい | 依存関係を見て、同時にできるコンパイルをコア数ぶん、自動で並列に走らせる |
| 進捗表示が 1 行 | 出力が少なく、端末の描画で遅くならない（`[12/340] Building CXX ...`） |

小さなプロジェクトでは、差はあまり感じません。ファイルが数百〜数千になると、何も変更していないときの再ビルドや、1 ファイルだけ変えたときの、待ち時間の差が出ます。

## 使えるようにする

### Visual Studio に同梱

Visual Studio のインストーラーで、<strong>「C++ CMake ツール（C++ CMake tools for Windows）」</strong>のコンポーネントを入れると、CMake と Ninja が付いてきます（[インストール](setup.md)）。別に入れる必要はありません。

### 単体で入れる

| 方法 | コマンド |
| --- | --- |
| winget | `winget install Ninja-build.Ninja` |
| vcpkg | `vcpkg install ninja` |
| ダウンロード | [GitHub のリリース](https://github.com/ninja-build/ninja/releases) から `ninja-win.zip` を取って、`ninja.exe` を PATH に置く |

`ninja --version` で、入っているか確認します。

## 使い方

### Visual Studio で使う（一番簡単）

1. 「ファイル → 開く → フォルダー」で、`CMakeLists.txt` のあるフォルダーを開く（[CMake で使う](cmake.md)）
2. Visual Studio が自動で、**Ninja を使って**構成する
3. 「ビルド」や F5 で、そのままビルド・実行する

構成（Debug / Release）は、`CMakePresets.json` の `configurePresets` に `"generator": "Ninja"` と書いて選びます。

### コマンド ラインで使う

Developer Command Prompt for VS（または Developer PowerShell for VS）をスタート メニューから開きます。MSVC のコンパイラ（`cl.exe`）が使える環境変数が設定された状態になります。

```powershell
# 構成（設計図から build.ninja を作る）
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release

# ビルド
cmake --build build

# または、直接 ninja を呼ぶ
ninja -C build
```

| 項目 | 説明 |
| --- | --- |
| `-S .` | ソース（`CMakeLists.txt`）のあるフォルダー |
| `-B build` | ビルド結果を置くフォルダー（ソースと別にする） |
| `-G Ninja` | ジェネレーターに Ninja を使う |
| `-DCMAKE_BUILD_TYPE=Release` | Release でビルドする。Ninja（単一構成）は、構成ごとに別のフォルダーを作る |
| `cmake --build build` | ジェネレーターに関係なく、ビルドを実行する書き方。覚えるならこちら |

!!! warning "普通のターミナルでは、cl.exe が見つからない"
    普通の PowerShell や、コマンド プロンプトで `cmake -G Ninja` を実行すると、「C++ コンパイラが見つかりません」というエラーになります。Developer Command Prompt for VS から実行するか、`vcvars64.bat` を先に呼んで、環境を設定します。

    ```powershell
    "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
    ```

### 構成が 1 つずつ別になる（Debug と Release）

Ninja は、1 つのビルド フォルダーに 1 つの構成だけです（Visual Studio の `.sln` は、Debug と Release を切り替えられます）。

| 方法 | 説明 |
| --- | --- |
| 構成ごとにフォルダーを分ける | `build/debug` と `build/release`。`CMakePresets.json` に、プリセットを 2 つ書くと簡単 |
| `Ninja Multi-Config` | 1 つのビルド フォルダーで、`cmake --build build --config Release` のように、構成を選べる |

```powershell
# Ninja Multi-Config：1 つの構成フォルダーで、Debug と Release を切り替える
cmake -S . -B build -G "Ninja Multi-Config"
cmake --build build --config Debug
cmake --build build --config Release
```

## よく使う ninja のコマンド

```powershell
ninja -C build                 # ビルド（変更があった分だけ）
ninja -C build -v              # コマンドを全部表示（コンパイル オプションの確認に便利）
ninja -C build -j 4            # 並列数を 4 に制限（既定はコア数）
ninja -C build -k 0            # エラーがあっても、止まらず最後まで進める（全エラーを見たいとき）
ninja -C build -n              # 実際には実行せず、何が実行されるかだけ表示（ドライ ラン）
ninja -C build clean           # ビルド結果を消す
ninja -C build -t targets      # ターゲット（ビルドできるもの）の一覧
ninja -C build -t commands game  # game をビルドするコマンドの一覧
ninja -C build -t graph game   # 依存関係のグラフ（Graphviz 形式）
ninja -C build -d stats        # 内部の統計
```

| オプション | 用途 |
| --- | --- |
| `-C フォルダー` | そのフォルダーに移動して実行（`cd` と同じ） |
| `-v` | ビルド コマンドをそのまま表示 |
| `-j N` | 同時に実行する数 |
| `-k N` | N 個のエラーまで続行（0 で無制限） |
| `-n` | ドライ ラン |
| `-t clean` / `-t targets` / `-t commands` / `-t graph` | ツール機能 |

## compile_commands.json（解析ツール用）

**`compile_commands.json`** は、各ソースファイルをどんなコマンドでコンパイルしているかを記録したファイルです。clang-tidy、clangd（VS Code の補完）、cppcheck などの解析ツールがこれを使って、正しいインクルード パスや定義で、コードを解析します。

```powershell
cmake -S . -B build -G Ninja -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

`build/compile_commands.json` ができます。CMake の `CMakeLists.txt` に `set(CMAKE_EXPORT_COMPILE_COMMANDS ON)` と書いても同じです。

Visual Studio のジェネレーター（`.sln`）では、この出力に対応していません。Ninja（または Makefile）のジェネレーターだけが、出せます。

## ビルドをさらに速くする

| 方法 | 説明 |
| --- | --- |
| **ccache / sccache** | コンパイル結果をキャッシュして、同じコードの再コンパイルを省く。`-DCMAKE_CXX_COMPILER_LAUNCHER=sccache` |
| プリコンパイル済みヘッダ | `target_precompile_headers(game PRIVATE pch.h)`（[ビルドと CMake の構成](../design/practice/build-cmake.md)） |
| Unity ビルド | 複数の `.cpp` を 1 つにまとめて、コンパイルする（`-DCMAKE_UNITY_BUILD=ON`）。ヘッダの読み込みが減って速くなる。名前の衝突に注意 |
| ライブラリに分ける | 変更した部分だけ再ビルド |
| `/MP`（MSBuild）の代わりに、Ninja の並列 | Ninja は、既定で並列 |

## Visual Studio（.sln）と Ninja の使い分け

| 状況 | おすすめ |
| --- | --- |
| Visual Studio の GUI で、プロパティを設定したい | **`.sln` / `.vcxproj`** |
| コマンド ラインでビルド、CI（GitHub Actions など） | Ninja |
| clang-tidy や clangd を使いたい | Ninja（`compile_commands.json`） |
| チームで、IDE を統一していない | CMake + Ninja（どの IDE からも開ける） |
| 巨大なプロジェクトで、ビルドの待ち時間が長い | Ninja + ccache |
| Visual Studio で CMake を開く | 既定で Ninja。何もしなくてよい |

## よくあるミス

??? failure "「C++ コンパイラが見つかりません」と出る"
    普通のターミナルから実行しているためです。**Developer Command Prompt for VS** から実行するか、`vcvars64.bat` を呼びます。VS Code の場合は、CMake Tools 拡張機能が自動で環境を設定してくれます。

??? failure "Debug と Release を同じフォルダーに混ぜる"
    Ninja は、1 つのビルド フォルダーに 1 つの構成です。`build/` に、Debug と Release を交互にビルドすると、設定が混ざります。フォルダーを分けるか、`Ninja Multi-Config` を使います。

??? failure "古い `build/` を使い回して、設定が反映されない"
    ジェネレーターを変えたとき（Visual Studio から Ninja へ）や、コンパイラを変えたときは、`build/` を削除して、構成し直します。CMake は、最初の設定をキャッシュ（`CMakeCache.txt`）に残します。

??? failure "ビルドが 32 ビットになる"
    Developer Command Prompt の種類（x86 / x64）が環境を決めます。x64 Native Tools Command Prompt を使います。

??? failure "並列数が多すぎて、PC が固まる"
    メモリが少ないと、大量のコンパイラが同時に動いて、スワップします。`-j` で制限します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Ninja ＝ <strong>速さに特化したビルド実行ツール</strong>。CMake が `build.ninja` を作る
    - [x] Visual Studio の「フォルダーを開く」では、既定で Ninja
    - [x] コマンド ラインは Developer Command Prompt から。`cmake -S . -B build -G Ninja` → `cmake --build build`
    - [x] 構成はフォルダーごと（または `Ninja Multi-Config`）
    - [x] `compile_commands.json` で、clang-tidy などの解析ツールが使える

## 関連ページ

- [CMake で使う](cmake.md)
- [ビルドと CMake の構成](../design/practice/build-cmake.md)
- [外部ライブラリの入れ方](libraries.md)
- [Visual Studio の目次](index.md)
- [Ninja 公式](https://ninja-build.org/)
