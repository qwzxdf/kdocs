---
title: Comparison with PCF
tags:
  - 描画
---

# Comparison with PCF

<strong>VSM 系は方式ごとに光漏れ・メモリ・計算のバランスが違います</strong>。<strong>PCF と比べても得意な場面が違う</strong>ので、用途で使い分けます。このページでは VSM 系の比較表・PCF との使い分けを説明します。

!!! tip "ポイント"
    - VSM：安い・光漏れあり。ESM：簡単・数値に注意。EVSM：光漏れ少・重い。MSM：光漏れほぼなし・複雑。
    - PCF は深度の比較を正しく行うので、光漏れがないが大きなぼかしは重い。
    - VSM 系は大きなぼかしが安いが、光漏れ・メモリ。
    - 柔らかい影が主役なら VSM 系、安定・単純さなら PCF。

!!! info "このページを読む前に"
    - [VSM, ESM and MSM](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## VSM 系の比較
| 項目 | VSM | ESM | EVSM | MSM |
| --- | --- | --- | --- | --- |
| チャンネル数 | 2 | 1 | 4（または 2） | 4 |
| 光漏れ | <strong>あり（大）</strong> | 小（接触部で薄い） | 小 | 最小 |
| 精度の要求 | F32 | F32（オーバーフロー注意） | F32 | F16 でも可（工夫） |
| 計算コスト | 小 | 最小 | 中 | 中〜大 |
| フィルタ可能 | ○ | ○ | ○ | ○ |
| 実装の簡単さ | ○ | ○ | △ | × |

## PCF との使い分け
| 状況 | おすすめ |
| --- | --- |
| 広いソフト シャドウを安く | VSM・EVSM（シャドウ マップをぼかすだけ） |
| 精度・光漏れを避けたい | PCF（扱いが素直） |
| 接触硬化が欲しい | PCSS・レイトレ |
| メモリ・帯域が厳しい | PCF（深度 1 チャンネル）・ESM |
| 多くのライト | VSM 系（ぼかしが、1 回） |

<strong>現代のゲームでは PCF（＋ ノイズ ＋ TAA）が主流</strong>です。VSM 系は<strong>光漏れ・精度・メモリ</strong>の問題から、限定的に使われます（スポットライト・遠景・UI や特殊な効果など）。

## PCF と VSM 系の違い

| 観点 | PCF（比較サンプラー + 複数回） | VSM 系（VSM、ESM、EVSM、MSM） |
| --- | --- | --- |
| 保存するもの | 深度（1 チャンネル） | モーメント（2〜4 チャンネル） |
| 縁のなめらかさ | 複数回、読み込む（3×3 で 9 回、5×5 で 25 回）。サンプルが増えるほど重い | シャドウ マップをぼかして 1 回読む。ぼかしの大きさは自由 |
| 読み込み（画素あたり） | 数回〜数十回 | 1 回 |
| 広いぼかし | 重い（サンプルが半径の 2 乗で増える） | 安い（ぼかしの半径を変えてもシェーダーは同じ） |
| ミップ・異方性 | 使えない（深度の、ミップは意味がない） | 使える（遠くの影の、エイリアシングを減らせる） |
| 光漏れ | ない | ある（VSM、ESM）。EVSM、MSM で軽減 |
| バイアス | 必要（自己影を防ぐ） | 小さくてよい（確率的な、判定） |
| メモリ | 小さい | 2〜4 倍 |
| シャドウ パス | 深度のみ（ピクセル シェーダー不要。速い） | ピクセル シェーダーが必要（モーメントを計算） |
| 実装 | 簡単 | やや複雑（ぼかしパス、光漏れ対策） |

## 速さの違い（目安）

| 手法 | シャドウ パス | ぼかし | メイン パスの、読み込み |
| --- | --- | --- | --- |
| PCF 3×3（ハードウェア 2×2 × 9 = 実質 4 サンプル） | 最速 | 不要 | 4〜9 回 |
| PCF 5×5 | 最速 | 不要 | 25 回 |
| VSM（`R32G32`） | 少し重い | ガウスぼかし（シャドウ マップ全体で、1 回） | 1 回 |
| EVSM（`R32G32B32A32`） | 重い | ガウスぼかし（4 チャンネル） | 1 回 |
| MSM | 重い | ガウスぼかし | 1 回 + 判定の計算 |

PCF は <strong>画素ごとのサンプル数</strong>が、コストの大部分を占めます。VSM 系は <strong>シャドウ マップの、ぼかし</strong>（解像度ぶん）がコストの、大部分で画素ごとのコストは一定です。

## どちらを選ぶか

| 状況 | おすすめ |
| --- | --- |
| 標準的なゲーム（太陽 + 数個のライト） | PCF（3×3〜5×5）。シンプルで安定。まず、これ |
| 広いぼかしの影（柔らかい影、PCSS 風） | PCF だと重い。VSM 系が有利（ただし光漏れの対策が必要） |
| 遠景のカスケード（粗いシャドウ マップ） | VSM 系 + ミップで、エイリアシングを減らす |
| 光漏れが許せない（重なる物が多い、細かい構造） | PCF |
| メモリが厳しい | PCF（1 チャンネル） |

## 近年の傾向

| 傾向 | 内容 |
| --- | --- |
| PCF + ブルー ノイズ + TAA | 少ないサンプル（4〜8）を画素ごとにずらして時間方向に平均。光漏れなしでぼかしも柔軟 |
| ハードウェア レイトレーシング | ソフトな影を正確に（[Ray-Traced Shadows](../ray-traced.md)） |
| VSM 系の使いどころは、狭まった | 光漏れの対策が複雑。PCF + TAA で品質が十分に得られるため |

## よくあるミス

??? failure "VSM 系を選んだのに、光漏れの調整に時間がかかる"
    <strong>最初から EVSM・MSM を検討</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 方式ごとに光漏れ・メモリ・複雑さが違う
    - [x] PCF は安定、VSM 系は大きなぼかしが安い

## 参考

- Donnelly, Lauritzen, "Variance Shadow Maps", Symposium on Interactive 3D Graphics and Games 2006
- Reeves, Salesin, Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987
- Annen, Mertens, Seidel, Eisemann, Durand, "Exponential Shadow Maps", Graphics Interface 2008
- Peters, Klein, "Moment Shadow Mapping", Symposium on Interactive 3D Graphics and Games 2015
- Lauritzen, McGuire, "Layered Variance Shadow Maps", Graphics Interface 2008（光漏れの軽減）

## 関連ページ

- [VSM, ESM and MSM](index.md)
- [PCF](../pcf.md)
- [PCSS](../pcss.md)
