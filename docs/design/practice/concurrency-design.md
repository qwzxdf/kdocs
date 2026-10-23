---
title: 並行処理の設計
tags:
  - 設計
  - 実践
---

# 並行処理の設計

**並行処理**は複数の処理を同時に進める技術です。ゲームでは、「描画」「ゲームの更新」「ファイルのロード」「音の再生」「ネットワーク」を、別々のスレッドで動かすことがあります。うまく使うとロード中も画面が止まらない、複数のコアを使って重い処理を速く終わらせるといった効果があります。ただし、スレッドはバグの温床です。「たまにしか起きない」「デバッグすると消える」バグ（データ競争、デッドロック）が起きやすく、設計でそもそも起きにくくしておくことが一番大事です。この考え方をこのページでまとめます（仕組みは [並行処理（基礎）](../../basics/concurrency.md) と [thread](../../stl/concurrency/thread.md)・[mutex](../../stl/concurrency/mutex.md) を見てください）。

!!! tip "ポイント"
    - <strong>できるだけスレッドを使わない。</strong> まず 1 スレッドで速くする。必要になってから、分ける。
    - 使うなら、<strong>「共有しない」</strong>設計にする。共有するデータが少ないほど、バグも少ない。
    - 共有するなら、所有者を 1 つのスレッドに決める。他はメッセージ（コピー）で伝える。
    - やむを得ず共有するデータは、`mutex` で守るか、`atomic` にする。ロックの範囲は小さく、短く。
    - スレッドを手で作り回さず、「ジョブ（仕事）」を、スレッド プールに任せる。
    - 「スレッドの境界」を、設計図に書く（どのデータをどのスレッドが触るか）。

## 並行処理で起きる問題

| 問題 | 説明 |
| --- | --- |
| **データ競争**（data race） | 2 つのスレッドが同じデータを同時に読み書き（片方は書き込み）する。未定義動作 |
| デッドロック | スレッド A がロック 1 を持ってロック 2 を待ち、B がロック 2 を持ってロック 1 を待つ。永久に止まる |
| 競合状態（race condition） | 実行の順番しだいで結果が変わる。たまにしか再現しない |
| ロックの待ちで遅くなる | 1 つのロックに全スレッドが並んで結局 1 本しか動いていない |
| false sharing | 別々の変数でも同じキャッシュ ラインにあると、スレッドが邪魔しあって遅くなる |

<div class="anim" data-type="graph" data-label="デッドロック：お互いを待って止まる">
n a スレッドA 0 0
n b スレッドB 2 0
n l1 ロック1 0 1
n l2 ロック2 2 1
# 最初：どちらも、まだ何も持っていない
---
n a スレッドA 0 0
n b スレッドB 2 0
n l1 ロック1 0 1 hit
n l2 ロック2 2 1 hit
l a l1 hit 持つ
l b l2 hit 持つ
# A はロック 1、B はロック 2 を取った
---
n a スレッドA 0 0 gone
n b スレッドB 2 0 gone
n l1 ロック1 0 1
n l2 ロック2 2 1
l a l1 hit 持つ
l b l2 hit 持つ
l a l2 gone 待つ
l b l1 gone 待つ
# A はロック 2 を、B はロック 1 を待つ。お互いに待って、永久に動けない
</div>

## 設計の基本方針

### 1. 共有しない（一番安全）

**スレッドごとに自分専用のデータ**を持たせます。データを共有しなければ、データ競争は起きません。

| 方法 | 説明 |
| --- | --- |
| 処理を分割して、データも分割する | 敵の配列を前半と後半に分けて、別々のスレッドで更新する（お互いのデータを触らない） |
| スレッド ローカル（`thread_local`） | スレッドごとに別の変数を持つ（乱数生成器、一時バッファ） |
| コピーして渡す | データをコピーして渡し、渡したら元のスレッドは触らない |
| 結果だけを返す | 仕事の結果を、`std::future` やメッセージ キューで受け取る |

### 2. 所有者を決める（メッセージで伝える）

データの持ち主を1 つのスレッドだけにして、他のスレッドは、メッセージ（依頼）を送って、頼みます。

<svg class="fig flow" viewBox="0 0 544 196" role="img" aria-label="メッセージ キュー：所有者に頼む"><defs><marker id="fl49872" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">メッセージ キュー：所有者に頼む</text><line x1="126.0" y1="87.0" x2="199.0" y2="126.1" stroke="currentColor" stroke-width="2" marker-end="url(#fl49872)"/><text x="162.5" y="100.5" text-anchor="middle" style="font-size:12px">頼む</text><line x1="281.0" y1="148.0" x2="339.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl49872)"/><text x="310.0" y="142.0" text-anchor="middle" style="font-size:12px">取り出す</text><rect x="28.0" y="44.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="83.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">描画スレッド</text><rect x="202.0" y="128.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="240.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">キュー</text><rect x="342.0" y="128.0" width="174" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="429.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲームスレッド 持ち主</text></svg>

```cpp
// スレッド セーフなメッセージ キュー（簡易版）
template <class T>
class MessageQueue {
 public:
  void Push(T message) {
    {
      std::lock_guard lock(mutex_);
      queue_.push(std::move(message));
    }
    cv_.notify_one();
  }

  std::optional<T> TryPop() {
    std::lock_guard lock(mutex_);
    if (queue_.empty()) {
      return std::nullopt;
    }
    T message = std::move(queue_.front());
    queue_.pop();
    return message;
  }

 private:
  std::mutex mutex_;
  std::condition_variable cv_;
  std::queue<T> queue_;
};
```

| 利点 | 説明 |
| --- | --- |
| ロックがキューの中だけで済む | 他のコードはロックを意識しない |
| 所有者が明確 | データを変更するのは、持ち主のスレッドだけ |
| デッドロックしにくい | ロックが 1 つだけ |

### 3. 共有するなら、守る

どうしても共有するなら、次のどれかで守ります。

| 方法 | 使う場面 |
| --- | --- |
| `std::mutex` + `std::lock_guard`（[mutex](../../stl/concurrency/mutex.md)） | 複数の値をまとめて守る。基本はこれ |
| `std::atomic<T>`（[atomic](../../stl/concurrency/atomic.md)） | 1 つの数値・フラグ（カウンター、終了フラグ）。ロック不要 |
| `std::shared_mutex` | 読むのが多く、書くのが少ない（設定など） |
| 不変（読むだけ）にする | 作り終えたら、書き換えないデータは、複数のスレッドで読んでよい |
| ダブル バッファ | 書く用と読む用の 2 つを持ち、フレームの区切りで入れ替える |

### ロックのルール

| ルール | 理由 |
| --- | --- |
| ロックは `lock_guard` / `scoped_lock`（RAII） | 解除し忘れ・例外で外れないのを防ぐ（[RAII](../patterns/raii.md)） |
| ロックの範囲は短く | 長いと他のスレッドが待たされる |
| ロックを持ったまま、重い処理・I/O・他のロックをしない | 遅くなる・デッドロックの元 |
| 複数のロックは、いつも同じ順番で取る（または `std::scoped_lock(a, b)`） | デッドロックを防ぐ |
| ロックの中から、外のコード（コールバック）を呼ばない | 外のコードがさらにロックを取るとデッドロックする |
| データとそれを守るロックを同じクラスにまとめる | どのロックで守るのか、はっきりする |

## ジョブ システム（仕事をプールに任せる）

スレッドを**自分で作って管理する**と大変です。ゲームではスレッド プール（決まった数のスレッドが、待機している）に、ジョブ（小さな仕事）を投げる設計がよく使われます。

<svg class="fig flow" viewBox="0 0 418 280" role="img" aria-label="ジョブキューに仕事を積み、空いたワーカーが取って実行する"><defs><marker id="fl24895" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ジョブキューに仕事を積み、空いたワーカーが取って実行する</text><line x1="133.0" y1="125.0" x2="209.0" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl24895)"/><text x="171.0" y="100.0" text-anchor="middle" style="font-size:12px">取る</text><line x1="149.0" y1="148.0" x2="207.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl24895)"/><text x="178.0" y="142.0" text-anchor="middle" style="font-size:12px">取る</text><line x1="133.0" y1="171.0" x2="209.0" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl24895)"/><text x="171.0" y="184.0" text-anchor="middle" style="font-size:12px">取る</text><rect x="28.0" y="128.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="87.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ジョブ キュー</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="210.0" y="44.0" width="90" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="255.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ワーカー1</text><circle cx="212.0" cy="46.0" r="10" fill="#2ea043"/><text x="212.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="210.0" y="128.0" width="90" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="255.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ワーカー2</text><circle cx="212.0" cy="130.0" r="10" fill="#2ea043"/><text x="212.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="210.0" y="212.0" width="90" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="255.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ワーカー3</text><circle cx="212.0" cy="214.0" r="10" fill="#2ea043"/><text x="212.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text></svg>

```cpp
// 例：重い読み込みを、別のスレッドに任せる（std::async）
std::future<Texture> loading = std::async(std::launch::async, [] {
  return LoadTexture("boss.png");       // 別のスレッドで実行
});

// ... ゲームの更新は、止まらず続く ...

if (loading.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
  Texture texture = loading.get();       // 終わっていれば、受け取る
}
```

| 方法 | 説明 |
| --- | --- |
| `std::async` / `std::future` | 1 回きりの仕事の結果を受け取る（[future](../../stl/concurrency/future.md)） |
| `std::jthread` | 長く動くスレッド（ロード用、ネットワーク用） |
| 自作のスレッド プール + ジョブ キュー | 毎フレーム、細かい仕事を大量に投げる（物理、AI、アニメーション） |
| ライブラリ（Intel TBB、OpenMP、`std::execution::par`） | 配列の処理を並列で分ける（`parallel for`） |

## ゲームでよくあるスレッド構成

| 構成 | 説明 | 難しさ |
| --- | --- | --- |
| **1 スレッド** | すべて、メイン スレッドで | 簡単。まずこれ |
| メイン + ロード スレッド | ロード中も画面（ローディング表示）が止まらない | 易しい（`std::async`） |
| メイン + ワーカー（ジョブ） | 物理・AI・アニメーションをジョブで並列化 | 中 |
| ゲーム スレッド + 描画スレッド | 更新と描画を、1 フレームずらして並行 | 難しい（データの受け渡しの設計が必要） |

### ロードを別スレッドにする（よくある使い方）

| 設計のポイント | 説明 |
| --- | --- |
| ロード スレッドは、データを作るだけ | ゲームの状態（シーン、ECS）は、触らない |
| 作ったものは完成してから、メイン スレッドに渡す | `future` や完成キューで |
| GPU のリソース作成は、API によって、スレッドの制限がある | DirectX 11 は、デバイス自体はスレッド セーフだが、デバイス コンテキストは単一スレッド。注意 |
| 進み具合は、`std::atomic<float>` で伝える | ロード画面の進捗バー |

## ゲームでの使いどころ

| 場面 | 設計 |
| --- | --- |
| ロード | 別スレッドでデータを作り、メインに渡す |
| 物理・AI | エンティティを分割して、ジョブで並列に。結果をまとめる |
| サウンド | ミキサーは別スレッド。メインからはキューで「再生して」と頼む |
| ネットワーク | 受信スレッドがメッセージ キューに積み、メインが読む |
| ログ | ログ スレッドにメッセージを渡して、ファイルに書く（[ログとデバッグ支援](logging-debug.md)） |
| 描画 | ゲームの状態から、描画用のコマンドを**コピーして**、描画側に渡す |

## よくあるミス

??? failure "「たまにしか起きない」バグを放っておく"
    データ競争は動いたり動かなかったりします。**ThreadSanitizer**（Clang / GCC）や、Visual Studio の診断ツールで、競合を探します。

??? failure "`std::thread` を、`join` / `detach` せずに破棄する"
    `std::thread` のデストラクタは、join も detach もされていないと `std::terminate`（プログラムの強制終了）です。`std::jthread`（デストラクタで `join`）を使います。

??? failure "ロックの範囲が広い"
    関数全体をロックすると、他のスレッドが長く待たされます。共有データに触る、ほんの一部だけをロックします。

??? failure "スレッドの中で、ラムダが消えたローカル変数を参照する"
    `[&]` ですぐに消える変数を借りたラムダを、別スレッドで実行すると、ダングリングです。コピーキャプチャ（`[=]`、`[x = std::move(x)]`）にします（[所有権とライフタイム設計](../foundations/ownership-lifetime.md)）。

??? failure "ロックを取る順番がバラバラ"
    スレッドごとに違う順番でロックを取ると、デッドロックします。常に同じ順番にするか、`std::scoped_lock(a, b)` を使います。

??? failure "最適化のために、最初からマルチスレッドにする"
    マルチスレッドは、複雑さが大きく増えます。1 スレッドでアルゴリズムとデータの並びを直してから考えます（[パフォーマンス設計](performance-design.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] まず 1 スレッド。スレッドは必要になってから
    - [x] **共有しない**（データを分ける・コピーして渡す）。共有するなら、所有者を決めて、メッセージで頼む
    - [x] 共有データは `mutex`（`lock_guard`）か `atomic`。ロックは短く、順番は一定に
    - [x] スレッドを手で管理せず、`std::async` やジョブ（スレッド プール）に任せる
    - [x] `std::jthread` を使う。スレッド間のデータの境界を、設計図に書く

## 関連ページ

- [並行処理（基礎）](../../basics/concurrency.md)
- [thread / jthread](../../stl/concurrency/thread.md)
- [mutex](../../stl/concurrency/mutex.md) / [atomic](../../stl/concurrency/atomic.md)
- [RAII とスマートポインタ](../patterns/raii.md)
- [パフォーマンス設計](performance-design.md)
