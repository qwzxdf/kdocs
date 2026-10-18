---
title: Stochastic Transparency
tags:
  - 描画
---

# Stochastic Transparency

**確率的透明は、アルファ値に応じて、画素をランダムに捨て、複数フレームやサンプルで平均する**ことで、**半透明を表す手法**です。**ソート不要で、深度も書けます**が、**ノイズが出るので、TAA が前提**です。このページでは、**確率的透明の仕組み**を説明します。

!!! tip "ポイント"
    - **アルファ値の確率で、画素を残す・捨てる**。
    - **ソート不要・深度も書ける**。
    - **TAA や複数サンプルで、平均してなめらかに**。
    - **ノイズが出る**。

## 確率的透明
<strong>アルファを「そのフラグメントが残る確率」</strong>と考え、**画素ごとのランダムな値と比べて、残すか捨てるか**を決めます（[アルファ テストのハッシュド アルファ](../alpha-test/index.md)と同じ発想）。**不透明として深度に書ける**ので、**ソート不要**で、<strong>TAA（時間平均）</strong>で**滑らかな半透明**に**収束**します。

確率的透明の利点は、ソート不要で深度が書けること（DOF や SSAO などと相性が良い）、正確な期待値に収束すること、実装が簡単なことです。欠点は、ノイズが出て TAA やデノイズが必須なこと、1 フレームでは粗いこと、アルファが小さいと収束が遅いことです。

原典は、Enderton らの "Stochastic Transparency"（I3D 2010）です。

**髪・葉**など、**細かく重なる**物には**有効**です。

## よくあるミス

??? failure "ノイズが残る"
    **TAA** や **サンプル数を増やして**、**平均**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ランダムに捨てて、平均する**
    - [x] **TAA が前提**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [OIT](index.md)
- [Hashed Alpha](../alpha-test/hashed-alpha.md)
