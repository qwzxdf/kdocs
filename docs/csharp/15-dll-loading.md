---
title: 第 15 章 DLL の読み込み、x64、デバッグ
tags:
  - C#連携
---

# 第 15 章 DLL の読み込み、x64、デバッグ

この章は、連携が<strong>動かないとき</strong>のための章です。C# と C++ をつなぐと、エラー メッセージは短く、原因は多岐にわたります。「DLL が見つからない」と言われても、実際は、<strong>別の DLL が欠けている</strong>のかもしれません。この章では、DLL が読み込まれる仕組みを知り、原因を順番に切り分ける方法と、C# と C++ の両方にブレークポイントを置く方法を学びます。

## この章の考え方

`[LibraryImport("EngineApi.dll")]` が書かれた関数を、<strong>初めて呼んだ瞬間</strong>に、.NET は次の順で DLL を探し、読み込みます。

1. アプリケーションのフォルダー（`Editor.exe` と同じ場所）。
2. システムのフォルダー（`System32`）。
3. 環境変数 `PATH` のフォルダー、など。

読み込めたら、DLL の中から<strong>関数の名前</strong>を探します。ここまでで失敗すると、例外が出ます。

| 例外 | 意味 |
| --- | --- |
| `DllNotFoundException` | DLL（またはその DLL が必要とする別の DLL）が<strong>見つからない／読み込めない</strong> |
| `BadImageFormatException` | DLL は見つかったが、<strong>形式が合わない</strong>（ビット数が違う、など） |
| `EntryPointNotFoundException` | DLL は読み込めたが、<strong>その名前の関数が無い</strong> |
| `AccessViolationException` | 呼び出しは成功したが、<strong>不正なメモリアクセス</strong>（ポインターの間違い、構造体のずれ） |
| `SEHException` | ネイティブ側で、<strong>構造化例外</strong>が起きた（C++ の例外が漏れた、など） |

どの例外かで、原因の範囲が大きく変わります。

## この章のゴール

- 例外の種類から、原因を絞り込める。
- DLL の依存関係を調べられる。
- C# から C++ へ、ブレークポイントでステップ実行できる。
- 実行時に DLL を探す場所を、自分で制御できる。

## 手順 1：DllNotFoundException の切り分け

最も多いエラーです。メッセージは、次のようなものです。

```text
System.DllNotFoundException: Unable to load DLL 'EngineApi.dll' or one of its dependencies:
指定されたモジュールが見つかりません。 (0x8007007E)
```

<strong>「or one of its dependencies」が大事</strong>です。`EngineApi.dll` 自体はあっても、それが必要とする `Engine.dll` や `VCRUNTIME140.dll` が無いと、同じメッセージになります。

### チェックリスト

上から順に確認します。

| 順 | 確認すること | 方法 |
| --- | --- | --- |
| 1 | `EngineApi.dll` は `Editor.exe` の隣にあるか | `bin\x64\Debug\` をエクスプローラーで開く |
| 2 | `Engine.dll` も隣にあるか | 同上 |
| 3 | ビット数は両方 x64 か | `dumpbin /headers EngineApi.dll` で `machine (x64)` を確認 |
| 4 | C++ のランタイム（VCRUNTIME140 など）はあるか | 開発機なら入っている。配布先では、<strong>Visual C++ 再頒布可能パッケージ</strong>が必要 |
| 5 | Debug 版と Release 版が混ざっていないか | Debug の `Editor.exe` に Release の DLL、など |
| 6 | DLL の依存先を調べる | 次の方法 |

### 依存先を調べる

<strong>方法 1：dumpbin</strong>

```bash
dumpbin /dependents bin\x64\Debug\EngineApi.dll
```

```text
Image has the following dependencies:

    Engine.dll
    d3d12.dll
    dxgi.dll
    KERNEL32.dll
    MSVCP140D.dll
    VCRUNTIME140D.dll
    ...
```

`MSVCP140D.dll` や `VCRUNTIME140D.dll` のように、末尾が `D` のものは、<strong>デバッグ版のランタイム</strong>です。開発機以外には、通常入っていません。Debug 版を配布先に持っていくと、これが原因で失敗します。

<strong>方法 2：Dependencies（ツール）</strong>

昔の Dependency Walker の後継の、オープンソースのツール「Dependencies」で、GUI で依存関係の木を表示できます。見つからない DLL が赤で示されます。

<strong>方法 3：Process Monitor</strong>

Microsoft の Sysinternals の「Process Monitor」で、`Editor.exe` のファイル アクセスを記録し、`NAME NOT FOUND` になった `.dll` の名前を探します。

### ありがちな原因

| 症状 | 原因 |
| --- | --- |
| 自分の PC では動くが、友人の PC で動かない | Debug 版のランタイム、または再頒布可能パッケージが無い。Release 版を使い、再頒布パッケージを入れる |
| `Engine.dll` を作り直したら動かなくなった | `EngineApi.dll` を作り直していない（古い `Engine.lib` でリンクされている）。ソリューション全体をリビルドする |
| Visual Studio から動くが、`Editor.exe` を直接起動すると動かない | 作業ディレクトリが違う。DLL 探索がアプリのフォルダーなら問題ないが、ネイティブ側が相対パスで何かを読むときに壊れる |
| `d3d12.dll` が無い | Windows のバージョンが古い（Windows 10 の初期など）。または、Windows が N エディションで、Media Feature Pack が無い |

## 手順 2：BadImageFormatException

```text
System.BadImageFormatException: 間違ったフォーマットのプログラムを読み込もうとしました。 (0x8007000B)
```

ほとんどが、<strong>ビット数の不一致</strong>です。32 ビットのプロセスが 64 ビットの DLL を読み込もうとした（またはその逆）。

| 確認 | 方法 |
| --- | --- |
| `Editor.exe` は 64 ビットで動いているか | タスク マネージャーの「詳細」タブで、プロセス名の横に `(32 ビット)` と出ていないか |
| C# プロジェクトの設定 | `PlatformTarget` が `x64`、プラットフォームが `x64`（`Any CPU` + 「32 ビットを優先」が既定でオンの古い設定に注意） |
| ネイティブ側 | 構成マネージャーで `x64` になっているか。`dumpbin /headers` で確認 |
| 混在の検出 | `dumpbin /headers Editor.dll` は、マネージドでは使えない。`corflags` や `ILSpy` で確認する |

C++/CLI を使うときは、<strong>`net8.0` と `net8.0-windows` のずれ</strong>でも、似たエラーが出ることがあります（第 14 章）。

## 手順 3：EntryPointNotFoundException

```text
System.EntryPointNotFoundException: Unable to find an entry point named 'me_engine_tick' in DLL 'EngineApi.dll'.
```

DLL は読めたが、その名前が無い。

| 原因 | 確認 |
| --- | --- |
| C# 側の名前のタイプミス | `me_engine_tick` が、C のヘッダーと一致しているか |
| `extern "C"` が無い | `dumpbin /exports` に、長い（`?` を含む）名前で出ている |
| `ME_API`（`dllexport`）が付いていない | `dumpbin /exports` に出ていない |
| 古い DLL を読んでいる | `EngineApi.dll` を、ビルドし直す。ビルドの出力が、別フォルダーに出ていないか |
| 名前の装飾 | 32 ビットの `__stdcall` では `_name@8` のように装飾されるが、x64 では装飾されない |

## 手順 4：AccessViolationException と SEHException

```text
System.AccessViolationException: 保護されているメモリに読み取りまたは書き込みを行おうとしました。
```

呼び出しは成功したが、<strong>ポインターや構造体が壊れている</strong>。P/Invoke の最も難しい種類のエラーです。

| 原因 | 確認 |
| --- | --- |
| 構造体のずれ | C と C# で、フィールドの型・順番・大きさを見比べる。`sizeof` と `Marshal.SizeOf` を比べる |
| `bool` を使っている | `uint8_t` や `int32_t` に変える |
| `long` を使っている | C++ の Windows の `long` は 32 ビット。`int64_t` と C# の `long` を使う |
| ハンドルを解放済み | `SafeHandle` を使う（第 13 章）。C++ 側の `destroy` の後に使っていないか |
| コールバックが回収された | デリゲートを `static` に保持していない。`UnmanagedCallersOnly` に変える |
| 文字列を保持された | C++ が `const char*` を保存した。C# の呼び出しの終了後は、無効になる |
| 引数の個数・順番 | 宣言の引数が足りない、または多い。x64 では、<strong>多くても動いてしまう</strong>ことがある |
| スレッドの違い | 別のスレッドから、ネイティブのオブジェクトを同時に触っている |

`SEHException` は、ネイティブ側で、<strong>C++ の例外が `catch` されずに漏れた</strong>ときなどに出ます。第 12 章の `Guard` で、すべての関数が例外を止めているか確認します。

## 手順 5：混在デバッグ（C# から C++ へステップ実行）

C# の `Editor` を実行しながら、`EngineApi` や `Engine` の C++ コードに<strong>ブレークポイント</strong>を置き、止めたい。これには、<strong>ネイティブ コードのデバッグを有効にする</strong>必要があります。

1. `Editor` プロジェクトを右クリック →「プロパティ」。
2. 「デバッグ」→「デバッグ起動プロファイルを開く」（または「デバッグ」タブ）。
3. <strong>「ネイティブ コードのデバッグを有効にする」</strong>にチェックを入れる。

これで、`F5` で起動すると、C# と C++ の両方のブレークポイントが効きます。C# の `NativeMethods.me_engine_tick(…)` の行で `F11`（ステップ イン）すると、C++ の `me_engine_tick` の中へ入ります。

| 新しく出てきたもの | 説明 |
| --- | --- |
| 混在モード デバッグ | マネージド（C#）とネイティブ（C++）のコードを、1 つのデバッガーで同時にデバッグする |
| ネイティブ コードのデバッグを有効にする | プロパティ。オンにすると、起動が少し遅くなるが、C++ のブレークポイントが効き、C++ の例外も捕まえられる |
| コール スタック | C# と C++ のフレームが、混ざって表示される。外部コード（.NET の内部）は、`[外部コード]` と省略される |
| ステップ イン（`F11`） | 関数の中に入る。P/Invoke の呼び出しの行でも、C++ の中へ入れる |

### 例外で止める

「デバッグ → ウィンドウ → 例外設定」を開き、次の項目にチェックを入れると、例外が出た<strong>その場所</strong>で止まります。

| 項目 | 内容 |
| --- | --- |
| Common Language Runtime Exceptions | C# の例外 |
| C++ Exceptions | C++ の例外 |
| Win32 Exceptions | Win32 の例外（アクセス違反など） |

### シンボルとソースのずれ

ブレークポイントが、「現在、このブレークポイントはヒットしません。シンボルが読み込まれていません」と、白抜きになることがあります。

| 原因 | 対処 |
| --- | --- |
| `.pdb` が `.dll` と違う場所にある | 出力先をそろえる（第 1 章） |
| DLL が古い | ビルドし直す |
| 最適化されている | Debug 構成で試す |
| ネイティブ デバッグがオフ | 上の手順 3 |

## 手順 6：DLL の探す場所を制御する

標準の探索が合わない場合（DLL を `bin\x64\Debug\native\` のように、サブフォルダーに置きたいなど）は、<strong>自分で場所を指定</strong>できます。

### NativeLibrary.SetDllImportResolver

```csharp
using System.Reflection;
using System.Runtime.InteropServices;

namespace Editor.Interop;

internal static class NativeLoader
{
    // アプリの起動時（App のコンストラクターなど）に、1 回だけ呼ぶ。
    public static void Install()
    {
        NativeLibrary.SetDllImportResolver(typeof(NativeMethods).Assembly, Resolve);
    }

    private static nint Resolve(string libraryName, Assembly assembly, DllImportSearchPath? searchPath)
    {
        if (libraryName == "EngineApi.dll")
        {
            string path = Path.Combine(AppContext.BaseDirectory, "native", "EngineApi.dll");
            return NativeLibrary.Load(path);
        }
        return nint.Zero;   // それ以外は、既定の探索
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `NativeLibrary` | ネイティブ DLL を、<strong>手動で</strong>読み込む静的クラス。`Load`、`TryLoad`、`GetExport`、`Free` を持つ |
| `SetDllImportResolver` | P/Invoke が DLL を探すときに呼ばれる関数を登録する。登録は、アセンブリごとに 1 回だけ |
| `AppContext.BaseDirectory` | アプリの実行ファイルがあるフォルダー |
| `Path.Combine` | パスをつなぐ。`\` の重複を気にしなくてよい |
| `nint.Zero` を返す | 「自分では解決しない」の意味。既定の探索に任せる |

### 依存先の DLL も同じ場所に置く場合

`EngineApi.dll` が `Engine.dll` を必要とするとき、`native\` に両方を置いても、OS は<strong>`EngineApi.dll` の隣</strong>を探します（`LoadLibrary` の既定で、読み込んだ DLL のフォルダーは含まれる）。通常は、問題ありません。

別の場所にある場合は、起動時に追加します。

```csharp
[LibraryImport("kernel32.dll", EntryPoint = "SetDllDirectoryW", StringMarshalling = StringMarshalling.Utf16)]
[return: MarshalAs(UnmanagedType.Bool)]
private static partial bool SetDllDirectory(string path);
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `SetDllDirectory` | DLL を探す場所に、フォルダーを足す Windows API |
| `[return: MarshalAs(UnmanagedType.Bool)]` | 戻り値の `BOOL`（32 ビット整数）を、`bool` に変換する指定。<strong>Windows API の `BOOL` は 4 バイト</strong>なので、この指定が要る |
| `[DefaultDllImportSearchPaths]` | DLL の探す範囲を、属性で限定する。セキュリティの面で、`AssemblyDirectory` に限るのが推奨 |

!!! tip "DLL 乗っ取り対策"
    DLL の探索場所に、ユーザーが書き込めるフォルダーが入っていると、<strong>偽物の DLL を置かれる</strong>危険があります。配布する製品では、`[DefaultDllImportSearchPaths(DllImportSearchPath.AssemblyDirectory)]` で、アプリのフォルダーに限定します。

## 手順 7：クラッシュの調べ方

### ログとダンプ

C++ 側の想定外の終了を調べるには、<strong>クラッシュ ダンプ</strong>（その瞬間のメモリの記録）を取ります。

| 方法 | 内容 |
| --- | --- |
| Visual Studio で再現 | デバッグ実行して、例外で止まった場所のコール スタックを読む。最も簡単 |
| Windows のエラー報告（WER）でダンプを保存 | レジストリの `HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps` を設定する |
| `procdump` | Sysinternals のツール。`procdump -ma -e -w Editor.exe` で、例外時にダンプを保存 |

ダンプ ファイル（`.dmp`）を Visual Studio にドラッグして開き、「ネイティブ のみでデバッグ」や「混合でデバッグ」を押すと、クラッシュした時点のコール スタックと変数が見られます。`.pdb` が必要なので、<strong>ビルドごとに、`.pdb` を保存</strong>しておきます。

### アクセス違反のアドレスを読む

| アドレス | 意味 |
| --- | --- |
| `0x0000000000000000`～`0x000000000000FFFF` | null ポインター（またはその近く）の参照。`null` のオブジェクトの、メンバーへアクセスした |
| `0xFFFFFFFFFFFFFFFF` | 無効なハンドルの参照 |
| `0xDDDDDDDD...` | （Debug の MSVC）解放済みのメモリ |
| `0xCDCDCDCD...` | （Debug の MSVC）初期化前のメモリ |
| `0xFEEEFEEE...` | （Debug ヒープ）解放済みのヒープ |

## 手順 8：DirectX のデバッグ レイヤーのメッセージを見る

第 3 章で、Debug ビルドでは DX12 のデバッグ レイヤーを有効にしました。D3D12 が不正な使い方を検出すると、Visual Studio の<strong>出力ウィンドウ</strong>に、`D3D12 ERROR: …` と出ます。ネイティブ デバッグがオフだと、出力に出ない場合があります。<strong>混在デバッグを有効にした状態で</strong>、出力ウィンドウを見ます。

## 診断のフローチャート

```text
起動しない／呼べない
 │
 ├─ DllNotFoundException ─▶ 隣に DLL があるか → 依存先（dumpbin /dependents）→ ランタイム（D 付きは Debug 版）
 ├─ BadImageFormatException ─▶ ビット数（x64 だけにそろえる）
 ├─ EntryPointNotFoundException ─▶ 名前（dumpbin /exports）、extern "C"、ME_API
 ├─ AccessViolationException ─▶ 構造体のずれ → bool/long → ハンドル → コールバックの保持
 └─ SEHException ─▶ C++ の例外が漏れている → Guard を通っているか
```

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| `dumpbin /dependents` | `Engine.dll` が依存先に出る |
| 混在デバッグ | `NativeMethods.me_engine_tick` の行から `F11` で、C++ の `me_engine_tick` に入れる |
| `SetDllImportResolver` | （任意）`native\` に DLL を移しても起動できる |

## よくあるミス

??? failure "ネイティブ デバッグを有効にしたら、起動が遅くなった"
    正常です。Debug の C++ のシンボルを読み込むため。普段は、必要なときだけオンにする。

??? failure "`Editor.exe` を直接起動すると、`DllNotFoundException`、Visual Studio では動く"
    Visual Studio は、`PATH` や作業ディレクトリを、追加することがある。`bin\x64\Debug\` に、必要なものがすべてそろっているか確認する。

??? failure "Release 構成にすると、ネイティブ側だけ最適化されて、デバッグできない"
    Release ではブレークポイントが効きにくい。問題の再現は、Debug で行う。Release 版の調査用には、`/Zi`（デバッグ情報）と `/DEBUG` を Release にも付けて、`.pdb` を作っておく。

## 第 3 部のまとめ

| 章 | 学んだこと |
| --- | --- |
| 第 11 章 | 連携方式の比較、境界を越える型・文字列・メモリ・例外の決まり |
| 第 12 章 | C の API（不透明なハンドル、エラー コード、`Guard`） |
| 第 13 章 | P/Invoke（`LibraryImport`、構造体、`SafeHandle`、コールバック） |
| 第 14 章 | C++/CLI の橋と、P/Invoke との比較 |
| 第 15 章 | 読み込みの仕組みと、エラーの切り分け、混在デバッグ |

C# から C++ を呼ぶ<strong>土台</strong>が、そろいました。しかし、まだ<strong>画面にエンジンの絵が出ていません</strong>。

## 次の章へ

次の章（[第 16 章 3D ビューポートを埋め込む方法の比較](16-viewport-options.md)）から第 4 部です。WPF の画面の中に、DirectX 12 の絵を出す方法を比べ、この教材で使う方式を決めます。
