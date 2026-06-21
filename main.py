# 1. BaseAccount là Abstract Base Class chứa các thuộc tính chung:
#    - bank_name
#    - __balance (đóng gói)
#    - owner_name, account_number
# 2. SavingsAccount kế thừa BaseAccount:
#    - Có interest_rate
#    - Rút tiền bị phí 2%
#    - Có apply_interest()
# 3. CreditAccount kế thừa BaseAccount:
#    - Có credit_limit
#    - Cho phép số dư âm trong hạn mức
# 4. DigitalPremiumMixin:
#    - Hoàn tiền 1% cho giao dịch > 5,000,000
# 5. HybridAccount:
#    - Đa kế thừa SavingsAccount + DigitalPremiumMixin
# 6. Overloading:
#    - __add__
#    - __lt__
# 7. Duck Typing:
#    - process_payment()
#    - VNPayGateway
#    - ViettelMoneyGateway
# 8. Edge Cases:
#    - Abstract Class
#    - Credit Limit
#    - Overloading Type Check
#    - Invalid Payment Gateway

from abc import ABC, abstractmethod


class BaseAccount(ABC):
    bank_name = "Vietcombank"

    def __init__(self, owner_name, account_number):
        self.__balance = 0
        self.owner_name = owner_name
        self.account_number = account_number

    @property
    def balance(self):
        return self.__balance

    def _increase_balance(self, amount):
        self.__balance += amount

    def _decrease_balance(self, amount):
        self.__balance -= amount

    @property
    def owner_name(self):
        return self._owner_name

    @owner_name.setter
    def owner_name(self, value):
        self._owner_name = " ".join(value.split()).upper()

    @property
    def account_number(self):
        return self._account_number

    @account_number.setter
    def account_number(self, value):
        if not BaseAccount.validate_account_number(value):
            raise ValueError("Số tài khoản không hợp lệ")
        self._account_number = value

    @staticmethod
    def validate_account_number(account_number):
        return len(account_number) == 10 and account_number.isdigit()

    @classmethod
    def update_bank_name(cls, new_name):
        cls.bank_name = new_name

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    def __add__(self, other):
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance + other.balance

    def __lt__(self, other):
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance < other.balance


class SavingsAccount(BaseAccount):
    def __init__(self, owner_name, account_number, interest_rate):
        super().__init__(owner_name, account_number)
        self.interest_rate = interest_rate

    def deposit(self, amount):
        self._increase_balance(amount)

    def withdraw(self, amount):
        fee = amount * 0.02
        total = amount + fee

        if self.balance < total:
            raise ValueError("Không đủ số dư")

        self._decrease_balance(total)

    def apply_interest(self):
        interest = self.balance * self.interest_rate
        self._increase_balance(interest)
        return interest


class CreditAccount(BaseAccount):
    def __init__(self, owner_name, account_number, credit_limit):
        super().__init__(owner_name, account_number)
        self.credit_limit = credit_limit

    def deposit(self, amount):
        self._increase_balance(amount)

    def withdraw(self, amount):
        if self.balance - amount < -self.credit_limit:
            raise ValueError("Vượt quá hạn mức thấu chi cho phép")

        self._decrease_balance(amount)


class DigitalPremiumMixin:
    def cashback_reward(self, amount):
        if amount > 5_000_000:
            return amount * 0.01
        return 0


class HybridAccount(SavingsAccount, DigitalPremiumMixin):
    pass


class VNPayGateway:
    def execute_pay(self, account, amount):
        account.withdraw(amount)


class ViettelMoneyGateway:
    def execute_pay(self, account, amount):
        account.withdraw(amount)


def process_payment(payment_gateway, account, amount):
    try:
        payment_gateway.execute_pay(account, amount)
        print("Thanh toán thành công!")
    except AttributeError:
        print("Cổng thanh toán không hợp lệ hoặc chưa được tích hợp")


def create_account():
    print("\\n1. Savings Account")
    print("2. Credit Account")
    print("3. Hybrid Account")

    choice = input("Chọn loại tài khoản: ")

    try:
        account_number = input("Nhập số tài khoản: ")
        owner_name = input("Nhập tên chủ tài khoản: ")

        if choice == "1":
            rate = float(input("Lãi suất: "))
            return SavingsAccount(owner_name, account_number, rate)

        elif choice == "2":
            limit = float(input("Hạn mức tín dụng: "))
            return CreditAccount(owner_name, account_number, limit)

        elif choice == "3":
            rate = float(input("Lãi suất: "))
            return HybridAccount(owner_name, account_number, rate)

    except Exception as e:
        print("Lỗi:", e)

    return None


def main():
    accounts = []
    current_account = None

    while True:
        print("\\n" + " VIETCOMBANK DIGIBANK PRO ".center(50, "="))
        print("1. Mở tài khoản")
        print("2. Xem thông tin")
        print("3. Nạp / Rút")
        print("4. Áp dụng lãi suất")
        print("5. Overloading")
        print("6. Thanh toán")
        print("7. Thoát")

        choice = input("Chọn: ")

        match choice:
            case "1":
                acc = create_account()

                if acc:
                    accounts.append(acc)
                    current_account = acc
                    print("Tạo tài khoản thành công")

            case "2":
                if not current_account:
                    print("Chưa có tài khoản")
                    continue

                print("Chủ TK:", current_account.owner_name)
                print("STK:", current_account.account_number)
                print("Số dư:", current_account.balance)
                print("MRO:", [c.__name__ for c in current_account.__class__.__mro__])

            case "3":
                if not current_account:
                    continue

                action = input("1.Nạp 2.Rút: ")
                amount = float(input("Số tiền: "))

                try:
                    if action == "1":
                        current_account.deposit(amount)

                        if isinstance(current_account, HybridAccount):
                            cashback = current_account.cashback_reward(amount)
                            if cashback:
                                current_account.deposit(cashback)
                                print("Cashback:", cashback)

                    else:
                        current_account.withdraw(amount)

                    print("Số dư:", current_account.balance)

                except Exception as e:
                    print(e)

            case "4":
                if isinstance(current_account, SavingsAccount):
                    interest = current_account.apply_interest()
                    print("Tiền lãi:", interest)
                else:
                    print("Không hỗ trợ")

            case "5":
                if len(accounts) < 2:
                    print("Cần ít nhất 2 tài khoản")
                    continue

                other = accounts[0] if accounts[0] != current_account else accounts[1]

                print("A < B =", current_account < other)
                print("A + B =", current_account + other)

            case "6":
                if not current_account:
                    continue

                gateway_choice = input("1.VNPay 2.ViettelMoney: ")
                amount = float(input("Số tiền: "))

                gateway = VNPayGateway() if gateway_choice == "1" else ViettelMoneyGateway()
                process_payment(gateway, current_account, amount)

            case "7":
                break


if __name__ == "__main__":
    main()