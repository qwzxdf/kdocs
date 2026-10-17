---
title: 未定義動作（UB）
tags:
  - 基礎
---

# 未定義動作（UB）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

**未定義動作**（Undefined Behavior、UB）は、**C++ の規格が「こうなったら何が起きても知らない」と決めている操作**です。配列の範囲外アクセス、消えたオブジェクトの使用、`nullptr` の読み込みなどがそうです。落ちるとは限らず、**たまたま動いたり、Debug では動くのに Release で壊れたり、全然関係ない場所がおかしくなったり**します。原因を探すのがとても大変なので、「起こさない書き方」と「見つける道具」を知っておくことが大事です。

!!! tip "ポイント"
    - よくある UB は「範囲外」「消えたものを使う」「nullptr を読む」「初期化していない変数を読む」「符号付き整数のオーバーフロー」。
    - <strong>Debug ビルドで動いても安心しない。</strong> Release で壊れるのは UB のサイン。
    - 見つける道具: **AddressSanitizer**（`/fsanitize=address` / `-fsanitize=address`）、MSVC の Debug ビルドのチェック、警告レベルを上げる（`/W4` / `-Wall -Wextra`）。
    - コンテナは `[]` より範囲チェック付きの関数や、そもそも添字を使わない書き方（範囲 for、アルゴリズム）にすると起きにくい。

## 基本

### よくある未定義動作

| やったこと | 例 |
| --- | --- |
| 範囲外アクセス | `v[v.size()]`、`arr[-1]` |
| 消えたオブジェクトを使う | ローカル変数の参照を返す、`delete` した後に使う |
| 壊れたイテレータ・参照を使う | `push_back` で再確保された後の古い参照 |
| `nullptr` を読む | `Enemy* e = nullptr; e->hp` |
| 初期化していない変数を読む | `int x; std::println("{}", x);` |
| 符号付き整数のオーバーフロー | `int x = INT_MAX; x + 1` |
| 空のコンテナの `front` / `back` / `pop_back` | `std::vector<int>{}.back()` |
| 二重解放 | 同じポインタを 2 回 `delete` |
| データ競争 | 2 つのスレッドが同じ変数を同時に書く |
| 比較関数のルール違反 | `sort` に `<=` を渡す |

## 詳しく

### なぜ「何が起きても知らない」のか

C++ は、チェックを省くことで速く動くように作られています。たとえば `v[i]` は範囲チェックをしないので速いのですが、そのぶん範囲外を渡したときの動作は保証されません。さらにコンパイラは「UB は起きない」と仮定して最適化するので、UB があると**書いた覚えのない動き**になることがあります。

```cpp
// コンパイラは「x + 1 > x」は常に true だと仮定してよい（オーバーフローは UB なので）
bool AlwaysTrue(int x) { return x + 1 > x; }
```

### Debug と Release で違う理由

| ビルド | 何が違う | UB の見え方 |
| --- | --- | --- |
| Debug | 最適化なし。MSVC はイテレータの範囲チェックや未初期化メモリの埋め（`0xCC` など）がある | アサートで止まりやすい。たまたま動くこともある |
| Release | 最適化あり。チェックなし | 落ちる、値が化ける、何も起きない、のどれか |

### 見つける道具

| 道具 | 見つけられるもの | 使い方 |
| --- | --- | --- |
| AddressSanitizer（ASan） | 範囲外、解放後の使用、二重解放 | MSVC: プロジェクト設定で有効化（`/fsanitize=address`）。GCC / Clang: `-fsanitize=address` |
| UndefinedBehaviorSanitizer（UBSan） | オーバーフロー、nullptr の読み込みなど | GCC / Clang: `-fsanitize=undefined` |
| MSVC の Debug ビルド | vector の範囲外、壊れたイテレータ | Debug でアサートが出る |
| 警告 | 未初期化、型の不一致など | `/W4`（MSVC）、`-Wall -Wextra`（GCC / Clang） |
| `_GLIBCXX_ASSERTIONS` | 標準ライブラリの範囲外など（GCC） | `-D_GLIBCXX_ASSERTIONS` |

```cpp
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  // std::println("{}", v[3]);   // UB: Release では何が出るか分からない
  std::println("{}", v.at(2));   // at は範囲外なら例外を投げるので安全に気づける
}
```

```text title="実行結果"
3
```

### 起こさない書き方

| 危ない書き方 | 安全な書き方 |
| --- | --- |
| `for (int i = 0; i <= v.size(); ++i)` | `for (const auto& x : v)` |
| `int x;` | `int x = 0;` / `int x{};` |
| `Enemy* e; ... e->hp` | `Enemy* e = nullptr; ... if (e) { e->hp }` |
| `new` / `delete` | `std::make_unique` |
| 参照を保存する | ID で覚える、または寿命を設計する |
| `v.back()` | `if (!v.empty()) v.back()` |

## ゲームでの例

| 症状 | よくある原因 |
| --- | --- |
| Release だけで落ちる | 未初期化の変数、範囲外アクセス |
| たまにだけ落ちる | 消えた敵を指すポインタ（倒されたタイミング次第） |
| 関係ないオブジェクトの値が変わる | 範囲外への書き込みで別の変数を壊している |
| 特定のステージだけおかしい | 配列の大きさがステージによって違い、範囲外になっている |

## よくあるミス

??? failure "「動いたから大丈夫」と思う"
    UB はたまたま動くことがあります。別の PC、別のコンパイラ、少しコードを変えただけで壊れることがあります。

??? failure "未初期化のメンバ変数"
    ```cpp
    struct Enemy {
      int hp;      // 初期化していない
      float speed;
    };
    Enemy e;  // hp も speed もゴミ

    struct Enemy2 {
      int hp = 100;  // OK: 初期値を書いておく
      float speed = 1.0f;
    };
    ```

## これだけ覚える

!!! abstract "まとめ"
    - [x] UB は「何が起きてもおかしくない」。動いても安心しない
    - [x] 範囲外・消えたもの・nullptr・未初期化に注意
    - [x] 変数は必ず初期化する
    - [x] AddressSanitizer と警告で見つける

## 関連ページ

- [cppreference: Undefined behavior](https://en.cppreference.com/w/cpp/language/ub)
- [Microsoft Learn: AddressSanitizer](https://learn.microsoft.com/ja-jp/cpp/sanitizers/asan)
