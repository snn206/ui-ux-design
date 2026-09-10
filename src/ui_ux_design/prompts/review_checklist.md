<!-- prompts/review_checklist.md -->
# Anti-Pattern & Quality Review Checklist

## Bảng kiểm tra trước khi bàn giao UI (Checklist)
Trước khi xuất bản code hoặc hoàn tất task UI, Agent phải tự rà soát:

- [ ] **AI UI Smell #1 (Generic Gray Canvas)**: Có sử dụng tone màu thương hiệu hay rơi vào xám xịt vô hồn `#666`/`#999`?
- [ ] **AI UI Smell #2 (Rainbow Hell)**: Có quá 3 màu nhấn (accents) xung đột nhau không? Tỷ lệ 60-30-10 đã được đảm bảo chưa?
- [ ] **AI UI Smell #3 (Random Spacings)**: Toàn bộ padding, margin có tuân thủ 8px grid (`8px, 16px, 24px...`) không? Có giá trị lẻ (`13px, 17px, 23px`) không?
- [ ] **AI UI Smell #4 (Font Chaos)**: Có quá 2 họ font chữ trên cùng 1 trang không? Type scale có nhất quán không?
- [ ] **AI UI Smell #5 (Flat Darkness)**: Dark mode có phân lớp bề mặt rõ ràng qua elevation hay chỉ đơn giản là `#000000`?
- [ ] **AI UI Smell #6 (Linear Motion)**: Có transition nào đang dùng `ease` mặc định hoặc `linear` vụng về không?
- [ ] **AI UI Smell #7 (Low Contrast)**: Đã kiểm tra WCAG contrast ratio cho tất cả text/subtext (>= 4.5:1) chưa?
- [ ] **AI UI Smell #8 (Dead Clicks / No States)**: Các nút bấm, links có đủ trạng thái hover, active, focus-visible, disabled chưa?
