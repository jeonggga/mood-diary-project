<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import api from "../api";
import { LogOut, ChevronLeft, ChevronRight } from "lucide-vue-next";
import {
  format,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isSameDay,
  addMonths,
  subMonths,
  parseISO,
  isToday,
} from "date-fns";
import { ko } from "date-fns/locale";

// Diary interface
interface Diary {
  id: number;
  event: string;
  mood_level: number;
  deepFeeling?: string;
  comforting?: string;
  created_at: string;
}

const authStore = useAuthStore();
const diaries = ref<Diary[]>([]);
const currentDate = ref(new Date());
const selectedDate = ref(new Date());
const isWriting = ref(false);

const form = ref({
  mood_level: 0,
  event: "",
  deepFeeling: "",
  comforting: "",
});

const moodOptions = [
  { id: 1, label: "행복해", img: "/images/emoji_1.png" },
  { id: 2, label: "평온해", img: "/images/emoji_2.png" },
  { id: 3, label: "그저그래", img: "/images/emoji_3.png" },
  { id: 4, label: "우울해", img: "/images/emoji_4.png" },
  { id: 5, label: "화나", img: "/images/emoji_5.png" },
];

// Calendar calculations
const calendarDays = computed(() =>
  eachDayOfInterval({
    start: startOfMonth(currentDate.value),
    end: endOfMonth(currentDate.value),
  })
);

const monthTitle = computed(() =>
  format(currentDate.value, "yyyy년 M월", { locale: ko })
);

// Get diary for a date
const getDiaryForDate = (date: Date) =>
  diaries.value.find((d) => isSameDay(parseISO(d.created_at), date));

// When a date is selected
const selectDate = (date: Date) => {
  selectedDate.value = date;
  const diary = getDiaryForDate(date);
  if (diary) {
    form.value = { ...diary };
  } else {
    form.value = {
      mood_level: 0,
      event: "",
      deepFeeling: "",
      comforting: "",
    };
  }
};

// Load diaries from API
const loadDiaries = async () => {
  const res = await api.get("/diaries");
  diaries.value = res.data;
};

const saveDiary = async () => {
  await api.post("/diaries", {
    ...form.value,
    created_at: selectedDate.value.toISOString(),
  });
  isWriting.value = false;
  loadDiaries();
};

onMounted(loadDiaries);

// Get mood info
const selectedMood = computed(() =>
  moodOptions.find((m) => m.id === form.value.mood_level)
);

// Step management
const currentStep = ref(1);

const accordionOpen = ref({
  step1: false,
  step2: false,
  step3: false,
});

const canNextStep1 = computed(
  () => form.value.mood_level > 0 && form.value.event.trim().length > 0
);

const canNextStep2 = computed(() => form.value.deepFeeling.trim().length > 0);

const canSave = computed(
  () =>
    form.value.mood_level &&
    form.value.event.trim() &&
    form.value.deepFeeling.trim() &&
    form.value.comforting.trim()
);

const nextStep = () => {
  if (currentStep.value === 1 && canNextStep1.value) {
    currentStep.value = 2;
    accordionOpen.value.step1 = true; // Step1 접기
    accordionOpen.value.step2 = true; // Step2 열기
  } else if (currentStep.value === 2 && canNextStep2.value) {
    currentStep.value = 3;
    accordionOpen.value.step2 = true;
    accordionOpen.value.step3 = true;
  }
};

const toggleAccordion = (step: "step1" | "step2" | "step3") => {
  accordionOpen.value[step] = !accordionOpen.value[step];
};

// Get diary mood for calendar
const getDiaryMood = (date: Date) => {
  const diary = getDiaryForDate(date);
  if (!diary) return null;
  return moodOptions.find((m) => m.id === diary.mood_level) || null;
};
</script>

<template>
  <div class="min-h-screen">
    <!-- HEADER -->
    <header
      class="h-14 bg-transparent border border-gray-200 flex items-center justify-between px-6"
    >
      <h1 class="font-bold tracking-wide">MOOD DIARY</h1>
      <button
        @click="authStore.logout()"
        class="flex items-center gap-2 text-sm text-gray-500 hover:text-black"
      >
        <LogOut class="w-4 h-4" /> 로그아웃
      </button>
    </header>

    <div
      class="max-w-7xl mx-auto mt-6 mb-6 rounded-xl flex min-h-[600px] gap-4"
    >
      <!-- LEFT CALENDAR -->
      <div class="w-6/10 p-6 bg-white rounded-xl border border-gray-200">
        <div class="flex items-center justify-between mb-4">
          <button
            @click="currentDate = subMonths(currentDate, 1)"
            class="p-1 text-gray-400 hover:text-black"
          >
            <ChevronLeft />
          </button>
          <h2 class="font-bold text-lg">{{ monthTitle }}</h2>
          <button
            @click="currentDate = addMonths(currentDate, 1)"
            class="p-1 text-gray-400 hover:text-black"
          >
            <ChevronRight />
          </button>
        </div>

        <!-- Calendar grid -->
        <div class="grid grid-cols-7 border border-stone-200 text-sm">
          <div
            v-for="d in ['일', '월', '화', '수', '목', '금', '토']"
            :key="d"
            class="h-10 flex items-center justify-center text-xs text-stone-400 border-b border-stone-200"
          >
            {{ d }}
          </div>

          <!-- empty days -->
          <div
            v-for="n in startOfMonth(currentDate).getDay()"
            :key="'empty-' + n"
            class="h-24 border border-stone-200 p-2"
          />

          <div
            v-for="date in calendarDays"
            :key="date.toString()"
            @click="selectDate(date)"
            :class="[
              'relative h-24 border cursor-pointer p-2',
              isSameDay(date, selectedDate)
                ? 'border-black bg-black text-white font-bold'
                : 'border-stone-200',
            ]"
          >
            <span
              :class="
                isSameDay(date, selectedDate)
                  ? 'text-white font-bold'
                  : 'text-stone-600 font-normal'
              "
              >{{ format(date, "d") }}</span
            >
            <span
              v-if="isToday(date)"
              class="absolute top-2 right-2 text-[10px] px-2 py-0.5 rounded-full bg-stone-100 text-stone-500"
              >오늘</span
            >

            <div
              v-if="getDiaryMood(date)"
              class="absolute inset-0 flex items-center justify-center"
            >
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center bg-white"
              >
                <img
                  :src="getDiaryMood(date)?.img"
                  :alt="getDiaryMood(date)?.label"
                  class="w-14 h-14 object-contain"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT / Diary Steps -->
      <div
        class="w-[40%] p-6 bg-white rounded-xl border border-gray-200 space-y-4"
      >
        <!-- STEP 1 (항상 노출) -->
        <div>
          <p class="font-bold mb-2">오늘 하루 어땠나요?</p>
          <div class="flex gap-4 mb-4">
            <button
              v-for="mood in moodOptions"
              :key="mood.id"
              @click="form.mood_level = mood.id"
              :class="[
                'w-20 h-20 rounded-full flex items-center justify-center bg-white transition-all duration-150 hover:scale-110',
                form.mood_level === mood.id
                  ? 'ring-2 ring-black'
                  : 'ring-1 ring-gray-200',
              ]"
            >
              <img
                :src="mood.img"
                :alt="mood.label"
                class="w-14 h-14 object-contain"
              />
            </button>
          </div>

          <p class="font-bold mb-2">무슨 일이 있었나요?</p>
          <textarea
            v-model="form.event"
            class="w-full h-32 border border-gray-200 rounded-lg p-4 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-black placeholder:text-gray-400"
            placeholder="사실 위주로 담백하게 기록해 보세요."
          />

          <button
            class="mt-2 px-6 py-2 rounded-md transition"
            :class="
              canNextStep1
                ? 'bg-black text-white hover:bg-gray-900'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            "
            :disabled="!canNextStep1"
            @click="nextStep"
          >
            다음
          </button>
        </div>

        <!-- STEP1 아코디언 요약 -->
        <div v-if="accordionOpen.step1 && currentStep > 1">
          <div
            class="flex justify-between items-center cursor-pointer bg-gray-50 p-2 rounded"
            @click="toggleAccordion('step1')"
          >
            <p class="font-bold">오늘 하루 어땠나요? + 무슨 일이 있었나요?</p>
            <div class="flex items-center gap-2">
              <img
                v-if="form.mood_level"
                :src="selectedMood?.img"
                class="w-6 h-6"
              />
              <img
                src="/images/arrow-down.png"
                class="w-4 h-4 transition-transform"
                :class="{ 'rotate-180': accordionOpen.step1 }"
              />
            </div>
          </div>
          <div
            v-if="accordionOpen.step1"
            class="mt-2 p-2 bg-white rounded border border-gray-200"
          >
            <p class="mb-1"><strong>감정:</strong> {{ selectedMood?.label }}</p>
            <p><strong>사건:</strong> {{ form.event }}</p>
          </div>
        </div>

        <!-- STEP2 -->
        <div v-if="currentStep >= 2">
          <div
            class="flex justify-between items-center cursor-pointer"
            @click="toggleAccordion('step2')"
          >
            <p class="font-bold">더 깊게 자신의 감정을 써보세요</p>
            <img
              src="/images/arrow-down.png"
              class="w-4 h-4 transition-transform"
              :class="{ 'rotate-180': accordionOpen.step2 }"
            />
          </div>
          <div v-if="accordionOpen.step2" class="mt-2">
            <textarea
              v-model="form.deepFeeling"
              class="w-full h-32 border border-gray-200 rounded-lg p-4 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-black placeholder:text-gray-400"
              placeholder="마음속 깊은 감정을 자유롭게 기록해 보세요."
            />
            <button
              class="mt-2 px-6 py-2 rounded-md transition"
              :class="
                canNextStep2
                  ? 'bg-black text-white hover:bg-gray-900'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              "
              :disabled="!canNextStep2"
              @click="nextStep"
            >
              다음
            </button>
          </div>
        </div>

        <!-- STEP3 -->
        <div v-if="currentStep >= 3">
          <div
            class="flex justify-between items-center cursor-pointer"
            @click="toggleAccordion('step3')"
          >
            <p class="font-bold">나에게 따뜻한 위로를 써보세요</p>
            <img
              src="/images/arrow-down.png"
              class="w-4 h-4 transition-transform"
              :class="{ 'rotate-180': accordionOpen.step3 }"
            />
          </div>
          <div v-if="accordionOpen.step3" class="mt-2">
            <textarea
              v-model="form.comforting"
              class="w-full h-32 border border-gray-200 rounded-lg p-4 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-black placeholder:text-gray-400"
              placeholder="자신에게 위로와 격려를 적어보세요."
            />
            <button
              class="mt-2 px-6 py-2 rounded-md transition"
              :class="
                canSave
                  ? 'bg-black text-white hover:bg-gray-900'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              "
              :disabled="!canSave"
              @click="saveDiary"
            >
              기록 저장하기
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
