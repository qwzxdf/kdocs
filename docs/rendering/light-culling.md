---
title: Tiled と Clustered
tags:
  - 最適化
  - 3Dゲーム
---

# Tiled と Clustered

[Forward と Deferred](forward-deferred.md)で見たように**ライトが多い**と<strong>「ピクセル × 全ライト」</strong>の計算が**重く**なります。**ほとんどのライトは、その場所のピクセルに届かない**（遠い）のに**全部を計算**しているからです。<strong>画面を小さな領域に分けて、「その領域に影響するライトだけ」</strong>のリストを**先に作る**——これが**ライト カリング**です。**Tiled**（画面を、2 次元のタイルに分ける）、**Clustered**（**奥行き方向も分けて、3 次元**）の、**2 つの方式**を、**Forward と Deferred**の、**それぞれに**適用できます。このページは**何が改善するのか**、<strong>目的（計算と帯域）</strong>、**仕組み**、**使い分け**を説明します。

!!! tip "ポイント"
    - 目的：<strong>ピクセルごとに、「近くにあるライトだけ」を、計算</strong>する（<strong>計算量の削減</strong>）。<strong>G-Buffer を、1 回だけ読む</strong>（<strong>帯域の削減</strong>）。
    - <strong>Tiled</strong>：<strong>画面を、16×16 ピクセルなどの、タイルに分け</strong>、<strong>タイルごとに影響するライトのリスト</strong>を作る（<strong>コンピュート シェーダー</strong>）。
    - <strong>タイルの奥行きの範囲（最小・最大の深度）</strong>で、さらに絞る。<strong>弱点：奥行きが大きく変わるタイル（物体の縁）</strong>で、<strong>ライトが多く残る</strong>。
    - <strong>Clustered</strong>：<strong>奥行き方向もスライスに分け、3 次元の「クラスター（セル）」</strong>ごとにライトのリスト。<strong>奥行きの不連続に強い</strong>。<strong>半透明・Forward にも使いやすい</strong>。
    - <strong>Tiled / Clustered Deferred</strong>：<strong>ライティングをコンピュートで、1 パスで</strong>（<strong>G-Buffer を、1 回だけ読む</strong>）。
    - <strong>Tiled / Clustered Forward</strong>（Forward+）：<strong>Forward でタイル／クラスターのライト リスト</strong>を使う（<strong>MSAA・半透明が使える</strong>）。

## なぜ、絞るのか

**100 個のライトがあるシーン**で**あるピクセルに実際に届くライトは、数個**です。**全 100 個を計算するのは無駄**です。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="ライトの、影響範囲と、ピクセル">
<text x="20" y="24" class="fig-title">どのライトも、影響する範囲が、限られている。ピクセルに届くのは、ごく一部</text>
<rect x="20" y="50" width="400" height="200" rx="8" fill="rgba(150,150,150,0.1)" stroke="currentColor" stroke-width="2"/>
<circle cx="90" cy="110" r="46" fill="rgba(229,170,40,0.3)" stroke="#e5a828" stroke-width="2"/><circle cx="90" cy="110" r="4" fill="#e5a828"/>
<circle cx="200" cy="190" r="56" fill="rgba(229,170,40,0.3)" stroke="#e5a828" stroke-width="2"/><circle cx="200" cy="190" r="4" fill="#e5a828"/>
<circle cx="330" cy="100" r="40" fill="rgba(229,170,40,0.3)" stroke="#e5a828" stroke-width="2"/><circle cx="330" cy="100" r="4" fill="#e5a828"/>
<circle cx="360" cy="210" r="36" fill="rgba(229,170,40,0.3)" stroke="#e5a828" stroke-width="2"/><circle cx="360" cy="210" r="4" fill="#e5a828"/>
<circle cx="250" cy="130" r="7" fill="#e5484d"/><text x="262" y="126" style="font-size:12px;fill:#e5484d;font-weight:700">このピクセル</text>
<text x="450" y="80" style="font-weight:700">Forward / 素朴な Deferred</text><text x="450" y="102" style="font-size:12px">4 個のライトを、すべて計算</text>
<text x="450" y="150" style="font-weight:700">ライト カリング後</text><text x="450" y="172" style="font-size:12px">このピクセルに届く、1〜2 個だけ</text>
<text x="450" y="214" style="font-size:12px">ライトが、100 個でも、1000 個でも、</text><text x="450" y="232" style="font-size:12px">近くの数個だけの計算で、済む</text>
</svg>

| 目的 | 説明 |
| --- | --- |
| **計算量の削減** | **ピクセルごとに全ライトではなく、近くのライトだけ** |
| **帯域の削減**（Deferred） | **ライトごとに、G-Buffer をフルスクリーンで読まず、1 回だけ読む** |
| **スケーラビリティ** | **ライトを数千個**にしても**ピクセルあたりの負担が増えない** |

## Tiled（タイル分割）

### 仕組み

<svg class="fig flow" viewBox="0 0 1604 112" role="img" aria-label="Tiled：画面を、タイルに分けて、タイルごとに、影響するライトの、リストを作る"><defs><marker id="fl9676" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">Tiled：画面を、タイルに分けて、タイルごとに、影響するライトの、リストを作る</text><line x1="141.0" y1="64.0" x2="199.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl9676)"/><line x1="403.0" y1="64.0" x2="461.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl9676)"/><text x="432.0" y="58.0" text-anchor="middle" style="font-size:12px">深度の範囲</text><line x1="655.0" y1="64.0" x2="713.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl9676)"/><line x1="921.0" y1="64.0" x2="979.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl9676)"/><line x1="1194.0" y1="64.0" x2="1252.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl9676)"/><rect x="28.0" y="44.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="83.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">深度バッファ</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="202.0" y="44.0" width="198" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="301.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">タイルに分ける （16×16）</text><circle cx="204.0" cy="46.0" r="10" fill="#2ea043"/><text x="204.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="464.0" y="44.0" width="188" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="558.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">タイルの 最小・最大深度</text><circle cx="466.0" cy="46.0" r="10" fill="#e5a828"/><text x="466.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="716.0" y="44.0" width="202" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="817.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ライトを タイルの形と判定</text><circle cx="718.0" cy="46.0" r="10" fill="#e5484d"/><text x="718.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="982.0" y="44.0" width="209" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="1086.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">タイルごとの ライト リスト</text><circle cx="984.0" cy="46.0" r="10" fill="#9664e6"/><text x="984.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text><rect x="1255.0" y="44.0" width="321" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="1415.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ピクセルは、 自分のタイルの ライトだけ計算</text><circle cx="1257.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="1257.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">6</text></svg>

| 手順 | 内容 |
| --- | --- |
| **1. 画面をタイルに分ける** | **16×16 ピクセル**が、定番（**1920×1080 なら、約 8000 タイル**） |
| **2. タイルの深度の範囲を、求める** | **タイル内の最小深度・最大深度**（**コンピュート シェーダーで、リダクション**） |
| **3. タイルの形（視錐台）を作る** | **タイルの 4 辺と最小・最大深度**で囲まれた、**小さな視錐台** |
| **4. ライトを判定** | **各ライト（球）が、タイルの視錐台と交わるか** |
| **5. リストに追加** | **交わるライトの番号をタイルのリスト**に（共有メモリ → バッファ） |
| **6. ピクセルは、リストを読む** | **自分のタイルのライトだけ**を計算 |

**コンピュート シェーダー**で、**タイル ＝ 1 つのスレッド グループ**として、<strong>共有メモリ（groupshared）</strong>に、**リストを作ります**。**スレッドが手分けして、ライトを判定**するので**速い**です。

### 利点

| 利点 | 説明 |
| --- | --- |
| **計算が劇的に減る** | **ピクセルあたり、数個のライト** |
| **Deferred：G-Buffer を、1 回だけ読む** | **ライティング パスが、1 つ**（コンピュートで全ライトをまとめて処理）。**ライトごとのフルスクリーン ブレンドが、不要** |
| **ブレンド（加算）が、不要** | **ピクセルが全ライトの合計をレジスタ内**で計算し、**1 回だけ、書き込む**（**帯域**） |

### 弱点

| 弱点 | 説明 |
| --- | --- |
| **深度の不連続** | **タイル内に近い物と遠い物**（物体の縁）があると**最小〜最大の深度が広く**なり、**ライトが多く残る**（**無駄が出る**） |
| **半透明** | **深度バッファが不透明のみ**なので**半透明の位置は、考慮されない**（**別の対策が必要**） |
| **奥行きの情報が粗い** | **2.5 次元**（画面方向のみ、奥行きは、min/max の 1 区間） |

**この弱点を解決するのが、Clustered** です。

## Clustered（クラスター分割）

**画面を、2 次元のタイルだけでなく、奥行き方向にも分割**します。<strong>3 次元の小さなセル（クラスター）</strong>ごとに**ライトのリスト**を持ちます。

<svg class="fig illust" viewBox="0 0 800 280" role="img" aria-label="Clustered：視錐台を、奥行きにも分割">
<text x="20" y="24" class="fig-title">Clustered：視錐台を、画面方向（タイル）と、奥行き（スライス）に分け、セルごとに、ライトのリスト</text>
<polygon points="60,200 300,60 300,230 60,225" fill="rgba(76,139,245,0.12)" stroke="currentColor" stroke-width="2"/>
<g stroke="currentColor" stroke-width="1" opacity="0.7">
<line x1="100" y1="196" x2="100" y2="223"/><line x1="130" y1="170" x2="130" y2="224"/><line x1="170" y1="140" x2="170" y2="225"/><line x1="220" y1="103" x2="220" y2="227"/><line x1="300" y1="60" x2="300" y2="230"/>
</g>
<text x="62" y="248" style="font-size:12px">近い（スライスは細かい）</text><text x="236" y="248" style="font-size:12px">遠い（スライスは粗い）</text>
<circle cx="150" cy="190" r="7" fill="#e5484d"/><text x="160" y="186" style="font-size:11px;fill:#e5484d">ここのセルだけ</text>
<text x="360" y="70" style="font-weight:700">分け方</text>
<text x="360" y="94" style="font-size:12px">・画面方向：タイル（16×16 ピクセルなど）</text>
<text x="360" y="114" style="font-size:12px">・奥行き：対数スケールで、24〜32 スライス</text>
<text x="360" y="134" style="font-size:12px">　（近くは細かく、遠くは粗く）</text>
<text x="360" y="170" style="font-weight:700">ピクセルは</text>
<text x="360" y="194" style="font-size:12px">①画面の位置からタイルを、②深度からスライスを求め、</text>
<text x="360" y="214" style="font-size:12px">③そのセルのライト リストだけを、計算する</text>
</svg>

### 奥行きの分け方

**奥行きは対数スケール**でスライスに分けます。**近くは細かく、遠くは粗く**（**見た目の大きさに合わせる**）。

```text
スライス番号 ＝ floor( log(z / near) / log(far / near) × スライス数 )
```

| 項目 | 説明 |
| --- | --- |
| **スライス数** | **24〜32** がよく使われる |
| **対数分割の理由** | **透視投影で遠くはピクセルあたりの奥行きが大きい**ため、**画面上の均等な大きさに近づく** |
| **クラスターの総数** | **例**：**タイル 120×68 × 24 スライス ＝ 約 20 万**（**タイルを大きくして、減らす**ことも） |

### 利点

| 利点 | 説明 |
| --- | --- |
| **奥行きの不連続に強い** | <strong>「近い物」と「遠い物」が、別のセル</strong>になるので**ライトが無駄に残らない** |
| **深度プリパスが不要** | **タイルの min/max 深度を、求める必要がない**（**画面の位置と深度から、セルが決まる**） |
| **半透明が扱える** | **半透明の深度から、セルを引ける**（**不透明の深度に依存しない**） |
| **Forward と相性が良い** | **Forward でもセルのライト リストを、読むだけ** |
| **ボリューム効果にも使える** | **霧・ボリュメトリック ライト**の、計算単位にも |

### 弱点

| 弱点 | 説明 |
| --- | --- |
| **メモリが増える** | **クラスターの数 × リストの大きさ** |
| **構築のコスト** | **クラスターごとにライトを判定**（**数が多い**）。**コンピュートで並列化** |
| **実装がやや複雑** | **スライスの計算・リストの管理** |

## ライト リストの、データ構造

**クラスター／タイルごとに、ライトの番号のリスト**を持ちます。

| 構造 | 内容 |
| --- | --- |
| **ライト バッファ** | **全ライトの情報**（位置・色・半径）の配列 |
| **ライト インデックス リスト** | <strong>「セルごとのライト番号」を、1 本の配列に詰めたもの</strong> |
| **グリッド** | <strong>セルごとに、「リストの開始位置」と「個数」</strong> |
| <strong>カウンター（UAV）</strong> | **コンピュートがリストに書き込む位置**（アトミック加算） |

```text
グリッド[セル] → (開始位置, 個数)
ライト インデックス リスト[開始位置 .. 開始位置+個数] → ライト番号 → ライト バッファ[ライト番号]
```

<strong>ピクセルシェーダー（またはコンピュート）</strong>は、**グリッドを引いて、リストを読み、ライトを計算**します。

## 4 つの組み合わせ

| | **Forward 系**（色を物体を描きながら） | **Deferred 系**（G-Buffer から） |
| --- | --- | --- |
| **Tiled** | <strong>Tiled Forward（Forward+）</strong>：**深度プリパス → ライト カリング（コンピュート）→ Forward 描画**。**MSAA・半透明が使える** | **Tiled Deferred**：<strong>G-Buffer → ライト カリング ＋ ライティング（コンピュート 1 パス）</strong> |
| **Clustered** | **Clustered Forward**：**クラスターのライト リストを、Forward で読む**。**半透明に強い** | **Clustered Deferred**：**G-Buffer ＋ クラスターで、ライティング** |

### それぞれの使いどころ

| 方式 | 向く場面 |
| --- | --- |
| **Tiled Deferred** | **PC・コンソール**の**不透明中心**。**帯域に余裕がある** |
| <strong>Tiled Forward（Forward+）</strong> | **MSAA が欲しい・材質を自由に**したい |
| **Clustered Forward** | **半透明・ボリューム効果**をライトに反応させたい。**VR** |
| **Clustered Deferred** | **大規模・ライトが非常に多い** |

**現在の多くのゲームは、Clustered（または Tiled）を、Forward か Deferred と組み合わせて**います。**ハイブリッド**（**不透明は Deferred、半透明は Clustered Forward**）も、**一般的**です。

## 実装の注意

| 注意 | 説明 |
| --- | --- |
| **コンピュート シェーダーが、必要** | **DX11 はコンピュート シェーダー（`CSMain`）を使える**（**Feature Level 11 以上**） |
| **タイルの大きさ** | **16×16 が多い**。**小さい**と**精度が上がるがタイル数が増える** |
| **ライトの上限** | **タイル／クラスターあたりの、最大ライト数**を決める（**超えたら、切り捨て**） |
| **ライトの半径** | <strong>「影響範囲」</strong>を、**適切に決める**（**大きすぎる**と絞れない） |
| **影** | **影付きライトは、別に**（**影マップのコスト**。[そのほかの最適化](taa-upscaling.md)） |
| <strong>半透明（Tiled）</strong> | **深度の範囲が不透明のみ**。**半透明は全ライト、または、Clustered** |

## 手法の進化と改善点（まとめ）

| 手法 | ピクセルあたりのライティング | G-Buffer の読み込み | 弱点 |
| --- | --- | --- | --- |
| **Forward** | <strong>全ライト（オーバードロー込み）</strong> | なし | **ライトが多いと重い** |
| <strong>Deferred（ライト ボリューム）</strong> | **範囲内のライト** | **ライトごとに読み直し** | **帯域**・MSAA・半透明 |
| **Tiled Deferred** | **タイルのライト** | **1 回** | **深度の不連続** |
| **Clustered** | **セルのライト** | **1 回**（Deferred の場合） | **メモリ・構築コスト** |

<strong>「ライトを絞る」「G-Buffer を、1 回だけ読む」</strong>——この**2 つの積み重ね**で、**数千のライト**に**対応**してきました。

<!-- fig:tiled-light-count:begin -->

<svg class="fig illust motion" data-fig="tiled-light-count" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tiled-light-count" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Tiled: 画面をタイルに分け、タイルごとに、光が届く数を数える</text>
<rect x="130" y="90" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="194" y="90" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="258" y="90" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="322" y="90" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="386" y="90" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="450" y="90" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="90" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="578" y="90" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="130" y="154" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="194" y="154" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="258" y="154" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="322" y="154" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="386" y="154" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="450" y="154" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="154" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="578" y="154" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="130" y="218" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="194" y="218" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="258" y="218" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="322" y="218" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="386" y="218" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="450" y="218" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="218" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="578" y="218" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="130" y="282" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="194" y="282" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="258" y="282" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="322" y="282" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="386" y="282" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="450" y="282" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="282" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="578" y="282" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="130" y="346" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="194" y="346" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="258" y="346" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="322" y="346" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="386" y="346" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="450" y="346" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="346" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="578" y="346" width="62" height="62" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="130" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="161.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="194" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="225.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="258" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="289.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="322" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="353.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="417.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="481.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="545.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="609.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="130" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="161.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="194" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="225.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="258" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="289.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="322" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="353.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="417.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="481.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="545.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="609.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="130" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="161.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="194" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="225.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="258" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="289.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="322" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="353.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="417.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="481.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="545.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="609.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="161.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="225.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="289.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="353.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="417.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="481.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="545.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="609.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="161.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="225.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="289.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="353.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="417.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="481.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="545.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="609.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="130" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="161.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="194" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="225.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="258" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="289.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="322" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="353.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="417.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="481.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="545.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="609.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="130" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="161.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="194" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="225.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="258" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="289.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="322" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="353.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="386" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="417.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="450" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="481.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="514" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="545.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="609.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="130" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="161.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="194" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="225.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="258" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="289.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="322" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.59;0.59;0;0"/></rect>
<text x="353.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="386" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="417.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="450" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="481.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="514" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="545.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="578" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="609.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="161.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="225.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="289.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="322" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="353.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="386" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="417.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="450" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="481.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="514" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="545.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="578" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="609.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="161.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="225.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="289.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="353.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="386" y="346" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="417.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="450" y="346" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="481.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="514" y="346" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;0.37;0.37;0;0"/></rect>
<text x="545.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="609.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<rect x="130" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="161.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="194" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="225.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="258" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="289.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="322" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="353.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<text x="417.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="450" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="481.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="514" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="545.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="578" y="90" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="609.0" y="128.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="130" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="161.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="194" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="225.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="258" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="289.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="322" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="353.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="386" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="417.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="450" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.59;0.59"/></rect>
<text x="481.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="514" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.59;0.59"/></rect>
<text x="545.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="578" y="154" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="609.0" y="192.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="130" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="161.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="194" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="225.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="258" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="289.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="322" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.59;0.59"/></rect>
<text x="353.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="386" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="417.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="450" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.59;0.59"/></rect>
<text x="481.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="514" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.59;0.59"/></rect>
<text x="545.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="578" y="218" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="609.0" y="256.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<text x="161.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<text x="225.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<text x="289.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="322" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="353.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="386" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="417.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="450" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="481.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="514" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="545.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="578" y="282" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="609.0" y="320.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<text x="161.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<text x="225.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<text x="289.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<text x="353.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="386" y="346" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="417.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="450" y="346" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="481.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<rect x="514" y="346" width="62" height="62" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;0.37;0.37"/></rect>
<text x="545.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<text x="609.0" y="384.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></text>
<circle cx="258.0" cy="186.0" r="83.2" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></circle>
<circle cx="258.0" cy="186.0" r="6" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></circle>
<circle cx="482.0" cy="282.0" r="108.8" fill="none" stroke="#2ea043" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;1.0000" values="0;0;1;1"/></circle>
<circle cx="482.0" cy="282.0" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;1.0000" values="0;0;1;1"/></circle>
<circle cx="526.8" cy="166.8" r="64.0" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></circle>
<circle cx="526.8" cy="166.8" r="6" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000" values="0;0;1;1"/></circle>
<text x="130" y="75" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">各マス = 1 タイル。数字 = そのタイルに届く光の数</text>
<text x="390" y="430" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光が 3 個ある画面<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="390" y="430" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光 1 個目の円に触れるタイルが、+1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.3094;0.3097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="430" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 個目を足す。重なったタイルは 2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3094;0.3097;0.5546;0.5548;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="430" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 個目まで。各タイルは、数えた光だけ計算すればよい<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5546;0.5548;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:tiled-light-count:end -->

## よくあるミス

??? failure "タイルの深度範囲に、半透明を含めて、計算が崩れる"
    **不透明の深度**だけで、**min/max**を作ります。**半透明は別処理**。

??? failure "ライトの半径を、大きくしすぎて、リストがあふれる"
    **影響範囲を実際の減衰に合わせて、小さく**します。**上限の数も確認**します。

??? failure "Tiled で、物体の縁にライトのちらつきが出る"
    **深度の不連続**が原因のことがあります。**Clustered**にする、**タイルを小さく**する。

??? failure "クラスターのスライスを、線形に分けて、近くが粗くなる"
    **対数スケール**で分けます。

??? failure "ライト リストの、書き込みで競合する"
    **アトミック加算**（`InterlockedAdd`）で、**位置を確保**します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 目的：<strong>「ピクセル × 全ライト」を、「ピクセル × 近くのライト」に</strong>。<strong>G-Buffer を、1 回だけ読む</strong>（帯域）
    - [x] <strong>Tiled ＝ 画面を、タイルに分け、タイルごとのライト リスト</strong>（<strong>min/max 深度で絞る</strong>）。<strong>弱点は深度の不連続</strong>
    - [x] <strong>Clustered ＝ 奥行き（対数スライス）も分け、3 次元のセルごと</strong>。<strong>不連続・半透明に強い</strong>
    - [x] <strong>Forward 系（Forward+）</strong>は<strong>MSAA・半透明・材質の自由</strong>、<strong>Deferred 系</strong>は<strong>ライトが、非常に多い</strong>とき
    - [x] <strong>ライト リスト ＝ グリッド ＋ インデックス リスト ＋ ライト バッファ</strong>。<strong>コンピュート シェーダー</strong>で作る

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [Forward と Deferred](forward-deferred.md)
- [メモリ帯域幅](bandwidth.md)
- [Visibility Buffer](visibility-buffer.md)
- [法線とライティング](../3d/lighting-normals.md)
