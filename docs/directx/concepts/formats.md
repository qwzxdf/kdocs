---
title: Formats and Typeless
tags:
  - DirectX
---

# Formats and Typeless

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

テクスチャや頂点バッファの各画素・各要素が、<strong>何バイトでどう解釈されるか</strong>を決めるのが フォーマット（`DXGI_FORMAT_…`）です。`R8G8B8A8_UNORM` は「赤・緑・青・アルファが、各 8 ビット、0〜1 に正規化」という意味です。フォーマットの選び方で 見た目（色の正しさ）、精度、メモリ、速度が決まります。

!!! tip "ポイント"
    - 名前の読み方: `R8G8B8A8_UNORM` ＝ チャンネル（R、G、B、A）と各ビット数、その後ろが <strong>型</strong>（`UNORM`、`FLOAT`、`UINT`、`SNORM`、`SRGB`）。
    - <strong>色（アルベド）は `_SRGB`、データ（法線、粗さ）は `_UNORM`（リニア）</strong>。間違えると色が暗い・くすむ。
    - HDR は `R16G16B16A16_FLOAT`（1 を超える明るさを持てる）。
    - 深度を書いて読むなら `R32_TYPELESS`（型をビューで決める）。
    - 圧縮（BC1〜BC7）で、メモリを 1/4〜1/8 に。

## 名前の読み方

```text
DXGI_FORMAT_R8G8B8A8_UNORM_SRGB
            └┬┘└┬┘└┬┘└┬┘ └─┬─┘ └┬┘
          チャンネルと各ビット数  型  色空間
```

| 部分 | 意味 |
| --- | --- |
| `R8G8B8A8` | 赤 8 ビット、緑 8 ビット、青 8 ビット、アルファ 8 ビット（合計 32 ビット） |
| `UNORM` | 符号なしの整数を 0〜1 の小数に正規化して読む（255 → 1.0） |
| `SRGB` | sRGB のガンマで、保存されていて読むときにリニアへ自動変換 |

## 型の種類

| 型 | 内容 | 例 |
| --- | --- | --- |
| `UNORM` | 符号なし 0〜1 に正規化 | 色、マスク、`R8G8B8A8_UNORM` |
| `SNORM` | 符号つき−1〜1 に正規化 | 法線、`R8G8B8A8_SNORM` |
| `FLOAT` | 浮動小数点 | HDR の色、速度、`R16G16B16A16_FLOAT` |
| `UINT` | 符号なし整数（正規化なし） | ID、カウンター、`R32_UINT` |
| `SINT` | 符号つき整数 | `R32_SINT` |
| `SRGB` | sRGB のガンマ（`UNORM` の仲間） | 色の画像、`R8G8B8A8_UNORM_SRGB` |
| `TYPELESS` | 型なし（ビューで、決める） | 深度、`R32_TYPELESS` |

## sRGB とリニア

人間の目は暗い所の違いに敏感で画像は、<strong>sRGB</strong>（ガンマ約 2.2 の曲線）で保存されます。ところが、ライティングの計算は リニア（光の強さに比例）で行うのが正しいです。

```text
保存されている、色（sRGB） → リニアに、変換 → ライティングの、計算（リニア）→ sRGB に、変換 → 画面
```

`_SRGB` フォーマットを使うと ハードウェアが、自動で、この変換を行います。

| 場面 | フォーマット | 変換 |
| --- | --- | --- |
| 色のテクスチャ（アルベド）を読む | `R8G8B8A8_UNORM_SRGB` の SRV | 読むとき sRGB → リニア（自動） |
| 法線マップ、粗さ金属度を読む | `R8G8B8A8_UNORM`（リニア） | 変換しない |
| 画面（バック バッファ）に書く | RTV を `_SRGB` で作る | 書くとき、リニア → sRGB（自動） |
| HDR の中間バッファ | `R16G16B16A16_FLOAT` | 変換しない（リニアのまま） |

色を `_UNORM` で読むと、sRGB の値をそのままリニアとして計算し 暗く、くすんで見えます。法線を `_SRGB` で読むと、値が歪みます。

## HDR と精度

| フォーマット | ビット/画素 | 特徴 | 使いどころ |
| --- | --- | --- | --- |
| `R8G8B8A8_UNORM` | 32 | 0〜1 の 256 段階 | 最終画面、UI、通常のテクスチャ |
| `R10G10B10A2_UNORM` | 32 | RGB 各 10 ビット、アルファ 2 ビット | 法線、HDR10 の出力 |
| `R11G11B10_FLOAT` | 32 | 浮動小数点、アルファなし | HDR の中間バッファ（ブルーム）。軽い |
| `R16G16B16A16_FLOAT` | 64 | 半精度浮動小数点 | HDR のシーン色。標準 |
| `R32G32B32A32_FLOAT` | 128 | 単精度浮動小数点 | 高精度の計算（重い） |
| `R16G16_FLOAT` | 32 | 2 チャンネル | 速度、八面体法線 |
| `R32_FLOAT` | 32 | 1 チャンネル | 深度の SRV、距離 |
| `R8_UNORM` | 8 | 1 チャンネル | AO、マスク（軽い） |

## 深度のフォーマット

| フォーマット | 内容 |
| --- | --- |
| `D32_FLOAT` | 32 ビット浮動小数点の深度。精度が高い。reverse-Z と相性が良い |
| `D24_UNORM_S8_UINT` | 24 ビット深度 + 8 ビット ステンシル |
| `D32_FLOAT_S8X24_UINT` | 32 ビット浮動小数点 + ステンシル |
| `D16_UNORM` | 16 ビット。軽量（シャドウ マップ） |

## typeless：型をあとで決める

<strong>typeless</strong>（`R32_TYPELESS`、`R8G8B8A8_TYPELESS`）は ビット幅だけを決め 型は、ビューを作るときに決める、フォーマットです。同じメモリを別の型で見たいときに使います。

| 例 | リソース | ビューごとの型 |
| --- | --- | --- |
| 深度を書いて読む | `R32_TYPELESS` | DSV: `D32_FLOAT`、SRV: `R32_FLOAT` |
| 色を sRGB とリニアの両方で | `R8G8B8A8_TYPELESS` | SRV: `_UNORM_SRGB`、UAV: `_UNORM`（UAV は `_SRGB` 不可） |
| ステンシルつきの深度 | `R24G8_TYPELESS` | DSV: `D24_UNORM_S8_UINT`、SRV（深度）: `R24_UNORM_X8_TYPELESS`、SRV（ステンシル）: `X24_TYPELESS_G8_UINT` |

深度は書くとき（DSV）は深度の型、読むとき（SRV）は普通の浮動小数点の型、と 型が違うので typeless が、必要です。

## 圧縮

テクスチャのメモリを大きく減らすのが、ブロック圧縮（BC）です。4×4 のブロックごとに圧縮します。

| フォーマット | 圧縮率 | 用途 |
| --- | --- | --- |
| BC1（DXT1） | 1/8（4 ビット/画素） | 色（アルファなしまたは、1 ビット） |
| BC3（DXT5） | 1/4（8 ビット/画素） | 色 + アルファ |
| BC4 | 1/8 | 1 チャンネル（粗さ高さ） |
| BC5 | 1/4 | 2 チャンネル（法線マップの XY） |
| BC6H | 1/4 | HDR（キューブマップ、ライトマップ） |
| BC7 | 1/4 | 高品質な色 + アルファ |

BC のテクスチャは <strong>レンダー ターゲットや UAV にできません</strong>（読み取り専用）。圧縮の変換はビルド時にツール（`texconv`）で行い DDS に保存します。

## 頂点のフォーマット

頂点バッファの各要素にも同じフォーマットを使います（入力レイアウト）。

| 要素 | 典型的なフォーマット |
| --- | --- |
| 位置 | `R32G32B32_FLOAT` |
| 法線・接線 | `R32G32B32_FLOAT`、または省メモリで `R10G10B10A2_UNORM`、`R16G16B16A16_SNORM` |
| uv | `R32G32_FLOAT`、または `R16G16_FLOAT` |
| 色 | `R8G8B8A8_UNORM` |

## よくあるミス

??? failure "色が暗いくすむ"
    色の画像を `_UNORM` で読んでいる。`_SRGB` にする。または、`_SRGB` の RTV に書いたのにシェーダーでもガンマ変換して二重になっている。

??? failure "法線が歪む"
    法線マップを `_SRGB` で読んでいる。リニアの `_UNORM` にする。

??? failure "HDR の明るい部分が白飛び"
    シーン色を `R8G8B8A8_UNORM` で作っている（1 で、頭打ち）。`R16G16B16A16_FLOAT`（または `R11G11B10_FLOAT`）にする。

??? failure "深度の SRV が、作れない"
    深度を `D32_FLOAT` で作った。`R32_TYPELESS` で作り DSV と SRV で型を分ける。

??? failure "UAV を `_SRGB` で、作ろうとして失敗する"
    UAV は `_SRGB` を指定できない。`_UNORM` で作り色空間はシェーダーで、変換する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォーマット名 ＝ チャンネルとビット数 + 型（`UNORM`・`FLOAT`・`UINT`・`SRGB`）
    - [x] 色は `_SRGB`、データはリニアの `_UNORM`
    - [x] HDR は `R16G16B16A16_FLOAT`（軽くするなら `R11G11B10_FLOAT`）
    - [x] 深度を読み書きするなら `R32_TYPELESS`（DSV と SRV で型を分ける）
    - [x] 圧縮（BC）で、メモリを 1/4〜1/8 に。レンダー ターゲットには使えない
    - [x] UAV は `_SRGB` 不可

## 関連ページ

- [DirectX Concepts](index.md)
- [Resources and Views](resources-views.md)
- [Texture2D](../dx11/texture2d.md)
- [Gamma and sRGB](../../graphics/postprocess/tonemapping/gamma-srgb.md)
- [Microsoft Learn: DXGI_FORMAT](https://learn.microsoft.com/ja-jp/windows/win32/api/dxgiformat/ne-dxgiformat-dxgi_format)
