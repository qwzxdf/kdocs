---
title: ナビメッシュとは
tags:
  - 外部ライブラリ
  - AI
---

# ナビメッシュとは

ゲームで敵やキャラクターを、**目的地まで自然に歩かせたい**とき、まず「どこが歩けるのか」をコンピューターに教える必要があります。3D の世界は、ただの三角形の集まりなので、そのままでは「床」「壁」「階段」の区別がつきません。<strong>ナビゲーション メッシュ（ナビメッシュ）</strong> は、**歩ける場所だけを大きな凸ポリゴンの集まりで表したデータ**です。このページでは、ナビメッシュの考え方と、Recast Navigation の構成を説明します。

!!! tip "ポイント"
    - ナビメッシュ ＝ <strong>歩ける面を、少数の凸ポリゴンで表したもの</strong>。経路探索は<strong>ポリゴンをノード、隣り合う辺をエッジとしたグラフ</strong>で行う。
    - <strong>グリッドより、ポリゴンの数が少ない</strong>ので、探索が速く、メモリも少ない。
    - 経路探索の結果は<strong>ポリゴンの列</strong>。そこから、<strong>実際に歩く点の列（直線化）</strong>を作る。
    - ナビメッシュは<strong>ワールドのジオメトリから自動生成</strong>できる（Recast）。
    - 作るのは重い処理なので、<strong>ビルド時に作って保存</strong>する。

## 経路探索のための、空間の表し方

| 表し方 | 説明 | 長所 | 短所 |
| --- | --- | --- | --- |
| **グリッド** | 空間を升目に分ける | 実装が簡単 | 3D の複雑な地形には向かない。ノードが多い |
| **ウェイポイント** | 手で置いた点をつなぐ | 軽い | 手作業。配置の質に依存。動きが不自然 |
| **ナビメッシュ** | 歩ける面を凸ポリゴンで表す | 自動生成できる。自然な動き。ノードが少ない | 作るのに処理が必要 |

## なぜ凸ポリゴンなのか

**凸ポリゴン**の中は、**どの 2 点を結んでも、その線分が必ずポリゴンの中に収まります**。つまり、同じポリゴンの中なら、**壁に当たる心配なく、直線で歩けます**。

<svg class="fig illust" viewBox="0 0 800 250" role="img" aria-label="ナビメッシュのポリゴンと経路">
<defs><marker id="nv1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">ナビメッシュ：歩ける面を、凸ポリゴンに分ける</text>
<g stroke="currentColor" stroke-width="2">
<polygon points="40,80 200,70 220,180 50,190" fill="rgba(76,139,245,0.3)"/>
<polygon points="200,70 360,90 340,180 220,180" fill="rgba(46,160,67,0.3)"/>
<polygon points="360,90 520,60 540,170 340,180" fill="rgba(229,170,40,0.35)"/>
<polygon points="520,60 700,80 720,190 540,170" fill="rgba(150,100,230,0.3)"/>
</g>
<rect x="260" y="200" width="80" height="14" fill="rgba(150,150,150,0.5)"/>
<circle cx="80" cy="140" r="9" fill="#e5484d"/><text x="60" y="166" style="font-size:12px">開始</text>
<circle cx="680" cy="140" r="9" fill="#2ea043"/><text x="662" y="166" style="font-size:12px">目標</text>
<polyline points="80,140 210,125 350,135 530,115 680,140" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#nv1)"/>
<text x="20" y="236" style="font-size:12px">ポリゴン（ノード）の列をたどり、ポリゴンの境界（辺）をまたいで、目標へ向かう</text>
</svg>

| 概念 | 説明 |
| --- | --- |
| **ポリゴン** | 歩ける面の 1 区画。ノードとして扱う |
| <strong>共有する辺（ポータル）</strong> | 隣り合うポリゴンの境目。ここを越えて、移動する |
| <strong>経路（ポリゴンの列）</strong> | 開始点のポリゴンから、目標のポリゴンまでのたどり方（A* で探す） |
| <strong>直線化（ストリング プル）</strong> | ポリゴンの列から、実際に歩く点の列を作る（角で曲がる最短の線） |

## Recast Navigation の構成

| ライブラリ | 役割 | 使う時 |
| --- | --- | --- |
| **Recast** | 三角形のメッシュから、**ナビメッシュを作る** | ビルド時（エディタ・ツール） |
| **Detour** | ナビメッシュの上で**経路探索・最寄り点・レイキャスト** | 実行時 |
| **DetourCrowd** | **多数のエージェントの移動と回避** | 実行時 |
| **DetourTileCache** | **動く障害物**に合わせて、タイルを作り直す | 実行時 |
| **DebugUtils** | ナビメッシュの**デバッグ描画** | 開発中 |

**ナビメッシュの作成（Recast）と、使用（Detour）は、別のライブラリ**です。ゲームの実行時は、**保存したナビメッシュを読み込んで、Detour だけ**を使うのが基本です。

## 全体の流れ

<svg class="fig flow" viewBox="0 0 922 112" role="img" aria-label="Recast と Detour の役割"><defs><marker id="fl97256" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">Recast と Detour の役割</text><line x1="191.0" y1="64.0" x2="249.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl97256)"/><text x="220.0" y="58.0" text-anchor="middle" style="font-size:12px">入力</text><line x1="331.0" y1="64.0" x2="389.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl97256)"/><text x="360.0" y="58.0" text-anchor="middle" style="font-size:12px">保存</text><line x1="597.0" y1="64.0" x2="655.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl97256)"/><text x="626.0" y="58.0" text-anchor="middle" style="font-size:12px">読み込み</text><line x1="737.0" y1="64.0" x2="795.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl97256)"/><rect x="28.0" y="44.0" width="160" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="108.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ワールドの メッシュ</text><rect x="252.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="290.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Recast</text><rect x="392.0" y="44.0" width="202" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="493.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ナビメッシュ （ファイル）</text><rect x="658.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="696.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Detour</text><rect x="798.0" y="44.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="846.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">経路・位置</text></svg>

## 導入

| 方法 | 内容 |
| --- | --- |
| **vcpkg** | `vcpkg install recastnavigation`（Recast・Detour・DetourCrowd・DetourTileCache・DebugUtils が入る） |
| **ソース** | [GitHub の recastnavigation](https://github.com/recastnavigation/recastnavigation) を取得し、`Recast/`・`Detour/` などの `Source` と `Include` を、プロジェクトに追加 |
| **CMake** | `add_subdirectory` で取り込む。ライブラリごとにターゲットがある |

```cpp
#include "Recast.h"
#include "DetourNavMesh.h"
#include "DetourNavMeshBuilder.h"
#include "DetourNavMeshQuery.h"
```

!!! note "座標系と単位"
    Recast は**右手系・Y が上**で**単位はメートル**を想定した設定値が多いです。DirectX（左手系）のゲームでは、**X を反転して渡す**か、座標系を統一します（[座標系](../../gamemath/coordinate-systems.md)）。ライブラリの**バージョンで、関数のシグネチャが変わる**ことがあるので、自分のヘッダを確認してください。

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| **敵の追跡・巡回** | 目標の位置まで経路を求めて歩かせる |
| **キャラのクリック移動** | クリックした地面の点を、最寄りのナビメッシュ上の点に補正する |
| <strong>群衆（RTS・ゾンビ）</strong> | DetourCrowd で、多数を動かして、お互いを避けさせる |
| **ドアやバリケード** | TileCache で、動的に通行可否を変える |
| **ジャンプ・はしご** | オフメッシュ リンクで、離れた場所をつなぐ |

## よくあるミス

??? failure "実行時に、毎回ナビメッシュを作る"
    重い処理です。ビルド時に作って保存し、実行時は読み込みます。

??? failure "Recast の設定（エージェントの大きさ）が、キャラと合わない"
    半径・高さ・登れる段差が実際のキャラと違うと壁に刺さったり、通れる所を通れなかったりします。

??? failure "ナビメッシュ上にない点を、そのまま経路探索に使う"
    先に `findNearestPoly` で、ナビメッシュ上の点に補正します。

??? failure "座標系が違い、ナビメッシュが鏡像になる"
    Recast は右手系・Y 上です。このサイトの左手系とは、**境界で X を反転**してそろえます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ナビメッシュ ＝ <strong>歩ける面の凸ポリゴン</strong>。<strong>ポリゴンをノードにして経路探索</strong>
    - [x] <strong>Recast で作り（ビルド時）</strong>、<strong>Detour で使う（実行時）</strong>
    - [x] 結果は<strong>ポリゴンの列</strong>。<strong>直線化</strong>して、歩く点にする
    - [x] <strong>群衆は DetourCrowd</strong>、<strong>動く障害物は TileCache</strong>
    - [x] <strong>座標系・単位・エージェントの大きさ</strong>に注意

## 関連ページ

- [Recast & Detour](index.md)
- [Recast：ナビメッシュを作る](build.md)
- [Detour：経路を探す](query.md)
- [群衆と動的な障害物](crowd.md)
- [A*（アルゴリズム）](../../optimize/algorithms.md)
