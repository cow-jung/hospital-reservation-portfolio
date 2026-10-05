// =====================================================================
// 마이페이지 JavaScript 최종본
// =====================================================================
//
// 기능
// 1. 회원 탈퇴 팝업 열기 / 닫기
// 2. 회원 탈퇴 사유 직접 입력
// 3. 예약 취소 팝업 열기 / 닫기
// 4. 예약 취소 사유 직접 입력
// 5. 예약 취소 최종 확인
//
// =====================================================================



// =====================================================================
// 1. 회원 탈퇴 팝업
// =====================================================================


// 회원 탈퇴 팝업
const withdrawModal =
    document.getElementById(
        "withdraw_modal"
    );


// 회원 탈퇴 팝업 열기 버튼
const withdrawOpenButton =
    document.getElementById(
        "withdraw_open_button"
    );


// 회원 탈퇴 팝업 X 버튼
const withdrawCloseButton =
    document.getElementById(
        "withdraw_close_button"
    );


// 회원 탈퇴 팝업 취소 버튼
const withdrawCancelButton =
    document.getElementById(
        "withdraw_cancel_button"
    );


// 탈퇴 사유 선택
const withdrawReason =
    document.getElementById(
        "withdraw_reason"
    );


// 탈퇴 사유 직접 입력
const withdrawReasonDirect =
    document.getElementById(
        "withdraw_reason_direct"
    );



// =====================================================================
// 회원 탈퇴 팝업 열기
// =====================================================================

if (
    withdrawOpenButton &&
    withdrawModal
) {

    withdrawOpenButton.addEventListener(
        "click",
        function () {

            // 기존 입력 초기화
            if (withdrawReason) {
                withdrawReason.value = "";
            }


            if (withdrawReasonDirect) {

                withdrawReasonDirect.value = "";

                withdrawReasonDirect.style.display =
                    "none";

                withdrawReasonDirect.required =
                    false;
            }


            // 팝업 열기
            withdrawModal.style.display =
                "flex";
        }
    );
}



// =====================================================================
// 회원 탈퇴 팝업 닫기 함수
// =====================================================================

function closeWithdrawModal() {

    if (withdrawModal) {

        withdrawModal.style.display =
            "none";
    }
}



// X 버튼
if (withdrawCloseButton) {

    withdrawCloseButton.addEventListener(
        "click",
        closeWithdrawModal
    );
}


// 취소 버튼
if (withdrawCancelButton) {

    withdrawCancelButton.addEventListener(
        "click",
        closeWithdrawModal
    );
}



// =====================================================================
// 회원 탈퇴 직접 입력
// =====================================================================

if (
    withdrawReason &&
    withdrawReasonDirect
) {

    withdrawReason.addEventListener(
        "change",
        function () {

            // 직접 입력 선택
            if (
                withdrawReason.value ===
                "직접 입력"
            ) {

                withdrawReasonDirect.style.display =
                    "block";

                withdrawReasonDirect.required =
                    true;
            }

            // 다른 사유 선택
            else {

                withdrawReasonDirect.style.display =
                    "none";

                withdrawReasonDirect.required =
                    false;

                withdrawReasonDirect.value =
                    "";
            }
        }
    );
}



// =====================================================================
// 2. 예약 취소 팝업
// =====================================================================


// 예약 취소 팝업
const reservationCancelModal =
    document.getElementById(
        "reservation_cancel_modal"
    );


// 모든 예약 취소 버튼
const reservationCancelButtons =
    document.querySelectorAll(
        ".reservation-cancel-button"
    );


// 예약 취소 X 버튼
const reservationCancelCloseButton =
    document.getElementById(
        "cancel_modal_close"
    );


// 예약 취소 닫기 버튼
const reservationCancelCancelButton =
    document.getElementById(
        "cancel_modal_cancel"
    );


// 예약 취소 form
const reservationCancelForm =
    document.getElementById(
        "reservation_cancel_form"
    );


// 예약 취소 사유
const cancelReason =
    document.getElementById(
        "cancel_reason"
    );


// 예약 취소 직접 입력
const cancelReasonDirect =
    document.getElementById(
        "cancel_reason_direct"
    );



// =====================================================================
// 예약 취소 팝업 열기
// =====================================================================

reservationCancelButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                // 예약번호 가져오기
                const reservationId =
                    button.dataset.reservationId;


                // -----------------------------------------------------
                // 해당 예약의 취소 URL 동적으로 설정
                //
                // 예:
                // /mypage/reservation/3/cancel
                // -----------------------------------------------------

                if (reservationCancelForm) {

                    reservationCancelForm.action =
                        `/mypage/reservation/${reservationId}/cancel`;
                }


                // 취소 사유 초기화
                if (cancelReason) {

                    cancelReason.value =
                        "";
                }


                if (cancelReasonDirect) {

                    cancelReasonDirect.value =
                        "";

                    cancelReasonDirect.style.display =
                        "none";

                    cancelReasonDirect.required =
                        false;
                }


                // 팝업 열기
                if (reservationCancelModal) {

                    reservationCancelModal.style.display =
                        "flex";
                }
            }
        );
    }
);



// =====================================================================
// 예약 취소 팝업 닫기
// =====================================================================

function closeReservationCancelModal() {

    if (reservationCancelModal) {

        reservationCancelModal.style.display =
            "none";
    }
}



// X 버튼
if (reservationCancelCloseButton) {

    reservationCancelCloseButton.addEventListener(
        "click",
        closeReservationCancelModal
    );
}


// 닫기 버튼
if (reservationCancelCancelButton) {

    reservationCancelCancelButton.addEventListener(
        "click",
        closeReservationCancelModal
    );
}



// =====================================================================
// 예약 취소 직접 입력
// =====================================================================

if (
    cancelReason &&
    cancelReasonDirect
) {

    cancelReason.addEventListener(
        "change",
        function () {

            // 직접 입력
            if (
                cancelReason.value ===
                "직접 입력"
            ) {

                cancelReasonDirect.style.display =
                    "block";

                cancelReasonDirect.required =
                    true;
            }

            // 다른 사유
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

if (reservationCancelForm) {

    reservationCancelForm.addEventListener(
        "submit",
        function (event) {

            // ---------------------------------------------------------
            // 취소 사유 선택 여부 확인
            // ---------------------------------------------------------

            if (
                !cancelReason ||
                cancelReason.value === ""
            ) {

                event.preventDefault();

                alert(
                    "예약 취소 사유를 선택해주세요."
                );

                return;
            }


            // ---------------------------------------------------------
            // 직접 입력을 선택했는데 내용이 없는 경우
            // ---------------------------------------------------------

            if (
                cancelReason.value ===
                "직접 입력"
                &&
                cancelReasonDirect.value.trim()
                === ""
            ) {

                event.preventDefault();

                alert(
                    "예약 취소 사유를 입력해주세요."
                );

                return;
            }


            // ---------------------------------------------------------
            // 최종 확인
            // ---------------------------------------------------------

            const result =
                confirm(
                    "예약을 취소하시겠습니까?"
                );


            // 사용자가 취소 선택
            if (!result) {

                event.preventDefault();
            }
        }
    );
}



// =====================================================================
// 3. 팝업 바깥 영역 클릭 시 닫기
// =====================================================================

window.addEventListener(
    "click",
    function (event) {

        // 회원 탈퇴 팝업 바깥
        if (
            event.target ===
            withdrawModal
        ) {

            closeWithdrawModal();
        }


        // 예약 취소 팝업 바깥
        if (
            event.target ===
            reservationCancelModal
        ) {

            closeReservationCancelModal();
        }
    }
);



// =====================================================================
// 4. ESC 키로 팝업 닫기
// =====================================================================

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Escape") {

            closeWithdrawModal();

            closeReservationCancelModal();
        }
    }
);