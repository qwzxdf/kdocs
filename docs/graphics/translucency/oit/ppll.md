---
title: Per-Pixel Linked List（PPLL）
tags:
  - 描画
---

# Per-Pixel Linked List（PPLL）

**PPLL は、画素ごとに、重なった半透明の断片をリストに記録し、最後に深度で並べ替えて、ブレンドする手法**です。**正確ですが、メモリと並べ替えのコストが大きい**です。このページでは、**PPLL の仕組みと実装**を説明します。

!!! tip "ポイント"
    - **描画時：断片（色・深度）を、画素ごとのリストへ追加**。
    - **UAV と、アトミック操作**を使う。
    - **最後に、画素ごとに深度で並べ替えて、ブレンド**。
    - **重なりが多いと、メモリと時間が膨らむ**。

## Per-Pixel Linked List（PPLL）
**画素ごとに、重なったフラグメントを「連結リスト」で全部保存**し、**最後に、画素ごとに、深度順に並べて合成**します。**DirectX 11 の UAV とアトミック操作**で**実現**できます（**Yang らの手法**）。

### データ構造

| バッファ | 内容 |
| --- | --- |
| **ヘッド ポインタ バッファ**（`RWTexture2D<uint>`） | **画素ごとの、リストの先頭**（番号） |
| **ノード バッファ**（`RWStructuredBuffer<Node>`） | **フラグメントの色・深度・次のノード番号** |
| **カウンタ** | **次に使えるノード番号**（`InterlockedAdd`） |

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

| 点 | 説明 |
| --- | --- |
| **`kMaxLayers`** | **1 画素で扱う最大層数**（**ローカル配列の大きさ**。**16〜32**）。**多いほどレジスタを消費** |
| **挿入ソート** | **層数が少ないので、単純な挿入ソート**で**十分** |
| <strong>降順（奥から）</strong> | **深度の大きい（遠い）順**に並べて、**奥から手前へ合成** |

| 利点 | 欠点 |
| --- | --- |
| **正確**（ソート済みで合成） | **メモリが大きい**（4K で数百 MB になりうる） |
| **層数に上限がない**（ノード バッファの許す限り） | **画素ごとのソートが重い**（層が多いと極端に遅い） |
| **ライティング済みの色を保存**するので、**後処理が簡単** | **オーバーフロー**時に、**フラグメントが欠ける** |

## よくあるミス

??? failure "重なりが多い所で、リストがあふれる"
    **リストの長さに上限**を設け、**超えた分は破棄**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **断片を記録して、最後に並べ替える**
    - [x] **正確だが、メモリを食う**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [OIT](index.md)
- [Depth Peeling](depth-peeling.md)
- [ハイブリッド](hybrid.md)
