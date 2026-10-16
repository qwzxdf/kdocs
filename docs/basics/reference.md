---
title: 参照と const 参照
tags:
  - 基礎
---

# 参照と const 参照

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++98〜</span>
</div>

**参照**は、**すでにある変数に付ける「別名」**です。`int& r = x;` と書くと、`r` は `x` そのものになり、`r` を書き換えると `x` も変わります。コピーを作らずに同じものを触れるので、関数の引数で大きなデータを渡すときに欠かせません。`const` を付けた**const 参照**（`const T&`）は「読むだけの別名」で、書き換えはできませんが、コピーもされません。

!!! tip "結論"
    - **関数の引数は、読むだけなら `const T&`、書き換えるなら `T&`、小さい型（int、float、ポインタ）なら値渡し。**
    - 参照は作ったときの相手から変えられない。null にもならない。
    - **消えた変数の参照を使うと未定義動作**（ローカル変数の参照を返す、など）。
    - 範囲 for も同じ考え方: 読むだけ `const auto&`、書き換える `auto&`。

## 基本

```cpp
#include <print>

int main() {
  int hp = 100;
  int& ref = hp;  // ref は hp の別名

  ref -= 30;
  std::println("hp = {}", hp);  // hp も 70 になっている

  const int& view = hp;  // 読むだけの別名
  // view = 0;  // コンパイルエラー: const なので書き換えられない
  std::println("view = {}", view);
}
```

```text title="実行結果"
hp = 70
view = 70
```

<div class="mem">
<div class="mem-step"><span class="mem-label">メモリ</span><span class="mem-cells"><span class="move">70</span></span><span class="mem-note">← hp も ref も view も、この 1 つの場所を指している（コピーは無い）</span></div>
</div>

## 詳しく

### 関数の引数での使い分け

| 書き方 | 重要度 | 意味 | 使うとき |
| --- | --- | --- | --- |
| `void F(const T& x)` | <span class="rank rank-must">必須</span> | 読むだけ。コピーしない | string、vector、構造体など大きいもの |
| `void F(T& x)` | <span class="rank rank-must">必須</span> | 書き換える。呼んだ側の変数が変わる | 中身を更新する関数 |
| `void F(T x)` | <span class="rank rank-must">必須</span> | コピーを受け取る | int、float、bool、ポインタ、小さい構造体（16 バイト程度まで） |
| `void F(T&& x)` | <span class="rank rank-sometimes">たまに</span> | 右辺値参照。ムーブで受け取る | [ムーブ](move.md)を参照 |

```cpp
#include <print>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  int hp;
};

// 読むだけ: const 参照
void PrintEnemy(const Enemy& e) { std::println("{} HP {}", e.name, e.hp); }

// 書き換える: 参照
void Damage(Enemy& e, int amount) { e.hp -= amount; }

// 小さい値: 値渡し
int Clamp0(int value) { return value < 0 ? 0 : value; }

int main() {
  Enemy slime = {"スライム", 10};
  Damage(slime, 15);
  slime.hp = Clamp0(slime.hp);
  PrintEnemy(slime);
}
```

```text title="実行結果"
スライム HP 0
```

### 値渡しとの違い

```cpp
#include <print>

void AddByValue(int x) { x += 10; }     // コピーを変えるだけ
void AddByRef(int& x) { x += 10; }      // 元を変える

int main() {
  int score = 0;
  AddByValue(score);
  std::println("{}", score);
  AddByRef(score);
  std::println("{}", score);
}
```

```text title="実行結果"
0
10
```

### 参照の性質

| 性質 | 参照 | ポインタ |
| --- | --- | --- |
| null になれる？ | なれない | なれる（`nullptr`） |
| あとから指す相手を変えられる？ | 変えられない | 変えられる |
| 書き方 | 普通の変数と同じ（`r.hp`） | `p->hp`、`*p` |
| 作るとき | 必ず相手を指定する | 後で代入してもいい |

「必ずある相手を使わせる」なら参照、「無いかもしれない」「付け替える」ならポインタを使います（[ポインタ](pointer.md)）。

### 戻り値の参照

```cpp
#include <print>
#include <vector>

class Party {
 public:
  // メンバへの参照を返す（Party が生きている間は安全）
  int& HpOf(std::size_t i) { return hp_[i]; }

 private:
  std::vector<int> hp_ = {30, 40, 50};
};

int main() {
  Party party;
  party.HpOf(1) += 5;  // 参照なので中身が変わる
  std::println("{}", party.HpOf(1));
}
```

```text title="実行結果"
45
```

### const の位置

| 書き方 | 意味 |
| --- | --- |
| `const T&` | 指す先を書き換えられない（読むだけ）。一番よく使う |
| `T const&` | 上と同じ意味（書き方が違うだけ） |
| `const` メンバ関数 `int Hp() const;` | その関数の中ではメンバを書き換えない。const 参照からも呼べる |

```cpp
#include <print>

class Player {
 public:
  int hp() const { return hp_; }   // const: 読むだけの関数
  void Heal(int n) { hp_ += n; }    // const なし: 書き換える関数

 private:
  int hp_ = 50;
};

void Show(const Player& p) {
  std::println("{}", p.hp());  // const 参照からは const 関数だけ呼べる
  // p.Heal(10);  // コンパイルエラー
}

int main() {
  Player p;
  p.Heal(10);
  Show(p);
}
```

```text title="実行結果"
60
```

## ゲームでの例

| 場面 | 書き方 |
| --- | --- |
| 描画関数 | `void Draw(const Sprite& sprite)` |
| 更新関数 | `void Update(Enemy& enemy, float dt)` |
| 全員を回して更新 | `for (auto& e : enemies)` |
| 全員を回して表示 | `for (const auto& e : enemies)` |
| ゲッター | `const std::string& name() const { return name_; }` |

## よくあるミス

??? failure "ローカル変数の参照を返す"
    ```cpp
    const std::string& MakeName() {
      std::string name = "Hero";
      return name;  // name は関数を抜けると消える
    }
    ```

    値で返します（`std::string MakeName()`）。戻り値の最適化が効くのでコピーのコストもほぼありません。

??? failure "vector の要素の参照を持ったまま push_back する"
    ```cpp
    Enemy& first = enemies[0];
    enemies.push_back(Enemy{});  // 再確保で first が壊れることがある
    ```

    詳しくは [vector の再確保](../stl/containers/vector.md#再確保引っ越しのしくみ) を参照してください。

??? failure "範囲 for で & を付け忘れて書き換わらない"
    ```cpp
    for (auto e : enemies) {
      e.hp -= 10;  // コピーを変えているだけ
    }
    for (auto& e : enemies) {
      e.hp -= 10;  // OK
    }
    ```

??? failure "int を const 参照で渡す"
    `void F(const int& x)` は間違いではありませんが、int は値渡しのほうが速いことが多いです（参照は中身がポインタなので、かえって間接参照が増える）。

## 理解度チェック

!!! question "Q1. 何が出力される？"
    ```cpp
    int a = 1;
    int& r = a;
    int b = r;
    b = 5;
    r = 3;
    std::println("{} {}", a, b);
    ```

    <div class="spoiler" markdown>

    **答え:** `3 5`。`b` は `r`（= `a`）の値をコピーした別の変数なので、`b = 5` は `a` に影響しません。`r = 3` は `a` を書き換えます。

    </div>

!!! question "Q2. `void Print(std::vector<int> v)` の問題点は？"
    <div class="spoiler" markdown>

    **答え:** 呼ぶたびに vector 全体がコピーされます。読むだけなら `const std::vector<int>&`（または `std::span<const int>`）にします。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 参照は別名。コピーしない
    - [x] 読むだけ `const T&`、書き換え `T&`、小さい型は値渡し
    - [x] 消える変数の参照を返さない・持ち続けない
    - [x] 範囲 for は `const auto&` / `auto&`

## 関連ページ

- [ポインタ](pointer.md)
- [ムーブ](move.md)
- [cppreference: Reference declaration](https://en.cppreference.com/w/cpp/language/reference)
