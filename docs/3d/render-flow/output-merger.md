---
title: 深度・ブレンド
tags:
  - 3Dゲーム
  - 描画
---

# 深度・ブレンド

**ピクセル シェーダーが色を決めても、すぐ画面に書かれるわけではありません**。**書き込む前に「その色を書いてよいか」「すでにある色とどう混ぜるか」を決める最後の工程**があります。**出力マージャー**（Output Merger）と呼ばれ、**深度テスト・ステンシルテスト・ブレンド**を行います。**手前にある物が奥の物を隠す**のも、**半透明の物が透けて見える**のも**この工程**です。

!!! tip "ポイント"
    - 出力マージャー ＝ <strong>書き込む前の最後の関門</strong>：<strong>① 深度テスト → ② ステンシル → ③ ブレンド → ④ 書き込み</strong>。
    - <strong>深度テスト</strong> ＝ <strong>今のピクセルが、すでに描かれた物より手前か</strong>。<strong>手前なら書く、奥なら捨てる</strong>。
    - <strong>深度バッファ</strong>は<strong>ピクセルごとの「一番手前の距離」を覚える画像</strong>。
    - <strong>ステンシル</strong> ＝ <strong>ピクセルごとの整数マスク</strong>。<strong>描く範囲を限定する</strong>。
    - <strong>ブレンド</strong> ＝ <strong>新しい色と既存の色を、式で混ぜる</strong>。<strong>半透明・加算など</strong>。
    - <strong>描く順番</strong>が<strong>重要</strong>：<strong>不透明は手前から（高速）、半透明は奥から</strong>。

## 全体の位置

<svg class="fig illust" viewBox="0 0 780 180" role="img" aria-label="出力マージャーの流れ"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">ピクセル シェーダーの後：深度 → ステンシル → ブレンド → 書き込み</text>
<g font-size="12">
<rect x="20" y="60" width="150" height="70" rx="8" fill="#9664e6" fill-opacity="0.2" stroke="#9664e6" stroke-width="2"/><text x="95" y="90" text-anchor="middle" style="font-weight:700">ピクセル</text><text x="95" y="110" text-anchor="middle" style="font-weight:700">シェーダー</text>
<rect x="210" y="60" width="130" height="70" rx="8" fill="#e5484d" fill-opacity="0.2" stroke="#e5484d" stroke-width="2"/><text x="275" y="90" text-anchor="middle" style="font-weight:700">深度テスト</text><text x="275" y="110" text-anchor="middle" style="font-size:11px">手前か？</text>
<rect x="380" y="60" width="130" height="70" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/><text x="445" y="90" text-anchor="middle" style="font-weight:700">ステンシル</text><text x="445" y="110" text-anchor="middle" style="font-size:11px">許可された範囲か？</text>
<rect x="550" y="60" width="100" height="70" rx="8" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043" stroke-width="2"/><text x="600" y="90" text-anchor="middle" style="font-weight:700">ブレンド</text><text x="600" y="110" text-anchor="middle" style="font-size:11px">混ぜる</text>
<rect x="690" y="60" width="70" height="70" rx="8" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5" stroke-width="2"/><text x="725" y="90" text-anchor="middle" style="font-weight:700">書込</text><text x="725" y="110" text-anchor="middle" style="font-size:11px">画像へ</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="172" y1="95" x2="208" y2="95" marker-end="url(#rfa)"/><line x1="342" y1="95" x2="378" y2="95" marker-end="url(#rfa)"/><line x1="512" y1="95" x2="548" y2="95" marker-end="url(#rfa)"/><line x1="652" y1="95" x2="688" y2="95" marker-end="url(#rfa)"/></g>
<text x="275" y="160" text-anchor="middle" style="font-size:11px;fill:#e5484d">奥なら捨てる</text>
<text x="445" y="160" text-anchor="middle" style="font-size:11px;fill:#e5aa28">範囲外なら捨てる</text>
</svg>

## 深度テスト

**3D では手前の物が奥の物を隠します**。**描く順番に関係なく、手前が勝つ**ように**ピクセルごとの「今までで一番手前の距離」を深度バッファに記録**します。

<svg class="fig illust motion" data-fig="depth-test" viewBox="0 0 780 300" role="img" aria-label="深度テスト">
<text x="20" y="24" class="fig-title">深度テスト：描く順番が逆でも、手前の物が勝つ</text>
<g transform="translate(40,50)">
<text x="0" y="-6" style="font-size:12px;font-weight:700">① 先に奥の青い四角を描く</text>
<rect x="0" y="0" width="150" height="120" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<rect x="30" y="20" width="90" height="80" fill="#4c8bf5" fill-opacity="0.8"/>
<text x="75" y="64" text-anchor="middle" style="font-size:12px;fill:#fff">奥(0.8)</text>
<text x="0" y="146" style="font-size:11px">深度バッファ：</text><text x="0" y="162" style="font-size:11px">この範囲は 0.8 を記録</text>
</g>
<g transform="translate(270,50)">
<text x="0" y="-6" style="font-size:12px;font-weight:700">② 後から手前の赤い四角を描く</text>
<rect x="0" y="0" width="150" height="120" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<rect x="30" y="20" width="90" height="80" fill="#4c8bf5" fill-opacity="0.8"/>
<rect x="60" y="40" width="70" height="70" fill="#e5484d" fill-opacity="0.9"/>
<text x="95" y="80" text-anchor="middle" style="font-size:12px;fill:#fff">手前(0.3)</text>
<text x="0" y="146" style="font-size:11px">0.3 は 0.8 より手前 → 書く</text><text x="0" y="162" style="font-size:11px">深度を 0.3 に更新</text>
</g>
<g transform="translate(500,50)">
<text x="0" y="-6" style="font-size:12px;font-weight:700">③ 逆順でも結果は同じ</text>
<rect x="0" y="0" width="150" height="120" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<rect x="60" y="40" width="70" height="70" fill="#e5484d" fill-opacity="0.9"/>
<rect x="30" y="20" width="90" height="80" fill="#4c8bf5" fill-opacity="0.8"/>
<rect x="60" y="40" width="70" height="70" fill="#e5484d" fill-opacity="0.95"/>
<text x="0" y="146" style="font-size:11px">先に赤(0.3)を描き、青(0.8)は</text><text x="0" y="162" style="font-size:11px">0.8 は 0.3 より奥 → 重なる所は捨てる</text>
</g>
<text x="40" y="270" style="font-size:13px">深度が小さい（手前）ほうが勝つ。描画の順番に関係なく、手前が必ず見える。</text>
</svg>

| 設定 | 意味 |
| --- | --- |
| **`DepthEnable`** | **深度テストを使う** |
| **`DepthFunc = LESS`** | **今の深度 < 記録された深度 のとき通す**（手前なら通す） |
| **`DepthWriteMask = ALL`** | **通ったら深度バッファを更新**（半透明では `ZERO`＝更新しない） |
| **`LESS_EQUAL`** | **同じ深度も通す**（空・多パスの重ね描きで使う） |

```cpp
D3D11_DEPTH_STENCIL_DESC desc = {};
desc.DepthEnable = TRUE;
desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;
desc.DepthFunc = D3D11_COMPARISON_LESS;
device->CreateDepthStencilState(&desc, depth_state.GetAddressOf());
context->OMSetDepthStencilState(depth_state.Get(), 0);
```

### 深度バッファの中身

**深度バッファは、描画先と同じ大きさの 2D の画像**で、**各ピクセルに 0〜1 の深度値**を**持ちます**。**フレームの始めに 1（一番奥）で初期化**します（**クリア**）。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="深度バッファ">
<text x="20" y="24" class="fig-title">カラー バッファと深度バッファ：同じ大きさの 2 枚の画像</text>
<g transform="translate(60,50)">
<rect x="0" y="0" width="240" height="150" fill="#87ceeb" fill-opacity="0.35" stroke="currentColor"/>
<rect x="60" y="50" width="70" height="100" fill="#a0763c" fill-opacity="0.8"/>
<circle cx="180" cy="90" r="36" fill="#e5484d" fill-opacity="0.8"/>
<text x="120" y="176" text-anchor="middle" style="font-size:12px;font-weight:700">カラー バッファ（見える絵）</text>
</g>
<g transform="translate(400,50)">
<defs><linearGradient id="dpg" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#222"/></linearGradient></defs>
<rect x="0" y="0" width="240" height="150" fill="#f4f4f4" stroke="currentColor"/>
<rect x="60" y="50" width="70" height="100" fill="#777"/>
<circle cx="180" cy="90" r="36" fill="#bbb"/>
<text x="120" y="176" text-anchor="middle" style="font-size:12px;font-weight:700">深度バッファ（白＝遠い、黒＝近い）</text>
</g>
<text x="400" y="228" style="font-size:12px">近い物ほど暗く（小さい値）。空は一番奥の 1.0（白）。</text>
</svg>

**深度バッファは、描画の仕組み以外にも使われます**。**ライティング（ピクセルの位置の再構築）・SSAO・フォグ・水の深度差**など、**後の工程が深度を読みます**。

## ステンシル

**ステンシル**は**ピクセルごとに 8 ビットの整数を持つバッファ**で、<strong>「描く範囲」を絞る</strong>のに**使います**（深度バッファと 1 枚にまとめる、24 ビット深度 + 8 ビットステンシルが一般的）。

| 用途 | 内容 |
| --- | --- |
| **マスク** | **窓や鏡の枠の中だけに描く** |
| **アウトライン** | **キャラクター本体のあるピクセルを 1 にして、その外側だけ輪郭色で描く** |
| **シルエット表示** | **壁の向こうの味方を隠れた部分だけ別の色で描く** |
| **影のボリューム** | **古い影の方式** |
| **デカール・ライト ボリューム** | **ライトが影響するピクセルだけ**を**計算する** |

**テスト条件と更新方法を、表側・裏側で別々に設定できます**。

## ブレンド

**色を書くとき、すでにある色とどう混ぜるか**を**決めるのが**ブレンド<strong>です。</strong>半透明（ガラス・煙）・加算（光・炎）**などを**実現します**。

<div class="formula">結果 = 新しい色 × 係数 A　⊕　既存の色 × 係数 B　（⊕：足す・引くなど）</div>

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="ブレンド">
<text x="20" y="24" class="fig-title">ブレンドの種類：同じ赤い円を、青い背景に描く</text>
<g transform="translate(40,50)">
<rect x="0" y="0" width="150" height="120" fill="#4c8bf5"/>
<circle cx="75" cy="60" r="40" fill="#e5484d"/>
<text x="75" y="150" text-anchor="middle" style="font-size:12px;font-weight:700">不透明（上書き）</text>
<text x="75" y="170" text-anchor="middle" style="font-size:11px">新 × 1 ＋ 既存 × 0</text>
</g>
<g transform="translate(230,50)">
<rect x="0" y="0" width="150" height="120" fill="#4c8bf5"/>
<circle cx="75" cy="60" r="40" fill="#e5484d" fill-opacity="0.5"/>
<text x="75" y="150" text-anchor="middle" style="font-size:12px;font-weight:700">アルファ ブレンド</text>
<text x="75" y="170" text-anchor="middle" style="font-size:11px">新 × α ＋ 既存 × (1−α)</text>
</g>
<g transform="translate(420,50)">
<rect x="0" y="0" width="150" height="120" fill="#4c8bf5"/>
<circle cx="75" cy="60" r="40" fill="#e5484d" style="mix-blend-mode:screen" opacity="0.9"/>
<circle cx="75" cy="60" r="40" fill="#ffd0a0" fill-opacity="0.35"/>
<text x="75" y="150" text-anchor="middle" style="font-size:12px;font-weight:700">加算</text>
<text x="75" y="170" text-anchor="middle" style="font-size:11px">新 × 1 ＋ 既存 × 1（明るくなる）</text>
</g>
<g transform="translate(610,50)">
<rect x="0" y="0" width="150" height="120" fill="#4c8bf5"/>
<circle cx="75" cy="60" r="40" fill="#1a2c55" fill-opacity="0.75"/>
<text x="75" y="150" text-anchor="middle" style="font-size:12px;font-weight:700">乗算</text>
<text x="75" y="170" text-anchor="middle" style="font-size:11px">新 × 既存（暗くなる）</text>
</g>
</svg>

| ブレンド | 式（係数） | 使い道 |
| --- | --- | --- |
| **不透明** | **1, 0** | **ふつうの物体** |
| **アルファ ブレンド** | **α, 1 − α** | **ガラス・半透明の物・UI** |
| **加算** | **1, 1** | **光る物・炎・魔法の粒子** |
| **乗算** | **0, 元の色** | <strong>影・色付きガラス（暗くする）</strong> |
| **プリマルチプライド アルファ** | **1, 1 − α** | **粒子で加算と半透明を混ぜたいとき** |

```cpp
D3D11_BLEND_DESC desc = {};
auto& rt = desc.RenderTarget[0];
rt.BlendEnable = TRUE;
rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOp = D3D11_BLEND_OP_ADD;
rt.SrcBlendAlpha = D3D11_BLEND_ONE;
rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&desc, blend_state.GetAddressOf());
```

## 描く順番が大事

**不透明な物**は**深度テストがあるので順番に関係なく正しく描かれます**。**でも手前から描くほうが速い**です。**半透明な物**は**深度に頼れないので奥から手前の順に描きます**。

<svg class="fig illust" viewBox="0 0 780 270" role="img" aria-label="描画順"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">描画の順番：不透明 → 半透明</text>
<g font-size="12">
<rect x="30" y="60" width="200" height="110" rx="8" fill="#4c8bf5" fill-opacity="0.15" stroke="#4c8bf5" stroke-width="2"/>
<text x="130" y="84" text-anchor="middle" style="font-weight:700">① 不透明</text>
<text x="46" y="110">・手前から奥へ（高速）</text><text x="46" y="130">・深度を書く</text><text x="46" y="150">・ブレンドなし</text>
<rect x="290" y="60" width="200" height="110" rx="8" fill="#9664e6" fill-opacity="0.15" stroke="#9664e6" stroke-width="2"/>
<text x="390" y="84" text-anchor="middle" style="font-weight:700">② 空</text>
<text x="306" y="110">・最奥のピクセルだけ</text><text x="306" y="130">・深度テストあり</text><text x="306" y="150">・深度は書かない</text>
<rect x="550" y="60" width="200" height="110" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/>
<text x="650" y="84" text-anchor="middle" style="font-weight:700">③ 半透明</text>
<text x="566" y="110">・奥から手前へ（ソート）</text><text x="566" y="130">・深度テストのみ（書かない）</text><text x="566" y="150">・ブレンドあり</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="232" y1="115" x2="288" y2="115" marker-end="url(#rfa)"/><line x1="492" y1="115" x2="548" y2="115" marker-end="url(#rfa)"/></g>
<text x="20" y="215" style="font-size:13px">半透明を奥から手前へ描くのは、「手前の物の下に奥の物が透けて見える」ように混ぜるため。</text>
<text x="20" y="240" style="font-size:13px">順番を間違えると、透けるはずの物が消えたり、不自然に見える（詳細：半透明のソート）。</text>
</svg>

## 複数の描画先（MRT）

**1 回のドロー コールで、複数の画像に同時に書き込む**ことが**できます**（Multiple Render Targets）。**ディファード レンダリングで、色・法線・材質を別々の画像に書く**ときに使います。

```hlsl
struct PSOutput {
  float4 albedo : SV_Target0;
  float4 normal : SV_Target1;
  float4 material : SV_Target2;
};
```

**G バッファ**など、**この仕組みを使う方式**は[フォワードとディファード](../../rendering/forward-deferred.md)で扱います。

## 早期深度テスト（Early-Z）

**深度テストはピクセル シェーダーの後**ですが、**GPU は結果が同じなら、ピクセル シェーダーの前に深度テストを行います**（**Early-Z**）。**隠れているピクセルのシェーダー計算を省略できます**。

| 条件 | 効果 |
| --- | --- |
| **ピクセル シェーダーが深度を変更しない** | **Early-Z が有効** |
| **`discard`（クリップ）を使う** | **Early-Z が使えない場合がある**（**アルファ テストの物は遅くなる**） |
| **手前から描く** | **隠れるピクセルが前もって捨てられる** |
| **深度プリパス** | **先に深度だけ描いて、後で色を描く**（**オーバードローを完全に省く**） |

詳しくは[オーバードロー](../../rendering/overdraw.md)で扱います。

## よくあるミス

??? failure "半透明の物が、奥の物を消してしまう"
    **半透明は深度の書き込みを切る**（`DepthWriteMask = ZERO`）。**奥から手前の順に描く**。

??? failure "深度バッファをクリアし忘れて、前フレームの絵が残る／消える"
    **毎フレーム、深度を 1.0 でクリア**する。

??? failure "近い面と遠い面を極端に設定して、遠くで Z ファイティング（ちらつき）"
    **近い面を遠ざける**、**リバース Z（1 が近い）と 32 ビット浮動小数の深度**を使う。

??? failure "深度とカラーの描画先の大きさが違い、描画されない"
    **深度ステンシルとレンダー ターゲットは同じ大きさ**にする。

??? failure "ブレンドの順序で、パーティクルの明るさが変わる"
    **加算は順序に依らない**が、**アルファ ブレンドは順序で変わる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力マージャー ＝ <strong>深度テスト → ステンシル → ブレンド → 書き込み</strong>
    - [x] <strong>深度テスト</strong> ＝ <strong>手前なら書く</strong>。<strong>描く順番に依らず、手前が勝つ</strong>
    - [x] <strong>ステンシル</strong>は<strong>描く範囲を絞るマスク</strong>
    - [x] <strong>ブレンド</strong>で<strong>半透明・加算・乗算</strong>。<strong>半透明は奥から手前、深度は書かない</strong>
    - [x] <strong>Early-Z</strong>で<strong>隠れたピクセルのシェーダーを省く</strong>。<strong>手前から描くと効く</strong>

## 参考

- Microsoft, "Output-Merger Stage"（Microsoft Learn）
- Microsoft, "Depth-Stencil State"・"Blend State"（Microsoft Learn）
- Fabian Giesen, "A trip through the Graphics Pipeline 2011"（Part 9）

## 関連ページ

- [描画の流れ（入門）](index.md)
- [ピクセルの色](pixel-shader.md)
- [画面に出す](present.md)
- [深度とカリング](../depth-culling.md)
- [ブレンドとソート](../../graphics/translucency/blending-sorting.md)
