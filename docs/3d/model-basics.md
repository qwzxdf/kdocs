---
title: 3D モデルの基礎
tags:
  - 3Dゲーム
---

# 3D モデルの基礎

ゲームに出てくるキャラクターや建物は、**3D モデル**と呼ばれるデータでできています。このページは、**3D モデルが何でできているか**を**ゼロから**説明します。次のページ以降に出てくる言葉（**頂点・ポリゴン・メッシュ・テクスチャ・バッファ**）の意味を先に押さえておくと読みやすくなります。

!!! tip "ポイント"
    - <strong>3D モデル ＝ 形（メッシュ）＋ 表面の絵（テクスチャ）＋ 質感の設定（マテリアル）</strong>。
    - <strong>メッシュ</strong>は、<strong>3D モデルの「形」そのもの</strong>のこと。<strong>三角形をたくさん貼り合わせて</strong>、形を作る。
    - <strong>頂点</strong>は三角形の<strong>角の点</strong>。<strong>三角形</strong>は<strong>頂点 3 つ</strong>でできる（<strong>ポリゴン</strong>とも呼ぶ）。
    - <strong>テクスチャ</strong>は、モデルの表面に<strong>貼る画像</strong>。<strong>UV</strong> は、「画像のどこをどの頂点に貼るか」を表す。
    - <strong>バッファ</strong>は、<strong>GPU が使うデータを置いておく、メモリの置き場</strong>。メッシュのデータは、ここに入れて、GPU に渡す。

## 3D モデルは、何でできているか

3D モデルは、**3 つの部品**でできています。

<svg class="fig illust" viewBox="0 0 760 300" role="img" aria-label="3D モデルは、メッシュ・テクスチャ・マテリアルでできている"><defs><radialGradient id="mg" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#ffffff"/><stop offset="0.4" stop-color="#4c8bf5"/><stop offset="1" stop-color="#16256b"/></radialGradient><pattern id="chk" width="20" height="20" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="#e5484d"/><rect x="10" y="10" width="10" height="10" fill="#e5484d"/><rect x="10" width="10" height="10" fill="#f6c244"/><rect y="10" width="10" height="10" fill="#f6c244"/></pattern></defs><text x="20" y="26" class="fig-title">3D モデル ＝ 形（メッシュ）＋ 表面の絵（テクスチャ）＋ 質感（マテリアル）</text><polygon points="110.0,78.0 172.0,109.0 110.0,140.0 48.0,109.0" fill="rgba(150,150,150,0.15)" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="48.0,109.0 110.0,140.0 110.0,202.0 48.0,171.0" fill="rgba(150,150,150,0.08)" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="110.0,140.0 172.0,109.0 172.0,171.0 110.0,202.0" fill="rgba(150,150,150,0.22)" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="110" cy="78" r="5" fill="#e5484d"/><circle cx="172" cy="109" r="5" fill="#e5484d"/><circle cx="110" cy="140" r="5" fill="#e5484d"/><circle cx="48" cy="109" r="5" fill="#e5484d"/><circle cx="48" cy="171" r="5" fill="#e5484d"/><circle cx="110" cy="202" r="5" fill="#e5484d"/><circle cx="172" cy="171" r="5" fill="#e5484d"/><text x="110" y="250" text-anchor="middle" style="font-size:14px;font-weight:600">メッシュ（形）</text><text x="110" y="272" text-anchor="middle" style="font-size:12px;font-weight:400">頂点と三角形だけ。素体</text><text x="205" y="150" text-anchor="middle" style="font-size:30px;font-weight:700">＋</text><rect x="250" y="80" width="120" height="120" rx="8" fill="url(#chk)" stroke="currentColor" stroke-width="2"/><path d="M 250 80 L 370 80" stroke="currentColor"/><text x="310" y="250" text-anchor="middle" style="font-size:14px;font-weight:600">テクスチャ（絵）</text><text x="310" y="272" text-anchor="middle" style="font-size:12px;font-weight:400">表面に貼る画像。シール</text><text x="405" y="150" text-anchor="middle" style="font-size:30px;font-weight:700">＋</text><circle cx="500" cy="140" r="58" fill="url(#mg)" stroke="currentColor" stroke-width="2"/><ellipse cx="480" cy="116" rx="14" ry="9" fill="rgba(255,255,255,0.85)"/><text x="500" y="250" text-anchor="middle" style="font-size:14px;font-weight:600">マテリアル（質感）</text><text x="500" y="272" text-anchor="middle" style="font-size:12px;font-weight:400">ツヤ・金属・ざらざら。塗料</text><text x="585" y="150" text-anchor="middle" style="font-size:30px;font-weight:700">＝</text><polygon points="670.0,78.0 732.0,109.0 670.0,140.0 608.0,109.0" fill="#f6c244" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="608.0,109.0 670.0,140.0 670.0,202.0 608.0,171.0" fill="#e5484d" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="670.0,140.0 732.0,109.0 732.0,171.0 670.0,202.0" fill="#c93a3f" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><ellipse cx="690" cy="108" rx="10" ry="6" fill="rgba(255,255,255,0.7)"/><text x="670" y="250" text-anchor="middle" style="font-size:14px;font-weight:600">完成した 3D モデル</text><text x="670" y="272" text-anchor="middle" style="font-size:12px;font-weight:400">ゲームで表示するもの</text></svg>

| 部品 | 一言で | 例えると |
| --- | --- | --- |
| **メッシュ**（mesh） | **3D モデルの形そのもの**。三角形の集まり | プラモデルの**白い素体** |
| **テクスチャ**（texture） | 表面に貼る**画像** | 素体に貼る、**シール・塗装** |
| **マテリアル**（material） | 「ツヤがあるか」「金属っぽいか」などの**質感の設定** | 塗料の種類（つや消し・メタリック） |

!!! note "「メッシュ」は、3D モデルの「形」のこと"
    「メッシュ」という言葉は最初は戸惑います。<strong>「3D モデルの形の部分」</strong>と、覚えます。**色や絵（テクスチャ）は、含みません**。**メッシュは形だけ**です。

## 頂点・辺・三角形（ポリゴン）

**3D の形はすべて、三角形の組み合わせ**でできています。曲がった球も**小さな三角形をたくさん貼り合わせて**、丸く見せています。

<svg class="fig" viewBox="0 0 600 260" role="img" aria-label="頂点・辺・三角形（面）">
<polygon points="70,200 190,200 130,80" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/>
<circle cx="70" cy="200" r="6" fill="currentColor"/><circle cx="190" cy="200" r="6" fill="currentColor"/><circle cx="130" cy="80" r="6" fill="currentColor"/>
<text x="30" y="222">頂点 A</text><text x="170" y="222">頂点 B</text><text x="105" y="68">頂点 C</text>
<text x="100" y="170">三角形</text>
<text x="20" y="22" class="fig-title">三角形 ＝ 頂点 3 つ</text>
<text x="20" y="245">頂点を結ぶ線が「辺」。囲まれた面が「ポリゴン」</text>
<text x="290" y="22" class="fig-title">三角形を貼り合わせると、形になる</text>
<polygon points="300,200 380,200 340,120" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/>
<polygon points="380,200 460,200 420,120 340,120" fill="rgba(76,139,245,0.12)" stroke="currentColor" stroke-width="2"/>
<line x1="380" y1="200" x2="420" y2="120" stroke="currentColor" stroke-width="2"/>
<polygon points="340,120 420,120 380,50" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/>
<polygon points="460,200 540,200 500,120 420,120" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/>
<line x1="460" y1="200" x2="500" y2="120" stroke="currentColor" stroke-width="2"/>
<text x="300" y="245">三角形が増えるほど、細かい形を作れる</text>
</svg>

| 用語 | 意味 |
| --- | --- |
| **頂点**（vertex） | 形の**角の点**。座標 `(x, y, z)` を持つ |
| **辺**（edge） | 頂点と頂点を結ぶ線 |
| **三角形 / ポリゴン**（polygon） | 頂点 3 つで囲まれた**面**。3D 描画の**基本単位** |
| **面**（face） | ポリゴンと同じ意味で使う |

!!! note "なぜ、三角形なのか"
    **3 つの点は必ず 1 つの平面を作る**からです。4 つ以上の点は、同じ平面にならないことがあります。**GPU は三角形を高速に描く**ように作られています。四角形は**三角形 2 つ**に分けて扱います。

### 頂点が持つ情報

頂点は**位置**だけでなく、**描画に必要な情報**を持たせます。

| 情報 | 意味 | 何のために |
| --- | --- | --- |
| **位置** | 3D 空間の座標 | **形そのもの** |
| **法線** | その点の**面が向いている方向** | 陰影をつける（[法線とライティング](lighting-normals.md)） |
| **UV** | **テクスチャ画像のどこを使うか** | 表面に絵を貼る |

## 頂点を三角形にまとめる（インデックス）

**四角形**を描くには、**三角形 2 つ**が必要です。頂点は 4 つですが**三角形 2 つの頂点は、合計 6 個**になります（**2 つが重複**します）。

<svg class="fig" viewBox="0 0 600 220" role="img" aria-label="頂点の共有（インデックス）">
<polygon points="60,40 190,40 190,170 60,170" fill="none" stroke="currentColor" stroke-width="2"/>
<line x1="60" y1="170" x2="190" y2="40" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/>
<text x="30" y="35">v3</text><text x="196" y="35">v2</text><text x="30" y="188">v0</text><text x="196" y="188">v1</text>
<text x="90" y="95">三角形 B</text><text x="80" y="150">三角形 A</text>
<text x="260" y="40" class="fig-title">頂点を 4 つだけ並べる</text>
<text x="260" y="65">頂点リスト：  v0  v1  v2  v3</text>
<text x="260" y="105" class="fig-title">三角形を「番号」で指定する</text>
<text x="260" y="130">三角形 A：  0 → 1 → 2</text>
<text x="260" y="152">三角形 B：  0 → 2 → 3</text>
<text x="260" y="190">v0 と v2 は、2 つの三角形で共有される</text>
</svg>

| 用語 | 意味 |
| --- | --- |
| **頂点リスト** | 頂点を**重複なしで**並べたもの |
| **インデックス**（index） | <strong>「どの頂点をどの順で三角形にするか」を、番号で書いたリスト</strong>（`0 1 2、0 2 3`） |

**インデックスを使うと同じ頂点を何度も書かなくて済みます**。立方体なら、頂点を 8 個に三角形（12 個）を、インデックスで表せます。

## テクスチャと UV

**テクスチャ**はモデルの表面に貼る**画像**です。レンガの壁、キャラクターの服の柄、金属の傷などは、テクスチャで表します。**形（メッシュ）を細かくしなくても見た目を豊かに**できます。

### UV：どこに貼るか

3D の形に、2D の画像を貼るには、<strong>「画像のどの部分をどの頂点に貼るか」</strong>を決める必要があります。これが **UV 座標**です。

<svg class="fig" viewBox="0 0 600 240" role="img" aria-label="UV でテクスチャを貼る">
<defs><marker id="mb1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">テクスチャ（2D の画像）</text>
<rect x="30" y="40" width="150" height="150" fill="rgba(229,72,77,0.25)" stroke="currentColor" stroke-width="2"/>
<polygon points="45,175 165,175 105,60" fill="rgba(76,139,245,0.4)" stroke="currentColor" stroke-width="2"/>
<text x="36" y="206">(0,1)</text><text x="132" y="206">(1,1)</text><text x="76" y="52">(0.5, 0.1)</text>
<text x="30" y="226">画像の、この三角形の部分を使う</text>
<line x1="200" y1="115" x2="300" y2="115" stroke="currentColor" stroke-width="2" marker-end="url(#mb1)"/>
<text x="205" y="105">貼る</text>
<text x="320" y="22" class="fig-title">3D の三角形</text>
<polygon points="340,190 500,190 420,60" fill="rgba(76,139,245,0.4)" stroke="currentColor" stroke-width="2"/>
<text x="318" y="210">頂点 A(0,1)</text><text x="470" y="210">頂点 B(1,1)</text><text x="385" y="52">頂点 C(0.5,0.1)</text>
<text x="320" y="230">頂点ごとに「画像の座標」を持つ</text>
</svg>

| 用語 | 意味 |
| --- | --- |
| **UV 座標** | **画像の中の位置**を表す、**2 つの数字** `(u, v)`。`(0, 0)` ～ `(1, 1)` の範囲 |
| **U** | 画像の**横方向**（左 → 右） |
| **V** | 画像の**縦方向**（DirectX は、上 → 下） |
| **テクセル** | テクスチャの**1 マス**（ピクセルの画像側の呼び方） |

**3 つの頂点の UV が決まれば、三角形の中の絵は、自動で補間**されます。

## GPU とバッファ

**GPU**（ジーピーユー）は、**画面に絵を描く専用の部品**（グラフィックスカード）です。GPU は**自分専用のメモリ**を持っています。

3D モデルを描くには、**メッシュのデータを、GPU のメモリにあらかじめ置いておきます**。この**置き場所**を**バッファ**と呼びます。

<svg class="fig illust" viewBox="0 0 800 300" role="img" aria-label="メッシュのデータを、GPU のバッファに置いてから、描画する"><defs><marker id="gb1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs><text x="20" y="26" class="fig-title">メッシュのデータは、起動時に 1 回だけ GPU のバッファへ。描画のたびに、使い回す</text><path d="M 24 96 L 76 96 L 96 116 L 96 196 L 24 196 Z" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/><text x="60" y="160" text-anchor="middle" style="font-size:14px;font-weight:700">モデル</text><text x="60" y="232" text-anchor="middle" style="font-size:14px;font-weight:700">ファイル</text><line x1="104" y1="146" x2="160" y2="146" stroke="currentColor" stroke-width="3" marker-end="url(#gb1)"/><text x="132" y="136" text-anchor="middle" style="font-size:12px;font-weight:600">読む</text><rect x="170" y="86" width="150" height="120" rx="10" fill="rgba(76,139,245,0.2)" stroke="currentColor" stroke-width="3"/><line x1="190" y1="86" x2="190" y2="72" stroke="currentColor" stroke-width="3"/><line x1="190" y1="206" x2="190" y2="220" stroke="currentColor" stroke-width="3"/><line x1="214" y1="86" x2="214" y2="72" stroke="currentColor" stroke-width="3"/><line x1="214" y1="206" x2="214" y2="220" stroke="currentColor" stroke-width="3"/><line x1="238" y1="86" x2="238" y2="72" stroke="currentColor" stroke-width="3"/><line x1="238" y1="206" x2="238" y2="220" stroke="currentColor" stroke-width="3"/><line x1="262" y1="86" x2="262" y2="72" stroke="currentColor" stroke-width="3"/><line x1="262" y1="206" x2="262" y2="220" stroke="currentColor" stroke-width="3"/><line x1="286" y1="86" x2="286" y2="72" stroke="currentColor" stroke-width="3"/><line x1="286" y1="206" x2="286" y2="220" stroke="currentColor" stroke-width="3"/><text x="245" y="120" text-anchor="middle" style="font-size:14px;font-weight:700">CPU 側のメモリ</text><rect x="186" y="140" width="18" height="40" rx="2" fill="#4c8bf5"/><rect x="208" y="140" width="18" height="40" rx="2" fill="#4c8bf5"/><rect x="230" y="140" width="18" height="40" rx="2" fill="#4c8bf5"/><rect x="252" y="140" width="18" height="40" rx="2" fill="#4c8bf5"/><rect x="274" y="140" width="18" height="40" rx="2" fill="#4c8bf5"/><rect x="296" y="140" width="18" height="40" rx="2" fill="#4c8bf5"/><text x="245" y="250" text-anchor="middle" style="font-size:14px;font-weight:700">頂点・インデックス</text><line x1="330" y1="146" x2="412" y2="146" stroke="currentColor" stroke-width="3" marker-end="url(#gb1)"/><text x="371" y="134" text-anchor="middle" style="font-size:13px;font-weight:700">転送</text><text x="371" y="170" text-anchor="middle" style="font-size:12px;font-weight:400">（1 回だけ）</text><rect x="420" y="86" width="170" height="120" rx="10" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="3"/><line x1="420" y1="106" x2="406" y2="106" stroke="currentColor" stroke-width="3"/><line x1="590" y1="106" x2="604" y2="106" stroke="currentColor" stroke-width="3"/><line x1="420" y1="128" x2="406" y2="128" stroke="currentColor" stroke-width="3"/><line x1="590" y1="128" x2="604" y2="128" stroke="currentColor" stroke-width="3"/><line x1="420" y1="150" x2="406" y2="150" stroke="currentColor" stroke-width="3"/><line x1="590" y1="150" x2="604" y2="150" stroke="currentColor" stroke-width="3"/><line x1="420" y1="172" x2="406" y2="172" stroke="currentColor" stroke-width="3"/><line x1="590" y1="172" x2="604" y2="172" stroke="currentColor" stroke-width="3"/><text x="505" y="120" text-anchor="middle" style="font-size:14px;font-weight:700">GPU のバッファ</text><rect x="440" y="136" width="130" height="50" rx="6" fill="rgba(255,255,255,0.25)" stroke="currentColor" stroke-width="2"/><rect x="448" y="146" width="14" height="30" rx="2" fill="#2ea043"/><rect x="468" y="146" width="14" height="30" rx="2" fill="#2ea043"/><rect x="488" y="146" width="14" height="30" rx="2" fill="#2ea043"/><rect x="508" y="146" width="14" height="30" rx="2" fill="#2ea043"/><rect x="528" y="146" width="14" height="30" rx="2" fill="#2ea043"/><rect x="548" y="146" width="14" height="30" rx="2" fill="#2ea043"/><text x="505" y="250" text-anchor="middle" style="font-size:14px;font-weight:700">頂点バッファ・インデックスバッファ</text><line x1="600" y1="146" x2="672" y2="146" stroke="currentColor" stroke-width="3" marker-end="url(#gb1)"/><text x="636" y="134" text-anchor="middle" style="font-size:12px;font-weight:600">毎フレーム</text><text x="636" y="170" text-anchor="middle" style="font-size:12px;font-weight:400">使い回す</text><rect x="680" y="96" width="100" height="80" rx="8" fill="rgba(229,170,40,0.2)" stroke="currentColor" stroke-width="3"/><rect x="718" y="176" width="24" height="12" fill="currentColor" opacity="0.5"/><rect x="704" y="188" width="52" height="8" rx="3" fill="currentColor" opacity="0.5"/><polygon points="730.0,118.0 752.0,129.0 730.0,140.0 708.0,129.0" fill="#f6c244" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="708.0,129.0 730.0,140.0 730.0,162.0 708.0,151.0" fill="#e5484d" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="730.0,140.0 752.0,129.0 752.0,151.0 730.0,162.0" fill="#c93a3f" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><text x="730" y="250" text-anchor="middle" style="font-size:14px;font-weight:700">画面</text></svg>

| 用語 | 意味 |
| --- | --- |
| **頂点バッファ** | **頂点リスト**を入れる、GPU 側の置き場 |
| **インデックスバッファ** | <strong>インデックス（三角形の番号リスト）</strong>を入れる、GPU 側の置き場 |
| **定数バッファ** | **行列や色**など、**少数の値**をシェーダーに渡す置き場（[変換と MVP](transforms-mvp.md)） |

!!! note "毎フレーム作らない"
    GPU への転送は**時間がかかる**ので、**ゲームの起動時やロード時に、1 回**やります。**毎フレームの描画**では、**置いてあるデータを使い回す**だけです。

## 入力レイアウト（頂点の並びの説明書）

頂点バッファに入っているのは、**ただの数字の並び**です。GPU は、「**最初の 12 バイトが位置、次の 12 バイトが法線**」という、**中身の意味を知りません**。そこで**並びを説明する**のが**入力レイアウト**です。

<svg class="fig" viewBox="0 0 600 170" role="img" aria-label="頂点バッファの中身と入力レイアウト">
<rect x="30" y="50" width="150" height="40" fill="rgba(76,139,245,0.35)" stroke="currentColor" stroke-width="2"/><text x="55" y="75">位置 (x, y, z)</text>
<rect x="180" y="50" width="150" height="40" fill="rgba(46,160,67,0.35)" stroke="currentColor" stroke-width="2"/><text x="205" y="75">法線 (x, y, z)</text>
<rect x="330" y="50" width="100" height="40" fill="rgba(229,170,40,0.4)" stroke="currentColor" stroke-width="2"/><text x="350" y="75">UV (u, v)</text>
<rect x="430" y="50" width="150" height="40" fill="rgba(76,139,245,0.15)" stroke="currentColor" stroke-width="2"/><text x="455" y="75">次の頂点の位置…</text>
<text x="30" y="30" class="fig-title">頂点バッファの中身（1 頂点ぶん）</text>
<text x="30" y="125">入力レイアウト：「0 バイト目から float 3 つ ＝ 位置、12 バイト目から float 3 つ ＝ 法線、24 バイト目から float 2 つ ＝ UV」</text>
<text x="30" y="148">と、GPU に教える</text>
</svg>

## ここまでの用語まとめ

| 用語 | 一言で |
| --- | --- |
| **3D モデル** | 形・絵・質感のセット |
| **メッシュ** | **3D モデルの形そのもの**（三角形の集まり） |
| **頂点** | 三角形の角の点。位置・法線・UV を持つ |
| **三角形 / ポリゴン** | 頂点 3 つの面。形の最小単位 |
| **インデックス** | 三角形を頂点の番号で指定するリスト |
| **テクスチャ** | 表面に貼る画像 |
| **UV** | 画像のどこを使うかの座標 |
| **マテリアル** | 質感の設定（色・ツヤ・金属度など） |
| **GPU** | 描画専用の部品 |
| **バッファ** | GPU に渡すデータを置く場所 |
| **入力レイアウト** | 頂点バッファの中身の並びを、GPU に教える説明書 |
| **シェーダー** | GPU 上で動く、頂点や色を計算する小さなプログラム |

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>3D モデル ＝ メッシュ（形）＋ テクスチャ（絵）＋ マテリアル（質感）</strong>
    - [x] <strong>メッシュは「形そのもの」</strong>。<strong>三角形（頂点 3 つ）の集まり</strong>
    - [x] <strong>頂点は、位置・法線・UV</strong> などを持つ。<strong>インデックス</strong>で頂点を使い回す
    - [x] <strong>テクスチャは貼る画像</strong>。<strong>UV でどこを貼るかを決める</strong>
    - [x] <strong>バッファは GPU のデータ置き場</strong>。<strong>起動時に 1 回</strong>転送して、使い回す

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [メッシュとテクスチャ](mesh-textures.md)（DX11 でのバッファ・テクスチャの作り方）
- [法線とライティング](lighting-normals.md)
- [PBR（物理ベースレンダリング）](pbr.md)
