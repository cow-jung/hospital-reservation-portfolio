// =====================================================================
// 예약 내역 페이지
// 예약 취소 팝업
// =====================================================================


// 취소 팝업
const cancelModal =
    document.getElementById(
        "reservation_cancel_modal"
    );


// 모든 예약 취소 버튼
const cancelButtons =
    document.querySelectorAll(
        ".reservation-cancel-button"
    );


// 팝업 닫기 버튼
const modalCloseButton =
    document.getElementById(
        "cancel_modal_close"
    );


// 팝업 닫기 버튼
const modalCancelButton =
    document.getElementById(
        "cancel_modal_cancel"
    );


// 취소 form
const cancelForm =
    document.getElementById(
        "reservation_cancel_form"
    );


// 취소 사유
const cancelReason =
    document.getElementById(
        "cancel_reason"
    );


// 직접 입력
const cancelReasonDirect =
    document.getElementById(
        "cancel_reason_direct"
    );



// =====================================================================
// 예약 취소 팝업 열기
// =====================================================================

cancelButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                const reservationId =
                    button.dataset.reservationId;


                // 해당 예약의 취소 URL 설정
                cancelForm.action =
                    `/mypage/reservation/${reservationId}/cancel`;


                // 기존 입력 초기화
                cancelReason.value = "";

                cancelReasonDirect.value = "";

                cancelReasonDirect.style.display =
                    "none";

                cancelReasonDirect.required =
                    false;


                // 팝업 열기
                cancelModal.style.display =
                    "flex";
            }
        );
    }
);



// =====================================================================
// 팝업 닫기
// =====================================================================

function closeCancelModal() {

    cancelModal.style.display =
        "none";
}


if (modalCloseButton) {

    modalCloseButton.addEventListener(
        "click",
        closeCancelModal
    );
}


if (modalCancelButton) {

    modalCancelButton.addEventListener(
        "click",
        closeCancelModal
    );
}



// =====================================================================
// 팝업 바깥 클릭
// =====================================================================

window.addEventListener(
    "click",
    function (event) {

        if (
            event.target ===
            cancelModal
        ) {

            closeCancelModal();
        }
    }
);



// =====================================================================
// 직접 입력 선택
// =====================================================================

if (cancelReason) {

    cancelReason.addEventListener(
        "change",
        function () {

            if (
                cancelReason.value ===
                "직접 입력"
            ) {

                cancelReasonDirect.style.display =
                    "block";

                cancelReasonDirect.required =
                    true;
            }

            else {

                cancelReasonDirect.style.display =
                    "none";

                cancelReasonDirect.required =
                    false;

                cancelReasonDirect.value =
                    "";
            }
        }
    );
}



// =====================================================================
// 예약 취소 최종 확인
// =====================================================================

if (cancelForm) {

    cancelForm.addEventListener(
        "submit",
        function (event) {

            const result =
                confirm(
                    "예약을 취소하시겠습니까?"
                );


            if (!result) {

                event.preventDefault();
            }
        }
    );
}