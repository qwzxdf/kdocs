---
title: ゲームループと固定タイムステップ
tags:
  - ゲームエンジン
---

# ゲームループと固定タイムステップ

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

**ゲームループ**は、<strong>「入力を読む → ゲームの状態を進める → 画面に描く」を毎フレーム繰り返す</strong>、ゲームの心臓部です。どんなゲームエンジンも中ではこのループが回っています。大事なのは「1 回の更新でどれだけ時間を進めるか」で、PC の速さによってゲームの進み方が変わらないようにする工夫（デルタタイム、固定タイムステップ）が必要になります。

!!! tip "ポイント"
    - ループの基本形は `while (running) { ProcessInput(); Update(dt); Render(); }`。
    - 動きは「速さ × 経過時間（dt）」で計算する。フレーム数で動かすと、速い PC ほど速く動いてしまう。
    - **物理や当たり判定は固定タイムステップ**（毎回 1/60 秒ずつ進める）にすると、結果が安定して再現性も出る。
    - 経過時間の計測は `std::chrono::steady_clock`。

!!! info "このページを読む前に"
    [`std::chrono`](../stl/utilities/chrono.md) を使います。

## 基本

### 一番シンプルなループ

```cpp
while (running) {
  ProcessInput();  // キーボード・パッドの状態を読む
  Update();        // ゲームを 1 フレーム進める
  Render();        // 画面に描く
}
```

これだと、**PC が速いほど Update が多く呼ばれ、ゲームが速く進んでしまいます**。

### 可変タイムステップ（デルタタイム）

前のフレームから何秒経ったか（デルタタイム、dt）を測って、動きに掛けます。

```cpp
#include <print>

struct Player {
  float x = 0.0f;
  float speed = 100.0f;  // 1 秒あたり 100 ピクセル
};

int main() {
  Player player;

  // 実際には毎フレーム now() で測るが、ここでは 30FPS と 60FPS を再現する
  for (float dt : {1.0f / 30.0f, 1.0f / 30.0f}) {
    player.x += player.speed * dt;
  }
  float at30fps = player.x;

  player.x = 0.0f;
  for (int i = 0; i < 4; ++i) {
    player.x += player.speed * (1.0f / 60.0f);
  }
  std::println("30FPS で 2 フレーム: {:.2f} / 60FPS で 4 フレーム: {:.2f}", at30fps,
               player.x);
}
```

```text title="実行結果"
30FPS で 2 フレーム: 6.67 / 60FPS で 4 フレーム: 6.67
```

フレームレートが違っても、同じ時間（1/15 秒）で同じ距離だけ進みます。

<svg class="fig flow" viewBox="0 0 412 172" role="img" aria-label="ゲームループ：1 フレームの流れ"><defs><marker id="fl61423" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ゲームループ：1 フレームの流れ</text><line x1="107.0" y1="124.0" x2="165.0" y2="124.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl61423)"/><line x1="247.0" y1="124.0" x2="305.0" y2="124.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl61423)"/><path d="M346.0,102.0 Q206.0,50.0 66.0,102.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl61423)"/><text x="206.0" y="64.0" text-anchor="middle" style="font-size:12px">次のフレーム</text><rect x="28.0" y="104.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">入力</text><rect x="168.0" y="104.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="206.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">更新</text><rect x="308.0" y="104.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="346.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">描画</text></svg>

## 詳しく

### 可変タイムステップの問題

| 問題 | 何が起きるか |
| --- | --- |
| 処理落ちで dt が大きくなる | 弾が壁をすり抜ける、ジャンプの高さが変わる |
| 物理の計算が dt によって変わる | 同じ操作でも結果が毎回少し違う（リプレイ・オンライン同期ができない） |
| デバッガで止めた後 | dt が何秒にもなって、全部が吹っ飛ぶ |

### 固定タイムステップ

**ゲームの状態は、いつも決まった時間（例: 1/60 秒）ずつ進める**方法です。実際に経過した時間を「貯金」しておき、1/60 秒ぶん貯まるたびに Update を 1 回呼びます。

```cpp
#include <print>
#include <vector>

int main() {
  constexpr double kFixedDt = 1.0 / 60.0;
  double accumulator = 0.0;
  int updates = 0;

  // 実際のフレーム時間（重いフレームや軽いフレームが混ざっている）
  std::vector<double> frame_times = {0.016, 0.050, 0.008, 0.016};

  for (double frame_time : frame_times) {
    accumulator += frame_time;
    while (accumulator >= kFixedDt) {  // 貯まった分だけ固定の dt で進める
      ++updates;                       // Update(kFixedDt) を呼ぶ
      accumulator -= kFixedDt;
    }
  }
  std::println("合計 {:.3f} 秒で Update は {} 回", 0.090, updates);
}
```

```text title="実行結果"
合計 0.090 秒で Update は 5 回
```

重いフレーム（0.050 秒）のあとは Update が複数回呼ばれ、軽いフレームでは 0 回のこともあります。**ゲームの中の時間は、いつも 1/60 秒単位で正確に進みます**。

### 本番に近い形

```cpp
#include <algorithm>
#include <chrono>

void RunGame() {
  using Clock = std::chrono::steady_clock;
  constexpr double kFixedDt = 1.0 / 60.0;
  constexpr double kMaxFrameTime = 0.25;  // これ以上は切り捨てる（デバッガで止めた後など）

  auto previous = Clock::now();
  double accumulator = 0.0;

  while (IsRunning()) {
    auto now = Clock::now();
    double frame_time = std::chrono::duration<double>(now - previous).count();
    previous = now;
    frame_time = std::min(frame_time, kMaxFrameTime);  // 「死のスパイラル」を防ぐ

    ProcessInput();

    accumulator += frame_time;
    while (accumulator >= kFixedDt) {
      FixedUpdate(kFixedDt);  // 物理・当たり判定・ゲームロジック
      accumulator -= kFixedDt;
    }

    double alpha = accumulator / kFixedDt;  // 次の Update までの割合（0〜1）
    Render(alpha);                          // 前の状態と今の状態を alpha で補間して描く
  }
}
```

| 部品 | 意味 |
| --- | --- |
| `kMaxFrameTime` | 1 フレームの時間に上限を付ける。重すぎると Update が追いつかず、さらに重くなる「死のスパイラル」を防ぐ |
| `FixedUpdate` | 固定の dt で呼ばれる。物理やロジックはここ |
| `alpha` と補間 | Update が 60 回/秒でも、144Hz のモニタで滑らかに見せるために、前の位置と今の位置の間を描く |

### 何をどこで更新するか

| 処理 | 置き場所 |
| --- | --- |
| 物理、当たり判定、AI、ゲームのルール | `FixedUpdate`（固定 dt） |
| 入力の読み取り | フレームの最初 |
| アニメーション、カメラの追従、パーティクル | `Update(dt)`（可変 dt）か FixedUpdate |
| 描画 | `Render`（補間して描く） |

Unity の `FixedUpdate` と `Update` の違いも、この考え方です。

### 待ち方（フレームレートの制限）

| 方法 | 特徴 |
| --- | --- |
| 垂直同期（VSync） | モニタの更新に合わせて描画 API が待ってくれる。一番簡単で正確 |
| `std::this_thread::sleep_for` | OS の都合で長めに寝ることがあり、正確ではない |
| 忙しく待つ（ループで時間を見る） | 正確だが CPU を 100% 使う |

## ゲームでの例

ライブラリ（DxLib、SDL、raylib、Siv3D など）を使う場合も、ループの形は同じです。

```cpp
while (ProcessMessage() == 0) {   // DxLib の例
  input.Update();
  scene_manager.Update(dt);
  scene_manager.Draw();
  ScreenFlip();                   // VSync で待つ
}
```

<!-- fig:fixed-step-accum:begin -->

<svg class="fig illust motion" data-fig="fixed-step-accum" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-fixed-step-accum" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">固定タイムステップ: 描画の間隔がバラバラでも、物理は一定の刻みで進める</text>
<text x="70" y="100" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">物理の刻み（1/60 秒ごと）</text>
<text x="70" y="215" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">描画フレーム（実際の経過時間）</text>
<line x1="70" y1="140" x2="710" y2="140" stroke="#94a3b8" stroke-width="2"/>
<line x1="70" y1="255" x2="710" y2="255" stroke="#94a3b8" stroke-width="2"/>
<rect x="115.6124031007752" y="235" width="8" height="40" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/></rect>
<text x="119.6124031007752" y="295" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">10 ms<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/></text>
<rect x="214.8372093023256" y="235" width="8" height="40" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1859;0.1862;1.0000" values="0;0;1;1"/></rect>
<text x="218.8372093023256" y="295" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">20 ms<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1859;0.1862;1.0000" values="0;0;1;1"/></text>
<rect x="149.68733850129198" y="120" width="6" height="40" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2066;0.2069;1.0000" values="0;0;1;1"/></rect>
<rect x="438.09302325581393" y="235" width="8" height="40" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3032;0.3034;1.0000" values="0;0;1;1"/></rect>
<text x="442.09302325581393" y="295" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">45 ms<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3032;0.3034;1.0000" values="0;0;1;1"/></text>
<rect x="232.37467700258395" y="120" width="6" height="40" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3239;0.3241;1.0000" values="0;0;1;1"/></rect>
<rect x="315.06201550387595" y="120" width="6" height="40" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3239;0.3241;1.0000" values="0;0;1;1"/></rect>
<rect x="397.7493540051679" y="120" width="6" height="40" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3239;0.3241;1.0000" values="0;0;1;1"/></rect>
<rect x="517.4728682170542" y="235" width="8" height="40" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4204;0.4207;1.0000" values="0;0;1;1"/></rect>
<text x="521.4728682170542" y="295" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">16 ms<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4204;0.4207;1.0000" values="0;0;1;1"/></text>
<rect x="480.43669250645996" y="120" width="6" height="40" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4411;0.4414;1.0000" values="0;0;1;1"/></rect>
<rect x="557.1627906976744" y="235" width="8" height="40" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5377;0.5379;1.0000" values="0;0;1;1"/></rect>
<text x="561.1627906976744" y="295" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">8 ms<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5377;0.5379;1.0000" values="0;0;1;1"/></text>
<rect x="706.0" y="235" width="8" height="40" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6549;0.6552;1.0000" values="0;0;1;1"/></rect>
<text x="710.0" y="295" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b" opacity="0">30 ms<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6549;0.6552;1.0000" values="0;0;1;1"/></text>
<rect x="563.1240310077519" y="120" width="6" height="40" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6756;0.6759;1.0000" values="0;0;1;1"/></rect>
<rect x="645.811369509044" y="120" width="6" height="40" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6756;0.6759;1.0000" values="0;0;1;1"/></rect>
<text x="390" y="345" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">実際の経過時間は、ばらつく（10〜45 ms）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="1;1;0;0"/></text>
<text x="390" y="345" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 1（10 ms）: 物理を 0 回進める<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.1859;0.1862;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="345" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 2（20 ms）: 物理を 1 回進める<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1859;0.1862;0.3032;0.3034;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="345" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 3（45 ms）: 物理を 3 回進める<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3032;0.3034;0.4204;0.4207;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="345" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 4（16 ms）: 物理を 1 回進める<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4204;0.4207;0.5377;0.5379;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="345" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 5（8 ms）: 物理を 0 回進める<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5377;0.5379;0.6549;0.6552;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="345" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">フレーム 6（30 ms）: 物理を 2 回進める<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6549;0.6552;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">溜まった時間（アキュムレータ）から、1/60 秒ずつ引いて、引けた回数だけ物理を進める</text>
</svg>

<!-- fig:fixed-step-accum:end -->

## よくあるミス

??? failure "フレーム数で動かす"
    `x += 2;` を毎フレーム実行すると、60FPS と 144FPS で速さが 2 倍以上違います。`x += speed * dt;` にします。

??? failure "dt に上限を付けない"
    ウィンドウをドラッグしている間やデバッガで止めた後、dt が数秒になり、キャラクターが壁をすり抜けて飛んでいきます。

??? failure "float で経過時間を足し続ける"
    長時間のプレイで誤差が溜まります。合計時間は `double` か、整数の `std::chrono::nanoseconds` などで持ちます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力 → 更新 → 描画 を毎フレーム繰り返す
    - [x] 動きは `速さ × dt`
    - [x] 物理・ロジックは固定タイムステップ、dt には上限
    - [x] 計測は `steady_clock`

## 関連ページ

- [std::chrono](../stl/utilities/chrono.md)
- [Gaffer On Games: Fix Your Timestep!](https://gafferongames.com/post/fix_your_timestep/)
