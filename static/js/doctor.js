// =====================================================================
// 의료진 조회 페이지
// =====================================================================
//
// 기능
// 1. 의료진 이름 검색
// 2. 초성 필터
// =====================================================================


// 검색 입력창
const doctorSearchInput =
    document.getElementById(
        "doctor_search"
    );


// 검색 버튼
const doctorSearchButton =
    document.getElementById(
        "doctor_search_button"
    );


// 의료진 카드
const doctorCards =
    document.querySelectorAll(
        ".doctor-card"
    );


// 초성 버튼
const doctorFilterButtons =
    document.querySelectorAll(
        ".doctor-filter-button"
    );


// 검색 결과 없음
const doctorEmpty =
    document.getElementById(
        "doctor_empty"
    );



// =====================================================================
// 한글 초성
// =====================================================================

const doctorInitials = [

    "ㄱ",
    "ㄲ",
    "ㄴ",
    "ㄷ",
    "ㄸ",
    "ㄹ",
    "ㅁ",
    "ㅂ",
    "ㅃ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅉ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ"

];



// =====================================================================
// 이름의 첫 글자 초성 구하기
// =====================================================================

function getDoctorInitial(name) {

    if (!name) {

        return "";

    }


    const firstCharacter =
        name.charAt(0);


    const code =
        firstCharacter.charCodeAt(0);


    // 한글이 아닌 경우
    if (
        code < 0xAC00
        ||
        code > 0xD7A3
    ) {

        return firstCharacter;

    }


    const initialIndex =
        Math.floor(
            (code - 0xAC00)
            /
            588
        );


    return doctorInitials[
        initialIndex
    ];

}



// =====================================================================
// 검색 결과 표시 함수
// =====================================================================

function updateDoctorEmptyMessage(
    visibleCount
) {

    if (!doctorEmpty) {

        return;

    }


    if (visibleCount === 0) {

        doctorEmpty.style.display =
            "block";

    }

    else {

        doctorEmpty.style.display =
            "none";

    }

}



// =====================================================================
// 의료진 이름 검색
// =====================================================================

function searchDoctors() {

    const keyword =
        doctorSearchInput.value
            .trim()
            .toLowerCase();


    let visibleCount =
        0;


    doctorCards.forEach(
        function (card) {


            const doctorName =
                card.dataset.name
                    .toLowerCase();


            // 검색어가 이름에 포함된 경우
            if (
                doctorName.includes(
                    keyword
                )
            ) {


                card.style.display =
                    "flex";


                visibleCount++;

            }


            else {


                card.style.display =
                    "none";

            }

        }
    );


    updateDoctorEmptyMessage(
        visibleCount
    );

}



// =====================================================================
// 검색 버튼
// =====================================================================

if (
    doctorSearchButton
    &&
    doctorSearchInput
) {

    doctorSearchButton.addEventListener(
        "click",
        function () {

            searchDoctors();

        }
    );


    // Enter 검색
    doctorSearchInput.addEventListener(
        "keydown",
        function (event) {


            if (
                event.key === "Enter"
            ) {

                searchDoctors();

            }

        }
    );

}



// =====================================================================
// 초성 필터
// =====================================================================

doctorFilterButtons.forEach(
    function (button) {


        button.addEventListener(
            "click",
            function () {


                // 선택한 초성
                const selectedInitial =
                    button.dataset.filter;



                // -----------------------------------------------------
                // 기존 active 해제
                // -----------------------------------------------------

                doctorFilterButtons.forEach(
                    function (item) {


                        item.classList.remove(
                            "active"
                        );

                    }
                );


                // 현재 버튼 활성화
                button.classList.add(
                    "active"
                );



                // 검색창 초기화
                if (doctorSearchInput) {

                    doctorSearchInput.value =
                        "";

                }



                let visibleCount =
                    0;



                // -----------------------------------------------------
                // 의료진 필터링
                // -----------------------------------------------------

                doctorCards.forEach(
                    function (card) {


                        const doctorName =
                            card.dataset.name;


                        const initial =
                            getDoctorInitial(
                                doctorName
                            );



                        // 전체
                        if (
                            selectedInitial ===
                            "전체"
                        ) {


                            card.style.display =
                                "flex";


                            visibleCount++;

                        }


                        // 선택한 초성과 같은 경우
                        else if (
                            initial ===
                            selectedInitial
                        ) {


                            card.style.display =
                                "flex";


                            visibleCount++;

                        }


                        // 다른 초성
                        else {


                            card.style.display =
                                "none";

                        }

                    }
                );


                updateDoctorEmptyMessage(
                    visibleCount
                );

            }
        );

    }
);