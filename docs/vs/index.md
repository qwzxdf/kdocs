# Visual Studio

C++ でゲームを作る学生の多くは <strong>Visual Studio（ビジュアル スタジオ）</strong> を使います。このカテゴリでは**C++23 のコードを動かすための設定**、**外部ライブラリの入れ方**、**デバッグのやり方**、**よく出るエラー**を Visual Studio の画面に沿ってまとめています。このサイトのサンプルコードは C++23 で書かれているので、まず「[C++23 を使えるようにする設定](settings.md)」を済ませてください。

このカテゴリの画面は、すべて **Visual Studio 2026（18.x）の日本語版**で撮っています。メニューや設定画面の名前は、2022 までと少し違う所があります（たとえば、オプションは検索つきの設定画面になり、新しいソリューションのファイルは `.slnx` になりました）。2022 を使っているときは、画面の見た目が違っても、項目の名前をたどれば同じ設定に着けます。コンパイラは `v145` です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [インストールとプロジェクトの作成](setup.md) | 何を入れるか新しいプロジェクトの作り方、ソリューションとプロジェクトの違い |
| [C++23 を使えるようにする設定](settings.md) | 言語標準、警告、よく変える設定、プロパティ シート |
| [文字コードを UTF-8 にしよう](utf8.md) | `/utf-8`、`.gitattributes`、コンソールの文字化け |
| [.editorconfig](editorconfig.md) | 改行・字下げ・文字コードをファイルに書いてそろえる。書き方、Visual Studio 独自の設定 |
| [Git の基礎](git.md) | 履歴を残して戻す。コミット、ブランチ、マージ、コンフリクト、`.gitignore` |
| [SourceTree と GitHub Desktop](git-gui.md) | 画面で Git を使う。事故（detached HEAD・force push・巨大ファイル）と対処 |
| [Git LFS とゲームのリポジトリ](git-lfs.md) | 大きなバイナリの預け方、track、容量、フォルダー構成 |
| [チーム開発の進め方](team.md) | ブランチ、プルリクエスト、レビュー、clang-format |
| [GitHub Actions で自動ビルド](github-actions.md) | push のたびにビルドとテストを自動で動かす |
| [clang-tidy と静的解析](clang-tidy.md) | 動かさずに怪しい書き方を見つける。設定と NOLINT |
| [単体テスト](unit-test.md) | GoogleTest・doctest・Catch2 の選び方と書き方 |
| [RenderDoc と PIX](renderdoc-pix.md) | フレームを捕まえて、描画呼び出しを 1 つずつ調べる |
| [GPU デバッグの流れ](gpu-debug.md) | 真っ黒・一部だけ消える、などの症状からの切り分け |
| [Tracy](tracy.md) | フレームごとの時間を時間軸で見るプロファイラ |
| [外部ライブラリの入れ方](libraries.md) | vcpkg、ヘッダを置く方法、`.lib` / `.dll` を使う方法 |
| [デバッグのやり方](debugging.md) | ブレークポイント、ウォッチ、呼び出し履歴、例外、メモリのバグ探し |
| [AddressSanitizer](asan.md) | メモリの範囲外アクセス・解放済みメモリの使用を、その場で検出 |
| [パフォーマンス プロファイラー](profiler.md) | 遅い場所を測る。ホット パス、PIX・Tracy |
| [プリプロセッサマクロ](preprocessor.md) | `NOMINMAX`、`IMGUI_API`、`_DEBUG` などビルド設定でのマクロ |
| [インクルード ディレクトリとマクロ](include-dirs.md) | 追加のインクルード ディレクトリ、`$(SolutionDir)` などのパス用マクロ |
| [プロジェクトの種類とエントリーポイント](project-types.md) | コンソールと Windows アプリ、`main` と `WinMain`、サブシステム、DLL |
| [便利な機能とショートカット](tips.md) | よく使うキー、整形、IntelliSense、設定ファイル |
| [よくあるエラー](errors.md) | `LNK2019`、`C1083`、文字化け DLL が見つからない、など |
| [CMake で使う](cmake.md) | 「フォルダーを開く」で CMake のプロジェクトを開く |
| [Ninja](ninja.md) | 速いビルド ツール。コマンド ラインや CI でのビルド |

## 用語

プロジェクトを作ると最初に出てくる 6 つの言葉です。1 つずつ別のページで詳しく説明しています。

| 用語 | 意味 |
| --- | --- |
| [ソリューション（`.slnx` / `.sln`）](terms/solution.md) | プロジェクトをまとめる入れ物。ゲーム本体、ツール、ライブラリなど |
| [プロジェクト（`.vcxproj`）](terms/project.md) | 1 つの実行ファイル（`.exe`）やライブラリ（`.lib`）を作る単位 |
| [構成（Configuration）](terms/configuration.md) | **Debug**（デバッグ用）と **Release**（製品用）など、ビルド設定の組 |
| [プラットフォーム](terms/platform.md) | **x64**（64 ビット）か Win32（32 ビット）。今は **x64 にする** |
| [ビルド](terms/build.md) | ソースコードを実行できるファイルにすること（コンパイル + リンク） |
| [MSVC（エムエスブイシー）](terms/msvc.md) | Visual Studio が使うコンパイラ。GCC、Clang とは別のもの |

## 関連ページ

- [はじめに：このサイトの読み方](../how-to-read.md)
- [外部ライブラリ](../libs/index.md)
