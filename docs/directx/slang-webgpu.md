---
title: Slang and WebGPU
tags:
  - DirectX
---

# Slang and WebGPU

HLSL で書いたシェーダーは、DirectX では動きますが、Vulkan や Metal、ブラウザーでは、そのままでは動きません。ゲームを複数の環境に出そうとすると、シェーダーを環境ごとに書き直すことになります。

この問題に取り組む新しい技術が Slang（シェーダー言語）と WebGPU（ブラウザー向けの描画 API）です。このページでは、この 2 つが何なのかを DirectX を知っている人向けに紹介します。実際に使う場面は、まだ限られますが、今後出会う可能性が高いので、概要を押さえておきます。

!!! tip "ポイント"
    - Slang は、HLSL に近い文法のシェーダー言語。HLSL、SPIR-V、Metal、GLSL、CUDA などに変換できる
    - 追加の機能として、モジュール、ジェネリクス（interface）、自動微分がある
    - WebGPU は、ブラウザーから GPU を使う API。DX12、Vulkan、Metal の共通部分を取り出した形をしている
    - WebGPU のシェーダー言語は WGSL。ネイティブ用の実装（Dawn、wgpu）を使うと、アプリからも使える
    - どちらも、「API ごとの違いを吸収する層」という立ち位置

!!! info "このページを読む前に"
    - [Shaders and DXC](dx12/shaders-dxc.md)
    - [DX12 and Vulkan Mapping](vulkan-mapping.md)

## Slang {#slang}

Slang は、NVIDIA が中心になって作り、Khronos Group（Vulkan を管理する団体）に移管された、シェーダー言語とコンパイラーです。

### HLSL に近い {#hlsl-like}

文法は HLSL に近く、既存の HLSL を少しの修正で読み込めます。HLSL を知っていれば、読み書きに困りません。

### 多くの出力先 {#targets}

1 つのソースから、次のような出力を作れます。

| 出力先 | 用途 |
| --- | --- |
| HLSL / DXIL | DirectX 11 / 12 |
| SPIR-V | Vulkan |
| Metal | Apple の環境 |
| GLSL | OpenGL |
| WGSL | WebGPU |
| CUDA | NVIDIA の GPU の計算 |

DirectX と Vulkan の両方に出すゲームでは、シェーダーを Slang 1 本で書けば、環境ごとの書き直しが減ります。

### 言語の機能 {#features}

HLSL にない機能があります。

- モジュール：`import` で、ソース ファイルを分割できる（HLSL は `#include`）
- ジェネリクスとインターフェース：`interface` で共通の約束を決め、実装を差し替えられる。マテリアルの切り替えなどに使う
- 自動微分：シェーダーの関数の微分を自動で作れる。微分可能レンダリングや、機械学習に使う

ゲームでは、まずマルチ API 対応のために使われます。

## WebGPU {#webgpu}

WebGPU は、W3C が標準化した、ブラウザーから GPU を使うための API です。WebGL の後継にあたります。

WebGL は、OpenGL ES を元にした古い API で、新しい GPU の機能を引き出せません。WebGPU は、DX12、Vulkan、Metal に共通する考え方（コマンドの記録、パイプラインの事前作成、バインド グループ）を取り出した設計で、これらの上に実装されます。

### DX12 を知っていると {#dx12}

用語は少し違いますが、構造は馴染みがあります。

| WebGPU | DX12 に近いもの |
| --- | --- |
| `GPUDevice` | `ID3D12Device` |
| `GPUQueue` | `ID3D12CommandQueue` |
| `GPUCommandEncoder` | コマンド リスト |
| `GPURenderPipeline` | PSO |
| `GPUBindGroup` | ディスクリプタ テーブル |
| `GPUBuffer` / `GPUTexture` | `ID3D12Resource` |

DX12 と違い、リソース バリアやヒープ管理は、WebGPU の実装が自動で行います。安全性のために、API が簡素になっています。

### WGSL {#wgsl}

WebGPU のシェーダー言語は WGSL で、Rust に似た文法です。HLSL とは別の言語なので、HLSL のコードを使いたい場合は、Slang で WGSL に変換する、という選択肢があります。

### ブラウザーの外でも {#native}

WebGPU の実装は、ブラウザーの外でも使えます。Google の Dawn と、Mozilla の wgpu が代表的です。C++ から Dawn を使うと、DX12、Vulkan、Metal をまたいで動くアプリが書けます。

## どう付き合うか {#how}

DirectX のゲームを作る学生にとっては、すぐに必要になる技術ではありません。ただ、次のような場面で出会います。

- ゲームを Vulkan や Switch、スマホにも出す（Slang や、シェーダーの変換）
- Web で動くデモを作る（WebGPU）
- クロスプラットフォームの描画ライブラリ（bgfx、Diligent Engine、Dawn など）を使う

まずは DirectX で描画の考え方を身につければ、これらは、その知識の応用として読めます。

## これだけ覚える {#summary}

- Slang は、HLSL に近いシェーダー言語で、HLSL、SPIR-V、Metal、WGSL などに変換できる
- WebGPU は、ブラウザー向けの現代的な描画 API。DX12、Vulkan、Metal の共通部分
- どちらも、API ごとの違いを吸収する層。DirectX の知識がそのまま土台になる

## 関連ページ

- [DX12 and Vulkan Mapping](vulkan-mapping.md)
- [Shaders and DXC](dx12/shaders-dxc.md)
- [DX11 and DX12 Mapping](compare.md)
