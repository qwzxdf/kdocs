---
title: コピーとムーブ
tags:
  - 最適化
---

# コピーとムーブ

C++ は**オブジェクトを渡すたびにコピーが起きる**言語です。`std::string` や `std::vector` のような大きなオブジェクトをコピーすると、メモリの確保と中身の複製が行われます。小さなコピーを 1 回するだけなら無視できますが、毎フレーム何千回も起きると、確保と複製で全体の速さに響きます。このページは無駄なコピーを見つけて、なくす方法をまとめます。道具は参照（`const&`）、ムーブ、ビュー（`string_view`、`span`）、コピーの省略（RVO）です（基礎は [参照](../basics/reference.md)、[ムーブ](../basics/move.md)）。

!!! tip "ポイント"
    - <strong>読むだけの大きなものは `const T&`</strong> で渡す。小さい型（`int`、`float`）は値渡し。
    - 文字列は<strong>`std::string_view`</strong>、配列は`std::span` で渡すとコピーも確保もない。
    - 受け取って持つなら値渡し + `std::move`。コンテナに入れるなら `emplace_back`。
    - 戻り値は値で返す。ムーブや RVO でコピーは起きない。`std::move` を `return` に付けない。
    - 範囲 for は `const auto&`。`auto` だと 1 つずつコピーする。
    - 「コピーされている」ことに気づくのが難しいので、コピーを禁止して見つける方法も使う。

!!! info "このページを読む前に"
    - [optimize/index.md](index.md)（このセクション全体の地図と、読む順番）
    - [計測（プロファイリング）](measure.md)（測ってから直す、という進め方）

## コピーがどれだけ重いか

| 型 | コピーで起きること | 重さ |
| --- | --- | --- |
| `int`、`float`、`Vec3` | 数バイトを複製 | ほぼ無料 |
| `std::string`（長い） | **メモリを確保**して、文字を複製 | 重い |
| `std::vector<T>` | メモリを確保して、全要素をコピー | とても重い（要素数に比例） |
| `std::shared_ptr` | 参照カウントを増やす（アトミック操作） | 軽いが、無料ではない |
| `std::function`（大きなキャプチャ） | 確保して複製 | 重い |
| `std::map` / `unordered_map` | ノードを 1 つずつ確保して複製 | 重い |

## 1. 引数の渡し方

```cpp
// 遅い：呼ぶたびに、vector 全体をコピーする
float Average(std::vector<float> values);

// 速い：コピーしない（読むだけ）
float Average(const std::vector<float>& values);

// もっと良い：vector でも array でも渡せる（コピーなし）
float Average(std::span<const float> values);
```

| 渡す・受け取る | 書き方 | コピー |
| --- | --- | --- |
| 読むだけ（大きい型） | `const T&` | なし |
| 読むだけ（文字列） | `std::string_view` | なし（ポインタと長さだけ） |
| 読むだけ（配列） | `std::span<const T>` | なし |
| 書き換える | `T&` | なし |
| 受け取って自分のものにする | `T`（値渡し）+ `std::move` | 渡す側が `std::move` すれば、なし |
| 小さい型 | `T`（値渡し） | ほぼ無料 |

詳しくは [const と引数の渡し方](../design/foundations/const-and-passing.md) を見てください。

## 2. ムーブ

**ムーブ**は「中身のメモリの持ち主を移す」操作です。`std::vector` をムーブすると要素をコピーせずポインタを付け替えるだけなので、一瞬です。

```cpp
std::vector<int> a = MakeBigList();     // 100 万個
std::vector<int> b = a;                  // コピー：100 万個を複製（重い）
std::vector<int> c = std::move(a);       // ムーブ：ポインタを移すだけ（一瞬）。a は空になる
```

### ムーブを使う場面

| 場面 | 書き方 |
| --- | --- |
| コンテナに入れる | `v.push_back(std::move(x));`、または `v.emplace_back(引数...)` |
| 受け取って持つ | `Enemy(std::string name) : name_(std::move(name)) {}` |
| 持ち主を移す | `owner = std::move(other);` |
| 関数から返す | `return x;`（`std::move` を付けない。下の注意） |

### emplace_back

```cpp
// push_back：一時オブジェクトを作ってから、ムーブする
v.push_back(Enemy("slime", 10));

// emplace_back：コンテナの中で、直接作る（ムーブも不要）
v.emplace_back("slime", 10);
```

### ムーブの注意

| 注意 | 説明 |
| --- | --- |
| `return std::move(x);` は書かない | ローカル変数を返すときは、コンパイラが自動で最適化（RVO・自動ムーブ）する。`std::move` を付けるとかえって最適化を妨げることがある |
| `const` のオブジェクトはムーブできない | `const std::string s; std::move(s)` は、コピーになる |
| ムーブしたあとの変数は使わない | 「有効だが中身は不定」な状態。再代入か破棄だけ |
| ムーブが遅い型もある | 大きな配列を持つ `std::array<T, N>` は、要素をムーブする（O(N)） |
| ムーブコンストラクタは `noexcept` にする | `noexcept` でないと `vector` の再確保のとき、ムーブせずにコピーされる |

## 3. 戻り値

```cpp
std::vector<Hit> FindHits() {
  std::vector<Hit> hits;
  // ... 追加 ...
  return hits;          // コピーされない（RVO / ムーブ）
}

auto hits = FindHits();  // ここに直接作られる、またはムーブされる
```

**値で返してよい**（コピーされません）。「大きいから引数で受け取って書き込もう」（`void FindHits(std::vector<Hit>& out)`）は、古い書き方です。ただし、毎フレーム呼ぶ関数で、メモリを使い回したい場合はあえて引数で受け取る（`out.clear()` して容量を再利用する）ほうが、速いこともあります（[メモリ確保](allocation.md)）。

| 返し方 | コピー | 使いどころ |
| --- | --- | --- |
| `T`（値で返す） | なし（RVO・ムーブ） | 基本はこれ |
| `const T&`（参照で返す） | なし | メンバ変数を読み取り専用で見せる。持ち主より長く使わない |
| `T&`（出力引数） | なし | 毎フレーム呼ぶ。容量を使い回したいとき |

## 4. 範囲 for のコピー

```cpp
// 遅い：1 つずつコピーしている（auto は値）
for (auto enemy : enemies) {        // Enemy を毎回コピー
  enemy.Update();                    // しかも、コピーを更新しているので、元は変わらない（バグ）
}

// 正しい：参照で回す
for (auto& enemy : enemies) {       // 書き換えるなら auto&
  enemy.Update();
}
for (const auto& enemy : enemies) { // 読むだけなら const auto&
  Draw(enemy);
}
```

**`auto` だけだと 1 つずつコピー**です。意図しないコピーの一番よくある原因です。

## 5. 文字列のコピーを減らす

| 遅い | 速い |
| --- | --- |
| `void Log(std::string msg)` | `void Log(std::string_view msg)` |
| `std::string name = GetName();`（毎回コピー） | `const std::string& name = GetName();`（`GetName` が参照を返すなら） |
| `s.substr(0, 5)` を比べるだけに使う（確保が起きる） | `std::string_view(s).substr(0, 5)`（コピーなし） |
| `std::string key = "player";` をループの中で毎回作る | `constexpr std::string_view kKey = "player";` |
| `map<std::string, T>` を `const char*` で引く（一時 string が作られる） | 透過的ハッシュで `string_view` のまま引く（[std::hash](../stl/utilities/hash.md#transparent)） |

## 6. 見えないコピーを見つける

コピーは書いていなくても**暗黙に**起きます。見つける方法です。

| 方法 | 説明 |
| --- | --- |
| コピーを禁止する（`= delete`） | 大きなクラスのコピーコンストラクタを `= delete` にすると、コピーしている場所がコンパイル エラーで分かる。必要なら明示的な `Clone()` を作る |
| プロファイラーで `memcpy` や `operator new` の上位を探す | コピーの呼び出し元をたどる（[計測](measure.md)） |
| 警告を有効にする | MSVC の `/W4`、Clang-Tidy の `performance-unnecessary-copy-initialization`、`performance-for-range-copy` |
| コピーのカウンター | コピーコンストラクタにカウンターを仕込んで、回数を数える |

```cpp
class Mesh {
 public:
  Mesh() = default;
  Mesh(const Mesh&) = delete;                  // 勝手にコピーされたら、エラー
  Mesh& operator=(const Mesh&) = delete;
  Mesh(Mesh&&) noexcept = default;             // ムーブは OK
  Mesh& operator=(Mesh&&) noexcept = default;

  Mesh Clone() const;                          // どうしても必要なら、明示的に
};
```

## ゲームでの使いどころ

| 場面 | 直し方 |
| --- | --- |
| 関数に大きな構造体を値渡ししている | `const&` にする |
| ログやメッセージの文字列 | `string_view` で受け取る |
| `for (auto e : entities)` | `for (auto& e : entities)` |
| コンテナに構造体を追加 | `emplace_back`、`std::move` |
| 設定の構造体を毎フレーム渡している | 参照・ポインタで、1 つを共有する |
| ラムダに大きなものをコピーキャプチャ | 参照キャプチャ（寿命に注意）か、`shared_ptr` で共有 |
| `vector<vector<T>>` を関数に値渡し | `const&` か `span` |

## よくあるミス

??? failure "`const std::string&` を受け取って、結局コピーして持つ"
    `Enemy(const std::string& name) : name_(name)` は必ず 1 回コピーします。持つだけなら `Enemy(std::string name) : name_(std::move(name))` のほうが一時オブジェクトを渡したときコピーなしで済みます。

??? failure "`return std::move(local);` と書く"
    かえって RVO を妨げ遅くなることがあります。`return local;` と書きます（コンパイラが警告を出すこともあります）。

??? failure "ムーブしたものをあとで使う"
    ムーブ後は中身が不定です。`std::move(a)` したあとの `a` は再代入するかそのまま破棄します。

??? failure "`const` 参照でもらったものを保存して使う"
    `const T&` で借りたものをメンバに**参照で**保存すると、元が消えたときダングリングになります。保存するならコピーかムーブで、値として持ちます（[所有権とライフタイム設計](../design/foundations/ownership-lifetime.md)）。

??? failure "小さな型まで、`const&` にする"
    `const int&` はポインタ（8 バイト）を渡すので、`int`（4 バイト）を値で渡すより遅くなることがあります。小さい型は値渡しです。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読むだけの大きなものは<strong>`const&`</strong>、文字列は`string_view`、配列は`span`
    - [x] 受け取って持つなら値渡し + `std::move`。コンテナへは `emplace_back`
    - [x] 戻り値は値で返す。`return std::move(x)` は書かない
    - [x] 範囲 for は`const auto&` / `auto&`（`auto` はコピー）
    - [x] 大きなクラスはコピーを `= delete` にして、無駄なコピーをエラーで見つける

## 関連ページ

- [最適化の進め方](index.md)
- [ムーブ（基礎）](../basics/move.md)
- [参照（基礎）](../basics/reference.md)
- [const と引数の渡し方](../design/foundations/const-and-passing.md)
- [メモリ確保](allocation.md)
- [std::string_view](../stl/utilities/string_view.md)
- [std::span](../stl/containers/span.md)
- [std::unique_ptr](../stl/utilities/unique_ptr.md)
