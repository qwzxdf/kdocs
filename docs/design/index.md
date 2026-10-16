# 設計

ゲームのコードを「動く」だけでなく「直しやすく・増やしやすく」するための考え方をまとめています。ここは関数の説明ではないので、各ページは「悪い例 → 何が困るか → 良い例 → いつ使う・使わない」の流れで書いています。重要な順に並べています。

## 基本

| ページ | 重要度 | 一言で |
| --- | --- | --- |
| [設計の基本原則](principles.md) | <span class="rank rank-must">必須</span> | 単一責任・疎結合・合成・DRY・YAGNI |
| [クラス設計](class-design.md) | <span class="rank rank-must">必須</span> | 壊れた状態を作らせないクラスの作り方 |
| [ヘッダとソースの分け方](header-source.md) | <span class="rank rank-must">必須</span> | include を減らし、ビルドを速く、循環を防ぐ |
| [命名とコーディング規約](naming.md) | <span class="rank rank-often">よく使う</span> | 名前の付け方と書き方をそろえる |
| [エラー処理の方針](error-handling.md) | <span class="rank rank-often">よく使う</span> | assert・optional・expected・例外の使い分け |

## パターン

| ページ | 重要度 | 一言で |
| --- | --- | --- |
| [シングルトンとグローバル](singleton.md) | <span class="rank rank-often">よく使う</span> | 便利だが使いすぎに注意。代わりの方法 |
| [コマンドパターン](command.md) | <span class="rank rank-often">よく使う</span> | 命令をオブジェクトにする（キーコンフィグ・アンドゥ・リプレイ） |
| [ストラテジー](strategy.md) | <span class="rank rank-often">よく使う</span> | やり方を部品にして差し替える |
| [ファクトリとデータ駆動](factory.md) | <span class="rank rank-often">よく使う</span> | 作る処理をまとめ、数値はデータファイルへ |
| [依存性の注入](dependency-injection.md) | <span class="rank rank-sometimes">たまに</span> | 使う相手を外から渡して差し替えやすく |
| [データ指向設計](data-oriented.md) | <span class="rank rank-sometimes">たまに</span> | データの並びから考えて大量の処理を速く |

ゲームエンジンでよく使うパターン（[ステートマシン](../engine/state-machine.md)、[イベント（オブザーバー）](../engine/event.md)、[オブジェクトプール](../engine/object-pool.md)、[コンポーネント](../engine/component.md)）は [ゲームエンジン](../engine/index.md) にあります。
