# ゲームエンジン

ゲームエンジンやゲームの土台を自分で作るときに必要になる、設計の考え方と実装の仕方をまとめています。重要な順に並べています。

| ページ | 重要度 | 一言で |
| --- | --- | --- |
| [ゲームループと固定タイムステップ](game-loop.md) | <span class="rank rank-must">必須</span> | 入力 → 更新 → 描画 を、正しい時間（固定タイムステップ）で、回し続ける仕組み |
| [シーン管理](scene.md) | <span class="rank rank-must">必須</span> | タイトル・ゲーム・リザルトなどの画面（シーン）を、切り替えて管理する |
| [コンポーネント指向](component.md) | <span class="rank rank-must">必須</span> | オブジェクトを、機能の部品（コンポーネント）で組み立てる。継承の限界を超える |
| [ステートマシン](../design/patterns/state-machine.md) | <span class="rank rank-often">よく使う</span> | 状態（待機・移動・攻撃）と、その遷移を、はっきり管理する |
| [イベントシステム](../design/patterns/event.md) | <span class="rank rank-often">よく使う</span> | 起きたことを、興味のある相手に、相手を知らずに知らせる |
| [リソース管理](resource.md) | <span class="rank rank-often">よく使う</span> | 画像・音・モデルを、1 回だけ読み込んで、使い回す。キャッシュと解放 |
| [シリアライズ](serialization/index.md) | <span class="rank rank-often">よく使う</span> | セーブ・ロード。JSON やバイナリのライブラリの選び方 |
| [ハンドルと世代 ID](handle.md) | <span class="rank rank-often">よく使う</span> | 消えるかもしれない相手を、番号 ＋ 世代で、安全に指す |
| [ECS](../design/patterns/ecs.md) | <span class="rank rank-often">よく使う</span> | データと処理を分けて、大量のオブジェクトを、速く回す |
| [オブジェクトプール](../design/patterns/object-pool.md) | <span class="rank rank-sometimes">たまに</span> | 作っては消すもの（弾・敵）を、あらかじめ用意して、使い回す |
| [入力](input.md) | <span class="rank rank-often">よく使う</span> | キーボード・マウス・ゲームパッドを、毎フレーム決まった形で取る |
| [サウンド](audio.md) | <span class="rank rank-often">よく使う</span> | 効果音と BGM の鳴らし方、ライブラリの選び方 |
| [ゲーム AI](ai/index.md) | <span class="rank rank-sometimes">たまに</span> | ビヘイビア ツリーと経路探索（A*） |
| [ネットワーク](network.md) | <span class="rank rank-sometimes">たまに</span> | UDP、同期、遅れを隠す工夫 |

## 読む順番のおすすめ

1. [ゲームループ](game-loop.md) と [シーン管理](scene.md) で、ゲーム全体の骨組みを作る
2. [コンポーネント指向](component.md) でオブジェクトを作る
3. [ステートマシン](../design/patterns/state-machine.md) と [イベント](../design/patterns/event.md) で、動きとつながりを整理する
4. [リソース管理](resource.md) と [シリアライズ](serialization/index.md) で、読み込みと保存を作る
5. オブジェクトが増えてきたら [ハンドル](handle.md) → [ECS](../design/patterns/ecs.md) → [オブジェクトプール](../design/patterns/object-pool.md)

前提になる C++ の知識は [基礎](../basics/index.md) にまとめています。
