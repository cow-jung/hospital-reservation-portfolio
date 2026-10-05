// admin_department_create.html 전용 스크립트
// 파일을 선택하면 저장 전에 실제 이미지가 어떻게 보일지 바로 미리보여줍니다.
// (서버에 업로드하기 전, 브라우저 안에서만 임시로 읽어서 보여주는 것이라
//  '등록' 버튼을 누르기 전까지는 실제로 저장되지 않습니다)

document.addEventListener("DOMContentLoaded", function () {
    var fileInput = document.getElementById("dept_image_file");
    var previewWrap = document.getElementById("dept-image-preview-wrap");
    var previewImg = document.getElementById("dept-image-preview");

    if (!fileInput || !previewWrap || !previewImg) {
        return;
    }

    fileInput.addEventListener("change", function () {
        var file = fileInput.files && fileInput.files[0];

        if (!file) {
            previewWrap.style.display = "none";
            previewImg.src = "";
            return;
        }

        var objectUrl = URL.createObjectURL(file);
        previewImg.src = objectUrl;
        previewWrap.style.display = "block";
    });
});
