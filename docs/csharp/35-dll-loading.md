---
title: 第 35 章 DLL の読み込み、x64、デバッグ
tags:
  - C#連携
---

# 第 35 章 DLL の読み込み、x64、デバッグ

C# と C++ をつなぐと、困るのは「動かないとき」です。エラー メッセージは短く、原因はいろいろあります。「DLL が見つかりません」と言われても、実は別の DLL が欠けていただけ、ということがよくあります。この章では、DLL がどう読み込まれるかを知って、原因を順番に切り分ける方法と、C# と C++ の両方にブレークポイントを置いて追う方法をまとめます。

## 例外の名前で、原因の範囲が決まる

`[LibraryImport("EngineApi.dll")]` を付けた関数は、初めて呼んだ瞬間に.NET が DLL を探して読み込みます。探す順番は、アプリのフォルダー（`Editor.exe` と同じ場所）、システムのフォルダー（`System32`）、環境変数 `PATH` のフォルダー、のような順です。見つかって読み込めたら、次は DLL の中から関数の名前を探します。どこかで失敗すると例外になり、その種類で、原因の見当がつきます。

| 例外 | 起きたこと |
| --- | --- |
| `DllNotFoundException` | DLL（またはその DLL が必要とする別の DLL）が見つからない、または読み込めない |
| `BadImageFormatException` | DLL はあったが、形式が合わない。多くはビット数の違い |
| `EntryPointNotFoundException` | DLL は読めたが、その名前の関数がない |
| `AccessViolationException` | 呼び出しは成功したが、不正なメモリを触った。ポインターの間違いや構造体のずれ |
| `SEHException` | ネイティブ側で構造化例外が起きた。C++ の例外が漏れた、など |

## DllNotFoundException

いちばんよく出るエラーです。

```text
System.DllNotFoundException: Unable to load DLL 'EngineApi.dll' or one of its dependencies:
指定されたモジュールが見つかりません。 (0x8007007E)
```

大事なのは「or one of its dependencies」の部分です。`EngineApi.dll` 自体はそこにあっても、それが必要としている `Engine.dll` や `VCRUNTIME140.dll` がないと、同じメッセージになります。

次の順で確かめていきます。

1. `EngineApi.dll` が `Editor.exe` の隣（`bin\x64\Debug\`）にあるか。
2. `Engine.dll` も隣にあるか。
3. 両方とも x64 か。`dumpbin /headers EngineApi.dll` に `machine (x64)` と出ます。
4. C++ のランタイム（`VCRUNTIME140.dll` など）があるか。開発機には入っていますが、配布先では「Visual C++ 再頒布可能パッケージ」が必要です。
5. Debug 版と Release 版が混ざっていないか。
6. 上のどれでもなければ、次の方法で依存先を調べる。

### 依存先を調べる

いちばん手軽なのは `dumpbin` です。

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

`MSVCP140D.dll` や `VCRUNTIME140D.dll` のように、名前の末尾が `D` のものは、デバッグ版のランタイムです。開発機以外には普通入っていないので、Debug 版を配布先に持っていくと、これが原因で失敗します。

GUI で見たいなら、オープンソースの「Dependencies」が使えます（昔の Dependency Walker の後継です）。依存関係が木で見え、見つからない DLL が赤く表示されます。さらに調べたいなら、Sysinternals の Process Monitor で `Editor.exe` のファイル アクセスを記録して、`NAME NOT FOUND` になった `.dll` を探す方法もあります。

よくある原因を症状から並べておきます。

- 自分の PC では動くのに、友人の PC では動かない。Debug 版のランタイムか、再頒布可能パッケージがない。Release 版を配って、再頒布パッケージを入れてもらう。
- `Engine.dll` を作り直したら動かなくなった。`EngineApi.dll` を作り直していない。古い `Engine.lib` にリンクされたままなので、ソリューション全体をリビルドする。
- Visual Studio からは動くのに、`Editor.exe` を直接起動すると動かない。作業ディレクトリが違う。`bin\x64\Debug\` に必要なものがそろっているかを確かめる。
- `d3d12.dll` がない。Windows が古い、または N エディションで Media Feature Pack がない。

## BadImageFormatException

```text
System.BadImageFormatException: 間違ったフォーマットのプログラムを読み込もうとしました。 (0x8007000B)
```

ほとんどの場合、ビット数の不一致です。32 ビットのプロセスが 64 ビットの DLL を読もうとした（またはその逆）ときに出ます。

- `Editor.exe` が 64 ビットで動いているか。タスク マネージャーの「詳細」タブで、プロセス名の横に `(32 ビット)` と出ていないかを見ます。
- C# プロジェクトの `PlatformTarget` とプラットフォームが `x64` か。`Any CPU` で「32 ビットを優先」が入っていると、32 ビットで起動することがあります。
- ネイティブ側の構成マネージャーが `x64` か。

C++/CLI を使っているときは、`net8.0` と `net8.0-windows` のずれでも似たエラーが出ます（第 34 章）。

## EntryPointNotFoundException

```text
System.EntryPointNotFoundException: Unable to find an entry point named 'me_engine_tick' in DLL 'EngineApi.dll'.
```

DLL は読めたけれど、その名前の関数がない、という意味です。次のあたりを疑います。

- C# 側の名前のタイプミス。C のヘッダーと一致しているか。
- `extern "C"` がない。`dumpbin /exports` に、`?` を含む長い名前で出ています。
- `ME_API`（`dllexport`）が付いていない。`dumpbin /exports` に出てきません。
- 古い DLL を読んでいる。ビルドの出力が別のフォルダーに出ていないかを確認します。

## AccessViolationException と SEHException

```text
System.AccessViolationException: 保護されているメモリに読み取りまたは書き込みを行おうとしました。
```

呼び出しそのものは成功したけれど、ポインターや構造体が壊れている、というパターンです。P/Invoke でいちばん難しいエラーです。疑う場所は次のとおりです。

- 構造体のずれ。C と C# でフィールドの型、順番、大きさを見比べます。`sizeof` と `Marshal.SizeOf` を比べるのが手っ取り早いです。
- `bool` や `long` を使っている。`uint8_t` / `int32_t` / `int64_t` に変えます。
- すでに解放したハンドルを使っている。`SafeHandle` で防げます（第 33 章）。
- コールバックが GC に回収された。デリゲートを `static` に持つか、`UnmanagedCallersOnly` に変えます。
- C++ が受け取った `const char*` を保存していた。C# の呼び出しが終わると、無効になります。
- 宣言の引数の数や順番が違う。x64 では、引数が多すぎても動いてしまうことがあるので、気づきにくいです。
- 別のスレッドから、同じネイティブのオブジェクトを同時に触っている。

`SEHException` は、C++ の例外が `catch` されずに漏れたときなどに出ます。第 32 章の `Guard` をすべての関数が通っているかを確かめてください。

## C# から C++ へ、ステップ実行する

C# の `Editor` を動かしながら、`EngineApi` や `Engine` の C++ のコードにもブレークポイントを置いて止めたいことがあります。そのためには、ネイティブ コードのデバッグを有効にします。

1. `Editor` を右クリックして「プロパティ」を開く。
2. 「デバッグ」（または「デバッグ起動プロファイルを開く」）を開く。
3. 「ネイティブ コードのデバッグを有効にする」にチェックを入れる。

これで、`F5` で起動すると、C# と C++ の両方のブレークポイントが効きます。C# の `NativeMethods.me_engine_tick(...)` の行で `F11`（ステップ イン）を押すと、C++ の `me_engine_tick` の中に入れます。コール スタックには、C# と C++ のフレームが混ざって出ます。.NET の内部は `[外部コード]` と省略されます。

オンにすると起動が少し遅くなるので、普段はオフにしておき、必要なときだけオンにするのがおすすめです。

### 例外のところで止める

「デバッグ → ウィンドウ → 例外設定」を開いて、「Common Language Runtime Exceptions」（C# の例外）、「C++ Exceptions」、「Win32 Exceptions」（アクセス違反など）にチェックを入れると、例外が起きた場所で止まります。

### ブレークポイントが白抜きで止まらないとき

「シンボルが読み込まれていません」と出て、ブレークポイントが白抜きになることがあります。`.pdb` が `.dll` と違う場所にある、DLL が古い、最適化されている、ネイティブ デバッグがオフ、のどれかが多いです。出力先をそろえて（第 1 章）、Debug 構成でビルドし直してみてください。

## DLL を探す場所を自分で決める

DLL を `bin\x64\Debug\native\` のようなサブフォルダーに置きたいとき、標準の探索では見つかりません。`NativeLibrary.SetDllImportResolver` で、探し方を自分で書けます。

```csharp
using System.Reflection;
using System.Runtime.InteropServices;

namespace Editor.Engine;

internal static class NativeLoader
{
    // アプリの起動時に 1 回だけ呼ぶ。
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
        return nint.Zero;   // それ以外は、既定の探索に任せる
    }
}
```

`NativeLibrary` は、ネイティブ DLL を手動で読み込む静的クラスです。`nint.Zero` を返すと「自分では解決しない」という意味になり、既定の探索に戻ります。

`EngineApi.dll` が必要とする `Engine.dll` は、OS が `EngineApi.dll` の隣を探します（読み込んだ DLL のフォルダーが対象に含まれるため）。両方を同じフォルダーに置けば問題ありません。別の場所に置きたいなら、起動時に `SetDllDirectory` で探す場所を足します。

```csharp
[LibraryImport("kernel32.dll", EntryPoint = "SetDllDirectoryW", StringMarshalling = StringMarshalling.Utf16)]
[return: MarshalAs(UnmanagedType.Bool)]
private static partial bool SetDllDirectory(string path);
```

`[return: MarshalAs(UnmanagedType.Bool)]` が必要なのは、Windows API の `BOOL` が 4 バイトの整数だからです。

!!! tip "配布するなら、探す場所を限る"
    探索場所にユーザーが書き込めるフォルダーが含まれていると、偽物の DLL を置かれる危険があります。製品として配るときは、`[DefaultDllImportSearchPaths(DllImportSearchPath.AssemblyDirectory)]` で、アプリのフォルダーだけに限定します。

!!! info "このページを読む前に"
    - [第 34 章 C++/CLI で橋を作る](34-cpp-cli.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

## クラッシュしたときの調べ方

C++ 側の想定外の終了は、クラッシュ ダンプ（その瞬間のメモリの記録）を取ると調べられます。いちばん簡単なのは、Visual Studio で再現させて、例外で止まった場所のコール スタックを読む方法です。再現しにくいときは、Windows のエラー報告（WER）でダンプを保存する設定にするか、Sysinternals の `procdump -ma -e -w Editor.exe` で、例外が起きた時点のダンプを保存します。

`.dmp` ファイルを Visual Studio にドラッグして開き、「混合でデバッグ」を押すと、クラッシュした時点のコール スタックと変数を見られます。`.pdb` が必要なので、ビルドごとに保存しておきましょう。

アクセス違反のアドレスにも、ヒントがあります。

| アドレス | 意味 |
| --- | --- |
| `0x0000000000000000` から `0x000000000000FFFF` あたり | `null` ポインターの参照（`null` のオブジェクトのメンバーを触った） |
| `0xFFFFFFFFFFFFFFFF` | 無効なハンドルの参照 |
| `0xDDDDDDDD...`（Debug の MSVC） | 解放済みのメモリ |
| `0xCDCDCDCD...`（Debug の MSVC） | 初期化前のメモリ |
| `0xFEEEFEEE...`（Debug ヒープ） | 解放済みのヒープ |

DirectX 12 のデバッグ レイヤー（第 3 章）が不正な使い方を見つけると、出力ウィンドウに `D3D12 ERROR: ...` と出ます。ネイティブ デバッグがオフだと出ないことがあるので、混在デバッグをオンにして見てください。

## 迷ったときのまとめ

```text
起動しない／呼べない
 │
 ├─ DllNotFoundException ─▶ 隣に DLL があるか → 依存先（dumpbin /dependents）→ ランタイム（D 付きは Debug 版）
 ├─ BadImageFormatException ─▶ ビット数（x64 だけにそろえる）
 ├─ EntryPointNotFoundException ─▶ 名前（dumpbin /exports）、extern "C"、ME_API
 ├─ AccessViolationException ─▶ 構造体のずれ → bool/long → ハンドル → コールバックの保持
 └─ SEHException ─▶ C++ の例外が漏れている → Guard を通っているか
```

??? failure "ネイティブ デバッグをオンにしたら、起動が遅くなった"
    正常です。C++ のシンボルを読み込むためです。普段はオフにして、必要なときだけオンにします。

??? failure "`Editor.exe` を直接起動すると `DllNotFoundException` なのに、Visual Studio からは動く"
    Visual Studio は `PATH` や作業ディレクトリを追加することがあります。`bin\x64\Debug\` に必要なものがそろっているかを確かめます。

??? failure "Release 構成だと、ブレークポイントが効かない"
    最適化されているためです。問題の再現は Debug で行います。Release の調査用には、`/Zi`（デバッグ情報）と `/DEBUG` を Release にも付けて、`.pdb` を作っておきます。

## 第 3 部のまとめ

| 章 | 学んだこと |
| --- | --- |
| 第 31 章 | 連携方式の比較、境界を越える型・文字列・メモリ・例外の決まり |
| 第 32 章 | C の API（不透明なハンドル、エラー コード、`Guard`） |
| 第 33 章 | P/Invoke（`LibraryImport`、構造体、`SafeHandle`、コールバック） |
| 第 34 章 | C++/CLI の橋と、P/Invoke との比較 |
| 第 35 章 | 読み込みの仕組みと、エラーの切り分け、混在デバッグ |

C# から C++ を呼ぶ土台がそろいました。ただ、まだ画面にエンジンの絵は出ていません。次の章からは、WPF の画面の中に DirectX 12 の絵を出す方法を考えます。

[第 36 章 3D ビューポートを埋め込む方法の比較](36-viewport-options.md) へ進みます。
