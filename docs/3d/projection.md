---
title: 投影（プロジェクション）
tags:
  - 3Dゲーム
---

# 投影（プロジェクション）

<strong>投影（プロジェクション）</strong>は、**3D の世界を、2D の画面に映す**変換です。人間の目やカメラは、**遠くのものが小さく見える**（遠近感）ので、3D ゲームでもそれを計算で再現します。これが**透視投影**です。一方、遠くても大きさが変わらない**正射投影**もあり、2D ゲームや UI、設計図のような絵で使います。プロジェクション行列は、**見える範囲（視錐台）を、標準の箱（クリップ空間）に変換する行列**でさらに「**w に距離を入れる**」という仕組みで遠近感を作り出します。このページは投影の考え方、各パラメータ（視野角、アスペクト比、near / far）の意味、**深度が非線形になる理由**、DirectX 11 での扱いを説明します。

!!! tip "ポイント"
    - <strong>透視投影</strong> ＝ 遠いものが小さい（3D ゲームの普通のカメラ）。<strong>正射投影</strong> ＝ 遠近感なし（2D、UI、設計図）。
    - 透視投影の<strong>パラメータ</strong>は、<strong>視野角（FOV）、アスペクト比、near、far</strong> の 4 つ。
    - <strong>遠近感は、「w に距離を入れて、あとで w で割る」</strong>ことで生まれる（透視除算）。
    - <strong>near は、できるだけ大きく</strong>（0.1 以上）。<strong>near が小さい、far が大きい</strong>と<strong>深度の精度が落ちて、z-fighting</strong> が起きる。
    - 深度は<strong>非線形</strong>（near の近くに精度が集中する）。<strong>reverse-Z</strong>（near と far を入れ替える）で、精度を改善できる。
    - <strong>`proj` は、画面サイズやズームが変わったときだけ</strong>作り直す。

## 視錐台（見える範囲）

カメラから見える 3D の範囲は、<strong>四角錐を、near と far で切り取った形（視錐台：frustum）</strong>です。

<svg class="fig" viewBox="0 0 520 250" role="img" aria-label="視錐台"><circle cx="260" cy="26" r="7" fill="currentColor"/><text x="272" y="22">カメラ（目）</text><line x1="260" y1="26" x2="110" y2="215" stroke="currentColor" stroke-width="2"/><line x1="260" y1="26" x2="410" y2="215" stroke="currentColor" stroke-width="2"/><line x1="215" y1="83" x2="305" y2="83" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/><text x="315" y="87">near 面（これより手前は映らない）</text><line x1="110" y1="215" x2="410" y2="215" stroke="currentColor" stroke-width="2"/><text x="150" y="238">far 面（これより奥は映らない）</text><text x="100" y="110">視野角</text><text x="100" y="128">（FOV）</text><path d="M 232 63 A 45 45 0 0 0 288 63" fill="none" stroke="currentColor"/></svg>

視錐台の**中にあるもの**だけが、画面に映ります。外にあるものは、**クリップ**（切り捨て）されます。

## 透視投影のパラメータ

```cpp
Matrix proj = Matrix::CreatePerspectiveFieldOfView(fov_y, aspect, near_plane, far_plane);
```

| パラメータ | 意味 | 目安 |
| --- | --- | --- |
| **`fov_y`**（視野角） | **縦方向**の視野の広さ（**ラジアン**） | 60〜90 度（FPS は 90 度前後、三人称は 45〜60 度） |
| **`aspect`**（アスペクト比） | 画面の**幅 ÷ 高さ** | `width / (float)height`（16:9 なら 1.78） |
| **`near_plane`** | 一番近い距離（これより手前は映らない） | **0.1** 以上（0 や負は禁止） |
| **`far_plane`** | 一番遠い距離（これより奥は映らない） | ゲームの範囲に合わせる（1000 など） |

### 視野角（FOV）

<svg class="fig" viewBox="0 0 620 220" role="img" aria-label="視野角の違い"><defs><marker id="f1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">視野角（FOV）が小さい：望遠</text><circle cx="80" cy="120" r="6" fill="currentColor"/><line x1="80" y1="120" x2="270" y2="85" stroke="currentColor"/><line x1="80" y1="120" x2="270" y2="155" stroke="currentColor"/><text x="100" y="190">見える範囲が狭く、拡大して見える</text><text x="330" y="20" class="fig-title">視野角が大きい：広角</text><circle cx="360" cy="120" r="6" fill="currentColor"/><line x1="360" y1="120" x2="580" y2="30" stroke="currentColor"/><line x1="360" y1="120" x2="580" y2="210" stroke="currentColor"/><text x="370" y="205">見える範囲が広いが、端が歪んで見える</text></svg>

| FOV | 見え方 |
| --- | --- |
| **小さい**（30〜45°） | 望遠レンズ。遠くが大きく見え、遠近感が弱い。ズーム |
| **中くらい**（60°） | 自然な見え方。三人称ゲーム |
| **大きい**（90〜110°） | 広角レンズ。広く見えるが画面の端が引き伸ばされる。FPS（速さの感覚が強い） |

**縦の FOV**を指定するのが普通です。横の FOV は、アスペクト比で決まります（`横 = 2 × atan(tan(縦 / 2) × aspect)`）。FPS のゲームで「FOV 90」と言うとき、横の FOV のことが多いので、縦に直して使います。

### アスペクト比

**画面の縦横比に合わせない**と、絵が横に伸びたり縮んだりします。**ウィンドウのサイズが変わったら、`proj` を作り直します**。

```cpp
void OnResize(int width, int height) {
  float aspect = static_cast<float>(width) / static_cast<float>(height);
  proj = Matrix::CreatePerspectiveFieldOfView(fov_y, aspect, near_plane, far_plane);
  // ビューポート、深度バッファ、レンダー ターゲットも作り直す
}
```

## 透視投影のしくみ

### 遠近感は「w で割る」から生まれる

<svg class="fig" viewBox="0 0 620 250" role="img" aria-label="遠近感"><defs><marker id="p1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">遠いものが小さく見えるのは、w（距離）で割るから</text><circle cx="60" cy="140" r="6" fill="currentColor"/><text x="40" y="165">カメラ</text><line x1="60" y1="140" x2="520" y2="60" stroke="currentColor" stroke-dasharray="4 4"/><line x1="60" y1="140" x2="520" y2="220" stroke="currentColor" stroke-dasharray="4 4"/><line x1="200" y1="115" x2="200" y2="165" stroke="currentColor" stroke-width="4"/><text x="190" y="105">近い（同じ高さ）</text><line x1="400" y1="85" x2="400" y2="195" stroke="currentColor" stroke-width="4"/><text x="390" y="78">遠い（同じ高さ）</text><line x1="130" y1="125" x2="130" y2="155" stroke="currentColor" stroke-width="2"/><text x="100" y="118">画面</text><text x="20" y="235">同じ高さでも、距離が 2 倍なら、画面の上では、約半分の大きさ（x ÷ w, y ÷ w）</text></svg>

プロジェクション行列は、**ビュー空間の座標をクリップ空間（同次座標 `x, y, z, w`）に変換**します。このとき、**`w` にカメラからの距離が入ります**。

<svg class="fig flow" viewBox="0 0 360 280" role="img" aria-label="透視投影：ビュー空間 → クリップ空間 → NDC"><defs><marker id="fl74520" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">透視投影：ビュー空間 → クリップ空間 → NDC</text><line x1="137.0" y1="87.0" x2="137.0" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl74520)"/><text x="137.0" y="100.0" text-anchor="middle" style="font-size:12px">プロジェクション行列を掛ける</text><line x1="137.0" y1="171.0" x2="137.0" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl74520)"/><text x="137.0" y="184.0" text-anchor="middle" style="font-size:12px">w'で割る（透視除算）</text><rect x="58.0" y="44.0" width="158" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="137.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ビュー空間 (x,y,z)</text><circle cx="60.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="60.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="28.0" y="128.0" width="218" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="137.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">クリップ空間 (x',y',z',w')</text><circle cx="30.0" cy="130.0" r="10" fill="#2ea043"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="35.5" y="212.0" width="203" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="137.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">NDC (x'/w',y'/w',z'/w')</text><circle cx="37.5" cy="214.0" r="10" fill="#e5a828"/><text x="37.5" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

**遠いほど `w` が大きい**ので、`x / w`、`y / w` が小さくなり、画面の中央に寄ります。これが遠近感です。**この割り算は、GPU が自動で行います**（頂点シェーダーが `SV_POSITION` を返したあと）。

<div class="anim" data-label="同じ大きさの物体：近いと大きく、遠いと小さく（w で割る）">
*A *A *A *A _ _ # 近い（w が小さい）：4 マスぶん大きく見える
_ *B *B _ _ _ # 中くらい（w が中間）：2 マスぶん
_ _ *C _ _ _ # 遠い（w が大きい）：1 マスぶん
</div>

### 行列の中身（右手系・行ベクトル）

SimpleMath の `CreatePerspectiveFieldOfView`（右手系）は、次の行列です。

<div class="formula">f = 1 / tan(fovY / 2)</div>
<div class="mat-row"><table class="matrix"><tr><td>f/aspect</td><td>0</td><td>0</td><td>0</td></tr><tr><td>0</td><td>f</td><td>0</td><td>0</td></tr><tr><td>0</td><td>0</td><td>far/(near−far)</td><td class="hl">−1</td></tr><tr><td>0</td><td>0</td><td>near·far/(near−far)</td><td>0</td></tr></table><span class="mat-note">最後の列の −1 が、w に −z を入れる（遠いほど w が大きくなる）</span></div>

| 要素 | 意味 |
| --- | --- |
| `f = 1 / tan(fovY / 2)` | 視野角が小さいほど大きい（拡大率）。x, y をスケール |
| `f / aspect` | 横はアスペクト比で割って、縦横比を合わせる |
| 右下の `-1` | **`w' = -z`**（右手系で前が −Z なので距離が正になる） |
| `far / (near - far)` と `near * far / (near - far)` | **z を、0〜1 の深度に変換**する式（Direct3D の深度範囲）。非線形（後述） |

<strong>暗記する必要はありません。</strong>`w' = −z` が遠近感の元で、z の式が深度の元だ、と知っていれば十分です。

### NDC（正規化デバイス座標）

`w` で割ったあとの座標が **NDC** です。見える範囲は**直方体**になります。

| 軸 | Direct3D（DirectX 11） | OpenGL |
| --- | --- | --- |
| **x** | −1（左）〜 1（右） | −1 〜 1 |
| **y** | −1（下）〜 1（上） | −1 〜 1 |
| <strong>z（深度）</strong> | <strong>0（near）〜 1（far）</strong> | <strong>−1（near）〜 1（far）</strong> |

**この範囲の外**にある三角形（の部分）は、画面に出ません。**クリップ**されます。DirectX と OpenGL では、**深度の範囲が違う**ので行列の式が少し違います。**SimpleMath（DirectXMath）は、0〜1 の Direct3D 用**です。

## 深度が非線形になる理由

NDC の深度 `z'`（0〜1）は、**距離 `z` に対して、非線形**です。

```text
右手系・Direct3D：   z_ndc = far * (near - d) / (d * (near - far)) の形（d = カメラからの距離）
                    ≒ （far / (far - near)） × (1 − near / d)
```

| 距離 | 深度（near = 0.1、far = 1000 の例） |
| --- | --- |
| 0.1（near） | 0.0 |
| 0.2 | 0.5 |
| 1.0 | 0.9 |
| 10 | 0.99 |
| 100 | 0.999 |
| 1000（far） | 1.0 |

<strong>near の近くで深度が急激に変わり、遠くはほとんど変わりません。</strong>つまり、**深度の精度（細かさ）が、手前にたくさん割り当てられ、遠くは粗い**のです。そのため、遠くで 2 つの面が近いと、深度の差を区別できず、**z-fighting**（ちらつき）が起きます（[深度バッファとカリング](depth-culling.md)）。

### 精度を保つ工夫

| 方法 | 説明 |
| --- | --- |
| **near をできるだけ大きく** | 0.01 より 0.1、0.1 より 1。near を 10 倍にすると、精度が約 10 倍よくなる |
| **far を必要最小限に** | 1000 で足りるなら、100000 にしない |
| **reverse-Z** | **near と far を入れ替える**（深度を 1 → 0 にする）。浮動小数点の深度は、0 付近の精度が高いので、遠くの精度が大きく改善する（[深度バッファとカリング](depth-culling.md)） |
| **32 ビット浮動小数点の深度バッファ**（`DXGI_FORMAT_D32_FLOAT`） | 24 ビット整数より、reverse-Z と相性がよい |
| **世界を分割して描く** | 近景と遠景を別の near / far で描く |

## 正射投影 {#orthographic}

**遠近感がない**投影です。遠くても大きさが変わりません。

```cpp
// 画面の幅 × 高さ（ワールド単位）の範囲を映す
Matrix ortho = Matrix::CreateOrthographic(width, height, near_plane, far_plane);

// 左右・上下を、座標で指定する版（UI や 2D の画面ピクセルに合わせるとき）
Matrix ortho2 = Matrix::CreateOrthographicOffCenter(0.0f, width, height, 0.0f, 0.0f, 1.0f);
```

| 使いどころ | 説明 |
| --- | --- |
| **2D ゲーム、UI** | 画面のピクセル座標で位置を指定できる |
| <strong>アイソメトリック（斜め見下ろし）</strong> | 遠近感のない、斜めのカメラ |
| **影の生成**（シャドウ マップ） | 平行光（太陽光）の影を正射投影で描く |
| **設計図・エディターの側面図** | 大きさをそのまま測れる |
| **ミニマップ** | 真上からの正射投影 |

正射投影では、**w が常に 1**（遠近感なし）です。x, y が距離に関係なく、決まった比率で画面に出ます。

## 透視投影と正射投影の比較

| 項目 | 透視投影 | 正射投影 |
| --- | --- | --- |
| 遠近感 | **ある**（遠いと小さい） | ない |
| 視野の形 | 四角錐の台（視錐台） | 直方体 |
| w | 距離が入る（割る） | 常に 1 |
| 平行な線 | 遠くで 1 点に集まる（消失点） | 平行のまま |
| 用途 | **3D ゲームの普通のカメラ** | 2D、UI、影、設計図 |
| 主なパラメータ | 視野角、アスペクト比、near、far | 幅、高さ、near、far |

## 視野角を変える演出

| 演出 | 方法 |
| --- | --- |
| <strong>ズーム（スナイパー）</strong> | FOV を小さくする |
| **ダッシュの疾走感** | FOV を少し大きくする（70 → 80） |
| **被ダメージの歪み** | FOV を一瞬だけ変える |
| **ドリー ズーム**（映画の演出） | カメラを動かしながら、FOV を逆に変える |

FOV を変えたら、`proj` を**作り直します**（毎フレームでも軽い計算です）。滑らかに変えるには、FOV を補間（`Lerp`）します。

## DirectX 11 での設定

プロジェクション行列は、**CPU で作り、`mvp` に含めて、定数バッファで GPU に渡します**（[MVP 変換](transforms-mvp.md)）。深度に関連する、DX11 の設定は、次のとおりです。

| 設定 | 場所 | 説明 |
| --- | --- | --- |
| **ビューポートの深度範囲** | `D3D11_VIEWPORT::MinDepth / MaxDepth` | 0.0 〜 1.0（通常）。reverse-Z でも、このままでよい |
| **深度バッファのフォーマット** | `DXGI_FORMAT_D32_FLOAT` / `D24_UNORM_S8_UINT` | 浮動小数点（D32）は、reverse-Z 向き |
| **深度比較関数** | `D3D11_DEPTH_STENCIL_DESC::DepthFunc` | 通常は `LESS`。**reverse-Z は `GREATER`**（または `GREATER_EQUAL`） |
| **深度バッファのクリア値** | `ClearDepthStencilView` | 通常は 1.0。**reverse-Z は 0.0** |

詳しくは [深度バッファとカリング](depth-culling.md) を見てください。

## ゲームでの使いどころ

| 場面 | 設定 |
| --- | --- |
| 三人称アクション | 透視投影。FOV 50〜60°、near 0.1〜0.3、far 500〜1000 |
| FPS | 透視投影。FOV 80〜100°（横）。武器は別の FOV で描くこともある |
| 2D ゲーム・UI | 正射投影（ピクセル座標） |
| 広い世界（遠景が必要） | far を大きくする代わりに、reverse-Z と D32_FLOAT で、精度を保つ |
| シャドウ マップ（太陽の影） | 正射投影で光の向きから描く |
| スナイパー ライフル | FOV を小さくして、拡大 |
| ウィンドウのリサイズ | アスペクト比を更新して、`proj` を作り直す |

## よくあるミス

??? failure "near を 0 や、ごく小さい値にする"
    near が 0 だと、プロジェクション行列が壊れます（0 で割る）。0.001 のように小さいと、深度の精度が悪くなって、z-fighting が出ます。0.1 以上にします。

??? failure "far を、とても大きくする"
    near と far の比が大きいほど、深度の精度が落ちます。必要な範囲だけにするか、reverse-Z を使います。

??? failure "FOV を度のまま渡す"
    `CreatePerspectiveFieldOfView(60.0f, ...)` は、60 ラジアンです。ラジアン（`XMConvertToRadians(60.0f)`）で渡します。

??? failure "アスペクト比を固定のまま、ウィンドウをリサイズして、絵が伸びる"
    ウィンドウのサイズが変わったら、`aspect` を更新して、`proj` を作り直します。

??? failure "縦の FOV と横の FOV を取り違える"
    `CreatePerspectiveFieldOfView` は、**縦**の FOV です。ゲームの設定画面の「FOV」が横なら、縦に変換します。

??? failure "手系の違うプロジェクション関数を混ぜる"
    `CreatePerspectiveFieldOfView`（右手系）と、`XMMatrixLookAtLH`（左手系）を混ぜると何も映りません。揃えます。

??? failure "透視投影の後ろの点を、そのまま使う"
    `w <= 0` の点は、カメラの後ろです。`w` で割ると反転した位置になります。必ず `w` を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>透視投影</strong> ＝ 遠いものが小さい。<strong>`w` に距離を入れて、`w` で割る</strong>のが遠近感の元
    - [x] パラメータは <strong>視野角（縦・ラジアン）、アスペクト比、near、far</strong>。ウィンドウのサイズが変わったら作り直す
    - [x] <strong>NDC</strong>：x, y は −1〜1、z は <strong>0〜1</strong>（Direct3D）。範囲外はクリップされる
    - [x] <strong>深度は非線形</strong>。near を大きく、far を小さく。<strong>reverse-Z</strong> で、精度を改善
    - [x] <strong>正射投影</strong> ＝ 遠近感なし。2D、UI、影、ミニマップ

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [MVP 変換](transforms-mvp.md)
- [カメラ](camera.md)
- [深度バッファとカリング](depth-culling.md)
- [SimpleMath](simplemath.md)
