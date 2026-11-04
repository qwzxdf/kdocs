---
title: Method Comparison
tags:
  - 描画
---

# Method Comparison

草や葉や金網は板ポリゴンに絵を貼って、アルファで形を切り抜くのが定番です。ところが切り抜き方は 1 つではありません。<strong>clip</strong>、<strong>Alpha to Coverage</strong>、<strong>ディザ</strong>、<strong>ハッシュド アルファ</strong>、そして普通の<strong>ブレンド</strong>があり縁の見た目も必要な前提もコストもすべて違います。間違えて選ぶと MSAA が無いのに縁がジャギーのまま TAA が無いのに画面がざらざら、といった症状になります。

このページは同じセクションの 4 ページで個別に説明した方式を並べて、自分のゲームに合う方式を選ぶための比較ページです。各方式の仕組みと実装の細部はそれぞれのページに任せます。ここでは違いを数字と図で見て、迷ったときの選び方と全部を切り替えられる 1 本のシェーダーを載せます。

!!! tip "ポイント"
    縁をなめらかにする手段（MSAA か TAA か）は、方式の前提で決まります。方式を先に選ぶのではなく使っているアンチエイリアスから逆算してください。clip は軽くて前提が要りませんが、縁は二択のままです。A2C は MSAA をハッシュドは TAA を前提にします。ディザは前提が要らない代わりに網目が見えることを受け入れる方式です。ガラスのように本当に透ける物にはどれも向かないので、ブレンドを使います。

!!! info "このページを読む前に"
    - [Alpha Testing](index.md)（このセクション全体の地図と clip の基本、ミップで葉が薄くなる問題）
    - [Anti-Aliasing](../../postprocess/antialiasing/index.md)（MSAA と TAA が何をするか。この比較の前提になる）

## 5 つの方式を同じ縁で比べる

最初に見た目の違いを図で押さえます。アルファが左端の 0 から右端の 1 へ 24 画素で一様に増えていく縁を考えて、方式ごとに各画素がどう描かれるかを並べました。濃いほどその画素に残る量が多いことを表します。

<svg class="fig flow" viewBox="0 0 640 444" role="img" aria-label="アルファが 0 から 1 へ変わる縁を、5 つの方式で描いたときの見え方"><text x="14" y="22" class="fig-title">縁のアルファが 0 → 1 に変わる 24 画素</text><text x="14" y="66" style="font-size:12px;font-weight:600">clip（二択）</text><text x="14" y="82" style="font-size:11px;font-weight:400">2 段階</text><rect x="190" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="254" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="270" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="286" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="302" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="318" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="334" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="350" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="366" y="44" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="382" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="398" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="414" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="430" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="446" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="462" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="478" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="494" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="510" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="526" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="44" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="254" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="270" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="286" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="302" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="318" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="334" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="350" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="366" y="60" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="382" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="398" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="414" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="430" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="446" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="462" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="478" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="494" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="510" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="526" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="60" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="254" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="270" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="286" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="302" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="318" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="334" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="350" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="366" y="76" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="382" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="398" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="414" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="430" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="446" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="462" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="478" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="494" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="510" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="526" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="76" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="44" width="384" height="48" fill="none" stroke="#94a3b8" stroke-width="1"/><text x="14" y="140" style="font-size:12px;font-weight:600">Alpha to Coverage（4x）</text><text x="14" y="156" style="font-size:11px;font-weight:400">5 段階</text><rect x="190" y="118" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="118" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="118" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="118" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="254" y="118" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="270" y="118" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="286" y="118" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="302" y="118" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="318" y="118" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="334" y="118" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="350" y="118" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="366" y="118" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="382" y="118" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="398" y="118" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="414" y="118" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="430" y="118" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="446" y="118" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="462" y="118" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="478" y="118" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="494" y="118" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="510" y="118" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="526" y="118" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="118" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="118" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="134" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="134" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="134" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="134" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="254" y="134" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="270" y="134" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="286" y="134" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="302" y="134" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="318" y="134" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="334" y="134" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="350" y="134" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="366" y="134" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="382" y="134" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="398" y="134" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="414" y="134" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="430" y="134" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="446" y="134" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="462" y="134" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="478" y="134" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="494" y="134" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="510" y="134" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="526" y="134" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="134" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="134" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="150" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="150" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="150" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="150" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="254" y="150" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="270" y="150" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="286" y="150" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="302" y="150" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="318" y="150" width="16" height="16" fill="rgba(76,139,245,0.21)"/><rect x="334" y="150" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="350" y="150" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="366" y="150" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="382" y="150" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="398" y="150" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="414" y="150" width="16" height="16" fill="rgba(76,139,245,0.42)"/><rect x="430" y="150" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="446" y="150" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="462" y="150" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="478" y="150" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="494" y="150" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="510" y="150" width="16" height="16" fill="rgba(76,139,245,0.64)"/><rect x="526" y="150" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="150" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="150" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="118" width="384" height="48" fill="none" stroke="#94a3b8" stroke-width="1"/><text x="14" y="214" style="font-size:12px;font-weight:600">ディザ（Bayer 4x4）</text><text x="14" y="230" style="font-size:11px;font-weight:400">16 段階</text><rect x="190" y="192" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="192" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="192" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="192" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="254" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="270" y="192" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="286" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="302" y="192" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="318" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="334" y="192" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="350" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="366" y="192" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="382" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="398" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="414" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="430" y="192" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="446" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="462" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="478" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="494" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="510" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="526" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="192" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="254" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="270" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="286" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="302" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="318" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="334" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="350" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="366" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="382" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="398" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="414" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="430" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="446" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="462" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="478" y="208" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="494" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="510" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="526" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="208" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="224" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="224" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="238" y="224" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="254" y="224" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="270" y="224" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="286" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="302" y="224" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="318" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="334" y="224" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="350" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="366" y="224" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="382" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="398" y="224" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="414" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="430" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="446" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="462" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="478" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="494" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="510" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="526" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="224" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="192" width="384" height="48" fill="none" stroke="#94a3b8" stroke-width="1"/><text x="14" y="288" style="font-size:12px;font-weight:600">ハッシュド（毎フレーム変わる）</text><text x="14" y="304" style="font-size:11px;font-weight:400">確率</text><rect x="190" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="254" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="270" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="286" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="302" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="318" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="334" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="350" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="366" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="382" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="398" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="414" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="430" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="446" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="462" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="478" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="494" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="510" y="266" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="526" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="266" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="254" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="270" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="286" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="302" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="318" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="334" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="350" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="366" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="382" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="398" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="414" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="430" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="446" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="462" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="478" y="282" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="494" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="510" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="526" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="282" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="206" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="222" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="238" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="254" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="270" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="286" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="302" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="318" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="334" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="350" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="366" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="382" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="398" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="414" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="430" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="446" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="462" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="478" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="494" y="298" width="16" height="16" fill="rgba(76,139,245,0.00)"/><rect x="510" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="526" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="542" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="558" y="298" width="16" height="16" fill="rgba(76,139,245,0.85)"/><rect x="190" y="266" width="384" height="48" fill="none" stroke="#94a3b8" stroke-width="1"/><text x="14" y="362" style="font-size:12px;font-weight:600">ブレンド</text><text x="14" y="378" style="font-size:11px;font-weight:400">連続</text><rect x="190" y="340" width="16" height="16" fill="rgba(76,139,245,0.02)"/><rect x="206" y="340" width="16" height="16" fill="rgba(76,139,245,0.05)"/><rect x="222" y="340" width="16" height="16" fill="rgba(76,139,245,0.09)"/><rect x="238" y="340" width="16" height="16" fill="rgba(76,139,245,0.12)"/><rect x="254" y="340" width="16" height="16" fill="rgba(76,139,245,0.16)"/><rect x="270" y="340" width="16" height="16" fill="rgba(76,139,245,0.19)"/><rect x="286" y="340" width="16" height="16" fill="rgba(76,139,245,0.23)"/><rect x="302" y="340" width="16" height="16" fill="rgba(76,139,245,0.27)"/><rect x="318" y="340" width="16" height="16" fill="rgba(76,139,245,0.30)"/><rect x="334" y="340" width="16" height="16" fill="rgba(76,139,245,0.34)"/><rect x="350" y="340" width="16" height="16" fill="rgba(76,139,245,0.37)"/><rect x="366" y="340" width="16" height="16" fill="rgba(76,139,245,0.41)"/><rect x="382" y="340" width="16" height="16" fill="rgba(76,139,245,0.44)"/><rect x="398" y="340" width="16" height="16" fill="rgba(76,139,245,0.48)"/><rect x="414" y="340" width="16" height="16" fill="rgba(76,139,245,0.51)"/><rect x="430" y="340" width="16" height="16" fill="rgba(76,139,245,0.55)"/><rect x="446" y="340" width="16" height="16" fill="rgba(76,139,245,0.58)"/><rect x="462" y="340" width="16" height="16" fill="rgba(76,139,245,0.62)"/><rect x="478" y="340" width="16" height="16" fill="rgba(76,139,245,0.66)"/><rect x="494" y="340" width="16" height="16" fill="rgba(76,139,245,0.69)"/><rect x="510" y="340" width="16" height="16" fill="rgba(76,139,245,0.73)"/><rect x="526" y="340" width="16" height="16" fill="rgba(76,139,245,0.76)"/><rect x="542" y="340" width="16" height="16" fill="rgba(76,139,245,0.80)"/><rect x="558" y="340" width="16" height="16" fill="rgba(76,139,245,0.83)"/><rect x="190" y="356" width="16" height="16" fill="rgba(76,139,245,0.02)"/><rect x="206" y="356" width="16" height="16" fill="rgba(76,139,245,0.05)"/><rect x="222" y="356" width="16" height="16" fill="rgba(76,139,245,0.09)"/><rect x="238" y="356" width="16" height="16" fill="rgba(76,139,245,0.12)"/><rect x="254" y="356" width="16" height="16" fill="rgba(76,139,245,0.16)"/><rect x="270" y="356" width="16" height="16" fill="rgba(76,139,245,0.19)"/><rect x="286" y="356" width="16" height="16" fill="rgba(76,139,245,0.23)"/><rect x="302" y="356" width="16" height="16" fill="rgba(76,139,245,0.27)"/><rect x="318" y="356" width="16" height="16" fill="rgba(76,139,245,0.30)"/><rect x="334" y="356" width="16" height="16" fill="rgba(76,139,245,0.34)"/><rect x="350" y="356" width="16" height="16" fill="rgba(76,139,245,0.37)"/><rect x="366" y="356" width="16" height="16" fill="rgba(76,139,245,0.41)"/><rect x="382" y="356" width="16" height="16" fill="rgba(76,139,245,0.44)"/><rect x="398" y="356" width="16" height="16" fill="rgba(76,139,245,0.48)"/><rect x="414" y="356" width="16" height="16" fill="rgba(76,139,245,0.51)"/><rect x="430" y="356" width="16" height="16" fill="rgba(76,139,245,0.55)"/><rect x="446" y="356" width="16" height="16" fill="rgba(76,139,245,0.58)"/><rect x="462" y="356" width="16" height="16" fill="rgba(76,139,245,0.62)"/><rect x="478" y="356" width="16" height="16" fill="rgba(76,139,245,0.66)"/><rect x="494" y="356" width="16" height="16" fill="rgba(76,139,245,0.69)"/><rect x="510" y="356" width="16" height="16" fill="rgba(76,139,245,0.73)"/><rect x="526" y="356" width="16" height="16" fill="rgba(76,139,245,0.76)"/><rect x="542" y="356" width="16" height="16" fill="rgba(76,139,245,0.80)"/><rect x="558" y="356" width="16" height="16" fill="rgba(76,139,245,0.83)"/><rect x="190" y="372" width="16" height="16" fill="rgba(76,139,245,0.02)"/><rect x="206" y="372" width="16" height="16" fill="rgba(76,139,245,0.05)"/><rect x="222" y="372" width="16" height="16" fill="rgba(76,139,245,0.09)"/><rect x="238" y="372" width="16" height="16" fill="rgba(76,139,245,0.12)"/><rect x="254" y="372" width="16" height="16" fill="rgba(76,139,245,0.16)"/><rect x="270" y="372" width="16" height="16" fill="rgba(76,139,245,0.19)"/><rect x="286" y="372" width="16" height="16" fill="rgba(76,139,245,0.23)"/><rect x="302" y="372" width="16" height="16" fill="rgba(76,139,245,0.27)"/><rect x="318" y="372" width="16" height="16" fill="rgba(76,139,245,0.30)"/><rect x="334" y="372" width="16" height="16" fill="rgba(76,139,245,0.34)"/><rect x="350" y="372" width="16" height="16" fill="rgba(76,139,245,0.37)"/><rect x="366" y="372" width="16" height="16" fill="rgba(76,139,245,0.41)"/><rect x="382" y="372" width="16" height="16" fill="rgba(76,139,245,0.44)"/><rect x="398" y="372" width="16" height="16" fill="rgba(76,139,245,0.48)"/><rect x="414" y="372" width="16" height="16" fill="rgba(76,139,245,0.51)"/><rect x="430" y="372" width="16" height="16" fill="rgba(76,139,245,0.55)"/><rect x="446" y="372" width="16" height="16" fill="rgba(76,139,245,0.58)"/><rect x="462" y="372" width="16" height="16" fill="rgba(76,139,245,0.62)"/><rect x="478" y="372" width="16" height="16" fill="rgba(76,139,245,0.66)"/><rect x="494" y="372" width="16" height="16" fill="rgba(76,139,245,0.69)"/><rect x="510" y="372" width="16" height="16" fill="rgba(76,139,245,0.73)"/><rect x="526" y="372" width="16" height="16" fill="rgba(76,139,245,0.76)"/><rect x="542" y="372" width="16" height="16" fill="rgba(76,139,245,0.80)"/><rect x="558" y="372" width="16" height="16" fill="rgba(76,139,245,0.83)"/><rect x="190" y="340" width="384" height="48" fill="none" stroke="#94a3b8" stroke-width="1"/><text x="14" y="434" style="font-size:12px;font-weight:400">濃さ＝その画素に残る量。左は透明、右は不透明。</text></svg>

clip はアルファが 0.5 を超えた画素だけを残します。縁は 1 本の境目になり段階は 2 つです。

Alpha to Coverage は、アルファをサンプルの個数に直します。4x MSAA なら 0 個から 4 個までの 5 段階です。画素の中ではサンプルの一部だけが描かれリゾルブで平均されるので、縁が 5 段階の濃さで並びます。

ディザは画素ごとのしきい値が決まった並び（図は 4×4 の Bayer 行列）になっています。アルファが同じなら同じ画素が必ず残ります。網目は規則的でアルファが少し変わるごとに残る画素が 1 つずつ増えるので、段階は 16 です。

ハッシュドはしきい値が乱数です。アルファ 0.3 の画素が残る確率は 0.3 になります。1 フレームだけ見るとノイズですが、TAA が数フレームを平均すると、確率が濃さに変わります。

ブレンドだけは画素を捨てずに背景と混ぜます。濃さが連続して変わる唯一の方式で、その代わりに描く順番（ソート）が結果を左右します。

## 比較表

次の表は観点ごとに方式を並べた引く用です。各セルの理由はこの後の節で書きます。

| 観点 | clip | A2C | ディザ | ハッシュド | ブレンド |
| --- | --- | --- | --- | --- | --- |
| 縁 | ジャギー | なめらか | 粒状（規則的） | なめらか（TAA 後） | なめらか |
| 段階 | 2 | サンプル数 + 1 | 16（4×4） | 確率 | 連続 |
| ソート | 不要 | 不要 | 不要 | 不要 | 必要 |
| 深度の書き込み | する | する | する | する | 普通はしない |
| 前提 | なし | MSAA | なし | TAA | なし |
| ノイズ | なし | なし | 網目 | ざらつき | なし |
| 向く対象 | 金網・柵 | 葉・草 | フェード・LOD | 葉・髪 | ガラス・煙 |

## 方式ごとの性格

### clip

ピクセル シェーダーが `clip(alpha - cutoff)` で画素を捨てます。ブレンドもサンプル数も関係しないので、前提が何も要りません。ただし縁は、画素の中心でアルファを見て残すか捨てるかを決めるだけなので、MSAA を有効にしていても階段のままです。MSAA は三角形の縁を平均するもので、シェーダー内の `clip` の結果は 4 サンプルすべてに同じに効くからです。

もう 1 つの弱点はミップマップで遠くの葉が薄くなることです。アルファ 1 の画素と 0 の画素が平均されて 0.4 くらいになると、しきい値 0.5 を割って消えます。対策のカバレッジ保存は [Alpha Testing](index.md) にあります。

### Alpha to Coverage

A2C はブレンド ステートの `AlphaToCoverageEnable` を有効にするだけで、シェーダーから出力するアルファがそのままカバレッジ マスクに変わります。サンプル数が N なら段階は N + 1 です。2x で 3 段階、4x で 5 段階、8x で 9 段階になります。

縁の幅はアルファの勾配で決まります。ぼやけたアルファのままだと縁が広くぼやけるので、`fwidth` で画素 1 つ分に絞る「シャープ化」を併用します（[Alpha to Coverage](alpha-to-coverage.md)）。MSAA が無い構成ではサンプルが 1 つしかないのでほぼ clip と同じになり、有効にする意味がありません。

### ディザ

ディザはアルファを画素ごとのしきい値と比べて捨てます。しきい値の並びが規則的なので、フレームごとに同じ画素が残り静止画でも動画でも結果が変わりません。TAA が無くても安定する点が、ハッシュドとの大きな違いです。

代わりに網目が見えます。1080p の画面で 4 画素の周期は小さいのですが、フェード中の物体を近くで見ると、網戸越しのような模様になります。視点に近い遮蔽物を透かす場面（カメラとキャラの間の壁）や LOD の切り替えのフェードに向いています（[Dithered Transparency](dither.md)）。

### ハッシュド アルファ

ハッシュドはディザと同じ形ですが、しきい値を乱数（ハッシュ）にします。しきい値が一様乱数ならアルファ a の画素が残る確率はちょうど a です。ミップで薄くなったアルファも確率として残るので、葉がスカスカになりません。

ただし 1 フレームの結果はノイズです。TAA が前のフレームと平均して初めてなめらかになります。TAA の無い構成ではざらつきがそのまま見えます。ハッシュの作り方（画面座標か物体の位置か）と近づいたときの粒の大きさの問題は [Hashed Alpha](hashed-alpha.md) にあります。

### ブレンド

ブレンドは画素を捨てず `source * a + background * (1 - a)` で混ぜます。ガラスや煙のように後ろが透けて見える物の唯一の選択肢です。ただし、手前から奥へ重ねる順番が結果を変えるので、描く前にソートが要ります。ソートの限界は [Alpha Blending and Sorting](../blending-sorting/index.md)、順番に依存しない方式は OIT のページにあります。

深度は普通は書きません。書くと後ろの物がブレンド前に消えるからです。葉にブレンドを使うと葉どうしの前後が崩れ遠くの葉が手前の葉を透かして見えるように描かれてしまいます。

## 数字で見積もる

方式を選ぶ前に段階数とノイズの量を式で見ておきます。

アルファ a の縁を A2C で N サンプル（4x なら N = 4）にすると、描かれるサンプル数は `round(a * N)` です。隣り合う段階の差は `1 / N` なので、4x では 0.25、8x では 0.125 になります。a = 0.40 は 2 サンプル（0.5）になり元のアルファより 0.10 だけ濃く見えます。この誤差が帯状の縞（バンディング）として見えるのが、A2C の弱点です。

ハッシュドは 1 画素の結果が 0 か 1 かの二択なので、1 フレームの標準偏差は `sqrt(a * (1 - a))` です。a = 0.5 で最大の 0.5 になります。TAA が N フレームを平均すると、標準偏差は `sqrt(a * (1 - a) / N)` に縮みます。a = 0.5 の場合を計算すると、次のとおりです。

- N = 1（TAA 無し）: 0.50
- N = 8: 約 0.18
- N = 16: 約 0.13

ノイズを半分にするにはフレーム数を 4 倍にする必要があります。TAA の履歴は動きで捨てられるので、動く物の縁では実際の N は小さくなります。動きの速い葉でざらつきが残るのは、このためです。

ディザの Bayer 4×4 はしきい値が `(i + 0.5) / 16` の 16 個なので、段階は 16、アルファの量子化誤差は最大で 1/32 です。誤差が規則的な網目になるのが、ハッシュドとの違いです。

## 選び方

図の順に質問していくとたいていの場合は決まります。

<svg class="fig flow" viewBox="0 0 640 330" role="img" aria-label="方式を選ぶ流れ。上から順に質問して、はいなら右の方式にする"><defs><marker id="amA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">選ぶ順番</text><rect x="16" y="44" width="230" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="131.0" y="65.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">本当の半透明（ガラス・煙）？</text><line x1="246" y1="65" x2="326" y2="65" stroke="currentColor" stroke-width="2" marker-end="url(#amA)"/><text x="286" y="58" text-anchor="middle" style="font-size:11px">はい</text><rect x="326" y="44" width="190" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="421.0" y="65.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ブレンド / OIT</text><line x1="131" y1="86" x2="131" y2="110" stroke="currentColor" stroke-width="2" marker-end="url(#amA)"/><text x="141" y="102" style="font-size:11px">いいえ</text><rect x="16" y="110" width="230" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="131.0" y="131.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">MSAA を使っている？</text><line x1="246" y1="131" x2="326" y2="131" stroke="currentColor" stroke-width="2" marker-end="url(#amA)"/><text x="286" y="124" text-anchor="middle" style="font-size:11px">はい</text><rect x="326" y="110" width="190" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="421.0" y="131.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">Alpha to Coverage</text><line x1="131" y1="152" x2="131" y2="176" stroke="currentColor" stroke-width="2" marker-end="url(#amA)"/><text x="141" y="168" style="font-size:11px">いいえ</text><rect x="16" y="176" width="230" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="131.0" y="197.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">TAA を使っている？</text><line x1="246" y1="197" x2="326" y2="197" stroke="currentColor" stroke-width="2" marker-end="url(#amA)"/><text x="286" y="190" text-anchor="middle" style="font-size:11px">はい</text><rect x="326" y="176" width="190" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="421.0" y="197.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ハッシュド アルファ</text><line x1="131" y1="218" x2="131" y2="242" stroke="currentColor" stroke-width="2" marker-end="url(#amA)"/><text x="141" y="234" style="font-size:11px">いいえ</text><rect x="16" y="242" width="230" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="131.0" y="263.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">フェードや LOD の切り替え？</text><line x1="246" y1="263" x2="326" y2="263" stroke="currentColor" stroke-width="2" marker-end="url(#amA)"/><text x="286" y="256" text-anchor="middle" style="font-size:11px">はい</text><rect x="326" y="242" width="190" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="421.0" y="263.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ディザ（Bayer / IGN）</text><line x1="131" y1="284" x2="131" y2="312" stroke="currentColor" stroke-width="2" marker-end="url(#amA)"/><text x="141" y="304" style="font-size:11px">いいえ</text><rect x="16" y="312" width="230" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="131.0" y="333.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">clip（アルファ テスト）</text><text x="270" y="338" style="font-size:12px;font-weight:400">どれも当てはまらなければ、まず clip。</text></svg>

1. 本当に透ける物（ガラス・煙・水）ならブレンドか OIT です。ほかの方式は後ろを混ぜて見せることができません。
2. 葉や草でフォワード レンダリングと MSAA を使うなら A2C にします。ソート不要で縁がなめらかになりノイズもありません。
3. ディファード レンダリングでは MSAA が重いので、TAA がある前提のハッシュドを選びます。TAA が無いなら clip のまま縁を受け入れるかディザで網目に変えます。
4. フェードアウトや LOD の切り替えには、ディザです。2 つの LOD に補い合うパターンを使えば、切り替えの瞬間に穴が開きません。
5. 金網や柵のように元々縁がくっきりした物は clip で十分です。

## 組み合わせる

1 つだけを使うより組み合わせるのが普通です。

- A2C とシャープ化: 縁の幅を画素 1 つ分に保つ。
- ハッシュドと TAA: ノイズを時間方向に平均してなめらかにする。
- A2C とノイズ: アルファに画素ごとのノイズを足して、5 段階の縞を細かい点に変える（[Alpha to Coverage](alpha-to-coverage.md)）。
- Z プリパスと上のどれか: 隠れた画素の重いシェーダーを省く（[Performance and Shadow Passes](performance.md)）。

## 5 方式を切り替える 1 本のシェーダー

ここから実際に 5 方式を切り替えるコードを載せます。ピクセル シェーダー（HLSL）と D3D11 のステート作りです。HLSL は 5 つの `ALPHA_MODE` すべてを `fxc`（`ps_5_0`）でコンパイルして確かめました。C++ はコンパイルしていません。

### 定数と入力

```hlsl
// alpha_methods.hlsl : アルファ テスト系 5 方式を、1 本のピクセル シェーダーで切り替える。
// ALPHA_MODE: 0=clip  1=A2C  2=ディザ(Bayer)  3=ハッシュド(IGN)  4=ブレンド
#ifndef ALPHA_MODE
#define ALPHA_MODE 0
#endif

Texture2D    g_albedo : register(t0);
SamplerState g_linear : register(s0);

cbuffer PerMaterial : register(b1) {
  float g_cutoff;         // clip のしきい値。0.5 が既定
  float g_fade;           // ディザで消す強さ。1 = 全部描く、0 = 全部消す
  uint  g_frame_index;    // フレーム番号。ハッシュのノイズを毎フレーム動かす
  float g_pad;            // 16 バイト境界にそろえる詰め物
};

struct PSInput {
  float4 position : SV_Position;  // xy は画面の画素座標
  float2 uv       : TEXCOORD0;
};
```

`ALPHA_MODE` はコンパイル時のマクロです。5 方式を `if` で分けると使わない分岐までシェーダーに残るので、方式ごとに別のシェーダーを作ります。`g_pad` は定数バッファの 16 バイト境界を守る詰め物で、省くと C++ 側の構造体とサイズがずれます。`SV_Position.xy` は画素の中心が 0.5 になる座標なので、Bayer の添え字には整数に切り捨てて使います。

### ノイズとしきい値

```hlsl
// 4x4 の Bayer 行列。0〜15 を (i + 0.5) / 16 に直して、しきい値 0〜1 にする。
static const float kBayer4[16] = {
   0,  8,  2, 10,
  12,  4, 14,  6,
   3, 11,  1,  9,
  15,  7, 13,  5};

float Bayer4(float2 pixel) {
  uint2 p = uint2(pixel) & 3;                      // 4 画素ごとに繰り返す
  return (kBayer4[p.y * 4 + p.x] + 0.5) / 16.0;    // +0.5 は、0 と 1 を除く（端の値でも判定が割れる）
}

// Interleaved Gradient Noise（Jimenez 2014）。画面座標から安く 0〜1 のノイズを作る。
float Ign(float2 pixel) {
  return frac(52.9829189 * frac(dot(pixel, float2(0.06711056, 0.00583715))));
}

// A2C 用: 縁のアルファを、画面の 1 画素ぶんの幅だけなだらかにする。
float SharpenAlpha(float alpha, float cutoff) {
  float w = max(fwidth(alpha), 1e-4);              // 画素あたりのアルファの変化。0 割りを避ける
  return saturate((alpha - cutoff) / w + 0.5);     // cutoff で 0.5 になり、幅 w で 0→1
}
```

Bayer 行列の `+ 0.5` はしきい値が 0 や 1 にならないようにするための補正です（ここで足しました）。しきい値が 0 だとアルファがほぼ 0 でも残る画素が出ます。`Ign` の 3 つの定数は Jimenez の発表にある値です。`SharpenAlpha` の `fwidth` は隣の画素とのアルファの差の大きさなので、これで割ると縁の幅がどの距離でも画面上の 1 画素になります。分母の下限 `1e-4` はアルファが平らな場所での 0 割りを防ぐために足しました。

### 本体

```hlsl
float4 main(PSInput input) : SV_Target {
  float4 c = g_albedo.Sample(g_linear, input.uv);
  float a = c.a;

#if ALPHA_MODE == 0
  clip(a - g_cutoff);                              // しきい値未満は捨てる。縁は二択でジャギーになる
#elif ALPHA_MODE == 1
  a = SharpenAlpha(a, g_cutoff);                   // 出力のアルファがそのままカバレッジになる
#elif ALPHA_MODE == 2
  clip(a * g_fade - Bayer4(input.position.xy));    // 規則正しい網目。TAA が無くても安定する
#elif ALPHA_MODE == 3
  float t = frac(Ign(input.position.xy) + 0.61803398875 * (g_frame_index & 63)); // フレームごとに黄金比ずらす（足した）
  clip(a - t);                                     // 確率 a で残る。TAA で平均して使う
#else
  // ブレンド: 捨てない。ソートとブレンド ステートが別に要る。
#endif
  return float4(c.rgb, a);
}
```

モード 1（A2C）には `clip` がありません。アルファを返すだけでブレンド ステート側がカバレッジに変えます。モード 3 はフレームごとに黄金比（0.618…）ずつしきい値をずらします。ずらさないと毎フレーム同じ画素が残り TAA が平均してもなめらかになりません。`& 63` は `g_frame_index` が大きくなっても `frac` の精度が落ちないように 64 フレームで折り返します。この黄金比のずらしはハッシュド アルファの論文の方法ではなく、この比較用に足した処理です。

### D3D11 のステート

```cpp
#include <d3d11.h>
#include <wrl/client.h>

using Microsoft::WRL::ComPtr;

struct AlphaStates {
  ComPtr<ID3D11BlendState> opaque;   // clip / ディザ / ハッシュド: ブレンドしない
  ComPtr<ID3D11BlendState> a2c;      // Alpha to Coverage
  ComPtr<ID3D11BlendState> blend;    // 通常のアルファ ブレンド
  ComPtr<ID3D11DepthStencilState> depth_write;  // 深度を書く（clip 系）
  ComPtr<ID3D11DepthStencilState> depth_read;   // 深度を読むだけ（ブレンド）
};

bool CreateAlphaStates(ID3D11Device* device, AlphaStates* out) {
  D3D11_BLEND_DESC bd = {};
  bd.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
  if (FAILED(device->CreateBlendState(&bd, &out->opaque))) return false;

  bd.AlphaToCoverageEnable = TRUE;           // 出力アルファをカバレッジ マスクに変換する
  if (FAILED(device->CreateBlendState(&bd, &out->a2c))) return false;

  bd.AlphaToCoverageEnable = FALSE;
  auto& rt = bd.RenderTarget[0];
  rt.BlendEnable = TRUE;
  rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;       // 手前の色 * a
  rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;  // 背景 * (1 - a)
  rt.BlendOp = D3D11_BLEND_OP_ADD;
  rt.SrcBlendAlpha = D3D11_BLEND_ONE;
  rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
  rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
  if (FAILED(device->CreateBlendState(&bd, &out->blend))) return false;

  D3D11_DEPTH_STENCIL_DESC dd = {};
  dd.DepthEnable = TRUE;
  dd.DepthFunc = D3D11_COMPARISON_LESS;
  dd.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;
  if (FAILED(device->CreateDepthStencilState(&dd, &out->depth_write))) return false;

  dd.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;  // ブレンドは深度を書かない
  return SUCCEEDED(device->CreateDepthStencilState(&dd, &out->depth_read));
}

void BindAlphaMode(ID3D11DeviceContext* ctx, const AlphaStates& s, int mode) {
  const float factor[4] = {0, 0, 0, 0};
  ID3D11BlendState* blend = s.opaque.Get();
  if (mode == 1) blend = s.a2c.Get();
  if (mode == 4) blend = s.blend.Get();
  ctx->OMSetBlendState(blend, factor, 0xffffffff);
  ctx->OMSetDepthStencilState(mode == 4 ? s.depth_read.Get() : s.depth_write.Get(), 0);
}
```

A2C の状態を作るときだけ `AlphaToCoverageEnable` を立て、`BlendEnable` は立てません。A2C はブレンドではなくサンプルの描く・描かないで動くからです。A2C を使うにはレンダー ターゲットと深度バッファが同じサンプル数の MSAA でなければなりません（作り方は [Alpha to Coverage](alpha-to-coverage.md)）。ブレンドの状態は深度の書き込みをゼロにして、不透明な物を先に描いた深度バッファを「読むだけ」にします。

## よくあるミス

??? failure "MSAA も TAA も無いのに、A2C やハッシュドを選ぶ"
    MSAA 無しの A2C はサンプルが 1 つなので、clip と見分けがつかず縁はジャギーのままです。TAA 無しのハッシュドは毎フレーム変わるノイズがそのまま見えて、葉がちらつきます。症状を見たらまず MSAA か TAA が有効かを確かめてください。無ければ clip かディザに戻します。

??? failure "A2C の縁が、帯状に縞になる"
    4x MSAA は 5 段階しか出せないので、広い範囲でなだらかに薄くなる場所では縞が見えます。アルファに画素ごとのノイズを足して縞を点に変える方法（[Alpha to Coverage](alpha-to-coverage.md)）か、サンプル数を増やす方法があります。

??? failure "ハッシュドを動く物に使うとちらつく"
    TAA の履歴が動きで捨てられると、平均するフレーム数が減ってノイズが戻ります。動きベクトルが葉に出ていないと特にひどくなります。物の位置からハッシュを作ると、パターンが物に貼り付いて安定します。

??? failure "ブレンドで葉を描いて、葉の前後が崩れる"
    深度を書かないブレンドでは葉どうしの前後が描く順番だけで決まります。葉のように数が多く細かく重なる物はソートが追いつきません。葉には clip 系を使いブレンドはガラスや煙に限ります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 方式は MSAA を使うか TAA を使うかで決める
    - [x] 段階は clip が 2、A2C が N + 1、Bayer 4×4 が 16
    - [x] 本当に透ける物だけが、ブレンド

## 参考

このページは同じセクションの 4 ページ（Alpha Testing、Alpha to Coverage、Hashed Alpha、Dithered Transparency）と一般的な実装の知識をもとに書きました。次の資料はこのページを書くために読み直していません。標準偏差の式と段階数の計算はこのページで自分で導きました。

- Chris Wyman, Morgan McGuire, "Hashed Alpha Testing", Proceedings of the ACM SIGGRAPH Symposium on Interactive 3D Graphics and Games (I3D), 2017.（ハッシュド アルファの節）
- Ignacio Castaño, "Computing Alpha Mipmaps", The Witness 開発ブログ, 2010.（clip の節のカバレッジ保存）
- Jorge Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014, Advances in Real-Time Rendering in Games.（Interleaved Gradient Noise の定数）
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018.（透明とアルファ合成の章）

## 関連ページ

- [Alpha Testing](index.md)
- [Alpha to Coverage](alpha-to-coverage.md)
- [Hashed Alpha](hashed-alpha.md)
- [Dithered Transparency](dither.md)
- [Performance and Shadow Passes](performance.md)
- [Anti-Aliasing](../../postprocess/antialiasing/index.md)
