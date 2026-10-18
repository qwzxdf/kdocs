---
title: Shaders and Compilation
tags:
  - DirectX
---

# Shaders and Compilation

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>シェーダー</strong>は、GPU の上で動く、小さなプログラムです。DirectX では、<strong>HLSL</strong>（High-Level Shading Language）という、C に似た言語で、書き、<strong>バイトコード</strong>に、コンパイルして、GPU に、渡します。頂点シェーダー（VS）は、頂点ごと、ピクセル シェーダー（PS）は、ピクセルごと、計算シェーダー（CS）は、自由な、並列計算を、行います。

!!! tip "ポイント"
    - HLSL を、<strong>コンパイル</strong>して、バイトコード（`ID3DBlob`）を、得る。それから、`CreateVertexShader` などで、シェーダー オブジェクトを、作る。
    - コンパイルの、タイミングは、2 通り。<strong>ビルド時</strong>（`fxc`、Visual Studio の HLSL コンパイラー。`.cso` を、読む）と、<strong>実行時</strong>（`D3DCompileFromFile`）。
    - 入口の関数の名前（`VSMain` など）と、ターゲット（`vs_5_0`）を、指定する。
    - コンパイルの、エラーは、`errors` の ブロブに、文字列で、入る。必ず、表示する。
    - バイトコードは、<strong>入力レイアウトの作成</strong>にも、使う（[Input Layout](input-layout.md)）。

## 最小の HLSL

```hlsl
// triangle.hlsl: 位置と色を、受け取り、そのまま、通す。
struct VSInput {
  float3 position : POSITION;      // 頂点バッファから来る（input-layout.md）
  float4 color : COLOR;
};

struct VSOutput {
  float4 position : SV_Position;   // クリップ空間の位置（システム値）。ラスタライザーが使う
  float4 color : COLOR;            // ピクセル シェーダーへ、補間されて渡る
};

VSOutput VSMain(VSInput input) {
  VSOutput output;
  output.position = float4(input.position, 1.0);
  output.color = input.color;
  return output;
}

float4 PSMain(VSOutput input) : SV_Target {
  return input.color;              // SV_Target: レンダー ターゲットへ書く色
}
```

`: POSITION` や `: SV_Position` は、<strong>セマンティクス</strong>（意味づけ）です。`SV_` で、始まる、システム値は、パイプラインが、特別な、意味で、扱います（`SV_Position` は、クリップ空間の、位置、`SV_Target` は、出力先の色）。それ以外の、名前（`POSITION`、`COLOR`、`TEXCOORD0`）は、VS の入力と、VS から PS への、受け渡しを、つなぐ、目印です。

## 実行時に、コンパイルする

```cpp
#include <d3dcompiler.h>
#pragma comment(lib, "d3dcompiler.lib")

Microsoft::WRL::ComPtr<ID3DBlob> CompileShader(const wchar_t* path, const char* entry, const char* target) {
  UINT flags = D3DCOMPILE_ENABLE_STRICTNESS;
#if defined(_DEBUG)
  flags |= D3DCOMPILE_DEBUG | D3DCOMPILE_SKIP_OPTIMIZATION;   // デバッガーで、ソースを、辿れる
#endif
  Microsoft::WRL::ComPtr<ID3DBlob> bytecode;
  Microsoft::WRL::ComPtr<ID3DBlob> errors;
  HRESULT hr = D3DCompileFromFile(path, nullptr, D3D_COMPILE_STANDARD_FILE_INCLUDE, entry, target, flags, 0,
                                  &bytecode, &errors);
  if (FAILED(hr)) {
    if (errors) OutputDebugStringA(static_cast<const char*>(errors->GetBufferPointer()));   // エラー文を出力
    return nullptr;
  }
  return bytecode;
}
```

| 引数 | 内容 |
| --- | --- |
| `pFileName` | HLSL ファイルの、パス |
| `pDefines` | `#define` の、配列（`nullptr` で、無し） |
| `pInclude` | `#include` の、解決。`D3D_COMPILE_STANDARD_FILE_INCLUDE` で、ファイルから、読む |
| `pEntrypoint` | 入口の関数名（`"VSMain"`） |
| `pTarget` | ターゲット（`"vs_5_0"`、`"ps_5_0"`、`"cs_5_0"`） |
| `Flags1` | `D3DCOMPILE_*`（下の表） |
| `ppCode` | 出力: バイトコード |
| `ppErrorMsgs` | 出力: エラー・警告の、文字列 |

| フラグ | 内容 |
| --- | --- |
| `D3DCOMPILE_ENABLE_STRICTNESS` | 古い構文を、禁止する（常に、付ける） |
| `D3DCOMPILE_DEBUG` | デバッグ情報を、埋める（グラフィックス デバッガーで、ソースを、見られる） |
| `D3DCOMPILE_SKIP_OPTIMIZATION` | 最適化を、しない（デバッグ時） |
| `D3DCOMPILE_OPTIMIZATION_LEVEL3` | 最大の最適化（既定） |
| `D3DCOMPILE_WARNINGS_ARE_ERRORS` | 警告を、エラー扱い |

エラーの、文字列（`errors`）は、`ID3DBlob` に、入ります。<strong>`FAILED` の時、必ず、表示</strong>します。表示しないと、「シェーダーが、作れない」としか、分からず、原因が、探せません。

## シェーダー オブジェクトを作る

```cpp
auto vs_bytecode = CompileShader(L"triangle.hlsl", "VSMain", "vs_5_0");
auto ps_bytecode = CompileShader(L"triangle.hlsl", "PSMain", "ps_5_0");

Microsoft::WRL::ComPtr<ID3D11VertexShader> vertex_shader;
device->CreateVertexShader(vs_bytecode->GetBufferPointer(), vs_bytecode->GetBufferSize(), nullptr, &vertex_shader);

Microsoft::WRL::ComPtr<ID3D11PixelShader> pixel_shader;
device->CreatePixelShader(ps_bytecode->GetBufferPointer(), ps_bytecode->GetBufferSize(), nullptr, &pixel_shader);
```

| 作る関数 | シェーダーの種類 | ターゲット |
| --- | --- | --- |
| `CreateVertexShader` | 頂点 | `vs_5_0` |
| `CreatePixelShader` | ピクセル | `ps_5_0` |
| `CreateComputeShader` | 計算 | `cs_5_0` |
| `CreateGeometryShader` | ジオメトリ | `gs_5_0` |
| `CreateHullShader`、`CreateDomainShader` | ハル、ドメイン（テッセレーション） | `hs_5_0`、`ds_5_0` |

描くとき、`VSSetShader`、`PSSetShader` で、パイプラインに、つなぎます（[Drawing a Triangle](triangle.md)）。

## ビルド時に、コンパイルする

実行時の、コンパイルは、起動が遅く、リリースで、HLSL を、同梱する、必要が、あります。<strong>ビルド時に、コンパイルして、`.cso`（コンパイル済み）を、読み込む</strong>のが、製品の、標準です。

### Visual Studio

HLSL ファイルを、プロジェクトに、追加し、ファイルの、プロパティで、次を、設定します。

| 設定 | 値 |
| --- | --- |
| 項目の種類 | HLSL コンパイラ |
| シェーダーの種類 | 頂点シェーダー（`/vs`）、ピクセル シェーダー（`/ps`）、計算シェーダー（`/cs`） |
| シェーダー モデル | 5.0（`/5_0`） |
| エントリ ポイント名 | `VSMain` など |
| オブジェクト ファイル名 | `$(OutDir)%(Filename).cso` |

1 つの HLSL ファイルに、複数のシェーダーが、ある場合は、シェーダーごとに、別の、HLSL ファイル（または、別の、設定）に、します。

```cpp
// .cso を読み込む。
std::vector<char> ReadFile(const wchar_t* path) {
  std::ifstream file(path, std::ios::binary | std::ios::ate);
  std::vector<char> data(static_cast<size_t>(file.tellg()));
  file.seekg(0);
  file.read(data.data(), data.size());
  return data;
}

auto vs_data = ReadFile(L"triangle_vs.cso");
device->CreateVertexShader(vs_data.data(), vs_data.size(), nullptr, &vertex_shader);
```

### fxc（コマンド ライン）

```text
fxc /T vs_5_0 /E VSMain /Fo triangle_vs.cso triangle.hlsl
fxc /T ps_5_0 /E PSMain /Fo triangle_ps.cso triangle.hlsl
```

| オプション | 内容 |
| --- | --- |
| `/T` | ターゲット（`vs_5_0`） |
| `/E` | 入口の関数名 |
| `/Fo` | 出力ファイル |
| `/Zi` | デバッグ情報 |
| `/Od` | 最適化を、しない |
| `/O3` | 最大の、最適化 |

`fxc` は、シェーダー モデル 5.1 までです。SM 6.0 以上は、`dxc`（DirectX Shader Compiler）が、必要で、D3D12 向けです（[Shaders and DXC](../dx12/shaders-dxc.md)）。

## 開発中の、ホット リロード

実行時の、コンパイルを、使うと、シェーダーを、書き換えて、ゲームを、再起動せずに、反映できます。

```cpp
// ファイルの更新時刻が、変わったら、再コンパイルして、シェーダーを、差し替える。
auto time = std::filesystem::last_write_time(L"triangle.hlsl");
if (time != last_write_time_) {
  last_write_time_ = time;
  auto bytecode = CompileShader(L"triangle.hlsl", "PSMain", "ps_5_0");
  if (bytecode) {                                          // 失敗したら、古いシェーダーを、使い続ける
    device->CreatePixelShader(bytecode->GetBufferPointer(), bytecode->GetBufferSize(), nullptr, &pixel_shader);
  }
}
```

コンパイルが、失敗したときは、<strong>古いシェーダーを、残す</strong>ようにします。そうしないと、タイプミスの、たびに、画面が、真っ黒になります。

## リフレクション（シェーダーの、情報を、読む）

バイトコードから、「どんな、入力・定数バッファ・テクスチャが、あるか」を、読み取れます（`D3DReflect`）。入力レイアウトの、自動生成などに、使えます。

```cpp
Microsoft::WRL::ComPtr<ID3D11ShaderReflection> reflection;
D3DReflect(vs_bytecode->GetBufferPointer(), vs_bytecode->GetBufferSize(), IID_PPV_ARGS(&reflection));
D3D11_SHADER_DESC desc;
reflection->GetDesc(&desc);                                // 入力の数、定数バッファの数など
```

## よくあるミス

??? failure "`D3DCompileFromFile` が、失敗するが、理由が、分からない"
    `errors` の、内容を、表示していない。`OutputDebugStringA` で、出力ウィンドウに、出す。ファイルの、パスが、実行ファイルの、作業ディレクトリから、見えるかも、確認する。

??? failure "実行ファイルを、別の場所に、置くと、シェーダーが、見つからない"
    パスが、相対で、作業ディレクトリに、依存している。`.cso` を、実行ファイルの、隣に、置き、`GetModuleFileName` で、パスを、組み立てる。

??? failure "ピクセル シェーダーの、入力が、頂点シェーダーの、出力と、合わない"
    セマンティクスや、型が、合っていない。`VSOutput` を、両方で、同じ構造体に、すると、間違えにくい。

??? failure "ビルドしたのに、古い、シェーダーが、動く"
    `.cso` の、出力先と、読み込み先が、違う。Debug と Release の、出力フォルダを、取り違えている。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シェーダー ＝ GPU で動く小さなプログラム。HLSL で書き、バイトコードにする
    - [x] 実行時は `D3DCompileFromFile`、製品は、ビルド時に `.cso` を作る
    - [x] 入口の関数名と、ターゲット（`vs_5_0` など）を、指定
    - [x] コンパイル エラーの、文字列は、必ず、表示する
    - [x] `CreateVertexShader`・`CreatePixelShader`・`CreateComputeShader` で、オブジェクトにする
    - [x] SM 6 以上は、`dxc`（D3D12）

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Input Layout](input-layout.md)
- [Drawing a Triangle](triangle.md)
- [Compute Shader](compute-shader.md)
- [Shaders and DXC](../dx12/shaders-dxc.md)
- [Microsoft Learn: D3DCompileFromFile](https://learn.microsoft.com/ja-jp/windows/win32/api/d3dcompiler/nf-d3dcompiler-d3dcompilefromfile)
