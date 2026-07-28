"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Đề bài 9: Trợ Lý Sàng Lọc Hồ Sơ Tuyển Dụng & Hẹn Phỏng Vấn

NGUYÊN TẮC THIẾT KẾ (bắt buộc tuân thủ):
1. Input / Output đồng nhất giữa mọi tool:
   - Input: mỗi tham số đều là str, KHÔNG có giá trị mặc định ngầm.
   - Output: luôn là 1 chuỗi JSON (str) theo đúng envelope:
       {
         "status": "success" | "error",
         "data": {...} | null,
         "error": {"code": "...", "message": "..."} | null
       }
2. KHÔNG BAO GIỜ throw exception ra ngoài — mọi lỗi (thiếu field, sai định
   dạng, sai kiểu, không tồn tại dữ liệu...) đều được validate tường minh
   và trả về trong "error", không im lặng bỏ qua / không tự suy diễn giá
   trị mặc định thay cho field bắt buộc.
3. Tool KHÔNG gọi LLM, KHÔNG tự suy luận ngữ nghĩa (matching kỹ năng,
   đánh giá phù hợp...) — việc đó thuộc về Agent (Role 1), dựa trên dữ
   liệu thô mà tool trả về. Tool chỉ tra cứu / validate / ghi dữ liệu.
4. Mỗi tool chỉ làm đúng MỘT việc, không tool nào lấn sang việc của
   tool khác (VD: schedule_interview không tự ý so khớp kỹ năng ứng
   viên với JD — đó là việc của check_job_requirements + Agent).
"""

import json
import re
from datetime import datetime


# ============================================================
# 📦 MOCK DATABASE (giả lập dữ liệu ứng viên & yêu cầu vị trí)
# ============================================================

CANDIDATE_DB = {
    "CV-1042": {
        "candidate_id": "CV-1042",
        "name": "Nguyễn Văn A",
        "position_applied": "Backend Developer",
        "skills": ["Python", "SQL", "Django", "Git"],
        "experience_years": 3,
        "education": "Cử nhân Khoa học Máy tính",
    },
    "CV-2078": {
        "candidate_id": "CV-2078",
        "name": "Trần Thị B",
        "position_applied": "Data Analyst",
        "skills": ["SQL", "Excel", "Power BI", "Python"],
        "experience_years": 2,
        "education": "Cử nhân Thống kê",
    },
}

JOB_REQUIREMENTS_DB = {
    "Backend Developer": {
        "job_title": "Backend Developer",
        "required_skills": ["Python", "SQL", "Django"],
        "min_experience_years": 2,
    },
    "Data Analyst": {
        "job_title": "Data Analyst",
        "required_skills": ["SQL", "Excel", "Power BI"],
        "min_experience_years": 1,
    },
    "Frontend Developer": {
        "job_title": "Frontend Developer",
        "required_skills": ["JavaScript", "React", "CSS"],
        "min_experience_years": 1,
    },
}

# Lưu vết các lịch phỏng vấn đã đặt thành công (giả lập persistence)
SCHEDULED_INTERVIEWS = []

CANDIDATE_ID_PATTERN = re.compile(r"^CV-\d+$", re.IGNORECASE)
DATETIME_PATTERN = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})$")

WORK_HOUR_START = 7   # 07:00
WORK_HOUR_END = 20    # 20:00 (không tính mốc 20:00)


# ============================================================
# 🧱 HELPER: chuẩn hóa envelope input/output — dùng nội bộ,
# KHÔNG đăng ký vào AVAILABLE_TOOLS.
# ============================================================

def _success(data: dict) -> str:
    return json.dumps({"status": "success", "data": data, "error": None}, ensure_ascii=False)


def _error(code: str, message: str) -> str:
    return json.dumps(
        {"status": "error", "data": None, "error": {"code": code, "message": message}},
        ensure_ascii=False,
    )


def _validate_required_str(value, field_name: str):
    """
    Validate một field bắt buộc kiểu str: phải tồn tại, đúng kiểu str,
    và không rỗng sau khi strip. Trả về (True, cleaned_value) nếu hợp lệ,
    ngược lại trả về (False, error_json_string).
    """
    if value is None:
        return False, _error("MISSING_FIELD", f"Thiếu tham số bắt buộc: '{field_name}'.")
    if not isinstance(value, str):
        return False, _error(
            "INVALID_TYPE", f"Tham số '{field_name}' phải là kiểu chuỗi (str)."
        )
    cleaned = value.strip()
    if cleaned == "":
        return False, _error(
            "MISSING_FIELD", f"Tham số '{field_name}' không được để trống."
        )
    return True, cleaned


# ============================================================
# 🔧 TOOL 1: Tra cứu hồ sơ ứng viên
# ============================================================

def get_candidate_profile(candidate_id: str) -> str:
    """
    Tra cứu hồ sơ ứng viên theo mã CV trong hệ thống. Chỉ đọc dữ liệu,
    không đánh giá / không so khớp với vị trí tuyển dụng.

    Args:
        candidate_id (str): Mã hồ sơ ứng viên, định dạng 'CV-<số>'
            (Ví dụ: 'CV-1042'). Bắt buộc, không được rỗng.

    Returns:
        str: Chuỗi JSON theo envelope {status, data, error}.
            - success -> data chứa: candidate_id, name, position_applied,
              skills (list), experience_years (int), education.
            - error   -> error.code thuộc:
              MISSING_FIELD | INVALID_TYPE | INVALID_FORMAT | NOT_FOUND.
        Hàm KHÔNG BAO GIỜ raise exception; mọi lỗi được trả trong "error".
    """
    ok, result = _validate_required_str(candidate_id, "candidate_id")
    if not ok:
        return result
    cleaned_id = result.upper()

    if not CANDIDATE_ID_PATTERN.match(cleaned_id):
        return _error(
            "INVALID_FORMAT",
            f"Mã ứng viên '{candidate_id}' không đúng định dạng 'CV-<số>' (Ví dụ: CV-1042).",
        )

    profile = CANDIDATE_DB.get(cleaned_id)
    if profile is None:
        return _error(
            "NOT_FOUND",
            f"Không tìm thấy ứng viên với mã '{cleaned_id}' trong hệ thống.",
        )

    return _success(dict(profile))


# ============================================================
# 🔧 TOOL 2: Tra cứu yêu cầu tuyển dụng của một vị trí
# ============================================================

def check_job_requirements(job_title: str) -> str:
    """
    Tra cứu yêu cầu tuyển dụng (kỹ năng bắt buộc, số năm kinh nghiệm tối
    thiểu) của một vị trí công việc. Chỉ đọc dữ liệu, không so khớp với
    ứng viên cụ thể nào.

    Args:
        job_title (str): Tên vị trí tuyển dụng (Ví dụ: 'Data Analyst').
            Bắt buộc, không được rỗng.

    Returns:
        str: Chuỗi JSON theo envelope {status, data, error}.
            - success -> data chứa: job_title, required_skills (list),
              min_experience_years (int).
            - error   -> error.code thuộc:
              MISSING_FIELD | INVALID_TYPE | NOT_FOUND.
        Hàm KHÔNG BAO GIỜ raise exception; mọi lỗi được trả trong "error".
    """
    ok, result = _validate_required_str(job_title, "job_title")
    if not ok:
        return result
    cleaned_title = result

    req = JOB_REQUIREMENTS_DB.get(cleaned_title)
    if req is None:
        available = ", ".join(JOB_REQUIREMENTS_DB.keys())
        return _error(
            "NOT_FOUND",
            f"Không tìm thấy yêu cầu tuyển dụng cho vị trí '{job_title}'. "
            f"Các vị trí hiện có trong hệ thống: {available}.",
        )

    return _success(dict(req))


# ============================================================
# 🔧 TOOL 3: Đặt lịch phỏng vấn
# ============================================================

def schedule_interview(candidate_id: str, interviewer_name: str, interview_datetime: str) -> str:
    """
    Đặt lịch phỏng vấn cho một ứng viên đã tồn tại trong hệ thống, vào
    một thời điểm hợp lệ. Đây là bước GHI DỮ LIỆU (write) duy nhất trong
    bộ tool — vì vậy tool tự validate chặt trước khi ghi, KHÔNG tự suy
    diễn / KHÔNG bịa lịch hẹn khi input sai. Tool này KHÔNG tự đánh giá
    độ phù hợp ứng viên với vị trí — việc đó do Agent quyết định dựa
    trên kết quả của get_candidate_profile + check_job_requirements
    trước khi gọi tool này.

    Args:
        candidate_id (str): Mã ứng viên, định dạng 'CV-<số>'. Bắt buộc.
        interviewer_name (str): Tên người phỏng vấn. Bắt buộc, không rỗng.
        interview_datetime (str): Ngày giờ phỏng vấn, định dạng bắt buộc
            'DD/MM/YYYY HH:MM' (Ví dụ: '05/11/2025 14:00'). Bắt buộc.

    Returns:
        str: Chuỗi JSON theo envelope {status, data, error}.
            - success -> data chứa: candidate_id, candidate_name,
              interviewer_name, interview_datetime (đã chuẩn hóa).
            - error   -> error.code thuộc:
              MISSING_FIELD | INVALID_TYPE | INVALID_FORMAT |
              CANDIDATE_NOT_FOUND | INVALID_DATE | INVALID_TIME |
              PAST_DATETIME.
        Hàm KHÔNG BAO GIỜ raise exception; mọi lỗi được trả trong "error".
        Khi trả về "error", KHÔNG có lịch hẹn nào được tạo/ghi vào hệ thống.
    """
    # 1. Validate từng field bắt buộc — không được thiếu field nào,
    #    không tự điền giá trị mặc định thay thế.
    ok, result = _validate_required_str(candidate_id, "candidate_id")
    if not ok:
        return result
    cleaned_id = result.upper()

    ok, result = _validate_required_str(interviewer_name, "interviewer_name")
    if not ok:
        return result
    cleaned_interviewer = result

    ok, result = _validate_required_str(interview_datetime, "interview_datetime")
    if not ok:
        return result
    cleaned_dt_str = result

    # 2. Validate định dạng mã ứng viên
    if not CANDIDATE_ID_PATTERN.match(cleaned_id):
        return _error(
            "INVALID_FORMAT",
            f"Mã ứng viên '{candidate_id}' không đúng định dạng 'CV-<số>' (Ví dụ: CV-2078).",
        )

    # 3. Validate ứng viên có tồn tại trong hệ thống không
    profile = CANDIDATE_DB.get(cleaned_id)
    if profile is None:
        return _error(
            "CANDIDATE_NOT_FOUND",
            f"Không tìm thấy ứng viên với mã '{cleaned_id}'. Không thể đặt lịch phỏng vấn.",
        )

    # 4. Validate định dạng ngày giờ
    match = DATETIME_PATTERN.match(cleaned_dt_str)
    if not match:
        return _error(
            "INVALID_FORMAT",
            f"'{interview_datetime}' không đúng định dạng bắt buộc 'DD/MM/YYYY HH:MM' "
            f"(Ví dụ: 05/11/2025 14:00). Không thể đặt lịch phỏng vấn.",
        )

    day, month, year, hour, minute = (int(x) for x in match.groups())

    # 5. Validate ngày tháng có thật (chặn 30/02, 31/04, 32/13, v.v.)
    try:
        parsed_dt = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    except ValueError:
        return _error(
            "INVALID_DATE",
            f"'{interview_datetime}' không phải là ngày giờ có thật trong lịch "
            f"(ví dụ: ngày/tháng không tồn tại). Không thể đặt lịch phỏng vấn.",
        )

    # 6. Validate giờ giấc hợp lý (khung giờ làm việc 07:00 - 20:00)
    if not (WORK_HOUR_START <= parsed_dt.hour < WORK_HOUR_END):
        return _error(
            "INVALID_TIME",
            f"Giờ phỏng vấn '{parsed_dt.strftime('%H:%M')}' nằm ngoài khung giờ làm việc "
            f"hợp lý ({WORK_HOUR_START:02d}:00 - {WORK_HOUR_END:02d}:00). "
            f"Không thể đặt lịch phỏng vấn.",
        )

    # 7. Validate không đặt lịch trong quá khứ
    if parsed_dt < datetime.now():
        return _error(
            "PAST_DATETIME",
            f"Thời gian '{cleaned_dt_str}' đã ở trong quá khứ. Không thể đặt lịch phỏng vấn.",
        )

    # Mọi điều kiện hợp lệ -> ghi lịch hẹn
    interview_record = {
        "candidate_id": cleaned_id,
        "candidate_name": profile["name"],
        "interviewer_name": cleaned_interviewer,
        "interview_datetime": parsed_dt.strftime("%d/%m/%Y %H:%M"),
    }
    SCHEDULED_INTERVIEWS.append(interview_record)

    return _success(interview_record)


# ============================================================
# 🔧 TOOL 4: Sinh câu hỏi phỏng vấn theo vị trí (tiện ích, không
# nằm trong tools_expected bắt buộc nhưng cùng chuẩn envelope)
# ============================================================

def generate_interview_questions(job_title: str) -> str:
    """
    Sinh (theo mẫu cố định, KHÔNG gọi LLM) bộ câu hỏi phỏng vấn tham
    khảo cho một vị trí tuyển dụng đã tồn tại trong hệ thống.

    Args:
        job_title (str): Tên vị trí tuyển dụng. Bắt buộc, không rỗng,
            phải tồn tại trong hệ thống (dùng chung DB với
            check_job_requirements).

    Returns:
        str: Chuỗi JSON theo envelope {status, data, error}.
            - success -> data chứa: job_title, questions (list[str]).
            - error   -> error.code thuộc:
              MISSING_FIELD | INVALID_TYPE | NOT_FOUND.
        Hàm KHÔNG BAO GIỜ raise exception; mọi lỗi được trả trong "error".
    """
    ok, result = _validate_required_str(job_title, "job_title")
    if not ok:
        return result
    cleaned_title = result

    if cleaned_title not in JOB_REQUIREMENTS_DB:
        available = ", ".join(JOB_REQUIREMENTS_DB.keys())
        return _error(
            "NOT_FOUND",
            f"Không tìm thấy vị trí '{job_title}' trong hệ thống. "
            f"Các vị trí hiện có: {available}.",
        )

    questions = [
        f"Hãy mô tả kinh nghiệm liên quan trực tiếp đến vị trí {cleaned_title}.",
        "Bạn đã từng xử lý một tình huống khó trong công việc như thế nào?",
        f"Vì sao bạn phù hợp với vị trí {cleaned_title} và văn hóa công ty?",
    ]
    return _success({"job_title": cleaned_title, "questions": questions})


# ============================================================
# 📋 ĐĂNG KÝ TOOLS ĐỂ AGENT SỬ DỤNG
# ============================================================

AVAILABLE_TOOLS = {
    "get_candidate_profile": get_candidate_profile,
    "check_job_requirements": check_job_requirements,
    "schedule_interview": schedule_interview,
    "generate_interview_questions": generate_interview_questions,
}
