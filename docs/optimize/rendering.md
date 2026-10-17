---
title: 描画の最適化
tags:
  - 最適化
---

# 描画の最適化

ゲームの 1 フレームは、**CPU が「何を描くか」の命令を作り、GPU がそれを実際に描く**という、2 人のやり取りで成り立っています。どちらかが遅いと、フレーム全体が遅くなります。たとえば、CPU が 5 ms で命令を作っても、GPU が描くのに 20 ms かかるなら、フレームは 20 ms です（逆も同じ）。つまり、描画の最適化は、「**どちらがボトルネックか**」を知るところから始まります。このページは、描画でよく効く最適化（**ドロー コールを減らす、描く量を減らす、1 回の描画を軽くする**）をまとめます。

!!! tip "ポイント"
    - まず<strong>CPU 側が遅いのか、GPU 側が遅いのか</strong>を見分ける（[計測](measure.md)）。
    - CPU 側の遅さは、多くは<strong>ドロー コール（描画命令）の多さ</strong>。<strong>まとめる</strong>（バッチ、インスタンシング）。
    - GPU 側の遅さは、<strong>ピクセル数（オーバードロー）</strong>、<strong>頂点数</strong>、<strong>シェーダーの重さ</strong>、<strong>メモリ帯域（テクスチャ）</strong>。
    - 一番効くのは<strong>描かないこと</strong>。見えないものは、描かない（<strong>カリング</strong>）。
    - <strong>状態の切り替え</strong>（シェーダー、テクスチャ、レンダー ターゲット）を、減らす。

## 描画のしくみ（簡単に）

<svg class="fig flow" viewBox="0 0 1309 196" role="img" aria-label="CPU が描画命令を作り、GPU が処理する"><defs><marker id="fl12852" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">CPU が描画命令を作り、GPU が処理する</text><line x1="150.0" y1="87.0" x2="150.0" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><line x1="275.0" y1="148.0" x2="333.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><text x="304.0" y="142.0" text-anchor="middle" style="font-size:12px">送る</text><line x1="494.0" y1="148.0" x2="552.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><line x1="802.0" y1="148.0" x2="860.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><line x1="1096.0" y1="148.0" x2="1154.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><rect x="79.5" y="44.0" width="141" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="150.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">CPU ゲームの更新</text><circle cx="81.5" cy="46.0" r="10" fill="#4c8bf5"/><text x="81.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="28.0" y="128.0" width="244" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="150.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">描画命令を作る （ドローコール）</text><circle cx="30.0" cy="130.0" r="10" fill="#2ea043"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="336.0" y="128.0" width="155" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="413.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">GPU 頂点シェーダー</text><circle cx="338.0" cy="130.0" r="10" fill="#e5a828"/><text x="338.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="555.0" y="128.0" width="244" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="677.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ラスタライズ （ピクセルに分解）</text><circle cx="557.0" cy="130.0" r="10" fill="#e5484d"/><text x="557.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="863.0" y="128.0" width="230" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="978.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ピクセルシェーダー （色付け）</text><circle cx="865.0" cy="130.0" r="10" fill="#9664e6"/><text x="865.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text><rect x="1157.0" y="128.0" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="1219.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">画面に書き込む</text><circle cx="1159.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="1159.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">6</text></svg>

| 用語 | 意味 |
| --- | --- |
| **ドロー コール** | 「この形を、この設定で描いて」という、GPU への 1 回の描画命令 |
| **頂点シェーダー** | 頂点（三角形の角）の位置を計算するプログラム |
| **ピクセル シェーダー** | 画面の 1 点（ピクセル）の色を計算するプログラム |
| **オーバードロー** | 同じピクセルに、何度も描くこと（手前に隠れて見えないものまで描く） |
| **フィルレート** | 1 秒に描けるピクセル数。GPU の限界の 1 つ |
| **メモリ帯域** | GPU が、テクスチャなどを読み書きできる速さ |

## 1. CPU と GPU、どちらが遅いか

| 症状 | 原因の候補 | 確かめ方 |
| --- | --- | --- |
| **解像度を下げると、速くなる** | **GPU 側**（ピクセルが多い。フィルレート、シェーダーが重い） | 解像度を半分にして、フレーム時間を比べる |
| **解像度を下げても、変わらない** | **CPU 側**（ドロー コール、ゲームの更新） | 同上 |
| **オブジェクトの数を減らすと、速くなる** | CPU 側（ドロー コール）か、GPU 側（頂点数） | |
| **GPU プロファイラーで、GPU が 100% 近い** | GPU 側 | RenderDoc、PIX、NVIDIA Nsight |
| **CPU プロファイラーで、描画の関数が上位** | CPU 側 | Visual Studio のプロファイラー |

## 2. ドロー コールを減らす（CPU 側）

1 回のドロー コールには、**CPU のコスト**（命令の準備・ドライバーの処理）があります。数千回になると、CPU が間に合いません。

### バッチ（まとめて描く）

<strong>同じシェーダー・同じテクスチャのものを、1 回の命令にまとめて描きます。</strong>

| 方法 | 説明 |
| --- | --- |
| **静的バッチ** | 動かないオブジェクトを、1 つの大きなメッシュに結合して、まとめて描く |
| **動的バッチ** | 毎フレーム、小さなオブジェクトを、1 つのバッファに詰めて、まとめて描く（スプライトなど） |
| **インスタンシング** | **同じメッシュを、位置・色だけ変えて、大量に**描く。1 回のドロー コールで、数千個（木、草、弾、パーティクル） |
| **テクスチャ アトラス** | 複数の小さな画像を、1 枚の大きな画像にまとめる。テクスチャの切り替えがなくなり、バッチしやすくなる |
| **ドロー コールの並べ替え** | シェーダー・テクスチャ・マテリアルが同じものを、続けて描く（状態の切り替えを減らす） |

<div class="anim" data-type="graph" data-label="インスタンシング：1 回の命令で、たくさん描く">
n cpu CPU 0 1
n gpu GPU 2 1
# 通常：木が 1000 本なら、ドロー コールが 1000 回
---
n cpu CPU 0 1 hit
n gpu GPU 2 1 gone
l cpu gpu hit 木_x1000回
# 毎回、CPU が命令を作って送る。CPU が間に合わない
---
n cpu CPU 0 1 hit
n gpu GPU 2 1 hit
l cpu gpu hit 木_x1000を1回で
# インスタンシング：メッシュは 1 つ、位置のリストを渡して、1 回の命令で全部描く
</div>

### 状態の切り替えを減らす

| 切り替えの種類 | コスト |
| --- | --- |
| **シェーダー**（パイプライン状態）の変更 | 大きい |
| **レンダー ターゲット**の変更 | 大きい |
| **テクスチャ**のバインド | 中 |
| **頂点バッファ / 定数バッファ**の変更 | 小〜中 |

描画を、**状態の切り替えが少なくなる順**（シェーダー → テクスチャ → メッシュ）に並べ替えます（ソート キーを作って、ソートする）。

## 3. 描く量を減らす（CPU と GPU）

**描かない**のが、一番速いです。

### カリング（見えないものを、描かない）

| カリング | 内容 |
| --- | --- |
| **視錐台カリング** | カメラに映らない範囲（画面の外・後ろ）のオブジェクトは、描かない。バウンディング ボックスで判定する |
| **背面カリング** | 裏向きの三角形は、描かない（GPU が自動で。**既定で有効**にする） |
| **オクルージョン カリング** | 手前の壁に隠れて見えないものは、描かない。GPU のクエリや、CPU 側の簡易ラスタライズ |
| **距離カリング** | 遠くの小さなものは、描かない |
| **LOD**（Level of Detail） | 遠くのものは、**頂点の少ない簡単なモデル**に切り替える |

カリングの判定には、[空間分割](algorithms.md)（四分木、BVH）が使えます。**全オブジェクトを毎フレーム 1 つずつ判定する**と、CPU が重くなるので、階層的に判定します。

### 2D ゲームの場合

| 工夫 | 説明 |
| --- | --- |
| **画面外のスプライトを、描かない** | カメラの範囲外は、スキップ |
| **スプライトを、アトラスにまとめてバッチ** | 1 回のドロー コールで、数千個 |
| **タイルマップを、チャンクごとに 1 つのメッシュに** | タイル 1 枚ずつ描かない |
| **透明部分が大きいスプライトの、余白を切る** | 無駄なピクセルを減らす（オーバードロー） |

## 4. 1 回の描画を軽くする（GPU 側）

### ピクセルを減らす（オーバードロー対策）

| 方法 | 説明 |
| --- | --- |
| **不透明なものは、手前から奥へ描く** | 手前を先に描くと、奥のピクセルは、深度テストで捨てられる（ピクセル シェーダーが実行されない） |
| **透明なものは、奥から手前へ描く** | 透明は、順番が結果に影響する。最後にまとめて |
| **半透明のパーティクルを、減らす・小さくする** | 画面いっぱいの半透明は、非常に重い |
| **解像度を下げる**（動的解像度） | 重いときだけ、内部解像度を下げて、拡大する |
| **ポストエフェクトを、半分の解像度で** | ブルームなどは、小さい解像度で十分 |

### シェーダーを軽くする

| 方法 | 説明 |
| --- | --- |
| **ピクセル シェーダーの計算を、減らす** | `pow`、`sin`、テクスチャの何度もの読み込み、ループが重い |
| **頂点シェーダーで済むものは、そちらで** | ピクセルより、頂点のほうが数が少ない |
| **テクスチャ ルックアップに置き換える** | 重い計算を、事前に計算した表で引く |
| **精度を下げる**（モバイルは `half`） | `float` より `half` が速い GPU がある |
| **`discard` / 分岐の多用を避ける** | GPU は、分岐が苦手（スレッドが同じ道を通るほど速い） |

### 頂点・メモリを減らす

| 方法 | 説明 |
| --- | --- |
| **頂点数を減らす**（LOD、モデルの簡略化） | 小さく映るものに、高精細なモデルは不要 |
| **頂点フォーマットを小さくする** | `float` を `half` や正規化した整数に。法線や UV を圧縮 |
| **テクスチャを圧縮する**（BC フォーマット） | メモリと帯域を、4〜8 分の 1 に（[メモリ使用量](memory-usage.md)） |
| **ミップマップを使う** | 遠くは小さなテクスチャを読む。キャッシュに優しく、見た目も良い |
| **テクスチャの大きさを、画面の大きさに合わせる** | 画面で 100 ピクセルのものに、4096 のテクスチャは不要 |

## 5. 描画の道具を使って調べる

| 道具 | 何が分かるか |
| --- | --- |
| **RenderDoc**（無料） | 1 フレームを、ドロー コール 1 つずつに分解。何を、どの順番で描いたか。テクスチャ、バッファの中身 |
| **PIX**（Microsoft・無料） | DirectX の、CPU / GPU のタイミング。どの描画が重いか |
| **NVIDIA Nsight / AMD Radeon GPU Profiler** | GPU の内部（シェーダーの重さ、メモリ帯域）の詳細 |
| <strong>Visual Studio の「グラフィックス診断」</strong> | フレームの キャプチャ（古い API 向け） |
| **オーバードローの可視化** | 何回描かれたかを、色で表示（自作のデバッグ表示で、加算ブレンドで表示する） |

## ゲームでの使いどころ

| 場面 | 直し方 |
| --- | --- |
| 草・木・弾を大量に描く | インスタンシング |
| 2D のスプライトが多い | アトラス + スプライト バッチ |
| 動かない街・地形 | 静的バッチ + 視錐台カリング + LOD |
| 画面いっぱいのエフェクトで、重くなる | 半透明の範囲を減らす。解像度を下げる |
| UI が重い | UI を、まとめて 1 つのバッチに。変更がなければ、描画結果を使い回す（キャッシュ） |
| モバイル・低スペック | テクスチャの圧縮、解像度の調整、シェーダーの簡略化 |

## よくあるミス

??? failure "ボトルネックを調べずに、シェーダーを直す"
    CPU 側が遅いのに、シェーダーを最適化しても、速くなりません。まず、CPU と GPU のどちらが遅いかを、解像度の変更や、プロファイラーで確かめます。

??? failure "全オブジェクトを、毎フレーム 1 つずつカリング判定する"
    オブジェクトが数万になると、判定自体で CPU が重くなります。空間分割で、階層的に判定します。

??? failure "ドロー コールの数だけを見る"
    ドロー コールが少なくても、1 回が非常に重ければ遅いです。GPU 側のプロファイラーで、実際の時間を見ます。

??? failure "テクスチャが大きすぎる"
    必要以上に大きく、圧縮もしていないと、メモリ帯域とメモリ使用量の両方で、不利です。

??? failure "最適化のつもりで、見た目が壊れる"
    カリングを強くしすぎて、画面の端でオブジェクトが消える、LOD の切り替えが目立つ、などです。見た目も、必ず確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] まず<strong>CPU 側か GPU 側か</strong>を見分ける。解像度を下げて比べる
    - [x] CPU 側は<strong>ドロー コールを減らす</strong>（バッチ、インスタンシング、アトラス、状態の並べ替え）
    - [x] 一番効くのは<strong>描かないこと</strong>。<strong>カリング</strong>（視錐台・遠さ・隠れ）と LOD
    - [x] GPU 側は<strong>オーバードロー・シェーダー・テクスチャの大きさ</strong>を見直す
    - [x] <strong>RenderDoc / PIX</strong> で、1 フレームを分解して調べる

## 関連ページ

- [最適化の進め方](index.md)
- [計測（プロファイリング）](measure.md)
- [アルゴリズムとデータ構造（空間分割）](algorithms.md)
- [メモリ使用量](memory-usage.md)
- [Dear ImGui](../libs/imgui/index.md)
- [描画の最適化（詳細）](gfx/index.md)
- [深度とカリング](../3d/depth-culling.md)
- [メッシュとテクスチャ（インスタンシング・サンプラー）](../3d/mesh-textures.md)
- [スキニングとアニメーション](../3d/skinning-animation.md)
- [3D の衝突判定](../3d/collision-3d.md)
