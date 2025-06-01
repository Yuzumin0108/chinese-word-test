// モックデータ（実際はサーバーから取得）
const HSK_VOCAB = {
    "HSK1": [
        {"cn": "你好", "pinyin": "nǐ hǎo", "jp": "こんにちは"},
        {"cn": "谢谢", "pinyin": "xiè​xiè", "jp": "ありがとう"},
        {"cn": "再见", "pinyin": "zài​jiàn", "jp": "さようなら"}
    ],
    "HSK2": [
        {"cn": "朋友", "pinyin": "péng​you", "jp": "友達"},
        {"cn": "学习", "pinyin": "xué​xí", "jp": "学習する"},
        {"cn": "工作", "pinyin": "gōng​zuò", "jp": "働く"}
    ],
    "HSK3": [
        {"cn": "今天", "pinyin": "jīn​tiān", "jp": "今日、きょう"},
        {"cn": "帮助", "pinyin": "bāng​zhù", "jp": "助ける、手伝う"},
        {"cn": "认为", "pinyin": "rèn​wéi", "jp": "～と考える"}
    ],
    "HSK4": [
        {"cn": "发展", "pinyin": "fā​zhǎn", "jp": "発展"},
        {"cn": "经济", "pinyin": "jīng​jì", "jp": "経済"},
        {"cn": "文化", "pinyin": "wén​huà", "jp": "文化"}
    ]
};

let currentQuiz = null;
let currentQuestionIndex = 0;
let userAnswers = [];

// DOM要素の取得
document.addEventListener('DOMContentLoaded', () => {
    const quizSettings = document.getElementById('quizSettings');
    const questionDisplay = document.getElementById('questionDisplay');
    const userAnswer = document.getElementById('userAnswer');
    const submitAnswer = document.getElementById('submitAnswer');
    const nextQuestion = document.getElementById('nextQuestion');
    const restartQuiz = document.getElementById('restartQuiz');

    // テスト設定フォームの送信処理
    quizSettings.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const level = document.getElementById('level').value;
        const n_questions = parseInt(document.getElementById('n_questions').value);
        const mode = document.getElementById('mode').value;

        // クイズの生成
        const questions = generateQuiz(level, n_questions, mode);
        
        // クイズの開始
        startQuiz(questions);
    });

    // 答えの提出処理
    submitAnswer.addEventListener('click', () => {
        const answer = userAnswer.value.trim();
        if (answer) {
            userAnswers[currentQuestionIndex] = {
                id: currentQuiz[currentQuestionIndex].id,
                user_answer: answer
            };
            
            // スコアの更新
            updateScore();
            
            // 次の問題へ
            if (currentQuestionIndex < currentQuiz.length - 1) {
                currentQuestionIndex++;
                showQuestion(currentQuiz[currentQuestionIndex]);
            } else {
                // テスト終了
                showResults();
            }
            
            userAnswer.value = '';
        }
    });

    // 次の問題ボタンのクリック処理
    nextQuestion.addEventListener('click', () => {
        if (currentQuestionIndex < currentQuiz.length - 1) {
            currentQuestionIndex++;
            showQuestion(currentQuiz[currentQuestionIndex]);
        }
    });

    // テストの再開処理
    restartQuiz.addEventListener('click', () => {
        currentQuiz = null;
        currentQuestionIndex = 0;
        userAnswers = [];
        document.getElementById('quizArea').classList.add('hidden');
    });
});

// クイズの生成
function generateQuiz(level, n_questions, mode) {
    const words = HSK_VOCAB[level];
    const selectedWords = words.sort(() => 0.5 - Math.random()).slice(0, n_questions);
    
    return selectedWords.map((word, index) => ({
        id: index + 1,
        prompt: mode === "JP→CN" ? word.jp : `${word.cn} (${word.pinyin})`,
        answer: mode === "JP→CN" ? `${word.cn} (${word.pinyin})` : word.jp
    }));
}

// クイズの開始
function startQuiz(questions) {
    currentQuiz = questions;
    currentQuestionIndex = 0;
    userAnswers = Array(questions.length).fill(null);
    
    document.getElementById('quizArea').classList.remove('hidden');
    showQuestion(questions[0]);
}

// 問題の表示
function showQuestion(question) {
    const questionDisplay = document.getElementById('questionDisplay');
    questionDisplay.textContent = `${question.id}. ${question.prompt}`;
    
    const nextQuestion = document.getElementById('nextQuestion');
    nextQuestion.classList.add('hidden');
}

// スコアの更新
function updateScore() {
    const scoreDisplay = document.getElementById('scoreDisplay');
    const correctCount = userAnswers.filter((answer, index) => 
        answer && answer.user_answer.toLowerCase() === currentQuiz[index].answer.toLowerCase()
    ).length;
    
    scoreDisplay.textContent = `正解数: ${correctCount}/${currentQuiz.length}`;
    
    const nextQuestion = document.getElementById('nextQuestion');
    nextQuestion.classList.remove('hidden');
}

// 結果の表示
function showResults() {
    const correctCount = userAnswers.filter((answer, index) => 
        answer && answer.user_answer.toLowerCase() === currentQuiz[index].answer.toLowerCase()
    ).length;
    
    const percentage = (correctCount / currentQuiz.length * 100).toFixed(1);
    
    const scoreDisplay = document.getElementById('scoreDisplay');
    scoreDisplay.innerHTML = `
        <h2>テスト結果</h2>
        <p>${correctCount}/${currentQuiz.length} 問正解 (${percentage}%)</p>
        ${getFeedback(percentage)}
    `;
    
    document.getElementById('nextQuestion').classList.add('hidden');
    document.getElementById('restartQuiz').classList.remove('hidden');
}

// フィードバックの生成
function getFeedback(percentage) {
    if (percentage >= 90) {
        return '<p>素晴らしい！完璧なスコアです！</p>';
    } else if (percentage >= 70) {
        return '<p>良いスコアですね！次も頑張りましょう！</p>';
    } else {
        return '<p>もう少し練習が必要かもしれませんね。</p>';
    }
}
