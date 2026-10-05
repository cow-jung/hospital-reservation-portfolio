// =====================================================================
// 회원정보 수정 페이지 JavaScript
// =====================================================================
//
// 기능
// 1. 새 비밀번호 실시간 유효성 검사
// 2. 비밀번호 확인 일치 여부 검사
// 3. 오류 발생 시 입력창 빨간색 표시
// =====================================================================


// 새 비밀번호 입력창
const newPassword =
    document.getElementById("new_password");


// 새 비밀번호 확인 입력창
const newPasswordConfirm =
    document.getElementById("new_password_confirm");


// 오류 메시지
const passwordError =
    document.getElementById("password_error");

const passwordConfirmError =
    document.getElementById("password_confirm_error");



// =====================================================================
// 새 비밀번호 검사
// =====================================================================

function validateNewPassword() {

    const password =
        newPassword.value;


    // 비밀번호를 입력하지 않았으면
    // 변경하지 않는 것이므로 정상 처리
    if (password === "") {

        clearPasswordError();

        return true;
    }


    // 8자 이상
    if (password.length < 8) {

        showPasswordError(
            "비밀번호는 8자 이상이어야 합니다."
        );

        return false;
    }


    // 영문자 포함
    if (!/[A-Za-z]/.test(password)) {

        showPasswordError(
            "영문자를 1개 이상 포함해야 합니다."
        );

        return false;
    }


    // 숫자 포함
    if (!/[0-9]/.test(password)) {

        showPasswordError(
            "숫자를 1개 이상 포함해야 합니다."
        );

        return false;
    }


    // 특수문자 포함
    if (!/[^A-Za-z0-9]/.test(password)) {

        showPasswordError(
            "특수문자를 1개 이상 포함해야 합니다."
        );

        return false;
    }


    clearPasswordError();

    return true;
}



// =====================================================================
// 새 비밀번호 오류 표시
// =====================================================================

function showPasswordError(message) {

    newPassword.classList.add(
        "input-invalid"
    );


    passwordError.textContent =
        message;


    passwordError.style.display =
        "block";
}



// =====================================================================
// 새 비밀번호 오류 제거
// =====================================================================

function clearPasswordError() {

    newPassword.classList.remove(
        "input-invalid"
    );


    passwordError.textContent =
        "";


    passwordError.style.display =
        "none";
}



// =====================================================================
// 비밀번호 확인 검사
// =====================================================================

function validatePasswordConfirm() {

    // 새 비밀번호를 입력하지 않았다면
    // 확인도 검사하지 않음
    if (newPassword.value === "") {

        clearPasswordConfirmError();

        return true;
    }


    // 서로 다르면 오류
    if (
        newPassword.value
        !==
        newPasswordConfirm.value
    ) {

        newPasswordConfirm.classList.add(
            "input-invalid"
        );


        passwordConfirmError.textContent =
            "새 비밀번호가 일치하지 않습니다.";


        passwordConfirmError.style.display =
            "block";


        return false;
    }


    clearPasswordConfirmError();

    return true;
}



// =====================================================================
// 비밀번호 확인 오류 제거
// =====================================================================

function clearPasswordConfirmError() {

    newPasswordConfirm.classList.remove(
        "input-invalid"
    );


    passwordConfirmError.textContent =
        "";


    passwordConfirmError.style.display =
        "none";
}



// =====================================================================
// 입력할 때마다 실시간 검사
// =====================================================================

if (newPassword) {

    newPassword.addEventListener(
        "input",
        function () {

            validateNewPassword();


            // 비밀번호 확인에도 값이 있으면
            // 일치 여부 다시 검사
            if (
                newPasswordConfirm.value !== ""
            ) {

                validatePasswordConfirm();
            }

        }
    );
}


if (newPasswordConfirm) {

    newPasswordConfirm.addEventListener(
        "input",
        function () {

            validatePasswordConfirm();

        }
    );
}