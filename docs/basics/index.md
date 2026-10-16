# 基礎

STL やゲームエンジンのページを読むために必要な、C++ の基本的な考え方をまとめています。重要な順に並べています。

| ページ | 重要度 | 一言で |
| --- | --- | --- |
| [参照と const 参照](reference.md) | <span class="rank rank-must">必須</span> | コピーせずに同じものを触る「別名」 |
| [ポインタ](pointer.md) | <span class="rank rank-must">必須</span> | 場所（アドレス）を持つ変数 |
| [継承と仮想関数](virtual.md) | <span class="rank rank-must">必須</span> | 種類ごとに違う処理を同じ呼び方で |
| [テンプレート](template.md) | <span class="rank rank-must">必須</span> | 型をあとから決められるひな形 |
| [範囲 for](range-for.md) | <span class="rank rank-must">必須</span> | コンテナを順に回すループ |
| [ラムダ式](lambda.md) | <span class="rank rank-must">必須</span> | その場で書く小さな関数 |
| [イテレータ](iterator.md) | <span class="rank rank-often">よく使う</span> | コンテナの「今どこ」 |
| [ムーブ](move.md) | <span class="rank rank-often">よく使う</span> | コピーせずに中身を移す |
| [所有権](ownership.md) | <span class="rank rank-often">よく使う</span> | 誰が消す責任を持つか |
| [ファイル入出力](file-io.md) | <span class="rank rank-often">よく使う</span> | セーブ・設定・ステージの読み書き |
| [ranges とビュー](ranges.md) | <span class="rank rank-often">よく使う</span> | 範囲をまとめて扱う・加工して見る |
| [計算量](big-o.md) | <span class="rank rank-often">よく使う</span> | データが増えたときの重さの増え方 |
| [未定義動作](ub.md) | <span class="rank rank-often">よく使う</span> | 何が起きてもおかしくない操作 |
| [キャッシュ効率](cache.md) | <span class="rank rank-sometimes">たまに</span> | データの並べ方で速さが変わる理由 |
| [並行処理の基本](concurrency.md) | <span class="rank rank-sometimes">たまに</span> | 複数の処理を同時に進めるときの守り方 |
