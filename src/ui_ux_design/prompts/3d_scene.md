<!-- prompts/3d_scene.md -->
# 3D Scene Architecture & Lighting Model Prompt

## Quy chuẩn xây dựng Scene 3D (Three.js / Babylon.js / WebGL)
Khi sinh code 3D hoặc tương tác WebGL, bắt buộc phải thiết lập hệ thống chiếu sáng và vật liệu chuẩn PBR (Physically Based Rendering).

## 3-Point Lighting Setup
- **Key Light (Đèn chính)**: DirectionalLight, intensity `1.2 - 1.5`, góc 45° từ phía trước - trên. Tạo shadow chính.
- **Fill Light (Đèn phụ)**: DirectionalLight hoặc AmbientLight, intensity `0.4 - 0.6`, góc đối diện Key Light để làm dịu bóng đổ.
- **Rim/Back Light (Đèn viền)**: DirectionalLight, intensity `0.8 - 1.0`, chiếu từ phía sau hướng về camera để tách vật thể khỏi nền.

## Material & Performance Guidelines
- Sử dụng `MeshStandardMaterial` hoặc `MeshPhysicalMaterial` với roughness và metalness định rõ.
- Luôn kiểm tra aspect ratio và update projection matrix khi resize cửa sổ.
- Tối ưu hóa draw calls: gộp geometries (BufferGeometryUtils.mergeGeometries) khi có nhiều static meshes.
