// admin_department_edit.html 전용 스크립트
// 새 이미지 파일을 선택하면, 저장 전에 기존 이미지 자리에서 바로
// 새 이미지로 미리보기가 바뀝니다. (실제 저장은 '수정 저장' 버튼을 눌러야 됩니다)

document.addEventListener("DOMContentLoaded", function () {
    var fileInput = document.getElementById("dept_image_file");
    var previewImg = document.getElementById("dept-image-preview");
    var emptyLabel = document.getElementById("dept-image-empty");

    if (!fileInput || !previewImg) {
        return;
    }

    fileInput.addEventListener("change", function () {
        var file = fileInput.files && fileInput.files[0];

        if (!file) {
            return;
        }

        var objectUrl = URL.createObjectURL(file);
        previewImg.src = objectUrl;
        previewImg.style.display = "inline-block";

        if (emptyLabel) {
            emptyLabel.style.display = "none";
        }
    });
});
