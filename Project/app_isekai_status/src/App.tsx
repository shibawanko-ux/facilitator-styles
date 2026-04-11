import { useState } from 'react';
import type { Answer } from './logic/types';
import { calculateStatus } from './logic/calculator';
import StartScreen from './components/StartScreen';
import QuestionScreen from './components/QuestionScreen';
import LoadingScreen from './components/LoadingScreen';
import ResultScreen from './components/ResultScreen';
import LoginScreen from './components/LoginScreen';
import { useAuth } from './hooks/useAuth';

type Screen = 'start' | 'question' | 'loading' | 'result';

export default function App() {
  const { auth, handleLogin } = useAuth();
  const [screen, setScreen] = useState<Screen>('start');
  const [result, setResult] = useState<ReturnType<typeof calculateStatus> | null>(null);

  if (!auth.isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} error={auth.error} />;
  }

  const handleStart = () => setScreen('question');

  const handleComplete = (answers: Record<number, Answer>) => {
    const typedAnswers = {
      q1: answers[1],
      q2: answers[2],
      q3: answers[3],
      q4: answers[4],
      q5: answers[5],
      q6: answers[6],
    };
    setResult(calculateStatus(typedAnswers));
    setScreen('loading');
  };

  const handleLoadingDone = () => setScreen('result');

  const handleRetry = () => {
    setResult(null);
    setScreen('start');
  };

  if (screen === 'start') return <StartScreen onStart={handleStart} />;
  if (screen === 'question') return <QuestionScreen onComplete={handleComplete} />;
  if (screen === 'loading') return <LoadingScreen onDone={handleLoadingDone} />;
  if (screen === 'result' && result) return <ResultScreen result={result} onRetry={handleRetry} />;
  return null;
}
