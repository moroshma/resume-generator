import { QuestionsList, ResumeDraftLabels } from "#components";
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
  } = useQA();

  const { generatePdf } = useResume();

  const pdfFile = ref<File | undefined>(undefined);

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

  const answeredCount = computed(() => {
    return Object.values(answers.value).length;
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

  watch(questions, (newV, oldV) => {
    questionsByStep[stepNumber.value] = newV;
  });

  watch(stepNumber, (newVal, oldVal) => {
    answersByStep[oldVal] = { ...answers.value };
    allAnswers.value = { ...answers.value };
    questionsByStep[oldVal] = [...questions.value];

    questions.value = questionsByStep[newVal];
    Object.assign(answers.value, answersByStep[newVal]);

    answers.value = {};
  });

  async function nextStep() {
    if (stepNumber.value === 1) {
      answers.value = answersByStep[stepNumber.value];

      getNextQuestions();
    } else if (stepNumber.value === 2) {
      answers.value = { ...answersByStep[1], ...answersByStep[2] };
      await generateLabels();
      pdfFile.value = await generatePdf("resume", {
        ...answersByStep[1],
        ...answersByStep[2],
      });
    }

    stepNumber.value = stepNumber.value + 1;
  }

  return {
    allAnswers,
    draft,
    nextStep,
    draftProgress,
    stepNumber,
  };
};
