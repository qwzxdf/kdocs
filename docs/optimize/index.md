# 最適化

**最適化**は、プログラムの動きを変えずに、**速く・軽く**することです。ゲームは 1 秒に 60 回（1 フレーム約 16 ミリ秒）、すべての処理を終える必要があるので、最適化は避けて通れません。ただし、**勘で直すと、ほとんど効果がなく、コードが読みにくくなるだけ**になります。このカテゴリでは、「**測る → 原因を見つける → 効果の大きい順に直す → また測る**」という進め方と、ゲームでよく効く技術を、順にまとめます。設計（変更しやすさ）の話は [設計](../design/index.md) にあります。最適化は、**計測した数字**で判断するのが違いです。

!!! tip "ポイント"
    - <strong>計測してから直す。</strong> 遅い場所は、勘では当たらない。プロファイラーで、一番時間を使っている場所を見る。
    - 効果が大きい順は、<strong>アルゴリズム（計算量）→ メモリの並び（キャッシュ）→ メモリ確保 → コピー → 細かい書き方</strong>。
    - 速さは必ず <strong>Release ビルド</strong>で測る（Debug は数倍〜数十倍遅く、別物）。
    - 見るのは平均ではなく<strong>最悪のフレーム</strong>。たまに起きる遅いフレームが、カクつきになる。
    - 速くなったかは、**数字で確認**する。速くならなかった変更は、元に戻す。

## 最適化の進め方

```text
① 目標を決める       ← 「60 FPS（16.6 ms）で動かす」「ロードを 5 秒以内に」
② 計測する           ← どこが遅いか（プロファイラー）
③ 原因を考える        ← アルゴリズム？ メモリ？ 確保？ コピー？ 描画？
④ 1 つだけ直す        ← 1 度に 1 つ。何が効いたか分かるように
⑤ また計測する        ← 速くなった？ なっていなければ元に戻す
⑥ ②へ戻る            ← 目標に届くまで
```

<div class="anim" data-type="graph" data-label="最適化は「測る」からはじめて、「測る」で終わる">
n goal 目標 0 0 hit
n measure 計測 1 0
n find 原因 2 0
n fix 直す 3 0
n check 再計測 4 0
l goal measure
l measure find
l find fix
l fix check
l check measure 戻る
# ① 目標を決める（16.6 ms など）
---
n goal 目標 0 0
n measure 計測 1 0 hit
n find 原因 2 0
n fix 直す 3 0
n check 再計測 4 0
l goal measure hit
l measure find
l find fix
l fix check
l check measure 戻る
# ② プロファイラーで、遅い場所を探す
---
n goal 目標 0 0
n measure 計測 1 0
n find 原因 2 0 hit
n fix 直す 3 0
n check 再計測 4 0
l goal measure
l measure find hit
l find fix
l fix check
l check measure 戻る
# ③ 一番時間を使っている場所の、原因を考える
---
n goal 目標 0 0
n measure 計測 1 0
n find 原因 2 0
n fix 直す 3 0 hit
n check 再計測 4 0
l goal measure
l measure find
l find fix hit
l fix check
l check measure 戻る
# ④ 1 つだけ直す
---
n goal 目標 0 0
n measure 計測 1 0
n find 原因 2 0
n fix 直す 3 0
n check 再計測 4 0 hit
l goal measure
l measure find
l find fix
l fix check hit
l check measure 戻る
# ⑤ 速くなったか確認する。目標に届かなければ、②へ戻る
</div>

## ページ一覧

| ページ | 一言で |
| --- | --- |
| [計測（プロファイリング）](measure.md) | 速さを測る道具と、測り方 |
| [アルゴリズムとデータ構造](algorithms.md) | 計算量を減らす。一番効果が大きい |
| [メモリとキャッシュ](memory-cache.md) | データの並べ方で、速さが何倍も変わる |
| [メモリ確保](allocation.md) | `new` を減らす。使い回す・まとめて確保する |
| [コピーとムーブ](copy-move.md) | 無駄なコピーをなくす |
| [SIMD（ベクトル化）](simd.md) | 1 命令で、複数のデータをまとめて計算 |
| [マルチスレッド化](multithreading.md) | 複数のコアで分担する |
| [コンパイラの最適化](compiler.md) | オプションと、コンパイラに任せられること |
| [描画の最適化](rendering.md) | ドロー コール、バッチ、カリング |
| [ロード時間・起動時間](loading.md) | 待たせない。バイナリ化・非同期 |
| [メモリ使用量](memory-usage.md) | 軽くする。構造体のサイズ、圧縮、リーク探し |

## 最適化の優先順位

| 順番 | 観点 | 効果 | 例 |
| --- | --- | --- | --- |
| 1 | **アルゴリズム** | 桁が変わる | 総当たりの当たり判定を、空間分割に |
| 2 | **メモリの並び** | 数倍 | ポインタの配列を、連続した配列に |
| 3 | **メモリ確保** | 数倍〜 | 毎フレームの `new` をやめる |
| 4 | **コピー** | 数十 % 〜数倍 | 値渡しを、参照に |
| 5 | **並列化・SIMD** | コア数・幅ぶん | ジョブで分担、ベクトル化 |
| 6 | **細かい書き方** | 数 % | `i++` と `++i`（コンパイラがやってくれる） |

効果の大きいものから順に確認します。<strong>1 や 2 を飛ばして 6 を直しても、ほとんど効きません。</strong>

## やってはいけない最適化

| 失敗 | 理由 |
| --- | --- |
| 計測せずに直す | 遅い場所は、勘ではほとんど当たらない |
| Debug で測る | Debug は最適化がなく、標準ライブラリの検査も入る。製品の速さと別物 |
| 平均だけ見る | カクつきは、たまに来る遅いフレーム。最悪値を見る |
| 一度に、たくさん直す | どれが効いたか分からない。悪化した変更も紛れる |
| 読めなくなるほど直す | 数 % のために、メンテナンスできないコードにしない |
| 1 回しか動かない処理を直す | 初期化などは、速くしても体感が変わらない |

「<strong>早すぎる最適化は、諸悪の根源</strong>」（ドナルド・クヌース）。まず読みやすく書き、**遅い場所だけ**直します。

## 設計・ほかのカテゴリにある、最適化の話

最適化は、設計やライブラリの話と重なります。次のページにも、**速さ・軽さ**に関する解説があります（設計側と重複して書いてあります）。

| テーマ | ページ | 最適化との関係 |
| --- | --- | --- |
| **ECS** | [ECS](../design/patterns/ecs.md) | 大量のオブジェクトを、連続した配列で速く回す |
| **データ指向設計** | [データ指向設計](../design/patterns/data-oriented.md) | キャッシュに優しいデータの並び（SoA） |
| **CRTP** | [CRTP とポリシーベース設計](../design/patterns/crtp-policy.md) | 仮想関数の呼び出しをなくす（静的ポリモーフィズム） |
| **オブジェクトプール** | [オブジェクトプール](../design/patterns/object-pool.md) | `new` / `delete` を減らす |
| **PImpl・ヘッダ分割** | [PImpl](../design/patterns/pimpl.md)、[ヘッダとソースの分け方](../design/foundations/header-source.md) | **ビルド時間**の短縮 |
| **パフォーマンス設計** | [パフォーマンス設計](../design/practice/performance-design.md) | 設計の段階で、速さを考える |
| **ビルド** | [ビルドと CMake の構成](../design/practice/build-cmake.md)、[Ninja](../vs/ninja.md) | ビルドの高速化 |
| **仮想関数のコスト** | [仮想関数（基礎）](../basics/virtual.md) | 間接呼び出しと、インライン化の阻害 |
| **キャッシュ・計算量** | [キャッシュ効率（基礎）](../basics/cache.md)、[計算量（基礎）](../basics/big-o.md) | 速さの土台になる知識 |
| **コンテナの選択** | [コンテナの選び方](../container-chart.md)、[std::flat_map](../stl/containers/flat_map.md)、[std::hash](../stl/utilities/hash.md) | 連続メモリ・ハッシュで速く |
| <strong>メモリ確保（STL）</strong> | [std::pmr](../stl/memory/pmr.md)、[std::allocator](../stl/memory/allocator.md) | アロケーターで確保を速く |
| **ハンドル・リソース** | [ハンドル](../engine/handle.md)、[リソース管理](../engine/resource.md) | ポインタの無効化を防ぎ、確保を減らす |
| **シリアライズ** | [シリアライズ](../engine/serialization/index.md)、[simdjson](../libs/serialization/simdjson.md)、[zpp-bits](../libs/serialization/zpp-bits.md) | ロード時間・ファイルサイズ |
| **3D の数学** | [DirectXMath](../3d/directxmath.md)、[SimpleMath](../3d/simplemath.md) | SIMD による高速な計算 |
| **3D の描画・判定** | [深度とカリング](../3d/depth-culling.md)、[メッシュとテクスチャ](../3d/mesh-textures.md)、[3D の衝突判定](../3d/collision-3d.md) | カリング、インスタンシング、ブロードフェーズ |
| **スキニング** | [スキニングとアニメーション](../3d/skinning-animation.md) | GPU スキニング、骨の削減 |

## 関連ページ

- [パフォーマンス設計](../design/practice/performance-design.md)
- [計算量（基礎）](../basics/big-o.md)
- [キャッシュ効率（基礎）](../basics/cache.md)
