---
title: Jolt のビルドと設定
tags:
  - 外部ライブラリ
  - 物理演算
---

# Jolt のビルドと設定

Jolt は<strong>ビルドのときの設定（プリプロセッサの定義・CMake のオプション）</strong>によって、**クラスの中身（メンバ）や、機能が変わります**。**ライブラリを作ったときの設定と、自分のプロジェクトで `#include` するときの設定が食い違う**と、**実行時に原因不明のクラッシュ**が起きます。このページは**主な設定の意味**、**Debug / Release の使い分け**、**倍精度・決定性**、**vcpkg と CMake の違い**、**食い違いを防ぐ方法**をまとめます（導入の基本は [Jolt Physics](index.md)）。

!!! tip "ポイント"
    - <strong>Jolt のビルド設定（定義）は、「ライブラリ」と「使う側」で、必ず一致させる</strong>。<strong>ずれると構造体の大きさが違い、メモリが壊れる</strong>。
    - 主な定義：<strong>`JPH_DEBUG_RENDERER`</strong>（デバッグ描画）、<strong>`JPH_PROFILE_ENABLED`</strong>（プロファイル）、<strong>`JPH_DOUBLE_PRECISION`</strong>（倍精度）、<strong>`JPH_ENABLE_ASSERTS`</strong>、<strong>`JPH_CROSS_PLATFORM_DETERMINISTIC`</strong>。
    - <strong>Debug と Release で、別々にビルド</strong>する（<strong>ランタイム `/MD` と `/MDd`</strong> も合わせる）。
    - <strong>CPU の命令セット（SSE4.1・AVX2 など）の設定</strong>も<strong>一致</strong>させる。
    - <strong>vcpkg で入れると、設定が一貫する</strong>。<strong>自分でビルドするなら、CMake のオプションを、メモしておく</strong>。
    - <strong>`JPH_DEBUG_RENDERER` と `JPH_PROFILE_ENABLED` は、製品版では無効</strong>にする。

## なぜ設定を合わせるのか

Jolt は**ヘッダの中にクラスの定義**を持ちます。**一部のクラスは、定義（マクロ）によって、メンバが増えたり減ったりします**。

```text
JPH_DEBUG_RENDERER が有効 → Body などのクラスに、デバッグ用のメンバが追加される
```

**ライブラリ（`Jolt.lib`）をビルドしたときと自分のコード（ヘッダを include）で、定義が違う**と**同じクラスなのにサイズや並びが違う**ことになり、**メモリを読み間違えて、クラッシュ**します。**コンパイルもリンクも通る**ので、**気づきにくい**バグです。

| ずれの例 | 症状 |
| --- | --- |
| **ライブラリは `JPH_DEBUG_RENDERER` あり、自分のプロジェクトはなし** | **構造体のサイズが違い、物体の情報が壊れる** |
| **ライブラリは Release、自分のプロジェクトは Debug** | **ランタイム（CRT）の不一致**（`LNK2038`）、または**実行時のクラッシュ** |
| **倍精度（`JPH_DOUBLE_PRECISION`）の有無が違う** | **位置の型（`RVec3`）が違い、座標が壊れる** |
| **AVX2 の有無が違う** | **`Vec4` などのアライメントの要求が違う** |

## 主な定義（プリプロセッサ）

| 定義 | 意味 | 使うとき |
| --- | --- | --- |
| **`JPH_DEBUG_RENDERER`** | **デバッグ描画**（衝突の形・制約の表示）を、有効にする | **Debug・Profile 構成**。**製品では無効** |
| **`JPH_PROFILE_ENABLED`** | **Jolt 内蔵のプロファイラー**を有効にする | 性能を調べるとき。**製品では無効** |
| **`JPH_ENABLE_ASSERTS`** | **assert を有効**にする | **Debug 構成**（既定で、Debug は有効） |
| **`JPH_DOUBLE_PRECISION`** | <strong>位置を倍精度（`double`）</strong>で持つ | **広大なワールド**（数十 km 以上）で、**遠くの精度**が必要なとき |
| **`JPH_CROSS_PLATFORM_DETERMINISTIC`** | **異なる CPU・OS でも同じ結果**（決定性）にする | **ネットワーク同期（ロックステップ）・リプレイ** |
| `JPH_OBJECT_STREAM` | **オブジェクトのシリアライズ**（`ObjectStream`） | エディタ・ツール |
| `JPH_USE_*`（`JPH_USE_AVX2` など） | **使う CPU 命令セット** | **CMake が自動で設定** |
| `JPH_FLOATING_POINT_EXCEPTIONS_ENABLED` | **浮動小数点の例外**を有効に（バグの検出） | Debug |

!!! warning "定義は、自分のプロジェクトにも、必ず書く"
    **Jolt のヘッダを include する側**（自分のゲームの全部のプロジェクト）で、**同じ定義**を<strong>プロパティの「プリプロセッサの定義」</strong>に、書きます（[プリプロセッサマクロ](../../vs/preprocessor.md)）。**CMake で `target_link_libraries(... Jolt)`** すると、**`PUBLIC` な定義が、自動で伝わります**。

## Debug と Release

| 構成 | 設定 |
| --- | --- |
| **Debug** | **最適化なし**・**assert 有効**・**`JPH_DEBUG_RENDERER`** |
| **Release** | **最適化**・**assert なし**・**デバッグ描画なし** |
| **Distribution**（配布用） | <strong>Release ＋ LTO（リンク時の最適化）</strong>、**すべての診断を無効** |

**Debug の物理は、非常に遅い**（数十倍）ことがあります。**ゲームの動作確認が重いときは**、**物理だけ Release のライブラリを使う**（ただし、**ランタイムの設定は、合わせる**）ことも検討します。

### ランタイム ライブラリ（/MD と /MT）

<strong>Visual Studio の「コード生成 → ランタイム ライブラリ」</strong>を、**ライブラリと自分のプロジェクトで、そろえます**。

| 設定 | 意味 |
| --- | --- |
| **`/MD`**（Release）/ **`/MDd`**（Debug） | **DLL 版のランタイム** |
| **`/MT`** / **`/MTd`** | **静的リンクのランタイム** |

!!! warning "Jolt の CMake の既定は、静的ランタイム"
    <strong>Jolt を、CMake で自分でビルドすると、既定で静的ランタイム（`/MT`）</strong>になる場合があります。**自分のプロジェクトが `/MD` なら、不一致**（`LNK2038`）になります。**CMake のオプションで、DLL 版（`/MD`）にする**（**`USE_STATIC_MSVC_RUNTIME_LIBRARY` を `OFF`**。名前はバージョンで変わるので、`CMakeLists.txt` を確認）。**vcpkg は、`/MD` に合わせてあります**（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)）。

## 倍精度（Double Precision）

<strong>既定は位置も単精度（`float`）</strong>です。**原点から遠く離れる**と**精度が落ちて、物体が震えたり、すり抜けたり**します。

| 距離（原点から） | 単精度の最小の刻み（目安） |
| --- | --- |
| 100 m | 約 8 マイクロメートル |
| 1 km | 約 0.1 ミリメートル |
| 10 km | 約 1 ミリメートル |
| 100 km | 約 8 ミリメートル |

**数 km までなら、単精度で十分**です。**広大なワールド**（宇宙ゲーム・巨大なオープンワールド）では、**`JPH_DOUBLE_PRECISION`**（**位置を `double` で持つ**）を使います。

| 型 | 単精度のとき | 倍精度のとき |
| --- | --- | --- |
| **`Vec3`** | `float` × 3 | **常に `float`**（方向・速度など） |
| **`RVec3`**（位置） | `Vec3` と同じ | **`double` × 3** |
| **`Real`** | `float` | `double` |

**位置を扱う API は、`RVec3` / `Real`** で書いておくと、**どちらの設定でもコンパイルできます**（[Jolt Physics](index.md) のサンプルが `RVec3` を使うのは、この理由）。

!!! note "倍精度は、メモリと速度の代償"
    **位置が `double`** になるので、**メモリと計算が少し増えます**。**必要なときだけ**有効にします。**別の方法**（<strong>ワールドを区画に分けて、原点を動かす（フローティング・オリジン）</strong>）もあります。

## 決定性（Determinism）

**決定性**とは**同じ入力から、いつも同じ結果**になることです。

| 用途 | 説明 |
| --- | --- |
| **リプレイ** | **入力だけを記録**して、**物理の結果を再現** |
| **ロックステップのネットワーク** | **全員が同じ入力で同じ結果**を計算する（**物理の状態は送らない**） |
| **テスト** | **物理のバグを再現**できる |

Jolt は**同じバイナリ・同じ CPU 環境なら、決定的**です。**異なる CPU・コンパイラ・OS をまたぐ**決定性が必要なら、**`JPH_CROSS_PLATFORM_DETERMINISTIC`** を有効にします（**速度が少し落ちます**）。

| 注意 | 説明 |
| --- | --- |
| **更新の順番を固定** | **物体を追加する順・更新の呼び出し順**が同じであること |
| **固定タイムステップ** | **可変の `dt` は、決定性を壊す**（[世界の初期化と更新](system.md)） |
| **浮動小数点の設定** | **`/fp:fast` は避ける**（`/fp:precise`）。Jolt の既定の設定に従う |
| **スレッド数に依存しない** | **Jolt はスレッド数が違っても同じ結果**になるよう設計されている |

## CPU の命令セット

**SIMD の命令セット**（SSE4.1・SSE4.2・AVX・AVX2・AVX512・FMA・F16C）の、**使うものを選べます**。**新しい命令を使うと速く、古い CPU では動きません**。

| 設定（CMake） | 意味 |
| --- | --- |
| `USE_SSE4_1` / `USE_SSE4_2` | **SSE4.1 / 4.2** |
| **`USE_AVX2`** | **AVX2**（多くの現代の PC で使える） |
| `USE_AVX512` | AVX-512（対応 CPU が限られる） |
| `USE_LZCNT` / `USE_TZCNT` / `USE_F16C` / `USE_FMADD` | **個別の命令** |

**配布するゲーム**では、**対象の PC の範囲**を考えて決めます（**Steam のハードウェア調査**で、**AVX2 の普及率**を確認する、など）。**AVX2 を有効にしたら、ライブラリと自分のプロジェクトで、`/arch:AVX2` をそろえます**。

## vcpkg と CMake の違い

| 方法 | 長所 | 短所 |
| --- | --- | --- |
| **vcpkg** | **簡単**。**設定が一貫**する。**Debug / Release が、自動** | **ビルド設定の細かな調整が限られる**（機能の選択） |
| <strong>CMake（自分でビルド）</strong> | **すべての設定を制御**できる | **設定の一致を自分で管理** |
| **ソースをプロジェクトに入れる** | **ビルドがプロジェクトと一緒** | **ビルドが重い**・設定を合わせる |

### vcpkg の機能

```powershell
vcpkg install joltphysics[debug-renderer,profiler]:x64-windows
```

| 機能（feature） | 意味 |
| --- | --- |
| `debug-renderer` | **`JPH_DEBUG_RENDERER`** を有効に |
| `profiler` | **`JPH_PROFILE_ENABLED`** を有効に |

**機能名はポートのバージョンで変わります**。**`vcpkg search joltphysics`** や、**ポートの `portfile`・`vcpkg.json`** で確認します。

### CMake で、自分のプロジェクトに組み込む

```cmake
add_subdirectory(third_party/JoltPhysics/Build)
target_link_libraries(my_game PRIVATE Jolt)
```

**`Jolt` ターゲットを、リンク**すれば、**インクルード・定義**が**自動で伝わります**（`PUBLIC` なので）。**手動で定義を書く必要が、ありません**。

## ビルドが通ったかの確認

**設定の食い違いを実行時に検出**する仕組みが、あります。

```cpp
JPH_ASSERT(sizeof(Body) == ...);
```

| 方法 | 説明 |
| --- | --- |
| **`JPH_ENABLE_ASSERTS`** | **Debug で内部のチェック**が有効（**構造体のずれを早く検出**） |
| **`Factory` の登録時のチェック** | **型の不一致**で**初期化時に失敗**することがある |
| **最小のサンプルを動かす** | <strong>[最小の流れ](index.md)</strong>（球が落ちるだけ）で、**クラッシュしないか**確認 |

**入れ直したとき**、**構成を変えたとき**は、**まず最小のサンプル**で確認します。

## 製品版で無効にするもの

| 定義 | 製品版 |
| --- | --- |
| `JPH_DEBUG_RENDERER` | **無効**（描画コードを含めない） |
| `JPH_PROFILE_ENABLED` | **無効**（計測の負荷を避ける） |
| `JPH_ENABLE_ASSERTS` | **無効** |
| `JPH_DOUBLE_PRECISION` | 必要なら有効（**設計の判断**） |
| `JPH_CROSS_PLATFORM_DETERMINISTIC` | **ネットワーク同期が必要なら有効** |

（[プリプロセッサマクロ](../../vs/preprocessor.md)）

## よくあるミス

??? failure "Jolt のライブラリと、自分のプロジェクトで、`JPH_DEBUG_RENDERER` の有無が違う"
    **実行時にクラッシュ**します。**両方で同じ定義**にします。

??? failure "`LNK2038`（ランタイムの不一致）が出る"
    **`/MD` と `/MT`**（または `/MDd`）が、そろっていません。**ライブラリ側を合わせます**。

??? failure "Debug のライブラリを、Release のプロジェクトでリンクする"
    **構成ごとに別のライブラリ**を使います（`$(Configuration)` でパスを分ける）。

??? failure "位置が遠くで、物体が震える"
    **単精度の限界**です。**倍精度**、または**原点の移動**を検討します。

??? failure "`/fp:fast` で決定性が失われる"
    **`/fp:precise`** にします。

??? failure "AVX2 を有効にしたら、古い PC で起動しない"
    **対象の PC に、AVX2 があるか**確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>Jolt の定義（`JPH_DEBUG_RENDERER` など）は、ライブラリと自分のプロジェクトで、必ず一致</strong>。<strong>ずれると実行時にクラッシュ</strong>
    - [x] <strong>Debug と Release は、別のライブラリ</strong>。<strong>ランタイム（`/MD`・`/MDd`）も、そろえる</strong>
    - [x] <strong>倍精度</strong>は、<strong>広大なワールド</strong>のとき。<strong>位置は `RVec3` / `Real`</strong> で書く
    - [x] <strong>決定性</strong>は、<strong>リプレイ・ロックステップ</strong>に。<strong>固定タイムステップ</strong>が前提
    - [x] <strong>vcpkg は一貫</strong>、<strong>CMake は細かく制御</strong>。<strong>`Jolt` ターゲットをリンクすれば、定義が伝わる</strong>
    - [x] <strong>製品版は、デバッグ描画・プロファイル・assert を無効</strong>

## 関連ページ

- [Jolt Physics](index.md)
- [世界の初期化と更新](system.md)
- [デバッグ描画](debug-renderer.md)
- [プリプロセッサマクロ](../../vs/preprocessor.md)
- [外部ライブラリの入れ方](../../vs/libraries.md)
- [CMake で使う](../../vs/cmake.md)
