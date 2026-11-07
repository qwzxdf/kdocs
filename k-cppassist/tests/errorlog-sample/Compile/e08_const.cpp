// const・参照・ライフタイム
#include <string>

struct Counter {
  int count = 0;
  void Inc() { ++count; }
  int Get() const { return count; }
  void BadConst() const { count = 1; }   // const メソッドで書き換え
  void CallNonConst() const { Inc(); }   // C2662: const から非 const を呼ぶ
};

const int kMax = 10;

void Const(const Counter& c) {
  c.Inc();                               // C2662
  kMax = 20;                             // const に代入
  const std::string s = "a";
  s += "b";                              // const の文字列に追記
  int& r = kMax;                         // C2440: const int から int&
  (void)r;
}

int& Dangling() {
  int local = 1;
  return local;                          // C4172: ローカルの参照を返す
}
