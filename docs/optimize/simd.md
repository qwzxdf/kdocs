---
title: SIMD（ベクトル化）
tags:
  - 最適化
---

# SIMD（ベクトル化）

**SIMD**（シムディー、Single Instruction, Multiple Data）は、**1 つの命令で、複数のデータをまとめて計算する**CPU の機能です。たとえば、4 つの `float` の足し算を、普通は 4 回の命令で行いますが、SIMD なら**1 回の命令で 4 つ同時**に計算できます（SSE なら 4 個、AVX なら 8 個の `float`）。ゲームには、**大量の座標・色・行列**の計算があるので、SIMD でうまく計算すると、**数倍速く**なることがあります。ただし、**手で書くのは難しい**ので、まず「**コンパイラに自動でやってもらう**」ことから始め、本当に必要なときだけ手で書きます。

!!! tip "ポイント"
    - <strong>まず自動ベクトル化</strong>。ループを、コンパイラが SIMD にできる形で書く（Release、`/O2`）。
    - 自動でできる形は、<strong>連続した配列を、前から順に、同じ計算</strong>。<strong>[SoA](memory-cache.md)</strong>（種類ごとの配列）と相性がよい。
    - 手で書くなら<strong>ライブラリ</strong>（DirectXMath、glm、xsimd、`std::simd`）。<strong>生のイントリンシック</strong>は最後の手段。
    - <strong>データの並び（メモリ）が先</strong>。SIMD の前に、キャッシュとアルゴリズムを直す。
    - <strong>計測して</strong>効果を確かめる。SIMD にしても、メモリがボトルネックなら速くならない。

## SIMD とは

```text
普通（スカラー）：  a0+b0 → a1+b1 → a2+b2 → a3+b3        4 回の命令
SIMD（4 並列）：    [a0 a1 a2 a3] + [b0 b1 b2 b3]          1 回の命令
                  = [a0+b0 a1+b1 a2+b2 a3+b3]
```

<div class="anim" data-label="SIMD：4 つの足し算を、1 回で">
1 2 3 4 | 10 20 30 40 # 4 個ずつの 2 つの配列（a と b）
*1 *2 *3 *4 | *10 *20 *30 *40 # 普通：1 つずつ足すので、命令が 4 回
+11 +22 +33 +44 | _ _ _ _ # SIMD：1 回の命令で、4 つとも同時に足される
</div>

| 名前 | 幅 | `float` の数 | 備考 |
| --- | --- | --- | --- |
| **SSE2** | 128 ビット | 4 | 64 ビット x86 では、必ず使える |
| **AVX / AVX2** | 256 ビット | 8 | 2013 年以降の多くの PC。**使えない CPU もある** |
| **AVX-512** | 512 ビット | 16 | 一部の CPU のみ。発熱で、クロックが下がることも |
| **NEON** | 128 ビット | 4 | ARM（スマホ、Switch、Mac の M シリーズ） |

配るゲームは、**プレイヤーの CPU が AVX2 を持っているとは限らない**ので、「SSE2 は必須でよい」「AVX2 は、あれば使う」のように決めます。

## 1. 自動ベクトル化（まずこれ）

コンパイラは、**ループを見て、SIMD にできそうなら、自動で変換**します（MSVC は `/O2` で有効）。

```cpp
// 自動ベクトル化されやすい書き方
void ScaleAll(float* data, int count, float k) {
  for (int i = 0; i < count; ++i) {
    data[i] *= k;               // 連続した配列を、同じ計算で
  }
}
```

### ベクトル化されやすい条件

| 条件 | 説明 |
| --- | --- |
| **連続した配列**を、前から順に読む | `vector<float>`、`float[]`。ポインタをたどる構造は不可 |
| **ループの回数が、事前に分かる** | `for (i = 0; i < n; ++i)`。途中で `break` しない |
| **反復どうしが独立**している | `a[i]` の計算が、`a[i-1]` の結果に依存しない |
| **同じ型・同じ計算**の繰り返し | 分岐が少ない（`if` が多いと難しい） |
| **ポインタが重ならない**と、コンパイラが分かる | `__restrict` を付ける（MSVC・GCC・Clang） |
| **関数呼び出しがない**（またはインライン化できる） | ループの中で、見えない関数を呼ばない |

### ベクトル化を阻むもの

| 原因 | 直し方 |
| --- | --- |
| ループの中の **`if`** | 計算してから選ぶ（`result = cond ? a : b`）、または分岐を外に出す |
| **構造体の配列**（AoS）で、一部のメンバだけ使う | **SoA** にする（[メモリとキャッシュ](memory-cache.md)） |
| 反復の**依存**（`a[i] = a[i-1] + x`） | アルゴリズムを変える（スキャン、分割して計算） |
| **`std::vector<bool>`** | ビット詰めなので、別。`std::vector<uint8_t>` にする |
| 浮動小数点の**合計**（`sum += a[i]`） | 厳密な順序の保証で、ベクトル化されない。`/fp:fast` を付けるか、手で複数の和に分ける |
| **例外・`virtual` 呼び出し**のあるループ | ループの外へ出す |

### コンパイラに、結果を聞く（MSVC）

プロパティ → C/C++ → コマンド ライン → 追加のオプションに **`/Qvec-report:2`** を入れると、**各ループが、ベクトル化されたか・されなかった理由**を出力してくれます。

```text
--- Analyzing function: ScaleAll
c:\game\math.cpp(5) : info C5001: loop vectorized
c:\game\math.cpp(12) : info C5002: loop not vectorized due to reason '1100'
```

`1100` などの番号は、理由の番号です（公式ドキュメントに一覧があります）。

## 2. 手で書く：数学ライブラリを使う

ゲームの数学（`Vec3`、`Mat4`、クォータニオン）は、**SIMD を使ったライブラリ**がすでにあります。**自分でイントリンシックを書く前に、これを使います**。

| ライブラリ | 特徴 |
| --- | --- |
| **DirectXMath**（`<DirectXMath.h>`） | Windows の標準。`XMVECTOR`、`XMMATRIX` が SIMD。Visual Studio に含まれる。**DirectX と相性が良い** |
| **glm** | OpenGL 風の数学。`GLM_FORCE_SIMD_AVX2` などで SIMD を有効にできる。vcpkg: `glm` |
| **xsimd** | C++ の SIMD ラッパー。SSE / AVX / NEON を、同じコードで書ける。vcpkg: `xsimd` |
| **Eigen** | 行列・線形代数。SIMD を自動で使う |
| **`std::simd`**（C++26） | 標準の SIMD ライブラリ（`<simd>`）。まだ新しく、コンパイラ対応は途中 |

```cpp
#include <DirectXMath.h>
using namespace DirectX;

// 位置を、速度で更新する（XMVECTOR は 4 つの float をまとめた SIMD 型）
void Integrate(XMFLOAT3* positions, const XMFLOAT3* velocities, int count, float dt) {
  XMVECTOR vdt = XMVectorReplicate(dt);
  for (int i = 0; i < count; ++i) {
    XMVECTOR p = XMLoadFloat3(&positions[i]);        // メモリから SIMD レジスタへ
    XMVECTOR v = XMLoadFloat3(&velocities[i]);
    p = XMVectorMultiplyAdd(v, vdt, p);              // p += v * dt（1 命令）
    XMStoreFloat3(&positions[i], p);                 // メモリへ戻す
  }
}
```

### DirectXMath の使い方のコツ

| コツ | 説明 |
| --- | --- |
| **保存用の型と、計算用の型を分ける** | メンバ変数は `XMFLOAT3`（普通の `float` 3 つ）、計算するときだけ `XMVECTOR` にロードする |
| **`XMVECTOR` を、構造体のメンバにしない**（16 バイト境界が必要） | アライメント違反で、クラッシュする |
| **関数の引数は `FXMVECTOR` などの別名** | 呼び出し規約が、レジスタ渡しになる |
| **ロードとストアを、最小限に** | `XMLoad` → 計算を連続 → `XMStore`。行き来すると遅くなる |

## 3. 手で書く：イントリンシック（上級）

CPU の SIMD 命令を、C++ の関数として直接呼ぶ方法です（`<immintrin.h>`）。

```cpp
#include <immintrin.h>

// 8 個の float を、一度に足す（AVX）。配列は 32 バイト境界が望ましい
void AddArrays(const float* a, const float* b, float* out, int count) {
  int i = 0;
  for (; i + 8 <= count; i += 8) {
    __m256 va = _mm256_loadu_ps(a + i);       // 8 個を読み込む
    __m256 vb = _mm256_loadu_ps(b + i);
    _mm256_storeu_ps(out + i, _mm256_add_ps(va, vb));   // 足して、書き込む
  }
  for (; i < count; ++i) {                     // 余りの要素
    out[i] = a[i] + b[i];
  }
}
```

| 項目 | 注意 |
| --- | --- |
| **CPU が対応しているか確認する** | AVX2 がない CPU で実行すると、クラッシュする。実行時に判定して、切り替える（`__cpuid`） |
| **コードが読みにくい** | 命令名が難しい。ライブラリを優先する |
| **移植性がない** | x86 専用。ARM では別の書き方（NEON） |
| **余りの処理が必要** | 要素数が、幅（8 個）で割り切れないとき |
| **コンパイラのほうが速いこともある** | 自動ベクトル化の結果と、必ず比べる |

## SIMD が効く場面・効かない場面

| 効く | 効かない |
| --- | --- |
| 大量の座標・速度の更新 | 分岐だらけの AI |
| 行列とベクトルの計算（スキニング、変換） | 少数のオブジェクト（準備のコストが勝つ） |
| 画像・音の処理（ピクセル、サンプル） | ポインタをたどる処理（キャッシュミスが支配的） |
| 当たり判定の前処理（距離の計算） | メモリ帯域が限界（データの読み込みが遅い） |
| パーティクル | 1 回しか呼ばれない処理 |

**SIMD は「計算が重い」ときの道具**です。ゲームの遅さの多くは、<strong>メモリ（キャッシュミス）</strong>が原因なので、[メモリとキャッシュ](memory-cache.md) を先に直します。

## ゲームでの使いどころ

| 場面 | 方法 |
| --- | --- |
| パーティクルの更新（数万個） | SoA + 自動ベクトル化。必要なら xsimd |
| スキニング（骨のアニメーション） | 行列計算を、DirectXMath で |
| 当たり判定の距離計算 | 位置を SoA にして、まとめて距離の 2 乗を計算 |
| 数学ライブラリ全般 | DirectXMath / glm（SIMD 有効）を使う |
| 画像処理・音のミキシング | 配列をまとめて処理するループ。自動ベクトル化を確認 |

## よくあるミス

??? failure "メモリの並びを直さずに、SIMD に手を出す"
    AoS のまま SIMD を使うと、データを集める（gather）コストで、速くならないことが多いです。先に SoA にします。

??? failure "AVX2 を前提にして、古い PC で起動しない"
    プレイヤーの CPU が対応しているとは限りません。**実行時に判定して**、使えなければ SSE2 や普通のコードに切り替えます。

??? failure "`XMVECTOR` をメンバ変数にして、クラッシュする"
    16 バイト境界が必要で、`new` したときなどに、ずれてクラッシュします。メンバは `XMFLOAT3` などにします。

??? failure "SIMD にしても、速くならない"
    ボトルネックが、メモリ読み込みや分岐にあります。プロファイラーで、本当に計算が重いかを確かめます。

??? failure "浮動小数点の結果が、少し変わる"
    SIMD で足す順番が変わると、丸め誤差で、結果が少し変わります。決定的な（再現できる）シミュレーションが必要なら、注意します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SIMD ＝ <strong>1 命令で、複数のデータをまとめて計算</strong>（SSE は `float` 4 個、AVX は 8 個）
    - [x] まず<strong>自動ベクトル化</strong>。連続した配列（SoA）を、同じ計算で回すループを書く
    - [x] 手で書くなら<strong>ライブラリ</strong>（DirectXMath、glm、xsimd）。生のイントリンシックは最後
    - [x] CPU の対応を実行時に確認する。メンバに `XMVECTOR` を置かない
    - [x] メモリが原因のことが多い。<strong>計測して</strong>効果を確かめる

## 関連ページ

- [最適化の進め方](index.md)
- [メモリとキャッシュ](memory-cache.md)
- [コンパイラの最適化](compiler.md)
- [ECS](../design/patterns/ecs.md)
- [`<bit>` とビット演算](../stl/numeric/bit.md)
- [DirectXMath（SIMD の数学ライブラリ）](../3d/directxmath.md)
- [SimpleMath](../3d/simplemath.md)
- [CRTP とポリシーベース設計](../design/patterns/crtp-policy.md)
