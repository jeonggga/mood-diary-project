<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue";
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
  emotion_desc: string;
  emotion_meaning: string;
  self_talk: string;
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
  emotion_desc: "",
  emotion_meaning: "",
  self_talk: "",
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
  }),
);

const monthTitle = computed(() =>
  format(currentDate.value, "yyyy년 M월", { locale: ko }),
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
    isViewMode.value = true;
  } else {
    form.value = {
      mood_level: 0,
      event: "",
      emotion_desc: "",
      emotion_meaning: "",
      self_talk: "",
    };
    isViewMode.value = false;
    currentStep.value = 1;
    openSection.value = "step1";
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
  // Switch to View Mode
  isViewMode.value = true;
  triggerToast("기록 저장이 완료되었습니다!");
};

onMounted(async () => {
  await loadDiaries();
  selectDate(selectedDate.value);
});

// Get mood info
const selectedMood = computed(() =>
  moodOptions.find((m) => m.id === form.value.mood_level),
);

// Step management
const currentStep = ref(1);
const openSection = ref<"step1" | "step2" | "step3" | "step4" | "all">("step1");
const isEventInputOpen = ref(false);

const formattedSelectedDate = computed(() =>
  format(selectedDate.value, "yyyy.MM.dd"),
);

const canNextStep1 = computed(
  () => form.value.mood_level > 0 && form.value.event.trim().length > 0,
);

const canNextStep2 = computed(() => form.value.emotion_desc.trim().length > 0);
const canNextStep3 = computed(
  () => form.value.emotion_meaning.trim().length > 0,
);

const canSave = computed(
  () =>
    form.value.mood_level &&
    form.value.event.trim() &&
    form.value.emotion_desc.trim() &&
    form.value.emotion_meaning.trim() &&
    form.value.self_talk.trim(),
);

const nextStep = async () => {
  if (currentStep.value === 1 && canNextStep1.value) {
    currentStep.value = 2;
    openSection.value = "step2";
    await nextTick();
    emotionDescInput.value?.focus();
  } else if (currentStep.value === 2 && canNextStep2.value) {
    currentStep.value = 3;
    openSection.value = "step3";
    await nextTick();
    emotionMeaningInput.value?.focus();
  } else if (currentStep.value === 3 && canNextStep3.value) {
    currentStep.value = 4;
    openSection.value = "step4";
    await nextTick();
    selfTalkInput.value?.focus();
  }
};

const toggleSection = (section: "step1" | "step2" | "step3" | "step4") => {
  if (section === "step1") {
    openSection.value = "step1";
  } else if (section === "step2" && currentStep.value >= 2) {
    openSection.value = "step2";
  } else if (section === "step3" && currentStep.value >= 3) {
    openSection.value = "step3";
  } else if (section === "step4" && currentStep.value >= 4) {
    openSection.value = "step4";
  }
};

const toggleEventInput = () => {
  isEventInputOpen.value = !isEventInputOpen.value;
};

// Toast state
const showToast = ref(false);
const toastMessage = ref("");

const triggerToast = (message: string) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 3000); // Hide after 3 seconds
};

// View mode state
const isViewMode = ref(false);

const enableEditMode = () => {
  isViewMode.value = false;
  currentStep.value = 4;
  openSection.value = "all";
  isEventInputOpen.value = true;
};

// Select mood and auto-open event input
const selectMood = async (id: number) => {
  form.value.mood_level = id;
  isEventInputOpen.value = true;
  await nextTick();
  eventInput.value?.focus();
};

// Input refs
const eventInput = ref<HTMLTextAreaElement | null>(null);
const emotionDescInput = ref<HTMLTextAreaElement | null>(null);
const emotionMeaningInput = ref<HTMLTextAreaElement | null>(null);
const selfTalkInput = ref<HTMLTextAreaElement | null>(null);

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
        <!-- RIGHT HEADER: Date & Edit Button -->
        <div
          class="flex justify-between items-center border-b border-gray-100 pb-4"
        >
          <!-- Left aligned date -->
          <h2 class="font-bold text-xl text-gray-800">
            {{ formattedSelectedDate }}
          </h2>
          <button
            v-if="isViewMode"
            @click="enableEditMode"
            class="text-xs text-gray-400 hover:text-black underline"
          >
            수정하기
          </button>
          <div v-else class="w-8"></div>
          <!-- Spacer if no button -->
        </div>

        <!-- READ ONLY VIEW -->
        <div v-if="isViewMode" class="space-y-6 animate-fadeIn">
          <!-- Mood Display -->
          <div class="flex flex-col items-center">
            <img
              :src="selectedMood?.img"
              class="w-24 h-24 object-contain mb-2"
            />
            <p class="font-bold text-xl">{{ selectedMood?.label }}</p>
          </div>

          <!-- Sections -->
          <div class="space-y-4">
            <div class="bg-gray-50 p-4 rounded-xl">
              <p class="text-xs text-gray-400 mb-1 font-bold">
                무슨 일이 있었나요?
              </p>
              <p class="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {{ form.event }}
              </p>
            </div>

            <div class="bg-gray-50 p-4 rounded-xl">
              <p class="text-xs text-gray-400 mb-1 font-bold">
                무슨 감정이 들었나요?
              </p>
              <p class="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {{ form.emotion_desc }}
              </p>
            </div>

            <div class="bg-gray-50 p-4 rounded-xl">
              <p class="text-xs text-gray-400 mb-1 font-bold">감정의 의미</p>
              <p class="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {{ form.emotion_meaning }}
              </p>
            </div>

            <div class="bg-gray-50 p-4 rounded-xl">
              <p class="text-xs text-gray-400 mb-1 font-bold">
                나에게 해주는 말
              </p>
              <p class="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {{ form.self_talk }}
              </p>
            </div>
          </div>
        </div>

        <!-- EDIT FORM -->
        <div v-else>
          <!-- STEP 1 -->
          <div class="pb-4">
            <!-- Header / Summary -->
            <div
              class="flex justify-between items-center py-2 transition-colors"
              :class="{ 'cursor-pointer': openSection !== 'all' }"
              @click="openSection !== 'all' && toggleSection('step1')"
            >
              <div class="flex items-center gap-2">
                <span
                  class="flex items-center justify-center w-6 h-6 rounded-full bg-black text-white text-xs font-bold"
                  >1</span
                >
                <p class="font-bold text-md">오늘 하루 어땠나요?</p>
              </div>
              <!-- Summary & Arrow -->
              <div class="flex items-center gap-4">
                <div
                  v-if="
                    openSection !== 'step1' &&
                    openSection !== 'all' &&
                    form.mood_level
                  "
                  class="flex items-center"
                >
                  <img
                    :src="selectedMood?.img"
                    class="w-8 h-8 object-contain"
                  />
                </div>
                <img
                  v-if="openSection !== 'all'"
                  src="/images/arrow-down.png"
                  class="w-4 h-4 transition-transform duration-300"
                  :class="{
                    'rotate-180':
                      openSection === 'step1' || openSection === 'all',
                  }"
                />
              </div>
            </div>

            <!-- Content -->
            <div
              v-show="openSection === 'step1' || openSection === 'all'"
              class="mt-4 animate-fadeIn"
            >
              <!-- Mood Selection -->
              <div class="flex gap-4 mb-6 justify-center">
                <button
                  v-for="mood in moodOptions"
                  :key="mood.id"
                  @click="selectMood(mood.id)"
                  :class="[
                    'w-16 h-16 rounded-full flex items-center justify-center bg-white transition-all duration-200 hover:scale-110',
                    form.mood_level === mood.id
                      ? 'ring-2 ring-black scale-110'
                      : 'ring-1 ring-gray-200 grayscale hover:grayscale-0',
                  ]"
                >
                  <img
                    :src="mood.img"
                    :alt="mood.label"
                    class="w-12 h-12 object-contain"
                  />
                </button>
              </div>

              <!-- Event Section (Accordion) -->
              <div class="mb-4">
                <div
                  class="flex justify-between items-center bg-gray-50 p-3 rounded-lg transition-colors mb-2"
                  :class="{ 'cursor-pointer': openSection !== 'all' }"
                  @click="openSection !== 'all' && toggleEventInput()"
                >
                  <p class="font-bold text-sm text-gray-700">
                    무슨 일이 있었나요?
                  </p>
                  <img
                    v-if="openSection !== 'all'"
                    src="/images/arrow-down.png"
                    class="w-3 h-3 transition-transform duration-300"
                    :class="{
                      'rotate-180': isEventInputOpen || openSection === 'all',
                    }"
                  />
                </div>
                <div v-show="isEventInputOpen || openSection === 'all'">
                  <textarea
                    ref="eventInput"
                    v-model="form.event"
                    class="w-full h-32 border border-gray-200 rounded-lg p-4 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-black placeholder:text-gray-400"
                    placeholder="사실 위주로 담백하게 기록해 보세요."
                  />
                </div>
              </div>

              <button
                v-if="openSection !== 'all'"
                class="w-full py-3 rounded-xl font-bold transition-all"
                :class="
                  canNextStep1
                    ? 'bg-black text-white hover:bg-gray-800 shadow-md transform active:scale-95'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                "
                :disabled="!canNextStep1"
                @click="nextStep"
              >
                다음
              </button>
            </div>
          </div>

          <!-- STEP 2 (NEW) -->
          <div v-if="currentStep >= 2" class="pb-4">
            <div
              class="flex justify-between items-center py-2 transition-colors"
              :class="{ 'cursor-pointer': openSection !== 'all' }"
              @click="openSection !== 'all' && toggleSection('step2')"
            >
              <div class="flex items-center gap-2">
                <span
                  class="flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold"
                  :class="
                    openSection === 'step2'
                      ? 'bg-black text-white'
                      : 'bg-gray-200 text-gray-500'
                  "
                  >2</span
                >
                <p class="font-bold text-md">무슨 감정이 들었나요?</p>
              </div>
              <img
                v-if="openSection !== 'all'"
                src="/images/arrow-down.png"
                class="w-4 h-4 transition-transform duration-300"
                :class="{
                  'rotate-180': openSection === 'step2',
                }"
              />
            </div>

            <div
              v-show="openSection === 'step2' || openSection === 'all'"
              class="mt-4 animate-fadeIn"
            >
              <textarea
                ref="emotionDescInput"
                v-model="form.emotion_desc"
                class="w-full h-32 border border-gray-200 rounded-lg p-4 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-black placeholder:text-gray-400 mb-4"
                placeholder="그때 느꼈던 감정을 구체적인 단어로 표현해 보세요. (예: 억울함, 서운함, 홀가분함)"
              />
              <button
                v-if="openSection !== 'all'"
                class="w-full py-3 rounded-xl font-bold transition-all"
                :class="
                  canNextStep2
                    ? 'bg-black text-white hover:bg-gray-800 shadow-md transform active:scale-95'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                "
                :disabled="!canNextStep2"
                @click="nextStep"
              >
                다음
              </button>
            </div>
          </div>

          <!-- STEP 3 (OLD Step 2) -->
          <div v-if="currentStep >= 3" class="pb-4">
            <div
              class="flex justify-between items-center py-2 transition-colors"
              :class="{ 'cursor-pointer': openSection !== 'all' }"
              @click="openSection !== 'all' && toggleSection('step3')"
            >
              <div class="flex items-center gap-2">
                <span
                  class="flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold"
                  :class="
                    openSection === 'step3'
                      ? 'bg-black text-white'
                      : 'bg-gray-200 text-gray-500'
                  "
                  >3</span
                >
                <p class="font-bold text-md">더 깊게 자신의 감정을 써보세요</p>
              </div>
              <img
                v-if="openSection !== 'all'"
                src="/images/arrow-down.png"
                class="w-4 h-4 transition-transform duration-300"
                :class="{
                  'rotate-180': openSection === 'step3',
                }"
              />
            </div>

            <div
              v-show="openSection === 'step3' || openSection === 'all'"
              class="mt-4 animate-fadeIn"
            >
              <textarea
                ref="emotionMeaningInput"
                v-model="form.emotion_meaning"
                class="w-full h-32 border border-gray-200 rounded-lg p-4 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-black placeholder:text-gray-400 mb-4"
                placeholder="이 감정이 나에게 어떤 의미인지, 왜 그런 마음이 들었는지 적어보세요."
              />
              <button
                v-if="openSection !== 'all'"
                class="w-full py-3 rounded-xl font-bold transition-all"
                :class="
                  canNextStep3
                    ? 'bg-black text-white hover:bg-gray-800 shadow-md transform active:scale-95'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                "
                :disabled="!canNextStep3"
                @click="nextStep"
              >
                다음
              </button>
            </div>
          </div>

          <!-- STEP 4 (OLD Step 3) -->
          <div v-if="currentStep >= 4" class="pb-4">
            <div
              class="flex justify-between items-center py-2 transition-colors"
              :class="{ 'cursor-pointer': openSection !== 'all' }"
              @click="openSection !== 'all' && toggleSection('step4')"
            >
              <div class="flex items-center gap-2">
                <span
                  class="flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold"
                  :class="
                    openSection === 'step4'
                      ? 'bg-black text-white'
                      : 'bg-gray-200 text-gray-500'
                  "
                  >4</span
                >
                <p class="font-bold text-md">나에게 따뜻한 위로를 써보세요</p>
              </div>
              <img
                v-if="openSection !== 'all'"
                src="/images/arrow-down.png"
                class="w-4 h-4 transition-transform duration-300"
                :class="{
                  'rotate-180': openSection === 'step4',
                }"
              />
            </div>

            <div
              v-show="openSection === 'step4' || openSection === 'all'"
              class="mt-4 animate-fadeIn"
            >
              <textarea
                ref="selfTalkInput"
                v-model="form.self_talk"
                class="w-full h-32 border border-gray-200 rounded-lg p-4 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-black placeholder:text-gray-400 mb-4"
                placeholder="자신에게 해주고 싶은 따뜻한 말 한마디를 적어보세요."
              />
              <button
                class="w-full py-3 rounded-xl font-bold transition-all"
                :class="
                  canSave
                    ? 'bg-black text-white hover:bg-gray-800 shadow-md transform active:scale-95'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                "
                :disabled="!canSave"
                @click="saveDiary"
              >
                기록 저장하기
              </button>
            </div>
          </div>
        </div>
        <!-- End of Edit Form -->
      </div>
    </div>

    <!-- Toast Notification -->
    <div
      v-if="showToast"
      class="fixed top-20 left-1/2 transform -translate-x-1/2 bg-black text-white px-6 py-3 rounded-full shadow-lg transition-all duration-300 z-50 animate-fadeIn"
    >
      {{ toastMessage }}
    </div>
  </div>
</template>
