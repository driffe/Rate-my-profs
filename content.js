// 드래그 이벤트 리스너 추가
document.addEventListener('mouseup', function(e) {
    const selectedText = window.getSelection().toString().trim();
    if (selectedText) {
        // 설정 확인
        try {
            chrome.storage.sync.get(['university', 'autoPopup'], function(result) {
                console.log('설정 확인:', result);
                if (result.autoPopup !== false) { // autoPopup이 false가 아닐 때만 실행
                    console.log('교수님 검색 시작:', selectedText);
                    console.log('대학교:', result.university || '미지정');
                    searchProfessor(selectedText, e, result.university);
                } else {
                    console.log('자동 팝업이 비활성화되어 있습니다.');
                }
            });
        } catch (error) {
            console.error('설정 확인 중 오류 발생:', error);
            // 오류 발생 시에도 기본 검색 시도
            searchProfessor(selectedText, e);
        }
    }
});

// Rate My Professor 검색 함수
async function searchProfessor(name, event, university) {
    try {
        // 검색 URL 생성 (대학교 정보 포함)
        const searchQuery = university ? `${name} ${university}` : name;
        const searchUrl = `https://www.ratemyprofessors.com/search/professors?q=${encodeURIComponent(searchQuery)}`;
        console.log('검색 URL:', searchUrl);
        
        // 팝업 생성
        const popup = document.createElement('div');
        popup.style.cssText = `
            position: fixed;
            top: ${event.pageY}px;
            left: ${event.pageX}px;
            background: white;
            border: 1px solid #ccc;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 10000;
            max-width: 300px;
        `;
        
        popup.innerHTML = `
            <h3>${name}</h3>
            <p>검색 중...</p>
        `;
        
        document.body.appendChild(popup);
        console.log('팝업 생성됨');
        
        // 팝업 닫기 버튼
        const closeButton = document.createElement('button');
        closeButton.innerHTML = 'X';
        closeButton.style.cssText = `
            position: absolute;
            right: 5px;
            top: 5px;
            border: none;
            background: none;
            cursor: pointer;
        `;
        closeButton.onclick = () => {
            console.log('팝업 닫기 버튼 클릭됨');
            popup.remove();
        };
        popup.appendChild(closeButton);

        // 백그라운드 스크립트에 메시지 전송
        console.log('백그라운드 스크립트에 메시지 전송 중...');
        try {
            chrome.runtime.sendMessage({
                action: 'searchProfessor',
                url: searchUrl
            }, function(response) {
                if (chrome.runtime.lastError) {
                    console.error('메시지 전송 오류:', chrome.runtime.lastError);
                    popup.innerHTML = `
                        <h3>${name}</h3>
                        <p>확장 프로그램 오류가 발생했습니다. 페이지를 새로고침하고 다시 시도해주세요.</p>
                    `;
                    return;
                }
                
                console.log('백그라운드 스크립트 응답:', response);
                if (response && response.success) {
                    const professorData = response.data;
                    console.log('교수님 정보 수신:', professorData);
                    popup.innerHTML = `
                        <h3>${professorData.name}</h3>
                        <div style="margin-top: 10px;">
                            <p><strong>평점:</strong> ${professorData.rating} / 5.0</p>
                            <p><strong>다시 수강할 의향:</strong> ${professorData.wouldTakeAgain}%</p>
                            <p><strong>난이도:</strong> ${professorData.difficulty} / 5.0</p>
                        </div>
                        <a href="${professorData.url}" target="_blank" style="display: block; margin-top: 10px; color: #2c3e50; text-decoration: none;">
                            자세히 보기 →
                        </a>
                    `;
                } else {
                    console.log('교수님 정보를 찾을 수 없음');
                    popup.innerHTML = `
                        <h3>${name}</h3>
                        <p>교수님 정보를 찾을 수 없습니다.</p>
                    `;
                }
            });
        } catch (error) {
            console.error('메시지 전송 중 오류 발생:', error);
            popup.innerHTML = `
                <h3>${name}</h3>
                <p>확장 프로그램 오류가 발생했습니다. 페이지를 새로고침하고 다시 시도해주세요.</p>
            `;
        }
        
        // 10초 후 자동으로 팝업 닫기
        setTimeout(() => {
            console.log('팝업 자동 닫힘');
            popup.remove();
        }, 10000);
        
    } catch (error) {
        console.error('교수님 검색 중 오류 발생:', error);
    }
} 