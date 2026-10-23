---
title: 座標系と格子
tags:
  - ゲーム数学
---

# 座標系と格子

ゲームでは**同じ位置をいろいろな座標で表す**ことがよくあります。マウスの位置は画面のピクセル、キャラの位置はワールド座標、マップのマス目はタイル座標、全方位の弾は極座標、といった具合です。座標系どうしを行き来する計算を知っておくと、タイルマップ・UI・レーダー・全方位の演出がすっきり書けます。このページでは、極座標・グリッド座標・ヘックス座標・アイソメトリック・画面座標を説明します。3D の座標変換（行列）は[3D のセクション](../3d/index.md)を参照してください。

!!! tip "ポイント"
    - 座標は<strong>「何を原点にして、どの向きに数えるか」</strong>で変わる。<strong>変換式を持っておく</strong>。
    - 極座標（角度と距離）は、円運動・全方位に向く。デカルト座標との相互変換は、sin / cos と atan2。
    - タイルマップはワールド座標 ÷ タイルサイズ ＝ セル番号。負の座標の丸めに注意。
    - ヘックスはキューブ座標（x + y + z = 0）が扱いやすい。
    - アイソメトリックは2 つの軸を斜めにする変換。描画の順番（奥から手前）に注意。
    - 画面座標は Y が下向きが多い。数学の座標と上下が逆。

!!! info "このページを読む前に"
    - [ゲーム数学](index.md)（このセクション全体の地図と、読む順番）
    - [座標系](coordinate-systems.md)（このサイトの座標系の約束）

## デカルト座標と極座標

| 座標 | 表し方 | 向いている場面 |
| --- | --- | --- |
| **デカルト座標** | (x, y) | 直線の移動・格子・矩形 |
| 極座標 | (r, θ)（距離と角度） | 円運動・全方位・レーダー・渦巻き |

### 変換

```text
デカルト → 極:  r = √(x² + y²),   θ = atan2(y, x)
極 → デカルト:  x = r cos θ,       y = r sin θ
```

```cpp
struct Polar {
  float radius;
  float angle;
};

Polar ToPolar(Vector2 p) {
  return {p.Length(), std::atan2(p.y, p.x)};
}

Vector2 FromPolar(Polar p) {
  return Vector2(p.radius * std::cos(p.angle), p.radius * std::sin(p.angle));
}
```

| 使いどころ | 説明 |
| --- | --- |
| 渦巻き | `r` を時間で増やしながら、`θ` も増やす |
| 全方位の弾（弾幕） | `θ` を等間隔に変えて、同じ `r` の方向に撃つ |
| レーダー・ミニマップ | 距離を縮め、角度を保って描く |
| 円形のメニュー | 角度から、選択された項目を決める |
| カメラの周回（オービット） | 注視点の周りを角度で回る |

### 球面座標（3D）

3D の全方位を、2 つの角度と距離で表します。

```text
x = r × sin φ × cos θ
y = r × cos φ
z = r × sin φ × sin θ
```

| 記号 | 意味 |
| --- | --- |
| r | 中心からの距離 |
| θ（方位角） | 水平面での回転 |
| φ（天頂角・極角） | 上（+y）からの角度 |

オービットカメラ（対象の周りを回るカメラ）は、θ と φ をマウスで動かし、r をズームにして、位置を求めます。φ は 0 や π（真上・真下）に近づきすぎないように、制限します。

## 画面座標・UV 座標・NDC

| 座標 | 原点 | 範囲 | 使いどころ |
| --- | --- | --- | --- |
| **画面（ピクセル）座標** | 左上 | (0, 0)〜(幅, 高さ)。Y は下向き | マウス・UI |
| UV 座標 | 左上（DirectX） | (0, 0)〜(1, 1) | テクスチャ |
| NDC（正規化デバイス座標） | 中央 | x・y が -1〜1。Y は上向き（DirectX） | GPU の画面座標 |

### 変換

```cpp
Vector2 ScreenToNdc(Vector2 screen, Vector2 size) {
  return Vector2(screen.x / size.x * 2.0f - 1.0f, 1.0f - screen.y / size.y * 2.0f);
}

Vector2 NdcToScreen(Vector2 ndc, Vector2 size) {
  return Vector2((ndc.x + 1.0f) * 0.5f * size.x, (1.0f - ndc.y) * 0.5f * size.y);
}
```

| 点 | 説明 |
| --- | --- |
| Y の向きが逆 | 画面は下向き、NDC は上向き。1 - y で反転 |
| 解像度に依存しない UI | 画面を 0〜1 の割合で扱い、描画時にピクセルへ変換 |
| DPI・拡大率 | 高 DPI の画面では、論理ピクセルと物理ピクセルが違う（[ImGui の DPI](../libs/imgui/style.md)） |
| ワールド座標との変換 | 3D はビュー・射影の行列で（[3D：MVP](../3d/transforms-mvp.md)） |

## グリッド（タイルマップ）

**マス目のゲーム**（パズル・ローグライク・SRPG・2D アクション）ではワールド座標とマスの番号（セル）を行き来します。

### 変換

```cpp
struct Cell {
  int x;
  int y;
};

Cell WorldToCell(Vector2 world, float tile_size) {
  return {static_cast<int>(std::floor(world.x / tile_size)),
          static_cast<int>(std::floor(world.y / tile_size))};
}

Vector2 CellToWorld(Cell cell, float tile_size) {
  return Vector2(static_cast<float>(cell.x) * tile_size, static_cast<float>(cell.y) * tile_size);
}

Vector2 CellCenter(Cell cell, float tile_size) {
  return CellToWorld(cell, tile_size) + Vector2(tile_size * 0.5f, tile_size * 0.5f);
}
```

!!! warning "負の座標は `floor` で丸める"
    `static_cast<int>(-0.5f)` は 0（0 に向かって切り捨て）です。セル -1 になるべき位置が、セル 0 になってしまいます。`std::floor` を通してから整数にします。

### 配列に入れる

| 方法 | 説明 |
| --- | --- |
| 1 次元配列 | `index = y × 幅 + x`。メモリが連続で速い |
| 範囲外の確認 | `0 ≤ x < 幅` かつ `0 ≤ y < 高さ` を確かめてから、アクセス |
| チャンク | 広いマップを、16×16 などのブロックに分けて、必要な所だけ持つ |

```cpp
bool InBounds(Cell c, int width, int height) {
  return c.x >= 0 && c.x < width && c.y >= 0 && c.y < height;
}

int ToIndex(Cell c, int width) {
  return c.y * width + c.x;
}
```

### 隣のセルと距離

| 近傍 | 方向 | 距離 |
| --- | --- | --- |
| 4 近傍 | 上下左右 | マンハッタン距離 `|dx| + |dy|` |
| 8 近傍 | 斜めも含む | チェビシェフ距離 `max(|dx|, |dy|)` |
| ユークリッド距離 | 直線 | `√(dx² + dy²)`（円形の範囲） |

| 場面 | 距離の選び方 |
| --- | --- |
| 上下左右にしか動けない | マンハッタン |
| 斜めも 1 歩 | チェビシェフ |
| 範囲攻撃（円形） | ユークリッド（2 乗のまま比較） |

斜めの移動が 1 歩で、実際は `√2` 倍長いことが、経路探索で問題になります（コストを 14 と 10 にする、など。[アルゴリズム](../optimize/algorithms.md)）。

## ヘックス（六角形）グリッド

**六角形のマス**は、隣のセルまでの距離が全方向で等しいのでストラテジーゲームで人気です。座標の表し方が複数あります。

| 座標 | 特徴 |
| --- | --- |
| オフセット座標 | 行を半分ずらして表す。配列に入れやすいが計算が面倒 |
| 軸座標（axial） | 2 つの軸 (q, r)。配列にも計算にも使いやすい |
| キューブ座標 | 3 つの軸 (x, y, z)、x + y + z = 0。距離・回転の計算が簡単 |

### キューブ座標

```cpp
struct Hex {
  int q;
  int r;
};

int HexDistance(Hex a, Hex b) {
  int dq = a.q - b.q;
  int dr = a.r - b.r;
  return (std::abs(dq) + std::abs(dq + dr) + std::abs(dr)) / 2;
}
```

| 計算 | 説明 |
| --- | --- |
| 隣の 6 セル | 6 個の方向ベクトル `(+1, 0)`・`(+1, -1)`・`(0, -1)`・`(-1, 0)`・`(-1, +1)`・`(0, +1)` を足す |
| 距離 | キューブ座標なら `max(|dx|, |dy|, |dz|)` |
| 60 度の回転 | 座標を並べ替えて符号を反転するだけ |
| 範囲（半径 N） | `|x|, |y|, |z| ≤ N` のセル |
| ピクセルとの変換 | 六角形の大きさから、決まった式で（尖った上向き・平らな上向きで違う） |

まず軸座標で保存し、計算するときにキューブ座標へと使い分けます。

<svg class="fig illust" data-fig="grids-neighbors" viewBox="0 0 780 300" role="img" aria-label="グリッドの隣"><text x="20" y="24" class="fig-title">四角グリッドは 4 方向か 8 方向、六角グリッドは 6 方向（どれも距離が同じ）</text><rect x="40" y="60" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="80" y="60" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="120" y="60" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="160" y="60" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="200" y="60" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="40" y="100" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="80" y="100" width="40" height="40" fill="#e5484d" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="120" y="100" width="40" height="40" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="160" y="100" width="40" height="40" fill="#e5484d" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="200" y="100" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="40" y="140" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="80" y="140" width="40" height="40" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="120" y="140" width="40" height="40" fill="#e5aa28" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="160" y="140" width="40" height="40" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="200" y="140" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="40" y="180" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="80" y="180" width="40" height="40" fill="#e5484d" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="120" y="180" width="40" height="40" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="160" y="180" width="40" height="40" fill="#e5484d" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="200" y="180" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="40" y="220" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="80" y="220" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="120" y="220" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="160" y="220" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><rect x="200" y="220" width="40" height="40" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><text x="40" y="280" style="font-size:12px;">緑：4 近傍　緑＋赤：8 近傍</text><text x="40" y="298" style="font-size:12px;">斜めは距離 √2（直進の 1.41 倍）</text><polygon points="437.6,138.0 437.6,162.0 416.9,174.0 396.1,162.0 396.1,138.0 416.9,126.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="458.4,174.0 458.4,198.0 437.6,210.0 416.9,198.0 416.9,174.0 437.6,162.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="479.2,210.0 479.2,234.0 458.4,246.0 437.6,234.0 437.6,210.0 458.4,198.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="458.4,102.0 458.4,126.0 437.6,138.0 416.9,126.0 416.9,102.0 437.6,90.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="479.2,138.0 479.2,162.0 458.4,174.0 437.6,162.0 437.6,138.0 458.4,126.0" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="500.0,174.0 500.0,198.0 479.2,210.0 458.4,198.0 458.4,174.0 479.2,162.0" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="520.8,210.0 520.8,234.0 500.0,246.0 479.2,234.0 479.2,210.0 500.0,198.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="479.2,66.0 479.2,90.0 458.4,102.0 437.6,90.0 437.6,66.0 458.4,54.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="500.0,102.0 500.0,126.0 479.2,138.0 458.4,126.0 458.4,102.0 479.2,90.0" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="520.8,138.0 520.8,162.0 500.0,174.0 479.2,162.0 479.2,138.0 500.0,126.0" fill="#e5aa28" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="541.6,174.0 541.6,198.0 520.8,210.0 500.0,198.0 500.0,174.0 520.8,162.0" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="562.4,210.0 562.4,234.0 541.6,246.0 520.8,234.0 520.8,210.0 541.6,198.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="520.8,66.0 520.8,90.0 500.0,102.0 479.2,90.0 479.2,66.0 500.0,54.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="541.6,102.0 541.6,126.0 520.8,138.0 500.0,126.0 500.0,102.0 520.8,90.0" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="562.4,138.0 562.4,162.0 541.6,174.0 520.8,162.0 520.8,138.0 541.6,126.0" fill="#2ea043" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="583.1,174.0 583.1,198.0 562.4,210.0 541.6,198.0 541.6,174.0 562.4,162.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="562.4,66.0 562.4,90.0 541.6,102.0 520.8,90.0 520.8,66.0 541.6,54.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="583.1,102.0 583.1,126.0 562.4,138.0 541.6,126.0 541.6,102.0 562.4,90.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><polygon points="603.9,138.0 603.9,162.0 583.1,174.0 562.4,162.0 562.4,138.0 583.1,126.0" fill="none" fill-opacity="0.45" stroke="currentColor" stroke-opacity="0.5"/><text x="430" y="262" style="font-size:12px;">六角グリッド：隣は 6 つ、どれも距離が等しい</text></svg>

どの方向を「隣」とするかで経路探索・範囲攻撃の形が変わります。六角グリッドは、隣がすべて同じ距離なのが利点です。

## アイソメトリック（斜め見下ろし）

**2D の絵で立体的に見える**ようにする、斜め見下ろしの表現です。タイル座標 (x, y) を、画面の斜めの配置に変換します。

```text
screen_x = (x - y) × (タイルの幅 / 2)
screen_y = (x + y) × (タイルの高さ / 2)
```

```cpp
Vector2 IsoToScreen(Cell c, float tile_w, float tile_h) {
  return Vector2((static_cast<float>(c.x) - static_cast<float>(c.y)) * tile_w * 0.5f,
                 (static_cast<float>(c.x) + static_cast<float>(c.y)) * tile_h * 0.5f);
}

Vector2 ScreenToIso(Vector2 s, float tile_w, float tile_h) {
  float a = s.x / (tile_w * 0.5f);
  float b = s.y / (tile_h * 0.5f);
  return Vector2((a + b) * 0.5f, (b - a) * 0.5f);
}
```

| 点 | 説明 |
| --- | --- |
| 逆変換でクリック位置から、セルを求める | `ScreenToIso` の結果を `floor` |
| タイルの縦横比は 2:1 が定番 | きれいな斜めの線になる |
| 描画の順番 | 奥（x + y が小さい）から手前へ。順番を間違えると手前の物が奥に隠れる |
| 高さ（z） | `screen_y` から、`z × 高さ` を引く（上へずらす） |
| 当たり判定 | 元のタイル座標（見えない直交座標）で行う（画面上の斜めではやらない） |

## 座標の「向き」の違い

**ツール・ライブラリ・API で座標の向きが違う**ために、モデルが反転したり、上下逆になったりします。

| 場面 | 違い |
| --- | --- |
| 画面座標（Win32・ImGui） | 原点が左上、Y が下向き |
| 数学・物理 | Y が上向き |
| DirectX の UV | 原点が左上、V が下向き |
| OpenGL の UV | 原点が左下、V が上向き |
| 左手系・右手系 | Z の向き・外積の向き（[3D：座標系](coordinate-systems.md)） |
| 画像ファイル | 上の行がメモリの先頭（上下反転して扱うライブラリもある） |

境界で変換する（読み込み時・描画時に、1 か所で）ことが混乱を避けるコツです。

<!-- fig:grid-cell-lookup:begin -->

<svg class="fig illust motion" data-fig="grid-cell-lookup" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-grid-cell-lookup" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">位置からマスの番号を求める: セルの大きさで割って、切り捨てる</text>
<rect x="150" y="90" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="184.0" y="129.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(0,0)</text>
<rect x="220" y="90" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="254.0" y="129.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(1,0)</text>
<rect x="290" y="90" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="324.0" y="129.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(2,0)</text>
<rect x="360" y="90" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="394.0" y="129.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(3,0)</text>
<rect x="430" y="90" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="464.0" y="129.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(4,0)</text>
<rect x="500" y="90" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="534.0" y="129.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(5,0)</text>
<rect x="150" y="160" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="184.0" y="199.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(0,1)</text>
<rect x="220" y="160" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="254.0" y="199.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(1,1)</text>
<rect x="290" y="160" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="324.0" y="199.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(2,1)</text>
<rect x="360" y="160" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="394.0" y="199.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(3,1)</text>
<rect x="430" y="160" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="464.0" y="199.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(4,1)</text>
<rect x="500" y="160" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="534.0" y="199.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(5,1)</text>
<rect x="150" y="230" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="184.0" y="269.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(0,2)</text>
<rect x="220" y="230" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="254.0" y="269.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(1,2)</text>
<rect x="290" y="230" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="324.0" y="269.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(2,2)</text>
<rect x="360" y="230" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="394.0" y="269.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(3,2)</text>
<rect x="430" y="230" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="464.0" y="269.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(4,2)</text>
<rect x="500" y="230" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="534.0" y="269.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(5,2)</text>
<rect x="150" y="300" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="184.0" y="339.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(0,3)</text>
<rect x="220" y="300" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="254.0" y="339.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(1,3)</text>
<rect x="290" y="300" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="324.0" y="339.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(2,3)</text>
<rect x="360" y="300" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="394.0" y="339.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(3,3)</text>
<rect x="430" y="300" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="464.0" y="339.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(4,3)</text>
<rect x="500" y="300" width="68" height="68" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="534.0" y="339.0" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#94a3b8">(5,3)</text>
<rect x="360" y="160" width="68" height="68" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="411.8" cy="180.3" r="8" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></circle>
<rect x="150" y="300" width="68" height="68" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.5928;0.5931;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="206.0" cy="310.5" r="8" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.5928;0.5931;1.0000" values="0;0;1;1;0;0"/></circle>
<rect x="500" y="90" width="68" height="68" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5928;0.5931;1.0000" values="0;0;1;1"/></rect>
<circle cx="569.3" cy="90.7" r="8" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5928;0.5931;1.0000" values="0;0;1;1"/></circle>
<text x="150" y="78" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">原点 (0, 0) は左上。y は下向き。セル 1 つ = 10 × 10</text>
<text x="390" y="415" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ゲームの座標から、配列の番号を求める<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="1;1;0;0"/></text>
<text x="390" y="415" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">(37.4, 12.9) ÷ 10 = (3.74, 1.29) → 切り捨て → マス (3, 1)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="415" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">(8.0, 31.5) ÷ 10 = (0.80, 3.15) → 切り捨て → マス (0, 3)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.5928;0.5931;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="415" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">(59.9, 0.1) ÷ 10 = (5.99, 0.01) → 切り捨て → マス (5, 0)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5928;0.5931;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:grid-cell-lookup:end -->

## よくあるミス

??? failure "負の座標を `static_cast<int>` で切り捨てて、セルがずれる"
    `std::floor` で丸めてから、整数にします。

??? failure "画面座標の Y が下向きなのを忘れて、上下が逆になる"
    変換で `1 - y` や、符号の反転をします。

??? failure "タイル座標の配列で、範囲外にアクセスする"
    境界を確かめてから、アクセスします。

??? failure "アイソメトリックの当たり判定を、画面の斜めの座標で行う"
    元のタイル座標で判定します。

??? failure "斜め移動のコストを、上下左右と同じにして、斜めが得になる"
    斜めのコストを約 1.41 倍（14 と 10）にします。

??? failure "極座標で `atan2` の引数の順番を間違える"
    `atan2(y, x)` の順です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>極座標 ⇄ デカルト</strong>：sin / cos と atan2。円運動・全方位に
    - [x] 画面は Y が下向き。座標の向きの違いは境界で 1 回だけ変換
    - [x] タイル座標 ＝ `floor(ワールド ÷ タイルサイズ)`。負は floor
    - [x] 4 近傍 ＝ マンハッタン、8 近傍 ＝ チェビシェフ
    - [x] ヘックスは軸座標・キューブ座標
    - [x] アイソメトリックは 2:1 の斜め変換。当たり判定は元の座標で

## 関連ページ

- [ゲーム数学](index.md)
- [三角関数と角度](trigonometry.md)
- [3D：座標系](coordinate-systems.md)
- [アルゴリズム（A* と空間分割）](../optimize/algorithms.md)
