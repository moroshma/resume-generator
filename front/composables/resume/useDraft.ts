import { QuestionsList, ResumeDraftLabels } from "#components";
import { ValidationError } from "~/utils/errors/ValidationError";
import { useQA } from "./useQA";
import { useResume } from "./useResume";

export const useDraft = () => {
  const {
    initBasicQuestions,
    generateLabels,
    questions,
    getNextQuestions,
    answers,
    labels,
    areAllQuestionsAnswered,
  } = useQA();

  const { generatePdf } = useResume();

  const pdfFile = ref<File | undefined>(undefined);

  const validationError = ref<Error | undefined>(undefined);

  const steps: IStep[] = [
    { component: QuestionsList, title: "Базовые вопросы", id: 1 },
    {
      component: QuestionsList,
      title: "Дополнительные вопросы",
      id: 2,
    },
    {
      component: ResumeDraftLabels,
      title: "Редактирование лейблов и просмотр PDF",
      id: 3,
    },
  ];

  const allAnswers = ref({});

  const answersByStep = reactive<Record<number, Record<string, string>>>({
    1: {},
    2: {},
  });

  const questionsByStep = reactive<Record<number, IQuestion[]>>({
    1: [],
    2: [],
  });

  const stepNumber = ref(1);
  const step = computed(() => steps[stepNumber.value - 1]);

  onMounted(() => {
    initBasicQuestions();
  });

  const draft = computed<IDraft>((): IDraft => {
    return {
      id: 1,
      step: step.value,
      baseQuestions: questionsByStep[1],
      generatedQuestions: questionsByStep[2],
      answersToBasicQuestions: answersByStep[1],
      answersToGeneratedQuestions: answersByStep[2],
      labels: labels.value,
      pdf: pdfFile.value,
    };
  });

  const draftProgress = computed<IDraftProgress>(() => {
    return {
      totalSteps: 3,
      step: draft.value.step,
    };
  });

  const canMoveToNextStep = (): boolean => {
    return areAllQuestionsAnswered();
  };

  watch(questions, (newV, oldV) => {
    questionsByStep[stepNumber.value] = newV;
  });

  watch(
    draft,
    (newV, oldV) => {
      if (stepNumber.value === 1) {
        answers.value = newV.answersToBasicQuestions;
      } else if (stepNumber.value === 2) {
        answers.value = newV.answersToGeneratedQuestions;
      }
      allAnswers.value = { ...answers.value };
    },
    {
      deep: true,
    }
  );

  async function nextStep() {
    if ([1, 2].includes(stepNumber.value) && !canMoveToNextStep()) {
      const error = new ValidationError("Заполните ответы на все вопросы.");
      validationError.value = undefined;
      setTimeout(() => {
        validationError.value = error;
      }, 50);
      throw error;
    } else {
      validationError.value = undefined;
    }

    stepNumber.value = stepNumber.value + 1;

    if (stepNumber.value === 2) {
      answers.value = answersByStep[stepNumber.value - 1];

      await getNextQuestions();
    } else if (stepNumber.value === 3) {
      answers.value = { ...answersByStep[1], ...answersByStep[2] };
      await generateLabels();
      pdfFile.value = await generatePdf("resume", {
        ...answersByStep[1],
        ...answersByStep[2],
      });
    }
  }

  return {
    allAnswers,
    draft,
    nextStep,
    draftProgress,
    stepNumber,
    validationError,
  };
};
