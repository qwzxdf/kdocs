---
title: 構成（Configuration）
tags:
  - Visual Studio
---

# 構成（Configuration）

構成は、<strong>ビルドの設定一式に付けた名前</strong>です。Visual Studio には、最初から **Debug**（開発用）と **Release**（製品用）の 2 つがあります。名前が違うだけで、実体は「コンパイラとリンカーの設定のセット」が 2 つあるだけです。同じソースから、まったく違う性格の実行ファイルが作られます。

!!! tip "ポイント"
    - Debug は「バグを見つけやすい」、Release は「速い」。目的が正反対の設定になっている
    - 違いの中心は、<strong>最適化（`/Od` と `/O2`）、ランタイム ライブラリ（`/MDd` と `/MD`）、マクロ（`_DEBUG` と `NDEBUG`）</strong>
    - 速さを測るのは、必ず Release。Debug は、何倍も遅いので、比べられない
    - 「Debug では動くのに、Release でおかしい」は、<strong>初期化していない変数や未定義動作</strong>の疑いが強い
    - 構成は、自分で増やせる（例：最適化はするがデバッグ情報は残す `Profile`）

## このページを読む前に

- [プロジェクト（.vcxproj）](project.md)
- [プラットフォーム](platform.md)

## 構成とプラットフォーム {#pair}

画面の上のドロップダウンには、「Debug」と「x64」が並んでいます。この 2 つの<strong>組み合わせ</strong>が、1 つのビルド設定を決めます。

| | x64 | Win32 |
| --- | --- | --- |
| Debug | `Debug|x64` | `Debug|Win32` |
| Release | `Release|x64` | `Release|Win32` |

プロパティ画面の左上にある「構成」「プラットフォーム」は、<strong>どの組み合わせに、いま変更を書き込むか</strong>の選択です。「すべての構成」を選ぶと、Debug と Release の両方に書き込まれます（[C++23 を使えるようにする設定](../settings.md#open)）。

`.vcxproj` には、この組み合わせを使って、次のように書かれています。

```xml
<ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
  <ClCompile>
    <Optimization>Disabled</Optimization>
  </ClCompile>
</ItemDefinitionGroup>
<ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'">
  <ClCompile>
    <Optimization>MaxSpeed</Optimization>
  </ClCompile>
</ItemDefinitionGroup>
```

## Debug と Release の違い {#diff}

新しいプロジェクトが持つ、既定の設定を比べます。

| 項目 | Debug | Release | 意味 |
| --- | --- | --- | --- |
| 最適化 | `/Od`（無効） | `/O2`（速度を優先） | `/Od` は、書いたとおりに実行する。`/O2` は、順番の入れ替えや、変数の消去をする |
| インライン展開 | しない | する | 関数呼び出しを、本体で置き換える |
| ランタイム ライブラリ | `/MDd` | `/MD` | `d` はデバッグ版の CRT（C ランタイム） |
| マクロ | `_DEBUG` | `NDEBUG` | `assert` の有効／無効が、これで決まる |
| デバッグ情報 | `/ZI`（編集して続行が使える） | `/Zi`（または無し） | 変数名や行番号と、実行ファイルを結びつける情報 |
| 基本ランタイム チェック | `/RTC1` | なし | スタックの破壊や、初期化していないローカル変数を検出 |
| リンク時コード生成 | なし | `/GL` と `/LTCG` | ファイルをまたいだ最適化 |
| 増分リンク | `/INCREMENTAL` | `/INCREMENTAL:NO` | 変更部分だけをリンクし直す |
| 未参照の関数の削除 | なし | `/OPT:REF`、`/OPT:ICF` | 使われない関数と、同じ中身の関数をまとめる |
| イテレーターのデバッグ | 有効（`_ITERATOR_DEBUG_LEVEL=2`） | 無効（`0`） | 範囲外のイテレーターを、実行時にエラーにする |

### 最適化（/Od と /O2）

`/Od` では、書いたコードが、1 行ずつそのまま機械語になります。ブレークポイントで止めて、変数の値を見られるのは、この性質のおかげです。

`/O2` では、コンパイラが、見た目と違うコードを作ります。

- 使われない変数や計算を、消す
- 小さい関数を、呼び出し元に埋め込む（インライン展開）
- ループを展開する、SIMD 命令に変える
- 処理の順序を、入れ替える

そのため、Release のデバッグでは、「変数が `<最適化されました>` と表示される」「ブレークポイントが、違う行で止まる」「ステップ実行の順番が飛ぶ」ことがあります。バグを調べるときは、Debug に戻すか、最適化を一部だけ弱めます。

### ランタイム ライブラリ（/MDd と /MD） {#runtime}

プログラムは、`std::string` や `malloc` を、**ランタイム ライブラリ**から呼んでいます。

| オプション | 意味 |
| --- | --- |
| `/MD` | リリース版を、DLL で使う。実行時に、`vcruntime140.dll` などが必要 |
| `/MDd` | デバッグ版を、DLL で使う |
| `/MT` | リリース版を、実行ファイルに埋め込む（静的リンク）。DLL が要らない |
| `/MTd` | デバッグ版を、静的リンクする |

<strong>リンクするすべての `.lib` で、この設定をそろえる</strong>必要があります。Debug の本体に、Release 用に作られたライブラリを混ぜると、`LNK2038`（`RuntimeLibrary` の不一致）が出ます。外部ライブラリを vcpkg で入れると、構成に合うものが、自動で選ばれます（[外部ライブラリの入れ方](../libraries.md)）。

### デバッグ ヒープのパターン

Debug の CRT は、メモリに目印の値を書き込みます。バグ探しの手がかりになります。

| 値 | 意味 |
| --- | --- |
| `0xCDCDCDCD` | 確保したばかりで、まだ何も書いていないヒープ |
| `0xDDDDDDDD` | 解放したあとのヒープ |
| `0xFDFDFDFD` | 確保した範囲の前後にある、ガード（番兵）。上書きされると、解放のときに検出される |
| `0xCCCCCCCC` | 初期化していないローカル変数（スタック。`/RTC1` が有効なとき） |

変数の値が `0xCCCCCCCC` や `0xCDCDCDCD` になっていたら、<strong>初期化し忘れ</strong>です。`0xDDDDDDDD` なら、<strong>解放済みのメモリを使っています</strong>。

!!! note "Release は、これらを書かない"
    Release では、メモリの中身は、そこに以前あったままです。初期化していない変数は、「たまたま 0 だった」「たまたま前の値だった」と、毎回、違う値になり得ます。Debug で動いて、Release で壊れる、一番多い理由です。

## Release でだけ壊れる、よくある原因 {#release-only}

| 原因 | 症状 | 調べ方 |
| --- | --- | --- |
| 初期化していない変数 | 値が毎回違う。まれにしか起きない | `/W4` の警告（C4701、C4700）を見る。Debug の `0xCCCCCCCC` を確認 |
| 未定義動作（範囲外アクセス、符号付き整数のオーバーフロー） | 最適化で、コードが消える・変わる | [AddressSanitizer](../asan.md)、`-fsanitize=undefined` |
| `assert` の中に副作用がある | Release では `assert` ごと消えて、処理が飛ぶ | `assert(Init())` のような書き方を、やめる |
| 浮動小数点の計算順序 | 結果が、ごく僅かに違う | `/fp:precise`（既定）か `/fp:strict` で試す |
| 最適化による、コードの並べ替え | スレッドの同期がおかしくなる | `std::atomic` と `std::mutex` を、正しく使う |
| タイミング | Debug だと遅いので、レースが起きない | スレッド サニタイザーや、ログで追う |

```cpp
#include <cassert>

bool Init();

void Boot() {
  // 悪い例: Release では assert ごと消えるので、Init() が呼ばれない。
  assert(Init());

  // 良い例: 副作用のある処理は、assert の外へ出す。
  const bool ok = Init();
  assert(ok);
}
```

<strong>Release の `NDEBUG` が定義されていると、`assert` は何もしなくなります。</strong>`assert` の中の式は、実行されません。

## 自分の構成を作る {#custom}

ゲーム開発では、「Debug は遅すぎて、Release はデバッグしにくい」という悩みが出ます。そこで、第 3 の構成を作ります。

| 構成の名前 | 目的 | 設定の特徴 |
| --- | --- | --- |
| Debug | バグ探し | 最適化なし。すべてのチェックが有効 |
| Profile（または RelWithDebInfo） | 速度の計測 | 最適化あり（`/O2`）。デバッグ情報は付ける（`/Zi`、`/DEBUG`）。アサートは無効 |
| Release | 製品の確認 | 最適化あり。デバッグ情報は別ファイルに出す |
| Shipping | 配布 | 製品用。ログとデバッグ機能を、マクロで外す |

### 作り方

1. ビルド → **構成マネージャー**を開く
2. 「アクティブ ソリューション構成」→ **新規作成**
3. 名前を `Profile` にして、「設定のコピー元」を `Release` にする
4. 「新しいプロジェクト構成を作成する」にチェックを付ける
5. プロジェクトのプロパティで、`Profile` を選んで、設定を変える

`Profile` では、Release と同じ最適化のまま、`/Zi`（デバッグ情報を作る）と、リンカーの `/DEBUG` を付けます。パフォーマンスの測定は、**実際の製品に近い設定で行わないと、意味がありません**（[パフォーマンス プロファイラー](../profiler.md)）。

### 構成ごとに、マクロで挙動を変える

プリプロセッサ定義に、構成ごとのマクロを入れておくと、コードの中で分けられます。

| 構成 | プリプロセッサ定義の例 |
| --- | --- |
| Debug | `_DEBUG;GAME_DEBUG;GAME_ENABLE_LOG` |
| Profile | `NDEBUG;GAME_PROFILE;GAME_ENABLE_LOG` |
| Shipping | `NDEBUG;GAME_SHIPPING` |

```cpp
#if defined(GAME_DEBUG)
  DrawDebugOverlay();   // デバッグ用の表示
#endif

#if defined(GAME_ENABLE_LOG)
  Log("loaded: {}", path);
#endif
```

プリプロセッサ定義の入れ方は、[プリプロセッサマクロ](../preprocessor.md)で説明しています。

## 構成を、コマンドラインで選ぶ {#cli}

ビルド サーバー（CI）や、コマンド ラインでは、構成を名前で指定します。

```bash
msbuild MyGame.sln /p:Configuration=Release /p:Platform=x64 /m
```

| 引数 | 意味 |
| --- | --- |
| `/p:Configuration=Release` | 構成を `Release` にする |
| `/p:Platform=x64` | プラットフォームを `x64` にする |
| `/m` | プロジェクトを並列にビルドする |

CMake を使うときは、Debug と Release は「構成の種類（`CMAKE_BUILD_TYPE`）」で決めます。Visual Studio のジェネレーターでは、ビルドするときに `--config Release` で選びます（[CMake で使う](../cmake.md)）。

## よくあるミス

??? failure "Debug だけにオプションを入れて、Release で効かない"
    プロパティを開いたとき、構成が「アクティブ（Debug）」のままだったのが原因です。構成を「すべての構成」にしてから変えます。

??? failure "速さを測ったら遅い。Debug で測っていた"
    Debug は、最適化がなく、チェックが多いので、数倍から数十倍遅くなります。速さの測定、ゲームのフレームレートの確認は、Release（または Profile）で行います。

??? failure "Debug ビルドで、標準コンテナの動きが極端に遅い"
    `_ITERATOR_DEBUG_LEVEL=2` が有効で、イテレーターの検査が走っています。大量のデータを扱うテストは、Release で行います。`_ITERATOR_DEBUG_LEVEL` を 0 にする設定は、リンクするすべてのライブラリで、そろえないといけません（ずれると、ABI の不一致で、実行時に壊れます）。

??? failure "Release にしたら、`LNK2038`（RuntimeLibrary の不一致）が出た"
    Debug 用に作られたライブラリを、Release にリンクしています。または、その逆です。ライブラリを、対応する構成で、ビルドし直します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 構成は、ビルド設定のセット。Debug は検査が多く、Release は速い
    - [x] 違いの中心は、最適化、ランタイム ライブラリ、`_DEBUG` / `NDEBUG`
    - [x] すべてのライブラリで、構成をそろえる
    - [x] 測るのは、Release。バグを追うのは、Debug
    - [x] Release でだけ壊れたら、初期化していない変数と、未定義動作を疑う
    - [x] 速度を測りたいなら、デバッグ情報つきの `Profile` 構成を作る

## 関連ページ

- [プラットフォーム](platform.md)
- [プロジェクト（.vcxproj）](project.md)
- [ビルド](build.md)
- [C++23 を使えるようにする設定](../settings.md)
- [AddressSanitizer](../asan.md)
- [プリプロセッサマクロ](../preprocessor.md)
- [Visual Studio の目次](../index.md)
