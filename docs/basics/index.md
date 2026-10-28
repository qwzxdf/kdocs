# 基礎

STL やゲームエンジンのページを読むために必要な、C++ の基本的な考え方をまとめています。重要な順に並べています。

| ページ | 重要度 | 一言で |
| --- | --- | --- |
| [コンパイラとビルドの仕組み](compiler.md) | <span class="rank rank-often">よく使う</span> | ソースが実行ファイルになるまで（プリプロセス・コンパイル・リンク）、エラーの種類、MSVC・Clang・GCC |
| [参照と const 参照](reference.md) | <span class="rank rank-must">必須</span> | コピーせずに、同じものを触る「別名」。関数の引数を軽く・書き換え可能にする |
| [ポインタ](pointer.md) | <span class="rank rank-must">必須</span> | 場所（アドレス）を持つ変数。`nullptr` や、ぶら下がりに注意 |
| [継承と仮想関数](virtual.md) | <span class="rank rank-must">必須</span> | 種類ごとに違う処理を同じ呼び方で。`virtual`・`override`・仮想デストラクタ |
| [テンプレート](template.md) | <span class="rank rank-must">必須</span> | 型をあとから決められるひな形。`vector<int>` の `<int>` の正体 |
| [範囲 for](range-for.md) | <span class="rank rank-must">必須</span> | コンテナの全要素を順に回すループ。`for (auto& x : v)` |
| [ラムダ式](lambda.md) | <span class="rank rank-must">必須</span> | その場で書ける、名前のない小さな関数。キャプチャ（外の変数の使い方） |
| [イテレータ](iterator.md) | <span class="rank rank-often">よく使う</span> | コンテナの「今どこ」を指すもの。無効になる場面に注意 |
| [ムーブ](move.md) | <span class="rank rank-often">よく使う</span> | コピーせず、中身を「移す」。`std::move` と、移した後の状態 |
| [所有権](ownership.md) | <span class="rank rank-often">よく使う</span> | 誰が消す責任を持つか。`unique_ptr` と生ポインタの使い分け |
| [コンテナの選び方](container-chart.md) | <span class="rank rank-must">必須</span> | 迷ったら `std::vector`。ほかのコンテナを選ぶ理由をフローチャートで |
| [ファイル入出力](file-io.md) | <span class="rank rank-often">よく使う</span> | セーブ・設定・ステージの、読み書き。テキストとバイナリ |
| [ranges とビュー](ranges.md) | <span class="rank rank-often">よく使う</span> | 範囲をまとめて扱い、`filter`・`transform` で、コピーせず加工して見る |
| [計算量](big-o.md) | <span class="rank rank-often">よく使う</span> | データが増えたとき、処理の重さが、どう増えるか（O(1)・O(n)・O(n²)） |
| [未定義動作](ub.md) | <span class="rank rank-often">よく使う</span> | 何が起きても、おかしくない操作。範囲外アクセス・符号付き整数のオーバーフローなど |
| [定義済みマクロ](predefined-macros.md) | <span class="rank rank-often">よく使う</span> | `__FILE__`・`__LINE__`・`__func__` など、場所やビルドの情報を取るマクロ。`#` と `##`、機能テスト マクロ |
| [ビット演算](bit-operations.md) | <span class="rank rank-often">よく使う</span> | 整数をビットとして扱う。フラグ・マスク・シフト・`<bit>`。優先順位と、シフトの罠 |
| [キャッシュ効率](cache.md) | <span class="rank rank-sometimes">たまに</span> | メモリの階層と、データの並べ方で、速さが変わる理由 |
| [並行処理の基本](concurrency.md) | <span class="rank rank-sometimes">たまに</span> | 複数の処理を同時に進めるときの、守り方（排他・原子操作） |
