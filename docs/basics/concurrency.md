---
title: 並行処理の基本
tags:
  - 基礎
  - 並行処理
---

# 並行処理の基本

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
</div>

**並行処理**（マルチスレッド）は、**複数の処理を同時に進める**ことです。今の CPU には複数のコア（計算する部品）があるので、重い処理を別のスレッドに任せると、ゲームが止まらずに済みます。たとえば「ロード画面のアニメーションを動かしながら、裏でステージを読み込む」がそうです。ただし、**2 つのスレッドが同じデータを同時に触ると壊れる**（データ競争）ので、守り方を知っておく必要があります。

!!! tip "ポイント"
    - スレッドは [`std::jthread`](../stl/concurrency/thread.md) で作る（終わるのを自動で待ってくれる）。
    - **同じデータを複数のスレッドが触るなら、必ず守る**：[`std::mutex`](../stl/concurrency/mutex.md) でロックするか、[`std::atomic`](../stl/concurrency/atomic.md) を使う。
    - 「結果を 1 つ返すだけ」の処理なら [`std::async`](../stl/concurrency/future.md) が一番簡単。
    - ゲームの描画やゲームロジックは、基本的にメインスレッド 1 本で書く。別スレッドに出すのは**ロード・音声・重い計算**など切り離しやすいものだけ。
    - バグが再現しにくく難しいので、必要になるまで使わなくていい。

## 基本

### スレッドを作る

```cpp
#include <print>
#include <thread>

void LoadStage(int stage) {
  std::println("ステージ {} を読み込み中...", stage);
}

int main() {
  std::jthread loader(LoadStage, 3);  // 別のスレッドで LoadStage(3) が動き始める
  // ここでメインスレッドは別のことができる
}  // loader が消えるときに、終わるのを待つ（join）
```

```text title="実行結果"
ステージ 3 を読み込み中...
```

### データ競争（Data Race）

```cpp
int counter = 0;
// スレッド A: ++counter;   スレッド B: ++counter;
```

`++counter` は「読む → 1 足す → 書く」の 3 段階なので、2 つのスレッドが同時に行うと、片方の結果が上書きされて消えることがあります。これは**未定義動作**で、たまにしか起きないので見つけにくいバグになります。

<div class="mem">
<div class="mem-step"><span class="mem-label">スレッド A</span><span class="mem-note">counter を読む（0）→ 1 にする → 書く（1）</span></div>
<div class="mem-step"><span class="mem-label">スレッド B</span><span class="mem-note">　　counter を読む（0）→ 1 にする → 書く（1）</span></div>
<div class="mem-step"><span class="mem-label">結果</span><span class="mem-note">2 回足したのに 1 になる</span></div>
</div>

### 守り方

```cpp
#include <atomic>
#include <mutex>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::atomic<int> atomic_counter = 0;  // 方法 1: atomic（単純な数値ならこれ）

  int counter = 0;                      // 方法 2: mutex で守る
  std::mutex mutex;

  {
    std::vector<std::jthread> workers;
    for (int t = 0; t < 4; ++t) {
      workers.emplace_back([&] {
        for (int i = 0; i < 1000; ++i) {
          ++atomic_counter;
          std::lock_guard lock(mutex);  // この行から } まで、他のスレッドは入れない
          ++counter;
        }
      });
    }
  }  // 全員の終わりを待つ

  std::println("{} {}", atomic_counter.load(), counter);
}
```

```text title="実行結果"
4000 4000
```

## 詳しく

### 道具の使い分け

| やりたいこと | 道具 |
| --- | --- |
| 別のスレッドで処理を動かす | [`std::jthread`](../stl/concurrency/thread.md) |
| 処理を投げて、結果をあとで受け取る | [`std::async` / `std::future`](../stl/concurrency/future.md) |
| 1 つの数値・フラグを共有する | [`std::atomic`](../stl/concurrency/atomic.md) |
| 複数のデータをまとめて守る | [`std::mutex` + `std::lock_guard`](../stl/concurrency/mutex.md) |
| 「データが来るまで待つ」 | [`std::condition_variable`](../stl/concurrency/condition_variable.md) |
| 同時に動く数を制限する・全員がそろうのを待つ | [セマフォ・ラッチ・バリア](../stl/concurrency/latch.md) |
| スレッドに「止まって」と伝える | [`std::stop_token`](../stl/concurrency/stop_token.md#stop_token)（jthread と一緒に使う） |

### 気をつけること

| 問題 | 内容 | 防ぎ方 |
| --- | --- | --- |
| データ競争 | 同じデータを同時に書く | mutex / atomic |
| デッドロック | A を持って B を待つスレッドと、B を持って A を待つスレッドが永遠に待つ | 複数のロックは `std::scoped_lock` で一度に取る |
| 共有しすぎ | ロックだらけで結局 1 本ずつしか動かない | 共有するデータを減らす。各スレッドに自分の分を持たせ、最後にまとめる |
| UI・描画 API を別スレッドから呼ぶ | 多くのライブラリはメインスレッドからしか呼べない | 結果だけ受け取り、メインスレッドで反映する |

### ゲームでのよくある形

<svg class="fig flow" viewBox="0 0 870 298" role="img" aria-label="ロードスレッドで読み込み、完了フラグでメインスレッドが切り替える"><defs><marker id="fl33769" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ロードスレッドで読み込み、完了フラグでメインスレッドが切り替える</text><line x1="107.0" y1="124.0" x2="249.0" y2="124.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl33769)"/><line x1="331.0" y1="124.0" x2="524.0" y2="124.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl33769)"/><path d="M565.0,102.0 Q315.5,50.0 66.0,102.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl33769)"/><text x="315.5" y="64.0" text-anchor="middle" style="font-size:12px">繰り返す</text><line x1="290.0" y1="147.0" x2="290.0" y2="227.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl33769)"/><text x="290.0" y="181.0" text-anchor="middle" style="font-size:12px">開始</text><line x1="415.0" y1="250.0" x2="473.0" y2="250.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl33769)"/><text x="444.0" y="244.0" text-anchor="middle" style="font-size:12px">終わったら</text><line x1="604.2" y1="227.0" x2="740.8" y2="147.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl33769)"/><text x="672.5" y="181.0" text-anchor="middle" style="font-size:12px">毎フレーム確認</text><rect x="28.0" y="104.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">入力</text><circle cx="30.0" cy="106.0" r="10" fill="#4c8bf5"/><text x="30.0" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="252.0" y="104.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="290.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">更新</text><circle cx="254.0" cy="106.0" r="10" fill="#4c8bf5"/><text x="254.0" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="527.0" y="104.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="565.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">描画</text><circle cx="529.0" cy="106.0" r="10" fill="#4c8bf5"/><text x="529.0" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="168.0" y="230.0" width="244" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="290.0" y="250.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ロードスレッド ステージ読み込み</text><circle cx="170.0" cy="232.0" r="10" fill="#2ea043"/><text x="170.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="476.0" y="230.0" width="178" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="565.0" y="250.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">完了フラグ （atomic）</text><circle cx="478.0" cy="232.0" r="10" fill="#e5a828"/><text x="478.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="718.0" y="104.0" width="124" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="780.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">シーン切り替え</text><circle cx="720.0" cy="106.0" r="10" fill="#e5484d"/><text x="720.0" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

<!-- fig:data-race-counter:begin -->

<svg class="fig illust motion" data-fig="data-race-counter" viewBox="0 0 780 460" role="img"><rect x="0" y="0" width="780" height="460" rx="14" fill="#ffffff"/>
<defs><marker id="arr-data-race-counter" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">2 つのスレッドが、同じカウンターを +1 する: ロックなしで 1 になる</text>
<text x="60" y="85" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">ロックなし</text>
<line x1="110" y1="138" x2="720" y2="138" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="100" y="144" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">スレッド A</text>
<line x1="110" y1="193" x2="720" y2="193" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="100" y="199" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">スレッド B</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="140" y="120" width="120" height="36" fill="#2563eb" opacity="0.9"/>
<text x="200" y="144" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">読む(0)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.1513;0.1515;1.0000" values="0;0;1;1"/><rect x="280" y="175" width="120" height="36" fill="#2ea043" opacity="0.9"/>
<text x="340" y="199" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">読む(0)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="420" y="120" width="120" height="36" fill="#2563eb" opacity="0.9"/>
<text x="480" y="144" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">書く(1)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.3331;0.3333;1.0000" values="0;0;1;1"/><rect x="560" y="175" width="120" height="36" fill="#2ea043" opacity="0.9"/>
<text x="620" y="199" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">書く(1)</text>
</g>
<text x="390" y="255" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">共有カウンター = 0<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="1;1;0;0"/></text>
<text x="390" y="255" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">共有カウンター = 0<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;0.2422;0.2424;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="255" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">共有カウンター = 1<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;0.3331;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="255" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#e5484d" opacity="0">共有カウンター = 1  ← 2 回足したのに 1<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.3331;0.3333;0.4846;0.4848;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="305" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">std::mutex でロックあり</text>
<line x1="110" y1="353" x2="720" y2="353" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="100" y="359" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">スレッド A</text>
<line x1="110" y1="403" x2="720" y2="403" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="100" y="409" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">スレッド B</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.5149;0.5152;1.0000" values="0;0;1;1"/><rect x="140" y="335" width="260" height="36" fill="#2563eb" opacity="0.9"/>
<text x="270" y="359" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">ロック+読む+書く</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.5149;0.5152;1.0000" values="0;0;1;1"/><rect x="140" y="385" width="260" height="36" fill="#64748b" opacity="0.9"/>
<text x="270" y="409" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">待つ</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;1.0000" values="0;0;1;1"/><rect x="420" y="385" width="260" height="36" fill="#2ea043" opacity="0.9"/>
<text x="550" y="409" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">ロック+読む+書く</text>
</g>
<text x="390" y="450" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">共有カウンター = 2（正しい）<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.7573;0.7576;1.0000" values="0;0;1;1"/></text>
</svg>

<!-- fig:data-race-counter:end -->

## よくあるミス

??? failure "守らずに共有する"
    「たぶん大丈夫」で共有した変数が、数時間に 1 回だけ壊れる、というバグになります。共有するものは必ず守ります。

??? failure "std::thread の join を忘れる"
    `std::thread` は、join も detach もせずに消えるとプログラムが強制終了します。`std::jthread` を使えば自動で join されます。

??? failure "スレッドの中からメインの描画やエンジンの関数を呼ぶ"
    多くのグラフィック・ウィンドウの API はメインスレッド専用です。読み込んだデータだけを渡し、GPU への登録などはメインスレッドで行います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スレッドは jthread、結果を受け取るなら async
    - [x] 共有するデータは mutex か atomic で必ず守る
    - [x] ゲームのロジックと描画はメインスレッド。重い処理だけ外に出す

## 関連ページ

- [std::thread / std::jthread](../stl/concurrency/thread.md)
- [std::mutex](../stl/concurrency/mutex.md)
- [std::atomic](../stl/concurrency/atomic.md)
