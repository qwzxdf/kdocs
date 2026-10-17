---
title: Visibility Buffer
tags:
  - 最適化
  - 3Dゲーム
---

# Visibility Buffer

[Deferred](forward-deferred.md) は、**ライティングを画面のピクセル数に比例**させましたが、代わりに **G-Buffer（4 枚前後の画面サイズのテクスチャ）の書き込みと読み込み**という、**帯域幅の重い仕事**が生まれました（[メモリ帯域幅](bandwidth.md)）。**Visibility Buffer** は、**G-Buffer に材質の値を書く代わりに、「どの物体の何番目の三角形か」という ID だけ**を書きます。**材質の計算は後で、ID から、頂点データを引き直して行う**ので、**画面サイズの書き込みが、1 枚（32 ビット程度）で済みます**。このページは**何が改善するのか**、**仕組み**、**代償**を説明します。

!!! tip "ポイント"
    - 目的：<strong>G-Buffer の帯域幅（4 枚 → 1 枚）</strong>と、<strong>小さな三角形でのピクセルシェーダーの無駄（quad overdraw）</strong>の削減。
    - 書くもの：<strong>インスタンス番号・三角形番号</strong>（例：32 ビット 1 枚）。<strong>材質の値は書かない</strong>。
    - 後のパス：<strong>ID から、三角形の頂点を読み、重心座標を計算し、属性（UV・法線）を補間し、テクスチャを引いて、ライティング</strong>。
    - 利点：<strong>書き込みの帯域が小さい</strong>・<strong>ジオメトリ パスが軽い</strong>（ピクセルシェーダーがほぼ空）・<strong>材質ごとにまとめて計算できる</strong>。
    - 代償：<strong>後のパスが複雑</strong>（<strong>頂点を自分で読み直す</strong>）。<strong>テクスチャのミップ選択（微分）を、自分で計算</strong>。<strong>バインドレスがほぼ必須</strong>。
    - <strong>Nanite・Meshlet ベースのレンダラ</strong>と、相性が良い（[Mesh Shader](mesh-shaders.md)）。

## G-Buffer の何が重いのか

| 重い所 | 説明 |
| --- | --- |
| **書き込み** | **1080p・4 枚で約 33 MB / フレーム**（60 FPS で約 2 GB/s） |
| **読み込み** | **ライティングで毎回、読む**（Tiled なら 1 回） |
| **オーバードロー** | **後ろで隠れる物も、G-Buffer に全部書く**（[オーバードロー](overdraw.md)） |
| **小さな三角形** | **ピクセルシェーダーが、2×2 ピクセル単位で動く**ため、**小さな三角形ほど、無駄**（quad overdraw） |

## 仕組み

<svg class="fig illust" viewBox="0 0 800 270" role="img" aria-label="Visibility Buffer の流れ">
<defs><marker id="vb1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">ID だけを書く → 後で、ID から、材質を計算する</text>
<rect x="20" y="50" width="170" height="80" rx="10" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/><text x="105" y="84" text-anchor="middle" style="font-weight:700">① ID パス</text><text x="105" y="106" text-anchor="middle" style="font-size:12px">深度 ＋ 三角形 ID</text>
<line x1="196" y1="90" x2="246" y2="90" stroke="currentColor" stroke-width="3" marker-end="url(#vb1)"/>
<rect x="254" y="50" width="170" height="80" rx="10" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="339" y="84" text-anchor="middle" style="font-weight:700">② 属性の復元</text><text x="339" y="106" text-anchor="middle" style="font-size:12px">頂点を読み、補間</text>
<line x1="430" y1="90" x2="480" y2="90" stroke="currentColor" stroke-width="3" marker-end="url(#vb1)"/>
<rect x="488" y="50" width="150" height="80" rx="10" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="563" y="84" text-anchor="middle" style="font-weight:700">③ 材質</text><text x="563" y="106" text-anchor="middle" style="font-size:12px">テクスチャを引く</text>
<line x1="644" y1="90" x2="690" y2="90" stroke="currentColor" stroke-width="3" marker-end="url(#vb1)"/>
<rect x="698" y="50" width="86" height="80" rx="10" fill="rgba(229,72,77,0.25)" stroke="currentColor" stroke-width="2"/><text x="741" y="96" text-anchor="middle" style="font-weight:700">④ 光</text>
<text x="20" y="176" style="font-weight:700">G-Buffer：</text><text x="110" y="176" style="font-size:12px">アルベド・法線・粗さ・深度 …（4 枚）を、画面全体に書く</text>
<text x="20" y="204" style="font-weight:700">Visibility：</text><text x="110" y="204" style="font-size:12px">ID（1 枚）だけ書く。残りは、ID から、後で計算</text>
<text x="20" y="240" style="font-size:12px">書き込みを減らす代わりに、②③ で、頂点バッファとテクスチャを、画面全体で読み直す</text>
</svg>

| 段階 | 内容 |
| --- | --- |
| **① ID パス** | **ピクセルシェーダーは、`SV_PrimitiveID` とインスタンス番号を、書くだけ**（軽い）。**深度も書く** |
| **② 属性の復元** | **ピクセルごとに三角形の 3 頂点を読み、ピクセルの位置から、重心座標を計算**し、**UV・法線を補間** |
| **③ 材質** | **補間した UV でテクスチャを引く**。**UV の微分（ミップ選択）は、重心座標の差から、自分で計算** |
| **④ ライティング** | **Deferred と同じ**（Tiled / Clustered と、組み合わせられる） |

**②③ のパスは、材質ごとにピクセルをまとめて処理**できる（**タイル分類**）ので**同じシェーダーが連続して動き**、**効率が上がります**。

## 何が改善するのか

| 改善 | 説明 |
| --- | --- |
| **書き込み帯域** | **4 枚 → 1 枚**（**約 4 分の 1**） |
| **ジオメトリ パスの軽さ** | **ピクセルシェーダーがほぼ空**。**大量の三角形・小さな三角形に強い** |
| **材質計算の、1 回化** | **最終的に見えるピクセルだけ**、材質を計算（**隠れた面の材質計算はゼロ**） |
| **材質の自由度** | **材質ごとのバリエーション**を**後のパスで分類して**処理 |

## 代償

| 代償 | 説明 |
| --- | --- |
| **実装が複雑** | **頂点の再読み込み・重心座標・微分の自前計算** |
| **テクスチャの読み込み** | <strong>バインドレス（番号でテクスチャを参照）</strong>が、事実上、必要（**DX11 では、難しい**） |
| **頂点の読み直し** | **ピクセルごとに、3 頂点を読む**（**キャッシュに乗る**ので通常は軽い） |
| **MSAA との相性** | **サンプルごとの、ID が必要**（**TAA 前提**の設計が多い） |
| **透明・アルファテスト** | **ID パスでアルファ テストのテクスチャ参照が必要** |

## 他の方式との使い分け

| 方式 | 向く場面 |
| --- | --- |
| <strong>Forward（Forward+）</strong> | **透明・MSAA・モバイル**。**材質が単純** |
| **Deferred** | **ライトが多い・DX11・実装が比較的簡単** |
| **Visibility Buffer** | **三角形が非常に多い・G-Buffer の帯域が、ボトルネック**。**GPU Driven / Meshlet と併用** |

<strong>「G-Buffer の帯域が、ボトルネックと測れた」</strong>ときに**検討**します（[何が重いのか](bottlenecks.md)）。

## よくあるミス

??? failure "帯域が、ボトルネックでないのに、導入する"
    **複雑さが見合いません**。**測ってから**。

??? failure "テクスチャの、ミップ選択が合わず、ちらつく"
    **重心座標から、UV の微分を正しく、計算**します（**勾配を手計算**）。

??? failure "アルファ テストの物を、ID パスで考慮していない"
    **ID パスのピクセルシェーダーで、テクスチャを引いて、`discard`** します。

??? failure "DX11 で、バインドレスを前提に設計する"
    **DX11 では、テクスチャ配列・アトラス**で代用します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Visibility Buffer ＝ <strong>三角形の ID だけを書き、材質は後で、ID から計算</strong>
    - [x] 改善：<strong>G-Buffer の書き込み帯域（4 枚 → 1 枚）</strong>・<strong>小さな三角形の無駄</strong>
    - [x] 代償：<strong>属性の復元・微分の自前計算・バインドレス</strong>。<strong>実装が複雑</strong>
    - [x] <strong>GPU Driven / Meshlet / 大量の三角形</strong>と、相性が良い（<strong>Nanite の方式</strong>）
    - [x] <strong>帯域がボトルネックのときに検討</strong>

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [Forward と Deferred](forward-deferred.md)
- [メモリ帯域幅](bandwidth.md)
- [Mesh Shader と Meshlet](mesh-shaders.md)
- [オーバードロー](overdraw.md)
