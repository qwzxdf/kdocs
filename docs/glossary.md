# 用語集

このサイトに出てくる用語の一言まとめです。詳しい説明はリンク先のページにあります。五十音順・アルファベット順に並べています。

## C++ の基礎

| 用語 | 一言で | 詳しく |
| --- | --- | --- |
| RAII | 作ったものの片付けをデストラクタに任せて、自動で確実に行う考え方 | [所有権](basics/ownership.md#スコープと寿命raii) |
| イテレータ | コンテナの「今どこを見ているか」。`begin()` は先頭、`end()` は最後の次 | [イテレータ](basics/iterator.md) |
| イテレータの無効化 | 追加・削除で中身が動き、持っていたイテレータ・参照・ポインタが壊れること | [イテレータ](basics/iterator.md#invalidation) |
| 仮想関数 | 基底クラスのポインタから呼んでも、実際の型の関数が呼ばれる仕組み | [継承と仮想関数](basics/virtual.md) |
| キャッシュ効率 | データがメモリ上に連続していると速く処理できること | [キャッシュ効率](basics/cache.md) |
| 計算量（O 記法） | データが増えたときに処理時間がどう増えるかの目安 | [計算量](basics/big-o.md) |
| コンセプト（concepts） | テンプレートに渡せる型の条件 | [テンプレート](basics/template.md#concepts型に条件を付ける) |
| 参照 | 変数の別名。コピーしない | [参照](basics/reference.md) |
| const 参照 | 読むだけの別名。関数の引数の基本 | [参照](basics/reference.md) |
| 償却 O(1) | たまに重いが、平均すると O(1)。vector の push_back | [計算量](basics/big-o.md#amortized) |
| 所有権 | そのオブジェクトを消す責任が誰にあるか | [所有権](basics/ownership.md) |
| スマートポインタ | 自動で delete してくれるポインタ（unique_ptr、shared_ptr） | [unique_ptr](stl/utilities/unique_ptr.md) |
| テンプレート | 型をあとから決められる関数・クラスのひな形 | [テンプレート](basics/template.md) |
| ビュー | 元のデータを変えずに「加工して見る」範囲。遅延評価される | [ranges とビュー](basics/ranges.md) |
| プロジェクション | ranges のアルゴリズムで、比べる前に要素を変換する指定（`&Enemy::hp`） | [ranges とビュー](basics/ranges.md#プロジェクション) |
| ポインタ | 変数の場所（アドレス）を入れる変数 | [ポインタ](basics/pointer.md) |
| 範囲 for | コンテナを先頭から順に回すループ | [範囲 for](basics/range-for.md) |
| 未定義動作（UB） | 規格で「何が起きても知らない」とされている操作 | [未定義動作](basics/ub.md) |
| ムーブ | 中身をコピーせずに持ち主を移すこと | [ムーブ](basics/move.md) |
| ラムダ式 | その場で書ける小さな関数 | [ラムダ式](basics/lambda.md) |
| ranges | 範囲をまとめて扱う C++20 の仕組み | [ranges とビュー](basics/ranges.md) |

## ゲームエンジン

| 用語 | 一言で | 詳しく |
| --- | --- | --- |
| ECS | エンティティ（番号）・コンポーネント（データ）・システム（処理）に分ける設計 | [ECS](engine/ecs.md) |
| オブジェクトプール | 作っては消すものをまとめて確保して使い回す仕組み | [オブジェクトプール](engine/object-pool.md) |
| コンポーネント | オブジェクトに取り付ける機能の部品 | [コンポーネント指向](engine/component.md) |
| 固定タイムステップ | ゲームの状態をいつも決まった時間ずつ進める方法 | [ゲームループ](engine/game-loop.md) |
| シーン | タイトル・ゲーム本編など、場面ごとのまとまり | [シーン管理](engine/scene.md) |
| シリアライズ | オブジェクトを保存・送信できるデータの並びに変換すること | [シリアライズ](engine/serialization/index.md) |
| ステートマシン | 今の状態と、状態の移り方をはっきり管理する仕組み | [ステートマシン](engine/state-machine.md) |
| デルタタイム（dt） | 前のフレームから経過した時間 | [ゲームループ](engine/game-loop.md) |
| ハンドル | オブジェクトをポインタではなく番号（＋世代）で指すもの | [ハンドルと世代 ID](engine/handle.md) |
| オブザーバー（イベント） | 起きたことを、購読している相手にまとめて知らせる仕組み | [イベントシステム](engine/event.md) |
