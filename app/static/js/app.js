document.addEventListener('DOMContentLoaded', function() {
    const recordModeBtn = document.getElementById('recordModeBtn');
    const translateModeBtn = document.getElementById('translateModeBtn');
    const recordControls = document.getElementById('recordControls');
    const translateControls = document.getElementById('translateControls');
    const recordBtn = document.getElementById('recordBtn');
    const translateBtn = document.getElementById('translateBtn');
    const signNameInput = document.getElementById('signNameInput');
    const output = document.getElementById('output');
    const continuousMode = document.getElementById('continuousMode');

    let isContinuousTranslating = false;
    let isRecording = false;
    let isTranslateMode = false;

    // 模式切换
    recordModeBtn.addEventListener('click', () => {
        recordModeBtn.classList.add('active');
        translateModeBtn.classList.remove('active');
        recordControls.style.display = 'block';
        translateControls.style.display = 'none';
        isTranslateMode = false;
        output.value = '';
    });

    translateModeBtn.addEventListener('click', async () => {
        recordModeBtn.classList.remove('active');
        translateModeBtn.classList.add('active');
        recordControls.style.display = 'none';
        translateControls.style.display = 'block';
        isTranslateMode = true;
        output.value = '';
    });

    // 录制功能
    recordBtn.addEventListener('click', async () => {
        try {
            if (!isRecording) {
                const name = signNameInput.value.trim();
                if (!name) {
                    throw new Error('请输入手语名称');
                }
                
                // 开始录制
                isRecording = true;
                recordBtn.textContent = '停止录制';
                output.value = '正在录制...';
                
                await handleRecord();
            } else {
                // 停止录制
                isRecording = false;
                recordBtn.textContent = '开始录制';
                
                const response = await handleRecord();

                if (response.ok) {
                    // 保存录制
                    const saveResponse = await handleSave(signNameInput.value.trim());
                    
                    if (saveResponse.ok) {
                        output.value = '录制保存成功';
                        signNameInput.value = '';
                    } else {
                        const error = await saveResponse.json();
                        throw new Error(error.error || '保存失败');
                    }
                } else {
                    const error = await response.json();
                    throw new Error(error.error || '录制失败');
                }
            }
        } catch (error) {
            output.value = `错误: ${error.message}`;
            isRecording = false;
            recordBtn.textContent = '开始录制';
        }
    });

    // 修改翻译按钮处理
    translateBtn.addEventListener('click', async () => {
        // 1. 如果正在录制，处理停止逻辑
        if (isRecording) {
            if (isContinuousTranslating) {
                // 停止连续翻译
                isContinuousTranslating = false;
                isRecording = false;
                translateBtn.textContent = '开始翻译';
                
                // 确保停止录制
                try {
                    await handleRecord();
                } catch (error) {
                    console.error('Error stopping recording:', error);
                }
            }
            return;
        }

        // 首先添加正则化函数
        function normalizeGlossText(text) {
            return text.split(/\s+/)
                .map(word => {
                    // 检查是否有语言前缀（如 Hksl_, Jsl_ 等）
                    const prefixMatch = word.match(/^[A-Za-z]+_/);
                    if (prefixMatch) {
                        // 移除语言前缀，并将剩余的下划线替换为空格
                        return word.substring(prefixMatch[0].length).toLowerCase().replace(/_/g, ' ');
                    }
                    return word.toLowerCase();
                })
                .join(' ');
        }
        
        try {
            if (continuousMode.checked) {
                // 连续翻译模式
                isContinuousTranslating = true;
                isRecording = true;
                translateBtn.textContent = '停止翻译';
                output.value = '开始连续翻译...';
                
                while (isContinuousTranslating) {
                    // 检查是否应该停止
                    if (!isContinuousTranslating || !isRecording) {
                        break;
                    }

                    // 开始录制
                    await handleRecord();
                    
                    // 等待1.5秒
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    
                    // 停止录制并翻译
                    const recordResponse = await handleRecord();
                    if (!recordResponse.ok) continue;

                    const translateResponse = await handleTranslate();
                    if (!translateResponse.ok) continue;

                    const data = await translateResponse.json();
                    if (data.status === 'success' && data.text) {
                        output.value = `最新翻译: ${data.text}`;
                        if (data.text.toLowerCase() !== 'idle') {
                            const glossInput = document.getElementById('gloss_input');
                            if (glossInput) {
                                const normalizedText = normalizeGlossText(data.text);
                                const currentValue = glossInput.value.trim();
                                glossInput.value = currentValue 
                                    ? `${currentValue} ${normalizedText}`
                                    : normalizedText;
                            }
                        }
                    }

                    // 短暂暂停后继续下一轮
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            } else {
                // 原有的单次翻译模式代码
                isRecording = true;
                translateBtn.textContent = '正在录制...';
                output.value = '正在录制...';
                
                await handleRecord();
                await new Promise(resolve => setTimeout(resolve, 3000));
                
                const recordResponse = await handleRecord();
                if (!recordResponse.ok) {
                    const error = await recordResponse.json();
                    throw new Error(error.error || '录制失败');
                }

                output.value = '正在翻译...';
                const translateResponse = await handleTranslate();
                
                if (!translateResponse.ok) {
                    const error = await translateResponse.json();
                    throw new Error(error.error || '翻译失败');
                }

                const data = await translateResponse.json();
                output.value = `翻译结果: ${data.text}`;
                
                if (data.text && data.text.toLowerCase() !== 'idle') {
                    const glossInput = document.getElementById('gloss_input');
                    if (glossInput) {
                        glossInput.value = normalizeGlossText(data.text);
                    }
                }
            }
            
        } catch (error) {
            console.error('Translation error:', error);
            output.value = `错误: ${error.message}`;
        } finally {
            // 重置所有状态
            if (!continuousMode.checked || !isContinuousTranslating) {
                isRecording = false;
                isContinuousTranslating = false;
                translateBtn.textContent = '开始翻译';
            }
        }
    });
});

// 修改API路径
const API_BASE = '/api/shuwa';

// 修改所有API调用
async function handleRecord() {
    try {
        const response = await fetch(`${API_BASE}/record`, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        return response;  // 返回响应
    } catch (error) {
        console.error('Error:', error);
        throw error;  // 抛出错误以便调用者处理
    }
}

async function handleTranslate() {
    try {
        const response = await fetch(`${API_BASE}/translate`, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        return response;  // 返回响应
    } catch (error) {
        console.error('Error:', error);
        throw error;  // 抛出错误以便调用者处理
    }
}

async function handleSave(name) {
    try {
        const response = await fetch(`${API_BASE}/save`, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: name })
        });
        return response;  // 返回响应
    } catch (error) {
        console.error('Error:', error);
        throw error;  // 抛出错误以便调用者处理
    }
} 