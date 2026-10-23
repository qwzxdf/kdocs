---
title: 単体テスト（GoogleTest・doctest・Catch2）
tags:
  - Visual Studio
---

# 単体テスト（GoogleTest・doctest・Catch2）

ゲームを直すたびに、起動して、遊んで、動作を確かめていると、時間がかかります。しかも、直した場所の外で何かが壊れても気づけません。ダメージ計算、アイテムの合成、当たり判定のような、「入力が決まれば結果が決まる」部分は、小さなプログラムで自動的に確かめるのが向いています。

単体テストは、<strong>関数やクラスを 1 つずつ呼んで、結果が期待どおりか自動で調べる</strong>仕組みです。直すたびに実行すれば、何かを壊したときにすぐ分かります。

!!! tip "ポイント"
    - テストは、テスト用の `main` を持つ別のプロジェクトとして作る
    - 書き方は 3 段階。準備（Arrange）、実行（Act）、確認（Assert）
    - 3 つのライブラリの書き方は似ている。GoogleTest は定番、doctest は軽い、Catch2 は読みやすい
    - 描画や入力のように見た目に頼るものより、計算ロジックから先にテストする

!!! info "このページを読む前に"
    - [外部ライブラリの入れ方](libraries.md)（vcpkg で導入する）
    - [プロジェクトの種類](project-types.md)（実行ファイルとライブラリを分ける）

## どれを選ぶか {#choose}

| ライブラリ | 特徴 | 向く人 |
| --- | --- | --- |
| GoogleTest | 定番で情報が多い。モック（`gmock`）も付く | まず迷ったらこれ |
| doctest | ヘッダー 1 つで軽い。ビルドが速い | 小さいプロジェクト |
| Catch2 | 文章に近い書き方（`SECTION`）ができる | 読みやすさを重視する人 |

どれも、`vcpkg install` でそのまま入ります。このページは GoogleTest を例にします。

## 導入と最初のテスト {#first}

テスト用のプロジェクトを、本体とは別に作ります。`vcpkg.json` に `gtest` を足します。

```json
{
  "dependencies": ["gtest"]
}
```

テスト対象は、ダメージ計算の関数です。

```cpp
// damage.h
#pragma once

// 攻撃力から防御力を引いたダメージを返す（最低でも 1）
int CalcDamage(int attack, int defense);
```

```cpp
// damage.cpp
#include "damage.h"

#include <algorithm>

int CalcDamage(int attack, int defense) {
  return std::max(1, attack - defense);
}
```

テストは次のとおりです。

```cpp
// damage_test.cpp
#include <gtest/gtest.h>

#include "damage.h"

TEST(DamageTest, SubtractsDefense) {
  EXPECT_EQ(CalcDamage(10, 3), 7);
}

TEST(DamageTest, IsAtLeastOne) {
  EXPECT_EQ(CalcDamage(3, 10), 1);  // 防御が高くても 0 にならない
}
```

`TEST(グループ名, テスト名)` が 1 つのテストです。中で `EXPECT_EQ(実際の値, 期待する値)` を使い、等しいか確かめます。失敗してもテストは続き、最後に一覧が出ます。

`main` は `gtest_main` ライブラリが用意するので、書かなくて構いません。実行すると、通ったテストと失敗したテストの数が出ます。

```text title="実行結果"
[==========] Running 2 tests from 1 test suite.
[ RUN      ] DamageTest.SubtractsDefense
[       OK ] DamageTest.SubtractsDefense (0 ms)
[ RUN      ] DamageTest.IsAtLeastOne
[       OK ] DamageTest.IsAtLeastOne (0 ms)
[  PASSED  ] 2 tests.
```

## よく使う確認 {#asserts}

| 書き方 | 確かめること |
| --- | --- |
| `EXPECT_EQ(a, b)` | `a == b` |
| `EXPECT_NE(a, b)` | `a != b` |
| `EXPECT_TRUE(x)` / `EXPECT_FALSE(x)` | 真偽 |
| `EXPECT_FLOAT_EQ(a, b)` | 浮動小数点がほぼ等しい |
| `EXPECT_NEAR(a, b, 誤差)` | 誤差の範囲で等しい |
| `ASSERT_*` | 同じ確認だが、失敗したらそのテストを打ち切る |

浮動小数点は、`==` で比べないでください。計算の誤差で一致しないことが多く、`EXPECT_NEAR` で許容する誤差を指定します。

`EXPECT_` と `ASSERT_` の違いは、失敗後に続けるかです。次の確認が前の結果に依存するとき（`nullptr` でないことを確かめてから使う、など）は `ASSERT_` を使います。

## 何をテストするか {#what}

ゲームで向いているのは、次のようなものです。

- ダメージ、経験値、ドロップ率などの計算
- インベントリの追加・削除・上限
- ステートマシンの遷移（この状態でこの入力なら、次はこの状態）
- 数学の関数（交差判定、座標変換）
- セーブデータの書き出しと読み込みで、同じ値に戻ること

逆に、画面の見た目や、描画 API の呼び出しは、単体テストでは扱いにくいです。描画と計算を分けて設計しておくと、計算の部分だけをテストできます。

## 自動で動かす {#ci}

テストは、書いても、実行しなければ意味がありません。[GitHub Actions](github-actions.md) で、push のたびに実行します。失敗したら PR に赤いバツが付くので、壊れたコードが `main` に入りにくくなります。

## よくあるミス {#mistakes}

??? failure "float を `EXPECT_EQ` で比べて、時々失敗する"
    `EXPECT_FLOAT_EQ` か `EXPECT_NEAR` を使います。

??? failure "テスト同士が影響し合って、順番で結果が変わる"
    グローバル変数やシングルトンの状態が残っているのが原因です。各テストの最初に状態を作り直します（GoogleTest なら、テストフィクスチャの `SetUp`）。

??? failure "実装をそのまま写しただけのテストを書いた"
    式をコピーして期待値にすると、実装が間違っていても通ります。電卓で出した値や、仕様書の例を期待値にします。

## これだけ覚える {#summary}

- 準備、実行、確認の 3 段で書く
- 浮動小数点は `EXPECT_NEAR`
- 計算ロジックから始めて、CI で毎回実行する

## 関連ページ

- [GitHub Actions で自動ビルド](github-actions.md)
- [clang-tidy と静的解析](clang-tidy.md)
- [デバッグ](debugging.md)
