---
title: Per-Pixel Linked List (PPLL)
tags:
  - 描画
---

# Per-Pixel Linked List (PPLL)

**PPLL は、画素ごとに、重なった半透明の断片をリストに記録し、最後に深度で並べ替えて、ブレンドする手法**です。**正確ですが、メモリと並べ替えのコストが大きい**です。このページでは、**PPLL の仕組みと実装**を説明します。

!!! tip "ポイント"
    - **描画時：断片（色・深度）を、画素ごとのリストへ追加**。
    - **UAV と、アトミック操作**を使う。
    - **最後に、画素ごとに深度で並べ替えて、ブレンド**。
    - **重なりが多いと、メモリと時間が膨らむ**。

## Per-Pixel Linked List（PPLL）
**画素ごとに、重なったフラグメントを「連結リスト」で全部保存**し、**最後に、画素ごとに、深度順に並べて合成**します。**DirectX 11 の UAV とアトミック操作**で**実現**できます（**Yang らの手法**）。

### データ構造

PPLL のデータ構造は、3 つです。ヘッド ポインタ バッファ（`RWTexture2D<uint>`）は、画素ごとのリストの先頭の番号を持ちます。ノード バッファ（`RWStructuredBuffer<Node>`）は、フラグメントの色・深度・次のノード番号を持ちます。カウンタは、次に使えるノード番号です（`InterlockedAdd`）。

原典は、Yang らの "Real-Time Concurrent Linked List Construction on the GPU"（EGSR 2010）です。

```hlsl
struct Node {
  uint color;
  float depth;
  uint next;
};

RWTexture2D<uint> head_pointers : register(u1);
RWStructuredBuffer<Node> nodes : register(u2);
RWByteAddressBuffer counter : register(u3);

[earlydepthstencil]
void PSCollect(VsOutput input) {
  float4 color = Shade(input);
  uint node_index;
  counter.InterlockedAdd(0, 1, node_index);
  if (node_index >= kMaxNodes) return;

  uint previous_head;
  InterlockedExchange(head_pointers[uint2(input.position.xy)], node_index, previous_head);

  Node node;
  node.color = PackColor(color);
  node.depth = input.position.z;
  node.next = previous_head;
  nodes[node_index] = node;
}
```

| 点 | 説明 |
| --- | --- |
| **`[earlydepthstencil]`** | **不透明の物に隠れたフラグメントを、シェーダーの前に捨てる**（**重要。ノードの無駄を減らす**） |
| **`InterlockedAdd`** | **ノード番号を確保** |
| **`InterlockedExchange`** | **ヘッドを、自分に付け替え**、**元のヘッドを `next` に**（**先頭に挿入**） |
| **`kMaxNodes`** | **ノード バッファの上限**（**超えたら、捨てる**）。**画面解像度 × 平均層数 × 係数**で決める |

### 合成パス

**画素ごとに、リストをたどって配列に取り出し、深度でソートして、奥から合成**します。

```hlsl
float4 PSResolve(VsOutput input) : SV_Target {
  uint head = head_pointers[uint2(input.position.xy)];
  Node list[kMaxLayers];
  int count = 0;
  while (head != kInvalid && count < kMaxLayers) {
    list[count++] = nodes[head];
    head = list[count - 1].next;
  }

  for (int i = 1; i < count; ++i) {
    Node key = list[i];
    int j = i - 1;
    while (j >= 0 && list[j].depth < key.depth) {
      list[j + 1] = list[j];
      --j;
    }
    list[j + 1] = key;
  }

  float4 result = float4(0, 0, 0, 0);
  for (int k = 0; k < count; ++k) {
    float4 c = UnpackColor(list[k].color);
    result.rgb = c.rgb * c.a + result.rgb * (1.0 - c.a);
    result.a = c.a + result.a * (1.0 - c.a);
  }
  return result;
}
```

並べ替えのコードの要点です。`kMaxLayers` は、1 画素で扱う最大層数で、ローカル配列の大きさです（16〜32）。多いほどレジスタを消費します。層数が少ないので、単純な挿入ソートで十分です。深度の大きい（遠い）順に降順で並べ、奥から手前へ合成します。

PPLL の利点は、正確なこと（ソート済みで合成）、層数に上限がないこと（ノード バッファの許す限り）、ライティング済みの色を保存するので後処理が簡単なことです。欠点は、メモリが大きいこと（4K で数百 MB になりうる）、画素ごとのソートが重いこと（層が多いと極端に遅い）、オーバーフロー時にフラグメントが欠けることです。

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

## 考え方：全部、リストに、溜める

**PPLL（Per-Pixel Linked List、画素ごとの、連結リスト）**は、**画面の各画素に、重なる、すべての、フラグメントを、リストとして、溜めて**、**最後に、画素ごとに、ソートして、ブレンド**する方法です（Yang ら、2010）。**デプス ピーリングのような、複数パスが、不要**で、**1 パスで、すべての層を、集められます**。

```text
画素 (x, y):  head ──→ [赤, 深度 0.3] ──→ [青, 深度 0.7] ──→ [緑, 深度 0.5] ──→ 終わり
                          リストの順序は、描かれた順（深度の順ではない）

最後に、画素ごとに、リストを取り出して、深度で並べ替え、奥から手前へブレンドする
```

## データ構造

| 要素 | 内容 |
| --- | --- |
| **ヘッド ポインタ バッファ**（画面と同じ大きさ） | 各画素の、リストの**先頭の、番号**。最初は `0xFFFFFFFF`（空） |
| **フラグメント バッファ**（大きな配列） | 全フラグメントを、**1 本の配列**に、書き込む。各要素は、`色`、`深度`、`次の要素の番号` |
| **カウンター** | 次に、使う、フラグメント バッファの、位置（アトミックに、増やす） |

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

## 構築パス：フラグメントを、溜める

半透明の、ピクセル シェーダーで、**フラグメントを、書き込み**ます。**レンダー ターゲットには、描きません**（`discard` するか、書き込みマスクを、無効に）。

```hlsl
// 構築パス（半透明のオブジェクトを描くとき）。
[earlydepthstencil]                                              // 不透明の深度で、隠れたフラグメントを、事前に捨てる
void BuildPS(PSInput input) {
  float4 color = ShadeFragment(input);

  // ① フラグメント バッファの、空き位置を、アトミックに、確保する
  uint index;
  g_counter.InterlockedAdd(0, 1, index);
  if (index >= kMaxFragments) return;                             // 溢れたら、捨てる

  // ② この画素の、ヘッドを、新しいノードに、入れ替え、前のヘッドを、受け取る
  uint pixel = (uint)input.position.y * g_screen_width + (uint)input.position.x;
  uint prev_head;
  g_head.InterlockedExchange(pixel * 4, index, prev_head);

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
| `InterlockedAdd` | カウンターを、アトミックに、増やして、**自分の、番号**を得る |
| `InterlockedExchange` | ヘッドを、自分の番号に、**入れ替え**、**前のヘッド**を受け取る。これで、**リストの、先頭に、追加**される |
| `[earlydepthstencil]` | 不透明な物で、隠れた、フラグメントは、シェーダー実行前に、捨てる |

## 解決パス：ソートして、ブレンド

**全画面の、ピクセル シェーダー**で、**画素ごとに、リストを、取り出し、ソートして、ブレンド**します。

```hlsl
float4 ResolvePS(float4 pos : SV_Position) : SV_Target {
  uint pixel = (uint)pos.y * g_screen_width + (uint)pos.x;
  uint node_index = g_head.Load(pixel * 4);

  // ① リストを、ローカル配列に、取り出す（最大 kMaxLayers 個）
  FragmentNode layers[kMaxLayers];
  int count = 0;
  while (node_index != 0xFFFFFFFF && count < kMaxLayers) {
    layers[count++] = g_fragments[node_index];
    node_index = layers[count - 1].next;
  }

  // ② 深度の大きい順（奥から手前）に、並べ替える（挿入ソート。層が、少ないので、これで十分）
  for (int i = 1; i < count; ++i) {
    FragmentNode key = layers[i];
    int j = i - 1;
    while (j >= 0 && layers[j].depth < key.depth) { layers[j + 1] = layers[j]; --j; }
    layers[j + 1] = key;
  }

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
| 長所 | **正確**（最大 `kMaxLayers` まで）。**1 パス**で、全層を、集められる |
| 長所 | **半透明の、ジオメトリを、1 回だけ、描く**（デプス ピーリングは、層の数だけ描く） |
| 短所 | **メモリ**が、大きい（フラグメント バッファ）。画面の、数倍〜数十倍の、フラグメントを、想定する |
| 短所 | **バッファが、溢れる**と、**フラグメントが、捨てられる**（画面が、欠ける）。上限の見積もりが、必要 |
| 短所 | **アトミック命令**が、**同じ画素に、集中**すると、競合して、遅い |
| 短所 | 解決パスの、画素ごとの、**ソートが、重い**（層が、多い画素） |
| 短所 | **画素ごとに、リストの長さが、バラバラ**で、**GPU の、スレッドが、待たされる**（ワープ内のばらつき） |

## 最適化

| 工夫 | 内容 |
| --- | --- |
| 色を、詰める | 色を `RGBA8`（4 バイト）にして、深度と合わせて、**8 バイト**に。**ノード全体で、12 バイト**（次の番号を含む） |
| 層の数の上限 | `kMaxLayers = 8〜16`。それ以上は、**近似**（奥の層を、まとめる） |
| 手前を残して、奥を、まとめる | 最も手前の、数層だけ、正確に。残りは、**WBOIT で、近似**（ハイブリッド、[Hybrid Approaches and Choosing](hybrid.md)） |
| 低解像度で、集める | 煙のような、ぼやけた物は、**画面の半分の解像度**で、集めて、**アップサンプル** |
| 画面を、タイルに分ける | タイルごとに、**フラグメントの、上限を、決める** |

## DirectX 11 での、リソース

PPLL には、**`RWByteAddressBuffer`** と **`RWStructuredBuffer`**（**UAV**）を、**ピクセル シェーダーから、書き込む**必要があります。DirectX 11 では、**ピクセル シェーダーでの、UAV の、使用**が、できます（`OMSetRenderTargetsAndUnorderedAccessViews`）。

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
    **リストの長さに上限**を設け、**超えた分は破棄**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **断片を記録して、最後に並べ替える**
    - [x] **正確だが、メモリを食う**

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
