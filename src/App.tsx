import { useDiagnosis } from './hooks/useDiagnosis';
import { TopPage } from './components/TopPage';
import { QuestionPage } from './components/QuestionPage';
import { ResultPage } from './components/ResultPage';

function App() {
  const {
    step,
    currentQuestion,
    currentQuestionIndex,
    totalQuestions,
    currentAnswer,
    progress,
    result,
    startDiagnosis,
    answerQuestion,
    nextQuestion,
    prevQuestion,
    goToTop,
  } = useDiagnosis();

  return (
    <div className="min-h-screen bg-gray-50">
      {step === 'top' && (
        <TopPage onStart={startDiagnosis} />
      )}

      {step === 'questions' && currentQuestion && (
        <QuestionPage
          question={currentQuestion}
          currentIndex={currentQuestionIndex}
          totalQuestions={totalQuestions}
          currentAnswer={currentAnswer}
          progress={progress}
          onAnswer={answerQuestion}
          onNext={nextQuestion}
          onPrev={prevQuestion}
        />
      )}

      {step === 'result' && result && (
        <ResultPage
          result={result}
          onRestart={goToTop}
        />
      )}
    </div>
  );
}

export default App;
