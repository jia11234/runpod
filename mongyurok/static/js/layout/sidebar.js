const sidebar = document.getElementById('sidebar');
const btn = document.getElementById('toggle-btn');

btn.addEventListener('click', () => {
  sidebar.classList.toggle('collapsed');
});

document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
        item.classList.add('active');


        const container = document.getElementById('history-container');
        if (item.dataset.mode === 'dokdae') {
            container.innerHTML = '독대 모드 내용입니다.'; // 여기에 실제 로직 연동
        } else {
            container.innerHTML = '역할극 모드 내용입니다.';
        }
    });
});