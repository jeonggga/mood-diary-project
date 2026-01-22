<script setup lang="ts">
// [DiaryPage.vue] 메인 일기장 페이지
// - 달력을 보여주고, 날짜별 감정 일기를 작성/조회하는 핵심 기능을 담당합니다.

// Vue 핵심 기능들을 가져옵니다.
// - ref: 반응형 데이터 (값이 바뀌면 화면 갱신)
// - computed: 계산된 속성 (다른 데이터가 바뀌면 자동으로 다시 계산됨)
// - onMounted: 컴포넌트가 화면에 처음 나타날 때 실행되는 라이프사이클 훅
// - nextTick: 화면 갱신이 완료된 직후에 실행할 로직을 위해 사용
import { ref, computed, onMounted, nextTick } from "vue";
import { useAuthStore } from "../stores/auth";
import api from "../api";
import { LogOut, ChevronLeft, ChevronRight } from "lucide-vue-next"; // 아이콘들
// 날짜 관련 라이브러리 (date-fns)
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
import { ko } from "date-fns/locale"; // 한국어 날짜 포맷 지원

// ------------------------------------------------------------------
// 1. 타입 정의 (TypeScript Interface)
// ------------------------------------------------------------------
// 일기 데이터의 구조를 정의합니다. 백엔드 DB 구조와 일치해야 합니다.
interface Diary {
  id: number;
  event: string; // 있었던 일 (사실)
  mood_level: number; // 감정 점수/ID (1~5)
  emotion_desc: string; // 감정 단어/묘사
  emotion_meaning: string; // 감정의 의미
  self_talk: string; // 스스로에게 해주는 말 (위로)
  created_at: string; // 작성일 (ISO String)
}

// ------------------------------------------------------------------
// 2. 상태(State) 변수
// ------------------------------------------------------------------
const authStore = useAuthStore();

// 불러온 일기 목록 전체를 저장하는 배열
const diaries = ref<Diary[]>([]);

// 달력에서 현재 보여주고 있는 '기준 날짜' (월 단위 이동 시 사용)
const currentDate = ref(new Date());

// 사용자가 클릭해서 선택한 '특정 날짜' (일기 작성/조회 대상)
const selectedDate = ref(new Date());

// 현재 작성 중인지(로딩/저장 중) 상태 (중복 클릭 방지 등)
const isWriting = ref(false);

// 일기 작성 폼 데이터 (v-model로 입력창과 연결됨)
const form = ref({
  mood_level: 0,
  event: "",
  emotion_desc: "",
  emotion_meaning: "",
  self_talk: "",
});

// 제공되는 감정 이모티콘 옵션들
const moodOptions = [
  { id: 1, label: "행복해", img: "/images/emoji_1.png" },
  { id: 2, label: "평온해", img: "/images/emoji_2.png" },
  { id: 3, label: "그저그래", img: "/images/emoji_3.png" },
  { id: 4, label: "우울해", img: "/images/emoji_4.png" },
  { id: 5, label: "화나", img: "/images/emoji_5.png" },
];

// ------------------------------------------------------------------
// 3. 계산된 속성 (Computed) - 달력 로직
// ------------------------------------------------------------------

// 현재 보고 있는 달(Month)의 모든 날짜 리스트를 생성합니다.
// 예: 2024년 1월이면 1월 1일 ~ 1월 31일까지의 Date 객체 배열을 만듭니다.
const calendarDays = computed(() =>
  eachDayOfInterval({
    start: startOfMonth(currentDate.value),
    end: endOfMonth(currentDate.value),
  }),
);

// 달력 상단에 표시할 제목 (예: "2024년 1월")
const monthTitle = computed(() =>
  format(currentDate.value, "yyyy년 M월", { locale: ko }),
);

// ------------------------------------------------------------------
// 4. 메서드 (함수) - 일기 데이터 처리
// ------------------------------------------------------------------

// [조회] 특정 날짜에 작성된 일기를 diaries 배열에서 찾아 반환합니다.
const getDiaryForDate = (date: Date) =>
  diaries.value.find((d) => isSameDay(parseISO(d.created_at), date));

// [선택] 달력에서 날짜를 클릭했을 때 실행됩니다.
const selectDate = (date: Date) => {
  selectedDate.value = date;
  const diary = getDiaryForDate(date);

  if (diary) {
    // 해당 날짜에 일기가 이미 있다면 -> 내용을 폼에 채우고 '조회 모드'로 설정
    form.value = { ...diary }; // 객체 복사
    isViewMode.value = true;
  } else {
    // 일기가 없다면 -> 폼을 초기화하고 '작성 모드'로 설정 (Step 1부터 시작)
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

// [API] 서버에서 모든 일기 목록을 가져옵니다.
const loadDiaries = async () => {
  const res = await api.get("/diaries");
  diaries.value = res.data;
};

// [API] 작성한 일기를 서버에 저장합니다.
const saveDiary = async () => {
  await api.post("/diaries", {
    ...form.value,
    // 선택된 날짜를 ISO 문자열 포맷으로 변환해서 전송
    created_at: selectedDate.value.toISOString(),
  });
  isWriting.value = false;

  // 저장 후 목록을 다시 불러와서 화면(달력의 이모티콘 등)을 갱신합니다.
  loadDiaries();
  // 저장 완료 후 '조회 모드'로 전환하여 작성 내용을 보여줍니다.
  isViewMode.value = true;
  // 저장 완료 안내 Toast 메시지 띄우기
  triggerToast("기록 저장이 완료되었습니다!");
};

// [초기화] 컴포넌트 마운트 시 실행
onMounted(async () => {
  await loadDiaries(); // 데이터 불러오기
  selectDate(selectedDate.value); // 오늘 날짜 선택 상태로 시작
});

// 선택된 감정 ID에 해당하는 이모티콘/라벨 정보를 찾습니다. (상세 조회용)
const selectedMood = computed(() =>
  moodOptions.find((m) => m.id === form.value.mood_level),
);

// ------------------------------------------------------------------
// 5. 단계별 작성(Step) 관리 로직
// ------------------------------------------------------------------
// 현재 작성 중인 단계 (1~4)
const currentStep = ref(1);

// 아코디언 메뉴 중 열려있는 섹션 (step1, step2, ... all)
const openSection = ref<"step1" | "step2" | "step3" | "step4" | "all">("step1");

// Step 1에서 감정 선택 후 텍스트 입력창이 열려있는지 여부
const isEventInputOpen = ref(false);

// 선택된 날짜를 "YYYY.MM.DD" 형식으로 포맷팅 (우측 헤더 표시용)
const formattedSelectedDate = computed(() =>
  format(selectedDate.value, "yyyy.MM.dd"),
);

// [유효성 검사] 각 단계별로 '다음' 버튼 활성화 조건
// Step 1: 감정을 선택하고 + 사건 내용을 입력했는지
const canNextStep1 = computed(
  () => form.value.mood_level > 0 && form.value.event.trim().length > 0,
);
// Step 2, 3: 내용을 입력했는지
const canNextStep2 = computed(() => form.value.emotion_desc.trim().length > 0);
const canNextStep3 = computed(
  () => form.value.emotion_meaning.trim().length > 0,
);

// 전체 저장 가능 여부 (모든 필드가 채워졌는지)
const canSave = computed(
  () =>
    form.value.mood_level &&
    form.value.event.trim() &&
    form.value.emotion_desc.trim() &&
    form.value.emotion_meaning.trim() &&
    form.value.self_talk.trim(),
);

// [다음] 버튼 클릭 시 다음 단계로 이동하고, 해당 입력창에 포커스를 줍니다.
const nextStep = async () => {
  if (currentStep.value === 1 && canNextStep1.value) {
    currentStep.value = 2; // 단계 증가
    openSection.value = "step2"; // 아코디언 펼치기
    await nextTick(); // 화면 갱신 기다리기
    emotionDescInput.value?.focus(); // 입력창 포커스
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

// 아코디언 헤더 클릭 시 섹션을 토글하는 함수
const toggleSection = (section: "step1" | "step2" | "step3" | "step4") => {
  // 이미 진행된 단계(currentStep)까지만 열 수 있도록 제한
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

// ------------------------------------------------------------------
// 6. UI 상태 및 헬퍼
// ------------------------------------------------------------------

// Toast(저장 완료 알림) 관련 상태
const showToast = ref(false);
const toastMessage = ref("");

// Toast를 띄우고 3초 뒤에 끄는 헬퍼 함수
const triggerToast = (message: string) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 3000); // 3초 후 숨김
};

// [조회 모드] vs [편집 모드] 플래그
// true: 이미 작성된 일기를 볼 때 / false: 새로 작성하거나 수정할 때
const isViewMode = ref(false);
// [수정하기] 버튼 클릭 시 '편집 모드'로 진입
const enableEditMode = () => {
  isViewMode.value = false;
  currentStep.value = 4; // 모든 단계를 완료한 상태로 간주
  openSection.value = "all"; // 모든 섹션을 펼침
  isEventInputOpen.value = true;
};

// 감정 이모티콘 선택 시 처리
const selectMood = async (id: number) => {
  form.value.mood_level = id;
  isEventInputOpen.value = true; // 텍스트 입력창 열기
  await nextTick();
  eventInput.value?.focus(); // 텍스트 입력창으로 커서 이동
};

// DOM 요소 접근을 위한 Refs (focus 주기 위해 사용)
const eventInput = ref<HTMLTextAreaElement | null>(null);
const emotionDescInput = ref<HTMLTextAreaElement | null>(null);
const emotionMeaningInput = ref<HTMLTextAreaElement | null>(null);
const selfTalkInput = ref<HTMLTextAreaElement | null>(null);

// 달력 날짜 칸에 표시할 이모티콘을 찾습니다.
const getDiaryMood = (date: Date) => {
  const diary = getDiaryForDate(date);
  if (!diary) return null;
  // 일기가 있으면 해당 감정 ID에 맞는 이모티콘 정보를 반환
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
            class="p-1 text-gray-400 hover:text-black cursor-pointer"
          >
            <ChevronLeft />
          </button>
          <h2 class="font-bold text-lg">{{ monthTitle }}</h2>
          <button
            @click="currentDate = addMonths(currentDate, 1)"
            class="p-1 text-gray-400 hover:text-black cursor-pointer"
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
        class="w-[40%] bg-white rounded-xl border border-gray-200 flex flex-col h-[760px]"
      >
        <!-- RIGHT HEADER: Date & Edit Button -->
        <div
          class="flex justify-between items-center border-b border-gray-100 p-6 pb-4 shrink-0"
        >
          <!-- Left aligned date -->
          <h2 class="font-bold text-xl text-gray-800">
            {{ formattedSelectedDate }}
          </h2>
          <button
            v-if="isViewMode"
            @click="enableEditMode"
            class="text-xs text-gray-400 hover:text-black underline cursor-pointer"
          >
            수정하기
          </button>
          <div v-else class="w-8"></div>
          <!-- Spacer if no button -->
        </div>

        <!-- SCROLLABLE CONTENT AREA -->
        <div class="p-6 pt-4 overflow-y-auto flex-1 custom-scrollbar space-y-4">
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
                    class="flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold"
                    :class="
                      openSection === 'step1'
                        ? 'bg-black text-white'
                        : 'bg-gray-200 text-gray-500'
                    "
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
                      'rotate-180': openSection === 'step1',
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
                      'w-16 h-16 rounded-full flex items-center justify-center bg-white transition-all duration-200 hover:scale-110 cursor-pointer',
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
                        'rotate-180': isEventInputOpen,
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
                  v-if="openSection !== 'all' && currentStep === 1"
                  class="w-full py-3 rounded-xl font-bold transition-all"
                  :class="
                    canNextStep1
                      ? 'bg-black text-white hover:bg-gray-800 shadow-md transform active:scale-95 cursor-pointer'
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
                  v-if="openSection !== 'all' && currentStep === 2"
                  class="w-full py-3 rounded-xl font-bold transition-all"
                  :class="
                    canNextStep2
                      ? 'bg-black text-white hover:bg-gray-800 shadow-md transform active:scale-95 cursor-pointer'
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
                  <p class="font-bold text-md">
                    더 깊게 자신의 감정을 써보세요
                  </p>
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
                  v-if="openSection !== 'all' && currentStep === 3"
                  class="w-full py-3 rounded-xl font-bold transition-all"
                  :class="
                    canNextStep3
                      ? 'bg-black text-white hover:bg-gray-800 shadow-md transform active:scale-95 cursor-pointer'
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
                      ? 'bg-black text-white hover:bg-gray-800 shadow-md transform active:scale-95 cursor-pointer'
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

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 20px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #d1d5db;
}
</style>
