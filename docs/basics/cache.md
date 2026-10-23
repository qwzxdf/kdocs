---
title: キャッシュ効率
tags:
  - 基礎
  - パフォーマンス
---

# キャッシュ効率

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
</div>

CPU は計算がとても速い一方で、メモリ（RAM）からデータを読むのは遅いです。そこで CPU は、最近使ったデータとその周りを**キャッシュ**という小さくて速い置き場にまとめてコピーしておきます。**データがメモリ上に隙間なく並んでいると、一度読んだときに次の要素もキャッシュに入っている**ので、続けて速く処理できます。逆に、データがあちこちに散らばっていると、毎回遅いメモリまで取りに行くことになります。これが「vector は速く、list は遅い」理由です。

!!! tip "ポイント"
    - <strong>たくさんのデータを毎フレーム回すなら、vector に値で並べて持つ。</strong>
    - ポインタの vector（`vector<Enemy*>`、`vector<unique_ptr<Enemy>>`）は、本体がバラバラに置かれるので回すのが遅くなる。
    - 「よく一緒に使うデータは近くに置く」「使わないデータは分けて置く」と速くなる（ECS や SoA の考え方）。
    - 要素数が少ない（数百個まで）なら、気にしなくてもほとんど差は出ない。

!!! info "このページを読む前に"
    - [basics/index.md](index.md)（このセクション全体の地図と、読む順番）

## 基本

### 速さの目安

| 場所 | 読むのにかかる時間（目安） |
| --- | --- |
| CPU のレジスタ | 1 |
| L1 キャッシュ | 約 4 |
| L2 キャッシュ | 約 12 |
| L3 キャッシュ | 約 40 |
| メモリ（RAM） | 約 200 以上 |

メモリから 1 回読む間に、CPU は数百回の計算ができます。

### 連続していると速い

<div class="mem">
<div class="mem-step"><span class="mem-label">vector&lt;Enemy&gt;</span><span class="mem-cells"><span class="move">A</span><span class="move">B</span><span class="move">C</span><span class="move">D</span></span><span class="mem-note">A を読むと、B・C・D も一緒にキャッシュに入る（キャッシュライン = 64 バイト単位）</span></div>
<div class="mem-step"><span class="mem-label">list / ポインタの vector</span><span class="mem-cells"><span class="move">A</span><span class="free">　</span><span class="free">　</span><span class="move">C</span><span class="free">　</span><span class="move">B</span><span class="free">　</span><span class="free">　</span><span class="move">D</span></span><span class="mem-note">1 つ読むたびに別の場所へ飛ぶ。毎回メモリまで取りに行く</span></div>
</div>

## 詳しく

### AoS と SoA

| 方式 | 書き方 | 得意なこと |
| --- | --- | --- |
| AoS（構造体の配列） | `std::vector<Particle>`（各要素に x, y, vx, vy, color...） | 1 つの要素の全部を使う処理 |
| SoA（配列の構造体） | `struct Particles { std::vector<float> x, y, vx, vy; }` | 一部のメンバだけを全要素に対して使う処理 |

```cpp
#include <print>
#include <vector>

// AoS: 位置の更新に使わない color もキャッシュに載ってしまう
struct ParticleAoS {
  float x, y;
  float vx, vy;
  int color[4];
};

// SoA: 位置の更新に必要な配列だけを読む
struct ParticlesSoA {
  std::vector<float> x, y, vx, vy;
  std::vector<int> color;
};

int main() {
  ParticlesSoA p;
  for (int i = 0; i < 4; ++i) {
    p.x.push_back(0.0f);
    p.vx.push_back(static_cast<float>(i));
  }
  for (std::size_t i = 0; i < p.x.size(); ++i) {
    p.x[i] += p.vx[i];  // x と vx だけが並んで読まれる
  }
  std::println("{} / AoS 1 個 {} バイト", p.x, sizeof(ParticleAoS));
}
```

```text title="実行結果"
[0, 1, 2, 3] / AoS 1 個 32 バイト
```

ECS（[エンティティ・コンポーネント・システム](../design/patterns/ecs.md)）は、この考え方をゲーム全体に広げたものです。

### ホットとコールドを分ける

毎フレーム使うデータ（ホット）と、たまにしか使わないデータ（コールド）を分けると、毎フレームの処理で読むメモリが減ります。

```cpp
struct EnemyHot {   // 毎フレーム更新
  float x, y;
  float vx, vy;
};
struct EnemyCold {  // 死んだときや UI 表示のときだけ
  std::string name;
  std::string description;
};
```

### 2 次元配列は横に回す

```cpp
// tiles[y * width + x] の並びなら
for (int y = 0; y < height; ++y) {
  for (int x = 0; x < width; ++x) {  // 内側を x にすると、メモリを順番に読む
    Process(tiles[y * width + x]);
  }
}
```

内側のループを `y` にすると、毎回 `width` 個ぶん離れた場所を読むことになり、遅くなります。

## ゲームでの例

| 場面 | 工夫 |
| --- | --- |
| 大量のパーティクル・弾 | vector に値で持つ。SoA にする |
| ポリモーフィズムで大量のオブジェクト | 種類ごとに vector を分ける |
| 当たり判定 | 位置と大きさだけの配列を別に持つ |
| タイルマップ | 1 本の vector、内側のループは x |

<!-- fig:cache-stride:begin -->

<svg class="fig illust motion" data-fig="cache-stride" viewBox="0 0 780 460" role="img"><rect x="0" y="0" width="780" height="460" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cache-stride" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">同じ 16 個を読む: 順番に読むと速く、とびとびに読むと遅い</text>
<text x="70" y="86" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">順番に読む（0, 1, 2, 3, ...）</text>
<rect x="70" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="89.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">0</text>
<rect x="111" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="130.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">1</text>
<rect x="152" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="171.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">2</text>
<rect x="193" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="212.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">3</text>
<rect x="248" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="267.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">4</text>
<rect x="289" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="308.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">5</text>
<rect x="330" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="349.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">6</text>
<rect x="371" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="390.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">7</text>
<rect x="426" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="445.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">8</text>
<rect x="467" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="486.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">9</text>
<rect x="508" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="527.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">10</text>
<rect x="549" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="568.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">11</text>
<rect x="604" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="623.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">12</text>
<rect x="645" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="664.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">13</text>
<rect x="686" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="705.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">14</text>
<rect x="727" y="100" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="746.0" y="124.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">15</text>
<rect x="70" y="100" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="111" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0914;0.0916;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="152" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1185;0.1187;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="193" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1455;0.1458;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="248" y="100" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1726;0.1729;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="289" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="330" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2268;0.2271;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="371" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2539;0.2542;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="426" y="100" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2810;0.2813;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="467" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3081;0.3084;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="508" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3352;0.3355;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="549" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3623;0.3626;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="604" y="100" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3894;0.3897;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="645" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4165;0.4168;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="686" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4436;0.4439;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="727" y="100" width="38" height="38" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4707;0.4710;1.0000" values="0;0;0.8;0.8"/></rect>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.0914;0.0916;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0914;0.0916;0.1185;0.1187;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1185;0.1187;0.1455;0.1458;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1455;0.1458;0.1726;0.1729;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1726;0.1729;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.2268;0.2271;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2268;0.2271;0.2539;0.2542;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2539;0.2542;0.2810;0.2813;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2810;0.2813;0.3081;0.3084;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3081;0.3084;0.3352;0.3355;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3352;0.3355;0.3623;0.3626;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3623;0.3626;0.3894;0.3897;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3894;0.3897;0.4165;0.4168;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4165;0.4168;0.4436;0.4439;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4436;0.4439;0.4707;0.4710;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="180" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4707;0.4710;1.0000" values="0;0;1;1"/></text>
<text x="110" y="180" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">回、キャッシュ ミス（赤）。緑 = ヒット</text>
<text x="70" y="236" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">4 つ飛ばしで読む（0, 4, 8, 12, 1, 5, ...）</text>
<rect x="70" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="89.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">0</text>
<rect x="111" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="130.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">1</text>
<rect x="152" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="171.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">2</text>
<rect x="193" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="212.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">3</text>
<rect x="248" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="267.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">4</text>
<rect x="289" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="308.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">5</text>
<rect x="330" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="349.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">6</text>
<rect x="371" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="390.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">7</text>
<rect x="426" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="445.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">8</text>
<rect x="467" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="486.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">9</text>
<rect x="508" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="527.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">10</text>
<rect x="549" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="568.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">11</text>
<rect x="604" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="623.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">12</text>
<rect x="645" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="664.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">13</text>
<rect x="686" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="705.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">14</text>
<rect x="727" y="250" width="38" height="38" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="746.0" y="274.0" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">15</text>
<rect x="70" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="248" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0914;0.0916;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="426" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1185;0.1187;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="604" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1455;0.1458;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="111" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1726;0.1729;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="289" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="467" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2268;0.2271;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="645" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2539;0.2542;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="152" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2810;0.2813;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="330" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3081;0.3084;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="508" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3352;0.3355;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="686" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3623;0.3626;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="193" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3894;0.3897;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="371" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4165;0.4168;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="549" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4436;0.4439;1.0000" values="0;0;0.8;0.8"/></rect>
<rect x="727" y="250" width="38" height="38" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4707;0.4710;1.0000" values="0;0;0.8;0.8"/></rect>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.0914;0.0916;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0914;0.0916;0.1185;0.1187;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1185;0.1187;0.1455;0.1458;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1455;0.1458;0.1726;0.1729;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1726;0.1729;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.2268;0.2271;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">7<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2268;0.2271;0.2539;0.2542;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2539;0.2542;0.2810;0.2813;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2810;0.2813;0.3081;0.3084;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">10<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3081;0.3084;0.3352;0.3355;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">11<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3352;0.3355;0.3623;0.3626;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3623;0.3626;0.3894;0.3897;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">13<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3894;0.3897;0.4165;0.4168;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">14<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4165;0.4168;0.4436;0.4439;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4436;0.4439;0.4707;0.4710;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="330" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4707;0.4710;1.0000" values="0;0;1;1"/></text>
<text x="110" y="330" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">回、キャッシュ ミス（赤）。緑 = ヒット</text>
<text x="70" y="410" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">4 個ずつが 1 つのキャッシュ ライン（隙間で区切り）。キャッシュは 2 ライン分だけ保持する想定</text>
</svg>

<!-- fig:cache-stride:end -->

## よくあるミス

??? failure "何でも unique_ptr の vector にする"
    `std::vector<std::unique_ptr<Bullet>>` は、弾 1 発ごとにヒープに置かれるので、全弾の更新がキャッシュミスだらけになります。ポリモーフィズムが要らないなら `std::vector<Bullet>` にします。

??? failure "少ないデータで気にしすぎる"
    敵が 10 体程度なら、どう並べても差はほぼ出ません。読みやすさを優先し、遅いと分かってから測って直します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 連続したメモリは速く、バラバラなメモリは遅い
    - [x] 大量のデータは vector に値で並べる
    - [x] よく一緒に使うものを近くに、使わないものは分ける

## 関連ページ

- [計算量](big-o.md)
- [std::vector のパフォーマンス](../stl/containers/vector.md#パフォーマンス)
- [ECS](../design/patterns/ecs.md)
