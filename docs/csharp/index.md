---
title: C# 連携
tags:
  - C#連携
---

# C# 連携

このカテゴリは <strong>Visual Studio の「WPF アプリケーション」プロジェクトを、一から作り C++ のゲーム エンジンと連携する、エディタを育てていく</strong>チュートリアルです。他のカテゴリのように用語を 1 つずつ引くページではなく、<strong>最初から最後まで順に手を動かして、1 つのソリューションを大きくしていく</strong>ガイドです。章を進めるたびにプロジェクトが増え機能が増え最後に <strong>3D ビューポート、シーン ツリー、プロパティ、Undo/Redo、保存、アセット ブラウザ、ゲーム DLL のホット リロード、Play モード</strong>を持つエディタが、完成します。

!!! tip "ポイント"
    - エンジンと実行側（Engine・Player・Game）は C++、<strong>エディタだけ C#（WPF + Prism）</strong>。
    - プロジェクトを<strong>役割ごとに分ける</strong>: Engine（中核）、EngineApi（C# 向けの入口）、Game（ゲームのコード）、Player（実行側）、Editor（エディタ）。
    - 描画は<strong>DirectX 12</strong>。3D ビューポートは WPF の中に Win32 の子ウィンドウを埋め込みエンジンがそこへ、直接描く。
    - 連携は <strong>C API + P/Invoke</strong> を主に <strong>C++/CLI</strong> との違いも、比べる。
    - C# が初めてでも読める。<strong>新しい C#・WPF・Prism の言葉や型が出るたびにその場で、くわしく説明する。</strong>

## 前提

| 項目 | 前提 |
| --- | --- |
| C++ | 中級（クラス、テンプレート、スマート ポインター、DLL の存在を知っている）。DirectX 12 の説明は[DirectX 12 Guide](../directx/dx12/index.md) へのリンクで、補う |
| C# | <strong>経験なし</strong>。第 5 章で C++ と比べながら、必要な範囲を学ぶ |
| WPF・Prism | 経験なし。第 6 章から順に説明する |
| 環境 | Windows 10/11、<strong>Visual Studio 2022</strong>（「.NET デスクトップ開発」と「C++ によるデスクトップ開発」のワークロード、Windows SDK）、DirectX 12 対応の GPU |
| .NET | <strong>.NET 8</strong>（LTS） |
| Prism | <strong>Prism 9</strong>（DryIoc 版）。版で API が変わる所は囲みで示す |

## 完成するもの

<strong>MiniEngine</strong>（この教材用の小さなゲーム エンジン）とその<strong>エディタ</strong>です。

```text
┌─────────────────────────────────────────────────────────────┐
│ MiniEngine Editor                                      [_][□][x] │
├────────────┬──────────────────────────────┬────────────────┤
│ シーン ツリー │        3D ビューポート (DX12)       │  プロパティ       │
│  ├ Camera   │                              │  Position X Y Z │
│  ├ Cube     │      （エンジンが直接描く）         │  Rotation …     │
│  └ Light    │                              │  Scale …        │
├────────────┴──────────────────────────────┴────────────────┤
│ アセット ブラウザ | ログ                          ▶ Play  ■ Stop │
└─────────────────────────────────────────────────────────────┘
```

## ソリューションの構成

```text
MiniEngine.sln
├─ Engine      C++  DLL   エンジンの中核（DX12 描画、シーン、アセット）。誰にも依存しない
├─ EngineApi   C++  DLL   Engine を C の関数として公開する入口。Editor（C#）はここだけを見る
├─ Game        C++  DLL   ゲームのコード。実行中に、差し替えられる（ホット リロード）
├─ Player      C++  EXE   ゲームを動かす実行側。Engine と Game を読み込む
└─ Editor      C#   EXE   WPF + Prism のエディタ。EngineApi.dll を呼ぶ
```

| 依存の向き | 意味 |
| --- | --- |
| Player → Engine | Player は、Engine の機能を使う。Game DLL は実行時に読み込む |
| Game → Engine | ゲームのコードは、Engine の機能で書く |
| EngineApi → Engine | C の関数に包んで、公開する |
| Editor → EngineApi | エディタは、C の関数だけを呼ぶ。Engine の C++ には触れない |
| Engine → （なし） | Engine は、他のどれにも依存しない（逆向きの依存を作らない） |

## 章の構成

| 部 | 章 | 内容 |
| --- | --- | --- |
| 0 準備 | [第 0 章 はじめる前に：道具と言葉の準備](00-prepare.md) | 道具の準備と言葉の整理 |
| 1 エンジンを作る | [第 1 章 全体像とソリューションの設計](01-overview.md) | 5 つのプロジェクトの役割、依存の規則、ソリューションの作成 |
|  | [第 2 章 Engine プロジェクト：DLL の骨組み](02-engine-skeleton.md) | DLL とエクスポート、公開ヘッダー、ログ |
|  | [第 3 章 Engine に DirectX 12 を載せる](03-engine-dx12.md) | デバイス、スワップ チェーン、フレーム |
|  | [第 4 章 Player：エンジンを動かす実行側](04-player.md) | Win32 のウィンドウとメッセージ ループ |
| 2 C#・WPF・Prism を学ぶ | [第 5 章 C++ を知っている人のための C# 入門](05-csharp-basics.md) | 型、クラス、プロパティ、null、コレクション、デリゲート |
|  | [第 6 章 WPF プロジェクトと XAML](06-wpf-xaml.md) | XAML の読み方、レイアウトの入口、リソース |
|  | [第 7 章 Visual Studio で XAML を書くコツ](07-vs-tips.md) | XAML ホット リロード、ライブ ビジュアル ツリー、バインディング エラー |
|  | [第 8 章 コントロールとコンテンツ モデル](08-controls.md) | コントロールの一覧と、コンテンツ モデル |
|  | [第 9 章 レイアウトの仕組み](09-layout.md) | Measure と Arrange、Grid、スクロール、DPI |
|  | [第 10 章 依存関係プロパティ、添付プロパティ、ルーテッド イベント](10-dependency-properties.md) | 依存関係プロパティ、添付プロパティ、ルーテッド イベント |
|  | [第 11 章 スタイル、リソース、テンプレート、トリガー](11-style-template.md) | リソース、スタイル、トリガー、ControlTemplate |
|  | [第 12 章 データバインディングと MVVM](12-binding-mvvm.md) | データ バインディング、MVVM、ICommand |
|  | [第 13 章 バインディングを掘り下げる](13-binding.md) | Mode と UpdateSourceTrigger、RelativeSource、入力検証、デバッグ |
|  | [第 14 章 リストとデータ表示](14-lists.md) | ListBox、ComboBox、DataGrid、選択、仮想化 |
|  | [第 15 章 非同期処理と UI スレッド](15-async-ui.md) | async / await、Dispatcher、IProgress |
|  | [第 16 章 Prism の導入と起動の流れ](16-prism-bootstrap.md) | Prism、DI コンテナー、ViewModelLocator |
|  | [第 17 章 リージョン、モジュール、ナビゲーション](17-regions-modules.md) | リージョン、モジュール、ナビゲーション |
|  | [第 18 章 イベント集約、ダイアログ、サービス](18-events-dialogs.md) | IEventAggregator、ダイアログ、サービス |
|  | [第 19 章 Prism を掘り下げる](19-prism-deep.md) | KeepAlive、IConfirmNavigationRequest、CompositeCommand |
|  | [第 20 章 MVVM ライブラリを比べる](20-mvvm-libraries.md) | BindableBase と CommunityToolkit.Mvvm などの比較 |
|  | [第 21 章 UserControl とカスタム コントロール](21-custom-controls.md) | UserControl とカスタム コントロール |
|  | [第 22 章 コードビハインドを減らす（Behaviors）](22-behaviors.md) | Behaviors でイベントをコマンドに結ぶ |
|  | [第 23 章 アプリの基本（起動・終了・ウィンドウ・コマンド）](23-app-basics.md) | 起動と終了、ウィンドウ、標準のコマンド |
|  | [第 24 章 アニメーション](24-animation.md) | Storyboard とイージング |
| 3 C# から C++ を呼ぶ | [第 25 章 C# から C++ を呼ぶ：連携方式の比較](25-interop-overview.md) | P/Invoke、C++/CLI、COM、IPC の比較と、境界のルール |
|  | [第 26 章 EngineApi：C の入口を作る](26-engine-api.md) | C の API（ハンドル、エラー コード） |
|  | [第 27 章 P/Invoke で C# から呼ぶ](27-pinvoke.md) | LibraryImport、構造体、SafeHandle、コールバック |
|  | [第 28 章 C++/CLI で橋を作る](28-cpp-cli.md) | C++/CLI の橋と比較 |
|  | [第 29 章 DLL の読み込み、x64、デバッグ](29-dll-loading.md) | 読み込みの仕組みと、エラーの切り分け、混在デバッグ |
| 4 3D ビューポート | [第 30 章 3D ビューポートを埋め込む方法の比較](30-viewport-options.md) | HwndHost、D3DImage、WriteableBitmap などの比較 |
|  | [第 31 章 HwndHost でビューポートを実装する](31-hwndhost.md) | 子ウィンドウの埋め込みと DX12 |
|  | [第 32 章 描画ループとスレッド](32-render-loop.md) | 描画スレッドとコマンド キュー |
|  | [第 33 章 入力とエディタ カメラ](33-input-camera.md) | 入力、カメラ、線の描画 |
| 5 エディタの機能 | [第 34 章 シーンのデータと API](34-scene-api.md) | ドキュメントとエンジンの分離、同期 |
|  | [第 35 章 シーン ツリー](35-scene-tree.md) | TreeView、選択、ドラッグ アンド ドロップ |
|  | [第 36 章 プロパティ パネル](36-property-panel.md) | 型ごとの DataTemplate、入力の検証 |
|  | [第 37 章 ピッキングとギズモ](37-picking-gizmo.md) | レイ、ピッキング、ギズモ |
|  | [第 38 章 Undo/Redo](38-undo-redo.md) | コマンド パターン、トランザクション |
|  | [第 39 章 保存と読み込み](39-save-load.md) | JSON、検証、非同期 |
|  | [第 40 章 アセット ブラウザ](40-asset-browser.md) | FileSystemWatcher、サムネイル、ドロップ |
| 6 ゲーム DLL と仕上げ | [第 41 章 Game DLL のインターフェース](41-game-interface.md) | 純粋仮想インターフェースと DLL の境界 |
|  | [第 42 章 ホット リロード](42-hot-reload.md) | シャドウ コピー、状態の引き継ぎ |
|  | [第 43 章 Play モード](43-play-mode.md) | 編集と Play の切り替え、元に戻す |
|  | [第 44 章 ログとエラー処理](44-logging-errors.md) | 例外の捕捉、ログ、ダンプ |
|  | [第 45 章 スレッド、メモリ、IDisposable](45-threads-memory.md) | スレッドの約束、リーク、IDisposable |
|  | [第 46 章 ビルド、テスト、配布](46-build-deploy.md) | Release、配布、CI、テスト |
|  | [第 47 章 まとめと、これから](47-next-steps.md) | 設計の振り返りと、これから |

## この教材の進め方

- 各章は <strong>「ゴール → 追加するもの → 手順（コードつき）→ 新しく出てきたものの解説 → 動作確認 → よくあるミス → 次へ」</strong>の順です。
- <strong>手順は必ず上から順に実行</strong>してください。前の章で作った物の上に次の章を積みます。
- 新しい型や関数が出てきたら、<strong>その場の表で何者かどう使うか C++ では何に近いか</strong>を説明します。
- コードは実際にビルドして確かめては、いません。ビルドが通らないときは各章の「よくあるミス」とエラー メッセージを手がかりにします。

## 関連ページ

- [DirectX 12 Guide](../directx/dx12/index.md)
- [Visual Studio](../vs/index.md)
- [ゲームエンジン](../engine/index.md)
