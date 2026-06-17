"""
app.py — Giao diện Streamlit cho Password Security Tool.

Phong cách password manager cao cấp (Bitwarden / 1Password).
Chạy: streamlit run app.py
"""

from pathlib import Path

import streamlit as st

from modules.database import init_db
from modules.auth import (
    register_user,
    login_user,
    get_user_profile,
    update_user_profile,
    change_user_password,
)
from modules.password_utils import (
    password_input,
    get_password_strength,
    meets_password_requirements,
    get_password_requirements_message,
    check_password_strength,
)
from modules.logger import log_activity, ACTION_LOGOUT

# ---------------------------------------------------------------------------
# Hằng số giao diện
# ---------------------------------------------------------------------------
APP_NAME = "PassGuard"
APP_SUBTITLE = "Công cụ Kiểm tra Độ Mạnh Mật Khẩu & Mã Hóa Dữ Liệu"
PRIMARY = "#2563EB"
PRIMARY_DARK = "#1D4ED8"
PRIMARY_DEEP = "#1E3A8A"

PUBLIC_PAGES = {
    "Đăng ký": "register",
    "Đăng nhập": "login",
    "Kiểm tra độ mạnh mật khẩu": "check_password",
}

AUTH_PAGES = {
    "Xem Profile": "view_profile",
    "Cập nhật Profile": "update_profile",
    "Đổi mật khẩu": "change_password",
    "Đăng xuất": "logout",
}

HERO_INTRO = (
    "PassGuard giúp bạn kiểm tra độ mạnh mật khẩu theo thời gian thực và đăng ký tài khoản an toàn. "
    "Mật khẩu được băm bằng <strong>Argon2id</strong> kết hợp Salt ngẫu nhiên — chống tấn công Rainbow Table hiệu quả. "
    "Dữ liệu cá nhân nhạy cảm (SĐT, CMND, địa chỉ) được mã hóa <strong>AES-256-GCM</strong> trước khi lưu vào cơ sở dữ liệu."
)

# ---------------------------------------------------------------------------
# Cấu hình trang Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# CSS tùy chỉnh — kiểm soát layout toàn cục
# ---------------------------------------------------------------------------
def _inject_custom_css() -> None:
    """Inject theme xanh #2563EB, sidebar tối, form card, input cao cấp."""
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            :root {{
                --primary: {PRIMARY};
                --primary-dark: {PRIMARY_DARK};
                --primary-deep: {PRIMARY_DEEP};
            }}

            html, body, [class*="css"] {{
                font-family: 'Inter', system-ui, sans-serif;
            }}

            .main .block-container {{
                padding-top: 1.5rem;
                padding-bottom: 3.5rem;
                max-width: 1080px;
            }}

            /* ── Sidebar gradient tối ── */
            section[data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #0B1F3A 0%, #122B4D 100%);
                border-right: none;
            }}
            section[data-testid="stSidebar"] .stButton {{
                margin-bottom: 0.5rem !important;
            }}
            section[data-testid="stSidebar"] .stButton > button {{
                width: 100% !important;
                border-radius: 12px !important;
                padding: 0.85rem 1.1rem !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                min-height: 46px !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                background: rgba(255,255,255,0.07) !important;
                color: #F1F5F9 !important;
                transition: all 0.2s ease !important;
            }}
            section[data-testid="stSidebar"] .stButton > button:hover {{
                background: rgba(37,99,235,0.22) !important;
                border-color: rgba(96,165,250,0.5) !important;
                transform: translateY(-1px);
            }}
            section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
                background: linear-gradient(135deg, {PRIMARY}, {PRIMARY_DARK}) !important;
                border: none !important;
                color: #FFFFFF !important;
                box-shadow: 0 4px 16px rgba(37,99,235,0.45) !important;
            }}
            section[data-testid="stSidebar"] hr {{
                border-color: rgba(255,255,255,0.12) !important;
                margin: 1.25rem 0 !important;
            }}

            .sidebar-logo {{
                display: flex;
                align-items: center;
                gap: 0.9rem;
            }}
            .sidebar-logo-mark {{
                width: 44px;
                height: 44px;
                background: linear-gradient(135deg, #3B82F6, {PRIMARY_DARK});
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.3rem;
                box-shadow: 0 4px 14px rgba(59,130,246,0.4);
            }}
            .sidebar-brand {{
                font-size: 1.3rem;
                font-weight: 800;
                color: #FFFFFF !important;
                line-height: 1.25;
                letter-spacing: -0.02em;
            }}
            .sidebar-tagline {{
                font-size: 0.72rem;
                color: #94A3B8 !important;
                margin-top: 0.15rem;
                line-height: 1.4;
            }}
            .sidebar-user {{
                background: rgba(37,99,235,0.14);
                border: 1px solid rgba(96,165,250,0.22);
                border-radius: 12px;
                padding: 0.9rem 1rem;
                margin: 0.6rem 0 1rem 0;
            }}
            .sidebar-footer {{
                background: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
                padding: 1rem;
                margin-top: 1.5rem;
            }}
            .sidebar-footer p {{
                margin: 0.2rem 0 !important;
                font-size: 0.78rem !important;
                color: #94A3B8 !important;
            }}
            .sidebar-footer strong {{ color: #CBD5E1 !important; }}

            /* ── Hero banner (chưa đăng nhập) ── */
            .hero-banner {{
                background: linear-gradient(135deg, #0F2D5C 0%, {PRIMARY_DARK} 50%, #3B82F6 100%);
                color: #FFFFFF;
                padding: 2.5rem 2.75rem;
                border-radius: 20px;
                margin-bottom: 2rem;
                box-shadow: 0 14px 42px rgba(29,78,216,0.22);
            }}
            .hero-banner h1 {{
                margin: 0 0 0.75rem 0;
                font-size: 2.3rem;
                font-weight: 800;
                letter-spacing: -0.03em;
            }}
            .hero-banner p {{
                margin: 0;
                font-size: 1.05rem;
                line-height: 1.75;
                opacity: 0.93;
            }}
            .security-badges {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-top: 1.25rem;
            }}
            .security-badge {{
                background: rgba(255,255,255,0.13);
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 999px;
                padding: 0.4rem 0.95rem;
                font-size: 0.8rem;
                font-weight: 600;
            }}

            /* ── Header từng trang ── */
            .page-hero {{
                background: linear-gradient(135deg, #0F2D5C 0%, #1E40AF 100%);
                color: #FFFFFF;
                padding: 2.25rem 2.75rem;
                border-radius: 20px;
                margin-bottom: 1.75rem;
                box-shadow: 0 10px 32px rgba(15,45,92,0.18);
            }}
            .page-hero-title {{
                margin: 0;
                font-size: 1rem;
                font-weight: 800;
                letter-spacing: -0.03em;
                line-height: 1.2;
            }}
            .page-hero-sub {{
                margin: 0.75rem 0 0 0;
                font-size: 1rem;
                line-height: 1.65;
                color: rgba(255,255,255,0.85);
            }}

            /* ── Form card ── */
            [data-testid="stForm"] {{
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 20px;
                padding: 2.5rem 3rem 2rem 3rem !important;
                box-shadow: 0 6px 28px rgba(15,23,42,0.07);
            }}

            /* Ẩn dòng "Press Enter to submit form" */
            [data-testid="stForm"] [data-testid="stNotificationContentInfo"],
            [data-testid="stForm"] [data-testid="InputInstructions"],
            [data-testid="stForm"] [data-baseweb="form-control-caption"] {{
                display: none !important;
            }}

            /* Cột form — gap rộng */
            [data-testid="stForm"] [data-testid="stHorizontalBlock"] {{
                gap: 1.75rem !important;
            }}
            [data-testid="stForm"] [data-testid="column"] {{
                min-width: 0 !important;
            }}

            /* Label & input */
            [data-testid="stForm"] label[data-testid="stWidgetLabel"] p,
            .field-label {{
                font-size: 0.95rem !important;
                font-weight: 600 !important;
                color: #334155 !important;
                margin-bottom: 0.45rem !important;
            }}

            [data-testid="stForm"] .stTextInput,
            [data-testid="stForm"] div[data-baseweb="input"] {{
                width: 100% !important;
            }}
            /* Target cả text input lẫn password input (DOM khác nhau) */
            [data-testid="stForm"] div[data-baseweb="input"] {{
                border-radius: 12px !important;
                border: 1.5px solid #CBD5E1 !important;
                background: #FAFBFC !important;
                min-height: 54px !important;
                box-sizing: border-box !important;
                transition: border-color 0.2s, box-shadow 0.2s !important;
            }}
            [data-testid="stForm"] div[data-baseweb="input"]:focus-within {{
                border-color: {PRIMARY} !important;
                background: #FFFFFF !important;
                box-shadow: 0 0 0 4px rgba(37,99,235,0.15) !important;
            }}
            [data-testid="stForm"] div[data-baseweb="input"] input {{
                width: 100% !important;
                background: transparent !important;
                border: none !important;
                padding: 1rem 1.15rem !important;
                font-size: 1.05rem !important;
                box-sizing: border-box !important;
                outline: none !important;
            }}
            .main div[data-baseweb="input"] {{
                border-radius: 12px !important;
            }}
            [data-testid="stForm"] .stTextInput {{
                margin-bottom: 1rem !important;
            }}

            [data-testid="stForm"] .stCheckbox label span {{
                font-size: 0.88rem !important;
                font-weight: 500 !important;
                white-space: nowrap !important;
            }}

            /* Nút submit chính */
            [data-testid="stForm"] .stButton > button[kind="primary"],
            .main div.stButton > button[kind="primary"] {{
                background: linear-gradient(135deg, {PRIMARY_DARK}, {PRIMARY_DEEP}) !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 1rem 1.5rem !important;
                font-weight: 700 !important;
                font-size: 1.08rem !important;
                min-height: 56px !important;
                box-shadow: 0 6px 22px rgba(29,78,216,0.35) !important;
                transition: all 0.2s ease !important;
            }}
            [data-testid="stForm"] .stButton > button[kind="primary"]:hover {{
                background: linear-gradient(135deg, #1E40AF, #172554) !important;
                box-shadow: 0 8px 26px rgba(29,78,216,0.45) !important;
                transform: translateY(-1px);
            }}

            .section-heading {{
                font-size: 0.95rem;
                font-weight: 700;
                color: #1E293B;
                margin: 1.25rem 0 0.75rem 0;
            }}

            /* Profile */
            .profile-field {{
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 1rem 1.25rem;
                margin-bottom: 0.75rem;
            }}
            .profile-field-label {{
                font-size: 0.78rem;
                font-weight: 600;
                color: #64748B;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 0.25rem;
            }}
            .profile-field-value {{
                font-size: 1rem;
                font-weight: 600;
                color: #0F172A;
            }}

            div[data-testid="stMetric"] {{
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
                padding: 1rem 1.25rem;
            }}

            /* Panel kiểm tra mật khẩu */
            [data-testid="stVerticalBlockBorderWrapper"] {{
                border-radius: 20px !important;
                padding: 2rem 2.5rem !important;
                box-shadow: 0 6px 28px rgba(15,23,42,0.06) !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Component UI dùng chung
# ---------------------------------------------------------------------------
def _render_hero() -> None:
    """Banner giới thiệu — chỉ hiện khi chưa đăng nhập."""
    if _is_logged_in():
        return
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>{APP_NAME} - {APP_SUBTITLE}</h1>
            <p>{HERO_INTRO}</p>
            <div class="security-badges">
                <span class="security-badge">Argon2id + Salt</span>
                <span class="security-badge">AES-256-GCM</span>
                <span class="security-badge">Chống Rainbow Table</span>
                <span class="security-badge">Lockout 5 lần / 3 phút</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _page_header(title: str, subtitle: str = "") -> None:
    """Header gradient cho mỗi trang — không dùng st.title (tránh thanh trắng thừa)."""
    sub_html = f'<p class="page-hero-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="page-hero">
            <h1 class="page-hero-title">{title}</h1>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _profile_field(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="profile-field">
            <div class="profile-field-label">{label}</div>
            <div class="profile-field-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _show_strength_badge(password: str) -> None:
    """Hiển thị badge độ mạnh mật khẩu."""
    strength = check_password_strength(password)
    if strength == "Yếu":
        st.error(f"Độ mạnh: **{strength}**")
        st.caption(get_password_requirements_message())
    elif strength == "Trung bình":
        st.warning(f"Độ mạnh: **{strength}** — Nên dùng ít nhất 12 ký tự để đạt mức Mạnh.")
    else:
        st.success(f"Độ mạnh: **{strength}**")


# ---------------------------------------------------------------------------
# Session & database
# ---------------------------------------------------------------------------
def _init_session_state() -> None:
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "db_ready" not in st.session_state:
        st.session_state.db_ready = False


@st.cache_resource
def _setup_database() -> bool:
    init_db()
    return True


def _is_logged_in() -> bool:
    return st.session_state.user is not None


def _logout() -> None:
    user = st.session_state.user
    if user:
        log_activity(user["id"], ACTION_LOGOUT, "Người dùng đăng xuất (Streamlit)")
    st.session_state.user = None
    st.session_state.page = "login"


def _nav_to(page_key: str) -> None:
    st.session_state.page = page_key
    st.rerun()


# ---------------------------------------------------------------------------
# Các trang — logic giữ nguyên
# ---------------------------------------------------------------------------
def page_register() -> None:
    _page_header(
        "Đăng ký tài khoản mới",
        "Tạo tài khoản an toàn với Argon2id và mã hóa AES-256-GCM.",
    )

    with st.form("register_form", clear_on_submit=False):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            username = st.text_input("Username *", placeholder="6–20 ký tự, chữ/số/._-")
            full_name = st.text_input("Họ và tên *", placeholder="Nguyễn Văn A")
        with col2:
            email = st.text_input("Email *", placeholder="name@example.com")
            phone = st.text_input("Số điện thoại", placeholder="10 chữ số (tùy chọn)")

        col3, col4 = st.columns(2, gap="large")
        with col3:
            identify_card = st.text_input("Số CMND/CCCD", placeholder="12 chữ số (tùy chọn)")
        with col4:
            address = st.text_input("Địa chỉ", placeholder="Tùy chọn")

        col5, col6 = st.columns(2, gap="large")
        with col5:
            password = password_input("Mật khẩu *", key="reg_password")
            if password:
                _show_strength_badge(password)
        with col6:
            confirm_password = password_input("Xác nhận mật khẩu *", key="reg_confirm")

        submitted = st.form_submit_button(
            "Đăng ký tài khoản",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not username.strip() or not full_name.strip() or not email.strip():
            st.error("Username, Họ tên và Email không được để trống.")
            return
        success, message, _ = register_user(
            username=username.strip(),
            full_name=full_name.strip(),
            email=email.strip(),
            password=password,
            confirm_password=confirm_password,
            phone=phone.strip() or None,
            identify_card=identify_card.strip() or None,
            address=address.strip() or None,
        )
        if success:
            st.success(message)
            st.info("Bạn có thể đăng nhập ngay từ menu bên trái.")
        else:
            st.error(message)


def page_login() -> None:
    _page_header(
        "Đăng nhập",
        "Nhập sai mật khẩu 5 lần liên tiếp sẽ bị khóa tài khoản trong 3 phút.",
    )

    with st.form("login_form"):
        identifier = st.text_input(
            "Username hoặc Email *",
            placeholder="Nhập username hoặc email",
        )
        password = password_input("Mật khẩu *", key="login_password")
        submitted = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)

    if submitted:
        if not identifier.strip():
            st.error("Vui lòng nhập Username hoặc Email.")
            return
        success, message, user = login_user(identifier.strip(), password)
        if not success:
            st.error(message)
            return

        st.session_state.user = user
        username = user.get("username", "")
        st.success(f"Đăng nhập thành công. Chào mừng **{username}**.")

        col1, col2, col3 = st.columns(3, gap="large")
        col1.metric("Username", username)
        col2.metric("Email", user.get("email") or "—")
        col3.metric("Họ tên", user.get("full_name") or "—")

        strength = check_password_strength(password)
        st.markdown('<p class="section-heading">Kiểm tra bảo mật mật khẩu</p>', unsafe_allow_html=True)
        if strength == "Yếu":
            st.warning("Mật khẩu quá yếu. Nên đổi mật khẩu mới đáp ứng yêu cầu tối thiểu.")
        elif strength == "Trung bình":
            st.warning("Mật khẩu ở mức trung bình. Nên dùng ít nhất 12 ký tự để đạt mức Mạnh.")
        else:
            st.success("Mật khẩu của bạn đang ở mức tốt.")

        st.session_state.page = "view_profile"
        st.rerun()


def page_check_password() -> None:
    """Kiểm tra độ mạnh — luôn plaintext."""
    _page_header(
        "Kiểm tra độ mạnh mật khẩu",
        "Phân tích mật khẩu theo thời gian thực — hiển thị rõ để minh họa.",
    )

    with st.form("check_password_form"):
        password = st.text_input(
            "Mật khẩu cần kiểm tra",
            placeholder="Nhập mật khẩu để phân tích...",
        )
        st.form_submit_button("Kiểm tra", type="primary", use_container_width=True)

    if password:
        strength = check_password_strength(password)
        if strength == "Yếu":
            st.error(f"Kết quả: **{strength}**")
            st.info(get_password_requirements_message())
        elif strength == "Trung bình":
            st.warning(f"Kết quả: **{strength}**")
            st.info("Đủ yêu cầu nhưng ngắn (8–11 ký tự). Nên dùng ít nhất 12 ký tự để đạt mức Mạnh.")
        else:
            st.success(f"Kết quả: **{strength}** — Mật khẩu tốt!")

    st.markdown('<p style="font-weight:600;margin:1.5rem 0 0.5rem 0;">Bảng tham khảo độ mạnh mật khẩu</p>', unsafe_allow_html=True)
    _img_path = Path(__file__).parent / "z7946335441668_1cb9bd6eda547b2aeffeb55468332bc4.jpg"
    if _img_path.exists():
        st.image(str(_img_path), use_container_width=True)


def page_view_profile() -> None:
    user_id = st.session_state.user["id"]
    profile = get_user_profile(user_id)

    _page_header("Thông tin cá nhân", "Dữ liệu nhạy cảm được giải mã an toàn từ cơ sở dữ liệu.")

    if not profile:
        st.error("Không tìm thấy thông tin.")
        return

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<p class="section-heading">Liên hệ</p>', unsafe_allow_html=True)
        _profile_field("Họ và tên", profile.get("full_name") or "Chưa cập nhật")
        _profile_field("Email", profile.get("email") or "Chưa cập nhật")
        _profile_field("Số điện thoại", profile.get("phone") or "Chưa cập nhật")
    with col2:
        st.markdown('<p class="section-heading">Định danh</p>', unsafe_allow_html=True)
        _profile_field("CMND/CCCD", profile.get("identify_card") or "Chưa cập nhật")
        _profile_field("Địa chỉ", profile.get("address") or "Chưa cập nhật")
        _profile_field("Username", profile.get("username", ""))


def page_update_profile() -> None:
    user_id = st.session_state.user["id"]
    current = get_user_profile(user_id)

    _page_header("Cập nhật thông tin", "Để giữ nguyên giá trị cũ, hãy để trống trường tương ứng.")

    if not current:
        st.error("Không tìm thấy tài khoản.")
        return

    with st.form("update_profile_form"):
        st.info(
            f"Họ tên hiện tại: **{current.get('full_name') or '(chưa có)'}** · "
            f"Email: **{current.get('email') or '(chưa có)'}**"
        )
        col1, col2 = st.columns(2, gap="large")
        with col1:
            full_name = st.text_input("Họ và tên mới")
            email = st.text_input("Email mới")
            phone = st.text_input("Số điện thoại mới (10 số)")
        with col2:
            identify_card = st.text_input("Số CMND/CCCD mới (12 số)")
            address = st.text_input("Địa chỉ mới")

        submitted = st.form_submit_button("Lưu thay đổi", type="primary", use_container_width=True)

    if submitted:
        success, message = update_user_profile(
            user_id,
            full_name=full_name.strip() or None,
            email=email.strip() or None,
            phone=phone.strip() or None,
            identify_card=identify_card.strip() or None,
            address=address.strip() or None,
        )
        if success:
            st.success(message)
            refreshed = get_user_profile(user_id)
            if refreshed:
                st.session_state.user = refreshed
        else:
            st.error(message)


def page_change_password() -> None:
    user_id = st.session_state.user["id"]

    _page_header(
        "Đổi mật khẩu",
        "Mật khẩu mới được hash lại bằng Argon2id sau khi xác thực mật khẩu cũ.",
    )

    with st.form("change_password_form"):
        old_pw = password_input("Mật khẩu cũ *", key="chg_old")
        new_pw = password_input("Mật khẩu mới *", key="chg_new")
        if new_pw:
            if not meets_password_requirements(new_pw):
                st.error(get_password_requirements_message())
            else:
                st.caption(f"Độ mạnh: **{get_password_strength(new_pw)}**")
        confirm_pw = password_input("Xác nhận mật khẩu mới *", key="chg_confirm")
        submitted = st.form_submit_button("Đổi mật khẩu", type="primary", use_container_width=True)

    if submitted:
        success, message = change_user_password(user_id, old_pw, new_pw, confirm_pw)
        if success:
            st.success(message)
        else:
            st.error(message)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def _sidebar_nav_button(label: str, page_key: str, is_active: bool) -> None:
    if st.sidebar.button(
        label,
        key=f"nav_{page_key}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
        if page_key == "logout":
            _logout()
            st.rerun()
        else:
            _nav_to(page_key)


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-logo">
                <div class="sidebar-logo-mark">🔒</div>
                <div>
                    <div class="sidebar-brand">{APP_NAME}</div>
                    <div class="sidebar-tagline">{APP_SUBTITLE}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        current = st.session_state.page

        if _is_logged_in():
            user = st.session_state.user
            st.markdown(
                f"""
                <div class="sidebar-user">
                    <div style="font-size:0.78rem;color:#94A3B8!important;">Đang đăng nhập</div>
                    <div style="font-size:1rem;font-weight:700;color:#FFFFFF!important;">
                        {user.get('username', '')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for label, page_key in AUTH_PAGES.items():
                if page_key == "logout":
                    st.markdown("---")
                _sidebar_nav_button(label, page_key, current == page_key)
        else:
            for label, page_key in PUBLIC_PAGES.items():
                _sidebar_nav_button(label, page_key, current == page_key)

        st.markdown(
            """
            <div class="sidebar-footer">
                <p><strong>Bảo mật</strong></p>
                <p>Argon2id</p>
                <p>AES-256-GCM</p>
                <p>Lockout: 5 lần / 3 phút</p>
            </div>
            """,
            unsafe_allow_html=True,
        )



def _render_page() -> None:
    page = st.session_state.page
    auth_only = {"view_profile", "update_profile", "change_password"}
    if page in auth_only and not _is_logged_in():
        st.warning("Vui lòng đăng nhập trước.")
        st.session_state.page = "login"
        page = "login"

    routes = {
        "register": page_register,
        "login": page_login,
        "check_password": page_check_password,
        "view_profile": page_view_profile,
        "update_profile": page_update_profile,
        "change_password": page_change_password,
    }
    routes.get(page, page_login)()


def main() -> None:
    _init_session_state()
    _inject_custom_css()

    try:
        if not st.session_state.db_ready:
            with st.spinner("Đang khởi tạo cơ sở dữ liệu..."):
                _setup_database()
            st.session_state.db_ready = True
    except Exception as e:
        st.error(f"Lỗi kết nối CSDL: {e}")
        st.info("Kiểm tra file `.env` và đảm bảo MySQL đang chạy.")
        st.stop()

    _render_sidebar()
    _render_hero()
    _render_page()


if __name__ == "__main__":
    main()