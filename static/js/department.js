// ============================================================
// 진료과 검색 및 초성 필터
// ============================================================


// 검색 입력창
const searchInput =
    document.getElementById("department_search");


// 검색 버튼
const searchButton =
    document.getElementById("department_search_button");


// 진료과 카드
const departmentCards =
    document.querySelectorAll(".department-card");


// 초성 버튼
const filterButtons =
    document.querySelectorAll(".filter-button");


// 검색 결과 없음 메시지
const emptyMessage =
    document.getElementById("department_empty");


// ============================================================
// 한글 초성 배열
// ============================================================

const koreanInitials = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ",
    "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ",
    "ㅋ", "ㅌ", "ㅍ", "ㅎ"
];


// ============================================================
// 글자의 초성을 구하는 함수
// ============================================================

function getInitial(text) {

    // 글자가 없는 경우
    if (!text) {
        return "";
    }


    // 첫 번째 글자
    const firstCharacter = text.charAt(0);


    // 유니코드 값
    const code =
        firstCharacter.charCodeAt(0);


    // 한글이 아닌 경우
    if (
        code < 0xAC00 ||
        code > 0xD7A3
    ) {

        return firstCharacter;
    }


    // 초성 번호 계산
    const initialIndex =
        Math.floor(
            (code - 0xAC00) / 588
        );


    return koreanInitials[initialIndex];
}


// ============================================================
// 진료과 이름 검색
// ============================================================

function searchDepartments() {

    // 검색어
    const keyword =
        searchInput.value
            .trim()
            .toLowerCase();


    let visibleCount = 0;


    departmentCards.forEach(
        function (card) {

            const departmentName =
                card.dataset.name
                    .toLowerCase();


            // 검색어가 진료과 이름에 포함되는 경우
            if (
                departmentName.includes(keyword)
            ) {

                card.style.display = "flex";

                visibleCount++;

            }

            else {

                card.style.display = "none";

            }

        }
    );


    // 결과가 하나도 없으면 안내 표시
    if (visibleCount === 0) {

        emptyMessage.style.display = "block";

    }

    else {

        emptyMessage.style.display = "none";

    }

}


// ============================================================
// 검색 버튼 클릭
// ============================================================

searchButton.addEventListener(
    "click",
    function () {

        searchDepartments();

    }
);


// ============================================================
// Enter 키 검색
// ============================================================

searchInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {

            searchDepartments();

        }

    }
);


// ============================================================
// 초성 버튼
// ============================================================

filterButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                const selectedInitial =
                    button.dataset.filter;


                // ---------------------------------------------
                // 모든 버튼 선택 효과 제거
                // ---------------------------------------------
                filterButtons.forEach(
                    function (item) {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                // 현재 누른 버튼 선택
                button.classList.add(
                    "active"
                );


                // 검색창 초기화
                searchInput.value = "";


                let visibleCount = 0;


                // ---------------------------------------------
                // 진료과 필터링
                // ---------------------------------------------
                departmentCards.forEach(
                    function (card) {

                        const departmentName =
                            card.dataset.name;


                        const initial =
                            getInitial(
                                departmentName
                            );


                        // 전체 버튼
                        if (
                            selectedInitial === "전체"
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

                        else {

                            card.style.display =
                                "none";

                        }

                    }
                );


                // 결과 없음 표시
                if (visibleCount === 0) {

                    emptyMessage.style.display =
                        "block";

                }

                else {

                    emptyMessage.style.display =
                        "none";

                }

            }
        );

    }
);