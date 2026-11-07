// アクセス制御・静的・名前空間
class Secret {
 private:
  int hidden_ = 0;
  void Hide() {}
 protected:
  int prot_ = 0;
 public:
  void Show() {}
};

namespace ns {
int Value() { return 1; }
}

void Access() {
  Secret s;
  s.hidden_ = 1;                         // C2248: private メンバー
  s.Hide();                              // C2248
  s.prot_ = 2;                           // C2248: protected
  Secret::Show();                        // 静的でない関数を修飾名で呼ぶ
  ns::Nothing();                         // C2039
  Value();                               // C3861: ns:: を付けていない
}
