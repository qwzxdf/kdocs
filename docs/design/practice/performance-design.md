---
title: パフォーマンス設計
tags:
  - 設計
  - 実践
---

# パフォーマンス設計

!!! info "詳しくは「最適化」へ"
    計測の方法、キャッシュ、メモリ確保、SIMD、マルチスレッド、描画、ロードなどの**具体的な最適化**は、[最適化](../../optimize/index.md) のカテゴリにまとめています。このページは設計の面から見た、速さの考え方の入口です。

ゲームは毎秒 60 回（1 フレーム約 16 ミリ秒）、すべての処理を終える必要があります。1 フレームでも間に合わないと、画面がカクつきます。パフォーマンス（速さ）は、あとから部分的に直すより、最初の設計で決まる部分が大きいです。ただし、やみくもに速くしようとすると、読みにくいだけで効果のないコードになります。大事なのは、「どこが遅いかを測ってから、効果の大きい順に直す」ことと、「最初から遅くなりにくい設計にしておく」ことです。このページはメモリ確保、キャッシュ、コピーとムーブ、アルゴリズムの 4 つの観点で、速さを設計に組み込む考え方をまとめます。

!!! tip "ポイント"
    - <strong>推測で最適化しない。</strong> **計測（プロファイラー）→ 一番遅い所を直す → また計測**。
    - 効果が大きい順は、アルゴリズム（計算量）→ メモリの並び（キャッシュ）→ メモリ確保 → コピー → 細かい書き方。
    - 毎フレーム何千回も呼ぶ所だけ、気にする。1 回だけの処理は、読みやすさを優先する。
    - 連続したメモリ（`vector`）に、同じ種類のデータを並べると、速い。
    - 毎フレームの `new` / `delete`、`vector` の作り直しを避ける（使い回す）。
    - デバッグ ビルドで速さを測らない。 必ず Release で。

## 速さを考える順番

<svg class="fig flow" viewBox="0 0 1084 112" role="img" aria-label="性能改善は、効果の大きい順に進める"><defs><marker id="fl8283" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">性能改善は、効果の大きい順に進める</text><line x1="135.0" y1="64.0" x2="193.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl8283)"/><line x1="331.0" y1="64.0" x2="389.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl8283)"/><line x1="527.0" y1="64.0" x2="585.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl8283)"/><line x1="709.0" y1="64.0" x2="767.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl8283)"/><line x1="863.0" y1="64.0" x2="921.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl8283)"/><rect x="28.0" y="44.0" width="104" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="80.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">① 計測する</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="196.0" y="44.0" width="132" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="262.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">② アルゴリズム</text><circle cx="198.0" cy="46.0" r="10" fill="#2ea043"/><text x="198.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="392.0" y="44.0" width="132" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="458.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">③ データの並び</text><circle cx="394.0" cy="46.0" r="10" fill="#e5a828"/><text x="394.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="588.0" y="44.0" width="118" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="647.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">④ メモリ確保</text><circle cx="590.0" cy="46.0" r="10" fill="#e5484d"/><text x="590.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="770.0" y="44.0" width="90" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="815.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">⑤ コピー</text><circle cx="772.0" cy="46.0" r="10" fill="#9664e6"/><text x="772.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text><rect x="924.0" y="44.0" width="132" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="990.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">⑥ 細かい書き方</text><circle cx="926.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="926.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">6</text></svg>

| 手順 | やること |
| --- | --- |
| ① 計測する | どこが遅いか（Visual Studio の「パフォーマンス プロファイラー」） |
| ② アルゴリズム | O(n²) を、O(n log n) や O(n) に |
| ③ データの並び | キャッシュに優しく（連続・同じ種類を並べる） |
| ④ メモリ確保 | 使い回す、プール、`reserve` |
| ⑤ コピー | `const&`、ムーブ、`string_view` |
| ⑥ 細かい書き方 | 最後。効果は小さいことが多い |

| 観点 | 効果の大きさ | 例 |
| --- | --- | --- |
| <strong>アルゴリズム（計算量）</strong> | とても大きい | 当たり判定を全員総当たりから空間分割に（[O(n²)](../../basics/big-o.md#on2) → O(n)） |
| メモリの並び（キャッシュ） | 大きい | 配列の構造体を種類ごとの配列に |
| メモリ確保 | 中〜大 | 毎フレームの `new` を、使い回しに |
| コピー | 中 | 大きなオブジェクトの値渡しを、参照に |
| 細かい書き方 | 小 | `i++` と `++i` の違い、など |

## 1. 計測する

<strong>一番大事です。</strong> 人間の「ここが遅そう」という勘はよく外れます。

| 道具 | 使い方 |
| --- | --- |
| Visual Studio のパフォーマンス プロファイラー（Alt + F2） | 「CPU の使用率」で、どの関数が全体の何 % を占めるかを見る。Release ビルドで |
| フレーム時間の表示 | 画面に、1 フレームの時間（ミリ秒）を出す（[Dear ImGui](../../libs/imgui/index.md) のグラフが便利） |
| 自作のタイマー | `ScopedTimer`（[RAII](../patterns/raii.md)）で、区間の時間を測る |
| Tracy / Superluminal | ゲーム向けのプロファイラー。フレームごとの流れが見える |

```cpp
// 区間の時間を測る RAII のタイマー
class ScopedTimer {
 public:
  explicit ScopedTimer(const char* name) : name_(name), start_(std::chrono::steady_clock::now()) {}
  ~ScopedTimer() {
    auto elapsed = std::chrono::steady_clock::now() - start_;
    std::println("{}: {:.3f} ms", name_, std::chrono::duration<double, std::milli>(elapsed).count());
  }

 private:
  const char* name_;
  std::chrono::steady_clock::time_point start_;
};

void Update() {
  ScopedTimer timer("Update");   // この関数の時間を測る
  // ...
}
```

## 2. キャッシュに優しいデータの並び

CPU はメモリから**遠くのデータを読むのが、とても遅い**ので近くのデータをキャッシュ（高速な小さな置き場）に先に取り込みます。連続して並んだデータは、一気に取り込めるので速く、あちこちに散らばったデータは、そのたびに遅い読み込みが起きます（[キャッシュ効率](../../basics/cache.md)）。

### 悪い例：オブジェクトのポインタの配列

```cpp
std::vector<std::unique_ptr<Enemy>> enemies;   // 敵がヒープのあちこちに散らばる
for (auto& e : enemies) {
  e->position += e->velocity * dt;             // 1 体ごとに、遠いメモリを読みに行く
}
```

### 良い例：データを連続して並べる

```cpp
std::vector<Enemy> enemies;                    // 敵のデータが、連続して並ぶ
for (Enemy& e : enemies) {
  e.position += e.velocity * dt;               // 次のデータは、すぐ隣にある
}
```

<div class="anim" data-label="連続したメモリ：キャッシュ ラインにまとめて載る">
A B C D E F G H # 連続した配列：8 個が、近くに並ぶ
*A *B *C *D E F G H # 1 回の読み込み（キャッシュ ライン 64 バイト）で、4 個を一度に取り込む
*A *B *C *D *E *F *G *H # 次の読み込みで、残りも一度に。速い
</div>

### 構造体の配列（AoS）と、配列の構造体（SoA）

```cpp
// AoS：1 体ぶんのデータが、まとまっている
struct Enemy { Vec3 position; Vec3 velocity; int hp; std::string name; /* ... */ };
std::vector<Enemy> enemies;

// SoA：項目ごとに、別の配列
struct Enemies {
  std::vector<Vec3> position;
  std::vector<Vec3> velocity;
  std::vector<int> hp;
};
```

| 並べ方 | 向いている処理 |
| --- | --- |
| AoS（構造体の配列） | 1 体の全部の項目をまとめて使う処理 |
| SoA（配列の構造体） | 一部の項目だけを全員に対して処理する（「全員の位置を速度で更新」） |

位置と速度だけが欲しい処理で、AoS だと使わない `name` や `hp` まで一緒に読み込まれるので、キャッシュが無駄になります。SoA なら、必要な項目だけが連続して並びます。これを徹底した設計が、[ECS](../patterns/ecs.md) と [データ指向設計](../patterns/data-oriented.md) です。

### キャッシュに優しくするコツ

| コツ | 説明 |
| --- | --- |
| `vector` を使う | 連続して並ぶ。`list` や `map` は、要素がバラバラで遅い |
| ポインタをたどる回数を減らす | `unique_ptr<T>` の配列より、`T` の配列 |
| 構造体を小さくする | 使わないメンバを減らす。`bool` を並べて、パディングを減らす |
| 熱いデータと冷たいデータを分ける | 毎フレーム使うもの（位置）と、たまにしか使わないもの（名前）を分ける |
| 処理を種類ごとにまとめる | 同じ処理を同じ種類のものに連続して行う（命令のキャッシュにも優しい） |
| 配列を順に読む | ランダムに飛ばず、前から順に |

## 3. メモリ確保を減らす

`new`、`malloc`、`vector` や `string` の拡張は、**1 回が遅く、時間も一定ではない**（[アロケータ](../../stl/memory/allocator.md)）。毎フレーム何度も呼ぶと、カクつきの原因になります。

| 方法 | 説明 |
| --- | --- |
| `reserve` で先に容量を確保 | `push_back` の再確保をなくす（[vector](../../stl/containers/vector.md#reserve)） |
| メンバに持って、使い回す | `clear()` で空にしても容量は残る。毎フレーム新しく作らない |
| オブジェクトプール | 作っては消すもの（弾、パーティクル）を、使い回す（[オブジェクトプール](../patterns/object-pool.md)） |
| フレーム用のアリーナ | 1 フレームだけ使う一時データを、積むだけの領域から取り、フレームの最後に一括解放（[std::pmr](../../stl/memory/pmr.md)） |
| スタックを使う | 小さくて、大きさが決まっているものは、`std::array`（スタック）。ヒープより速い |
| 文字列の連結を避ける | `s += ...` の繰り返しは、再確保が多い。`reserve`、`std::format_to` |

```cpp
// 悪い：毎フレーム、vector を作る
void Update() {
  std::vector<int> nearby;           // 毎フレーム、確保と解放
  FindNearby(nearby);
}

// 良い：メンバに持って、使い回す
class Scene {
  std::vector<int> nearby_;          // 容量が残る
  void Update() {
    nearby_.clear();                  // 空にするだけ（解放しない）
    FindNearby(nearby_);
  }
};
```

## 4. コピーを減らす

| 方法 | 説明 |
| --- | --- |
| **`const T&` で渡す** | 大きいものをコピーしない（[const と引数の渡し方](../foundations/const-and-passing.md)） |
| `string_view` / `span` | 文字列・配列をコピーせずに見る |
| ムーブ | 持ち主を移す。コンテナに入れるときは `std::move` / `emplace_back`（[ムーブ](../../basics/move.md)） |
| 値で返す | RVO・ムーブでコピーは起きない。`const` 参照を返して、危険を作らない |
| 範囲 for は `const auto&` | `for (auto e : enemies)` は、1 体ずつコピー |

## 5. アルゴリズムを見直す

| よくある遅さ | 直し方 |
| --- | --- |
| 全員 × 全員の当たり判定（O(n²)） | **空間分割**（グリッド、四分木、BVH）で、近いものだけ調べる |
| ループの中で毎回 `find`（O(n)） | `unordered_map` / `set` で引く、または先に並べる |
| ループの中で毎回 `vector::erase`（O(n)） | `erase_if`、または「swap して `pop_back`」（[erase_if](../../stl/algorithms/erase_if.md)） |
| 毎フレーム全体を `sort` | 変わったときだけ。ほぼ整列済みなら、挿入ソート |
| 同じ計算を毎フレーム繰り返す | キャッシュする。変わったときだけ再計算（ダーティ フラグ） |
| 文字列で比較する | ID（整数）にする |

## 6. マルチスレッドと分割

1 フレームの処理が重いとき、**複数のコアに分けて並列に**行う方法もあります。ただし、難しく、バグも増えるので、1 スレッドでここまで速くしてから考えます（[並行処理の設計](concurrency-design.md)）。

## 最適化してはいけない場所

| 場面 | 理由 |
| --- | --- |
| 1 回だけ実行される処理（初期化） | 速くしても効果が見えない |
| 計測で遅くないと分かっている所 | 読みにくくなるだけ |
| デバッグ ビルドの速さ | Debug は最適化されていない。製品の速さではない |

「**早すぎる最適化は、諸悪の根源**」（ドナルド・クヌース）。まず分かりやすく書き、遅い所だけ直すのが基本です。

## ゲームでの使いどころ

| 場面 | 設計 |
| --- | --- |
| 大量の弾・パーティクル | 連続した配列 + オブジェクトプール。種類ごとに処理 |
| 当たり判定 | 空間分割。静止物は最初に 1 回だけ構築 |
| AI の更新 | 全員を毎フレーム更新せず、**数フレームに 1 回**、グループに分けて更新する |
| 描画のデータ | 毎フレームの描画コマンドは、フレーム用アリーナに積む |
| 文字列（名前） | 実行時には ID（ハッシュ）を使い、文字列はデバッグ用にだけ持つ |
| ロード時間 | 起動時にまとめて確保。ロード中に作った大きな JSON を、バイナリ化（[シリアライズ](../../engine/serialization/index.md)） |

## よくあるミス

??? failure "Debug ビルドで速さを測る"
    Debug は最適化が無効で、標準ライブラリの検査も入り、数倍〜数十倍遅くなります。Release で測ります。

??? failure "計測せずに、「ここが遅いはず」と最適化する"
    実際のボトルネックは、別の場所にあることがほとんどです。プロファイラーで一番時間を使っている関数を見ます。

??? failure "平均だけを見る"
    ゲームで大事なのは、最悪のフレーム（たまに起きる遅いフレーム）です。平均が 5 ms でも、たまに 50 ms の遅いフレームがあれば、カクつきます。フレーム時間のグラフを見ます。

??? failure "細かい書き方を気にしすぎる"
    `i++` を `++i` にする、`inline` を付ける、といった工夫は、現代のコンパイラが自動でやります。アルゴリズムとデータの並びを見直すほうが、桁違いに効きます。

??? failure "速さのために、読めないコードにする"
    10% 速くなるために、メンテナンスできないコードにすると、後で必ず困ります。ボトルネックだけを最適化し、理由をコメントに残します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 計測してから直す。Release でプロファイラーを使う
    - [x] 効果の順：アルゴリズム → データの並び（キャッシュ）→ メモリ確保 → コピー
    - [x] 連続した `vector` に、同じ種類のデータを並べる
    - [x] 毎フレームの確保をやめ、使い回す（`reserve`、プール、フレーム用アリーナ）
    - [x] 最悪のフレームを見る。平均ではなく

## 関連ページ

- [キャッシュ効率（基礎）](../../basics/cache.md)
- [計算量（基礎）](../../basics/big-o.md)
- [データ指向設計](../patterns/data-oriented.md)
- [ECS](../patterns/ecs.md)
- [オブジェクトプール](../patterns/object-pool.md)
- [std::pmr](../../stl/memory/pmr.md)
- [計測（プロファイリング）](../../optimize/measure.md)
