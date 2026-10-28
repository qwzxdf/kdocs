---
title: Stochastic Transparency
tags:
  - 描画
---

# Stochastic Transparency

<strong>確率的透明はアルファ値に応じて、画素をランダムに捨て複数フレームやサンプルで平均する</strong>ことで、半透明を表す手法です。ソート不要で深度も書けますが、ノイズが出るので TAA が前提です。このページでは確率的透明の仕組みを説明します。

!!! tip "ポイント"
    - アルファ値の確率で、画素を残す・捨てる。
    - ソート不要・深度も書ける。
    - TAA や複数サンプルで、平均してなめらかに。
    - ノイズが出る。

!!! info "このページを読む前に"
    - [Order-Independent Transparency (OIT)](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 確率的透明
<strong>アルファを「そのフラグメントが残る確率」</strong>と考え、画素ごとのランダムな値と比べて、残すか捨てるかを決めます（[アルファ テストのハッシュド アルファ](../alpha-test/index.md)と同じ発想）。不透明として深度に書けるので、ソート不要で TAA（時間平均）で滑らかな半透明に収束します。

確率的透明の利点はソート不要で深度が書けること（DOF や SSAO などと相性が良い）、正確な期待値に収束すること実装が簡単なことです。欠点はノイズが出て TAA やデノイズが必須なこと、1 フレームでは粗いことアルファが小さいと収束が遅いことです。

原典は Enderton らの "Stochastic Transparency"（I3D 2010）です。

髪・葉など 細かく重なる物には有効です。

<!-- fig:stochastic-alpha:begin -->

<svg class="fig illust motion" data-fig="stochastic-alpha" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-stochastic-alpha" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">確率的透明: アルファを塗るサンプルの割合に置き換える</text>
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
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">半透明の面をサンプルごとに 描く / 描かない で決める<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">α = 0.25: 8 個のうち 2 個だけ描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">α = 0.5: 4 個<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">α = 0.75: 6 個。平均すると α の割合で塗られる(並べ替え不要、代わりにノイズ)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:stochastic-alpha:end -->

## 考え方：確率で描く

<strong>確率的透明</strong>（Stochastic Transparency、Enderton ら 2010）は、半透明を確率的なアルファ テストに置き換えます。アルファが 0.3 なら 30% の確率で描き、70% の確率で捨てます。深度を書き込みソートも不要になります。1 画素を複数のサンプルで描く（MSAA の、サンプルを使う）とサンプルごとに、違う結果になり平均すると半透明に見えます。

```text
アルファ 0.3 の、半透明の物:
  サンプル 1: 描く     （確率 30%）
  サンプル 2: 捨てる
  サンプル 3: 捨てる
  サンプル 4: 描く
  ↓ 平均（リゾルブ）
  半透明な色（約 30% の濃さ）
```

[Hashed Alpha](../alpha-test/hashed-alpha.md) と 同じ、考え方を 複数のサンプルに拡張した手法です。

## 基本の実装

MSAA の <strong>カバレッジ</strong>（どのサンプルを描くか）を アルファから作ります。

```hlsl
// ピクセル シェーダーが SV_Coverage を出力して、描くサンプルを決める。
struct PSOut {
  float4 color : SV_Target;
  uint coverage : SV_Coverage;
};

PSOut main(PSInput input) {
  float4 c = ShadeFragment(input);

  // アルファに応じて、4 つのサンプルのうち、何個を描くか（ランダムに選ぶ）
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
| 深度テスト | 有効。深度の書き込みも有効（描いた、サンプルの深度が残る） |
| ブレンド | 不要（不透明として、描く） |
| `SV_Coverage` | どのサンプルを描くかをシェーダーが決める |

## 正しい結果にならない理由

この方法は <strong>サンプルごとに深度を書きます</strong>。サンプルに 最も手前の描かれた、フラグメントの色だけが残ります。奥のフラグメントは手前のフラグメントに隠されて消えます。手前の物が描かれたサンプルでは、奥の物は見えません。

結果、手前と奥の両方が混ざった色には、ならず、サンプルごとにどちらか 1 つが、見えます。平均すると確率的には正しい（手前がアルファの確率で見え残りの確率で、奥が見える）ので期待値は正しいです。

問題は サンプル数が少ないことです。4 サンプルではノイズが大きくなります。

## ノイズを減らす

Enderton らの論文は、<strong>ノイズを減らす</strong>、工夫をいくつか提案しています。

| 工夫 | 内容 |
| --- | --- |
| サンプル数を増やす | 8x、16x、さらにサブピクセルで多くのサンプルを使う。メモリと帯域が増える |
| 層ごとの層化 | アルファに応じた、カバレッジのパターンを均等に分ける（ランダムでなく層化されたパターン）。ノイズが減る |
| ブルー ノイズ | サンプルの選択にブルー ノイズを使う。粒が均一で目立たない |
| TAA | フレームをまたいで、平均する。ノイズが時間方向にならされる |

## 論文のもう 1 つの方法：色の、正しい復元

論文は <strong>確率的な深度</strong>だけでなく、各サンプルの深度の順序から色を正しく、復元する拡張も述べています。

| 段階 | 内容 |
| --- | --- |
| ① 不透明度の推定 | 複数のサンプルの深度を比べて、各フラグメントの手前にどれだけの、不透明度があるかを推定する |
| ② 色の積算 | 手前の、不透明度で重みを付けて色を足す |

実装は複雑で メモリも帯域も、必要です。ゲームではあまり使われず TAA と、組み合わせた簡易版（ハッシュ アルファ）が使われます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | ソート不要。深度を書き込める。ライティングが 1 回（半透明の色をそのまま描く） |
| 長所 | 大量の重なり（髪、煙）でもコストはほぼ一定 |
| 長所 | TAA と相性が良い（ノイズを時間方向に平均できる） |
| 短所 | ノイズ（ざらつき）。TAA がないと目立つ |
| 短所 | MSAA のサンプル数に品質が依存する。メモリ、帯域が大きい |
| 短所 | 不透明に近い半透明は、ノイズが小さいが透明に近い（アルファ 0.1）では、ノイズが大きい |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| TAA を使っている + 半透明の髪、葉、煙 | よい選択（ハッシュ アルファ、または確率的透明） |
| TAA がない | ノイズが目立つ。WBOIT などを検討（[WBOIT](wboit.md)） |
| ガラス（正確な屈折、反射が必要） | 向かない（ノイズ、前後の混ざり） |

## よくあるミス

??? failure "ノイズが残る"
    <strong>TAA</strong> や サンプル数を増やして、平均する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ランダムに捨てて、平均する
    - [x] TAA が前提

## 参考

- Enderton, Sintorn, Shirley, Luebke, "Stochastic Transparency", Symposium on Interactive 3D Graphics and Games 2010
- Wyman, "Exploring and Expanding the Continuum of OIT Algorithms", High-Performance Graphics 2016
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Microsoft Learn, "SV_Coverage semantic"（HLSL）

## 関連ページ

- [OIT](index.md)
- [Hashed Alpha](../alpha-test/hashed-alpha.md)
