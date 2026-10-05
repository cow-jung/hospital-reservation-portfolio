// =====================================================================
// 유민정 담당 - 병원소개 이미지 슬라이드
// =====================================================================
//
// 기능
// 1. 병원 이미지 자동 슬라이드
// 2. 이전 / 다음 버튼
// 3. 하단 점 버튼으로 원하는 이미지 이동
// =====================================================================


// 모든 슬라이드 이미지 가져오기
const hospitalSlides =
    document.querySelectorAll(".hospital-slide");


// 하단 슬라이드 점 버튼 가져오기
const slideDots =
    document.querySelectorAll(".slide-dot");


// 이전 / 다음 버튼
const slidePrevButton =
    document.getElementById("slide_prev");

const slideNextButton =
    document.getElementById("slide_next");


// 현재 보여주고 있는 슬라이드 번호
// 배열은 0부터 시작
let currentSlide = 0;


// 자동 슬라이드 타이머
let slideTimer;


// =====================================================================
// 슬라이드 표시 함수
// =====================================================================

function showSlide(index) {

    // ---------------------------------------------------------
    // 마지막 이미지에서 다음으로 이동하면
    // 다시 첫 번째 이미지로 돌아감
    // ---------------------------------------------------------
    if (index >= hospitalSlides.length) {

        index = 0;
    }


    // 첫 번째 이미지에서 이전으로 이동하면
    // 마지막 이미지로 이동
    if (index < 0) {

        index =
            hospitalSlides.length - 1;
    }


    // 현재 슬라이드 번호 저장
    currentSlide = index;


    // ---------------------------------------------------------
    // 모든 이미지의 active 제거
    // ---------------------------------------------------------
    hospitalSlides.forEach(
        function (slide) {

            slide.classList.remove("active");

        }
    );


    // ---------------------------------------------------------
    // 모든 점 버튼의 active 제거
    // ---------------------------------------------------------
    slideDots.forEach(
        function (dot) {

            dot.classList.remove("active");

        }
    );


    // 선택된 이미지만 표시
    hospitalSlides[
        currentSlide
    ].classList.add("active");


    // 현재 위치의 점 버튼 표시
    slideDots[
        currentSlide
    ].classList.add("active");

}


// =====================================================================
// 다음 이미지
// =====================================================================

function nextSlide() {

    showSlide(
        currentSlide + 1
    );

}


// =====================================================================
// 이전 이미지
// =====================================================================

function prevSlide() {

    showSlide(
        currentSlide - 1
    );

}


// =====================================================================
// 자동 슬라이드 시작
// =====================================================================

function startAutoSlide() {

    // 기존 타이머가 있으면 먼저 제거
    clearInterval(slideTimer);


    // 4초마다 다음 이미지로 이동
    slideTimer =
        setInterval(
            nextSlide,
            4000
        );

}


// =====================================================================
// 다음 버튼
// =====================================================================

if (slideNextButton) {

    slideNextButton.addEventListener(
        "click",
        function () {

            // 다음 이미지 표시
            nextSlide();

            // 사용자가 버튼을 클릭했으므로
            // 자동 슬라이드 시간을 다시 시작
            startAutoSlide();

        }
    );

}


// =====================================================================
// 이전 버튼
// =====================================================================

if (slidePrevButton) {

    slidePrevButton.addEventListener(
        "click",
        function () {

            // 이전 이미지 표시
            prevSlide();

            // 자동 슬라이드 다시 시작
            startAutoSlide();

        }
    );

}


// =====================================================================
// 하단 점 버튼
// =====================================================================

slideDots.forEach(
    function (dot) {

        dot.addEventListener(
            "click",
            function () {

                // data-slide 값 가져오기
                const slideIndex =
                    Number(
                        dot.dataset.slide
                    );


                // 해당 이미지로 이동
                showSlide(
                    slideIndex
                );


                // 자동 슬라이드 다시 시작
                startAutoSlide();

            }
        );

    }
);


// =====================================================================
// 페이지 처음 실행
// =====================================================================

if (hospitalSlides.length > 0) {

    // 첫 번째 이미지 표시
    showSlide(0);

    // 자동 슬라이드 시작
    startAutoSlide();

}