export const useResume = () => {
  const generatePdf = async (labels: any) => {
    const { data } = await useFetch<any>("/api/v001/resume/pdf/generate", {
      method: "POST",
      body: { labels },
      responseType: "blob",
    });

    return URL.createObjectURL(data.value);
  };

  const saveResume = async (pdf: Blob) => {
    const formData = new FormData();
    formData.append("pdf", pdf);

    await useFetch("/api/v001/user/resume", {
      method: "POST",
      body: formData,
    });
  };

  const steps = ref([
    {
      title: "Базовые вопросы",
      hasQuestions: true,
    },
    {
      title: "Дополнительные вопросы",
      hasQuestions: true,
    },
    {
      title: "Редактирование лейблов",
      hasQuestions: false,
    },
    {
      title: "Просмотр резюме",
      hasQuestions: false,
    },
  ]);

  return {
    generatePdf,
    saveResume,
  };
};
