# 設計

ゲームのコードを「動く」だけでなく「**直しやすく・増やしやすく・壊れにくく**」するための考え方をまとめています。ここは関数の説明ではないので、各ページは「**悪い例 → 何が困るか → 良い例 → いつ使う・使わない**」の流れで書いています。**設計の基礎**（考え方）、**パターン**（困りごとに使える型）、**実践**（作り続けるための技術）の 3 つに分けています。

!!! tip "ポイント"
    - まず **設計の基礎** の「設計の基本原則」「クラス設計」「所有権とライフタイム設計」を読む。
    - 困りごとが出たら、**パターンの早見表**で、使えそうな型を探す。
    - 設計は**最初から完璧に作らない**。動くものを作り、**困ったところから、少しずつ直す**（[リファクタリング](practice/refactoring-smells.md)）。

## 設計の基礎

考え方と、守ると壊れにくくなるルールです。

| ページ | 重要度 | 一言で |
| --- | --- | --- |
| [設計の基本原則](foundations/principles.md) | <span class="rank rank-must">必須</span> | 単一責任・疎結合・合成・DRY・YAGNI |
| [クラス設計](foundations/class-design.md) | <span class="rank rank-must">必須</span> | 壊れた状態を作らせないクラスの作り方 |
| [所有権とライフタイム設計](foundations/ownership-lifetime.md) | <span class="rank rank-must">必須</span> | 誰が消すか、いつまで生きているか |
| [継承と合成](foundations/composition-vs-inheritance.md) | <span class="rank rank-must">必須</span> | 継承の使いどころと、機能を部品にする合成 |
| [const と引数の渡し方](foundations/const-and-passing.md) | <span class="rank rank-must">必須</span> | 値渡し・参照渡し・ムーブの使い分け |
| [インターフェース設計](foundations/interface-design.md) | <span class="rank rank-must">必須</span> | 抽象クラスと concepts で、差し替えられる口を作る |
| [モジュール境界とレイヤー設計](foundations/layers.md) | <span class="rank rank-often">よく使う</span> | 依存の向きを一方向にして、循環を防ぐ |
| [ヘッダとソースの分け方](foundations/header-source.md) | <span class="rank rank-must">必須</span> | include を減らし、ビルドを速く、循環を防ぐ |
| [命名とコーディング規約](foundations/naming.md) | <span class="rank rank-often">よく使う</span> | 名前の付け方と書き方をそろえる |
| [エラー処理の方針](foundations/error-handling.md) | <span class="rank rank-often">よく使う</span> | assert・optional・expected・例外の使い分け |
| [テスト容易性の設計](foundations/testability.md) | <span class="rank rank-often">よく使う</span> | ルールと外部を分け、偽物に差し替える |

## パターン

困りごとに使える「型」です。まず [デザインパターン早見表](patterns/index.md) で、困りごとから探せます。

| ページ | 重要度 | 一言で |
| --- | --- | --- |
| [デザインパターン早見表](patterns/index.md) | <span class="rank rank-must">必須</span> | 困りごとから、使えるパターンを探す |
| [RAII とスマートポインタ](patterns/raii.md) | <span class="rank rank-must">必須</span> | 取得はコンストラクタ、解放はデストラクタ |
| [イベントシステム（オブザーバー）](patterns/event.md) | <span class="rank rank-often">よく使う</span> | 起きたことを、相手を知らずに通知する |
| [ステートマシン](patterns/state-machine.md) | <span class="rank rank-often">よく使う</span> | 状態と遷移を、はっきり管理する |
| [コマンドパターン](patterns/command.md) | <span class="rank rank-often">よく使う</span> | 命令をオブジェクトにする（キーコンフィグ・アンドゥ・リプレイ） |
| [ストラテジー](patterns/strategy.md) | <span class="rank rank-often">よく使う</span> | やり方を部品にして差し替える |
| [ファクトリとデータ駆動](patterns/factory.md) | <span class="rank rank-often">よく使う</span> | 作る処理をまとめ、数値はデータファイルへ |
| [ECS](patterns/ecs.md) | <span class="rank rank-often">よく使う</span> | データと処理を分けて、大量のオブジェクトを速く |
| [オブジェクトプール](patterns/object-pool.md) | <span class="rank rank-sometimes">たまに</span> | 作っては消すものを、使い回す |
| [データ指向設計](patterns/data-oriented.md) | <span class="rank rank-sometimes">たまに</span> | データの並びから考えて、大量の処理を速く |
| [依存性の注入](patterns/dependency-injection.md) | <span class="rank rank-sometimes">たまに</span> | 使う相手を外から渡して、差し替えやすく |
| [シングルトンとグローバル](patterns/singleton.md) | <span class="rank rank-often">よく使う</span> | 便利だが使いすぎに注意。代わりの方法 |
| [PImpl](patterns/pimpl.md) | <span class="rank rank-sometimes">たまに</span> | 実装を `.cpp` に隠して、ビルドを速くする |
| [ビジター](patterns/visitor.md) | <span class="rank rank-sometimes">たまに</span> | 種類が決まったデータに、処理を足す |
| [イテレータ（パターン）](patterns/iterator-pattern.md) | <span class="rank rank-sometimes">たまに</span> | 自作のデータ構造を、範囲 for で回す |
| [デコレータ](patterns/decorator.md) | <span class="rank rank-sometimes">たまに</span> | 機能を、包んで重ねる |
| [CRTP とポリシーベース設計](patterns/crtp-policy.md) | <span class="rank rank-rare">知ってるだけ</span> | コンパイル時に決める多態 |

## 実践

作り続けるための技術です。

| ページ | 重要度 | 一言で |
| --- | --- | --- |
| [リファクタリングとコードの臭い](practice/refactoring-smells.md) | <span class="rank rank-must">必須</span> | 動きを変えずに、小さな手順で整える |
| [アンチパターン集](practice/anti-patterns.md) | <span class="rank rank-must">必須</span> | よくやる、あとで困る書き方 |
| [パフォーマンス設計](practice/performance-design.md) | <span class="rank rank-often">よく使う</span> | 計測してから、キャッシュ・確保・コピーを見直す |
| [ログとデバッグ支援の設計](practice/logging-debug.md) | <span class="rank rank-often">よく使う</span> | レベル付きログ、assert、デバッグ描画 |
| [並行処理の設計](practice/concurrency-design.md) | <span class="rank rank-sometimes">たまに</span> | 共有しない・メッセージで伝える・ロックは短く |
| [ビルドと CMake の構成](practice/build-cmake.md) | <span class="rank rank-sometimes">たまに</span> | ビルドを速く、再現できるように保つ |

## 読む順番のおすすめ

1. [設計の基本原則](foundations/principles.md) → [クラス設計](foundations/class-design.md) → [所有権とライフタイム設計](foundations/ownership-lifetime.md)
2. [RAII](patterns/raii.md)、[継承と合成](foundations/composition-vs-inheritance.md)、[const と引数の渡し方](foundations/const-and-passing.md)
3. 作りながら困ったら、[パターン早見表](patterns/index.md) と [アンチパターン集](practice/anti-patterns.md)
4. コードが大きくなったら、[レイヤー](foundations/layers.md)、[リファクタリング](practice/refactoring-smells.md)、[ビルド](practice/build-cmake.md)

ゲームの仕組み（ゲームループ、シーン、コンポーネント、リソース管理、シリアライズ）は [ゲームエンジン](../engine/index.md) にあります。
