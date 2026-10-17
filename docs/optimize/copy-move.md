---
title: コピーとムーブ
tags:
  - 最適化
---

# コピーとムーブ

C++ は、**オブジェクトを渡すたびに、コピーが起きる**言語です。`std::string` や `std::vector` のような大きなオブジェクトをコピーすると、**メモリの確保と、中身の複製**が行われます。小さなコピーを 1 回するだけなら無視できますが、**毎フレーム何千回も**起きると、確保と複製で、全体の速さに響きます。このページは、**無駄なコピーを見つけて、なくす**方法をまとめます。道具は、**参照**（`const&`）、**ムーブ**、**ビュー**（`string_view`、`span`）、<strong>コピーの省略（RVO）</strong>です（基礎は [参照](../basics/reference.md)、[ムーブ](../basics/move.md)）。

!!! tip "ポイント"
    - <strong>読むだけの大きなものは `const T&`</strong> で渡す。小さい型（`int`、`float`）は値渡し。
    - 文字列は<strong>`std::string_view`</strong>、配列は<strong>`std::span`</strong> で渡すと、コピーも確保もない。
    - 受け取って持つなら<strong>値渡し + `std::move`</strong>。コンテナに入れるなら `emplace_back`。
    - 戻り値は<strong>値で返す</strong>。ムーブや RVO で、コピーは起きない。`std::move` を `return` に付けない。
    - <strong>範囲 for は `const auto&`</strong>。`auto` だと、1 つずつコピーする。
    - 「コピーされている」ことに気づくのが難しいので、<strong>コピーを禁止して見つける</strong>方法も使う。

## コピーがどれだけ重いか

| 型 | コピーで起きること | 重さ |
| --- | --- | --- |
| `int`、`float`、`Vec3` | 数バイトを複製 | ほぼ無料 |
| `std::string`（長い） | **メモリを確保**して、文字を複製 | 重い |
| `std::vector<T>` | **メモリを確保**して、**全要素をコピー** | とても重い（要素数に比例） |
| `std::shared_ptr` | 参照カウントを増やす（アトミック操作） | 軽いが、無料ではない |
| `std::function`（大きなキャプチャ） | 確保して複製 | 重い |
| `std::map` / `unordered_map` | **ノードを 1 つずつ確保して複製** | 非常に重い |

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
| 受け取って、自分のものにする | `T`（値渡し）+ `std::move` | 渡す側が `std::move` すれば、なし |
| 小さい型 | `T`（値渡し） | ほぼ無料 |

詳しくは [const と引数の渡し方](../design/foundations/const-and-passing.md) を見てください。

## 2. ムーブ

**ムーブ**は、「中身のメモリの持ち主を**移す**」操作です。`std::vector` をムーブすると、要素をコピーせず、**ポインタを付け替えるだけ**なので、一瞬です。

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
| 関数から返す | **`return x;`**（`std::move` を付けない。下の注意） |

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
| **`return std::move(x);` は書かない** | ローカル変数を返すときは、コンパイラが自動で最適化（RVO・自動ムーブ）する。`std::move` を付けると、**かえって最適化を妨げる**ことがある |
| **`const` のオブジェクトは、ムーブできない** | `const std::string s; std::move(s)` は、コピーになる |
| **ムーブしたあとの変数は使わない** | 「有効だが中身は不定」な状態。再代入か、破棄だけ |
| **ムーブが遅い型もある** | 大きな配列を持つ `std::array<T, N>` は、要素をムーブする（O(N)） |
| **ムーブコンストラクタは `noexcept` にする** | `noexcept` でないと、`vector` の再確保のとき、ムーブせずにコピーされる |

## 3. 戻り値

```cpp
std::vector<Hit> FindHits() {
  std::vector<Hit> hits;
  // ... 追加 ...
  return hits;          // コピーされない（RVO / ムーブ）
}

auto hits = FindHits();  // ここに直接作られる、またはムーブされる
```

**値で返してよい**（コピーされません）。「大きいから、引数で受け取って書き込もう」（`void FindHits(std::vector<Hit>& out)`）は、古い書き方です。ただし、**毎フレーム呼ぶ関数**で、**メモリを使い回したい**場合は、あえて引数で受け取る（`out.clear()` して容量を再利用する）ほうが、速いこともあります（[メモリ確保](allocation.md)）。

| 返し方 | コピー | 使いどころ |
| --- | --- | --- |
| `T`（値で返す） | **なし**（RVO・ムーブ） | 基本はこれ |
| `const T&`（参照で返す） | なし | メンバ変数を、読み取り専用で見せる。持ち主より長く使わない |
| `T&`（出力引数） | なし | 毎フレーム呼ぶ。容量を使い回したいとき |

## 4. 範囲 for のコピー

```cpp
// 遅い：1 つずつコピーしている（auto は値）
for (auto enemy : enemies) {        // Enemy を、毎回コピー
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

**`auto` だけだと、1 つずつコピー**です。意図しないコピーの、一番よくある原因です。

## 5. 文字列のコピーを減らす

| 遅い | 速い |
| --- | --- |
| `void Log(std::string msg)` | `void Log(std::string_view msg)` |
| `std::string name = GetName();`（毎回コピー） | `const std::string& name = GetName();`（`GetName` が参照を返すなら） |
| `s.substr(0, 5)` を比べるだけに使う（確保が起きる） | `std::string_view(s).substr(0, 5)`（コピーなし） |
| `std::string key = "player";` を、ループの中で毎回作る | `constexpr std::string_view kKey = "player";` |
| `map<std::string, T>` を、`const char*` で引く（一時 string が作られる） | 透過的ハッシュで `string_view` のまま引く（[std::hash](../stl/utilities/hash.md#transparent)） |

## 6. 見えないコピーを見つける

コピーは、書いていなくても、**暗黙に**起きます。見つける方法です。

| 方法 | 説明 |
| --- | --- |
| **コピーを禁止する**（`= delete`） | 大きなクラスのコピーコンストラクタを `= delete` にすると、コピーしている場所が、コンパイル エラーで分かる。必要なら、明示的な `Clone()` を作る |
| **プロファイラーで、`memcpy` や `operator new` の上位を探す** | コピーの呼び出し元をたどる（[計測](measure.md)） |
| **警告を有効にする** | MSVC の `/W4`、Clang-Tidy の `performance-unnecessary-copy-initialization`、`performance-for-range-copy` |
| **コピーのカウンター** | コピーコンストラクタに、カウンターを仕込んで、回数を数える |

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
| 関数に、大きな構造体を値渡ししている | `const&` にする |
| ログやメッセージの文字列 | `string_view` で受け取る |
| `for (auto e : entities)` | `for (auto& e : entities)` |
| コンテナに、構造体を追加 | `emplace_back`、`std::move` |
| 設定の構造体を、毎フレーム渡している | 参照・ポインタで、1 つを共有する |
| ラムダに、大きなものをコピーキャプチャ | 参照キャプチャ（寿命に注意）か、`shared_ptr` で共有 |
| `vector<vector<T>>` を、関数に値渡し | `const&` か、`span` |

## よくあるミス

??? failure "`const std::string&` を受け取って、結局コピーして持つ"
    `Enemy(const std::string& name) : name_(name)` は、必ず 1 回コピーします。持つだけなら、`Enemy(std::string name) : name_(std::move(name))` のほうが、一時オブジェクトを渡したとき、コピーなしで済みます。

??? failure "`return std::move(local);` と書く"
    かえって RVO を妨げ、遅くなることがあります。`return local;` と書きます（コンパイラが警告を出すこともあります）。

??? failure "ムーブしたものを、あとで使う"
    ムーブ後は、中身が不定です。`std::move(a)` したあとの `a` は、再代入するか、そのまま破棄します。

??? failure "`const` 参照でもらったものを、保存して使う"
    `const T&` で借りたものを、メンバに**参照で**保存すると、元が消えたとき、ダングリングになります。保存するなら、コピーかムーブで、値として持ちます（[所有権とライフタイム設計](../design/foundations/ownership-lifetime.md)）。

??? failure "小さな型まで、`const&` にする"
    `const int&` は、ポインタ（8 バイト）を渡すので、`int`（4 バイト）を値で渡すより、遅くなることがあります。小さい型は、値渡しです。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読むだけの大きなものは<strong>`const&`</strong>、文字列は<strong>`string_view`</strong>、配列は<strong>`span`</strong>
    - [x] 受け取って持つなら<strong>値渡し + `std::move`</strong>。コンテナへは `emplace_back`
    - [x] 戻り値は<strong>値で返す</strong>。`return std::move(x)` は書かない
    - [x] 範囲 for は<strong>`const auto&` / `auto&`</strong>（`auto` はコピー）
    - [x] 大きなクラスは、コピーを `= delete` にして、無駄なコピーをエラーで見つける

## 関連ページ

- [最適化の進め方](index.md)
- [ムーブ（基礎）](../basics/move.md)
- [参照（基礎）](../basics/reference.md)
- [const と引数の渡し方](../design/foundations/const-and-passing.md)
- [メモリ確保](allocation.md)
- [std::string_view](../stl/utilities/string_view.md)
