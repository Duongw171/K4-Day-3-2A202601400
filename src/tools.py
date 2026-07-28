"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.
"""

def get_weather(location: str) -> str:
    """
    Tra cứu thời tiết hiện tại của một thành phố.
    
    Args:
        location (str): Tên thành phố (Ví dụ: 'Hà Nội', 'TP.HCM', 'Đà Nẵng')
        
    Returns:
        str: Thông tin thời tiết chi tiết
    """
    loc_lower = location.lower()
    if "hà nội" in loc_lower or "ha noi" in loc_lower:
        return "Thời tiết Hà Nội: 28°C, Nắng nhẹ, Độ ẩm 65%."
    elif "hồ chí minh" in loc_lower or "tp.hcm" in loc_lower or "hcm" in loc_lower:
        return "Thời tiết TP.HCM: 33°C, Nắng nóng, Có mây."
    elif "đà nẵng" in loc_lower or "da nang" in loc_lower:
        return "Thời tiết Đà Nẵng: 30°C, Gió nhẹ, Mát mẻ."
    else:
        return f"LỖI: Không tìm thấy dữ liệu thời tiết cho địa điểm '{location}'."


def search_flights(origin: str, destination: str) -> str:
    """
    Tra cứu chuyến bay giữa hai địa điểm.
    
    Args:
        origin (str): Nơi đi (Ví dụ: 'TP.HCM')
        destination (str): Nơi đến (Ví dụ: 'Hà Nội')
        
    Returns:
        str: Danh sách chuyến bay khả dụng và giá vé
    """
    return (
        f"Chuyến bay từ {origin} -> {destination} ngày mai:\n"
        f"1. VN123 (08:00) - Giá: 1,500,000 VNĐ (Còn vé)\n"
        f"2. VJ456 (14:30) - Giá: 1,200,000 VNĐ (Còn vé)"
    )


# Danh sách các tool được đăng ký để Agent sử dụng
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "search_flights": search_flights,
}
"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.
"""


def parse_resume(resume_text: str) -> str:
    """
    Trích xuất thông tin chính từ hồ sơ ứng viên.

    Args:
        resume_text (str): Nội dung văn bản của CV / hồ sơ.

    Returns:
        str: Tóm tắt kỹ năng, kinh nghiệm, học vấn, và điểm mạnh chính.
    """
    if not resume_text or not resume_text.strip():
        return "LỖI: Nội dung hồ sơ rỗng hoặc không hợp lệ."

    # Mô phỏng phân tích resume cho ví dụ.
    return (
        "Tóm tắt hồ sơ ứng viên:\n"
        "- Kỹ năng chính: Python, Phân tích dữ liệu, Quản lý dự án\n"
        "- Kinh nghiệm: 3 năm tuyển dụng IT, phỏng vấn kỹ thuật, sàng lọc CV\n"
        "- Học vấn: Cử nhân Quản trị Nhân sự / Khoa học Máy tính\n"
        "- Điểm mạnh: Giao tiếp tốt, đánh giá phù hợp năng lực, sắp xếp lịch phỏng vấn."
    )


def screen_candidate(candidate_profile: str, job_description: str) -> str:
    """
    Đánh giá sơ bộ mức độ phù hợp của ứng viên với mô tả công việc.

    Args:
        candidate_profile (str): Thông tin ứng viên đã được trích xuất.
        job_description (str): Mô tả yêu cầu công việc.

    Returns:
        str: Nhận xét về mức độ phù hợp và đề xuất bước tiếp theo.
    """
    if not candidate_profile or not job_description:
        return "LỖI: Thiếu profile ứng viên hoặc mô tả công việc."

    if "tuyển dụng" in job_description.lower() or "phỏng vấn" in job_description.lower():
        return (
            "Ứng viên có phù hợp sơ bộ với yêu cầu tuyển dụng.\n"
            "Đề xuất: Tiếp tục vào vòng phỏng vấn kỹ thuật và đánh giá kỹ năng mềm."
        )

    return (
        "Ứng viên có một số điểm phù hợp nhưng cần thảo luận thêm với người tuyển dụng.\n"
        "Đề xuất: kiểm tra chi tiết yêu cầu công việc và kỹ năng chuyên môn."
    )


def extract_skills(resume_text: str) -> str:
    """
    Liệt kê kỹ năng chính từ hồ sơ ứng viên.

    Args:
        resume_text (str): Nội dung hồ sơ ứng viên.

    Returns:
        str: Danh sách kỹ năng liên quan đến vị trí tuyển dụng.
    """
    if not resume_text or not resume_text.strip():
        return "LỖI: Nội dung hồ sơ rỗng hoặc không hợp lệ."

    return (
        "Kỹ năng tìm được:\n"
        "- Tuyển dụng và sàng lọc hồ sơ\n"
        "- Phỏng vấn ứng viên\n"
        "- Quản lý lịch phỏng vấn\n"
        "- Giao tiếp và thuyết trình\n"
    )


def match_candidate_to_role(candidate_profile: str, job_description: str) -> str:
    """
    So sánh ứng viên với yêu cầu công việc và đưa ra kết luận.

    Args:
        candidate_profile (str): Hồ sơ ứng viên đã phân tích.
        job_description (str): Mô tả công việc.

    Returns:
        str: Đánh giá cuối cùng và khuyến nghị.
    """
    if not candidate_profile or not job_description:
        return "LỖI: Thiếu profile ứng viên hoặc mô tả công việc."

    return (
        "Đánh giá kết hợp: Ứng viên phù hợp 70-80% với vai trò.\n"
        "Khuyến nghị: mời vào vòng phỏng vấn và kiểm tra thêm về kỹ năng chuyên môn."
    )


def schedule_interview(candidate_name: str, preferred_times: str) -> str:
    """
    Tạo lịch hẹn phỏng vấn cho ứng viên.

    Args:
        candidate_name (str): Tên ứng viên.
        preferred_times (str): Khung thời gian ứng viên mong muốn.

    Returns:
        str: Xác nhận lịch hẹn phỏng vấn.
    """
    if not candidate_name or not preferred_times:
        return "LỖI: Thiếu tên ứng viên hoặc thời gian mong muốn."

    return (
        f"Đã đặt lịch phỏng vấn cho {candidate_name}.\n"
        f"Thời gian đề xuất: {preferred_times}.\n"
        "Vui lòng xác nhận lại với bộ phận nhân sự."
    )


def generate_interview_questions(job_role: str) -> str:
    """
    Sinh bộ câu hỏi phỏng vấn phù hợp với vị trí.

    Args:
        job_role (str): Tên vị trí tuyển dụng.

    Returns:
        str: Danh sách câu hỏi phỏng vấn đề xuất.
    """
    if not job_role or not job_role.strip():
        return "LỖI: Vui lòng cung cấp tên vị trí tuyển dụng."

    return (
        f"Bộ câu hỏi phỏng vấn cho vị trí {job_role}:\n"
        "1. Hãy mô tả kinh nghiệm của bạn trong tuyển dụng và sàng lọc hồ sơ.\n"
        "2. Bạn ưu tiên yếu tố nào khi lựa chọn ứng viên phù hợp?\n"
        "3. Làm sao bạn xử lý khi ứng viên có kỹ năng tốt nhưng văn hóa chưa phù hợp?\n"
    )


# Danh sách các tool được đăng ký để Agent sử dụng
AVAILABLE_TOOLS = {
    "parse_resume": parse_resume,
    "screen_candidate": screen_candidate,
    "extract_skills": extract_skills,
    "match_candidate_to_role": match_candidate_to_role,
    "schedule_interview": schedule_interview,
    "generate_interview_questions": generate_interview_questions,
}
