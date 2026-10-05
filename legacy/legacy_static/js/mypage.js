// =========================================================
// 유민정 담당 - 마이페이지 JavaScript
// =========================================================
//
// 회원 탈퇴 사유에서 "직접 입력"을 선택하면
// 직접 입력 textarea를 화면에 표시하는 기능
// =========================================================


// 탈퇴 사유 선택창
const withdrawReasonSelect =
    document.getElementById("withdraw_reason");

// 직접 입력 영역
const withdrawReasonDirectArea =
    document.getElementById("withdraw_reason_direct_area");

// 직접 입력 textarea
const withdrawReasonDirect =
    document.getElementById("withdraw_reason_direct");


// mypage.html에 해당 요소가 존재할 때만 실행
if (
    withdrawReasonSelect &&
    withdrawReasonDirectArea &&
    withdrawReasonDirect
) {

    // 탈퇴 사유가 변경될 때 실행
    withdrawReasonSelect.addEventListener("change", function () {

        // 사용자가 "직접 입력"을 선택한 경우
        if (withdrawReasonSelect.value === "직접 입력") {

            // 직접 입력창 표시
            withdrawReasonDirectArea.style.display = "block";

            // 직접 입력을 필수값으로 변경
            withdrawReasonDirect.required = true;

        } else {

            // 다른 사유를 선택한 경우 직접 입력창 숨김
            withdrawReasonDirectArea.style.display = "none";

            // 필수 입력 해제
            withdrawReasonDirect.required = false;

            // 이전에 작성한 값이 있다면 초기화
            withdrawReasonDirect.value = "";

        }

    });

}