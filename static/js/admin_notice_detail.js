// admin_notice_detail.html 전용 스크립트
// - '삭제' 버튼을 누르면 브라우저 기본 confirm() 대신,
//   화면에 맞춘 삭제 확인 모달을 띄웁니다.
// - 모달에서 '삭제'를 다시 누르면 그때 실제 삭제 폼을 제출합니다.

document.addEventListener("DOMContentLoaded", function () {
    var deleteBtn = document.getElementById("notice-delete-btn");
    var modal = document.getElementById("notice-delete-modal");
    var cancelBtn = document.getElementById("notice-delete-cancel");
    var confirmBtn = document.getElementById("notice-delete-confirm");
    var deleteForm = document.getElementById("notice-delete-form");

    if (!deleteBtn || !modal || !cancelBtn || !confirmBtn || !deleteForm) {
        return;
    }

    function openModal() {
        modal.style.display = "flex";
    }

    function closeModal() {
        modal.style.display = "none";
    }

    deleteBtn.addEventListener("click", openModal);
    cancelBtn.addEventListener("click", closeModal);

    // 모달 바깥(어두운 배경) 클릭 시에도 닫히도록
    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    // ESC 키로도 닫히도록
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && modal.style.display === "flex") {
            closeModal();
        }
    });

    confirmBtn.addEventListener("click", function () {
        deleteForm.submit();
    });
});
