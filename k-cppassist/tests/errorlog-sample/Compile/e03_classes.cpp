// クラスまわり
class Shape {
 public:
  virtual double Area() const = 0;
  virtual ~Shape() = default;
};

class Circle : public Shape {
 public:
  double Area() { return 3.14; }         // const が無く override にならない(Circle も抽象のまま)
};

class NoDefault {
 public:
  NoDefault(int v) : v_(v) {}
  int v_;
};

class Deleted {
 public:
  Deleted() = default;
  Deleted(const Deleted&) = delete;
  void Foo();
};

class Dup {
 public:
  void Bar();
  void Bar();                            // C2535: 同じメンバーの再宣言
  int x_;
  int x_;                                // C2086 系: 再定義
};

void Classes() {
  Shape s;                               // C2259: 抽象クラス
  NoDefault nd;                          // C2512: 既定コンストラクターがない
  Deleted d1;
  Deleted d2 = d1;                       // C2280: 削除された関数
  Circle c;                              // C2259
  c.Perimeter();                         // C2039: メンバーがない
  c.Area(1, 2);                          // C2661: 引数の数
  (void)s; (void)nd; (void)d2;
}

void Deleted::Foo() {}
void Missing::Baz() {}                   // C2653: Missing はクラスではない
int Circle::Radius() { return 0; }       // C2039: 宣言されていないメンバー
