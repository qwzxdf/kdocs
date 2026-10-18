---
title: Shadow Volumes
tags:
  - 描画
---

# Shadow Volumes

**シャドウ マップ**は、<strong>画像（ラスタ）</strong>に基づくので**解像度・エイリアシング**の限界があります。**シャドウ ボリューム**（Shadow Volumes、Crow 1977）は、<strong>遮蔽物のシルエットを光と反対方向に押し出した「影の体積」</strong>を**ジオメトリ**として作り、**画素がその体積の内側にあるか**を、**ステンシル バッファ**で数えて判定する方式です。**ピクセル単位で正確**で**解像度の限界・バイアスがありません**。**Doom 3**（2004）で使われました。**現在は主流ではありません**が、**原理**は**ステンシルの使い方・シルエットの考え方**として、学ぶ価値があります。

!!! tip "ポイント"
    - <strong>シルエット辺を光の反対方向に押し出して、影の体積（ボリューム）</strong>を作る。
    - 画素が<strong>体積の内側 ＝ 影</strong>。<strong>ステンシルで「入った回数 − 出た回数」</strong>を数える。
    - <strong>Z-Pass</strong>：簡単だが<strong>カメラがボリュームの内側</strong>にあると<strong>破綻</strong>。
    - <strong>Z-Fail（Carmack's Reverse）</strong>：<strong>カメラの位置を問わず正しい</strong>。<strong>キャップ（蓋）</strong>が必要。
    - <strong>ピクセル単位で正確</strong>（解像度・バイアス・エイリアシングなし）。ただし<strong>常にハード エッジ</strong>。
    - 欠点：<strong>フィル レートが重い</strong>。<strong>ジオメトリが複雑だと体積が増える</strong>。<strong>半影・アルファ・植物が苦手</strong>。

## 原理：影の体積

**光源**から見て、<strong>遮蔽物の「シルエット」</strong>（光に面した面と背いた面の境界の辺）を、**光と反対の方向に無限遠まで押し出し**ます。**押し出した面で囲まれた領域**が、**影の体積**です。**この体積に入った点は、光から隠れている**ので**影**です。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="シャドウ ボリューム">
<text x="20" y="24" class="fig-title">シルエットを光と反対方向へ押し出した領域が、影の体積</text>
<circle cx="80" cy="130" r="10" fill="rgba(229,170,40,0.9)" stroke="currentColor" stroke-width="2"/><text x="60" y="160" style="font-size:12px">光源</text>
<rect x="220" y="100" width="40" height="60" fill="rgba(150,150,150,0.8)" stroke="currentColor" stroke-width="2"/><text x="200" y="94" style="font-size:12px">遮蔽物</text>
<polygon points="260,100 740,40 740,220 260,160" fill="rgba(60,60,60,0.35)" stroke="currentColor" stroke-dasharray="4 3"/>
<text x="460" y="136" style="font-size:13px;font-weight:700">影の体積（内側 ＝ 影）</text>
<line x1="80" y1="130" x2="740" y2="40" stroke="currentColor" stroke-dasharray="2 4" opacity="0.4"/><line x1="80" y1="130" x2="740" y2="220" stroke="currentColor" stroke-dasharray="2 4" opacity="0.4"/>
<text x="260" y="240" style="font-size:12px">シルエットの辺 → 光と反対方向へ延長して、面（側面）を作る</text>
</svg>

### シルエット辺

**三角形が光に面しているか**は、**法線と光への方向の内積**で判定します。**光に面した三角形と背いた三角形が辺を共有している**とき、**その辺はシルエット**です。

判定の内容です。面が光に面するのは、`dot(N, L) > 0` のときです（`L` は面から光への向き）。シルエット辺は、隣り合う 2 つの三角形の一方が光に面し、他方が背いている辺です。ボリュームの側面は、シルエット辺を光と反対方向へ押し出した四角形になります。

**閉じたメッシュ**（穴のない 2-多様体）が、**前提**です。**穴・T 字接合**があると**ボリュームが閉じず**、**破綻**します。

<!-- fig:shadow-volume-stencil:begin -->

<svg class="fig illust motion" data-fig="shadow-volume-stencil" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-shadow-volume-stencil" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ステンシル:視線が影の体積に入ったら +1、出たら −1。残りが 1 なら影</text>
<rect x="30" y="330" width="720" height="14" fill="#d6c7a1"/>
<polygon points="300,150 350,150 560,330 400,330" fill="#1e293b" fill-opacity="0.25" stroke="#475569" stroke-width="2" stroke-dasharray="6 4"/>
<rect x="290" y="135" width="70" height="18" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<circle cx="330" cy="60" r="13" fill="#e5aa28"/>
<text x="350" y="64" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">光</text>
<circle cx="50" cy="130" r="8" fill="#2563eb"/>
<text x="44" y="116" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">カメラ</text>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.1652;0.1655;1.0000" values="0;0;1;1;0;0"/><line x1="50" y1="130" x2="180" y2="330" stroke="#2563eb" stroke-width="2.5"/>
<circle cx="180" cy="330" r="7" fill="#2ea043"/>
<text x="400" y="380" text-anchor="middle" style="font-size:17px;font-weight:700;fill:#2ea043">この画素:ステンシル = 0 → 光が当たる（0）</text>
</g>
<rect x="140" y="344" width="80" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;1.0000" values="0;0;1;1"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;0.2618;0.2621;1.0000" values="0;0;1;1;0;0"/><line x1="50" y1="130" x2="260" y2="330" stroke="#2563eb" stroke-width="2.5"/>
<circle cx="260" cy="330" r="7" fill="#2ea043"/>
<text x="400" y="380" text-anchor="middle" style="font-size:17px;font-weight:700;fill:#2ea043">この画素:ステンシル = 0 → 光が当たる（0）</text>
</g>
<rect x="220" y="344" width="80" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2618;0.2621;1.0000" values="0;0;1;1"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2618;0.2621;0.3583;0.3586;1.0000" values="0;0;1;1;0;0"/><line x1="50" y1="130" x2="340" y2="330" stroke="#2563eb" stroke-width="2.5"/>
<circle cx="340" cy="330" r="7" fill="#2ea043"/>
<text x="400" y="380" text-anchor="middle" style="font-size:17px;font-weight:700;fill:#2ea043">この画素:ステンシル = 0 → 光が当たる（0）</text>
</g>
<rect x="300" y="344" width="80" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3583;0.3586;1.0000" values="0;0;1;1"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3583;0.3586;0.4549;0.4552;1.0000" values="0;0;1;1;0;0"/><line x1="50" y1="130" x2="420" y2="330" stroke="#2563eb" stroke-width="2.5"/>
<circle cx="391.42" cy="314.55" r="9" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="391.42" y="318.55" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">+1</text>
<circle cx="420" cy="330" r="7" fill="#e5484d"/>
<text x="400" y="380" text-anchor="middle" style="font-size:17px;font-weight:700;fill:#e5484d">この画素:ステンシル = 1 → 影（0 でない）</text>
</g>
<rect x="380" y="344" width="80" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4549;0.4552;1.0000" values="0;0;1;1"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4549;0.4552;0.5514;0.5517;1.0000" values="0;0;1;1;0;0"/><line x1="50" y1="130" x2="480" y2="330" stroke="#2563eb" stroke-width="2.5"/>
<circle cx="372.13" cy="279.83" r="9" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="372.13" y="283.83" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">+1</text>
<circle cx="480" cy="330" r="7" fill="#e5484d"/>
<text x="400" y="380" text-anchor="middle" style="font-size:17px;font-weight:700;fill:#e5484d">この画素:ステンシル = 1 → 影（0 でない）</text>
</g>
<rect x="440" y="344" width="80" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5514;0.5517;1.0000" values="0;0;1;1"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5514;0.5517;0.6480;0.6483;1.0000" values="0;0;1;1;0;0"/><line x1="50" y1="130" x2="540" y2="330" stroke="#2563eb" stroke-width="2.5"/>
<circle cx="358.94" cy="256.1" r="9" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="358.94" y="260.1" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">+1</text>
<circle cx="540" cy="330" r="7" fill="#e5484d"/>
<text x="400" y="380" text-anchor="middle" style="font-size:17px;font-weight:700;fill:#e5484d">この画素:ステンシル = 1 → 影（0 でない）</text>
</g>
<rect x="500" y="344" width="80" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6480;0.6483;1.0000" values="0;0;1;1"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6480;0.6483;0.7446;0.7448;1.0000" values="0;0;1;1;0;0"/><line x1="50" y1="130" x2="620" y2="330" stroke="#2563eb" stroke-width="2.5"/>
<circle cx="346.73" cy="234.12" r="9" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="346.73" y="238.12" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">+1</text>
<circle cx="518.42" cy="294.36" r="9" fill="#e5484d" stroke="#ffffff" stroke-width="2"/>
<text x="518.42" y="298.36" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">−1</text>
<circle cx="620" cy="330" r="7" fill="#2ea043"/>
<text x="400" y="380" text-anchor="middle" style="font-size:17px;font-weight:700;fill:#2ea043">この画素:ステンシル = 0 → 光が当たる（0）</text>
</g>
<rect x="580" y="344" width="80" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7446;0.7448;1.0000" values="0;0;1;1"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7446;0.7448;0.8411;0.8414;1.0000" values="0;0;1;1;0;0"/><line x1="50" y1="130" x2="700" y2="330" stroke="#2563eb" stroke-width="2.5"/>
<circle cx="338.14" cy="218.66" r="9" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<text x="338.14" y="222.66" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">+1</text>
<circle cx="481.6" cy="262.8" r="9" fill="#e5484d" stroke="#ffffff" stroke-width="2"/>
<text x="481.6" y="266.8" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff">−1</text>
<circle cx="700" cy="330" r="7" fill="#2ea043"/>
<text x="400" y="380" text-anchor="middle" style="font-size:17px;font-weight:700;fill:#2ea043">この画素:ステンシル = 0 → 光が当たる（0）</text>
</g>
<rect x="660" y="344" width="80" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.8411;0.8414;1.0000" values="0;0;1;1"/></rect>
<text x="40" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">カメラから各画素への視線を、順に見る（緑 +1 = 体積に入る、赤 −1 = 体積から出る）</text>
</svg>

<!-- fig:shadow-volume-stencil:end -->

## ステンシルによる判定

**画素から、カメラへ向かう（またはカメラから画素へ向かう）視線**が**影の体積の面を何回またぐか**を数えます。**体積に入る（前面）と +1、出る（背面）と −1**。**合計が 0 でなければ、体積の内側**＝影です。

### Z-Pass（Depth-Pass）

1. **シーンを通常描画**（**深度**を書く。**光の寄与はまだ加えない**、または**環境光だけ**）。
2. **影の体積の前面**を**深度テストあり・書き込みなし**で描き、**深度テストが通った所**で、**ステンシル +1**。
3. **背面**を同様に描き、**深度テストが通った所**で、**ステンシル −1**。
4. **ステンシルが 0 の画素**に、**光の寄与**を加える（**0 でない画素は、影**）。

Z-Pass の特徴です。考え方は、カメラから画素までの視線が体積に入ってから、出ないまま画素に着けば、画素は体積の中にある、というものです。利点は、簡単でキャップが不要なことです。致命的な欠点は、カメラが影の体積の内側にあると、カウントがずれる（入る側の面がカメラの後ろにある）ことで、影が反転します。

### Z-Fail（Carmack's Reverse）

**カメラが体積の中にあっても正しく**判定する方式です。<strong>視線を画素から「奥」</strong>へ向かって数えます。

1. **背面**を描き、**深度テストが失敗した所**（**面の裏側に隠れた所**）で、**ステンシル +1**。
2. **前面**を描き、**深度テストが失敗した所**で、**ステンシル −1**。
3. **0 でない画素**が、影。

| 項目 | 内容 |
| --- | --- |
| **利点** | **カメラの位置**を**問わない** |
| **必要なもの** | **キャップ**（**体積の光側と遠方側の蓋**）。<strong>遮蔽物自身の光に面した面（光側のキャップ）</strong>と、<strong>無限遠への押し出し（遠側のキャップ）</strong> |
| **遠側のキャップ** | **射影行列の遠クリップ面を無限遠**にする（**無限遠射影**）。**同次座標 w = 0** の頂点で、**無限遠を表す** |
| **欠点** | **キャップを作るコスト**。**遠クリップ面の扱い** |


Z-Fail は、Carmack が 2000 年頃に考案した方法で（"Carmack's Reverse"）、Z-Pass のカメラ内部の問題を解決しました。

Z-Fail は、Carmack が 2000 年頃に考案した方法で（"Carmack's Reverse"）、Z-Pass のカメラ内部の問題を解決しました。

```cpp
D3D11_DEPTH_STENCIL_DESC desc = {};
desc.DepthEnable = TRUE;
desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
desc.DepthFunc = D3D11_COMPARISON_LESS;
desc.StencilEnable = TRUE;
desc.StencilReadMask = 0xFF;
desc.StencilWriteMask = 0xFF;
desc.BackFace.StencilDepthFailOp = D3D11_STENCIL_OP_INCR_SAT;
desc.FrontFace.StencilDepthFailOp = D3D11_STENCIL_OP_DECR_SAT;
desc.FrontFace.StencilFunc = D3D11_COMPARISON_ALWAYS;
desc.BackFace.StencilFunc = D3D11_COMPARISON_ALWAYS;
```

ステート設定の要点です。`DepthWriteMask = ZERO` で、ボリュームは深度に書かず、ステンシルだけを更新します。`StencilDepthFailOp` は、深度テストが失敗したときの動作（Z-Fail）で、背面で +1、前面で −1 とします。カリングなしの両面描画にして、ステンシルの前面・背面の設定を分ければ、1 パスで描けます。

## 光のパス

**ライトごと**に**ステンシルをクリア**し、**影の体積を描いて**ステンシルを更新します。**ステンシルが 0 の画素だけ**に、**そのライトの寄与**を**加算ブレンド**で加えます。

```text
for each light:
  clear stencil
  draw shadow volumes of all casters (stencil update)
  draw lighting where stencil == 0 (additive)
```

**ライトが多い**と**パスが増え**、**重く**なります。

## 利点と欠点

| 利点 | 欠点 |
| --- | --- |
| **ピクセル単位で正確**（解像度・バイアス・エイリアシングなし） | **ハード エッジのみ**（**半影は別の工夫**が必要） |
| **全方向のライト**を**同じ手法**で扱える（キューブ マップ不要） | **フィル レートが重い**（ボリュームの面が画面を大きく覆う） |
| **遠近エイリアシングなし** | **閉じたメッシュ**が必要（穴があると破綻） |
| **ステンシルの活用の良い例** | **アルファ テスト・植物・髪**の影が扱えない |
| | **シルエットの検出**（CPU または GPU）が必要 |
| | **ジオメトリが複雑**だと**ボリュームが爆発** |

## 現在の位置づけ

**シャドウ マップ**が<strong>ハードウェアの進歩（比較サンプラー・PCF・大きなテクスチャ）</strong>で、**品質・柔軟性・コスト**で**上回った**ため、**シャドウ ボリュームは、ほとんど使われなく**なりました。

| 観点 | シャドウ マップ | シャドウ ボリューム |
| --- | --- | --- |
| **ソフト シャドウ** | PCF・PCSS・VSM | **難しい** |
| **アルファ・植物** | **可能** | **困難** |
| **ジオメトリの複雑さ** | **影響が小さい** | **体積が増える** |
| **フィル レート** | **中** | **重い** |
| **精度** | 解像度に依存 | **正確** |

**学ぶ意義**：**ステンシルの活用**（**カウントによる内外判定**）・**シルエットの概念**は、<strong>他の場面（デカール・UI のクリッピング・ボリューム ライト）</strong>にも**応用**できます。

## よくあるミス

??? failure "Z-Pass で、カメラが影の中にあると、影が反転する"
    **Z-Fail** を使います（キャップが必要）。

??? failure "メッシュに穴があり、影のボリュームが閉じずに、影が漏れる"
    **メッシュを閉じた状態**にします（穴・T 字接合を修正）。

??? failure "遠クリップ面で、ボリュームが切れて、影が欠ける"
    **無限遠射影**にします。

??? failure "全ライト・全物体でボリュームを描いて、重い"
    **影響範囲の外・見えない物**を除外します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シャドウ ボリューム ＝ <strong>シルエットを、光と反対へ押し出した「影の体積」</strong>を作り、<strong>ステンシルで内外を判定</strong>
    - [x] <strong>入る面で +1、出る面で −1</strong>。<strong>0 以外なら影</strong>
    - [x] <strong>Z-Pass</strong> は簡単だが<strong>カメラが体積内で破綻</strong>。<strong>Z-Fail（Carmack's Reverse）</strong>は<strong>常に正しいがキャップが必要</strong>
    - [x] <strong>ピクセル単位で正確</strong>だが、<strong>ハード エッジのみ・フィル レートが重い・閉じたメッシュが必要</strong>
    - [x] <strong>現在は、シャドウ マップが主流</strong>。<strong>ステンシルの発想</strong>は応用が効く

## 参考

- Crow, "Shadow Algorithms for Computer Graphics"（SIGGRAPH 1977）
- Heidmann, "Real Shadows, Real Time"（1991）
- Kilgard, "Robust Stencil Shadow Volumes"（NVIDIA、2001）

## 関連ページ

- [Shadows](index.md)
- [Shadow Map Basics](shadow-map-basics/index.md)
- [Ray-Traced Shadows](ray-traced.md)
