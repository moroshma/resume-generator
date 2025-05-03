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
    { component: shallowRef(QuestionsList), title: "Базовые вопросы", id: 1 },
    {
      component: shallowRef(QuestionsList),
      title: "Дополнительные вопросы",
      id: 2,
    },
    {
      component: shallowRef(ResumeDraftLabels),
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
      getNextQuestions();
    } else if (stepNumber.value === 2) {
      await generateLabels();
      pdfFile.value = await generatePdf();
    }

    stepNumber.value = stepNumber.value + 1;
  }

  return {
    draft,
    nextStep,
    draftProgress,
  };
};
