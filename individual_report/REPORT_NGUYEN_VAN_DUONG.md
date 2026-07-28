# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Văn Dương
- **Student ID**: 2A202601400
- **Date**: 2026-07-28

---

## I. Technical Contribution (15 Points)

Trong bài lab này, tôi đảm nhận vai trò Role 1 - Product Architect. Nhiệm vụ chính của tôi là xác định hướng giải quyết bài toán và thiết kế bộ test case để đánh giá khả năng của hệ thống Chatbot và ReAct Agent trong bối cảnh trợ lý tuyển dụng.

- **Modules Implemented**: [config/test_cases.json](../config/test_cases.json)
- **Code Highlights**: Tôi đã thiết kế 5 test cases phản ánh các tình huống khác nhau: câu hỏi đơn giản, câu hỏi quy định, tác vụ nhiều bước, và câu bẫy edge case. Trong đó, TC-05 tập trung vào tình huống ngày tháng không hợp lệ và thời gian đặt lịch phi lý.
- **Documentation**: Bộ test case này giúp hệ thống phân biệt rõ khi nào nên trả lời trực tiếp bằng Chatbot và khi nào cần dùng ReAct Agent với công cụ. Nó cũng đóng vai trò kiểm tra guardrail, đảm bảo Agent không tự bịa thông tin hoặc lặp vô tận khi gặp dữ liệu không hợp lệ.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Trong test case TC-05, hệ thống được yêu cầu đặt lịch phỏng vấn cho một ứng viên với thông tin không hợp lệ: ngày 30/02 và thời gian 3 giờ sáng. Đây là tình huống bẫy vì dữ liệu đầu vào không đúng và Agent cần phản ứng an toàn thay vì cố gắng thực hiện một hành động sai.
- **Log Source**: Các ghi nhận được thể hiện trong [docs/trace_eval.md](../docs/trace_eval.md) và luồng xử lý trong [src/app.py](../src/app.py).
- **Diagnosis**: Vấn đề không nằm ở khả năng suy luận của LLM mà ở mức prompt và guardrail. Khi nhận thấy dữ liệu đầu vào phi lý, Agent có thể bối rối và không biết nên dừng hay tiếp tục, dẫn đến phản hồi sai định dạng hoặc lặp lại hành động không cần thiết.
- **Solution**: Tôi đã định hướng test case để kiểm tra hành vi fallback an toàn: nếu đầu vào không hợp lệ, Agent phải dừng lại, báo rõ lỗi và không cố gọi tool sai. Điều này giúp hệ thống trở nên kỷ luật hơn và phù hợp hơn cho môi trường production.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: Khối Thought giúp Agent diễn giải được bước tiếp theo một cách rõ ràng hơn so với Chatbot. Điều này khiến quá trình phân tích và lựa chọn công cụ trở nên có cấu trúc và dễ kiểm soát hơn.
2. **Reliability**: ReAct không phải lúc nào cũng tốt hơn Chatbot. Với các câu hỏi đơn giản, Chatbot có thể phản hồi nhanh và hiệu quả hơn vì không cần thêm bước suy luận và gọi tool.
3. **Observation**: Observation đóng vai trò quan trọng vì chính kết quả từ môi trường làm thay đổi bước tiếp theo của Agent. Nếu không có observation, Agent rất dễ hallucinate hoặc đưa ra quyết định sai.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Trong tương lai, có thể dùng hệ thống hàng đợi bất đồng bộ để xử lý nhiều request cùng lúc và giảm độ trễ khi số lượng công việc tăng.
- **Safety**: Nên bổ sung một Supervisor LLM hoặc hệ thống validation trước khi Agent gọi tool để kiểm tra tính hợp lệ của đầu vào và giảm rủi ro hành động sai.
- **Performance**: Có thể tích hợp Vector DB hoặc memory structure để Agent tra cứu dữ liệu nhanh hơn khi hệ thống có nhiều công cụ và nhiều tình huống phức tạp.

---

> [!NOTE]
> Báo cáo này đã được hoàn thiện và lưu thành file báo cáo cá nhân theo mẫu quy định.
