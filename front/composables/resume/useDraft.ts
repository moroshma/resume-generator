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

  const AnswersByStep = ref<Record<number, Record<string, string>>>({
    1: {},
    2: {},
    3: {},
  });

  const allAnswers = ref({});

  const stepQuestions = reactive<Record<number, any[]>>({
    1: [],
    2: [],
    3: [],
  });

  const {
    initBasicQuestions,
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
    initBasicQuestions();
  });

  const answeredCount = computed(() => {
    return Object.values(answers.value).length;
  });

  watch(stepNumber, (newVal, oldVal) => {
    // Сохраняем ответы предыдущего шага
    AnswersByStep.value[oldVal] = { ...answers.value };
    allAnswers.value = { ...answers.value };
    stepQuestions[oldVal] = [...questions.value];
    // Восстанавливаем вопросы и ответы для нового шага
    questions.value = stepQuestions[newVal];
    Object.assign(answers.value, AnswersByStep.value[newVal]);

    answers.value = {};
  });

  function nextStep() {
    if (stepNumber.value === 1) {
      // проверить выполнение всех вопросов
      getNextQuestions();
    } else if (stepNumber.value === 2) {
      generateLabels();
      generatePdf();
    }

    stepNumber.value = stepNumber.value + 1;
  }

  const pdfBlob = ref<Blob | null>(null);
  const pdfUrl = computed(() =>
    pdfBlob.value ? URL.createObjectURL(pdfBlob.value) : null
  );

  const generatePdf = async () => {
    try {
      isLoading.value = true;
      const response: Blob = await $fetch("/api/resume/pdf/generate", {
        method: "POST",
        responseType: "blob", // Указываем тип ответа как blob
        body: {
          answers: allAnswers.value,
          generated_skills: [
            "Python",
            "Django",
            "Flask",
            "FastAPI",
            "JavaScript",
            "React",
            "Node.js",
            "HTML5",
            "CSS3",
            "SQL",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "RESTful APIs",
            "GraphQL",
            "Docker",
            "Kubernetes",
            "AWS",
            "Git",
            "CI/CD",
            "Agile/Scrum",
            "Unit Testing",
            "Integration Testing",
          ],
        },
      });
      pdfBlob.value = response;
      // pdfBlob.value = new File([response], "VIBE.pdf", {
      //   type: response.type,
      // });
    } finally {
      isLoading.value = false;
    }
  };

  return {
    pdfBlob,
    pdfUrl,
    initBasicQuestions,
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
    allAnswers,
  };
};
