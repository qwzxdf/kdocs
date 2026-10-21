---
title: ヒープ
tags:
  - 基礎
---

# ヒープ

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++98〜</span>
</div>

**ヒープ**は、**`new` や `malloc` で確保する、「好きなときに確保して、好きなときに返せる」メモリ領域**です。**関数を抜けても消えず、大きなものも置ける**代わりに、**確保・解放に時間がかかり、使い終わったら自分で返す責任**があります。<strong>「ヒープ」という言葉は文脈で 3 つの別のものを指す</strong>ので、このページで**整理**します。**ゲームではヒープをどれだけ避けるかが、フレーム時間の安定に直結**します。

!!! tip "ポイント"
    - ヒープ ＝ <strong>`new` / `malloc` で確保する、寿命を自分で決められるメモリ</strong>。<strong>スタックと対になる</strong>。
    - <strong>スタック</strong>：<strong>関数を抜けると自動で消える・高速・小さい</strong>。<strong>ヒープ</strong>：<strong>自分で返すまで残る・遅い・大きい</strong>。
    - <strong>確保が遅い理由</strong>：<strong>空き領域を探す・管理情報を更新する・ロックを取る</strong>。
    - <strong>断片化</strong>：<strong>確保と解放を繰り返すと、空きが細切れになり、大きな塊が取れなくなる</strong>。
    - <strong>所有者を決める</strong>：<strong>`std::unique_ptr` / `std::vector`</strong> に任せ、<strong>生の `new` / `delete` を書かない</strong>。
    - <strong>「ヒープ」は 3 種類の意味がある</strong>：<strong>メモリ領域</strong>・<strong>データ構造（優先度付きキュー）</strong>・<strong>GPU のヒープ（D3D12）</strong>。

## このページの「ヒープ」は、どのヒープか

| 呼び方 | 意味 | 詳しいページ |
| --- | --- | --- |
| <strong>ヒープ（メモリ領域）</strong> | **`new` / `malloc` で確保する自由なメモリ**。**このページ** | — |
| <strong>ヒープ（データ構造）</strong> | <strong>「一番大きい要素が先頭に来る」ように並べた配列</strong>。`priority_queue` の中身 | [make_heap / push_heap / pop_heap](../stl/algorithms/make_heap.md) |
| <strong>GPU のヒープ（D3D12）</strong> | **GPU メモリを確保する単位**（デフォルト ヒープ・アップロード ヒープ）／<strong>記述子を並べるヒープ（ディスクリプタ ヒープ）</strong> | [シーン データ（D3D12）](../rendering/gpu-driven-dx12/scene-data.md) |

**以下はメモリ領域としてのヒープ**の説明です。

## プログラムのメモリの 3 つの領域

**プログラムが使うメモリ**は、**大きく 3 つ**に分かれます。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="メモリの領域">
<text x="20" y="24" class="fig-title">プログラムのメモリ：静的領域・スタック・ヒープ</text>
<rect x="60" y="50" width="200" height="220" fill="none" stroke="currentColor" stroke-width="2"/>
<rect x="60" y="50" width="200" height="50" fill="rgba(150,150,150,0.3)"/><text x="72" y="80" style="font-size:13px">静的領域（グローバル・定数）</text>
<rect x="60" y="100" width="200" height="70" fill="rgba(229,170,40,0.25)"/><text x="72" y="130" style="font-size:13px">ヒープ</text><text x="72" y="150" style="font-size:11px">下から上へ（アドレス大へ）伸びる</text>
<rect x="60" y="170" width="200" height="40" fill="none"/><text x="72" y="194" style="font-size:11px" opacity="0.6">（未使用の広い空き）</text>
<rect x="60" y="210" width="200" height="60" fill="rgba(76,139,245,0.25)"/><text x="72" y="236" style="font-size:13px">スタック</text><text x="72" y="256" style="font-size:11px">上から下へ伸びる</text>
<line x1="160" y1="170" x2="160" y2="150" stroke="currentColor" stroke-width="2"/><line x1="160" y1="210" x2="160" y2="190" stroke="currentColor" stroke-width="2"/>
<text x="300" y="86" style="font-size:13px">静的領域</text><text x="300" y="106" style="font-size:12px">プログラム開始から終了まで存在する（グローバル変数・static）</text>
<text x="300" y="150" style="font-size:13px">ヒープ</text><text x="300" y="170" style="font-size:12px">new / malloc で確保。delete / free で返すまで残る</text>
<text x="300" y="230" style="font-size:13px">スタック</text><text x="300" y="250" style="font-size:12px">ローカル変数・関数の引数。関数を抜けると自動で消える</text>
</svg>

| 領域 | 何が置かれるか | 寿命 | 速さ | 大きさ |
| --- | --- | --- | --- | --- |
| **静的領域** | **グローバル変数・`static`・定数** | **プログラムの開始から終了まで** | 速い | コンパイル時に決まる |
| **スタック** | **ローカル変数・引数・戻り先** | <strong>関数を抜けるまで（自動）</strong> | **非常に速い** | **小さい**（Windows は既定 1 MB） |
| **ヒープ** | **`new` / `malloc` で確保したもの** | **自分で返すまで** | **遅い** | **大きい**（メモリの限り） |

## スタックとの違い

**スタック**は**関数を呼ぶたびに積まれ、抜けるたびに取り除かれる**、**後入れ先出し**の領域です。<strong>確保は「スタック ポインタを動かすだけ」</strong>なので**ほぼ無料**です。

```cpp
void Update() {
  int count = 0;
  float values[16];
}
```

`count` と `values` は**スタック**に置かれ、**`Update` を抜けた瞬間に消えます**。**解放の手間もなく、確保も速い**ですが**関数を抜けると使えなくなり、大きなものは置けません**。

**ヒープ**は、<strong>「必要な大きさを必要なときに確保し、不要になったら返す」</strong>領域です。

```cpp
void Load() {
  int* data = new int[1000000];
  Process(data);
  delete[] data;
}
```

`new int[1000000]`（約 4 MB）は**ヒープ**に置かれます。**`delete[]` で返すまで残り**、**関数の外に渡す**こともできます。

### 使い分け

| 場面 | 置き場所 |
| --- | --- |
| **小さくて、関数の中だけで使う** | **スタック** |
| <strong>大きい（数百 KB 以上）</strong> | **ヒープ**（スタックに置くとあふれる） |
| **関数を抜けても残したい** | **ヒープ**（所有者を決める） |
| **サイズが実行時まで分からない** | **ヒープ**（`std::vector` など） |
| **毎フレーム大量に作って捨てる** | **ヒープを避ける**（[フレーム アロケータ](../optimize/frame-allocation.md)・プール） |

## ヒープの確保が遅い理由

`new` は**ただメモリを渡す**わけではありません。**内部で複数の処理**が走ります。

| 処理 | 内容 |
| --- | --- |
| **空き領域を探す** | **十分な大きさの空きブロック**を、**空きリストから探す**（**断片化していると探索が長い**） |
| **ブロックを切り分ける** | **大きな空きから必要な分を切り取り**、**残りを空きリストに戻す** |
| **管理情報を書く** | **確保したサイズ・状態**を**ブロックの前後に記録**（**解放のとき必要**） |
| **ロックを取る** | **複数のスレッドが同時に確保**するので、**排他制御**（ロック）が**必要**（**競合すると待たされる**） |
| **OS にメモリを要求する** | **空きが足りなければ、OS に追加を頼む**（**ページ フォールトを伴い、さらに遅い**） |

<strong>スタックの確保が「数命令」</strong>なのに対し、**ヒープの確保は、数百ナノ秒〜数マイクロ秒**（**最悪でもっと**）かかります。**1 フレームで何千回も `new` する**と、**フレーム時間が不安定**になり、**ときどきカクつく**原因になります。

## 断片化

**確保と解放を繰り返す**と、**ヒープの空きが細かく分散**します（**断片化**）。**合計の空きは十分でも連続した大きな塊がなく、確保に失敗する**状態です。

<svg class="fig illust motion" data-fig="heap-fragmentation" viewBox="0 0 780 250" role="img" aria-label="ヒープの断片化">
<text x="20" y="24" class="fig-title">確保と解放を繰り返すと、空きが細切れになり、大きな塊が取れなくなる</text>
<g stroke="currentColor" stroke-width="1" fill="none"><rect x="40" y="60" width="700" height="40"/></g>
<g>
<rect x="40" y="60" width="100" height="40" fill="#4c8bf5"/>
<rect x="140" y="60" width="60" height="40" fill="#e5484d"/>
<rect x="200" y="60" width="120" height="40" fill="#4c8bf5"/>
<rect x="320" y="60" width="80" height="40" fill="#e5484d"/>
<rect x="400" y="60" width="140" height="40" fill="#4c8bf5"/>
<rect x="540" y="60" width="90" height="40" fill="#e5484d"/>
<rect x="630" y="60" width="110" height="40" fill="#4c8bf5"/>
</g>
<text x="40" y="52" style="font-size:12px">① 使用中（青）と、使用中（赤）が並ぶ</text>
<g stroke="currentColor" stroke-width="1" fill="none"><rect x="40" y="150" width="700" height="40"/></g>
<g>
<rect x="40" y="150" width="100" height="40" fill="#4c8bf5"/>
<rect x="140" y="150" width="60" height="40" fill="none" stroke="#e5484d" stroke-dasharray="4 3"/>
<rect x="200" y="150" width="120" height="40" fill="#4c8bf5"/>
<rect x="320" y="150" width="80" height="40" fill="none" stroke="#e5484d" stroke-dasharray="4 3"/>
<rect x="400" y="150" width="140" height="40" fill="#4c8bf5"/>
<rect x="540" y="150" width="90" height="40" fill="none" stroke="#e5484d" stroke-dasharray="4 3"/>
<rect x="630" y="150" width="110" height="40" fill="#4c8bf5"/>
</g>
<text x="40" y="142" style="font-size:12px">② 赤を解放：空きは合計 230、しかし最大の連続した空きは 90</text>
<rect x="40" y="200" width="200" height="30" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="5s" repeatCount="indefinite" calcMode="discrete" values="0;0;1;1;0" keyTimes="0;0.4;0.5;0.9;1"/></rect>
<text x="250" y="220" style="font-size:12px;fill:#e5484d" opacity="0"><animate attributeName="opacity" dur="5s" repeatCount="indefinite" calcMode="discrete" values="0;0;0;1;0" keyTimes="0;0.4;0.5;0.55;1"/>サイズ 200 の確保は、空きの合計は足りるのに失敗する</text>
</svg>

| 症状 | 原因・対策 |
| --- | --- |
| <strong>確保に失敗する（空きは合計で足りる）</strong> | **断片化**。**大きなブロックは、起動時に確保して使い回す** |
| **長時間動かすと徐々に遅くなる・メモリが増える** | **断片化**・**リーク**。**プール・アリーナで寿命をそろえる** |
| **メモリ使用量が実際より多く見える** | **解放済みでも、OS に返されていない**（ヒープが保持） |

## ヒープでよく起きる事故

| 事故 | 内容 | 対策 |
| --- | --- | --- |
| **リーク**（メモリ漏れ） | **`delete` し忘れ**。**使えない領域が増え続ける** | **`unique_ptr`・`vector`**（[所有権](ownership.md)） |
| **二重解放** | **同じポインタを、2 回 `delete`** | **解放後に `nullptr` を代入**・**所有者を 1 つに** |
| **ダングリング ポインタ** | **解放済みの領域をまだ指している** | **所有者のスコープを意識**・**`weak_ptr`** |
| **バッファ オーバーラン** | **確保した範囲を超えて、書く** | <strong>範囲チェック（`at`・`span`）</strong> |
| **`new[]` と `delete` の取り違え** | **`new[]` は `delete[]` で**返す | **`vector`・`unique_ptr<T[]>`** |

詳しくは[ポインタ](pointer.md)・[所有権](ownership.md)を参照してください。

## ヒープを減らす・避ける方法

ゲームでは**フレームの途中でヒープを確保しない**のが**基本方針**です。

| 方法 | 内容 |
| --- | --- |
| <strong>事前に確保（`reserve`）</strong> | **`std::vector::reserve`** で**あらかじめ必要な分を確保**し、**途中の再確保を避ける** |
| **スタックを使う** | <strong>小さな配列はスタック（`std::array`・固定長）</strong> |
| **オブジェクト プール** | **同じ型のオブジェクトを、あらかじめ多数作り**、**使い回す**（弾・エフェクト） |
| <strong>フレーム アロケータ（アリーナ）</strong> | **1 フレーム分の領域から、ポインタを進めるだけで確保**し、**フレームの終わりでまとめてリセット**（[フレーム アロケータ](../optimize/frame-allocation.md)） |
| <strong>小さい文字列の最適化（SSO）</strong> | **短い文字列はヒープを使わない**（`std::string` が内部で実施） |
| <strong>PMR（`std::pmr`）</strong> | **アロケータを差し替えられるコンテナ**（[アロケータ](../optimize/allocators/index.md)） |

```cpp
std::vector<Enemy> enemies;
enemies.reserve(256);
```

**`reserve` ひとつで、「ステージ中のヒープ確保」が消える**ことも多く、**最も手軽で効果的**です。

## まとめ：どの用語か迷ったら

| 文脈 | 意味 |
| --- | --- |
| **`new`・`delete`・`malloc`・メモリ確保・リーク** | <strong>メモリ領域のヒープ（このページ）</strong> |
| **`priority_queue`・`make_heap`・先頭が最大** | **データ構造のヒープ** |
| **D3D12・GPU・ディスクリプタ・アップロード** | **GPU のヒープ** |

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒープ ＝ <strong>`new` / `malloc` で確保する、寿命を自分で決められるメモリ</strong>。<strong>スタック</strong>は<strong>自動で消える高速な領域</strong>
    - [x] ヒープの確保は<strong>遅い</strong>（<strong>空き探し・管理情報・ロック</strong>）。<strong>毎フレームの確保は避ける</strong>
    - [x] <strong>断片化</strong>で<strong>空きの合計が足りても大きな塊が取れなくなる</strong>
    - [x] 所有者を決めて<strong>`unique_ptr` / `vector`</strong>。<strong>生の `new` / `delete` は書かない</strong>
    - [x] <strong>`reserve`・プール・フレーム アロケータ</strong>で<strong>ヒープを減らす</strong>
    - [x] <strong>「ヒープ」は 3 種類</strong>：<strong>メモリ領域・データ構造・GPU のヒープ</strong>

## 参考

- [C++ Core Guidelines: Resource management](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#r-resource-management)
- Gregory, "Game Engine Architecture"（メモリ管理の章）

## 関連ページ

- [ポインタ](pointer.md)
- [所有権](ownership.md)
- [キャッシュとメモリ](cache.md)
- [フレーム アロケータ（最適化）](../optimize/frame-allocation.md)
- [アロケータ（最適化）](../optimize/allocation.md)
- [make_heap / push_heap / pop_heap](../stl/algorithms/make_heap.md)
