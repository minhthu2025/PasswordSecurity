import os
import getpass
from datetime import datetime

from modules.database import init_db
from modules.password_utils import get_password_strength, meets_password_requirements, get_password_requirements_message, check_password_strength
from modules.auth import (
    register_user,
    login_user,
    get_user_profile,
    update_user_profile,
    change_user_password,
)
from modules.logger import log_activity, ACTION_LOGOUT


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def print_header(title: str):
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def input_nonempty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Giá trị không được để trống.")


def do_check_password():
    """Kiểm tra độ mạnh bất kỳ mật khẩu nào, không cần đăng nhập."""
    print_header("KIỂM TRA ĐỘ MẠNH MẬT KHẨU")
    print("Nhập mật khẩu bất kỳ để kiểm tra (Ctrl+C để hủy).\n")
    try:
        while True:
            password = getpass.getpass("Mật khẩu cần kiểm tra: ")
            if not password:
                print("Vui lòng nhập mật khẩu.")
                continue
            strength = check_password_strength(password)
            if strength == "Yếu":
                print(f"\n  Kết quả: Yếu")
                print(f"  {get_password_requirements_message()}")
            elif strength == "Trung bình":
                print(f"\n  Kết quả: Trung bình")
                print("  Mật khẩu đủ yêu cầu nhưng ngắn (≤ 8 ký tự). Nên dùng > 8 ký tự.")
            else:
                print(f"\n  Kết quả: Mạnh")
                print("  Mật khẩu tốt!")
            print()
            again = input("Kiểm tra mật khẩu khác? (y/n): ").strip().lower()
            if again != "y":
                break
    except KeyboardInterrupt:
        print("\nĐã hủy.")
    input("\nNhấn Enter để quay lại menu chính...")


def main_menu():
    while True:
        print_header("CÔNG CỤ KIỂM TRA ĐỘ MẠNH MẬT KHẨU - MENU CHÍNH")
        print("1. Đăng ký tài khoản mới")
        print("2. Đăng nhập")
        print("3. Kiểm tra độ mạnh mật khẩu (bất kỳ)")
        print("4. Thoát")
        choice = input("\nChọn chức năng (1-4): ").strip()

        if choice == "1":
            do_register()
        elif choice == "2":
            do_login()
        elif choice == "3":
            do_check_password()
        elif choice == "4":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ.")


def do_register():
    print_header("ĐĂNG KÝ TÀI KHOẢN")
    try:
        username = input_nonempty("Username: ")
        full_name = input_nonempty("Họ và tên: ")
        email = input_nonempty("Email: ")

        # Password with strength feedback
        while True:
            password = getpass.getpass("Mật khẩu: ")
            strength = get_password_strength(password)
            print(f"Độ mạnh mật khẩu: {strength}")
            if not meets_password_requirements(password):
                print(get_password_requirements_message())
                continue
            break

        confirm_password = getpass.getpass("Xác nhận mật khẩu: ")

        phone = input("Số điện thoại (không bắt buộc, 10 số): ").strip() or None
        identify_card = input("Số CMND/CCCD (không bắt buộc, 12 số): ").strip() or None
        address = input("Địa chỉ (không bắt buộc): ").strip() or None

        success, message, user_id = register_user(
            username=username,
            full_name=full_name,
            email=email,
            password=password,
            confirm_password=confirm_password,
            phone=phone,
            identify_card=identify_card,
            address=address,
        )
        print(f"\n{message}")
    except KeyboardInterrupt:
        print("\nĐã hủy đăng ký.")
    except Exception as e:
        print(f"\nLỗi: {e}")
    input("\nNhấn Enter để quay lại menu chính...")


def do_login():
    print_header("ĐĂNG NHẬP")
    try:
        identifier = input_nonempty("Username hoặc Email: ")
        password = getpass.getpass("Mật khẩu: ")

        success, message, user = login_user(identifier, password)

        if not success:
            print(f"\n{message}")
        else:
            # Hiển thị thông báo chào mừng
            username = user.get("username", "")
            print(f"\nĐăng nhập thành công! Chào mừng {username}")

            # Hiển thị thông tin tài khoản
            print("\nThông tin tài khoản:")
            print(f"- Username : {username}")
            print(f"- Email    : {user.get('email') or '(chưa cập nhật)'}")
            print(f"- Họ tên   : {user.get('full_name') or '(chưa cập nhật)'}")

            # Kiểm tra độ mạnh mật khẩu
            strength = check_password_strength(password)
            print("\n=== KIỂM TRA BẢO MẬT ===")
            print(f"Mật khẩu hiện tại của bạn đang ở mức: **{strength}**")
            if strength == "Yếu":
                print("\n⚠️  Cảnh báo: Mật khẩu của bạn quá yếu, không đáp ứng yêu cầu tối thiểu.")
                print("Gợi ý: Nên đổi mật khẩu mới với ít nhất 6 ký tự, kết hợp chữ hoa, chữ thường, số và ký tự đặc biệt.")
            elif strength == "Trung bình":
                print("\n⚠️  Cảnh báo: Mật khẩu của bạn chưa đủ mạnh.")
                print("Gợi ý: Nên đổi mật khẩu mới với ít nhất 12 ký tự, kết hợp chữ hoa, chữ thường, số và ký tự đặc biệt.")
            else:
                print("\n✅ Mật khẩu của bạn đang ở mức tốt.")

            user_session(user)
    except KeyboardInterrupt:
        print("\nĐã hủy đăng nhập.")
    except Exception as e:
        print(f"\nLỗi: {e}")
    input("\nNhấn Enter để quay lại menu chính...")


def user_session(user: dict):
    """Menu chính sau khi đăng nhập thành công."""
    user_id = user["id"]
    while True:
        print()
        print("1. Đổi mật khẩu ngay")
        print("2. Xem thông tin chi tiết")
        print("3. Chỉnh sửa thông tin")
        print("4. Quay lại menu chính")
        choice = input("\nChọn chức năng (1-4): ").strip()

        if choice == "1":
            change_password(user_id)
        elif choice == "2":
            view_profile(user_id)
        elif choice == "3":
            update_profile(user_id)
        elif choice == "4":
            log_activity(user_id, ACTION_LOGOUT, "Người dùng đăng xuất")
            print("Đã đăng xuất.")
            break
        else:
            print("Lựa chọn không hợp lệ.")


def view_profile(user_id: int):
    profile = get_user_profile(user_id)
    if not profile:
        print("Không tìm thấy thông tin.")
        return
    print_header("THÔNG TIN CÁ NHÂN")
    print(f"Họ và tên     : {profile.get('full_name') or '(chưa cập nhật)'}")
    print(f"Email         : {profile.get('email') or '(chưa cập nhật)'}")
    print(f"Số điện thoại : {profile.get('phone') or '(chưa cập nhật)'}")
    print(f"CMND/CCCD     : {profile.get('identify_card') or '(chưa cập nhật)'}")
    print(f"Địa chỉ       : {profile.get('address') or '(chưa cập nhật)'}")
    input("\nNhấn Enter để quay lại...")


def update_profile(user_id: int):
    current = get_user_profile(user_id)
    if not current:
        print("Không tìm thấy tài khoản.")
        return

    print_header("CẬP NHẬT THÔNG TIN")
    print("Để giữ nguyên giá trị cũ, hãy để trống và nhấn Enter.")
    print(f"Họ và tên hiện tại     : {current.get('full_name') or '(chưa có)'}")
    full_name = input("Họ và tên mới          : ").strip() or None

    print(f"Email hiện tại         : {current.get('email') or '(chưa có)'}")
    email = input("Email mới              : ").strip() or None

    print(f"Số điện thoại hiện tại : {current.get('phone') or '(chưa có)'}")
    phone = input("Số điện thoại mới (10 số): ").strip() or None

    print(f"CMND/CCCD hiện tại     : {current.get('identify_card') or '(chưa có)'}")
    identify_card = input("Số CMND/CCCD mới (12 số): ").strip() or None

    print(f"Địa chỉ hiện tại       : {current.get('address') or '(chưa có)'}")
    address = input("Địa chỉ mới            : ").strip() or None

    success, message = update_user_profile(
        user_id,
        full_name=full_name,
        email=email,
        phone=phone,
        identify_card=identify_card,
        address=address,
    )
    print(f"\n{message}")
    input("\nNhấn Enter để quay lại...")


def change_password(user_id: int):
    print_header("ĐỔI MẬT KHẨU")
    try:
        old_pw = getpass.getpass("Mật khẩu cũ: ")
        while True:
            new_pw = getpass.getpass("Mật khẩu mới: ")
            if not meets_password_requirements(new_pw):
                print(get_password_requirements_message())
                continue
            strength = get_password_strength(new_pw)
            print(f"Độ mạnh mật khẩu mới: {strength}")
            break
        confirm_pw = getpass.getpass("Xác nhận mật khẩu mới: ")

        success, message = change_user_password(user_id, old_pw, new_pw, confirm_pw)
        print(f"\n{message}")
    except KeyboardInterrupt:
        print("\nĐã hủy đổi mật khẩu.")
    input("\nNhấn Enter để quay lại...")


if __name__ == "__main__":
    try:
        print("Đang khởi tạo cơ sở dữ liệu...")
        init_db()
        print("Sẵn sàng.")
        main_menu()
    except Exception as e:
        print(f"Lỗi nghiêm trọng: {e}")
        import traceback
        traceback.print_exc()
