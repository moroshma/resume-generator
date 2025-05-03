export const useResume = () => {
  const generatePdf = async (
    name = "resume",
    answers: Record<string, string>
  ): Promise<File> => {
    const data = await $fetch<Blob>("/api/resume/pdf/generate", {
      method: "POST",
      body: {
        answers,
        generated_skills: ["Python"],
      },
      responseType: "blob",
    });

    if (!data) throw new Error("При генерации резюме возникла ошибка");

    return new File([data], name, { type: "application/pdf" });
  };

  const saveResume = async (pdf: Blob) => {
    const formData = new FormData();
    formData.append("resume", pdf);

    await $fetch("/api/v001/user/resume", {
      method: "POST",
      body: formData,
    });
  };

  const exportResume = async (id: number) => {
    const resume: File | undefined = await $fetch(`/api/resume/pdf/${id}`);

    if (resume) downloadAsFile(resume);
    else throw new Error("При экспорте резюме возникла ошибка");
  };

  const deleteResume = async (id: number) => {
    try {
      await $fetch(`/api/resume/pdf/${id}`, {
        method: "DELETE",
      });
    } catch (error) {
      throw error;
    }
  };

  function downloadAsFile(data: Blob) {
    let a = document.createElement("a");
    let file = new Blob([data], { type: "application/pdf" });
    a.href = URL.createObjectURL(file);
    a.download = "resume.pdf";
    a.click();
    a.remove();
  }

  return {
    generatePdf,
    saveResume,
    exportResume,
    deleteResume,
  };
};
