let isReading = false;
let utterance = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeVideoControls();
    initializeTooltips();
    addInViewAnimation();
    document.querySelectorAll('.ripple').forEach(button => {
        button.addEventListener('click', addRippleEffect);
    });
    document.body.classList.add('page-loaded');
    initializeTheme();
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshEntries);
    }
    addAvatarClickEvent();
});

// 初始化视频控制
function initializeVideoControls() {
    const timeline = document.querySelector('.timeline');
    const volumeSlider = document.querySelector('.volume-slider');
    
    // 时间轴点击事件
    if (timeline) {
        timeline.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            this.querySelector('.progress').style.width = `${percent * 100}%`;
        });
    }

    // 音量控制点击事件
    if (volumeSlider) {
        volumeSlider.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            this.querySelector('.volume-progress').style.width = `${percent * 100}%`;
        });
    }
}

// 初始化工具提示
function initializeTooltips() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', showTooltip);
        tooltip.addEventListener('mouseleave', hideTooltip);
    });
}

// 生成句子函数
function generateSentence() {
    const glossWords = document.getElementById('gloss_input').value.split(' ');
    const loadingOverlay = document.getElementById('loading');
    const sentenceElement = document.getElementById('generated_sentence');
    
    // 显示加载动画
    loadingOverlay.classList.add('fade-in');
    loadingOverlay.style.display = 'flex';

    // 发送请求到后端
    fetch('/generate_sentence', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'gloss_words': glossWords }),
    })
    .then(response => response.json())
    .then(data => {
        loadingOverlay.classList.remove('fade-in');
        loadingOverlay.classList.add('fade-out');
        
        setTimeout(() => {
            loadingOverlay.style.display = 'none';
            loadingOverlay.classList.remove('fade-out');
            
            sentenceElement.innerHTML = `<p>${data.sentence}</p>`;
            sentenceElement.classList.add('result-fade-in');
        }, 300);
    })
    .catch(error => {
        loadingOverlay.style.display = 'none';
        sentenceElement.innerHTML = '<p class="error">生成句子时出错，请重试。</p>';
        console.error('Error:', error);
    });
}

// 工具提示显示/隐藏函数
function showTooltip(e) {
    const tooltip = e.target;
    const tooltipText = tooltip.getAttribute('data-tooltip');
    
    if (!tooltipText) return;
    
    tooltip.style.opacity = '1';
    tooltip.style.visibility = 'visible';
}

function hideTooltip(e) {
    const tooltip = e.target;
    tooltip.style.opacity = '0';
    tooltip.style.visibility = 'hidden';
}

// 复制文本功能
function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    // 创建并显示 toast
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
      <div class="toast-content">
        <i class="ri-check-line"></i>
        <span>已复制到剪贴板</span>
      </div>
    `;
    document.body.appendChild(toast);
    
    // 2秒后移除 toast
    setTimeout(() => {
      toast.classList.add('toast-fade-out');
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }).catch(err => {
    console.error('复制文本失败:', err);
  });
}

// 主题切换相关函数
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.toggle('light-theme', savedTheme === 'light');
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const isLight = document.body.classList.toggle('light-theme');
    const theme = isLight ? 'light' : 'dark';
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
}

function updateThemeIcon(theme) {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'light' 
            ? '<i class="ri-moon-line"></i>' 
            : '<i class="ri-sun-line"></i>';
    }
}

// 添加元素进入视图动画
function addInViewAnimation() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    document.querySelectorAll('.animate-on-scroll').forEach((el) => {
        observer.observe(el);
    });
}

// 添加波纹效果
function addRippleEffect(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('div');
    const rect = button.getBoundingClientRect();
    
    ripple.className = 'ripple-effect';
    ripple.style.left = `${event.clientX - rect.left}px`;
    ripple.style.top = `${event.clientY - rect.top}px`;
    
    button.appendChild(ripple);
    
    ripple.addEventListener('animationend', () => {
        ripple.remove();
    });
}

// 标签切换动画
function switchTab(tabId) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        if (tab.id === tabId) {
            tab.classList.add('tab-fade-in');
            tab.classList.remove('hidden');
        } else {
            tab.classList.add('hidden');
            tab.classList.remove('tab-fade-in');
        }
    });
}


function readGeneratedText() {
  const generatedText = document.getElementById('generated_sentence').innerText;
  
  if ('speechSynthesis' in window) {
    if (isReading) {
      speechSynthesis.cancel();
      isReading = false;
    } else {
      utterance = new SpeechSynthesisUtterance(generatedText);
      utterance.lang = 'zh-CN';
      utterance.onend = function() {
        isReading = false;
        updateReadButtonIcon();
      };
      speechSynthesis.speak(utterance);
      isReading = true;
    }
    updateReadButtonIcon();
  } else {
    alert('抱歉，您的浏览器不支持文本朗读功能！');
  }
}

function updateReadButtonIcon() {
  const readButton = document.querySelector('.action-btn[onclick="readGeneratedText()"]');
  if (readButton) {
    const icon = readButton.querySelector('i');
    if (isReading) {
      icon.className = 'ri-pause-line';
    } else {
      icon.className = 'ri-sound-module-line';
    }
  }
}

window.addEventListener('beforeunload', function() {
  if (isReading) {
    speechSynthesis.cancel();
  }
});

let recommendedEntries = [
    {
        category: '日常用语',
        difficulty: 'easy',
        word: '你好',
        gloss: 'HELLO YOU GOOD'
    },
    {
        category: '问候语',
        difficulty: 'medium',
        word: '早上好',
        gloss: 'MORNING GOOD'
    },
    {
        category: '情感表达',
        difficulty: 'hard',
        word: '我很开心',
        gloss: 'I VERY HAPPY'
    },
    {
        category: '日常用语',
        difficulty: 'easy',
        word: '谢谢',
        gloss: 'THANK YOU'
    },
    {
        category: '问候语',
        difficulty: 'medium',
        word: '晚安',
        gloss: 'NIGHT PEACEFUL'
    },
    {
        category: '情感表达',
        difficulty: 'hard',
        word: '我爱你',
        gloss: 'I LOVE YOU'
    }
];

function refreshEntries() {
    const entriesGrid = document.querySelector('.entries-grid');
    const shuffled = [...recommendedEntries].sort(() => Math.random() - 0.5).slice(0, 3);
    
    entriesGrid.innerHTML = shuffled.map(entry => `
        <div class="entry-card">
            <div class="entry-header">
                <span class="entry-tag">${entry.category}</span>
                <span class="difficulty ${entry.difficulty}">${
                    entry.difficulty === 'easy' ? '简单' :
                    entry.difficulty === 'medium' ? '中等' : '困难'
                }</span>
            </div>
            <h4>${entry.word}</h4>
            <p class="entry-gloss">${entry.gloss}</p>
            <button class="practice-btn">
                <i class="ri-play-circle-line"></i>
                练习
            </button>
        </div>
    `).join('');
}

// 添加 toast 样式
const style = document.createElement('style');
style.textContent = `
  .toast-notification {
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    background-color: rgba(88, 28, 135, 0.9);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(5px);
    animation: toast-fade-in 0.3s ease-out;
  }

  .toast-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .toast-content i {
    color: #4ade80;
  }

  .toast-fade-out {
    animation: toast-fade-out 0.3s ease-out forwards;
  }

  @keyframes toast-fade-in {
    from {
      opacity: 0;
      transform: translateY(1rem);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes toast-fade-out {
    from {
      opacity: 1;
    }
    to {
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
            // Existing tab logic remains...

            // Add event listeners for practice buttons
            document.querySelectorAll('.practice-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const card = e.target.closest('.entry-card');
                    const title = card.querySelector('h4').textContent;
                    const category = card.querySelector('.entry-tag').textContent;
                    const difficulty = card.querySelector('.difficulty').textContent;
                    const gloss = card.querySelector('.entry-gloss').textContent;

                    openEntryDetailModal(title, category, difficulty, gloss);
                });
            });

            // Close modal when clicking on <span> (x)
            document.querySelector('.close').addEventListener('click', closeEntryDetailModal);

            // Close modal when clicking outside of it
            window.addEventListener('click', (event) => {
                if (event.target == document.getElementById('entryDetailModal')) {
                    closeEntryDetailModal();
                }
            });

            // Update learning tabs logic to handle recommended entries
            const learningTabs = document.querySelectorAll('.learning-tabs .tab-btn');
            const practiceArea = document.querySelector('.practice-area');
            const notesSection = document.getElementById('notesSection');
            const recommendedEntries = document.querySelector('.recommended-entries');
            const inputGroup = document.querySelector('.input-group');
            const resultCard = document.querySelector('.result-card');
            const learningStats = document.querySelector('.learning-stats');

            learningTabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    learningTabs.forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');

                    const tabText = tab.textContent.trim();

                    // Hide all sections first
                    inputGroup.style.display = 'block';
                    resultCard.style.display = 'block';
                    learningStats.style.display = 'flex';
                    notesSection.style.display = 'none';
                    recommendedEntries.style.display = 'none';

                    // Show appropriate section
                    if (tabText === '学习笔记') {
                        notesSection.style.display = 'block';
                        inputGroup.style.display = 'none';
                        resultCard.style.display = 'none';
                        learningStats.style.display = 'none';
                        loadNotes();
                    } else if (tabText === '相关词汇') {
                        recommendedEntries.style.display = 'block';
                        inputGroup.style.display = 'none';
                        resultCard.style.display = 'none';
                        learningStats.style.display = 'none';
                    }
                });
            });
        });

        function openEntryDetailModal(title, category, difficulty, gloss) {
            const modal = document.getElementById('entryDetailModal');
            const videoSrc = `https://example.com/videos/${title.toLowerCase().replace(/\s+/g, '-')}.mp4`;
            const video = document.getElementById('modalVideo');
            const placeholder = document.getElementById('videoPlaceholder');

            video.src = videoSrc;
            video.style.display = 'none';
            placeholder.style.display = 'flex';

            video.onloadeddata = function () {
                video.style.display = 'block';
                placeholder.style.display = 'none';
            };

            video.onerror = function () {
                video.style.display = 'none';
                placeholder.style.display = 'flex';
            };

            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalCategory').textContent = category;
            document.getElementById('modalDifficulty').textContent = difficulty;
            document.getElementById('modalDifficulty').className = `difficulty ${difficulty.toLowerCase()}`;
            document.getElementById('modalGloss').textContent = gloss;
            document.getElementById('modalDescription').textContent = `这是"${title}"手语的详细教学。通过观看视频和练习，你可以掌握这个手语表达。`;
            modal.style.display = 'block';
        }

        function closeEntryDetailModal() {
            const video = document.getElementById('modalVideo');
            video.pause();
            video.currentTime = 0;
            document.getElementById('entryDetailModal').style.display = 'none';
        }

        function startPractice() {
            alert('开始练习功能正在开发中');
        }

        function loadNotes() {
            // Add your note loading logic here
        }

        function saveNotes() {
            // Add your note saving logic here
        }




        document.addEventListener('DOMContentLoaded', () => {
                // 获取所有标签按钮和内容区域
                const tabButtons = document.querySelectorAll('.top-tab-btn');
                const tabContents = document.querySelectorAll('.tab-content');

                // 为每个标签按钮添加点击事件
                tabButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        // 获取要显示的标签页 ID
                        const tabId = button.getAttribute('data-tab');

                        // 移除所有按钮和内容区域的 active 类
                        tabButtons.forEach(btn => btn.classList.remove('active'));
                        tabContents.forEach(content => content.classList.remove('active'));

                        // 为当前点击的按钮和对应的内容区域添加 active 类
                        button.classList.add('active');
                        document.getElementById(tabId).classList.add('active');
                    });
                });

                // 初始化其他事件监听器
                initializeOtherEvents();
            });

            function initializeOtherEvents() {
                // 模式切换按钮
                const recordModeBtn = document.getElementById('recordModeBtn');
                const translateModeBtn = document.getElementById('translateModeBtn');
                const recordControls = document.getElementById('recordControls');
                const translateControls = document.getElementById('translateControls');

                if (recordModeBtn && translateModeBtn) {
                    recordModeBtn.addEventListener('click', () => {
                        recordModeBtn.classList.add('active');
                        translateModeBtn.classList.remove('active');
                        recordControls.style.display = 'block';
                        translateControls.style.display = 'none';
                    });

                    translateModeBtn.addEventListener('click', () => {
                        translateModeBtn.classList.add('active');
                        recordModeBtn.classList.remove('active');
                        translateControls.style.display = 'block';
                        recordControls.style.display = 'none';
                    });
                }
            }
// 如果使用 WebSocket
const socket = new WebSocket('your_websocket_url');
socket.onmessage = function(event) {
    const translationResult = event.data;
    updateGlossInput(translationResult);
    
    // 同时更新输出区域
    const output = document.getElementById('output');
    if (output) {
        output.value = translationResult;
    }
};

// 添加清空 gloss input 的函数
function clearGlossInput() {
    const glossInput = document.getElementById('gloss_input');
    if (glossInput) {
        glossInput.value = '';
        // 清空生成的句子结果
        const sentenceElement = document.getElementById('generated_sentence');
        if (sentenceElement) {
            sentenceElement.innerHTML = '';
        }
    }
}


// 更新标签页切换逻辑
document.addEventListener('DOMContentLoaded', function() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // 移除所有活动状态
            navBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // 添加新的活动状态
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
});

// 定义全局变量存储当前视频信息
let currentVideoData = null;



// 更新最近搜索标签
function updateRecentSearchTags(newSearch) {
    const searchTags = document.querySelector('.search-tags');
    const existingTags = Array.from(searchTags.children);
    
    // 检查是否已存在相同的标签
    const exists = existingTags.some(tag => tag.textContent === newSearch);
    if (!exists) {
        // 创建新标签
        const newTag = document.createElement('span');
        newTag.className = 'search-tag';
        newTag.textContent = newSearch;
        
        // 添加点击事件
        newTag.addEventListener('click', () => {
            document.querySelector('.search-input').value = newSearch;
            handleSearch();
        });
        
        // 如果标签数量超过3个，删除最旧的
        if (existingTags.length >= 3) {
            searchTags.removeChild(existingTags[0]);
        }
        
        // 添加新标签
        searchTags.appendChild(newTag);
    }
}

// 为搜索按钮添加事件监听
document.querySelector('.search-button').addEventListener('click', handleSearch);

// 为搜索输入框添加回车事件监听
document.querySelector('.search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

// 为搜索标签添加点击事件
document.querySelectorAll('.search-tag').forEach(tag => {
    tag.addEventListener('click', () => {
        document.querySelector('.search-input').value = tag.textContent;
        handleSearch();
    });
});

// 添加头像点击事件处理
function addAvatarClickEvent() {
    const avatar = document.querySelector('.avatar img');
    const profilePopup = document.querySelector('.profile-popup');
    
    if (!avatar || !profilePopup) {
        console.error('Avatar or profile popup elements not found');
        return;
    }
    
    // 点击头像显示/隐藏弹窗
    avatar.addEventListener('click', function(e) {
        e.stopPropagation();
        profilePopup.classList.toggle('show');
    });
    
    // 点击弹窗内部不关闭
    profilePopup.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // 点击页面其他地方关闭弹窗
    document.addEventListener('click', function() {
        profilePopup.classList.remove('show');
    });
    
    // 处理退出按钮点击
    const logoutBtn = document.querySelector('.profile-btn.logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            // 这里添加退出登录的逻辑
            console.log('退出登录');
        });
    }
    
    // 处理设置按钮点击
    const settingsBtn = document.querySelector('.profile-btn.settings');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', function() {
            // 这里添加跳转到设置页面的逻辑
            console.log('打开设置');
        });
    }
}

// 添加获取推荐的函数
function getRecommendations() {
    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.recommendation_text) {
            // 处理推荐文本
            displayRecommendations(data.recommendation_text);
        }
    })
    .catch(error => console.error('获取推荐失败:', error));
}

// 显示推荐内容的函数
function displayRecommendations(recommendations) {
    const recommendedEntries = document.querySelector('.recommended-entries');
    if (recommendedEntries) {
        recommendedEntries.style.display = 'block';
        const entriesGrid = recommendedEntries.querySelector('.entries-grid');
        
        // 清空现有内容
        entriesGrid.innerHTML = '';
        
        // 将空格分隔的字符串转换为数组
        const words = recommendations.split(' ');
        
        // 更新全局 recommendedEntries 数组的前三个词语
        for (let i = 0; i < Math.min(3, words.length); i++) {
            if (recommendedEntries[i]) {
                recommendedEntries[i].word = words[i];
                recommendedEntries[i].gloss = words[i].toUpperCase();
            }
        }
        
        // 使用更新后的 recommendedEntries 显示内容
        recommendedEntries.slice(0, 3).forEach(item => {
            const entryCard = document.createElement('div');
            entryCard.className = 'entry-card';
            entryCard.innerHTML = `
                <div class="entry-header">
                    <span class="entry-tag">${item.category}</span>
                    <span class="difficulty ${item.difficulty}">${
                        item.difficulty === 'easy' ? '简单' :
                        item.difficulty === 'medium' ? '中等' : '困难'
                    }</span>
                </div>
                <h4>${item.word}</h4>
                <p class="entry-gloss">${item.gloss}</p>
                <button class="practice-btn">
                    <i class="ri-play-circle-line"></i>
                    练习
                </button>
            `;
            entriesGrid.appendChild(entryCard);
        });
    }
}
