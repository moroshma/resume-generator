<template>
  <div class="profile-card">
    <div class="card-border"></div>

    <div class="content">
      <div class="header">
        <h1 class="title">
          <div class="name-fields">
            <EditableField v-model="data.name" label="Имя" class="name-field" />
            <EditableField
              v-model="data.surname"
              label="Фамилия"
              class="name-field"
            />
          </div>
        </h1>

        <div class="contact-badges">
          <EditableField
            v-model="data.email"
            type="email"
            placeholder="Email"
            icon="✉️"
          />
          <EditableField
            v-model="data.phone_number"
            type="tel"
            placeholder="Телефон"
            icon="📱"
          />
        </div>
      </div>

      <div class="main-sections">
        <div class="section-group">
          <div
            v-for="(edu, index) in data.education"
            :key="'edu-' + index"
            class="section"
          >
            <h3 class="section-title">
              <span>Образование</span>
              <button class="btn delete-btn" @click="removeEducation(index)">
                ×
              </button>
            </h3>
            <div class="info-grid">
              <EditableField
                v-model="edu.institution"
                placeholder="Учебное заведение"
              />
              <EditableField v-model="edu.degree" placeholder="Степень" />
              <DateRangeField :model="edu" />
            </div>
          </div>
          <button class="btn add-btn" @click="addEducation">
            <span>+ Добавить образование</span>
          </button>
        </div>

        <div class="section-group">
          <div
            v-for="(exp, index) in data.experience"
            :key="'exp-' + index"
            class="section"
          >
            <h3 class="section-title">
              <span>Опыт работы</span>
              <button class="btn delete-btn" @click="removeExperience(index)">
                ×
              </button>
            </h3>
            <div class="info-grid">
              <EditableField
                v-model="exp.company"
                placeholder="Название компании"
              />
              <EditableField v-model="exp.role" placeholder="Должность" />
              <DateRangeField :model="exp" />
              <EditableField
                v-model="exp.description"
                type="textarea"
                placeholder="Описание обязанностей"
              />
            </div>
          </div>
          <button class="btn add-btn" @click="addExperience">
            <span>+ Добавить опыт</span>
          </button>
        </div>

        <div class="section-group combined">
          <div class="social-section">
            <h3 class="section-title">Соцсети</h3>
            <div class="info-grid">
              <EditableField
                v-model="data.social_profiles.linkedin"
                placeholder="LinkedIn URL"
                icon="🔗"
              />
              <EditableField
                v-model="data.social_profiles.telegram"
                placeholder="Telegram @username"
                icon="✈️"
              />
            </div>
          </div>

          <div class="languages-section">
            <h3 class="section-title">Языки</h3>
            <TagInputField
              v-model="languageNames"
              @update:model-value="updateLanguages"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  layout: "home-layout",
  private: true,
});

// Инициализация структуры данных по умолчанию
const defaultData = () => ({
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

const { data, pending, error } = useFetch("/api/user", {
  // Инициализируем данные по умолчанию
  default: defaultData,
  // Автоматически обновляем реактивную структуру
  transform: (input) => ({
    ...defaultData(),
    ...input,
  }),
});

// Инициализация языков
const languageNames = computed(() => {
  return data.value.languages?.map((lang) => lang.language) || [];
});

function updateLanguages(langs) {
  data.value.languages = langs.map((language) => ({
    language,
    ...data.value.languages.find((l) => l.language === language),
  }));
}

// Education Methods
const addEducation = () => {
  data.value.education.push({
    institution: "",
    degree: "",
    from: "",
    to: "",
  });
};

const removeEducation = (index) => {
  data.value.education.splice(index, 1);
};

// Experience Methods
const addExperience = () => {
  data.value.experience.push({
    company: "",
    role: "",
    from: "",
    to: "",
    description: "",
  });
};

const removeExperience = (index) => {
  data.value.experience.splice(index, 1);
};
</script>

<style scoped>
.profile-card {
  position: relative;
  background: white;
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 800px;
  margin: 2rem auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(0, 0, 0, 0.02);
}

.content {
  position: relative;
  z-index: 1;
}

.header {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.name-fields {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.name-field {
  font-size: 1.8rem;
  font-weight: 600;
}

.contact-badges {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.2rem;
  margin-top: 1.5rem;
}

.main-sections {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.section-group {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section {
  position: relative;
  padding: 1.8rem;
  background: #f8fafc;
  border-radius: 14px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #334155;
  font-size: 1.1rem;
  margin-bottom: 1.2rem;
  padding-bottom: 0.8rem;
  border-bottom: 2px solid #e2e8f0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.2rem;
}

.add-btn {
  width: 100%;
  background: #f1f5f9;
  color: #64748b;
  padding: 1rem;
  border-radius: 10px;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}

.add-btn:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.add-btn span {
  margin-left: 0.5rem;
}

.delete-btn {
  border: 0;
  width: 28px;
  height: 28px;
  padding: 0;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #fecaca;
}

.combined {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 14px;
}

/* Обновленные стили для EditableField */
.editable-field {
  position: relative;
  padding: 0.5rem 0;
}

.view-mode {
  position: relative;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.2s;
  cursor: text;
}

.view-mode:hover {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.view-mode:hover::after {
  content: "✎";
  position: absolute;
  right: 0.8rem;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.6;
  font-size: 0.9em;
}

.edit-mode {
  width: 100%;
  padding: 0.8rem 1.2rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-family: inherit;
  font-size: inherit;
  transition: all 0.2s;
}

.edit-mode:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Адаптация для textarea */
.edit-mode[data-type="textarea"] {
  min-height: 100px;
  resize: vertical;
}
</style>
