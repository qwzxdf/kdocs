---
title: DirectXMath
tags:
  - 3Dゲーム
  - 数学ライブラリ
---

# DirectXMath

<div class="page-badges" markdown>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++11〜</span>
`#include <DirectXMath.h>`
</div>

**DirectXMath**（ダイレクト エックス マス）は、Microsoft が提供する、3D の数学ライブラリです。ベクトル、行列、クォータニオン、平面、色などを、SIMD（1 命令で複数のデータを計算する CPU の機能、[SIMD](../optimize/simd.md)）で高速に計算します。Visual Studio（Windows SDK）に含まれているので導入は不要です。ヘッダだけで使えて、DirectX の描画と相性がよく、ゲーム エンジンの数学の土台としても、よく使われます。ただし、型が 2 種類あり（保存用と計算用）、書き方が少し独特で慣れが必要です。そこで、DirectXMath をラップして、普通の C++ らしく書けるようにしたのが、[SimpleMath](simplemath.md) です。このカテゴリのサンプルは、SimpleMath を使います。このページは、DirectXMath 自体の仕組みを、説明します。

!!! tip "ポイント"
    - <strong>計算用の型 `XMVECTOR` / `XMMATRIX`</strong>（SIMD レジスタ）と、<strong>保存用の型 `XMFLOAT3` / `XMFLOAT4X4`</strong>（普通の `float` の並び）を、使い分ける。
    - メンバ変数・配列・ファイルには保存用。計算するときだけ、`XMLoad...` でロードし、`XMStore...` で書き戻す。
    - `XMVECTOR` を、クラスのメンバにしない（16 バイト境界の問題でクラッシュする）。
    - 左手系と右手系の関数が、両方ある（`XMMatrixLookAtLH` / `XMMatrixLookAtRH` など）。このサイトは `LH`（左手系）に統一。
    - 行ベクトル規約（`v * M`）。行列の掛け順は、左から右へ（先に適用する変換が左）。
    - 普段のコードは、SimpleMath で書く。性能が必要な所だけ、DirectXMath を直接。

!!! info "このページを読む前に"
    - [ゲーム数学](index.md)（このセクション全体の地図と、読む順番）
    - [座標系](coordinate-systems.md)（このサイトの座標系の約束）

## 型

### 計算用の型（SIMD）

| 型 | 中身 | 説明 |
| --- | --- | --- |
| **`XMVECTOR`** | 4 つの `float`（128 ビット） | ベクトル 1 つ（`x, y, z, w`）。SIMD レジスタに載る。3 次元でも、4 要素ぶんを使う |
| `XMMATRIX` | 4 つの `XMVECTOR`（4×4 の行列） | 行列 1 つ |

- 関数の引数やローカル変数として使う型です。クラスのメンバや、`std::vector` の要素にはしません（16 バイト境界が必要で、`new` や `vector` が、保証できないため）。

### 保存用の型（普通の float）

| 型 | 中身 | 説明 |
| --- | --- | --- |
| `XMFLOAT2` / `XMFLOAT3` / `XMFLOAT4` | `x, y, (z, (w))` の `float` | 2、3、4 次元の値。メンバ、配列、ファイルに |
| `XMFLOAT4X4` | `float[4][4]` | 4×4 の行列をメモリに保存する |
| `XMFLOAT3A` / `XMFLOAT4A` / `XMFLOAT4X4A` | 上と同じ、16 バイト境界に置く版 | アラインメントを保証できるとき、`Load` を速くする |
| `XMINT3` / `XMUINT3` など | 整数のベクトル | |
| `XMHALF2`、`XMUBYTE4` など | 圧縮した型 | 頂点データの圧縮 |

## ロードとストア

**保存用 ⇄ 計算用**の変換が、ロード（`XMLoad`）とストア（`XMStore`）です。

```cpp
#include <DirectXMath.h>
using namespace DirectX;

struct Particle {
  XMFLOAT3 position;     // 保存用：メンバには、これ
  XMFLOAT3 velocity;
};

void Update(Particle& p, float dt) {
  XMVECTOR pos = XMLoadFloat3(&p.position);        // 保存用 → 計算用
  XMVECTOR vel = XMLoadFloat3(&p.velocity);

  pos = XMVectorMultiplyAdd(vel, XMVectorReplicate(dt), pos);   // pos += vel * dt

  XMStoreFloat3(&p.position, pos);                  // 計算用 → 保存用
}
```

| 関数 | 意味 |
| --- | --- |
| `XMLoadFloat3(const XMFLOAT3*)` | `XMFLOAT3` を `XMVECTOR` にする（w は 0） |
| `XMStoreFloat3(XMFLOAT3*, XMVECTOR)` | `XMVECTOR` の x, y, z を、`XMFLOAT3` に書く |
| `XMLoadFloat4` / `XMStoreFloat4` | 4 次元 |
| `XMLoadFloat4x4` / `XMStoreFloat4x4` | 行列 |
| `XMVectorSet(x, y, z, w)` | 値から `XMVECTOR` を作る |
| `XMVectorReplicate(f)` | 4 つとも同じ値にする |
| `XMVectorGetX(v)` / `XMVectorGetY(v)` | 成分を `float` で取り出す |
| `XMVectorSetX(v, f)` | 成分を置き換える |

ロードとストアの回数を、少なくします。ロード → 計算を連続 → ストア、と並べると速く、行き来が多いと遅くなります。

## よく使う関数 {#functions}

名前の規則: `XMVector3...`（3 次元ベクトル）、`XMVector4...`、`XMMatrix...`、`XMQuaternion...`、`XMPlane...`。

### ベクトル {#dx-vector}

| 関数 | 意味 |
| --- | --- |
| `XMVectorAdd(a, b)` / `XMVectorSubtract(a, b)` | 足し算 / 引き算 |
| `XMVectorScale(v, s)` | スカラー倍 |
| `XMVectorMultiply(a, b)` | 要素ごとの掛け算 |
| `XMVectorMultiplyAdd(a, b, c)` | `a * b + c`（1 命令。FMA） |
| **`XMVector3Length(v)`** / `XMVector3LengthSq(v)` | 長さ / 長さの 2 乗（結果は全成分に入った `XMVECTOR`） |
| `XMVector3Normalize(v)` | 正規化 |
| `XMVector3Dot(a, b)` | 内積（結果は全成分に入る） |
| `XMVector3Cross(a, b)` | 外積 |
| `XMVector3Reflect(v, n)` | 反射 |
| `XMVectorLerp(a, b, t)` | 線形補間 |
| `XMVector3Transform(v, M)` | 位置を行列で変換する（w = 1 として） |
| `XMVector3TransformNormal(v, M)` | 方向を行列で変換する（平行移動なし、w = 0） |
| `XMVector3TransformCoord(v, M)` | 位置を変換して、w で割る（射影のとき） |
| `XMVector3Equal(a, b)` / `XMVector3NearEqual(a, b, eps)` | 等しい / ほぼ等しい |

### 行列 {#dx-matrix}

| 関数 | 意味 |
| --- | --- |
| `XMMatrixIdentity()` | 単位行列 |
| `XMMatrixTranslation(x, y, z)` | 平行移動 |
| `XMMatrixScaling(x, y, z)` | 拡大 |
| `XMMatrixRotationX/Y/Z(angle)` | 軸まわりの回転（ラジアン） |
| `XMMatrixRotationRollPitchYaw(pitch, yaw, roll)` | オイラー角による回転（引数の順に注意） |
| `XMMatrixRotationQuaternion(q)` | クォータニオンから |
| `XMMatrixMultiply(A, B)` | A × B（先に A、次に B を適用） |
| `XMMatrixInverse(&det, M)` | 逆行列（第 1 引数は、行列式を受け取るポインタ。`nullptr` でよい） |
| `XMMatrixTranspose(M)` | 転置 |
| `XMMatrixLookAtLH(eye, at, up)` / `...RH(...)` | ビュー行列（左手系 / 右手系） |
| `XMMatrixPerspectiveFovLH(fovY, aspect, near, far)` / `...RH(...)` | プロジェクション行列 |
| `XMMatrixOrthographicLH(w, h, near, far)` / `...RH` | 正射影 |
| `XMMatrixDecompose(&s, &r, &t, M)` | 行列を拡大・回転・平行移動に分解 |

### クォータニオン {#dx-quaternion}

| 関数 | 意味 |
| --- | --- |
| `XMQuaternionIdentity()` | 回転なし |
| `XMQuaternionRotationAxis(axis, angle)` | 軸と角度から |
| `XMQuaternionRotationRollPitchYaw(pitch, yaw, roll)` | オイラー角から |
| `XMQuaternionMultiply(q1, q2)` | 回転の合成 |
| `XMQuaternionSlerp(q1, q2, t)` | 球面線形補間 |
| `XMQuaternionNormalize(q)` | 正規化 |
| `XMQuaternionInverse(q)` / `XMQuaternionConjugate(q)` | 逆回転 / 共役 |

## 左手系と右手系

DirectXMath は、**左手系（`LH`）と右手系（`RH`）の両方の関数を持っています**。名前の末尾で選びます。

| 作るもの | 左手系 | 右手系 |
| --- | --- | --- |
| ビュー行列 | `XMMatrixLookAtLH` | `XMMatrixLookAtRH` |
| 透視投影 | `XMMatrixPerspectiveFovLH` | `XMMatrixPerspectiveFovRH` |
| 正射影 | `XMMatrixOrthographicLH` | `XMMatrixOrthographicRH` |

どちらも使えるので自分で決めて、全部をそろえます。混ぜると画面が反転するなどします（[座標系](coordinate-systems.md)）。Direct3D 自体は、手系を決めていません。決めるのはライブラリの関数とモデルの向きです。このサイトは左手系・Y-up・+Z が前に統一し、`...LH` の関数を使います（[SimpleMath](simplemath.md) の `Create…` は右手系なので、ビュー・射影はここの `LH` 関数に置き換えます）。

## 行ベクトル規約

DirectXMath は、**行ベクトル**の規約です。ベクトルを行列の左から掛けます（`v' = v * M`）。

```cpp
// ワールド行列：拡大 → 回転 → 平行移動 の順に、左から掛ける
XMMATRIX world = XMMatrixScaling(2, 2, 2) * XMMatrixRotationY(angle) * XMMatrixTranslation(x, y, z);

// 頂点の変換：頂点 × ワールド × ビュー × プロジェクション（左から順に）
XMVECTOR clip = XMVector4Transform(local, world * view * proj);
```

| 項目 | 行ベクトル（DirectXMath） | 列ベクトル（glm、OpenGL の数式） |
| --- | --- | --- |
| 変換の式 | `v' = v * M` | `v' = M * v` |
| 合成の順番 | 左から右（`S * R * T`） | 右から左（`T * R * S`） |
| 平行移動の位置 | 行列の4 行目 | 行列の4 列目 |

詳しくは [行列](matrices.md) を見てください。

## アラインメントと、メンバにできない理由

`XMVECTOR` は、**16 バイト境界**（アドレスが 16 の倍数）に置く必要があります。

| 場面 | 問題 |
| --- | --- |
| スタックのローカル変数・引数 | コンパイラが境界に置いてくれる（問題なし） |
| クラスのメンバにして、`new` でヒープに作る | `new` が、16 バイト境界を保証しない（C++17 前、32 ビット）。クラッシュする |
| `std::vector<XMVECTOR>` | 同上 |
| `static` / グローバル | コンパイラが配置（問題なし） |

保存用の型（`XMFLOAT3`）をメンバにするのが安全で一番簡単です。16 バイト境界が保証できるなら、`XMFLOAT3A` のように `A` が付く型を使うと、ロードが少し速くなります。

## 関数の渡し方（呼び出し規約）

`XMVECTOR` は、レジスタで渡すと速いので、**引数の書き方に決まり**があります。

```cpp
// 引数は、FXMVECTOR / GXMVECTOR / HXMVECTOR / CXMVECTOR という別名で受ける
XMVECTOR XM_CALLCONV Reflect(FXMVECTOR v, FXMVECTOR normal) {
  return XMVector3Reflect(v, normal);
}
```

| 別名 | 使う位置 |
| --- | --- |
| `FXMVECTOR` | 1〜3 番目の引数 |
| `GXMVECTOR` | 4 番目 |
| `HXMVECTOR` | 5、6 番目 |
| `CXMVECTOR` | 7 番目以降（スタック渡し） |
| `FXMMATRIX` / `CXMMATRIX` | 行列（1 番目は `FXMMATRIX`、以降は `CXMMATRIX`） |
| `XM_CALLCONV` | 呼び出し規約（`__vectorcall`）。関数の戻り値の型の後に付ける |

普通は気にしなくてよい（SimpleMath を使えば、隠れます）。自分で DirectXMath の関数を書くときに、必要になります。

## 速さの特徴

| 項目 | 特徴 |
| --- | --- |
| **SIMD で計算** | 1 つのベクトル演算が、1〜数命令。`float` 3 つを、1 回で |
| ロード・ストアのコスト | メモリとレジスタの行き来。ループの中で計算を連続させると速い |
| インライン化される | ほとんどの関数が、`inline`。最適化（`/O2`）で、効果が出る |
| `/arch:AVX2` | AVX 命令を使う（対応 CPU のみ）。`_XM_NO_INTRINSICS_` を定義すると、SIMD を使わない版 |
| `XMVector3Length` の結果 | 全成分に入った `XMVECTOR`。`float` が欲しいときは、`XMVectorGetX` で取り出す |

`/fp:fast` を付けるとさらに速くなることがあります（結果が少し変わります、[コンパイラの最適化](../optimize/compiler.md)）。

## DirectXMath と SimpleMath の使い分け

| 状況 | 選ぶもの |
| --- | --- |
| **普通のゲームのコード**（更新、カメラ、ゲームの仕組み） | SimpleMath（[SimpleMath](simplemath.md)）。書きやすい |
| 毎フレーム何万回も計算する（パーティクル、スキニング、当たり判定の前処理） | DirectXMath（`XMVECTOR`）を直接。ロード・ストアを最小に |
| DirectXMath の関数が必要（SimpleMath にない） | SimpleMath の型は、`XMVECTOR` / `XMMATRIX` に、自動で変換できる |

## よくあるミス

??? failure "`XMVECTOR` を、クラスのメンバにして、クラッシュする"
    16 バイト境界が保証されません。メンバは `XMFLOAT3`（保存用）にします。

??? failure "ロードとストアを、何度も行き来して、遅くなる"
    ロードして、計算を続けて、最後に 1 回ストアします。途中でストアして、またロードするのは、無駄です。

??? failure "左手系と右手系の関数を混ぜる"
    `XMMatrixLookAtLH` と `XMMatrixPerspectiveFovRH` を混ぜると、画面が反転したり、何も映らなくなります。LH か RH に統一します。

??? failure "行列の掛け順を、列ベクトルの感覚で書く"
    DirectXMath は行ベクトルなので、**`S * R * T`**（拡大 → 回転 → 平行移動）です。`T * R * S` と書くと、順序が逆になります。

??? failure "`XMVector3Length` の結果を、`float` として使う"
    結果は `XMVECTOR` です。`float` にするには、`XMVectorGetX(...)` で取り出します。

??? failure "`XMMatrixRotationRollPitchYaw` の引数の順番を間違える"
    引数は `(pitch, yaw, roll)` の順です（X 軸、Y 軸、Z 軸）。名前の「Roll Pitch Yaw」の順ではありません。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 計算用 `XMVECTOR` / `XMMATRIX`と、保存用 `XMFLOAT3` / `XMFLOAT4X4` を使い分ける
    - [x] メンバには保存用。計算はロード → 計算 → ストア
    - [x] 行ベクトル規約（`v * M`、掛け順は左から右）。`LH` / `RH` を統一
    - [x] 普段は SimpleMath。速さが必要な所だけ DirectXMath を直接
    - [x] Visual Studio に標準で入っている。ヘッダだけで使える

## 関連ページ

- [3D ゲーム（目次）](../3d/index.md)
- [SimpleMath](simplemath.md)
- [行列](matrices.md)
- [SIMD（ベクトル化）](../optimize/simd.md)
- [DirectXMath（Microsoft Learn）](https://learn.microsoft.com/ja-jp/windows/win32/dxmath/directxmath-portal)
