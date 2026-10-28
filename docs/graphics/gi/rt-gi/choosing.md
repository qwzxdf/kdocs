---
title: Choosing a Method
tags:
  - 描画
---

# Choosing a Method

<strong>動的な GI の手法は品質・コスト・必要なハードウェアで、向き不向きがあります</strong>。このページでは <strong>手法の選び方の目安と、長所・短所</strong>を説明します。

!!! tip "ポイント"
    - ハードウェア RT が使える → レイトレ GI ＋ ReSTIR。
    - 使えない → Lumen 的な方式・DDGI・SSGI。
    - 2D やステージ制 → Radiance Cascades。
    - 予算が厳しい → SSGI やプローブ。

!!! info "このページを読む前に"
    - [Ray-Traced GI](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 手法の選び方（動的 GI）
| 状況 | 方式 |
| --- | --- |
| HW RT 対応・最高品質 | レイトレ GI ＋ ReSTIR ＋ デノイズ、DDGI |
| HW RT なしの一般向け | Lumen 的（距離場 ＋ プローブ）、SDFGI |
| 2D ゲーム | Radiance Cascades・距離場ベースの 2D GI |
| モバイル | ライトマップ ＋ プローブ（動的 GI は避ける） |

## 長所と短所
| 長所 | 短所 |
| --- | --- |
| 正確（ジオメトリそのもの） | ノイズ ＋ デノイズが必須 |
| 画面外・裏側も反映 | コストが高い（レイ・デノイズ・加速構造） |
| 動く物・動くライトに自然に対応 | HW RT 対応 GPU（ソフトウェア方式は、品質が劣る） |
| ReSTIR などで年々、効率が向上 | 実装が複雑（ReSTIR・デノイザ） |


### 選ぶときの順番

方式の選択は技術の新しさでなく、<strong>制約から逆算</strong>して決めます。まず、対象のハードウェアを決めます（PC のみか、コンソールかモバイルか）。次に、動的な変化がどれだけ必要かを決めます。昼夜サイクルや破壊がなく光が固定なら、ライトマップとプローブで十分で、最も軽くて高品質です。動的な光が必要でも変化がゆっくりなら、DDGI のようなプローブの更新で足ります。ジオメトリが大きく変わるあるいは画面外の光が重要なら、Lumen 的な方式やレイトレ GI が選択肢に入ります。最後に、開発の人手を考えます。ReSTIR やデノイザは自前で作るには負担が大きく、既存のエンジンや SDK（Unreal、NRD、RTXGI）を使うほうが現実的です。

### 選ぶときの順番

方式の選択は技術の新しさでなく、<strong>制約から逆算</strong>して決めます。まず、対象のハードウェアを決めます（PC のみか、コンソールかモバイルか）。次に、動的な変化がどれだけ必要かを決めます。昼夜サイクルや破壊がなく光が固定なら、ライトマップとプローブで十分で、最も軽くて高品質です。動的な光が必要でも変化がゆっくりなら、DDGI のようなプローブの更新で足ります。ジオメトリが大きく変わるあるいは画面外の光が重要なら、Lumen 的な方式やレイトレ GI が選択肢に入ります。最後に、開発の人手を考えます。ReSTIR やデノイザは自前で作るには負担が大きく、既存のエンジンや SDK（Unreal、NRD、RTXGI）を使うほうが現実的です。

## 手法を選ぶ基準

<strong>リアルタイムのレイトレーシング GI</strong> には、<strong>複数の手法</strong>があります。どれが最良ということはなくゲームの条件で、選びます。

| 基準 | 内容 |
| --- | --- |
| ハードウェア RT の有無 | DXR 対応の GPUを前提にできるか |
| ターゲットの性能 | PC（高性能）、コンソール、ハイエンドのみミドル |
| シーンの規模 | 狭い室内、広いオープン ワールド |
| 光の変化 | 静的、昼夜が変わる動くライト |
| 品質の要求 | フォトリアル、スタイライズ |
| 開発のリソース | 自作、エンジンの機能を使う |

## 手法の比較

| 手法 | RT 必要 | コスト | 品質 | ノイズ | 世界全体 | 実装の、難しさ |
| --- | --- | --- | --- | --- | --- | --- |
| ライトマップ + プローブ（ベイク） | 不要 | 最小 | 高（静的） | なし | ○（事前） | 低〜中 |
| SSGI | 不要 | 小 | 中 | 中 | ×（画面のみ） | 低 |
| ボクセル GI | 不要 | 中〜大 | 中 | 小 | ○（範囲内） | 中〜高 |
| DDGI | 必要 | 中 | 中〜高（低周波） | 小 | ○ | 中 |
| ReSTIR GI + デノイズ | 必要 | 大 | 高 | 小〜中 | ○ | 高 |
| Lumen 型 | 任意（距離場でも可） | 中〜大 | 高 | 小 | ○ | 高 |
| Radiance Cascades | 不要 | 中 | 高（2D） | なし | ×（2D） | 中 |

## 状況別のおすすめ

| 状況 | おすすめ | 理由 |
| --- | --- | --- |
| 静的な場面（室内、一本道）、幅広いハード | ライトマップ + ライト プローブ | 最高品質で最安。どの GPU でも動く |
| 昼夜が変わるオープン ワールド（RT なし） | プローブの、動的更新 + 空の環境光、SSGI で補う | RT 不要。軽い |
| 昼夜、動く物（DXR 対応のハイエンド PC） | DDGI、または ReSTIR GI | 完全に動的。画面の外の光も使える |
| 最高品質（DXR、ハイエンド） | ReSTIR GI + デノイザー、DDGI（遠く）+ ReSTIR（近く） | ノイズが少なく細部が正確 |
| 2D ゲーム | Radiance Cascades | ノイズなし、光源数に依存しない |
| 自作の小規模エンジン（学習・インディー） | ライト プローブ（SH）+ SSGI、慣れたら DDGI | 実装が現実的 |

## 組み合わせる

<strong>1 つに絞らず</strong>、<strong>組み合わせる</strong>のが現実的です。

| 組み合わせ | 役割分担 |
| --- | --- |
| DDGI + SSGI | DDGI が、世界全体の低周波の間接光、SSGI が近距離の細かい陰影（接触の、光のにじみ） |
| ライトマップ + DDGI | 静的な背景は、ライトマップ（最高品質）、動く物は DDGI（動的）。DDGI のレイがライトマップを読む（ヒット シェーダーでライトマップを引く） |
| ReSTIR GI + DDGI | 近くは、ReSTIR（画素ごと高品質）、遠くは DDGI（プローブ、安い） |
| GI + AO + コンタクト シャドウ | GI は、低周波。細かい接触の暗さは AO / コンタクト シャドウで、補う（[AO](../../ao/index.md)、[Contact Shadows](../../shadows/contact-shadows.md)） |

## 判断の順序

```text
1. 光は、動くか？
     No  → ライトマップ + プローブ（ここで終わり。最も、安く、高品質）
     Yes ↓
2. ハードウェア RT を、前提にできるか？
     No  → プローブの動的更新 + SSGI（+ ボクセル GI）
     Yes ↓
3. 品質を、最優先か、それとも、安さか？
     最優先 → ReSTIR GI + デノイザー（+ DDGI）
     安さ   → DDGI
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| フォールバック | RT 非対応の環境に対応するならフォールバック（ベイク + SSGI）を用意 |
| 品質設定 | レイ数、プローブ数、デノイズの強さを設定で変えられるように |
| デバッグ | 間接光だけを表示するデバッグ ビュー（直接光を消す）を用意。GI のバグは見つけにくい |
| 測る | プロファイラ（[パフォーマンス プロファイラー](../../../vs/profiler.md)、PIX）で実際のコストを測る。計算量の見積もりが当たらないことが、多い |

## よくあるミス

??? failure "最新の手法を選んで、対象機種で動かない"
    <strong>対象のハードウェア</strong>から<strong>逆算して選ぶ</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ハードウェアと予算から、手法を選ぶ

## 参考

- Wright, Narkowicz, Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games
- Majercik, Guertin, Nowrouzezahrai, McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019（DDGI）
- Bitterli, Wyman, Pharr, Shirley, Lefohn, Jarosz, "Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting", ACM Transactions on Graphics (SIGGRAPH 2020)（ReSTIR）
- Ouyang, Liu, Kettunen, Pharr, Pantaleoni, "ReSTIR GI: Path Resampling for Real-Time Path Tracing", Computer Graphics Forum (High-Performance Graphics 2021)
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明の章）

## 関連ページ

- [Ray-Traced GI](index.md)
- [GI Comparison](../comparison.md)
- [DDGI](../ddgi.md)
