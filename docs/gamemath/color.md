---
title: 色の数学
tags:
  - ゲーム数学
---

# 色の数学

色はゲームの見た目を決める最も大きな要素ですが、**数値として扱うと意外に罠が多い**分野です。2 つの色を混ぜると暗くにごる、半透明の縁に白い線が出る、虹色にしたいのに RGB では作りにくい、といった問題は、**色の表し方と計算の空間**を知らないことが原因です。このページでは、**RGB・HSV・ガンマと線形空間・アルファ合成・色の補間・輝度**を説明します。

!!! tip "ポイント"
    - 色は<strong>RGB（赤緑青）</strong>が基本。<strong>色相を回したいときは HSV</strong>。
    - 画像や画面の色は<strong>ガンマ補正された空間（sRGB）</strong>。<strong>計算（補間・ライティング）は線形空間</strong>で行う。
    - <strong>色の補間・混ぜ合わせ</strong>は<strong>線形空間でしないと暗くにごる</strong>。
    - <strong>アルファ合成</strong>は、<strong>プリマルチプライド（事前乗算）</strong>が扱いやすく、縁の問題が少ない。
    - 明るさは<strong>輝度（人の目の感度で重みづけ）</strong>。<strong>(R + G + B) / 3 ではない</strong>。
    - 8 ビットの色は<strong>0〜255</strong>、浮動小数点の色は<strong>0〜1</strong>。<strong>変換を明確に</strong>。

## RGB

<strong>赤（R）・緑（G）・青（B）</strong>の強さで色を表します。

| 表し方 | 範囲 | 使いどころ |
| --- | --- | --- |
| **8 ビット整数** | 0〜255 | 画像ファイル・見た目の指定（`#FF8800`） |
| **浮動小数点** | 0.0〜1.0 | **シェーダー・計算** |
| <strong>HDR（浮動小数点）</strong> | 1 を超える値も使う | 明るさの差が大きい場面（[ポストプロセス](../rendering/postprocess.md)） |

```cpp
float ToFloat(uint8_t v) { return static_cast<float>(v) / 255.0f; }
uint8_t ToByte(float v) { return static_cast<uint8_t>(std::clamp(v, 0.0f, 1.0f) * 255.0f + 0.5f); }
```

| 点 | 説明 |
| --- | --- |
| **`+ 0.5` で四捨五入** | 切り捨てると全体がわずかに暗くなる |
| **clamp** | 範囲外の値は先に 0〜1 に収める |
| **パック形式** | 4 バイトの `uint32_t` に詰める（`0xAARRGGBB`・`0xAABBGGRR`）。**並び順が API で違う**ので注意 |

## HSV と HSL

<strong>色相（Hue）・彩度（Saturation）・明度（Value）</strong>で、色を表す方法です。**人間の感覚に近く**、色の調整に向いています。

| 成分 | 意味 | 範囲 |
| --- | --- | --- |
| <strong>H（色相）</strong> | 色の種類（赤→黄→緑→水→青→紫→赤の輪） | 0〜360 度（または 0〜1） |
| <strong>S（彩度）</strong> | 鮮やかさ（0 で灰色） | 0〜1 |
| <strong>V（明度）</strong> | 明るさ（0 で黒） | 0〜1 |

| 使いどころ | 説明 |
| --- | --- |
| **虹色・レインボー** | H だけを時間で回す（S・V は固定） |
| **色の明るさ・鮮やかさの調整** | V・S を変えるだけ |
| **敵・チームごとの色分け** | H を等間隔に配る（黄金角 137.5 度で、きれいに散らせる） |
| **ダメージで赤くなる** | S を上げる、H を赤へ寄せる |
| **補色** | H に 180 度を足す |

```cpp
Vector3 HsvToRgb(float h, float s, float v) {
  h = h - std::floor(h);
  float c = v * s;
  float x = c * (1.0f - std::abs(std::fmod(h * 6.0f, 2.0f) - 1.0f));
  float m = v - c;
  float r = 0.0f;
  float g = 0.0f;
  float b = 0.0f;
  int sector = static_cast<int>(h * 6.0f);
  switch (sector) {
    case 0: r = c; g = x; break;
    case 1: r = x; g = c; break;
    case 2: g = c; b = x; break;
    case 3: g = x; b = c; break;
    case 4: r = x; b = c; break;
    default: r = c; b = x; break;
  }
  return Vector3(r + m, g + m, b + m);
}
```

<strong>色相は輪（0 と 1 がつながっている）</strong>なので補間するときは、**最短の回り方**にします（角度の補間と同じ）。

## ガンマと線形空間

### 問題：画像の値は明るさに比例していない

人間の目は**暗い所の違いに敏感**です。そのため、**画像ファイルや画面は、暗い所の階調を細かく**保存しています（**ガンマ補正**、**sRGB**）。**sRGB の数値 0.5 は、実際の光の量では約 0.21 です**。

<svg class="fig illust" viewBox="0 0 640 260" role="img" aria-label="sRGB と線形の関係">
<defs><marker id="co1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">sRGB の値と、実際の光の量（線形）の関係</text>
<line x1="60" y1="220" x2="60" y2="50" stroke="currentColor" stroke-width="1.5" marker-end="url(#co1)"/>
<line x1="60" y1="220" x2="400" y2="220" stroke="currentColor" stroke-width="1.5" marker-end="url(#co1)"/>
<text x="404" y="224" style="font-size:12px">sRGB の値</text><text x="64" y="46" style="font-size:12px">光の量（線形）</text>
<line x1="60" y1="220" x2="380" y2="60" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4" opacity="0.6"/>
<path d="M60,220 C180,218 260,170 380,60" fill="none" stroke="#4c8bf5" stroke-width="3.5"/>
<text x="420" y="90" style="font-weight:700">ガンマ約 2.2</text>
<text x="420" y="114" style="font-size:13px">sRGB 0.5 → 線形 約 0.21</text>
<text x="420" y="136" style="font-size:13px">sRGB 0.2 → 線形 約 0.03</text>
<text x="420" y="170" style="font-size:12px">点線＝線形（そのまま比例）。</text>
<text x="420" y="190" style="font-size:12px">実線＝sRGB の値と光の量の関係。</text>
</svg>

### 変換

| 方向 | 近似式 | 厳密（sRGB） |
| --- | --- | --- |
| **sRGB → 線形** | `pow(c, 2.2)` | `c ≤ 0.04045 ? c / 12.92 : pow((c + 0.055) / 1.055, 2.4)` |
| **線形 → sRGB** | `pow(c, 1 / 2.2)` | `c ≤ 0.0031308 ? c × 12.92 : 1.055 × pow(c, 1/2.4) - 0.055` |

```cpp
float SrgbToLinear(float c) {
  return c <= 0.04045f ? c / 12.92f : std::pow((c + 0.055f) / 1.055f, 2.4f);
}

float LinearToSrgb(float c) {
  return c <= 0.0031308f ? c * 12.92f : 1.055f * std::pow(c, 1.0f / 2.4f) - 0.055f;
}
```

### どこで線形にするか

| 処理 | 空間 |
| --- | --- |
| **ライティング・ブレンド・補間・ぼかし** | **線形空間**で計算する |
| <strong>画像ファイル（アルベドの色）</strong> | sRGB で保存されている |
| **法線マップ・粗さなどのデータ** | 色ではなく**データ**。**線形のまま**（変換しない） |
| **画面への出力** | sRGB へ戻す |

**GPU は自動で変換してくれます**。テクスチャを **`_SRGB` フォーマット**で作ると、**読み込み時に線形へ**、**RTV を `_SRGB` で作ると、書き込み時に sRGB へ**変換されます（[PBR](../3d/pbr.md)）。

### 色の混ぜ方で変わる

赤（1, 0, 0）と緑（0, 1, 0）を、**半々で混ぜる**とどうなるでしょうか。

| 混ぜる空間 | 結果 | 見た目 |
| --- | --- | --- |
| **sRGB のまま** | (0.5, 0.5, 0) | **暗くにごった**黄 |
| **線形空間で混ぜて、sRGB へ** | (0.73, 0.73, 0) | **明るい**黄（物理的に正しい） |

**グラデーション・ぼかし・半透明の合成**は、**線形空間**で行うときれいに見えます。

## アルファ合成

**半透明**の色を背景に重ねる計算です。

### ストレート（非乗算）アルファ

```text
結果 = 前景色 × α + 背景色 × (1 - α)
```

### プリマルチプライド（事前乗算）アルファ

**色にあらかじめアルファを掛けておく**形式です。

```text
前景色' = 前景色 × α
結果   = 前景色' + 背景色 × (1 - α)
```

| 比べる点 | ストレート | プリマルチプライド |
| --- | --- | --- |
| **合成の式** | 乗算が 2 回 | **乗算が 1 回**（速い） |
| **縁の問題** | 縮小・補間で**透明部分の色が縁ににじむ**（白い輪郭・黒い輪郭） | **にじまない** |
| **加算合成** | 別の処理が必要 | **α = 0 にすれば、加算**（同じ式で扱える） |
| **画像の保存** | 一般的 | ツールで変換が必要 |

```cpp
Vector4 OverPremultiplied(Vector4 src, Vector4 dst) {
  return src + dst * (1.0f - src.w);
}
```

| ブレンドの設定（DirectX） | 説明 |
| --- | --- |
| **ストレート** | `SrcBlend = SRC_ALPHA`、`DestBlend = INV_SRC_ALPHA` |
| **プリマルチプライド** | `SrcBlend = ONE`、`DestBlend = INV_SRC_ALPHA` |
| **加算** | `SrcBlend = SRC_ALPHA（または ONE）`、`DestBlend = ONE` |

**半透明の縁に白や黒の線が出る**ときは、**ストレートの画像をプリマルチプライド扱いで描いている**（またはその逆）ことが多いです。

## 色の補間

| 方法 | 説明 |
| --- | --- |
| **RGB の lerp** | 簡単。線形空間で行えば、物理的に正しい |
| **HSV の lerp** | 色相を通る**虹のような**変化。**色相は最短の回り方**で |
| <strong>知覚的に均一な空間（Oklab など）</strong> | **見た目の変化が均等**。グラデーションがきれい |

```cpp
Vector3 LerpColorLinear(Vector3 srgb_a, Vector3 srgb_b, float t) {
  Vector3 a(SrgbToLinear(srgb_a.x), SrgbToLinear(srgb_a.y), SrgbToLinear(srgb_a.z));
  Vector3 b(SrgbToLinear(srgb_b.x), SrgbToLinear(srgb_b.y), SrgbToLinear(srgb_b.z));
  Vector3 c = Vector3::Lerp(a, b, t);
  return Vector3(LinearToSrgb(c.x), LinearToSrgb(c.y), LinearToSrgb(c.z));
}
```

| 使いどころ | 説明 |
| --- | --- |
| <strong>HP バー（緑→黄→赤）</strong> | 3 色のグラデーション（区間ごとに lerp） |
| **ダメージのフラッシュ** | 元の色から、白・赤へすぐ戻る |
| **時間帯の空の色** | 朝・昼・夕・夜の色を時間で補間 |
| **属性ごとの色** | 色相で配る |

## 輝度とコントラスト

### 輝度（明るさ）

人の目は**緑に最も敏感**で**青に鈍い**ため、**輝度**は次のように**重み付き**で求めます（**線形空間の値**で）。

```cpp
float Luminance(Vector3 linear_rgb) {
  return 0.2126f * linear_rgb.x + 0.7152f * linear_rgb.y + 0.0722f * linear_rgb.z;
}
```

| 使いどころ | 説明 |
| --- | --- |
| **グレースケール化** | 輝度を、R・G・B にコピー |
| **自動露出・トーンマップ** | 画面全体の平均輝度から、明るさを調整 |
| **文字色の選択** | 背景の輝度から、白文字か黒文字か決める |
| **ブルームのしきい値** | 輝度が高い部分だけ、光らせる |

### コントラスト比

**文字と背景**の読みやすさは、**輝度の比**で決まります（Web のアクセシビリティの基準：4.5 対 1 以上）。`(明るい側の輝度 + 0.05) / (暗い側の輝度 + 0.05)` です。

### 簡単な色調整

| 操作 | 式 |
| --- | --- |
| **明るさ** | `c × 倍率`（線形空間で） |
| **コントラスト** | `(c - 0.5) × 係数 + 0.5` |
| **彩度** | 輝度（グレー）との lerp（`lerp(gray, c, 彩度)`） |
| <strong>色味（ティント）</strong> | 色との乗算 |
| **ガンマ調整** | `pow(c, γ)` |

## トーンマップ（HDR → 表示）

**HDR の値**（1 を超える明るさ）は、そのままでは画面に出せません。**0〜1 に収める変換**が**トーンマップ**です。

| 方式 | 式 | 特徴 |
| --- | --- | --- |
| **Reinhard** | `c / (1 + c)` | 簡単。くすんだ見た目になりがち |
| <strong>ACES（近似）</strong> | 多項式の近似 | 映画風の見た目。標準的 |
| **露出の調整** | `c × 露出` の後でトーンマップ | 明るさの基準を決める |

詳しくは[PBR](../3d/pbr.md)の「トーンマッピング」にあります。

## よくあるミス

??? failure "sRGB の値のまま補間・ブレンド・ぼかしをして、暗くにごる"
    線形空間で計算して、最後に sRGB へ戻します。

??? failure "法線マップを sRGB として読み込み、法線が歪む"
    データのテクスチャは、`_SRGB` にしません。

??? failure "半透明の縁に、白い（黒い）線が出る"
    ストレートとプリマルチプライドの扱いを、そろえます。

??? failure "明るさを (R + G + B) / 3 で出す"
    輝度の重み（0.2126・0.7152・0.0722）を使います。

??? failure "色相の補間で、遠回りして虹色になる"
    色相は最短の回り方で補間します。

??? failure "8 ビットと浮動小数点の色を、取り違える"
    255 で割る・掛ける変換を境界ではっきりさせます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 色は<strong>RGB</strong>。<strong>色相の操作は HSV</strong>
    - [x] 画像・画面は<strong>sRGB（ガンマ）</strong>。<strong>計算は線形空間</strong>で
    - [x] <strong>補間・ブレンド・ぼかし</strong>は線形空間。<strong>暗くにごるのを防ぐ</strong>
    - [x] <strong>アルファ合成</strong>は<strong>プリマルチプライド</strong>が、縁の問題が少ない
    - [x] <strong>輝度 ＝ 0.2126R + 0.7152G + 0.0722B</strong>（線形値で）
    - [x] <strong>データのテクスチャ</strong>（法線・粗さ）は<strong>sRGB にしない</strong>

## 関連ページ

- [ゲーム数学](index.md)
- [補間（lerp）](interpolation.md)
- [PBR](../3d/pbr.md)
- [ポストプロセス](../rendering/postprocess.md)
- [テクスチャとストリーミング](../rendering/texture-streaming.md)
