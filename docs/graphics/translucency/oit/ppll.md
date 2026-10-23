---
title: Per-Pixel Linked List (PPLL)
tags:
  - 描画
---

# Per-Pixel Linked List (PPLL)

<strong>PPLL は画素ごとに重なった半透明の断片をリストに記録し、最後に深度で並べ替えてブレンドする手法</strong>です。正確ですがメモリと並べ替えのコストが大きいです。このページでは PPLL の仕組みと実装を説明します。

!!! tip "ポイント"
    - 描画時：断片（色・深度）を、画素ごとのリストへ追加。
    - UAV とアトミック操作を使う。
    - 最後に画素ごとに深度で並べ替えて、ブレンド。
    - 重なりが多いとメモリと時間が膨らむ。

!!! info "このページを読む前に"
    - [Order-Independent Transparency (OIT)](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## Per-Pixel Linked List（PPLL）
<strong>画素ごとに重なったフラグメントを「連結リスト」で全部保存</strong>し、最後に画素ごとに深度順に並べて合成します。DirectX 11 の UAV とアトミック操作で実現できます（Yang らの手法）。

### データ構造

PPLL のデータ構造は 3 つです。ヘッド ポインタ バッファ（`RWTexture2D<uint>`）は、画素ごとのリストの先頭の番号を持ちます。ノード バッファ（`RWStructuredBuffer<Node>`）はフラグメントの色・深度・次のノード番号を持ちます。カウンタは次に使えるノード番号です（`InterlockedAdd`）。

原典は Yang らの "Real-Time Concurrent Linked List Construction on the GPU"（EGSR 2010）です。

```hlsl
struct Node {
  uint color;
  float depth;
  uint next;
};
```

リストの 1 つのノード（フラグメント 1 枚ぶん）です。色（パック済み）、深度、そして同じ画素の次のノードの番号を、持ちます。

```hlsl
RWTexture2D<uint> head_pointers : register(u1);
RWStructuredBuffer<Node> nodes : register(u2);
RWByteAddressBuffer counter : register(u3);
```

3 つの UAV を使います。`head_pointers` は画素ごとのリストの先頭、`nodes` は全ノードを入れるバッファ、`counter` は次に使うノードの番号を数える、カウンターです。

```hlsl
[earlydepthstencil]
void PSCollect(VsOutput input) {
  float4 color = Shade(input);
  uint node_index;
  counter.InterlockedAdd(0, 1, node_index);
  if (node_index >= kMaxNodes) return;
```

`[earlydepthstencil]` は深度テストをピクセル シェーダーの前に、行う指定です。不透明な物の後ろに隠れたフラグメントは、ノードを作らずに捨てられます。ノードの番号をカウンターでアトミックに確保し、バッファが満杯なら捨てます。

```hlsl
  uint previous_head;
  InterlockedExchange(head_pointers[uint2(input.position.xy)], node_index, previous_head);
```

この画素の先頭を新しいノードの番号に、入れ替え前の先頭を受け取ります。1 命令で行うので同じ画素に同時に書く、スレッドがあってもリストが壊れません。

```hlsl
  Node node;
  node.color = PackColor(color);
  node.depth = input.position.z;
  node.next = previous_head;
  nodes[node_index] = node;
}
```

| 点 | 説明 |
| --- | --- |
| `[earlydepthstencil]` | 不透明の物に隠れたフラグメントを、シェーダーの前に捨てる（重要。ノードの無駄を減らす） |
| `InterlockedAdd` | ノード番号を確保 |
| `InterlockedExchange` | ヘッドを自分に付け替え、元のヘッドを `next` に（先頭に挿入） |
| `kMaxNodes` | ノード バッファの上限（超えたら、捨てる）。画面解像度 × 平均層数 × 係数で決める |

### 合成パス

画素ごとにリストをたどって配列に取り出し、深度でソートして奥から合成します。

```hlsl
float4 PSResolve(VsOutput input) : SV_Target {
  uint head = head_pointers[uint2(input.position.xy)];
  Node list[kMaxLayers];
  int count = 0;
  while (head != kInvalid && count < kMaxLayers) {
    list[count++] = nodes[head];
    head = list[count - 1].next;
  }
```

合成パスです。画素の先頭からリストを辿って、ローカルの配列に取り出します。長すぎるリストは `kMaxLayers` で打ち切ります。

```hlsl
  for (int i = 1; i < count; ++i) {
    Node key = list[i];
    int j = i - 1;
    while (j >= 0 && list[j].depth < key.depth) {
      list[j + 1] = list[j];
      --j;
    }
    list[j + 1] = key;
  }
```

奥の物が先になるよう深度の大きい順に、並べ替えます。層が数枚〜十数枚なので挿入ソートで、十分です。

```hlsl
  float4 result = float4(0, 0, 0, 0);
  for (int k = 0; k < count; ++k) {
    float4 c = UnpackColor(list[k].color);
    result.rgb = c.rgb * c.a + result.rgb * (1.0 - c.a);
    result.a = c.a + result.a * (1.0 - c.a);
  }
  return result;
}
```

並べ替えのコードの要点です。`kMaxLayers` は 1 画素で扱う最大層数で、ローカル配列の大きさです（16〜32）。多いほどレジスタを消費します。層数が少ないので単純な挿入ソートで十分です。深度の大きい（遠い）順に降順で並べ、奥から手前へ合成します。

PPLL の利点は正確なこと（ソート済みで合成）、層数に上限がないこと（ノード バッファの許す限り）、ライティング済みの色を保存するので後処理が簡単なことです。欠点はメモリが大きいこと（4K で数百 MB になりうる）、画素ごとのソートが重いこと（層が多いと極端に遅い）、オーバーフロー時にフラグメントが欠けることです。

<!-- fig:ppll-chain:begin -->

<svg class="fig illust motion" data-fig="ppll-chain" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ppll-chain" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">PPLL: 画素ごとに連結リストを作り、最後に深度で並べ替える</text>
<rect x="60" y="170" width="90" height="60" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
<text x="105" y="206" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">head</text>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1032;0.1034;1.0000" values="0;0;1;1"/><rect x="560" y="170" width="90" height="60" fill="#2563eb" opacity="0.9"/>
<text x="605" y="196" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">F1</text>
<text x="605" y="216" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#ffffff">z = 0.7</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2549;0.2552;1.0000" values="0;0;1;1"/><rect x="400" y="170" width="90" height="60" fill="#2ea043" opacity="0.9"><animate attributeName="x" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5517;0.6552;1.0000" values="400;400;240;240"/></rect>
<text x="445" y="196" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">F2<animate attributeName="x" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5517;0.6552;1.0000" values="445;445;285;285"/></text>
<text x="445" y="216" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#ffffff">z = 0.3<animate attributeName="x" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5517;0.6552;1.0000" values="445;445;285;285"/></text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4066;0.4069;1.0000" values="0;0;1;1"/><rect x="240" y="170" width="90" height="60" fill="#e5aa28" opacity="0.9"><animate attributeName="x" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5517;0.6552;1.0000" values="240;240;400;400"/></rect>
<text x="285" y="196" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">F3<animate attributeName="x" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5517;0.6552;1.0000" values="285;285;445;445"/></text>
<text x="285" y="216" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#ffffff">z = 0.5<animate attributeName="x" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5517;0.6552;1.0000" values="285;285;445;445"/></text>
</g>
<text x="390" y="110" text-anchor="middle" style="font-size:13px;font-weight:500;fill:#64748b">到着順: F1 → F2 → F3（新しいものが、リストの先頭になる）</text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">最初、リストは空<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1032;0.1034;1.0000" values="1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">F1 が到着: head が F1 を指す<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1032;0.1034;0.2549;0.2552;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">F2 が到着: head → F2 → F1<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2549;0.2552;0.4066;0.4069;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">F3 が到着: head → F3 → F2 → F1。深度はバラバラ<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4066;0.4069;0.5514;0.5517;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深度の小さい順に並べ替え: F2(0.3) → F3(0.5) → F1(0.7)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5514;0.5517;0.7583;0.7586;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">奥から手前へ、順に混ぜる<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7583;0.7586;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:ppll-chain:end -->

## 考え方：全部、リストに溜める

<strong>PPLL（Per-Pixel Linked List、画素ごとの連結リスト）</strong>は 画面の各画素に重なる、すべてのフラグメントをリストとして、溜めて、最後に画素ごとにソートしてブレンドする方法です（Yang ら、2010）。デプス ピーリングのような複数パスが不要で、1 パスですべての層を集められます。

```text
画素 (x, y):  head ──→ [赤, 深度 0.3] ──→ [青, 深度 0.7] ──→ [緑, 深度 0.5] ──→ 終わり
                          リストの順序は、描かれた順（深度の順ではない）

最後に、画素ごとに、リストを取り出して、深度で並べ替え、奥から手前へブレンドする
```

## データ構造

| 要素 | 内容 |
| --- | --- |
| ヘッド ポインタ バッファ（画面と同じ大きさ） | 各画素の、リストの先頭の番号。最初は `0xFFFFFFFF`（空） |
| フラグメント バッファ（大きな配列） | 全フラグメントを、1 本の配列に書き込む。各要素は `色`、`深度`、`次の要素の番号` |
| カウンター | 次に使う、フラグメント バッファの位置（アトミックに、増やす） |

```hlsl
struct FragmentNode {
  uint packed_color;      // RGBA8 に詰めた色
  float depth;            // 深度（並べ替え用）
  uint next;              // 同じ画素の、次のフラグメントの番号（0xFFFFFFFF なら、終わり）
};

RWStructuredBuffer<FragmentNode> g_fragments : register(u1);     // フラグメント バッファ
RWByteAddressBuffer g_head : register(u2);                       // ヘッド ポインタ（画素ごと）
RWByteAddressBuffer g_counter : register(u3);                    // 割り当て済みの、数
```

## 構築パス：フラグメントを溜める

半透明のピクセル シェーダーで、<strong>フラグメントを書き込み</strong>ます。レンダー ターゲットには描きません（`discard` するか、書き込みマスクを無効に）。

```hlsl
// 構築パス（半透明のオブジェクトを描くとき）。
[earlydepthstencil]                                              // 不透明の深度で、隠れたフラグメントを、事前に捨てる
void BuildPS(PSInput input) {
  float4 color = ShadeFragment(input);
```

構築パスの冒頭です。`[earlydepthstencil]` で隠れたフラグメントを先に捨て色を、計算します。

```hlsl
  // ① フラグメント バッファの、空き位置を、アトミックに、確保する
  uint index;
  g_counter.InterlockedAdd(0, 1, index);
  if (index >= kMaxFragments) return;                             // 溢れたら、捨てる
```

①ノードを入れる場所（番号）を、カウンターでアトミックに確保します。溢れたらそのフラグメントは捨てます。

```hlsl
  // ② この画素の、ヘッドを、新しいノードに、入れ替え、前のヘッドを、受け取る
  uint pixel = (uint)input.position.y * g_screen_width + (uint)input.position.x;
  uint prev_head;
  g_head.InterlockedExchange(pixel * 4, index, prev_head);
```

②この画素の先頭を自分の番号に、入れ替えて前の先頭を受け取ります。

```hlsl
  // ③ 新しいノードを、書き込む（次 = 前のヘッド）
  FragmentNode node;
  node.packed_color = PackColor(color);
  node.depth = input.position.z;
  node.next = prev_head;
  g_fragments[index] = node;
}
```

| 命令 | 内容 |
| --- | --- |
| `InterlockedAdd` | カウンターをアトミックに、増やして自分の番号を得る |
| `InterlockedExchange` | ヘッドを自分の番号に、入れ替え前のヘッドを受け取る。これでリストの先頭に追加される |
| `[earlydepthstencil]` | 不透明な物で隠れた、フラグメントはシェーダー実行前に、捨てる |

## 解決パス：ソートしてブレンド

<strong>全画面のピクセル シェーダー</strong>で、画素ごとにリストを取り出し、ソートしてブレンドします。

```hlsl
float4 ResolvePS(float4 pos : SV_Position) : SV_Target {
  uint pixel = (uint)pos.y * g_screen_width + (uint)pos.x;
  uint node_index = g_head.Load(pixel * 4);
```

合成パスの冒頭です。画素の番号から先頭のノードを、読みます。

```hlsl
  // ① リストを、ローカル配列に、取り出す（最大 kMaxLayers 個）
  FragmentNode layers[kMaxLayers];
  int count = 0;
  while (node_index != 0xFFFFFFFF && count < kMaxLayers) {
    layers[count++] = g_fragments[node_index];
    node_index = layers[count - 1].next;
  }
```

①リストを辿ってローカルの配列に、取り出します（最大 `kMaxLayers` 個）。

```hlsl
  // ② 深度の大きい順（奥から手前）に、並べ替える（挿入ソート。層が、少ないので、これで十分）
  for (int i = 1; i < count; ++i) {
    FragmentNode key = layers[i];
    int j = i - 1;
    while (j >= 0 && layers[j].depth < key.depth) { layers[j + 1] = layers[j]; --j; }
    layers[j + 1] = key;
  }
```

②深度の大きい順（奥から手前）に、挿入ソートします。

```hlsl
  // ③ 背景（不透明の描画結果）から、奥から手前へ、順にブレンドする
  float3 color = g_opaque_color.Load(int3(pos.xy, 0)).rgb;
  for (int k = 0; k < count; ++k) {
    float4 c = UnpackColor(layers[k].packed_color);
    color = lerp(color, c.rgb, c.a);                              // 通常のアルファ ブレンド
  }
  return float4(color, 1.0);
}
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 正確（最大 `kMaxLayers` まで）。1 パスで全層を集められる |
| 長所 | 半透明のジオメトリを、1 回だけ描く（デプス ピーリングは、層の数だけ描く） |
| 短所 | メモリが大きい（フラグメント バッファ）。画面の数倍〜数十倍のフラグメントを、想定する |
| 短所 | バッファが溢れると、フラグメントが捨てられる（画面が、欠ける）。上限の見積もりが必要 |
| 短所 | アトミック命令が、同じ画素に集中すると競合して、遅い |
| 短所 | 解決パスの画素ごとの、ソートが重い（層が多い画素） |
| 短所 | 画素ごとにリストの長さが、バラバラで GPU のスレッドが、待たされる（ワープ内のばらつき） |

## 最適化

| 工夫 | 内容 |
| --- | --- |
| 色を詰める | 色を `RGBA8`（4 バイト）にして、深度と合わせて 8 バイトに。ノード全体で 12 バイト（次の番号を含む） |
| 層の数の上限 | `kMaxLayers = 8〜16`。それ以上は近似（奥の層をまとめる） |
| 手前を残して奥をまとめる | 最も手前の、数層だけ正確に。残りは WBOIT で近似（ハイブリッド、[Hybrid Approaches and Choosing](hybrid.md)） |
| 低解像度で集める | 煙のような、ぼやけた物は画面の半分の解像度で集めて、アップサンプル |
| 画面をタイルに分ける | タイルごとに、フラグメントの上限を決める |

## DirectX 11 での、リソース

PPLL には <strong>`RWByteAddressBuffer`</strong> と `RWStructuredBuffer`（UAV）を、ピクセル シェーダーから書き込む必要があります。DirectX 11 ではピクセル シェーダーでの、UAV の使用ができます（`OMSetRenderTargetsAndUnorderedAccessViews`）。

```cpp
// レンダー ターゲット 0 個（描かない）+ UAV 3 つ（ヘッド、フラグメント、カウンター）を、ピクセル シェーダーへ設定する。
ID3D11UnorderedAccessView* uavs[3] = {fragment_uav.Get(), head_uav.Get(), counter_uav.Get()};
UINT initial_counts[3] = {0, 0, 0};
context->OMSetRenderTargetsAndUnorderedAccessViews(
    0, nullptr, depth_dsv_readonly.Get(),    // レンダー ターゲットなし。深度は、読み取り専用
    1, 3, uavs, initial_counts);             // UAV はスロット 1 から
// 毎フレームの最初に、ヘッド バッファを 0xFFFFFFFF で、カウンターを 0 で、クリアする。
const UINT clear_head[4] = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF};
context->ClearUnorderedAccessViewUint(head_uav.Get(), clear_head);
```

## よくあるミス

??? failure "重なりが多い所で、リストがあふれる"
    <strong>リストの長さに上限</strong>を設け、超えた分は破棄する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 断片を記録して、最後に並べ替える
    - [x] 正確だが、メモリを食う

## 参考

- Yang, Hensley, Grün, Thibieroz, "Real-Time Concurrent Linked List Construction on the GPU", Computer Graphics Forum (Eurographics Symposium on Rendering 2010)
- Carpenter, "The A-buffer, an Antialiased Hidden Surface Method", SIGGRAPH 1984
- Salvi, Montgomery, Lefohn, "Adaptive Transparency", High-Performance Graphics 2011
- Wyman, "Exploring and Expanding the Continuum of OIT Algorithms", High-Performance Graphics 2016
- Microsoft Learn, "RWStructuredBuffer / RWByteAddressBuffer"（HLSL のバッファ）と "InterlockedExchange"

## 関連ページ

- [OIT](index.md)
- [Depth Peeling](depth-peeling.md)
- [Hybrid Approaches and Choosing](hybrid.md)
