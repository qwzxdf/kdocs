---
title: GPU Driven Rendering
tags:
  - 最適化
  - 3Dゲーム
---

# GPU Driven Rendering

[ドロー コール](draw-calls.md)と[カリング](culling.md)は、**CPU が**、<strong>「何を描くか」を、1 つずつ、判断</strong>して、**1 つずつ、命令を出す**仕事でした。**物体が数万個**になると**この CPU の仕事が、限界**になります。**GPU Driven Rendering**は、**その判断と命令の作成を、GPU 自身にやらせる**方式です。**CPU は、「全物体のデータ」を、GPU に置いておくだけ**で**カリングも描画命令の作成も、GPU が行います**。このページは**何が改善するのか**、**仕組み**、**DX11 でできること・できないこと**を説明します。

!!! tip "ポイント"
    - 目的：<strong>CPU の仕事（カリング・ドロー コールの作成）を、GPU に移す</strong>。<strong>物体数が数万〜数十万でも、CPU がほぼ一定</strong>。
    - 中心の仕組み：<strong>① 全物体のデータを、GPU バッファに常駐　② コンピュート シェーダーで、カリング　③ 生き残った物の、描画引数を、GPU が書く　④ インダイレクト描画（Indirect）で、GPU が自分の書いた命令を実行</strong>。
    - <strong>CPU ⇄ GPU の、やり取りがほぼなくなる</strong>（<strong>ドロー コールもほぼ 1 回に</strong>）。
    - <strong>カリングも細かく</strong>できる（<strong>サブメッシュ・Meshlet 単位</strong>）。<strong>Hi-Z オクルージョン</strong>も、GPU で。
    - <strong>DX11</strong>：<strong>`DrawIndexedInstancedIndirect`</strong> で、<strong>部分的にできる</strong>（<strong>複数の描画を、1 回の命令でできない</strong>）。<strong>DX12 の `ExecuteIndirect`・Vulkan の multi-draw indirect</strong>が、本命。
    - <strong>制約</strong>：<strong>材質・シェーダーの扱い（バインドレス）が、必要</strong>。<strong>設計が大変</strong>。

## 従来の方式（CPU Driven）の問題

**毎フレーム**、**CPU が次の仕事を繰り返します**。

<svg class="fig illust" viewBox="0 0 800 280" role="img" aria-label="CPU Driven と GPU Driven の比べ">
<defs><marker id="gd1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">上：CPU Driven（CPU が、毎フレーム、全部やる）／下：GPU Driven（GPU が、自分で、決めて、描く）</text>
<rect x="20" y="40" width="130" height="60" rx="8" fill="rgba(229,72,77,0.25)" stroke="currentColor" stroke-width="2"/><text x="85" y="66" text-anchor="middle" style="font-weight:700">CPU</text><text x="85" y="86" text-anchor="middle" style="font-size:11px">全物体を判定</text>
<line x1="156" y1="70" x2="206" y2="70" stroke="currentColor" stroke-width="3" marker-end="url(#gd1)"/>
<rect x="214" y="40" width="190" height="60" rx="8" fill="rgba(229,72,77,0.25)" stroke="currentColor" stroke-width="2"/><text x="309" y="66" text-anchor="middle" style="font-weight:700">ドロー コール × 数千</text><text x="309" y="86" text-anchor="middle" style="font-size:11px">1 つずつ、命令を作る</text>
<line x1="410" y1="70" x2="460" y2="70" stroke="currentColor" stroke-width="3" marker-end="url(#gd1)"/>
<rect x="468" y="40" width="130" height="60" rx="8" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="533" y="76" text-anchor="middle" style="font-weight:700">GPU が描く</text>
<text x="620" y="76" style="font-size:12px;fill:#e5484d;font-weight:700">CPU が、ボトルネック</text>
<rect x="20" y="150" width="190" height="90" rx="8" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/><text x="115" y="176" text-anchor="middle" style="font-weight:700">全物体のデータ</text><text x="115" y="196" text-anchor="middle" style="font-size:11px">GPU バッファに、常駐</text><text x="115" y="214" text-anchor="middle" style="font-size:11px">（毎フレーム送らない）</text>
<line x1="216" y1="195" x2="262" y2="195" stroke="currentColor" stroke-width="3" marker-end="url(#gd1)"/>
<rect x="270" y="150" width="170" height="90" rx="8" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="355" y="176" text-anchor="middle" style="font-weight:700">コンピュート</text><text x="355" y="196" text-anchor="middle" style="font-size:11px">カリング</text><text x="355" y="214" text-anchor="middle" style="font-size:11px">描画引数を、書く</text>
<line x1="446" y1="195" x2="492" y2="195" stroke="currentColor" stroke-width="3" marker-end="url(#gd1)"/>
<rect x="500" y="150" width="150" height="90" rx="8" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="575" y="176" text-anchor="middle" style="font-weight:700">インダイレクト</text><text x="575" y="196" text-anchor="middle" style="font-size:11px">描画（ほぼ 1 回）</text>
<text x="660" y="196" style="font-size:12px;fill:#2ea043;font-weight:700">CPU は、ほぼ暇</text>
</svg>

| 従来の仕事（CPU） | 問題 |
| --- | --- |
| **物体ごとのカリング** | **数万個を毎フレーム、CPU が判定** |
| **物体ごとの描画命令** | **ドロー コールが数千〜数万** |
| **物体ごとの定数バッファ更新** | **CPU → GPU の、転送が多い** |
| **GPU の結果を待てない** | **カリングの結果を、CPU が知れない**（**同期待ちを避けるため**） |

## GPU Driven の、仕組み

### 1. データを、GPU に常駐させる

**シーンの全物体**（インスタンス）の、**ワールド行列・境界（球・箱）・メッシュの番号・材質の番号**を、**GPU のバッファ**（構造化バッファ）に、**置いておきます**。**動く物の変化した部分だけ**、**毎フレーム、更新**します。

| バッファ | 内容 |
| --- | --- |
| **インスタンス バッファ** | **ワールド行列・境界・メッシュ ID・材質 ID** |
| **メッシュ（ジオメトリ）バッファ** | **全メッシュの頂点・インデックスを、1 つの巨大なバッファ**に（**オフセットで参照**） |
| **材質バッファ** | **全材質のパラメータ・テクスチャの番号** |

### 2. コンピュート シェーダーで、カリング

**物体ごと（またはサブメッシュ・Meshlet ごと）に、1 つのスレッド**が**視錐台・オクルージョン・距離**で**見えるか**を判定します。

```hlsl
[numthreads(64, 1, 1)]
void CullCS(uint3 id : SV_DispatchThreadID) {
  Instance inst = instances[id.x];
  if (!InFrustum(inst.bounds)) return;
  if (IsOccluded(inst.bounds, hiz)) return;

  uint slot;
  InterlockedAdd(counter[0], 1, slot);
  visible_indices[slot] = id.x;
}
```

| 点 | 説明 |
| --- | --- |
| **数万個を並列に判定** | **GPU の並列性**が活きる（CPU の数十倍速い） |
| **`InterlockedAdd`** | **見えた物の詰め込み位置をアトミックに確保** |
| **出力** | **見えた物のインスタンス番号のリスト**と、**個数**（カウンター） |

### 3. 描画引数を、GPU が書く

**インダイレクト描画**は、**描画の引数**（**インデックス数・インスタンス数・開始位置**）を、**GPU バッファから、読んで**描きます。**この引数をコンピュート シェーダーが、書きます**。

```cpp
struct DrawIndexedIndirectArgs {
  uint32_t index_count_per_instance;
  uint32_t instance_count;
  uint32_t start_index_location;
  int32_t base_vertex_location;
  uint32_t start_instance_location;
};
```

```cpp
context->DrawIndexedInstancedIndirect(args_buffer, 0);
```

| 点 | 説明 |
| --- | --- |
| **`DrawIndexedInstancedIndirect`**（DX11） | **引数バッファ（`D3D11_RESOURCE_MISC_DRAWINDIRECT_ARGS`）から、描画** |
| **CPU は結果を知らない** | **何個描かれるか**は、**GPU が決める**（**CPU への読み戻しが、不要** ＝ **同期待ちなし**） |
| **インスタンス数にカリング結果が入る** | **カリング後の個数**で**描画** |

### 4. 1 回（または少数回）で、描く

**全メッシュを、1 つの巨大なバッファ**に入れ、**マルチ ドロー**（**複数の描画を、1 回の命令で**）にすれば、**ドロー コール 1 回**で、**全シーン**を描けます。

| API | マルチ ドロー |
| --- | --- |
| **DX12** | **`ExecuteIndirect`**（**複数の描画を、1 回で**） |
| **Vulkan** | **`vkCmdDrawIndexedIndirectCount`** |
| **DX11** | **`DrawIndexedInstancedIndirect` を、メッシュの種類ごとに、1 回**（**メッシュの数だけ**。**マルチ ドローは、標準ではない**） |

<strong>DX11 では、「メッシュの種類ごとに、1 回のインスタンス描画」</strong>が、**現実的な形**です（**同じメッシュを多数描く**）。

## 何が改善するのか

| 改善 | 説明 |
| --- | --- |
| **CPU の負担が一定** | **物体が、10 倍になっても、CPU はほぼ同じ**（GPU が並列に処理） |
| **カリングが細かく・強力に** | **サブメッシュ・Meshlet 単位**・**Hi-Z オクルージョン**を、**GPU で**（[カリング](culling.md)） |
| **ドロー コール・状態切り替えが激減** | **1 回〜少数回** |
| **同期待ちがない** | **カリング結果を、CPU に戻さない** |
| **大量のインスタンス** | **数十万個の草・岩・瓦礫** |

## 2 パス オクルージョン カリング

**Hi-Z オクルージョン**は、**前フレームの深度**を使うと、**遅れが出ます**（[カリング](culling.md)）。**GPU Driven で、これを解決する、定番の方法**です。

| パス | 内容 |
| --- | --- |
| **パス 1** | **前フレームで見えていた物**を**カリングして**、描く（**深度ができる**） |
| **深度の階層（Hi-Z）を、作る** | **今のフレームのパス 1 の深度**から |
| **パス 2** | **パス 1 で除外された物**を**今の Hi-Z で再判定**し、**見えるものだけ、追加で描く** |

**前フレームの見えていた物は、ほぼ、今も見える**ので**パス 1 で大半を描け**、**パス 2 は新しく見えるものだけ**——**遅れによる、ポップインも起きません**。

## 設計の課題

| 課題 | 説明 |
| --- | --- |
| **材質・シェーダーの扱い** | **1 回の描画で複数の材質**を扱う必要。<strong>バインドレス（テクスチャ配列・番号参照）</strong>が必要 |
| **透明物** | **ソートが必要**。**GPU Driven と、相性が悪い**（**別パス**） |
| <strong>動的なメッシュ（スキニング）</strong> | **事前にスキニング結果をバッファに書く** |
| **デバッグが難しい** | **GPU の中の処理**。**RenderDoc・PIX でバッファの中身を確認** |
| <strong>API の制約（DX11）</strong> | **マルチ ドローがない**。**DX12・Vulkan が本命** |
| **ツールとアセットの準備** | **メッシュを、1 つのバッファに**。**Meshlet 化など、ビルド時の処理**（[ベイク](../optimize/baking.md)） |

## 段階的に取り入れる

| 段階 | 内容 |
| --- | --- |
| **1. GPU インスタンシング** | **同じメッシュの多数のインスタンスをコンピュートでカリングし、`DrawIndexedInstancedIndirect`** |
| **2. 複数メッシュのインダイレクト** | **メッシュごとに引数バッファ**。**カリングをコンピュートに** |
| **3. Hi-Z オクルージョン** | **GPU で、2 パス** |
| **4. マルチ ドロー・バインドレス**（DX12 / Vulkan） | **全シーンを、1 回の描画で** |
| **5. Meshlet** | **単位を細かく**（[Mesh Shader](mesh-shaders.md)） |

## よくあるミス

??? failure "CPU が、ボトルネックでないのに、GPU Driven を導入する"
    **複雑さに見合いません**。**CPU のドロー コールが、限界のとき**に導入します。

??? failure "インダイレクト引数の、構造体の並びを間違える"
    **引数の順序・型**（`uint`）を、確認します。**デバッグ時はバッファを読み出して確認**。

??? failure "カリング結果の、カウンターを毎フレーム、クリアしない"
    **コンピュートの前に、0 にリセット**します。

??? failure "前フレームの Hi-Z で、急なカメラ移動にポップインする"
    **2 パス方式**にします。

??? failure "DX11 で、マルチ ドローを期待する"
    **DX11 は標準ではない**。**メッシュごとのインダイレクト**にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU Driven ＝ <strong>カリングと描画命令の作成を、GPU にやらせる</strong>。<strong>CPU の負担が物体数に依存しない</strong>
    - [x] 流れ：<strong>データ常駐 → コンピュートでカリング → 描画引数を、GPU が書く → インダイレクト描画</strong>
    - [x] <strong>同期待ちがなく</strong>、<strong>カリングも細かく（Meshlet・Hi-Z）</strong>できる
    - [x] <strong>2 パス オクルージョン</strong>で、<strong>前フレームの遅れ</strong>を解決
    - [x] <strong>DX11 は、`DrawIndexedInstancedIndirect`</strong>（メッシュごと）。<strong>マルチ ドローは DX12 / Vulkan</strong>
    - [x] <strong>CPU が、ボトルネックのときに</strong>導入。<strong>段階的に</strong>

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [ドロー コールとバッチ](draw-calls.md)
- [カリング](culling.md)
- [Mesh Shader と Meshlet](mesh-shaders.md)
- [Hi-Z とスクリーン空間トレース](hiz.md)
- [GPU Driven（D3D12 詳細）](gpu-driven-dx12/index.md)
