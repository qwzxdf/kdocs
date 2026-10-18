---
title: Stochastic Transparency
tags:
  - 描画
---

# Stochastic Transparency

**確率的透明は、アルファ値に応じて、画素をランダムに捨て、複数フレームやサンプルで平均する**ことで、**半透明を表す手法**です。**ソート不要で、深度も書けます**が、**ノイズが出るので、TAA が前提**です。このページでは、**確率的透明の仕組み**を説明します。

!!! tip "ポイント"
    - **アルファ値の確率で、画素を残す・捨てる**。
    - **ソート不要・深度も書ける**。
    - **TAA や複数サンプルで、平均してなめらかに**。
    - **ノイズが出る**。

## 確率的透明
<strong>アルファを「そのフラグメントが残る確率」</strong>と考え、**画素ごとのランダムな値と比べて、残すか捨てるか**を決めます（[アルファ テストのハッシュド アルファ](../alpha-test/index.md)と同じ発想）。**不透明として深度に書ける**ので、**ソート不要**で、<strong>TAA（時間平均）</strong>で**滑らかな半透明**に**収束**します。

確率的透明の利点は、ソート不要で深度が書けること（DOF や SSAO などと相性が良い）、正確な期待値に収束すること、実装が簡単なことです。欠点は、ノイズが出て TAA やデノイズが必須なこと、1 フレームでは粗いこと、アルファが小さいと収束が遅いことです。

原典は、Enderton らの "Stochastic Transparency"（I3D 2010）です。

**髪・葉**など、**細かく重なる**物には**有効**です。

<!-- fig:stochastic-alpha:begin -->

<svg class="fig illust motion" data-fig="stochastic-alpha" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-stochastic-alpha" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">確率的透明: アルファを、塗るサンプルの割合に置き換える</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><rect x="190" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="244" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="298" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="352" y="100" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="406" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="460" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="514" y="100" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="568" y="100" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="170" y="130" text-anchor="end" style="font-size:14px;font-weight:700;fill:#1f2937">α = 0.25</text>
<text x="640" y="130" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">2 / 8</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/><rect x="190" y="185" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="244" y="185" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="298" y="185" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="352" y="185" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="406" y="185" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="460" y="185" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="514" y="185" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="568" y="185" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="170" y="215" text-anchor="end" style="font-size:14px;font-weight:700;fill:#1f2937">α = 0.50</text>
<text x="640" y="215" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">4 / 8</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000" values="0;0;1;1"/><rect x="190" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="244" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="298" y="270" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="352" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="406" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="460" y="270" width="48" height="48" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="514" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="568" y="270" width="48" height="48" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5"/>
<text x="170" y="300" text-anchor="end" style="font-size:14px;font-weight:700;fill:#1f2937">α = 0.75</text>
<text x="640" y="300" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">6 / 8</text>
</g>
<text x="190" y="80" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 画素の 8 個のサンプル（青 = 描く）</text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">半透明の面を、サンプルごとに 描く / 描かない で決める<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">α = 0.25: 8 個のうち 2 個だけ描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">α = 0.5: 4 個<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">α = 0.75: 6 個。平均すると α の割合で塗られる(並べ替え不要、代わりにノイズ)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:stochastic-alpha:end -->

## 考え方：確率で、描く

**確率的透明**（Stochastic Transparency、Enderton ら、2010）は、**半透明を、確率的な、アルファ テスト**に、置き換えます。**アルファが、0.3** なら、**30% の確率で、描き、70% の確率で、捨てます**。**深度を書き込み**、**ソートも不要**になります。**1 画素を、複数の、サンプルで、描く**（MSAA の、サンプルを使う）と、**サンプルごとに、違う結果**になり、**平均すると、半透明**に、見えます。

```text
アルファ 0.3 の、半透明の物:
  サンプル 1: 描く     （確率 30%）
  サンプル 2: 捨てる
  サンプル 3: 捨てる
  サンプル 4: 描く
  ↓ 平均（リゾルブ）
  半透明な色（約 30% の濃さ）
```

[Hashed Alpha](../alpha-test/hashed-alpha.md) と、**同じ、考え方**を、**複数のサンプル**に、拡張した、手法です。

## 基本の、実装

MSAA の、**カバレッジ**（どのサンプルを、描くか）を、**アルファから、作ります**。

```hlsl
// ピクセル シェーダーが、SV_Coverage を出力して、描くサンプルを、決める。
struct PSOut {
  float4 color : SV_Target;
  uint coverage : SV_Coverage;
};

PSOut main(PSInput input) {
  float4 c = ShadeFragment(input);

  // アルファに応じて、4 つのサンプルのうち、何個を描くか（ランダムに、選ぶ）
  uint mask = 0;
  [unroll] for (uint s = 0; s < 4; ++s) {
    // サンプルごとに、違う乱数（画素の位置と、サンプル番号から）
    float r = Hash(input.position.xy, s);
    if (c.a > r) mask |= (1u << s);
  }

  PSOut o;
  o.color = float4(c.rgb, 1.0);       // 色は、そのまま（アルファは、使わない）
  o.coverage = mask;
  return o;
}
```

| 項目 | 内容 |
| --- | --- |
| 深度テスト | **有効**。**深度の書き込みも、有効**（描いた、サンプルの深度が、残る） |
| ブレンド | **不要**（不透明として、描く） |
| `SV_Coverage` | **どのサンプルを、描くか**を、シェーダーが、決める |

## 正しい結果にならない、理由

この方法は、**サンプルごとに、深度を、書きます**。サンプルに、**最も手前の、描かれた、フラグメントの、色**だけが、残ります。**奥のフラグメントは、手前のフラグメントに、隠されて**、**消えます**。**手前の物が、描かれた、サンプルでは、奥の物は、見えません**。

結果、**手前と奥の、両方が、混ざった色**には、**ならず**、**サンプルごとに、どちらか 1 つ**が、見えます。**平均すると、確率的には、正しい**（手前が、アルファの確率で、見え、残りの確率で、奥が見える）ので、**期待値は、正しい**です。

**問題**は、**サンプル数が、少ない**ことです。4 サンプルでは、**ノイズが、非常に大きく**なります。

## ノイズを、減らす

Enderton らの、論文は、**ノイズを、減らす**、**工夫**を、いくつか、提案しています。

| 工夫 | 内容 |
| --- | --- |
| **サンプル数を、増やす** | 8x、16x、さらに、**サブピクセル**で、多くのサンプルを使う。**メモリと、帯域が、増える** |
| **層ごとの、層化** | アルファに応じた、**カバレッジの、パターンを、均等に、分ける**（ランダムでなく、**層化された**パターン）。ノイズが、減る |
| **ブルー ノイズ** | サンプルの、選択に、**ブルー ノイズ**を使う。粒が、均一で、目立たない |
| **TAA** | フレームをまたいで、**平均**する。ノイズが、**時間方向に、ならされる** |

## 論文の、**もう 1 つ**の、方法：色の、正しい復元

論文は、**確率的な、深度**だけでなく、**各サンプルの、深度の、順序**から、**色を、正しく、復元**する、拡張も、述べています。

| 段階 | 内容 |
| --- | --- |
| ① 不透明度の、推定 | 複数のサンプルの、深度を、比べて、**各フラグメントの、手前に、どれだけの、不透明度が、あるか**を、推定する |
| ② 色の、積算 | 手前の、不透明度で、重みを付けて、**色を、足す** |

実装は、複雑で、**メモリも、帯域も、必要**です。ゲームでは、あまり、使われず、**TAA と、組み合わせた、簡易版**（ハッシュ アルファ）が、使われます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **ソート不要**。**深度を、書き込める**。**ライティングが、1 回**（半透明の色を、そのまま、描く） |
| 長所 | **大量の、重なり**（髪、煙）でも、**コストは、ほぼ、一定** |
| 長所 | **TAA と、相性が、良い**（ノイズを、時間方向に、平均できる） |
| 短所 | **ノイズ**（ざらつき）。TAA がないと、**目立つ** |
| 短所 | **MSAA の、サンプル数**に、品質が、依存する。メモリ、帯域が、大きい |
| 短所 | **不透明に近い**半透明は、**ノイズが、小さい**が、**透明に近い**（アルファ 0.1）では、**ノイズが、大きい** |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| **TAA を、使っている** + 半透明の**髪、葉、煙** | **よい選択**（ハッシュ アルファ、または、確率的透明） |
| TAA がない | ノイズが、目立つ。**WBOIT** などを検討（[WBOIT](wboit.md)） |
| ガラス（正確な、屈折、反射が、必要） | **向かない**（ノイズ、前後の、混ざり） |

## よくあるミス

??? failure "ノイズが残る"
    **TAA** や **サンプル数を増やして**、**平均**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ランダムに捨てて、平均する**
    - [x] **TAA が前提**

## 参考

- Enderton, Sintorn, Shirley, Luebke, "Stochastic Transparency", Symposium on Interactive 3D Graphics and Games 2010
- Wyman, "Exploring and Expanding the Continuum of OIT Algorithms", High-Performance Graphics 2016
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Microsoft Learn, "SV_Coverage semantic"（HLSL）

## 関連ページ

- [OIT](index.md)
- [Hashed Alpha](../alpha-test/hashed-alpha.md)
