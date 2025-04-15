import type { Ref } from "vue";

interface ProfileData {
  name: string;
  surname: string;
  email: string;
  phone_number: string;
  education: Education[];
  experience: Experience[];
  social_profiles: {
    linkedin: string;
    telegram: string;
  };
  languages: Language[];
}

interface Education {
  institution: string;
  degree: string;
  from: string;
  to: string;
}

interface Experience {
  company: string;
  role: string;
  from: string;
  to: string;
  description: string;
}

interface Language {
  language: string;
}

export const useProfile = () => {
  const defaultData = (): ProfileData => ({
    name: "",
    surname: "",
    email: "",
    phone_number: "",
    education: [],
    experience: [],
    social_profiles: {
      linkedin: "",
      telegram: "",
    },
    languages: [],
  });

  const data: Ref<ProfileData> = ref(defaultData());
  const isSaving = ref(false);
  const lastSaved = ref<Date | null>(null);
  const saveError = ref<string | null>(null);

  const { error, status } = useFetch("/api/user", {
    default: defaultData,
    transform: (input: any) => ({
      ...defaultData(),
      ...input,
    }),
    onResponse: ({ response }) => {
      if (response.ok && (response._data as ProfileData))
        data.value = response._data;
    },
    lazy: true,
  });

  const pending = computed(() => status.value === "pending");

  const debounce = <T extends (...args: any[]) => void>(
    fn: T,
    delay: number
  ) => {
    let timeoutId: ReturnType<typeof setTimeout>;
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn(...args), delay);
    };
  };

  const saveProfile = async () => {
    try {
      isSaving.value = true;
      saveError.value = null;

      await $fetch("/api/user", {
        method: "POST",
        body: data.value,
      });

      lastSaved.value = new Date();
    } catch (error) {
      saveError.value = "Ошибка сохранения профиля";
    } finally {
      isSaving.value = false;
    }
  };

  const debouncedSave = debounce(saveProfile, 500);

  watch(
    () => data.value,
    (newVal) => {
      if (!pending.value) debouncedSave();
    },
    { deep: true }
  );

  const addEducation = () => {
    data.value.education.push({
      institution: "",
      degree: "",
      from: "",
      to: "",
    });
  };

  const removeEducation = (index: number) => {
    data.value.education.splice(index, 1);
  };

  const addExperience = () => {
    data.value.experience.push({
      company: "",
      role: "",
      from: "",
      to: "",
      description: "",
    });
  };

  const removeExperience = (index: number) => {
    data.value.experience.splice(index, 1);
  };

  const updateLanguages = (langs: string[]) => {
    data.value.languages = langs.map((language) => ({
      language,
      ...data.value.languages.find((l) => l.language === language),
    }));
  };

  return {
    data,
    pending,

    isSaving,
    lastSaved,
    saveError,

    addEducation,
    removeEducation,
    addExperience,
    removeExperience,
    updateLanguages,
  };
};
