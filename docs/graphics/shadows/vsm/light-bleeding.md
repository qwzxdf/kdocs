---
title: 光漏れ
tags:
  - 描画
---

# 光漏れ

**VSM は、複数の物体が重なる影で、本来は影の所に、光が漏れて見えます**。**これが光漏れ（ライト ブリーディング）**で、**VSM の最大の欠点**です。**チェビシェフの不等式は、確率の上限しか与えないので、複雑な分布では、影を薄く評価しすぎる**ためです。このページでは、**光漏れが起きる理由・見え方・簡単な対策（影の割合の再マッピング）**を説明します。

!!! tip "ポイント"
    - **光漏れ ＝ 影の中なのに、光が漏れて明るく見える**。
    - **原因 ＝ 深度の分布が、2 つの山（手前と奥の物体）になる場合、平均と分散だけでは表せない**。
    - **簡単な対策**：**影の割合を、しきい値で再マッピング**（**低い値を 0 に潰す**）。
    - **本格的な対策**：**EVSM・MSM**。

## 弱点：光漏れ（ライト ブリーディング）
VSM は<strong>「分散」と「平均」だけ</strong>しか見ません。**遮蔽物が複数あり、深度が違う**場合、**統計だけでは区別できず**、**影の中に光が漏れた**ように見える部分が出ます。

<svg class="fig illust" viewBox="0 0 780 270" role="img" aria-label="VSM の光漏れ">
<text x="20" y="24" class="fig-title">深度の異なる遮蔽物が重なると、統計だけでは区別できず、影に光が漏れる</text>
<rect x="100" y="60" width="140" height="14" fill="rgba(150,150,150,0.7)" stroke="currentColor" stroke-width="2"/><text x="108" y="54" style="font-size:12px">遮蔽物 A（手前）</text>
<rect x="160" y="110" width="140" height="14" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/><text x="308" y="124" style="font-size:12px">遮蔽物 B（奥）</text>
<line x1="60" y1="230" x2="560" y2="230" stroke="currentColor" stroke-width="4"/><text x="60" y="254" style="font-size:12px">受け手</text>
<rect x="160" y="226" width="80" height="8" fill="#111" opacity="0.8"/><rect x="240" y="226" width="60" height="8" fill="#888" opacity="0.5"/>
<text x="330" y="190" style="font-size:12px;fill:#e5484d;font-weight:700">B の影の領域のうち、A に遮られていない所が、</text>
<text x="330" y="208" style="font-size:12px;fill:#e5484d;font-weight:700">本来より、薄く（明るく）見える ＝ 光漏れ</text>
<text x="400" y="100" style="font-size:12px">原因：A と B の深度の平均・分散だけでは、</text>
<text x="400" y="118" style="font-size:12px">「どちらが、何割か」が、分からない</text>
</svg>

### 対策

| 対策 | 内容 |
| --- | --- |
| <strong>光漏れの低減（リマップ）</strong> | 日向の割合 `p` を、**`(p − a) / (1 − a)`**（`a` は 0.2〜0.5）で、**下側を切り捨てて**引き伸ばす。**薄い漏れを消せる**が**半影の滑らかさが減る** |
| **分散の下限を調整** | `kMinVariance` を大きく |
| **ESM・EVSM・MSM** | 方式を変える（下記） |
| **遮蔽物の深度差を小さく** | シーンの設計（**重なりを少なく**） |

```hlsl
float ReduceLightBleeding(float p_max, float amount) {
  return saturate((p_max - amount) / (1.0 - amount));
}
```

## よくあるミス

??? failure "光漏れを消そうとしきい値を上げすぎて、影の縁が硬くなる"
    **しきい値を段階的に調整**。**EVSM・MSM への切り替えも検討**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **光漏れ ＝ VSM の欠点**。**多重の影で、影が薄くなりすぎる**
    - [x] **簡単な対策はしきい値、本格的には EVSM・MSM**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [VSM と ESM・MSM](index.md)
- [EVSM](evsm.md)
- [MSM](msm.md)
