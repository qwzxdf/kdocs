---
title: Premultiplied Alpha
tags:
  - 描画
---

# Premultiplied Alpha

<strong>乗算済みアルファは色にあらかじめアルファを掛けておく形式</strong>です。<strong>ブレンド式が単純になり縁の黒いにじみ（フリンジ）も防げます</strong>。通常ブレンドと加算ブレンドを、1 つのシェーダーで両立できるのも利点です。このページでは乗算済みアルファの意味と使い方を説明します。

!!! tip "ポイント"
    - 乗算済み ＝ 色 × α を、先に計算して保存。
    - ブレンド式：手前 ＋ 奥 × (1 − α)（One / InvSrcAlpha）。
    - テクスチャの縁の、黒や白のにじみが出ない。
    - α = 0 で加算、α = 1 で通常として 1 つの式で両立できる。

<!-- fig:premult-fringe:begin -->

<svg class="fig illust motion" data-fig="premult-fringe" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-premult-fringe" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">縁の黒い線:ストレート アルファは、補間で「透明部分の色」が混ざる</text>
<rect x="60" y="100" width="300" height="70" fill="#e5484d" stroke="#94a3b8" stroke-width="1.5"/>
<text x="210" y="90" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">テクセル A:赤・不透明（α = 1）</text>
<rect x="360" y="100" width="300" height="70" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="360" y="100" width="300" height="70" fill="#f1f5f9"/>
<text x="510" y="140" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">（透明。中の RGB は黒）</text>
<text x="510" y="90" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">テクセル B:透明（α = 0）、色は黒</text>
<text x="60" y="214" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ストレート（補間 → その後でブレンド）</text>
<rect x="60" y="230" width="25" height="40" fill="#e14a4f"/>
<rect x="85" y="230" width="25" height="40" fill="#d94f54"/>
<rect x="110" y="230" width="25" height="40" fill="#d25458"/>
<rect x="135" y="230" width="25" height="40" fill="#cc5a5d"/>
<rect x="160" y="230" width="25" height="40" fill="#c75f63"/>
<rect x="185" y="230" width="25" height="40" fill="#c36568"/>
<rect x="210" y="230" width="25" height="40" fill="#bf6b6e"/>
<rect x="235" y="230" width="25" height="40" fill="#bc7274"/>
<rect x="260" y="230" width="25" height="40" fill="#ba787a"/>
<rect x="285" y="230" width="25" height="40" fill="#b97f81"/>
<rect x="310" y="230" width="25" height="40" fill="#b88688"/>
<rect x="335" y="230" width="25" height="40" fill="#b88e8f"/>
<rect x="360" y="230" width="25" height="40" fill="#b99596"/>
<rect x="385" y="230" width="25" height="40" fill="#bb9d9e"/>
<rect x="410" y="230" width="25" height="40" fill="#bea5a6"/>
<rect x="435" y="230" width="25" height="40" fill="#c1aeae"/>
<rect x="460" y="230" width="25" height="40" fill="#c6b6b7"/>
<rect x="485" y="230" width="25" height="40" fill="#cbbfc0"/>
<rect x="510" y="230" width="25" height="40" fill="#d1c8c9"/>
<rect x="535" y="230" width="25" height="40" fill="#d7d2d2"/>
<rect x="560" y="230" width="25" height="40" fill="#dfdbdb"/>
<rect x="585" y="230" width="25" height="40" fill="#e7e5e5"/>
<rect x="610" y="230" width="25" height="40" fill="#f0efef"/>
<rect x="635" y="230" width="25" height="40" fill="#fafafa"/>
<rect x="60" y="230" width="600" height="40" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="314" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">乗算済み（先に α を掛けて保存 → 補間）</text>
<rect x="60" y="330" width="25" height="40" fill="#e64c51"/>
<rect x="85" y="330" width="25" height="40" fill="#e75358"/>
<rect x="110" y="330" width="25" height="40" fill="#e85b60"/>
<rect x="135" y="330" width="25" height="40" fill="#e96367"/>
<rect x="160" y="330" width="25" height="40" fill="#ea6a6e"/>
<rect x="185" y="330" width="25" height="40" fill="#eb7276"/>
<rect x="210" y="330" width="25" height="40" fill="#ec7a7d"/>
<rect x="235" y="330" width="25" height="40" fill="#ed8185"/>
<rect x="260" y="330" width="25" height="40" fill="#ee898c"/>
<rect x="285" y="330" width="25" height="40" fill="#ef9093"/>
<rect x="310" y="330" width="25" height="40" fill="#f0989b"/>
<rect x="335" y="330" width="25" height="40" fill="#f1a0a2"/>
<rect x="360" y="330" width="25" height="40" fill="#f3a7aa"/>
<rect x="385" y="330" width="25" height="40" fill="#f4afb1"/>
<rect x="410" y="330" width="25" height="40" fill="#f5b7b9"/>
<rect x="435" y="330" width="25" height="40" fill="#f6bec0"/>
<rect x="460" y="330" width="25" height="40" fill="#f7c6c7"/>
<rect x="485" y="330" width="25" height="40" fill="#f8cdcf"/>
<rect x="510" y="330" width="25" height="40" fill="#f9d5d6"/>
<rect x="535" y="330" width="25" height="40" fill="#faddde"/>
<rect x="560" y="330" width="25" height="40" fill="#fbe4e5"/>
<rect x="585" y="330" width="25" height="40" fill="#fcecec"/>
<rect x="610" y="330" width="25" height="40" fill="#fdf4f4"/>
<rect x="635" y="330" width="25" height="40" fill="#fefbfb"/>
<rect x="60" y="330" width="600" height="40" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60" y="222" width="25" height="156" fill="none" stroke="#e5aa28" stroke-width="3"><animate attributeName="x" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1037;0.1333;0.1630;0.1926;0.2222;0.2519;0.2815;0.3111;0.3407;0.3704;0.4000;0.4296;0.4593;0.4889;0.5185;0.5481;0.5778;0.6074;0.6370;0.6667;0.6963;0.7259;0.7556" values="60;60;85;110;135;160;185;210;235;260;285;310;335;360;385;410;435;460;485;510;535;560;585;610;635"/></rect>
<text x="60" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">A と B の境界を、バイリニア補間で読む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="60" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ストレートは、中間で「黒」が混ざって暗い縁（フリンジ）。乗算済みは、混ざらない<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.8145;0.8148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">→ 乗算済みアルファなら、縁が自然に薄くなるだけ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.8145;0.8148;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:premult-fringe:end -->

## 乗算済みアルファ
<strong>色にあらかじめアルファを掛けて保存</strong>しておく方式です（<strong>Premultiplied Alpha</strong>）。

<div class="formula">C_s' = C_s · α_s　（保存する色）　、　C_out = C_s' + C_d · (1 − α_s)</div>

| 利点 | 内容 |
| --- | --- |
| 式が簡単 | ソースに掛け算が不要（`ONE`） |
| 加算と通常を 1 つのブレンドで表せる | α を 0 にすれば加算（`C_s' + C_d`）になる |
| 縁のにじみが少ない | テクスチャの縁で、背景の色（黒や白）が混ざる問題が起きにくい |
| ミップ・フィルタが正しい | 縮小・補間しても、透明な部分の色に引きずられない |

<strong>ストレート アルファ</strong>（通常の画像）は、<strong>完全に透明な画素の RGB が不定</strong>で、縮小・補間時に縁に白や黒の線（ハロー）が出ます。乗算済みアルファのテクスチャを使うと、これが起きません。

## ストレート アルファと、乗算済みアルファ

画像の色とアルファの持ち方に、<strong>2 通り</strong>あります。

| 形式 | 保存する値 | 例（赤、アルファ 0.5） |
| --- | --- | --- |
| ストレート（非乗算） | 色（アルファを、掛けていない）とアルファ | `(1.0, 0.0, 0.0, 0.5)` |
| 乗算済み（Premultiplied） | 色 × アルファと、アルファ | `(0.5, 0.0, 0.0, 0.5)` |

乗算済みは <strong>色の値にアルファが、すでに掛かっている</strong>形です（Smith、1995）。

## ブレンド式の違い

| 形式 | ブレンドの式 |
| --- | --- |
| ストレート | `結果 = C × α + D × (1 − α)` |
| 乗算済み | `結果 = C' + D × (1 − α)`（`C' = C × α`） |

<strong>乗算済みはソースの色にアルファを、掛ける計算を省けます</strong>。さらに、<strong>複数の層を重ねる合成が結合法則を、満たします</strong>（層を先にまとめてあとで、背景に重ねても同じ結果になる）。

## なぜ乗算済みがよいのか

### ① 縁に白や黒の縁取り（フリンジ）が出ない

画像を <strong>縮小・拡大</strong>（バイリニア補間）するとき、<strong>隣り合う画素の色が混ざります</strong>。透明な画素の色（本当は見えない色）が縁の、不透明な画素と混ざって縁に変な色が、にじみます。

```text
画素 A: 赤、不透明      (1, 0, 0, 1.0)
画素 B: 透明（色は、黒） (0, 0, 0, 0.0)    ← 見えないが、色は、黒として保存されている

ストレートで、50% ずつ補間:  (0.5, 0, 0, 0.5)   ← 色が、暗い赤に（本来は、赤のまま、半透明であるべき）
乗算済みで、50% ずつ補間:    (0.5, 0, 0, 0.5)   ← 乗算済みなら、色 × アルファ が (0.5, 0, 0) で、正しい
```

ストレートでは補間の結果が `(0.5, 0, 0)`、アルファが 0.5 でブレンドの時に、<strong>さらにアルファを掛けて</strong>、`(0.25, 0, 0)` と <strong>暗く</strong>なります。縁が暗くなる（黒い縁取り）のは、これが原因です。

| 縁の問題 | 原因 |
| --- | --- |
| 黒い縁取り | 透明な画素の色が、黒（ストレートで補間が色とアルファを別々に、混ぜる） |
| 白い縁取り | 透明な画素の色が白 |

### ② 加算とアルファ ブレンドを、1 つの式で

乗算済みでは <strong>アルファを 0 にして、色だけを持たせる</strong>と <strong>加算ブレンド</strong>に、なります。

```text
結果 = C' + D × (1 − α)
α = 0 のとき:  結果 = C' + D        ← 加算ブレンド
α = 1 のとき:  結果 = C'            ← 不透明
```

<strong>1 つのブレンド ステート</strong>で、<strong>煙（アルファ ブレンド）と、火（加算）</strong>を同じパーティクル システムで、描けます。アルファだけを下げる（火が燃え尽きて、暗い煙に変わる）、といった表現がソート順を変えずに、できます。

### ③ ミップマップとフィルタリング

<strong>ミップマップを作るとき</strong>も、<strong>ストレートのまま平均すると縁が、おかしくなります</strong>。乗算済みでミップを作ると正しい、結果になります。

## 乗算済みの画像を作る

| 方法 | 内容 |
| --- | --- |
| 画像を書き出すときに掛ける | テクスチャを、作るツール（Photoshop、ツール）で乗算済みに変換 |
| 読み込み時に掛ける | エンジンが、ロード時に `rgb *= a` を行う（ミップを作る前に） |
| シェーダーで掛ける | `color.rgb *= color.a` |

```hlsl
// ストレートの画像を、乗算済みとして、出力する。
float4 c = g_tex.Sample(g_linear_wrap, input.uv);
c.rgb *= c.a;                                    // 乗算済みにする
return c;                                         // ブレンド: SrcBlend = ONE, DestBlend = INV_SRC_ALPHA
```

!!! warning "ミップを作る前に、乗算する"
    画像のミップを作るときは、<strong>乗算済みの状態で縮小</strong>します。ストレートでミップを作ってから、シェーダーで `rgb *= a` しても <strong>縁の、フリンジは消えません</strong>（ミップの中ですでに、色が混ざっている）。画像ファイルを作る段階で乗算済みに、しておくのが確実です。

## パーティクルでの使い方

火と煙を <strong>1 つのパーティクル システム</strong>で、描くとき乗算済みアルファが <strong>便利</strong>です。

```hlsl
// 火から煙へ、時間とともに、変化する、パーティクル。
float life = particle.age / particle.lifetime;           // 0（生まれた）〜 1（消える）
float3 color = lerp(fire_color, smoke_color, life);       // 色: 火 → 煙
float fire_amount = saturate(1.0 - life * 2.0);           // 前半は、火（光る）
float alpha = lerp(0.0, 0.6, saturate(life * 2.0));       // アルファ: 火のとき 0（加算）、煙のとき、不透明に
// 乗算済み: 色 × アルファ（煙の部分）+ 火の部分は、アルファ 0 で、色だけを足す
float3 premul = smoke_color * alpha + fire_color * fire_amount * 4.0;   // 4.0 は、火の、明るさ（HDR）
return float4(premul, alpha);
```

## ブレンド ステート

```cpp
// 乗算済みアルファ。
D3D11_RENDER_TARGET_BLEND_DESC& rt = blend.RenderTarget[0];
rt.BlendEnable = TRUE;
rt.SrcBlend = D3D11_BLEND_ONE;                    // ソースに、アルファを、掛けない（掛け済み）
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOp = D3D11_BLEND_OP_ADD;
rt.SrcBlendAlpha = D3D11_BLEND_ONE;
rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
```

## UI（画面の絵）との関係

ユーザー インターフェース（UI）の画像も、<strong>乗算済み</strong>にするライブラリが、多いです（フォント、アイコンの縁がきれいになる）。<strong>ストレートか乗算済みか</strong>を、ライブラリごとに確認します。

| 症状 | 原因 |
| --- | --- |
| UI の絵の縁に黒い線 | ストレートの画像を、乗算済みのブレンドで描いた（または、その逆） |
| UI の絵が全体に暗い | 乗算済みの画像を、ストレートのブレンドで描いた（アルファが二重に、掛かる） |

## よくあるミス

??? failure "半透明テクスチャの縁に、黒い線が出る"
    <strong>乗算済みアルファ</strong>にする（または縁の色を広げる）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 色にアルファを先に掛ける
    - [x] 縁のにじみを防ぎ、式も単純

## 参考

- Smith, "Image Compositing Fundamentals", Microsoft Technical Memo 4, 1995（乗算済みアルファ）
- Porter, Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）
- Microsoft Learn, "D3D11_RENDER_TARGET_BLEND_DESC"（`SrcBlend`、`DestBlend`、`BlendOp`）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [Blend State](blend-state.md)
