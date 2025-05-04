<template>
  <div
    class="card"
    :style="cardStyle"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <div class="card-border"></div>

    <div class="content">
      <div class="header">
        <h3 class="title">{{ resume.title }}</h3>
        <div class="progress" :style="{ '--progress': '100%' }">
          <span>100%</span>
        </div>
      </div>

      <div class="meta">
        <div class="date">
          {{ formatIsoDateTimeReadable(resume.created_at) }}
        </div>
      </div>

      <div class="actions">
        <button class="btn export" @click="handleExport(resume.resume_id)">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="size-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3"
            />
          </svg>
        </button>
        <button class="btn delete" @click="handleDelete(resume.resume_id)">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="size-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  resume: IResumePreview;
}>();

const emit = defineEmits<{ exportResume: number[]; deleteResume: number[] }>();

const isHovered = ref(false);

const cardStyle = computed(() => ({
  "--card-color": props.resume.resume_id % 2 == 0 ? "#d1242d" : "#17837b",
  transform: isHovered.value
    ? "rotate3d(0.5, -0.3, 0, 8deg)"
    : "rotate3d(0, 0, 0, 0deg)",
}));

function handleExport(id: number) {
  emit("exportResume", id);
}

function handleDelete(id: number) {
  emit("deleteResume", id);
}

function formatIsoDateTimeReadable(isoString: string) {
  const date = new Date(isoString);

  if (isNaN(date.getTime())) {
    console.error("Ошибка: Не удалось распознать строку как дату:", isoString);
    return "Неверная дата";
  }

  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");

  return `${day}.${month}.${year} ${hours}:${minutes}:${seconds}`;
}
</script>

<style scoped>
.btn.delete:hover {
  background: #ef4444;
}

.btn.delete:hover svg {
  stroke: white;
}
.card {
  position: relative;
  background: white;
  border-radius: 20px;
  padding: 2rem;
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(0, 0, 0, 0.02);
  overflow: hidden;
}

.card-border {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 2px;
  background: linear-gradient(45deg, var(--card-color) 0%, transparent 80%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.3;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.card:hover {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(0, 0, 0, 0.02);

  .card-border {
    opacity: 0.6;
  }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  max-width: 70%;
  line-height: 1.3;
}

.progress {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: radial-gradient(closest-side, white 79%, transparent 80% 100%),
    conic-gradient(var(--card-color) var(--progress), #e2e8f0 0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--card-color);
}

.meta {
  margin-bottom: 2rem;
}

.template {
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.date {
  font-size: 0.9rem;
  color: #718096;
}

.actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:hover {
  background: var(--card-color);

  svg {
    stroke: white;
  }
}

.btn svg {
  width: 18px;
  height: 18px;
  stroke: var(--card-color);
  transition: stroke 0.2s ease;
}
</style>
