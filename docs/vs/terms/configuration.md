---
title: 構成（Configuration）
tags:
  - Visual Studio
---

# 構成（Configuration）

構成は <strong>ビルドの設定一式に付けた名前</strong>です。Visual Studio には最初から Debug（開発用）と Release（製品用）の 2 つがあります。名前が違うだけで実体は「コンパイラとリンカーの設定のセット」が 2 つあるだけです。同じソースからまったく違う性格の実行ファイルが作られます。

!!! tip "ポイント"
    - Debug は「バグを見つけやすい」、Release は「速い」。目的が正反対の設定になっている
    - 違いの中心は <strong>最適化（`/Od` と `/O2`）、ランタイム ライブラリ（`/MDd` と `/MD`）、マクロ（`_DEBUG` と `NDEBUG`）</strong>
    - 速さを測るのは必ず Release。Debug は何倍も遅いので、比べられない
    - 「Debug では動くのに、Release でおかしい」は <strong>初期化していない変数や未定義動作</strong>の疑いが強い
    - 構成は自分で増やせる（例：最適化はするがデバッグ情報は残す `Profile`）

## このページを読む前に

- [プロジェクト（.vcxproj）](project.md)
- [プラットフォーム](platform.md)

## 構成とプラットフォーム {#pair}

画面の上のドロップダウンには「Debug」と「x64」が並んでいます。この 2 つの<strong>組み合わせ</strong>が、1 つのビルド設定を決めます。

![標準ツールバー。左のドロップダウンが構成（Debug）、右がプラットフォーム（x64）。その右の緑の三角がデバッグ開始のボタン](../img/toolbar-config.jpg)

| | x64 | Win32 |
| --- | --- | --- |
| Debug | `Debug|x64` | `Debug|Win32` |
| Release | `Release|x64` | `Release|Win32` |

プロパティ画面の左上にある「構成」「プラットフォーム」は、どの組み合わせにいま変更を書き込むかの選択です。「すべての構成」を選ぶと Debug と Release の両方に書き込まれます（[C++23 を使えるようにする設定](../settings.md#open)）。

`.vcxproj` にはこの組み合わせを使って、次のように書かれています。

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

新しいプロジェクトが持つ既定の設定を比べます。

| 項目 | Debug | Release | 意味 |
| --- | --- | --- | --- |
| 最適化 | `/Od`（無効） | `/O2`（速度を優先） | `/Od` は、書いたとおりに実行する。`/O2` は順番の入れ替えや変数の消去をする |
| インライン展開 | しない | する | 関数呼び出しを本体で置き換える |
| ランタイム ライブラリ | `/MDd` | `/MD` | `d` はデバッグ版の CRT（C ランタイム） |
| マクロ | `_DEBUG` | `NDEBUG` | `assert` の有効／無効がこれで決まる |
| デバッグ情報 | `/ZI`（編集して続行が使える） | `/Zi`（または無し） | 変数名や行番号と、実行ファイルを結びつける情報 |
| 基本ランタイム チェック | `/RTC1` | なし | スタックの破壊や初期化していないローカル変数を検出 |
| リンク時コード生成 | なし | `/GL` と `/LTCG` | ファイルをまたいだ最適化 |
| 増分リンク | `/INCREMENTAL` | `/INCREMENTAL:NO` | 変更部分だけをリンクし直す |
| 未参照の関数の削除 | なし | `/OPT:REF`、`/OPT:ICF` | 使われない関数と同じ中身の関数をまとめる |
| イテレーターのデバッグ | 有効（`_ITERATOR_DEBUG_LEVEL=2`） | 無効（`0`） | 範囲外のイテレーターを実行時にエラーにする |

### 最適化（/Od と /O2）

`/Od` では書いたコードが 1 行ずつそのまま機械語になります。ブレークポイントで止めて変数の値を見られるのは、この性質のおかげです。

`/O2` ではコンパイラが見た目と違うコードを作ります。

- 使われない変数や計算を消す
- 小さい関数を呼び出し元に埋め込む（インライン展開）
- ループを展開する SIMD 命令に変える
- 処理の順序を入れ替える

そのため、Release のデバッグでは「変数が `<最適化されました>` と表示される」「ブレークポイントが違う行で止まる」「ステップ実行の順番が飛ぶ」ことがあります。バグを調べるときは Debug に戻すか最適化を一部だけ弱めます。

### ランタイム ライブラリ（/MDd と /MD） {#runtime}

プログラムは `std::string` や `malloc` を**ランタイム ライブラリ**から呼んでいます。

| オプション | 意味 |
| --- | --- |
| `/MD` | リリース版を DLL で使う。実行時に `vcruntime140.dll` などが必要 |
| `/MDd` | デバッグ版を DLL で使う |
| `/MT` | リリース版を実行ファイルに埋め込む（静的リンク）。DLL が要らない |
| `/MTd` | デバッグ版を静的リンクする |

リンクするすべての `.lib` で、この設定をそろえる必要があります。Debug の本体に Release 用に作られたライブラリを混ぜると、`LNK2038`（`RuntimeLibrary` の不一致）が出ます。外部ライブラリを vcpkg で入れると、構成に合うものが自動で選ばれます（[外部ライブラリの入れ方](../libraries.md)）。

### デバッグ ヒープのパターン

Debug の CRT はメモリに目印の値を書き込みます。バグ探しの手がかりになります。

| 値 | 意味 |
| --- | --- |
| `0xCDCDCDCD` | 確保したばかりで、まだ何も書いていないヒープ |
| `0xDDDDDDDD` | 解放したあとのヒープ |
| `0xFDFDFDFD` | 確保した範囲の前後にある、ガード（番兵）。上書きされると解放のときに検出される |
| `0xCCCCCCCC` | 初期化していないローカル変数（スタック。`/RTC1` が有効なとき） |

変数の値が `0xCCCCCCCC` や `0xCDCDCDCD` になっていたら、初期化し忘れです。`0xDDDDDDDD` なら 解放済みのメモリを使っています。

!!! note "Release は、これらを書かない"
    Release ではメモリの中身は、そこに以前あったままです。初期化していない変数は「たまたま 0 だった」「たまたま前の値だった」と毎回、違う値になり得ます。Debug で動いて Release で壊れる、一番多い理由です。

## Release でだけ壊れる、よくある原因 {#release-only}

| 原因 | 症状 | 調べ方 |
| --- | --- | --- |
| 初期化していない変数 | 値が毎回違う。まれにしか起きない | `/W4` の警告（C4701、C4700）を見る。Debug の `0xCCCCCCCC` を確認 |
| 未定義動作（範囲外アクセス、符号付き整数のオーバーフロー） | 最適化で、コードが消える・変わる | [AddressSanitizer](../asan.md)、`-fsanitize=undefined` |
| `assert` の中に副作用がある | Release では `assert` ごと消えて、処理が飛ぶ | `assert(Init())` のような書き方をやめる |
| 浮動小数点の計算順序 | 結果がごく僅かに違う | `/fp:precise`（既定）か `/fp:strict` で試す |
| 最適化によるコードの並べ替え | スレッドの同期がおかしくなる | `std::atomic` と `std::mutex` を正しく使う |
| タイミング | Debug だと遅いので、レースが起きない | スレッド サニタイザーやログで追う |

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

<strong>Release の `NDEBUG` が定義されていると、`assert` は何もしなくなります。</strong>`assert` の中の式は実行されません。

## 自分の構成を作る {#custom}

ゲーム開発では「Debug は遅すぎて、Release はデバッグしにくい」という悩みが出ます。そこで、第 3 の構成を作ります。

| 構成の名前 | 目的 | 設定の特徴 |
| --- | --- | --- |
| Debug | バグ探し | 最適化なし。すべてのチェックが有効 |
| Profile（または RelWithDebInfo） | 速度の計測 | 最適化あり（`/O2`）。デバッグ情報は付ける（`/Zi`、`/DEBUG`）。アサートは無効 |
| Release | 製品の確認 | 最適化あり。デバッグ情報は別ファイルに出す |
| Shipping | 配布 | 製品用。ログとデバッグ機能をマクロで外す |

### 作り方

1. ビルド → **構成マネージャー**を開く（[画面](solution.md#config-manager)）
2. 「アクティブ ソリューション構成」→ 新規作成
3. 名前を `Profile` にして「設定のコピー元」を `Release` にする
4. 「新しいプロジェクト構成を作成する」にチェックを付ける
5. プロジェクトのプロパティで、`Profile` を選んで設定を変える

`Profile` では Release と同じ最適化のまま `/Zi`（デバッグ情報を作る）とリンカーの `/DEBUG` を付けます。パフォーマンスの測定は実際の製品に近い設定で行わないと意味がありません（[パフォーマンス プロファイラー](../profiler.md)）。

### 構成ごとにマクロで挙動を変える

プリプロセッサ定義に構成ごとのマクロを入れておくとコードの中で分けられます。

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

プリプロセッサ定義の入れ方は[プリプロセッサマクロ](../preprocessor.md)で説明しています。

## 構成をコマンドラインで選ぶ {#cli}

ビルド サーバー（CI）やコマンド ラインでは、構成を名前で指定します。

```bash
msbuild MyGame.sln /p:Configuration=Release /p:Platform=x64 /m
```

| 引数 | 意味 |
| --- | --- |
| `/p:Configuration=Release` | 構成を `Release` にする |
| `/p:Platform=x64` | プラットフォームを `x64` にする |
| `/m` | プロジェクトを並列にビルドする |

CMake を使うときは Debug と Release は「構成の種類（`CMAKE_BUILD_TYPE`）」で決めます。Visual Studio のジェネレーターでは、ビルドするときに `--config Release` で選びます（[CMake で使う](../cmake.md)）。

## よくあるミス

??? failure "Debug だけにオプションを入れて、Release で効かない"
    プロパティを開いたとき構成が「アクティブ（Debug）」のままだったのが原因です。構成を「すべての構成」にしてから変えます。

??? failure "速さを測ったら遅い。Debug で測っていた"
    Debug は最適化がなく、チェックが多いので数倍から数十倍遅くなります。速さの測定、ゲームのフレームレートの確認は Release（または Profile）で行います。

??? failure "Debug ビルドで、標準コンテナの動きが極端に遅い"
    `_ITERATOR_DEBUG_LEVEL=2` が有効でイテレーターの検査が走っています。大量のデータを扱うテストは Release で行います。`_ITERATOR_DEBUG_LEVEL` を 0 にする設定はリンクするすべてのライブラリで、そろえないといけません（ずれると、ABI の不一致で実行時に壊れます）。

??? failure "Release にしたら、`LNK2038`（RuntimeLibrary の不一致）が出た"
    Debug 用に作られたライブラリを Release にリンクしています。または、その逆です。ライブラリを対応する構成でビルドし直します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 構成はビルド設定のセット。Debug は検査が多く Release は速い
    - [x] 違いの中心は最適化、ランタイム ライブラリ、`_DEBUG` / `NDEBUG`
    - [x] すべてのライブラリで、構成をそろえる
    - [x] 測るのは、Release。バグを追うのは Debug
    - [x] Release でだけ壊れたら、初期化していない変数と未定義動作を疑う
    - [x] 速度を測りたいならデバッグ情報つきの `Profile` 構成を作る

## 関連ページ

- [プラットフォーム](platform.md)
- [プロジェクト（.vcxproj）](project.md)
- [ビルド](build.md)
- [C++23 を使えるようにする設定](../settings.md)
- [AddressSanitizer](../asan.md)
- [プリプロセッサマクロ](../preprocessor.md)
- [Visual Studio の目次](../index.md)
