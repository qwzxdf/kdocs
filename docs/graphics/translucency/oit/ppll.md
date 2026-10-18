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

### Data Structure {#データ構造}

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

### Composite Pass {#合成パス}

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

## Common Mistakes {#よくあるミス}

??? failure "重なりが多い所で、リストがあふれる"
    **リストの長さに上限**を設け、**超えた分は破棄**する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **断片を記録して、最後に並べ替える**
    - [x] **正確だが、メモリを食う**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [OIT](index.md)
- [Depth Peeling](depth-peeling.md)
- [ハイブリッド](hybrid.md)
