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
| 1 エンジンを作る | [第 1 章 全体像とソリューションの設計](01-overview.md) | 5 つのプロジェクトの役割、依存の規則、ソリューションの作成、出力先の共通化 |
| | [第 2 章 Engine プロジェクト：DLL の骨組み](02-engine-skeleton.md) | DLL とエクスポート、公開ヘッダー、ログ、エンジンの入口 |
| | [第 3 章 Engine に DirectX 12 を載せる](03-engine-dx12.md) | デバイス、スワップ チェーン、フレーム、色で画面を塗る |
| | [第 4 章 Player：エンジンを動かす実行側](04-player.md) | ウィンドウを作り、Engine を呼ぶ。最初の動作確認 |

以降の章（C# 入門、WPF、Prism、連携、ビューポート、エディタ機能、ホット リロード、Play モード）はこの目次に順に追加されます。

## この教材の進め方

- 各章は <strong>「ゴール → 追加するもの → 手順（コードつき）→ 新しく出てきたものの解説 → 動作確認 → よくあるミス → 次へ」</strong>の順です。
- <strong>手順は必ず上から順に実行</strong>してください。前の章で作った物の上に次の章を積みます。
- 新しい型や関数が出てきたら、<strong>その場の表で何者かどう使うか C++ では何に近いか</strong>を説明します。
- コードは実際にビルドして確かめては、いません。ビルドが通らないときは各章の「よくあるミス」とエラー メッセージを手がかりにします。

## 関連ページ

- [DirectX 12 Guide](../directx/dx12/index.md)
- [Visual Studio](../vs/index.md)
- [ゲームエンジン](../engine/index.md)
