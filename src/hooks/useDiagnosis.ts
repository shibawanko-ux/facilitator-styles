import { useState, useCallback, useMemo } from 'react';
import { Answer, DiagnosisResult, Question } from '../data/types';
import { questions, shuffleQuestions } from '../data/questions';
import { generateDiagnosisResult } from '../utils/scoring';

export type DiagnosisStep = 'top' | 'questions' | 'result';

export function useDiagnosis() {
  const [step, setStep] = useState<DiagnosisStep>('top');
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [shuffledQuestions, setShuffledQuestions] = useState<Question[]>([]);
  const [result, setResult] = useState<DiagnosisResult | null>(null);

  // 診断を開始
  const startDiagnosis = useCallback(() => {
    setShuffledQuestions(shuffleQuestions(questions));
    setAnswers([]);
    setCurrentQuestionIndex(0);
    setResult(null);
    setStep('questions');
  }, []);

  // 現在の質問
  const currentQuestion = useMemo(() => {
    return shuffledQuestions[currentQuestionIndex];
  }, [shuffledQuestions, currentQuestionIndex]);

  // 回答を記録
  const answerQuestion = useCallback((score: number) => {
    if (!currentQuestion) return;

    const newAnswer: Answer = {
      questionId: currentQuestion.id,
      score,
    };

    setAnswers((prev) => {
      // 既存の回答を更新するか、新しい回答を追加
      const existingIndex = prev.findIndex((a) => a.questionId === currentQuestion.id);
      if (existingIndex >= 0) {
        const updated = [...prev];
        updated[existingIndex] = newAnswer;
        return updated;
      }
      return [...prev, newAnswer];
    });
  }, [currentQuestion]);

  // 次の質問へ
  const nextQuestion = useCallback(() => {
    if (currentQuestionIndex < shuffledQuestions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    } else {
      // 全質問に回答したら結果を計算
      const diagnosisResult = generateDiagnosisResult(answers);
      setResult(diagnosisResult);
      setStep('result');
    }
  }, [currentQuestionIndex, shuffledQuestions.length, answers]);

  // 前の質問へ
  const prevQuestion = useCallback(() => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
    }
  }, [currentQuestionIndex]);

  // 現在の質問の回答を取得
  const currentAnswer = useMemo(() => {
    if (!currentQuestion) return undefined;
    return answers.find((a) => a.questionId === currentQuestion.id);
  }, [answers, currentQuestion]);

  // トップに戻る
  const goToTop = useCallback(() => {
    setStep('top');
    setAnswers([]);
    setCurrentQuestionIndex(0);
    setResult(null);
  }, []);

  // 進捗率
  const progress = useMemo(() => {
    if (shuffledQuestions.length === 0) return 0;
    return Math.round((currentQuestionIndex / shuffledQuestions.length) * 100);
  }, [currentQuestionIndex, shuffledQuestions.length]);

  return {
    step,
    currentQuestion,
    currentQuestionIndex,
    totalQuestions: shuffledQuestions.length,
    currentAnswer,
    progress,
    result,
    startDiagnosis,
    answerQuestion,
    nextQuestion,
    prevQuestion,
    goToTop,
  };
}
