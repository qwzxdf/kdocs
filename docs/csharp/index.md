---
title: C# 連携
tags:
  - C#連携
---

# C# 連携

このカテゴリは、Visual Studio の WPF アプリケーションと C++ のゲーム エンジンをつないで、**エディタを一から作っていく**チュートリアルです。他のカテゴリのように用語を 1 つずつ引くページではありません。最初から最後まで順に手を動かして、1 つのソリューションを大きくしていきます。章を進めるたびにプロジェクトと機能が増えて、最後には、3D ビューポート、シーン ツリー、プロパティ パネル、Undo/Redo、保存、アセット ブラウザ、ゲーム DLL のホット リロード、Play モードを持つエディタが完成します。

C# が初めてでも読めるように、新しい C#・WPF・Prism の言葉や型が出るたびに、その場で説明します。

## 全体の方針

- エンジンと実行側（Engine・Player・Game）は C++、エディタだけが C#（WPF + Prism）です。
- プロジェクトは役割ごとに分けます。Engine（中核）、EngineApi（C# 向けの入口）、Game（ゲームのコード）、Player（実行側）、Editor（エディタ）の 5 つです。
- 描画は DirectX 12 です。3D ビューポートは、WPF の中に Win32 の子ウィンドウを埋め込んで、エンジンがそこへ直接描きます。
- C++ との連携は、C の API と P/Invoke を主に使います。C++/CLI でも同じものを作って、手間を比べます。

## 前提

| 項目 | 前提 |
| --- | --- |
| C++ | 中級（クラス、テンプレート、スマート ポインター、DLL の存在を知っている）。DirectX 12 の説明は[DirectX 12 Guide](../directx/dx12/index.md) へのリンクで、補う |
| C# | 経験なし。第 5 章で C++ と比べながら、必要な範囲を学ぶ |
| WPF・Prism | 経験なし。第 6 章から順に説明する |
| 環境 | Windows 10/11、Visual Studio 2026（「.NET デスクトップ開発」と「C++ によるデスクトップ開発」のワークロード、Windows SDK）、DirectX 12 対応の GPU |
| .NET | .NET 8（LTS） |
| Prism | Prism 9（DryIoc 版）。版で API が変わる所は囲みで示す |

## 完成するもの

MiniEngine（この教材用の小さなゲーム エンジン）と、そのエディタです。

```text
MiniEngine Editor
+--------------+---------------------------+---------------+
| シーン ツリー | 3D ビューポート (DX12)     | プロパティ     |
|  - Camera    |                           |  Position     |
|  - Cube      | （エンジンが直接描く）      |  Rotation     |
|  - Light     |                           |  Scale        |
+--------------+---------------------------+---------------+
| アセット ブラウザ | ログ               [Play] [Stop]       |
+------------------------------------------------------------+
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
|  | [第 12 章 Prism の導入と起動の流れ](12-prism-bootstrap.md) | NuGet で Prism を入れる、PrismApplication で起動を作り替える、最初のビューモデルを ViewModelLocator で結ぶ |
|  | [第 13 章 データバインディングと MVVM](13-binding-mvvm.md) | シーン ツリーとプロパティ パネルをつなぎながら、バインディング、通知（BindableBase）、ICommand（DelegateCommand）、ObservableCollection、MVVM |
|  | [第 14 章 バインディングを掘り下げる](14-binding.md) | 削除ボタン、絞り込み、入力検証を足しながら、Mode と UpdateSourceTrigger、RelativeSource、CollectionView、デバッグ |
|  | [第 15 章 リストとデータ表示](15-lists.md) | アセット一覧とログ一覧を作りながら、ListBox、ComboBox、DataGrid、選択、仮想化 |
|  | [第 16 章 非同期処理と UI スレッド](16-async-ui.md) | アセットの読み込みを作りながら、async / await、Dispatcher、IProgress、キャンセル。DI コンテナーで部品を渡す最初の例 |
|  | [第 17 章 DI とは何か：IoC・DI・DI コンテナー](17-di-basics.md) | Editor の組み立てで見る、自分で new する困りごと、コンストラクター インジェクション、IoC との違い |
|  | [第 18 章 Prism の起動で何が起きるか](18-prism-startup.md) | `Main` の正体、起動の順番、`Container` の持ち主、Service Locator |
|  | [第 19 章 登録とライフタイム](19-registration-lifetime.md) | 遅延生成、Singleton と Transient、未登録の型、インターフェースの要否 |
|  | [第 20 章 ViewModelLocator のしくみ](20-viewmodel-locator.md) | AutoWire の流れ、名前の規則、動かないとき |
|  | [第 21 章 DI コンテナーの種類と DryIoc](21-di-containers.md) | コンテナーの種類、Prism の共通の窓口、DryIoc 単体 |
|  | [第 22 章 リージョン、モジュール、ナビゲーション](22-regions-modules.md) | MainWindow を枠にして、シーン ツリー、プロパティ、アセット、ログをモジュールに分ける。ナビゲーション |
|  | [第 23 章 イベント集約、ダイアログ、サービス](23-events-dialogs.md) | シーン ツリーの選択をプロパティ パネルへ伝える。IEventAggregator、サービス、ダイアログ |
|  | [第 24 章 Prism を掘り下げる](24-prism-deep.md) | KeepAlive、IConfirmNavigationRequest、CompositeCommand |
|  | [第 25 章 MVVM ライブラリを比べる](25-mvvm-libraries.md) | BindableBase と CommunityToolkit.Mvvm などの比較 |
|  | [第 26 章 UserControl とカスタム コントロール](26-custom-controls.md) | UserControl とカスタム コントロール |
|  | [第 27 章 コードビハインドを減らす（Behaviors）](27-behaviors.md) | Behaviors でイベントをコマンドに結ぶ |
|  | [第 28 章 アプリの基本（起動・終了・ウィンドウ・コマンド）](28-app-basics.md) | 起動と終了、ウィンドウ、標準のコマンド |
|  | [第 29 章 アニメーション](29-animation.md) | Storyboard とイージング |
| 3 C# から C++ を呼ぶ | [第 30 章 C# から C++ を呼ぶ：連携方式の比較](30-interop-overview.md) | P/Invoke、C++/CLI、COM、IPC の比較と、境界のルール |
|  | [第 31 章 EngineApi：C の入口を作る](31-engine-api.md) | C の API（ハンドル、エラー コード） |
|  | [第 32 章 P/Invoke で C# から呼ぶ](32-pinvoke.md) | LibraryImport、構造体、SafeHandle、コールバック |
|  | [第 33 章 C++/CLI で橋を作る](33-cpp-cli.md) | C++/CLI の橋と比較 |
|  | [第 34 章 DLL の読み込み、x64、デバッグ](34-dll-loading.md) | 読み込みの仕組みと、エラーの切り分け、混在デバッグ |
| 4 3D ビューポート | [第 35 章 3D ビューポートを埋め込む方法の比較](35-viewport-options.md) | HwndHost、D3DImage、WriteableBitmap などの比較 |
|  | [第 36 章 HwndHost でビューポートを実装する](36-hwndhost.md) | 子ウィンドウの埋め込みと DX12 |
|  | [第 37 章 描画ループとスレッド](37-render-loop.md) | 描画スレッドとコマンド キュー |
|  | [第 38 章 入力とエディタ カメラ](38-input-camera.md) | 入力、カメラ、線の描画 |
| 5 エディタの機能 | [第 39 章 シーンのデータと API](39-scene-api.md) | ドキュメントとエンジンの分離、同期 |
|  | [第 40 章 シーン ツリー](40-scene-tree.md) | TreeView、選択、ドラッグ アンド ドロップ |
|  | [第 41 章 プロパティ パネル](41-property-panel.md) | 型ごとの DataTemplate、入力の検証 |
|  | [第 42 章 ピッキングとギズモ](42-picking-gizmo.md) | レイ、ピッキング、ギズモ |
|  | [第 43 章 Undo/Redo](43-undo-redo.md) | コマンド パターン、トランザクション |
|  | [第 44 章 保存と読み込み](44-save-load.md) | JSON、検証、非同期 |
|  | [第 45 章 アセット ブラウザ](45-asset-browser.md) | FileSystemWatcher、サムネイル、ドロップ |
| 6 ゲーム DLL と仕上げ | [第 46 章 Game DLL のインターフェース](46-game-interface.md) | 純粋仮想インターフェースと DLL の境界 |
|  | [第 47 章 ホット リロード](47-hot-reload.md) | シャドウ コピー、状態の引き継ぎ |
|  | [第 48 章 Play モード](48-play-mode.md) | 編集と Play の切り替え、元に戻す |
|  | [第 49 章 ログとエラー処理](49-logging-errors.md) | 例外の捕捉、ログ、ダンプ |
|  | [第 50 章 スレッド、メモリ、IDisposable](50-threads-memory.md) | スレッドの約束、リーク、IDisposable |
|  | [第 51 章 ビルド、テスト、配布](51-build-deploy.md) | Release、配布、CI、テスト |
|  | [第 52 章 まとめと、これから](52-next-steps.md) | 設計の振り返りと、これから |

## この教材の進め方

- 各章は、「この章で Editor に足すもの」の表で始まります。そのあと、Editor を少し作って動かし、そこで出てきた仕組みを「深掘り」で説明する、という繰り返しです。最後に、動作確認、よくあるミス、ここまでの Editor のファイル一覧が付きます。
- コード ブロックのタイトルで、その扱いが分かります。
    - `ViewModels/SceneObjectViewModel.cs（新規）` や `（変更）`：Editor のファイルです。このまま残ります。
    - `実験：…（Editor には入れない）`：仕組みを見るためだけの、捨てるコードです。
- 手順は必ず上から順に実行してください。前の章で作った物の上に次の章を積みます。
- 新しい型や関数が出てきたら、その場の表で、何者か、どう使うか、C++ では何に近いかを説明します。
- コードは、実際にビルドして確かめてはいません。ビルドが通らないときは、各章の「よくあるミス」とエラー メッセージを手がかりにしてください。

## 関連ページ

- [DirectX 12 Guide](../directx/dx12/index.md)
- [Visual Studio](../vs/index.md)
- [ゲームエンジン](../engine/index.md)
