---
title: Choosing a Method
tags:
  - 描画
---

# Choosing a Method

動的な GI は最新の手法を選べば良いという話ではありません。ReSTIR GI は画質が高い代わりに RT 対応 GPU を要求します。ライトマップはどの機種でも動いて最も軽いのに、光が動くと使えません。対象の機種でそもそも動かない方式を選んでしまうと後から作り直すことになります。

このページは GI のセクションで解説した手法の中から、自分のゲームに合う方式を選ぶためのページです。まず、判断の順序を図で見ます。そのあと制約から逆算する考え方、手法の比較、状況別の選び方、レイ数の見積もりと続きます。最後に、判断を C++ のコードにして、予算を超えたときに段階的に軽くする仕組みも載せます。

!!! tip "ポイント"
    方式は技術の新しさではなく、対象のハードウェアと光の動きから逆算して決めます。光が動かないならライトマップとプローブで終わりです。動いても RT を前提にできないならプローブの動的更新と SSGI です。RT が使えるときに初めて DDGI と ReSTIR GI が選択肢に入ります。どの方式でも 1 つに絞らず組み合わせるのが普通です。

!!! info "このページを読む前に"
    - [Ray-Traced GI](index.md)（レイを飛ばして間接光を求める基本と、ノイズの問題）
    - [GI Comparison](../comparison.md)（GI 全体の方式を並べたページ。このページはその中の動的 GI の選び方に絞る）

## 判断の順序

迷ったときは次の図の順に質問します。上から順に聞いて最初に当てはまったところで決めます。

<svg class="fig flow" viewBox="0 0 680 300" role="img" aria-label="動的 GI の方式を選ぶ判断の順序"><defs><marker id="gcA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">判断の順序：上から聞いて、当てはまったところで決める</text><rect x="16" y="44" width="170" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="101.0" y="66.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">光は動く？</text><line x1="186" y1="66" x2="246" y2="66" stroke="currentColor" stroke-width="2" marker-end="url(#gcA)"/><text x="216" y="58" text-anchor="middle" style="font-size:11px">いいえ</text><rect x="246" y="44" width="230" height="44" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="361.0" y="66.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ライトマップ + プローブ（終わり）</text><line x1="101" y1="88" x2="101" y2="126" stroke="currentColor" stroke-width="2" marker-end="url(#gcA)"/><text x="111" y="112" style="font-size:11px">はい</text><rect x="16" y="126" width="170" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="101.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">RT を前提にできる？</text><line x1="186" y1="148" x2="246" y2="148" stroke="currentColor" stroke-width="2" marker-end="url(#gcA)"/><text x="216" y="140" text-anchor="middle" style="font-size:11px">いいえ</text><rect x="246" y="126" width="230" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="361.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">プローブの動的更新 + SSGI</text><line x1="101" y1="170" x2="101" y2="208" stroke="currentColor" stroke-width="2" marker-end="url(#gcA)"/><text x="111" y="194" style="font-size:11px">はい</text><rect x="16" y="208" width="170" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="101.0" y="230.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">広い世界か、予算が小さい？</text><line x1="186" y1="230" x2="246" y2="230" stroke="currentColor" stroke-width="2" marker-end="url(#gcA)"/><text x="216" y="222" text-anchor="middle" style="font-size:11px">はい</text><rect x="246" y="208" width="230" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="361.0" y="230.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">DDGI</text><line x1="101" y1="252" x2="101" y2="280" stroke="currentColor" stroke-width="2" marker-end="url(#gcA)"/><text x="111" y="272" style="font-size:11px">いいえ</text><text x="16" y="294" style="font-size:12px;font-weight:600">ReSTIR GI + デノイザー（近くは ReSTIR、遠くは DDGI の併用もある）</text></svg>

1. 光は動くか。昼夜の変化も動くライトも破壊もなく、光が固定ならライトマップとライト プローブで足ります。最も軽く最も高品質でどの GPU でも動きます。ここで終わりです。
2. RT を前提にできるか。動的な光が必要で DXR 対応 GPU を前提にできないならプローブを動的に更新して SSGI で補います。RT 非対応の機種を切り捨てられない場合のフォールバックの経路にもなります。
3. 世界が広いか予算が小さいか。RT は使えても画面外の光が重要な広い世界や GI に使える時間が小さい場合は、DDGI にします。プローブは画面の外にも置けて、画素数に依存しないからです。
4. 最後に残るのが ReSTIR GI とデノイザーです。画素ごとに高品質な結果が出る代わりに実装は重く、レイ数も画素数に比例します。

## 制約から逆算する

図の質問は次の 4 つの制約から来ています。順に見ます。

### 対象のハードウェア

PC だけかコンソールかモバイルかで、RT が使えるかが決まります。ハードウェア RT は DirectX 12 の機能（DXR）で、DirectX 11 にはありません。D3D11 だけで作っているなら RT を使う方式は選べずプローブ、SSGI、ボクセル GI、ライトマップから選びます。RT の有無は実行時に `CheckFeatureSupport` で調べられます（後のコードで示します）。

### 光の変化の大きさ

ベイクで済むならベイクが最良です。動的な光が必要でも変化がゆっくりなら DDGI のようにプローブを数フレームかけて更新する方式で足ります。ジオメトリが大きく変わるあるいは動く物の反射光が重要になって初めて、画素ごとの方式が必要になります。

### シーンの規模

狭い室内なら画面空間の SSGI でもそれなりに見えます。ただし SSGI は画面に映っている物しか拾えないので、画面外の明るい窓や壁からの光が消えます。広いオープン ワールドでは画面外の光を持つ方式（プローブ、ボクセル、距離場）が要ります。

### 開発の人手

ReSTIR やデノイザーは自作すると負担が大きい部分です。Unreal Engine のような既存のエンジンの機能や NRD、RTXGI のような SDK を使うほうが現実的です。自作の小規模なエンジンなら SH のライト プローブと SSGI から始めて、慣れてから DDGI に進むのが無理のない順番です。

## 手法の比較

次の表は手法を並べた引く用の一覧です。各セルの理由は手法ごとのページとこの後の節に書きます。

| 手法 | RT | コスト | 品質 | ノイズ | 世界全体 | 実装 |
| --- | --- | --- | --- | --- | --- | --- |
| ライトマップ + プローブ | 不要 | 最小 | 高（静的） | なし | ○（事前） | 低〜中 |
| [SSGI](../ssgi.md) | 不要 | 小 | 中 | 中 | ×（画面のみ） | 低 |
| [ボクセル GI](../voxel-gi.md) | 不要 | 中〜大 | 中 | 小 | ○（範囲内） | 中〜高 |
| [DDGI](../ddgi.md) | 必要 | 中 | 中〜高（低周波） | 小 | ○ | 中 |
| [ReSTIR GI](restir.md) | 必要 | 大 | 高 | 小〜中 | ○ | 高 |
| [Lumen 型](lumen-style.md) | 任意 | 中〜大 | 高 | 小 | ○ | 高 |
| [Radiance Cascades](radiance-cascades.md) | 不要 | 中 | 高（2D） | なし | ×（2D） | 中 |

## 状況別の選び方

### 静的な場面で幅広い機種を狙う

室内や一本道の背景はライトマップとライト プローブにします。ベイクに時間をかけられるぶんランタイムの品質が最も高く、コストはほぼゼロです。動く物にはプローブの SH で光を当てます。

### RT なしで昼夜が変わるオープン ワールド

プローブを動的に更新し空の環境光を差し替え画面の近くは SSGI で補います。RT が不要で軽い代わりにプローブの解像度より細かい間接光は出ません。細かい接触の暗さは AO とコンタクト シャドウで補います。

### DXR 対応の PC で、昼夜も動く物もある

DDGI か ReSTIR GI にします。どちらも完全に動的で画面外の光も使えます。品質を最優先するなら近くを ReSTIR GI、遠くを DDGI という併用もあります。

### 2D ゲーム

[Radiance Cascades](radiance-cascades.md) にします。ノイズが出ず光源の数に依存しません。3D にはそのままでは使えません。

### 自作の小規模エンジン

SH のライト プローブと SSGI から始めます。実装が現実的で後から DDGI へ移るときもプローブの置き方と補間の考え方がそのまま使えます。

## レイトレ GI の長所と短所

長所は 4 つあります。ジオメトリそのものにレイを飛ばすので結果が正確で、画面外や物の裏側の光も反映されます。動く物や動くライトに追加の仕掛けなしで対応できます。ReSTIR のような再利用の手法が進んで、同じレイ数での画質が年々上がっています。

短所はノイズとデノイズが避けられないことです。コストも高くレイを飛ばすだけでなく、加速構造の更新とデノイザーにも時間がかかります。HW RT 対応 GPU が前提で、ソフトウェア方式にすると品質が落ちます。ReSTIR とデノイザーの実装は複雑で、時間方向の履歴の扱いにバグが入りやすい部分でもあります。

## レイ数で見積もる

方式のコストを選ぶ前に 1 フレームに飛ばすレイの数を掛け算で見ます。次の図は画素ごとの方式とプローブの方式を並べたものです。

<svg class="fig flow" viewBox="0 0 680 248" role="img" aria-label="1 フレームに飛ばすレイの数の見積もり"><text x="14" y="22" class="fig-title">1 フレームのレイ数（百万本）</text><text x="14" y="56" style="font-size:12px;font-weight:600">画素ごと 1 本（1080p）</text><rect x="230" y="44" width="75" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="313" y="59" style="font-size:12px">2.07</text><text x="14" y="90" style="font-size:12px;font-weight:600">画素ごと 1 本（1440p）</text><rect x="230" y="78" width="133" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="371" y="93" style="font-size:12px">3.69</text><text x="14" y="124" style="font-size:12px;font-weight:600">画素ごと 1 本（4K）</text><rect x="230" y="112" width="300" height="22" rx="4" fill="rgba(76,139,245,0.35)" stroke="#4c8bf5" stroke-width="2"/><text x="538" y="127" style="font-size:12px">8.29</text><text x="14" y="158" style="font-size:12px;font-weight:600">DDGI 16384 個 × 64 本</text><rect x="230" y="146" width="37" height="22" rx="4" fill="rgba(229,170,40,0.4)" stroke="#e5aa28" stroke-width="2"/><text x="275" y="161" style="font-size:12px">1.05</text><text x="14" y="192" style="font-size:12px;font-weight:600">DDGI 16384 個 × 128 本</text><rect x="230" y="180" width="75" height="22" rx="4" fill="rgba(229,170,40,0.4)" stroke="#e5aa28" stroke-width="2"/><text x="313" y="195" style="font-size:12px">2.10</text><text x="14" y="236" style="font-size:12px;font-weight:400">青＝画素ごとの方式、黄＝プローブの方式（DDGI）。数は各行の掛け算そのもの。</text></svg>

画素ごとに 1 本なら 1080p で約 207 万本、4K で約 829 万本です。4K は 1080p の 4 倍の画素数なので、レイ数も 4 倍になります。解像度を上げるだけで GI のコストが画素数に比例して増えるのが、画素ごとの方式の性質です。

DDGI のレイ数はプローブの数とプローブごとのレイ数の積で決まり画面の解像度に依存しません。32 × 32 × 16 = 16384 個のプローブに 128 本ずつなら約 210 万本で、1080p の画素ごと 1 本と同じ桁です。64 本に減らすと半分の約 105 万本になります。ただし、DDGI の品質はプローブの密度で決まるので、レイ数が同じでも結果の性質は違います。

ノイズはレイ数 N に対して `1/√N` で減ります。1 画素 1 本を 4 本にしても、ノイズは半分にしかなりません。10 分の 1 にするには 100 倍のレイが要ります。レイを増やして解決するのではなく、デノイザーと再利用（ReSTIR）で補うのは、このためです（[Fighting Noise](noise.md)）。

レイ 1 本あたりの時間は GPU・シーンの複雑さ・加速構造で大きく変わるので、このページでは見積もりません。レイ数を出したら実機のプロファイラーで 1 本あたりの時間を測ってください。

## 組み合わせる

1 つに絞らず組み合わせるのが現実的です。

- DDGI と SSGI: DDGI が世界全体の低周波の間接光を SSGI が近距離の細かい陰影を担当する。
- ライトマップと DDGI: 静的な背景はライトマップで最高品質にして、動く物だけ DDGI で照らす。DDGI のレイがライトマップを読む構成もある。
- ReSTIR GI と DDGI: 近くは画素ごとの ReSTIR、遠くはプローブの DDGI にして、レイ数を抑える。
- GI と AO とコンタクト シャドウ: GI は低周波の光なので、細かい接触の暗さは [AO](../../ao/index.md) と [Contact Shadows](../../shadows/contact-shadows.md) で補う。

## 判断をコードにする

ここまでの判断を C++ にします。入力は対象機種の条件で出力は方式と設定です。実測が予算を超えたときに 1 段階だけ軽くする `Degrade` も付けました。`/W4` でコンパイルして警告なしで通り実行できることを MSVC で確かめました（`main` は、`ChooseGi` と `RaysPerFrame` が一通り動くことの確認用です）。

### 方式と入力

```cpp
// gi_planner.cpp : 対象機種の条件から、動的 GI の方式と設定を決める。
#include <d3d12.h>

#include <algorithm>
#include <cstdint>

enum class GiMethod {
  kBakedProbes,   // ライトマップ + ライト プローブ（光は固定）
  kProbesSsgi,    // プローブの動的更新 + SSGI（RT なし）
  kDdgi,          // DDGI（RT あり。変化はゆっくり）
  kReSTIR,        // ReSTIR GI + デノイズ（RT あり。最高品質）
};

struct TargetCaps {
  bool raytracing = false;     // DXR Tier 1.0 以上
  double frame_budget_ms = 16.6;  // 1 フレームの全体の予算
  double gi_budget_ms = 3.0;      // そのうち GI に使える時間
  bool dynamic_lighting = false;  // 昼夜・動くライト
  bool large_world = false;       // 画面外の光が重要な広いシーン
};

struct GiPlan {
  GiMethod method = GiMethod::kBakedProbes;
  uint32_t rays_per_pixel = 0;    // 画素ごとのレイ（ReSTIR のみ）
  uint32_t probe_count = 0;       // プローブの総数（DDGI のみ）
  uint32_t rays_per_probe = 0;    // プローブごとのレイ（DDGI のみ）
};
```

方式は列挙型にして設定は方式ごとに必要な物だけを使います。使わない項目は 0 のままにして、`RaysPerFrame` が方式を見て読み分けます。`frame_budget_ms` は今のコードでは使っていません。`gi_budget_ms` が GI に割り当てた時間で、この値を方式の選択に使います。

### RT の確認

```cpp
// DXR の対応を調べる。CheckFeatureSupport の戻り値を必ず見る（失敗したら「非対応」）。
bool SupportsRaytracing(ID3D12Device* device) {
  D3D12_FEATURE_DATA_D3D12_OPTIONS5 options5 = {};
  if (FAILED(device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS5, &options5, sizeof(options5)))) {
    return false;
  }
  return options5.RaytracingTier >= D3D12_RAYTRACING_TIER_1_0;
}
```

`CheckFeatureSupport` は古いドライバーで `OPTIONS5` 自体を知らないときに失敗します。戻り値を見ずに構造体を読むと初期値 0 のまま `NOT_SUPPORTED` と判定されるので動きはしますが、失敗の原因を取り逃がします。失敗したら非対応として扱いベイクとプローブの経路に落とします。

### 判断の順序

```cpp
// 判断の順序（図の流れ）。上から順に、当てはまったところで決める。
GiPlan ChooseGi(const TargetCaps& caps) {
  GiPlan plan;
  if (!caps.dynamic_lighting) {
    plan.method = GiMethod::kBakedProbes;  // 光が動かないなら、ここで終わり（最も安く高品質）
    return plan;
  }
  if (!caps.raytracing) {
    plan.method = GiMethod::kProbesSsgi;   // RT が前提にできない。フォールバックの経路
    return plan;
  }
  if (caps.large_world || caps.gi_budget_ms < 4.0) {
    // 広い世界か予算が小さい: プローブの寄与で安く。レイ数は予算に比例させる（目安）。
    plan.method = GiMethod::kDdgi;
    plan.probe_count = 32 * 32 * 16;       // 1 つの格子（カスケードを重ねて広げる）
    plan.rays_per_probe = caps.gi_budget_ms < 2.0 ? 64 : 128;
    return plan;
  }
  plan.method = GiMethod::kReSTIR;
  plan.rays_per_pixel = caps.gi_budget_ms >= 6.0 ? 2 : 1;
  return plan;
}
```

図の質問を上から `if` に書き写したものです。しきい値の 4.0 ms、6.0 ms、2.0 ms とレイ数の 64、128 はこのページで決めた一例です。論文や資料の値ではありません。自分のゲームで測って決めてください。

### レイ数と軽くする処理

```cpp
// 1 フレームのレイ数を見積もる（画素ごとの方式は画素数、プローブ方式はプローブ数 × レイ数）。
uint64_t RaysPerFrame(const GiPlan& plan, uint32_t width, uint32_t height) {
  switch (plan.method) {
    case GiMethod::kReSTIR:
      return static_cast<uint64_t>(width) * height * plan.rays_per_pixel;
    case GiMethod::kDdgi:
      return static_cast<uint64_t>(plan.probe_count) * plan.rays_per_probe;
    default:
      return 0;  // ベイクとプローブの SSGI は、レイを飛ばさない
  }
}

// 設定の切り替え: 実測が予算を超えたら 1 段階だけ軽くする（毎フレーム呼ばず、数十フレームの平均で）。
GiPlan Degrade(GiPlan plan) {
  if (plan.method == GiMethod::kReSTIR) {
    if (plan.rays_per_pixel > 1) {
      --plan.rays_per_pixel;
    } else {
      plan.method = GiMethod::kDdgi;        // 画素ごとの方式を諦めて、プローブにする
      plan.probe_count = 32 * 32 * 16;
      plan.rays_per_probe = 64;
      plan.rays_per_pixel = 0;
    }
  } else if (plan.method == GiMethod::kDdgi) {
    plan.rays_per_probe = std::max<uint32_t>(32, plan.rays_per_probe / 2);
  }
  return plan;
}

int main() {
  TargetCaps caps;
  caps.raytracing = true;
  caps.dynamic_lighting = true;
  GiPlan plan = ChooseGi(caps);
  return RaysPerFrame(plan, 1920, 1080) > 0 ? 0 : 1;
}
```

`RaysPerFrame` の掛け算は `uint64_t` にしてから行います。4K の 8.29 百万 × 2 本は 32 ビットに収まりますが、解像度やレイ数を増やすと溢れるので、先に型を広げます。

`Degrade` はフレーム時間の平均が予算を超えたときに 1 段階だけ軽くします。ReSTIR は画素ごとのレイを 1 本まで減らし、それでも足りなければ DDGI に切り替えます。DDGI はプローブごとのレイを半分にしますが、32 本を下限にします。これ以下ではプローブの更新が追いつかず光が遅れて見えるからです。毎フレーム呼ぶと切り替えが振動するので、数十フレームの平均で判断してください。

## 注意点

- フォールバック: RT 非対応の環境に対応するならベイクと SSGI の経路を最初から用意する。後から足すとアセットの作り方まで変わる。
- 品質設定: レイ数、プローブ数、デノイズの強さを設定画面で変えられるようにする。
- デバッグ: 間接光だけを表示するビューを用意する。直接光を消さないと GI のバグは見つけにくい。
- 測る: プロファイラー（[パフォーマンス プロファイラー](../../../vs/profiler.md)、PIX）で実際のコストを測る。レイ数の見積もりはあくまで入口で、実機の時間とは一致しない。

## よくあるミス

??? failure "最新の手法を選んで、対象機種で動かない"
    DXR を使う方式を選んだのに、対象に RT 非対応の GPU が含まれていると、起動時にデバイスの作成で失敗するか GI が真っ暗になります。企画の段階で対象機種の RT 対応を調べ非対応の機種向けにフォールバックの経路を残します。

??? failure "SSGI だけで済ませて、画面外の光が消える"
    SSGI は画面に映る物しか拾えないので、カメラを動かして明るい窓が画面から出た瞬間に部屋の明るさが急に落ちます。広い世界ではプローブやボクセルなど画面外を持つ方式を併用します。

??? failure "予算を超えて、設定の切り替えが振動する"
    1 フレームの時間で `Degrade` を呼ぶと軽くした直後に時間が下がり元に戻して、また超えます。品質が数フレームごとに行き来して、画面がちらつきます。数十フレームの平均で判断し上げる側にヒステリシスを持たせます。

??? failure "デバッグで直接光を見ているので、GI の誤りに気づかない"
    間接光は直接光に混ざると変化が小さく、明るさが少し違うだけでは気づけません。間接光だけを表示するビューで、色の漏れや暗さの誤りを確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 方式はハードウェアと光の動きから逆算して選ぶ
    - [x] 光が動かないならベイクで終わり
    - [x] レイ数は画素ごとなら画素数、DDGI ならプローブ数 × レイ数
    - [x] ノイズは `1/√N`。レイを増やすよりデノイズと再利用で補う

## 参考

このページは同じセクションの各ページ（Ray-Traced GI、ReSTIR GI、Lumen-Style Approaches、Radiance Cascades、DDGI、SSGI、Voxel GI）をもとに選び方の目安としてまとめたものです。次の資料はこのページを書くために読み直していません。レイ数の見積もりとコードのしきい値は、このページで決めた一例です。

- Daniel Wright, Krzysztof Narkowicz, Patrick Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games.（Lumen 型）
- Zander Majercik, Jean-Philippe Guertin, Derek Nowrouzezahrai, Morgan McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019.（DDGI）
- Benedikt Bitterli, Chris Wyman, Matt Pharr, Peter Shirley, Aaron Lefohn, Wojciech Jarosz, "Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting", ACM Transactions on Graphics (SIGGRAPH 2020).（ReSTIR）
- Yaobin Ouyang, Shiqiu Liu, Markus Kettunen, Matt Pharr, Jacopo Pantaleoni, "ReSTIR GI: Path Resampling for Real-Time Path Tracing", Computer Graphics Forum (High-Performance Graphics 2021).（ReSTIR GI）
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018.（大域照明の章）

## 関連ページ

- [Ray-Traced GI](index.md)
- [GI Comparison](../comparison.md)
- [DDGI](../ddgi.md)
- [ReSTIR GI](restir.md)
- [Fighting Noise](noise.md)
