---
title: アロケータ（メモリの貸し借りの仕組み）
tags:
  - 最適化
  - アロケータ
---

# アロケータ（メモリの貸し借りの仕組み）

**アロケータ**（allocator）は、メモリを貸し出し（確保）、返してもらう（解放）仕組みです。`new` や `malloc` の裏側にも、アロケータがいます。普通のアロケータ（OS やコンパイラのもの）は、どんな大きさ・どんな順番の要求にも応える万能型で、その分、遅く、時間が一定でなく、メモリが散らばります。ゲームでは、用途が決まっていることが多いので、用途に合わせた専用のアロケータを作ると、とても速く、予測可能になります。このカテゴリは、アロケータの種類ごとに、仕組み・コード・使いどころをまとめます。

## アロケータの基本

アロケータは、**2 つの操作**を持ちます。

```cpp
class Allocator {
 public:
  virtual void* Allocate(size_t size, size_t alignment) = 0;
  virtual void Deallocate(void* ptr, size_t size) = 0;
};
```

| 操作 | 意味 |
| --- | --- |
| `Allocate(size, alignment)` | `size` バイトを、`alignment`（境界）に合わせて貸す。足りなければ `nullptr`（または例外） |
| `Deallocate(ptr)` | 返す。種類によっては、できない（リニア）か、一括でだけできる |

### アライメント

メモリの開始位置が、型の大きさの倍数でないと、遅い（またはエラー）ことがあります。確保するたびに、境界に合わせます。

```cpp
constexpr size_t AlignUp(size_t value, size_t alignment) {
  return (value + alignment - 1) & ~(alignment - 1);
}
```

`alignment` は、2 のべき乗（1、2、4、8、16、64 ...）です。`SIMD`（`float4` は 16 バイト）やキャッシュライン（64 バイト）では、大きな境界が必要です。

## なぜ専用のアロケータか

| 万能のアロケータ（`new` / `malloc`）の問題 | 専用アロケータの解決 |
| --- | --- |
| **遅い**（空きを探す・ロックを取る） | ほぼ、ポインタを進めるだけ（数ナノ秒） |
| 時間が一定でない（カクつきの原因） | 常に一定（O(1)） |
| 断片化（細かい空きが増える） | まとめて捨てる・同じ大きさだけで、断片化しない |
| メモリが散らばる（キャッシュに悪い） | 連続して並ぶ（キャッシュに優しい） |
| スレッド間のロック | スレッドごとに持つ・ロックなし |
| 使用量が分からない | 自分で数えられる（デバッグ・予算管理） |

## 種類の一覧

<svg class="fig flow" viewBox="0 0 755 340" role="img" aria-label="アロケータの種類：大きなメモリを、切り分けるやり方の違い"><defs><marker id="fl96255" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">アロケータの種類：大きなメモリを、切り分けるやり方の違い</text><line x1="170.0" y1="185.0" x2="271.5" y2="147.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl96255)"/><line x1="192.0" y1="208.0" x2="289.0" y2="208.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl96255)"/><line x1="170.0" y1="231.0" x2="292.0" y2="276.7" stroke="currentColor" stroke-width="2" marker-end="url(#fl96255)"/><line x1="192.0" y1="191.4" x2="474.0" y2="135.5" stroke="currentColor" stroke-width="2" marker-end="url(#fl96255)"/><path d="M108.5,186.0 Q320.2,134.0 532.0,186.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl96255)"/><line x1="192.0" y1="224.6" x2="491.0" y2="283.9" stroke="currentColor" stroke-width="2" marker-end="url(#fl96255)"/><path d="M108.5,186.0 Q398.8,134.0 689.0,186.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl96255)"/><rect x="28.0" y="188.0" width="161" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2" opacity="0.55"/><text x="108.5" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">OS （大きなメモリ）</text><circle cx="30.0" cy="190.0" r="10" fill="#4c8bf5"/><text x="30.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="253.0" y="104.0" width="160" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="333.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">リニア （アリーナ）</text><circle cx="255.0" cy="106.0" r="10" fill="#2ea043"/><text x="255.0" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="292.0" y="188.0" width="82" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="333.0" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">スタック</text><circle cx="294.0" cy="190.0" r="10" fill="#2ea043"/><text x="294.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="295.0" y="272.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="333.0" y="292.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">プール</text><circle cx="297.0" cy="274.0" r="10" fill="#2ea043"/><text x="297.0" y="274.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="477.0" y="104.0" width="110" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="532.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">フリーリスト</text><circle cx="479.0" cy="106.0" r="10" fill="#2ea043"/><text x="479.0" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="494.0" y="188.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="532.0" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">バディ</text><circle cx="496.0" cy="190.0" r="10" fill="#2ea043"/><text x="496.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="494.0" y="272.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="532.0" y="292.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">スラブ</text><circle cx="496.0" cy="274.0" r="10" fill="#2ea043"/><text x="496.0" y="274.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="651.0" y="188.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="689.0" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">TLSF</text><circle cx="653.0" cy="190.0" r="10" fill="#2ea043"/><text x="653.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text></svg>

| アロケータ | 仕組み | 確保 | 解放 | 向く用途 | 弱点 |
| --- | --- | --- | --- | --- | --- |
| <strong>[リニア](linear.md)</strong>（アリーナ・バンプ） | ポインタを進めるだけ | 最速 | まとめて（`Reset`） | フレームの一時データ、ロード | 個別に返せない |
| [スタック](stack.md) | リニア + マーカーに戻す | 最速 | 後に確保したものから（LIFO） | スコープごとの一時データ | 順番を守る必要 |
| [プール](pool.md) | 同じ大きさのブロックを、並べておく | 最速 | 最速（個別に返せる） | 弾・敵・パーティクル | 大きさが、1 種類だけ |
| [フリーリスト](free-list.md) | 空きを、リストで管理 | 遅め（探す） | 個別（隣と結合） | 大きさがバラバラ・汎用 | 断片化・探す時間 |
| [バディ](buddy.md) | 2 のべき乗に、半分ずつ分割 | 速い | 速い（相棒と結合） | 大きさがバラバラ・断片化を抑えたい | 内部の無駄（最大 50%） |
| [スラブ](slab.md)（サイズクラス） | 大きさの段階ごとに、プールを持つ | 速い | 速い | 汎用（多くのメモリ管理の土台） | クラス間の無駄 |
| [TLSF](tlsf.md) | 2 段階の分類で、空きを O(1) で探す | O(1) | O(1) | リアルタイム・汎用 | 実装が複雑 |
| [フレーム](frame.md) | リニア + フレームごとにリセット | 最速 | フレームの頭で、まとめて | 毎フレームの一時データ | 1 フレームの寿命 |

### そのほかのページ

| ページ | 内容 |
| --- | --- |
| [スレッドとアロケータ](thread-local.md) | スレッドごとのアロケータ、ロックフリーのプール、キャッシュ |
| [STL との接続](stl-adapter.md) | `std::vector` などに、自作のアロケータを使わせる（`pmr`、`allocator_traits`） |
| [malloc の置き換え](global-replace.md) | mimalloc・jemalloc・tcmalloc。`operator new` を、丸ごと替える |
| [デバッグ用アロケータ](debug.md) | ガード・リーク追跡・使用量の計測・ページヒープ |

## 選び方

| 質問 | 答え → 選ぶもの |
| --- | --- |
| **まとめて捨てられるか**（フレーム・ロード・レベル） | はい → リニア / フレーム |
| 後から確保したものを、先に捨てるか（スコープ） | はい → スタック |
| 同じ大きさか（弾・敵・コンポーネント） | はい → プール |
| 大きさがバラバラ、個別に返す | 汎用 → TLSF / フリーリスト / スラブ、またはmimalloc |
| スレッドが複数 | スレッドごとに持つ、または mimalloc など |
| STL のコンテナで使いたい | `std::pmr` と組み合わせる |

!!! note "まず、`new` を減らす"
    アロケータを自作する前に、確保の回数を、減らすほうが、効果が大きいことが多いです（[メモリ確保](../allocation.md)、[毎フレームのヒープ確保を避ける](../frame-allocation.md)）。測って、遅いと分かってから作ります。

## 設計の基本

| ルール | 理由 |
| --- | --- |
| **確保先は、1 回の大きな確保**（起動時） | OS に、何度も頼まない |
| アライメントを守る | 型の要求（`alignof`）、SIMD、キャッシュライン |
| 使用量・最大使用量を数える | 予算管理・デバッグ |
| 足りなくなったときの動きを決める | `nullptr`・例外・assert・拡張 |
| デストラクタは、アロケータが呼ばない | `placement new` で作り、自分でデストラクタを呼ぶ（またはトリビアルな型だけ） |
| スレッド安全かどうかを、はっきりさせる | 既定は、ロックなし（速い）。共有するなら、別に対策（[スレッド](thread-local.md)） |

### オブジェクトを作る

アロケータは、メモリを貸すだけで、オブジェクトを作りません。`placement new` で作ります。

```cpp
template <typename T, typename... Args>
T* New(Allocator& allocator, Args&&... args) {
  void* memory = allocator.Allocate(sizeof(T), alignof(T));
  return new (memory) T(std::forward<Args>(args)...);
}

template <typename T>
void Delete(Allocator& allocator, T* object) {
  object->~T();
  allocator.Deallocate(object, sizeof(T));
}
```

## 使う場面

| 場面 | アロケータ |
| --- | --- |
| **毎フレームの一時データ**（描画命令・衝突の候補・一時文字列） | [フレーム](frame.md)（リニア） |
| ステージのロード中の一時データ | [リニア](linear.md)（ロード後に捨てる） |
| 関数内のスコープごとの一時データ | [スタック](stack.md) |
| 弾・敵・エフェクトなど、作っては消すもの | [プール](pool.md) |
| アセット（大きさがバラバラ） | [TLSF](tlsf.md) / [フリーリスト](free-list.md) |
| ゲーム全体のヒープ | [malloc の置き換え](global-replace.md)（mimalloc など） |
| スレッドごとの作業用メモリ | [スレッド](thread-local.md) |

## よくあるミス

??? failure "測らずに、アロケータを自作する"
    **`new` が、本当に遅いか**を、先にプロファイラーで確かめます（[プロファイラー](../../vs/profiler.md)）。

??? failure "アライメントを無視して、確保する"
    SIMD や `double` で、クラッシュしたり、遅くなったりします。`alignof` を守ります。

??? failure "デストラクタが呼ばれずに、リソースがリークする"
    アロケータの `Reset` は、デストラクタを呼びません。ファイルハンドルなどを持つ型は、自分で `~T()` を呼ぶか、トリビアルな型だけを置きます。

??? failure "リセット後のポインタを使う"
    `Reset` した後の、古いポインタは、すべて無効です。デバッグ時は、解放したメモリを、特別な値で埋めると気づきやすい（[デバッグ用アロケータ](debug.md)）。

??? failure "別のアロケータで確保したものを、別の方で返す"
    確保した本人に返すのが、鉄則です。どのアロケータのものか分かるようにします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アロケータは<strong>「大きなメモリを、自分のやり方で切り分けて貸す」</strong>仕組み
    - [x] 用途が決まれば、専用のアロケータが速い。まとめて捨てる → リニア、同じ大きさ → プール、後入れ先出し → スタック
    - [x] アライメントを守る。デストラクタは、自分で呼ぶ
    - [x] STL とは、`pmr` で接続。全体は mimalloc などに置き換えも選べる
    - [x] 先に測る。まず `new` を減らす

## 関連ページ

- [最適化の進め方](../index.md)
- [メモリ確保](../allocation.md)
- [毎フレームのヒープ確保を避ける](../frame-allocation.md)
- [std::allocator](../../stl/memory/allocator.md)
- [std::pmr](../../stl/memory/pmr.md)
- [オブジェクトプール（パターン）](../../design/patterns/object-pool.md)
