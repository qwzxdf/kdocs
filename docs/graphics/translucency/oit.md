---
title: OIT（順序非依存の半透明）
tags:
  - 描画
---

# OIT（順序非依存の半透明）

[ブレンドとソート](blending-sorting.md)で見たように、**半透明は、描く順番で結果が変わり、ソートには限界**があります（**交差・自己重なり・大量のパーティクル**）。**OIT**（Order-Independent Transparency、順序非依存の半透明）は、**描く順番に関係なく、正しい（または、それらしい）半透明の合成**を行う手法の総称です。<strong>正確だが重い方式（Depth Peeling・Per-Pixel Linked List）</strong>から、<strong>近似だが軽い方式（Weighted Blended OIT）</strong>、**確率的な方式**まで、**精度とコストのトレードオフ**があります。

!!! tip "ポイント"
    - OIT ＝ <strong>描画順に関係なく、半透明を合成</strong>する手法。<strong>ソート不要</strong>。
    - <strong>Depth Peeling</strong>：<strong>層を 1 枚ずつ剥がして</strong>描く。<strong>正確・重い</strong>（層の数だけパス）。
    - <strong>Per-Pixel Linked List（PPLL）</strong>：<strong>画素ごとにフラグメントを連結リストで保存</strong>し、<strong>最後に並べ替えて合成</strong>。<strong>正確・メモリが重い</strong>。
    - <strong>Weighted Blended OIT</strong>：<strong>深度に応じた重みで、順序なしに平均</strong>。<strong>近似・軽い</strong>（<strong>2 枚のレンダー ターゲット</strong>）。
    - <strong>確率的透明（Stochastic Transparency）</strong>：<strong>アルファを確率として、ノイズで合成</strong>。<strong>TAA で滑らかに</strong>。
    - 実用では、<strong>Weighted Blended</strong>（軽い）か、<strong>上位数層だけ正確に（Hybrid）</strong>が多い。

## 問題の整理

**画素ごとに、複数の半透明の層が重なる**場合、**正しい色は、奥から手前の順に合成した結果**です。

<div class="formula">C = C₁α₁ + (1−α₁)(C₂α₂ + (1−α₂)(C₃α₃ + …))　（1 が最も手前）</div>

**この式は、層の順序に依存**します。**OIT は、「層の順序」を知らなくても、この結果を近似または再現**します。

| 方式 | 順序の扱い | 精度 | コスト | メモリ |
| --- | --- | --- | --- | --- |
| <strong>ソート（従来）</strong> | **オブジェクト単位で並べる** | 交差で破綻 | 小 | 小 |
| **Depth Peeling** | **深度を使って、1 層ずつ取り出す** | **正確** | **N 回の描画**（N 層） | 中（N 枚） |
| **PPLL** | **全層を保存して、最後に並べる** | **正確** | <strong>中（ソートが重い）</strong> | **大**（画素 × 層数） |
| **Weighted Blended** | **順序を無視し、重みで近似** | **近似** | **小**（1 パス） | 小（2 枚） |
| **確率的** | **アルファを確率にして、TAA で平均** | 収束すれば正確 | 小〜中 | 小 |

## Depth Peeling

<strong>「最も手前の層」を、深度テストで取り出し、次に「その次の層」を取り出し…と、層を剥がしていく</strong>方法です。

| 手順 | 内容 |
| --- | --- |
| **① 1 枚目** | **通常の深度テスト**で、**最も手前の半透明の層**を、**画像 1 に描く**。**深度 1 を保存** |
| **② 2 枚目** | **深度 1 より奥の最も手前**を、**画像 2 に描く**（**前の深度より手前のフラグメントは、捨てる**） |
| **③ N 枚目まで繰り返す** | **層の数だけ、描画を繰り返す** |
| **④ 合成** | **奥の層から手前へ**、**N 枚の画像を重ねる** |

```hlsl
float4 PSMain(VsOutput input) : SV_Target {
  float previous_depth = previous_depth_texture.Load(int3(input.position.xy, 0)).r;
  clip(input.position.z - previous_depth - kEpsilon);
  return Shade(input);
}
```

| 点 | 説明 |
| --- | --- |
| **`clip(z - previous_depth - ε)`** | **前の層と同じか手前**の**フラグメント**を**捨てる** |
| **層の数** | **4 層で、多くのシーンは足りる**が、**足りない画素は、欠ける** |
| **コスト** | **N 回の描画**（**シーン全体の半透明ジオメトリを、N 回流す**） |
| **派生** | **Dual Depth Peeling**（**手前と奥を、同時に剥がす**：パスが半分） |

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

## Weighted Blended OIT

**順序を無視**して、**深度に応じた「重み」を付けた加重平均**で**合成**する、**近似手法**です（**McGuire と Bavoil、2013**）。**1 パスで描け、レンダー ターゲット 2 枚だけ**なので、**軽く**、**ゲームで実用的**です。

### 考え方

**手前の物ほど、重みを大きく**して、**平均**します。**順序を知らなくても、「手前らしさ」を深度から推定**して、**近似的な順序づけ**を得ます。

<div class="formula">C = Σ(Cᵢ · αᵢ · wᵢ) / Σ(αᵢ · wᵢ)　、　α_total = 1 − Π(1 − αᵢ)</div>

| 記号 | 意味 |
| --- | --- |
| **wᵢ** | **層 i の重み**（**深度が小さい＝手前ほど大きい**） |
| <strong>Σ(Cᵢ αᵢ wᵢ)</strong> | **重み付きの色の合計**（**アキュムレーション**） |
| <strong>Π(1 − αᵢ)</strong> | **全層の透過率の積**（<strong>リビール（背景の見える割合）</strong>） |

### 2 枚のレンダー ターゲット

| ターゲット | フォーマット | 内容 | ブレンド |
| --- | --- | --- | --- |
| **アキュムレーション** | `R16G16B16A16_FLOAT` | **`(Cᵢ·αᵢ·wᵢ, αᵢ·wᵢ)`** を**加算** | **ONE / ONE**（加算） |
| **リビール** | `R8_UNORM` | **`αᵢ`** を**透過率として乗算** | **ZERO / INV_SRC_COLOR**（`(1 − αᵢ)` を掛ける） |

```hlsl
struct PsOutput {
  float4 accumulation : SV_Target0;
  float reveal : SV_Target1;
};

PsOutput PSWeighted(VsOutput input) {
  float4 color = Shade(input);
  float z = input.position.z;
  float weight = max(min(1.0, max(max(color.r, color.g), color.b) * color.a), color.a) *
                 clamp(0.03 / (1e-5 + pow(z / 200.0, 4.0)), 1e-2, 3e3);

  PsOutput output;
  output.accumulation = float4(color.rgb * color.a, color.a) * weight;
  output.reveal = color.a;
  return output;
}
```

| 点 | 説明 |
| --- | --- |
| **`weight`** | **McGuire らの、深度に基づく重み関数**。**手前（z 小）ほど大きい** |
| **`output.accumulation`** | **`(RGB·α·w, α·w)`**。**加算ブレンド**で**累積** |
| **`output.reveal`** | **`α`**。**乗算ブレンド**で、**`(1 − α)` の積**が**残る** |

### 合成

```hlsl
float4 PSComposite(VsOutput input) : SV_Target {
  float4 accum = accumulation_texture.Load(int3(input.position.xy, 0));
  float reveal = reveal_texture.Load(int3(input.position.xy, 0)).r;
  if (reveal >= 0.999) discard;
  float3 average_color = accum.rgb / max(accum.a, 1e-5);
  return float4(average_color, 1.0 - reveal);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`reveal`（背景の見える割合）</strong> | **1 なら、半透明が何もない**（**描かずに捨てる**） |
| **`average_color`** | **重み付き平均の色** |
| **出力アルファ `1 − reveal`** | **半透明全体の、不透明度**。**通常のアルファ ブレンドで、背景に重ねる** |

| 利点 | 欠点 |
| --- | --- |
| **1 パス・軽い**（**2 枚の RT**） | **近似**（**同じ色の層が多いと、順序が反映されない**） |
| **ソート不要** | **色が違う層の重なりで、順序が違う**（**手前の赤と奥の青が、混ざって見える**） |
| **パーティクル・草・髪などの大量の重なりに強い** | **重み関数の調整**が必要（**シーンの深度範囲**） |

## 確率的透明

<strong>アルファを「そのフラグメントが残る確率」</strong>と考え、**画素ごとのランダムな値と比べて、残すか捨てるか**を決めます（[アルファ テストのハッシュド アルファ](alpha-test.md)と同じ発想）。**不透明として深度に書ける**ので、**ソート不要**で、<strong>TAA（時間平均）</strong>で**滑らかな半透明**に**収束**します。

| 利点 | 欠点 |
| --- | --- |
| **ソート不要・深度が書ける**（**DOF・SSAO などと相性が良い**） | **ノイズ**（**TAA・デノイズが必須**） |
| **正確な期待値に収束** | **1 フレームでは粗い** |
| **実装が簡単** | **アルファが小さいと、収束が遅い** |

**髪・葉**など、**細かく重なる**物には**有効**です。

## ハイブリッド

**実用では、正確な方式と、軽い方式を、組み合わせ**ます。

| 方式 | 内容 |
| --- | --- |
| <strong>上位 N 層だけ正確（Hybrid）</strong> | **手前の数層は、PPLL または Peeling で正確**に、**残りは Weighted Blended** |
| **重要な物だけ OIT** | **ガラス・髪など**は OIT、<strong>パーティクルは、加算ブレンド（順序不要）</strong> |
| **距離で切り替え** | **近くは正確、遠くは近似** |

## 方式の選び方

| 状況 | おすすめ |
| --- | --- |
| **パーティクルが大量・加算で済む** | <strong>加算ブレンド（OIT 不要）</strong> |
| **ガラス・水が少数** | <strong>ソート ＋ 2 パス（前面・背面）</strong> |
| **髪・草など、細かい重なり** | **ハッシュド アルファ ＋ TAA**・**Weighted Blended** |
| <strong>精度が重要（CAD・可視化）</strong> | **PPLL・Depth Peeling** |
| **ゲームで、広く使える軽い OIT** | **Weighted Blended OIT** |

## よくあるミス

??? failure "PPLL で、ノード バッファの上限を決めず、超えて壊れる"
    **`kMaxNodes` を超えたら、書かない**。**画面解像度 × 想定層数**で確保。

??? failure "PPLL の収集パスで、`[earlydepthstencil]` を付けず、隠れた物もノードに積む"
    **深度テストを、シェーダーの前に**行う。

??? failure "Weighted Blended で、リビールを加算ブレンドにして、おかしくなる"
    <strong>リビールは `ZERO / INV_SRC_COLOR`（乗算）</strong>、**アキュムレーションは加算**。

??? failure "Weighted Blended の重みが、シーンの深度範囲に合わず、手前と奥が区別されない"
    **ニア・ファーに合わせて、重み関数の係数を調整**する。

??? failure "OIT で描いた半透明に、DOF や SSAO がうまくかからない"
    **半透明は、深度を持たない**ので、**不透明のみに掛ける**、または**確率的な方式で深度を書く**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] OIT ＝ <strong>描画順に関係なく、半透明を合成</strong>する手法。<strong>ソート不要</strong>
    - [x] <strong>Depth Peeling</strong> ＝ <strong>層を 1 枚ずつ剥がす</strong>（正確・N 回描画）。<strong>PPLL</strong> ＝ <strong>画素ごとにリスト保存→ソート→合成</strong>（正確・メモリ大）
    - [x] <strong>Weighted Blended</strong> ＝ <strong>深度の重みで平均</strong>（近似・1 パス・RT 2 枚）。<strong>アキュムレーションは加算、リビールは乗算</strong>
    - [x] <strong>確率的透明</strong> ＝ <strong>アルファを確率にして、TAA で収束</strong>
    - [x] 実用は<strong>加算ブレンドで済ませる・Weighted Blended・上位層だけ正確</strong>などの<strong>組み合わせ</strong>

## 参考

- McGuire, Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Yang et al., "Real-Time Concurrent Linked List Construction on the GPU"（EGSR 2010）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001、Depth Peeling）
- Enderton et al., "Stochastic Transparency"（I3D 2010）
- Wyman, "Exploring and Expanding the Continuum of OIT Algorithms"（HPG 2016）

## 関連ページ

- [半透明](index.md)
- [ブレンドとソート](blending-sorting.md)
- [アルファ テスト](alpha-test.md)
- [アンチエイリアシング（TAA）](../postprocess/antialiasing/index.md)
