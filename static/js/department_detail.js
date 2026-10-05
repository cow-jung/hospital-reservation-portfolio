// =====================================================================
// 진료과 상세 페이지 탭
// =====================================================================


// 탭 버튼
const departmentTabs =
    document.querySelectorAll(
        ".department-tab"
    );


// 탭 내용
const departmentContents =
    document.querySelectorAll(
        ".department-tab-content"
    );



// =====================================================================
// 탭 클릭
// =====================================================================

departmentTabs.forEach(
    function (tab) {

        tab.addEventListener(
            "click",
            function () {

                // -----------------------------------------------------
                // 모든 탭 선택 해제
                // -----------------------------------------------------

                departmentTabs.forEach(
                    function (item) {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                // -----------------------------------------------------
                // 모든 내용 숨김
                // -----------------------------------------------------

                departmentContents.forEach(
                    function (content) {

                        content.classList.remove(
                            "active"
                        );

                    }
                );


                // -----------------------------------------------------
                // 현재 탭 활성화
                // -----------------------------------------------------

                tab.classList.add(
                    "active"
                );


                // 표시할 탭 ID
                const tabName =
                    tab.dataset.tab;


                const target =
                    document.getElementById(
                        tabName
                    );


                if (target) {

                    target.classList.add(
                        "active"
                    );

                }

            }
        );

    }
);