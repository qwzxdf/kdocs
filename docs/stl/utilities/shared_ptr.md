---
title: std::shared_ptr / std::weak_ptr
tags:
  - ユーティリティ
  - メモリ
---

# std::shared_ptr / std::weak_ptr

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::shared_ptr` は、**持ち主が何人もいてよいスマートポインタ**です。中で「今何人が持っているか」（参照カウント）を数えていて、最後の 1 人が手放したときに自動で `delete` します。`std::weak_ptr` は、shared_ptr が持っているものを**持ち主にならずに見る**ためのポインタで、相手がもう消えたかどうかを確かめられます。

!!! tip "ポイント"
    - <strong>まず [`unique_ptr`](unique_ptr.md) を検討する。</strong> 本当に「持ち主が複数」になる場面はゲームではそれほど多くない。
    - 作るのは `std::make_shared<T>(...)`。
    - 「相手が消えているかもしれない」参照には `weak_ptr` を使い、使う直前に `lock()` する。
    - **お互いを shared_ptr で持ち合うと、永遠に消えなくなる**（循環参照）。片方を weak_ptr にする。

!!! info "このページを読む前に"
    [`std::unique_ptr`](unique_ptr.md) と [所有権](../../basics/ownership.md) を先に読んでください。

## 宣言

```cpp
template <class T>
class shared_ptr;

template <class T>
class weak_ptr;
```

## 関数一覧

| 関数 | 重要度 | 何をする | 対象 |
| --- | --- | --- | --- |
| [`std::make_shared`](#make_shared) | <span class="rank rank-must">必須</span> | 作って shared_ptr にする | shared_ptr |
| [`operator->`](#arrow) | <span class="rank rank-must">必須</span> | 中身のメンバにアクセス | shared_ptr |
| [`operator*`](#deref) | <span class="rank rank-must">必須</span> | 中身の参照 | shared_ptr |
| [コピー](#copy) | <span class="rank rank-must">必須</span> | 持ち主を 1 人増やす | shared_ptr |
| [`operator bool`](#bool) | <span class="rank rank-often">よく使う</span> | 空でないか | shared_ptr |
| [`weak_ptr` を作る](#weak) | <span class="rank rank-often">よく使う</span> | 持ち主にならずに見る | weak_ptr |
| [`lock`](#lock) | <span class="rank rank-often">よく使う</span> | まだ生きていれば shared_ptr を取り出す | weak_ptr |
| [`expired`](#expired) | <span class="rank rank-sometimes">たまに</span> | もう消えたか | weak_ptr |
| [`reset`](#reset) | <span class="rank rank-sometimes">たまに</span> | 手放す | 両方 |
| [`use_count`](#use_count) | <span class="rank rank-sometimes">たまに</span> | 何人が持っているか（デバッグ用） | 両方 |
| [`get`](#get) | <span class="rank rank-sometimes">たまに</span> | 生ポインタを取り出す | shared_ptr |
| [`std::enable_shared_from_this`](#shared_from_this) | <span class="rank rank-rare">知ってるだけ</span> | 自分自身の shared_ptr を作る | shared_ptr |
| [`std::dynamic_pointer_cast`](#pointer_cast) | <span class="rank rank-rare">知ってるだけ</span> | 派生クラスの shared_ptr にキャスト | shared_ptr |

## よくある使い方

### 1. 複数から共有する

```cpp
#include <memory>
#include <print>
#include <string>

struct Texture {
  explicit Texture(std::string p) : path(std::move(p)) {}
  ~Texture() { std::println("{} を解放", path); }
  std::string path;
};

int main() {
  std::shared_ptr<Texture> a = std::make_shared<Texture>("slime.png");
  {
    std::shared_ptr<Texture> b = a;  // 持ち主が 2 人になる
    std::println("持ち主 {} 人", a.use_count());
  }  // b が消えて 1 人に
  std::println("持ち主 {} 人", a.use_count());
}  // a が消えて 0 人 → 解放
```

```text title="実行結果"
持ち主 2 人
持ち主 1 人
slime.png を解放
```

### 2. 消えているかもしれない相手を weak_ptr で見る

```cpp
#include <memory>
#include <print>

struct Enemy {
  int hp = 100;
};

struct Homing {
  std::weak_ptr<Enemy> target;  // 持ち主にはならない

  void Update() {
    if (auto t = target.lock()) {  // まだ生きていれば取り出せる
      std::println("追尾中（HP {}）", t->hp);
    } else {
      std::println("対象が消えた");
    }
  }
};

int main() {
  auto enemy = std::make_shared<Enemy>();
  Homing missile{enemy};
  missile.Update();
  enemy.reset();  // 敵が倒された
  missile.Update();
}
```

```text title="実行結果"
追尾中（HP 100）
対象が消えた
```

## 関数の詳しい説明

### std::make_shared {#make_shared}

```cpp
template <class T, class... Args>
std::shared_ptr<T> make_shared(Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 何個でも | `T` のコンストラクタ引数 |

- オブジェクトと参照カウントを**1 回の確保**でまとめて作ります（`new` してから shared_ptr に渡すより速い）

<div class="anim" data-label="auto p = std::make_shared<Enemy>()">
_ # p は空
+A:1 # 作って、参照数は 1
</div>

### operator-> {#arrow}

```cpp
T* operator->() const noexcept;
```

- 中身のメンバにアクセスします。空のとき未定義動作

### operator* {#deref}

```cpp
T& operator*() const noexcept;
```

- 中身の参照を返します。空のとき未定義動作

### コピー {#copy}

```cpp
shared_ptr(const shared_ptr& other) noexcept;
shared_ptr& operator=(const shared_ptr& other) noexcept;
```

- 同じものを指す shared_ptr がもう 1 つでき、参照カウントが 1 増えます
- ムーブ（`std::move`）なら参照カウントは変わりません（持ち主が移るだけ）

<div class="anim" data-label="auto q = p">
A:1 | _ # p だけが持っている（参照数 1）
A:1 | *A:1 # q が同じものを指す
A:2 | A:2 # 参照数が 2 になる
</div>

### operator bool {#bool}

```cpp
explicit operator bool() const noexcept;
```

- 何かを持っていれば `true`

```cpp
#include <memory>
#include <print>

int main() {
  std::shared_ptr<int> p;
  std::println("{}", static_cast<bool>(p));
  p = std::make_shared<int>(5);
  std::shared_ptr<int> q = p;  // コピー
  *q += 1;
  std::println("{} {} {}", static_cast<bool>(p), *p, p.use_count());
}
```

```text title="実行結果"
false
true 6 2
```

### weak_ptr を作る {#weak}

```cpp
weak_ptr(const shared_ptr<T>& r) noexcept;
```

- shared_ptr から作ります。参照カウントは増えません（相手が消えるのを邪魔しない）
- weak_ptr から直接 `->` で中身は使えません。`lock()` で shared_ptr に戻してから使います

### lock {#lock}

```cpp
std::shared_ptr<T> lock() const noexcept;
```

- 戻り値: 相手がまだ生きていれば、それを指す shared_ptr。消えていれば空の shared_ptr
- 取り出した shared_ptr を持っている間は、相手が消えないことが保証されます

### expired {#expired}

```cpp
bool expired() const noexcept;
```

- 相手がもう消えていれば `true`

```cpp
#include <memory>
#include <print>

int main() {
  auto p = std::make_shared<int>(1);
  std::weak_ptr<int> w = p;
  std::println("{}", w.expired());
  p.reset();
  std::println("{}", w.expired());
}
```

```text title="実行結果"
false
true
```

!!! note "実際は"
    `expired()` で確認してから `lock()` すると、その間に消える可能性があります（マルチスレッドのとき）。使うなら最初から `if (auto p = w.lock())` で書きます。

### reset {#reset}

```cpp
void reset() noexcept;
```

- 手放します。shared_ptr なら参照カウントが 1 減り、0 になれば解放されます

<div class="anim" data-label="q.reset()">
A:2 | A:2 # p と q が持っている
A:2 | xA:2 # q が手放す
A:1 | _ # 参照数が 1 に減る。0 になると破棄される
</div>

### use_count {#use_count}

```cpp
long use_count() const noexcept;
```

- 今何人の shared_ptr が持っているか。デバッグ表示用で、ロジックに使うものではありません

<div class="anim" data-label="p.use_count()">
A:2 | A:2 # p と q
*A:2 | A:2 # 今の参照数（2）を返す
</div>

### get {#get}

```cpp
T* get() const noexcept;
```

- 生ポインタを取り出します。持ち主は変わりません

### std::enable_shared_from_this {#shared_from_this}

```cpp
template <class T>
class enable_shared_from_this {
 public:
  std::shared_ptr<T> shared_from_this();
  std::weak_ptr<T> weak_from_this() noexcept;
};
```

- クラスがこれを継承すると、メンバ関数の中で「自分を指す shared_ptr」を作れます（`this` から shared_ptr を作ると二重管理になるため）
- **shared_ptr で管理されているときだけ**使えます

```cpp
#include <memory>
#include <print>
#include <vector>

class Unit : public std::enable_shared_from_this<Unit> {
 public:
  void Register(std::vector<std::weak_ptr<Unit>>& list) {
    list.push_back(weak_from_this());
  }
};

int main() {
  std::vector<std::weak_ptr<Unit>> registry;
  auto unit = std::make_shared<Unit>();
  unit->Register(registry);
  std::println("登録 {} / 生きている？ {}", registry.size(), !registry[0].expired());
}
```

```text title="実行結果"
登録 1 / 生きている？ true
```

### std::dynamic_pointer_cast {#pointer_cast}

```cpp
template <class T, class U>
std::shared_ptr<T> dynamic_pointer_cast(const std::shared_ptr<U>& r) noexcept;
```

- `dynamic_cast` の shared_ptr 版。キャストできなければ空の shared_ptr を返します。`static_pointer_cast` もあります

```cpp
#include <memory>
#include <print>

struct Base {
  virtual ~Base() = default;
};
struct Boss : Base {
  int phase = 2;
};

int main() {
  std::shared_ptr<Base> obj = std::make_shared<Boss>();
  if (auto boss = std::dynamic_pointer_cast<Boss>(obj)) {
    std::println("ボス フェーズ {}", boss->phase);
  }
}
```

```text title="実行結果"
ボス フェーズ 2
```

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    std::shared_ptr<Texture> t(new Texture("a.png"));  // 確保が 2 回
    Enemy* target;  // 消えたかどうか分からない
    ```

=== "今の書き方"

    ```cpp
    auto t = std::make_shared<Texture>("a.png");
    std::weak_ptr<Enemy> target;
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 共有リソース | 同じテクスチャ・サウンドを複数のオブジェクトが使う（最後の 1 つが消えたら解放） |
| 追尾・ターゲット | `weak_ptr` で敵を指す（倒されたら `lock()` が失敗する） |
| イベントの購読 | 購読者が消えたら自動で通知をやめる |

## パフォーマンス

- 参照カウントの増減は<strong>スレッドセーフ（アトミック）</strong>なので、コピーするたびに少しコストがかかります。引数は `const std::shared_ptr<T>&` か、使うだけなら `T&` で渡します。
- 1 つの shared_ptr は生ポインタ 2 個ぶん（16 バイト）の大きさです。
- 参照カウントのせいで「いつ消えるか」が分かりにくくなります。ゲームではオブジェクトの寿命をはっきりさせたいので、unique_ptr + ID / ハンドルで管理するほうが好まれます。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の shared_ptr を `->` / `*` | 未定義動作 |
| 同じ生ポインタから shared_ptr を 2 つ作る | 二重解放（未定義動作） |
| shared_ptr で管理されていないのに `shared_from_this()` | `std::bad_weak_ptr` 例外 |

## よくあるミス

??? failure "循環参照で永遠に消えない"
    ```cpp
    struct Node {
      std::shared_ptr<Node> parent;  // 子 → 親
      std::vector<std::shared_ptr<Node>> children;  // 親 → 子
    };
    // 親と子がお互いを持ち合うので、参照カウントが 0 にならない
    ```

    片方（子 → 親）を `std::weak_ptr<Node>` にします。

??? failure "何でも shared_ptr にする"
    「とりあえず shared_ptr」にすると、誰が持ち主か分からなくなり、消えるタイミングも読めなくなります。持ち主が 1 人なら unique_ptr です。

??? failure "値渡しで毎回参照カウントが動く"
    `void Draw(std::shared_ptr<Sprite> s)` は呼ぶたびにアトミックな増減が起きます。使うだけなら `void Draw(const Sprite& s)` にします。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::unique_ptr`](unique_ptr.md) | 持ち主が 1 人。軽い | ほとんどの場合 |
| 生ポインタ | 消えたか分からない | 寿命がはっきりしている相手 |
| ID / ハンドル | 番号で間接的に指す | ゲームオブジェクトの参照（ECS など） |

## コンパイラ対応

C++11 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] まず unique_ptr。本当に共有するときだけ shared_ptr
    - [x] 作るのは `std::make_shared`
    - [x] 消えているかもしれない相手は weak_ptr + `lock()`
    - [x] 持ち合いは片方を weak_ptr に

## 関連ページ

- [cpprefjp: std::shared_ptr](https://cpprefjp.github.io/reference/memory/shared_ptr.html)
- [cppreference: std::weak_ptr](https://en.cppreference.com/w/cpp/memory/weak_ptr)
