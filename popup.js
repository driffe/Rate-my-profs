// 설정 요소 가져오기
const universityInput = document.getElementById('university');
const autoPopupToggle = document.getElementById('autoPopupToggle');
const saveButton = document.getElementById('saveSettings');

// 저장된 설정 불러오기
chrome.storage.sync.get(['university', 'autoPopup'], function(result) {
    universityInput.value = result.university || '';
    autoPopupToggle.checked = result.autoPopup !== false; // 기본값은 true
});

// 설정 저장
saveButton.addEventListener('click', function() {
    const settings = {
        university: universityInput.value.trim(),
        autoPopup: autoPopupToggle.checked
    };
    
    chrome.storage.sync.set(settings, function() {
        // 저장 완료 메시지 표시
        saveButton.textContent = '저장됨!';
        saveButton.style.backgroundColor = '#27ae60';
        
        setTimeout(() => {
            saveButton.textContent = '설정 저장';
            saveButton.style.backgroundColor = '#2c3e50';
        }, 2000);
    });
}); 