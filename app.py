"""Professional application shell for the UBE Safety Talk workshop."""

import json
from datetime import date
from pathlib import Path

import streamlit as st

from src.approval import Action, ApprovalService, Status
from src.ownership import read_owners
from src.permissions import DEMO_USERS, Permission, has_permission, require_permission
from src.services import OwnerRegistrationError, submit_report
from src.storage import CSV_COLUMNS, REPORTS_PATH, SAMPLE_PATH, read_reports, validate_attachments
from src.validation import validate_report


st.set_page_config(
    page_title="UBE Safety Talk",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if st.get_option("server.address") not in ("127.0.0.1", "localhost", "::1"):
    st.error("Demo ใช้ได้เฉพาะ localhost: ตั้งค่า server.address เป็น 127.0.0.1 แล้วเริ่มแอปใหม่")
    st.stop()

st.markdown(
    """
    <style>
        :root {
            --enterprise-navy: #123B35;
            --enterprise-teal: #0F735C;
            --enterprise-background: #E8EDE9;
            --enterprise-border: #D2DED7;
            --enterprise-muted: #536D61;
        }

        .stApp {
            background: var(--enterprise-background);
            color: var(--enterprise-navy);
            font-family: "Segoe UI", Tahoma, sans-serif;
        }

        [data-testid="stHeader"] {
            background: var(--enterprise-background);
        }

        .block-container {
            max-width: 1280px;
            padding: 2rem 2.5rem 3.5rem;
        }

        section[data-testid="stSidebar"] {
            background: #0F735C;
            border-right: 1px solid var(--enterprise-border);
            border-top: 5px solid transparent;
            border-image: linear-gradient(to right, #F97A1B 0 33.33%, #C91E2A 33.33% 66.66%, #159978 66.66% 100%) 1;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.4rem;
        }

        section[data-testid="stSidebar"] hr {
            border-color: #60AA90;
            margin: 1.2rem 0;
        }

        section[data-testid="stSidebar"] [data-testid="stSelectbox"] label p,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: #FFFFFF;
        }

        section[data-testid="stSidebar"] [data-testid="stExpander"] {
            background: #F2F5F2;
            border: 1px solid var(--enterprise-border);
            border-radius: 10px;
            overflow: hidden;
        }

        section[data-testid="stSidebar"] [data-testid="stExpander"] summary,
        section[data-testid="stSidebar"] [data-testid="stExpander"] summary p {
            color: var(--enterprise-navy);
            font-weight: 600;
        }

        section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
            padding: 0.75rem 0.9rem;
        }

        section[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover,
        section[data-testid="stSidebar"] [data-testid="stExpander"] details[open] > summary {
            background: #D9EBE2;
            box-shadow: inset 3px 0 0 #159978;
        }

        section[data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
            fill: var(--enterprise-teal);
            color: var(--enterprise-teal);
        }

        section[data-testid="stSidebar"] [data-testid="stExpander"] summary:focus-visible,
        .stButton button:focus-visible {
            outline: 2px solid var(--enterprise-teal);
            outline-offset: 2px;
        }

        section[data-testid="stSidebar"] [data-testid="stButton"] button {
            background: #F2F5F2;
            border: 1px solid var(--enterprise-border);
            border-radius: 8px;
            color: var(--enterprise-navy);
            font-weight: 600;
            justify-content: flex-start;
            padding: 0.75rem 1rem;
        }

        section[data-testid="stSidebar"] [data-testid="stButton"] button[data-testid="stBaseButton-primary"] {
            background: #F97A1B;
            border-color: #F97A1B;
            box-shadow: inset 4px 0 0 #C91E2A;
            color: #10221F;
        }

        .sidebar-menu-label {
            color: #FFFFFF;
            font-size: 0.8rem;
            font-weight: 700;
            margin: 1rem 0 0.25rem;
        }

        section[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
            background: #FFE0CB;
            border-color: #F97A1B;
            color: var(--enterprise-navy);
        }

        .brand-block {
            border-bottom: 1px solid #60AA90;
            margin-bottom: 0.4rem;
            padding: 0.2rem 0 1.25rem;
        }

        .brand-row {
            align-items: center;
            display: flex;
            gap: 0.8rem;
        }

        .brand-mark {
            align-items: center;
            background: #C91E2A;
            border-radius: 12px;
            box-shadow: inset 0 -4px 0 #F97A1B;
            color: #FFFFFF;
            display: flex;
            font-size: 0.75rem;
            font-weight: 700;
            height: 46px;
            justify-content: center;
            letter-spacing: 0.05em;
            width: 46px;
        }

        .brand-title {
            color: #FFFFFF;
            font-size: 1.02rem;
            font-weight: 700;
            line-height: 1.25;
        }

        .brand-subtitle {
            color: #FFFFFF;
            font-size: 0.7rem;
            letter-spacing: 0.04em;
            margin-top: 0.18rem;
            text-transform: uppercase;
        }

        .demo-banner {
            background: #C91E2A;
            border: 1px solid #C91E2A;
            border-left: 3px solid #F97A1B;
            border-radius: 8px;
            color: #FFFFFF;
            font-size: 0.75rem;
            font-weight: 700;
            line-height: 1.5;
            padding: 0.75rem 0.9rem;
        }

        .sidebar-note {
            background: #E8EDE9;
            border: 1px solid var(--enterprise-border);
            border-radius: 8px;
            color: var(--enterprise-muted);
            font-size: 0.75rem;
            line-height: 1.6;
            padding: 0.8rem 0.9rem;
        }

        .sidebar-note strong {
            color: var(--enterprise-navy);
            display: block;
            font-size: 0.78rem;
            margin-bottom: 0.15rem;
        }

        .system-header, .queue-hero, .page-panel {
            background: #F2F5F2;
            border: 1px solid var(--enterprise-border);
            border-radius: 14px;
            box-shadow: 0 6px 24px rgba(18, 59, 53, 0.05);
        }

        .system-header {
            background: #123B35;
            border-top: 4px solid var(--enterprise-teal);
        }

        .system-header .header-eyebrow {
            color: #8CCDB5;
        }

        .header-content {
            align-items: center;
            display: flex;
            gap: 1.5rem;
            justify-content: space-between;
            padding: 1.6rem 2rem;
        }

        .header-eyebrow, .queue-eyebrow, .content-label {
            color: var(--enterprise-teal);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .system-header h1 {
            color: #F2F5F2;
            font-size: clamp(1.9rem, 3vw, 2.5rem);
            font-weight: 700;
            line-height: 1.15;
            margin: 0.45rem 0 0;
        }

        .company-name {
            color: #C9DCD2;
            font-size: 0.92rem;
            margin: 0.55rem 0 0;
        }

        .environment-tag {
            background: #D9EBE2;
            border: 1px solid #B8DFD1;
            border-radius: 999px;
            color: #1A653E;
            flex: 0 0 auto;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            padding: 0.45rem 0.75rem;
            text-transform: uppercase;
        }

        .breadcrumb {
            color: var(--enterprise-muted);
            font-size: 0.8rem;
            margin: 1.2rem 0 0.5rem;
        }

        .breadcrumb strong {
            color: var(--enterprise-navy);
        }

        .queue-hero {
            border-left: 4px solid var(--enterprise-teal);
            margin-bottom: 1rem;
            padding: 1.25rem 1.5rem;
        }

        .queue-hero h2 {
            color: var(--enterprise-navy);
            font-size: 1.5rem;
            margin: 0.35rem 0;
        }

        .queue-description {
            color: var(--enterprise-muted);
            font-size: 0.9rem;
        }

        [data-testid="stMetric"] {
            background: #F2F5F2;
            border: 1px solid var(--enterprise-border);
            border-top: 3px solid #159978;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(18, 59, 53, 0.04);
            min-height: 140px;
            padding: 1.1rem 1.2rem;
        }

        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--enterprise-navy);
            font-weight: 700;
        }

        [data-testid="stForm"] {
            background: #F2F5F2;
            border: 1px solid var(--enterprise-border);
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
        }

        [data-testid="stDataFrame"] {
            background: #F2F5F2;
            border: 1px solid var(--enterprise-border);
            border-radius: 12px;
            padding: 0.7rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #F2F5F2;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(18, 59, 53, 0.04);
        }

        .stButton button, .stDownloadButton button {
            border-radius: 8px;
        }

        .page-heading, .content-area {
            padding: 1.4rem 1.6rem;
        }

        .page-heading {
            border-bottom: 1px solid var(--enterprise-border);
        }

        .page-heading h2, .module-item h3, .next-step strong {
            color: var(--enterprise-navy);
        }

        .page-state, .module-number {
            color: var(--enterprise-teal);
            font-size: 0.72rem;
            font-weight: 700;
        }

        .page-heading p, .module-item p, .next-step {
            color: var(--enterprise-muted);
            line-height: 1.65;
        }

        .module-grid {
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }

        .next-step {
            background: #E8EDE9;
            border-radius: 8px;
            margin-top: 1rem;
            padding: 0.9rem;
        }

        .page-footer {
            border-top: 1px solid var(--enterprise-border);
            color: var(--enterprise-muted);
            display: flex;
            font-size: 0.75rem;
            gap: 0.5rem;
            justify-content: space-between;
            margin-top: 2rem;
            padding-top: 1rem;
        }

        @media (max-width: 760px) {
            .block-container {
                padding: 1.1rem 1rem 2rem;
            }
            .header-content, .page-footer {
                align-items: flex-start;
                flex-direction: column;
            }
            .header-content {
                padding: 1.25rem;
            }
            .module-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_placeholder(
    title: str,
    description: str,
    next_step: str,
    modules: tuple[tuple[str, str], ...],
) -> None:
    """Render a formal placeholder for the selected workshop page."""
    module_items = "".join(
        f"""
        <article class="module-item">
            <span class="module-number">MODULE {index:02d}</span>
            <h3>{module_title}</h3>
            <p>{module_description}</p>
        </article>
        """
        for index, (module_title, module_description) in enumerate(modules, start=1)
    )
    st.markdown(
        f"""
        <section class="page-panel">
            <div class="page-heading">
                <div class="page-state">Workshop Placeholder</div>
                <h2>{title}</h2>
                <p>{description}</p>
            </div>
            <div class="content-area">
                <div class="content-label">องค์ประกอบของหน้านี้</div>
                <div class="module-grid">{module_items}</div>
                <div class="next-step">
                    <strong>ขั้นตอนถัดไป</strong>
                    <span>{next_step}</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def select_sidebar_menu(menu_name):
    st.session_state.selected_menu = menu_name


with st.sidebar:
    st.markdown(
        """
        <div class="brand-block">
            <div class="brand-row">
                <div class="brand-mark">UBE</div>
                <div>
                    <div class="brand-title">UBE Safety Talk</div>
                    <div class="brand-subtitle">Safety Management</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="demo-banner">DEMO MODE<br>NO AUTHENTICATION</div>',
        unsafe_allow_html=True,
    )
    demo_user = st.selectbox(
        "ผู้ใช้สมมติ (Demo)",
        tuple(DEMO_USERS),
        format_func=lambda user: f"{user} · {DEMO_USERS[user]}",
        key="demo_user",
    )
    st.caption(f"บทบาทสมมติ: {DEMO_USERS[demo_user]} · ไม่ใช่สิทธิ์จริง")
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = "บันทึก Safety Talk"

    menu_items = (
        ("บันทึก Safety Talk", "จัดทำรายงานกิจกรรม Safety Talk"),
        ("Dashboard", "ดูภาพรวมและกิจกรรมรายเดือน"),
        ("ประวัติรายงาน", "ค้นหาและตรวจสอบรายงานที่ผ่านมา"),
        ("ประวัติ SQLite (ทดลอง)", "ดูรายงานในฐานข้อมูลทดลองแบบอ่านอย่างเดียว"),
    )
    if has_permission(DEMO_USERS[demo_user], Permission.APPROVE_REPORT):
        menu_items += (("Approval Queue", "ดูรายงานที่รอตรวจสอบ"),)
    st.markdown('<div class="sidebar-menu-label">เมนูหลัก</div>', unsafe_allow_html=True)
    for menu_name, _ in menu_items:
        st.button(
            menu_name,
            key=menu_name,
            type="primary" if st.session_state.selected_menu == menu_name else "secondary",
            on_click=select_sidebar_menu,
            args=(menu_name,),
            use_container_width=True,
        )

    selected_menu = st.session_state.selected_menu
    st.divider()
    st.markdown(
        """
        <div class="sidebar-note">
            <strong>Workshop Environment</strong>
            ระบบสาธิตภายในเครื่องสำหรับการอบรม Day 1
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <header class="system-header">
        <div class="header-content">
            <div>
                <div class="header-eyebrow">Safety Communication Management</div>
                <h1>UBE Safety Talk</h1>
                <p class="company-name">บริษัท อุบล ไบโอ เอทานอล จำกัด (มหาชน)</p>
            </div>
            <span class="environment-tag">Local Demonstration</span>
        </div>
    </header>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="breadcrumb">หน้าหลัก &nbsp;/&nbsp; <strong>{selected_menu}</strong></div>',
    unsafe_allow_html=True,
)

if selected_menu == "บันทึก Safety Talk":
    try:
        require_permission(DEMO_USERS[demo_user], Permission.CREATE_REPORT)
    except PermissionError as exc:
        st.error(str(exc))
        st.stop()
    st.subheader("บันทึก Safety Talk")
    st.caption("กรอกข้อมูลกิจกรรม Safety Talk โดยใช้ข้อมูลสำหรับสาธิตเท่านั้น")
    st.warning("ใช้ข้อมูลทดสอบเท่านั้น ห้ามอัปโหลดข้อมูลส่วนบุคคลจริงหรือเอกสารลับ")
    departments_path = Path(__file__).resolve().parent / "config" / "departments.json"
    with departments_path.open(encoding="utf-8") as departments_file:
        departments = json.load(departments_file)

    company = st.selectbox("บริษัท", ("UBE", "UBS"), key="talk_company")
    with st.form("safety_talk_form"):
        left_col, right_col = st.columns(2)
        with left_col:
            talk_date = st.date_input("วันที่สื่อสาร", value=None)
            department = st.selectbox(
                "หน่วยงาน",
                departments[company],
                key=f"talk_department_{company}",
                index=None,
                placeholder="เลือกหน่วยงาน",
            )
            reporter = st.text_input("ชื่อผู้รายงาน")
        with right_col:
            topic = st.text_input("หัวข้อ Safety Talk")
            participants = st.number_input(
                "จำนวนผู้เข้าร่วม (คน)", min_value=1, value=1, step=1
            )
        notes = st.text_area(
            "หมายเหตุรายละเอียด (ไม่บังคับ · ส่วนขยายจากโจทย์)",
            help="ช่องนี้เป็นส่วนขยายจากข้อกำหนดต้นฉบับ และยังไม่มีการบันทึกข้อมูล",
        )
        files = st.file_uploader(
            "หลักฐานประกอบ (ไม่บังคับ)",
            type=["jpg", "jpeg", "png", "pdf"],
            accept_multiple_files=True,
            help="ไฟล์แต่ละไฟล์ต้องมีขนาดน้อยกว่า 5 MB",
        )
        submitted = st.form_submit_button("บันทึกรายงาน")

    if submitted:
        report = {
            "talk_date": talk_date,
            "company": company,
            "department": department,
            "reporter": reporter,
            "topic": topic,
            "participants": participants,
        }
        errors = validate_report(report, departments) + validate_attachments(files)
        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                report_id = submit_report(DEMO_USERS[demo_user], report, files, departments, demo_user)
            except OwnerRegistrationError as exc:
                st.warning(f"{exc} รายงานนี้ยังส่งอนุมัติไม่ได้ กรุณาตรวจสอบข้อมูลเจ้าของก่อนสร้างซ้ำ")
            except PermissionError as exc:
                st.error(str(exc))
            except (OSError, ValueError) as exc:
                st.error(f"ไม่สามารถบันทึกรายงานได้: {exc}")
            else:
                st.success(f"บันทึกรายงานเรียบร้อย รหัสรายงาน: {report_id}")
                if notes.strip():
                    st.info("หมายเหตุเป็นส่วนขยายและยังไม่ได้บันทึกลง CSV")
elif selected_menu == "Dashboard":
    from src.dashboard import render_dashboard

    try:
        render_dashboard(REPORTS_PATH, DEMO_USERS[demo_user])
    except PermissionError as exc:
        st.error(str(exc))
elif selected_menu == "Approval Queue":
    from src.approval_queue import render_approval_queue

    render_approval_queue(DEMO_USERS[demo_user], REPORTS_PATH, demo_user)
elif selected_menu == "ประวัติ SQLite (ทดลอง)":
    from src.sqlite_history import SQLITE_PREVIEW_PATH
    from src.sqlite_history_page import render_sqlite_history

    render_sqlite_history(SQLITE_PREVIEW_PATH, demo_user)
else:
    import pandas as pd

    st.subheader("ประวัติรายงาน")
    st.caption("ค้นหาและตรวจสอบรายงาน Safety Talk ที่บันทึกในเครื่อง")
    try:
        history = pd.DataFrame(read_reports(REPORTS_PATH), columns=CSV_COLUMNS)
        if history.empty:
            st.info("ยังไม่มีรายงานที่บันทึก กรุณาเพิ่มรายงานจากหน้าบันทึก Safety Talk")
        else:
            search_col, company_col = st.columns([2, 1])
            with search_col:
                search = st.text_input("ค้นหารหัสรายงาน หัวข้อ หรือผู้รายงาน")
            with company_col:
                company_filter = st.selectbox("บริษัท", ("ทั้งหมด", "UBE", "UBS"), key="history_company")

            filtered = history
            if company_filter != "ทั้งหมด":
                filtered = filtered[filtered["company"] == company_filter]
            if search.strip():
                matches = filtered[["report_id", "topic", "reporter"]].fillna("").apply(
                    lambda column: column.str.contains(search.strip(), case=False, regex=False)
                ).any(axis=1)
                filtered = filtered[matches]

            if filtered.empty:
                st.info("ไม่พบรายงานที่ตรงกับเงื่อนไขการค้นหา")
            st.dataframe(filtered, hide_index=True, use_container_width=True)
            st.download_button(
                "ดาวน์โหลด CSV",
                data=filtered.to_csv(index=False, columns=CSV_COLUMNS).encode("utf-8-sig"),
                file_name=f"SafetyTalk_{date.today():%Y%m%d}.csv",
                mime="text/csv; charset=utf-8",
            )
            st.markdown("#### ส่งขออนุมัติ (Demo)")
            if has_permission(DEMO_USERS[demo_user], Permission.SUBMIT_REPORT):
                owners = read_owners()
                approval = ApprovalService(reports_path=REPORTS_PATH)
                available = [
                    report_id for report_id in filtered["report_id"].tolist()
                    if owners.get(report_id) == demo_user and approval.get_status(report_id) == Status.DRAFT
                ]
                if available:
                    selected_report = st.selectbox(
                        "เลือกรายงาน Draft ที่คุณเป็นเจ้าของ",
                        available,
                        index=None,
                        placeholder="เลือก Report ID",
                        key="approval_report_id",
                    )
                    if st.button("ส่งขออนุมัติ", disabled=selected_report is None):
                        try:
                            approval.transition(selected_report, Action.SUBMIT, demo_user, DEMO_USERS[demo_user])
                        except (PermissionError, ValueError, OSError) as exc:
                            st.error(f"ส่งขออนุมัติไม่สำเร็จ: {exc}")
                        else:
                            st.success(f"ส่งขออนุมัติรายงาน {selected_report} แล้ว (Pending)")
                else:
                    st.caption("ไม่มีรายงาน Draft ที่คุณเป็นเจ้าของในผลการค้นหา รายงานเดิมที่ไม่มีข้อมูลเจ้าของไม่สามารถส่งได้")
    except (OSError, ValueError) as exc:
        st.error(f"ไม่สามารถอ่านประวัติรายงานได้: {exc}")

st.markdown(
    """
    <footer class="page-footer">
        <span>UBE Safety Talk · Workshop Day 1</span>
        <span>Local demonstration only</span>
    </footer>
    """,
    unsafe_allow_html=True,
)
