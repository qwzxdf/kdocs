# ゲームエンジン

ゲームエンジンやゲームの土台を自分で作るときに必要になる、設計の考え方と実装の仕方をまとめています。重要な順に並べています。

| ページ | 重要度 | 一言で |
| --- | --- | --- |
| [ゲームループと固定タイムステップ](game-loop.md) | <span class="rank rank-must">必須</span> | 入力 → 更新 → 描画 を正しい時間で回す |
| [シーン管理](scene.md) | <span class="rank rank-must">必須</span> | タイトル・ゲーム・リザルトを切り替える |
| [コンポーネント指向](component.md) | <span class="rank rank-must">必須</span> | オブジェクトを機能の部品で組み立てる |
| [ステートマシン](../design/patterns/state-machine.md) | <span class="rank rank-often">よく使う</span> | 状態と遷移をはっきり管理する |
| [イベントシステム](../design/patterns/event.md) | <span class="rank rank-often">よく使う</span> | 起きたことを興味のある相手に知らせる |
| [リソース管理](resource.md) | <span class="rank rank-often">よく使う</span> | 画像・音を 1 回だけ読み込んで使い回す |
| [シリアライズ](serialization/index.md) | <span class="rank rank-often">よく使う</span> | セーブ・ロード、JSON やバイナリのライブラリ |
| [ハンドルと世代 ID](handle.md) | <span class="rank rank-often">よく使う</span> | 消えるかもしれない相手を安全に指す |
| [ECS](../design/patterns/ecs.md) | <span class="rank rank-often">よく使う</span> | データと処理を分けて大量のオブジェクトを速く回す |
| [オブジェクトプール](../design/patterns/object-pool.md) | <span class="rank rank-sometimes">たまに</span> | 作っては消すものを使い回す |

## 読む順番のおすすめ

1. [ゲームループ](game-loop.md) と [シーン管理](scene.md) で、ゲーム全体の骨組みを作る
2. [コンポーネント指向](component.md) でオブジェクトを作る
3. [ステートマシン](../design/patterns/state-machine.md) と [イベント](../design/patterns/event.md) で、動きとつながりを整理する
4. [リソース管理](resource.md) と [シリアライズ](serialization/index.md) で、読み込みと保存を作る
5. オブジェクトが増えてきたら [ハンドル](handle.md) → [ECS](../design/patterns/ecs.md) → [オブジェクトプール](../design/patterns/object-pool.md)

前提になる C++ の知識は [基礎](../basics/index.md) にまとめています。
