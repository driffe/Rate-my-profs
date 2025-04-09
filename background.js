// 메시지 리스너 추가
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'searchProfessor') {
        console.log('검색 요청 수신:', request.url);
        
        // 응답이 이미 전송되었는지 확인하는 플래그
        let responseSent = false;
        
        fetchProfessorData(request.url)
            .then(data => {
                console.log('교수님 데이터 가져오기 성공:', data);
                if (!responseSent) {
                    responseSent = true;
                    sendResponse({ success: true, data: data });
                }
            })
            .catch(error => {
                console.error('교수님 데이터 가져오기 실패:', error);
                if (!responseSent) {
                    responseSent = true;
                    sendResponse({ success: false, error: error.message });
                }
            });
            
        // 비동기 응답을 위해 true 반환
        return true;
    }
});

// Rate My Professor 데이터 가져오기
async function fetchProfessorData(searchUrl) {
    try {
        console.log('검색 페이지 요청 중:', searchUrl);
        // 검색 페이지 가져오기
        const response = await fetch(searchUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });
        console.log('검색 페이지 응답 상태:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP 오류: ${response.status}`);
        }
        
        const html = await response.text();
        console.log('HTML 응답 수신 완료');
        
        // HTML 파싱
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        console.log('HTML 파싱 완료');
        
        // 첫 번째 검색 결과의 교수님 정보 추출
        const professorCard = doc.querySelector('a[href*="/ShowRatings.jsp"]');
        if (!professorCard) {
            console.log('교수님 카드를 찾을 수 없음');
            throw new Error('교수님 정보를 찾을 수 없습니다.');
        }
        console.log('교수님 카드 찾음');
        
        // 교수님 정보 추출
        const name = professorCard.querySelector('.NameTitle__Name-dowf0z-0')?.textContent.trim() || '이름 없음';
        const rating = professorCard.querySelector('.CardNumRating__CardNumRatingNumber-sc-17b90b3-0')?.textContent.trim() || 'N/A';
        const wouldTakeAgain = professorCard.querySelector('.CardFeedback__CardFeedbackNumber-sc-1lxuhw3-0')?.textContent.trim() || 'N/A';
        const difficulty = professorCard.querySelector('.CardFeedback__CardFeedbackNumber-sc-1lxuhw3-0:nth-child(2)')?.textContent.trim() || 'N/A';
        const url = 'https://www.ratemyprofessors.com' + professorCard.getAttribute('href');
        
        console.log('추출된 교수님 정보:', {
            name,
            rating,
            wouldTakeAgain,
            difficulty,
            url
        });
        
        return {
            name,
            rating,
            wouldTakeAgain,
            difficulty,
            url
        };
    } catch (error) {
        console.error('데이터 가져오기 중 오류 발생:', error);
        throw error;
    }
} 