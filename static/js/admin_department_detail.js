// admin_department_detail.html 전용 스크립트
// - '삭제' 버튼을 누르면 브라우저 기본 confirm() 대신,
//   화면에 맞춘 삭제 확인 모달을 띄웁니다.
// - 모달에서 '삭제'를 다시 누르면 그때 실제 삭제 폼을 제출합니다.

document.addEventListener("DOMContentLoaded", function () {
    var deleteBtn = document.getElementById("dept-delete-btn");
    var modal = document.getElementById("dept-delete-modal");
    var cancelBtn = document.getElementById("dept-delete-cancel");
    var confirmBtn = document.getElementById("dept-delete-confirm");
    var deleteForm = document.getElementById("dept-delete-form");

    // 소속 의료진이 있어 삭제 버튼이 비활성화된 경우 등,
    // 이 페이지에 삭제 버튼/모달이 없을 수 있으므로 방어적으로 체크
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
