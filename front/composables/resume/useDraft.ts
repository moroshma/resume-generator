import { QuestionsList, ResumeDraftLabels } from "#components";
import { useQA } from "./useQA";

export const useDraft = () => {
  const steps = [
    { component: shallowRef(QuestionsList), title: "Базовые вопросы" },
    { component: shallowRef(QuestionsList), title: "Дополнительные вопросы" },
    {
      component: shallowRef(ResumeDraftLabels),
      title: "Редактирование лейблов",
    },
  ];

  const {
    initQuestions,
    generateLabels,
    questions,
    getNextQuestions,
    isLoading,
    answers,
    totalQuestions,
    labels,
  } = useQA();
  const stepNumber = ref(1);
  const step = computed(() => steps[stepNumber.value - 1]);

  onMounted(() => {
    initQuestions();
  });

  const answeredCount = computed(() => {
    const allAnswers = Object.values(answers);

    if (stepNumber.value === 1) {
      return questions.value
        .filter((q: any) => q.type === "base")
        .reduce((count: any, question: any) => {
          return count + (answers[question.id]?.trim() ? 1 : 0);
        }, 0);
    }

    return questions.value
      .filter((q: any) => q.type === "additionally")
      .reduce((count: any, question: any) => {
        return count + (answers[question.id]?.trim() ? 1 : 0);
      }, 0);
  });

  function nextStep() {
    if (stepNumber.value === 1) {
      // проверить выполнение всех вопросов
      getNextQuestions();
    } else if (stepNumber.value === 2) {
      generateLabels();
    } else if (stepNumber.value === 3) {
      //генерация резюме
    }

    stepNumber.value = stepNumber.value + 1;
  }

  return {
    initQuestions,
    generateLabels,
    questions,
    getNextQuestions,
    isLoading,
    answers,
    answeredCount,
    totalQuestions,
    labels,
    step,
    nextStep,
    stepNumber,
  };
};
