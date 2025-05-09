export const useResume = () => {
  const generatePdf = async (
    name = "resume",
    labels: ILabel[]
  ): Promise<File> => {
    const data = await $fetch<Blob>("/api/resume/pdf/generate", {
      method: "POST",
      body: {
        resume_data: labels,
      },
      responseType: "blob",
    });

    if (!data) throw new Error("При генерации резюме возникла ошибка");

    return new File([data], name, { type: "application/pdf" });
  };

  const saveResume = async (pdf: File, name: string) => {
    const data = new FormData();
    const newFile = new File([await pdf.arrayBuffer()], name);
    data.append("resume", newFile);

    const res = await $fetch("api/resume/pdf/create", {
      method: "POST",
      body: data,
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
