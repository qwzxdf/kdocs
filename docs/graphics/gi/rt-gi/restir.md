---
title: ReSTIR GI
tags:
  - 描画
---

# ReSTIR GI

**ReSTIR は、「良いサンプルを、隣の画素や前フレームから借りる」ことで、少ないレイでも、きれいな結果を出す手法**です。**重みつきリザーバー サンプリング**を使い、**サンプルを再利用**します。このページでは、**ReSTIR の考え方と効果**を説明します。

!!! tip "ポイント"
    - **リザーバーに、「良さそうなサンプル」を 1 つだけ保持**する。
    - **隣の画素・前フレームのリザーバーと混ぜる（再利用）**。
    - **再利用すると、実質のサンプル数が、桁違いに増える**。
    - **バイアスの管理（再利用してよいかの判定）が難しい**。

<!-- fig:restir-reservoir:begin -->

<svg class="fig illust motion" data-fig="restir-reservoir" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-restir-reservoir" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">リザーバー:候補を流して見ながら、良さそうな 1 つだけ覚える</text>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0825;0.0828;1.0000" values="0;0;1;1"/><rect x="60" y="130" width="62" height="24.0" fill="#94a3b8" stroke="#1f2937" stroke-width="1.5"/>
<text x="91" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 A</text>
<text x="91" y="172.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;1.0000" values="0;0;1;1"/><rect x="140" y="130" width="62" height="32.0" fill="#60a5fa" stroke="#1f2937" stroke-width="1.5"/>
<text x="171" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 B</text>
<text x="171" y="180.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.3</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2480;0.2483;1.0000" values="0;0;1;1"/><rect x="220" y="130" width="62" height="116.0" fill="#e5484d" stroke="#1f2937" stroke-width="1.5"/>
<text x="251" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 C</text>
<text x="251" y="264.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 2.4</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;1.0000" values="0;0;1;1"/><rect x="300" y="130" width="62" height="28.0" fill="#94a3b8" stroke="#1f2937" stroke-width="1.5"/>
<text x="331" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 D</text>
<text x="331" y="176.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4135;0.4138;1.0000" values="0;0;1;1"/><rect x="380" y="130" width="62" height="40.0" fill="#fbbf24" stroke="#1f2937" stroke-width="1.5"/>
<text x="411" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 E</text>
<text x="411" y="188.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.5</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4963;0.4966;1.0000" values="0;0;1;1"/><rect x="460" y="130" width="62" height="64.0" fill="#2ea043" stroke="#1f2937" stroke-width="1.5"/>
<text x="491" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 F</text>
<text x="491" y="212.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 1.1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5790;0.5793;1.0000" values="0;0;1;1"/><rect x="540" y="130" width="62" height="26.0" fill="#94a3b8" stroke="#1f2937" stroke-width="1.5"/>
<text x="571" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 G</text>
<text x="571" y="174.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6618;0.6621;1.0000" values="0;0;1;1"/><rect x="620" y="130" width="62" height="36.0" fill="#a78bfa" stroke="#1f2937" stroke-width="1.5"/>
<text x="651" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 H</text>
<text x="651" y="184.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.4</text>
</g>
<rect x="60" y="290" width="200" height="70" fill="#ffffff" stroke="#1f2937" stroke-width="2.5" rx="6"/>
<text x="160" y="282" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">リザーバー（1 つだけ保持）</text>
<rect x="70" y="300" width="60" height="50" fill="#e2e8f0"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172;0.2000;0.2828;0.3655;0.4483;0.5310;0.6138;0.6966" values="#e2e8f0;#94a3b8;#60a5fa;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d"/></rect>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 A<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1172;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 B<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.2825;0.2828;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2825;0.2828;0.3652;0.3655;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3652;0.3655;0.4480;0.4483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4480;0.4483;0.5308;0.5310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5308;0.5310;0.6135;0.6138;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6135;0.6138;0.6963;0.6966;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6963;0.6966;0.7790;0.7793;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 A 到着:採用の確率 = 0.1 / (累計 0.1) = 100 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0825;0.0828;0.1652;0.1655;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 B 到着:採用の確率 = 0.3 / (累計 0.4) = 75 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;0.2480;0.2483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 C 到着:採用の確率 = 2.4 / (累計 2.8) = 86 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2480;0.2483;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 D 到着:採用の確率 = 0.2 / (累計 3.0) = 7 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.4135;0.4138;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 E 到着:採用の確率 = 0.5 / (累計 3.5) = 14 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4135;0.4138;0.4963;0.4966;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 F 到着:採用の確率 = 1.1 / (累計 4.6) = 24 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4963;0.4966;0.5790;0.5793;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 G 到着:採用の確率 = 0.1 / (累計 4.8) = 3 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5790;0.5793;0.6618;0.6621;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 H 到着:採用の確率 = 0.4 / (累計 5.2) = 8 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6618;0.6621;0.7446;0.7448;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 採用! リザーバーを入れ替える<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0825;0.0828;0.1652;0.1655;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 採用! リザーバーを入れ替える<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;0.2480;0.2483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 採用! リザーバーを入れ替える<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2480;0.2483;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.4135;0.4138;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4135;0.4138;0.4963;0.4966;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4963;0.4966;0.5790;0.5793;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5790;0.5793;0.6618;0.6621;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6618;0.6621;0.7446;0.7448;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">最後に残った 1 つが、重みに比例して選ばれた「良い」サンプル。全部を覚えなくても、1 つだけで済む。<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7790;0.7793;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="70" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">候補を 1 つずつ流す。明るい（寄与の大きい）候補ほど、残りやすい。</text>
</svg>

<!-- fig:restir-reservoir:end -->

## ReSTIR GI

**ReSTIR**（Reservoir-based Spatiotemporal Importance Resampling）は、<strong>「良いサンプルを近い画素や前フレームから借りる」</strong>ことで、1 画素あたりの有効なサンプル数を、桁違いに増やす手法です。2020 年に Bitterli らが直接光（ReSTIR DI）で提案し、2021 年に Ouyang らが間接光（ReSTIR GI）へ拡張しました。ここでは、手法の背景から順に、仕組みを組み立てます。

### 出発点：サンプルを賢く選びたい

レイトレ GI のノイズの根本原因は、<strong>「寄与の大きいサンプルを引き当てる確率が低い」</strong>ことです。画素の周りの半球に、ランダムにレイを 1 本飛ばしても、明るい壁や光源に当たる確率は小さく、大半のレイは暗い場所に当たって、ほとんど寄与しません。たまに明るい所に当たる画素と、当たらない画素が混在して、ノイズになります。

もし「どの方向のサンプルが寄与が大きいか」が事前に分かっていれば、その方向だけを選べばよいのですが、それは答えを知っているのと同じで、不可能です。そこで、<strong>安いサンプルを大量に作り、その中から質の良いものを選ぶ</strong>という考え方が出てきます。

### RIS：候補を作って、良いものを選ぶ

**RIS**（Resampled Importance Sampling、Talbot ら 2005）は、まず M 個の候補サンプルを、簡単な分布（たとえば BRDF に従う方向）で作ります。次に、各候補の「良さ」を、安く計算できる<strong>目標関数</strong> p̂ で評価します。ReSTIR GI では、p̂ は、そのサンプルの寄与の大きさ（反射光の輝度）です。そして、p̂ に比例する確率で、M 個の中から 1 個を選びます。選ばれたサンプルには、補正の重みが付きます。

ポイントは、**候補の評価（p̂ の計算）はレイトレースを必要としない**ことです。レイを飛ばさなくても、サンプルがすでにどこに当たるか分かっていれば、その寄与は計算できます。したがって、M を増やしても、コストの増え方が小さいまま、質の良い 1 個を選べます。

### リザーバー：1 個だけ覚えておく

RIS で M 個の候補を、画素ごとに全部保存すると、メモリが膨大です。そこで、<strong>重み付きリザーバー サンプリング</strong>（Chao 1982）を使います。候補を 1 個ずつ処理しながら、「今までで選ばれたサンプル 1 個」と「重みの合計」だけを覚えておけば、最終的に RIS と同じ分布のサンプルが得られる、という仕組みです。このデータの入れ物を<strong>リザーバー</strong>と呼びます。

```hlsl
struct Reservoir {
  Sample sample;
  float w_sum;
  float m;
};

void Update(inout Reservoir r, Sample s, float weight, float u) {
  r.w_sum += weight;
  r.m += 1.0;
  if (u * r.w_sum < weight) {
    r.sample = s;
  }
}
```

新しい候補が来るたびに、`weight / w_sum` の確率でサンプルを入れ替えます。早く来た候補ほど、後から置き換えられる確率が高くなるので、結果的に全候補が、重みに比例する確率で選ばれます。リザーバーのサイズは、サンプル 1 個分に固定で、M がいくつでも変わりません。

### 再利用：リザーバー同士をマージする

ReSTIR の核心は、リザーバー同士を<strong>マージ</strong>できることです。隣の画素のリザーバーは、「その画素の M 個の候補から選ばれた 1 個」を持っています。この 1 個を、自分のリザーバーの候補として投入すれば、あたかも<strong>相手の M 個の候補をすべて見たかのように</strong>、サンプルを選べます。実際に追加でレイを飛ばす必要はありません。

<strong>時間的な再利用</strong>では、前フレームの同じ位置（動きベクトルで再投影）のリザーバーとマージします。毎フレーム、前フレームまでの全サンプル履歴を引き継ぐので、静止していればサンプル数は雪だるま式に増えます。<strong>空間的な再利用</strong>では、近隣（例：半径 30 画素以内）の数画素のリザーバーとマージします。隣の画素は、自分と似た環境にいるので、良いサンプルは自分にとっても良いサンプルである可能性が高いからです。

履歴が増えすぎて、古いサンプルばかりになると、変化への追従が遅れます。そのため、リザーバーの M に上限を設け（例：現在のフレームの 20 倍まで）、古い情報を徐々に薄めます。

### ReSTIR GI のサンプルとは何か

直接光の ReSTIR DI では、サンプルは「ライト上の 1 点」でした。間接光の ReSTIR GI では、サンプルは<strong>「画素から飛ばしたレイが最初に当たった点（二次ヒット点）とその点の情報」</strong>です。具体的には、二次ヒット点の位置 x₂、法線 n₂、そしてその点から画素の方向に出る放射輝度 L₂（直接光とキャッシュから得た間接光）を保存します。

このサンプルは、隣の画素が使うときに、**そのまま再利用**できます。隣の画素の視点位置 x₁' から、同じ二次ヒット点 x₂ へ向かう新しい経路を作り、その経路の寄与を、x₂ に保存された L₂ を使って計算します。これを<strong>再接続</strong>（reconnection）と呼びます。新たにレイトレースをしなくても（可視性の確認 1 回を除いて）、他の画素のサンプルを自分用の経路に変換できます。

### バイアスの管理：ヤコビアンと可視性

再利用で気をつけるのは、<strong>隣の画素のサンプルを、そのまま自分のサンプルとして扱うと、確率密度がずれる</strong>ことです。隣の画素から見た二次ヒット点の方向と、自分から見た方向は、一般に違うので、同じ点を選ぶ確率が違います。この確率密度の差を補正するのが、<strong>ヤコビアン</strong>（方向の測度から面積の測度への変換係数）です。ヤコビアンは、二次ヒット点までの距離と、二次ヒット点の法線と各視点方向のなす角の余弦から計算できます。

もう 1 つの補正は、<strong>可視性</strong>です。隣の画素から見えた二次ヒット点が、自分からは壁の裏に隠れて見えないことがあります。そのままだと、壁の向こうの光が漏れます。そこで、再接続の経路について、シャドウ レイを 1 本飛ばして、遮蔽されていれば、そのサンプルを捨てます。この 1 本のレイは安いので、全体のコストにはあまり響きません。

さらに、法線や深度が大きく違う画素のリザーバーは、そもそも再利用しません。これらの条件を満たさないサンプルを混ぜると、画面に不自然なにじみが出るからです。ヤコビアンと可視性の補正をきちんと入れる方式を<strong>不偏</strong>（unbiased）、入れずに近似する方式を<strong>偏りあり</strong>（biased）と呼びます。不偏のほうが正確ですが重く、実際の製品では、見た目に影響が出ない範囲で近似するのが普通です。

### 最終的なシェーディング

リザーバーに入っているサンプルと重みから、画素の間接光を計算します。ReSTIR 後のノイズは、通常の 1 画素 1 レイに比べて桁違いに小さくなりますが、まだ多少残るので、通常のデノイザーを軽く掛けて仕上げます。

### 発展と実装

ReSTIR は、DI（直接光）から GI（間接光）、さらに <strong>ReSTIR PT</strong>（Lin ら 2022、パス全体の再利用）へと発展しています。NVIDIA の RTXDI（直接光）や RTXGI などに採用され、商用エンジンへの組み込みも進んでいます。実装は複雑で、パラメータが多く（候補数、空間再利用の半径と数、M の上限、バイアス補正の方式）、デバッグも難しい手法です。まずは、時間的な再利用だけを実装して、効果を確かめるところから始めるのがよいでしょう。

## よくあるミス

??? failure "再利用が強すぎて、光が不自然ににじむ"
    **法線・深度が合わないサンプルは再利用しない**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **良いサンプルを借りて、少ないレイで高品質**
    - [x] **バイアスの管理が、鍵**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Ray-Traced GI](index.md)
- [Fighting Noise](noise.md)
- [Choosing a Method](choosing.md)
