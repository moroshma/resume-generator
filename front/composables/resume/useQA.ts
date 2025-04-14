export const useQA = () => {
  const MOCK_QUESTIONS = Array.from({ length: 10 }, (_, i) => ({
    id: i + 1,
    text: `Текстовый вопрос ${i + 1}`,
    placeholder: `Введите ответ на вопрос ${i + 1}`,
    type: "base",
  }));
  const MOCK_QUESTIONS2 = Array.from({ length: 10 }, (_, i) => ({
    id: MOCK_QUESTIONS.length + i + 1,
    text: `доп вопросы ${i + 1}`,
    placeholder: `Введите ответ на вопрос ${i + 1}`,
    type: "additionally",
  }));
  const questions = ref<any>([]);
  const answers = reactive<Record<string, string>>({});
  const labels = ref<any>([]);
  const pdfUrl = ref("");

  const totalQuestions = computed(() => questions.value.length);

  const isLoading = ref(false);

  const initQuestions = async () => {
    // const data = await $fetch("/api/v001/resume/basic/question");
    questions.value = MOCK_QUESTIONS;
  };

  const getNextQuestions = async () => {
    console.log(answers);
    // const { data } = await useFetch<any>("/api/v001/resume/question/get", {
    //   method: "POST",
    //   body: { answers },
    // });

    // if (data.value?.questions) {
    questions.value = MOCK_QUESTIONS2;
    // }
  };

  const generateLabels = async () => {
    // const { data } = await useFetch<any>("/api/v001/resume/label/generate", {
    //   method: "POST",
    //   body: { answers },
    // });

    labels.value = [
      {
        title: "Заголовок",
        answer: "Ответ для редактирования",
      },
    ];
  };

  return {
    questions,
    answers,
    labels,
    pdfUrl,
    initQuestions,
    getNextQuestions,
    generateLabels,
    isLoading,
    totalQuestions,
  };
};
