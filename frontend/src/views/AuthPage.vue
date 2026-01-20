<script setup lang="ts">
// ------------------------------------------------------------------
// [AuthPage.vue] 인증 페이지 (로그인 & 회원가입)
// ------------------------------------------------------------------
// Vue 3 Composition API를 사용하여 setup 스크립트를 작성합니다.
import { ref, nextTick } from "vue";

// 우리가 정의한 Pinia 스토어(auth.ts)를 가져옵니다.
// 이 스토어 안에는 로그인(login), 회원가입(register) 같은 실제 서버 통신 로직이 들어있습니다.
import { useAuthStore } from "../stores/auth";

// ------------------------------------------------------------------
// 1. 상태(State) 변수 정의
// ------------------------------------------------------------------

// 현재 화면이 '로그인' 모드인지, '회원가입' 모드인지 구분하는 플래그입니다.
// true: 로그인 화면 / false: 회원가입 화면
const isLogin = ref(true);

// 사용자가 입력 폼에 작성하는 아이디와 비밀번호를 연결(binding)할 변수입니다.
// ref("")로 초기화하여 빈 문자열로 시작합니다.
const username = ref("");
const password = ref("");

// 로그인/회원가입 실패 시 사용자에게 보여줄 에러 메시지를 담는 변수입니다.
// (현재는 Toast 메시지를 주로 사용하므로 보조적인 용도로 쓰입니다.)
const errorMsg = ref("");

// useAuthStore()를 호출하여 auth 스토어 인스턴스를 생성합니다.
// 이 객체를 통해 store에 정의된 액션(함수)들을 실행할 수 있습니다.
const authStore = useAuthStore();

// ------------------------------------------------------------------
// 2. Toast(알림 메시지) 관련 상태
// ------------------------------------------------------------------
// 토스트 메시지를 화면에 보여줄지 여부를 결정합니다. (true: 보임, false: 숨김)
const showToast = ref(false);
// 토스트에 띄울 텍스트 내용을 저장합니다.
const toastMessage = ref("");

// ------------------------------------------------------------------
// 3. 이벤트 핸들러 (함수)
// ------------------------------------------------------------------

/**
 * 폼 제출(Submit) 버튼을 눌렀을 때 실행되는 메인 함수입니다.
 * - 로그인 모드이면: authStore.login() 실행
 * - 회원가입 모드이면: authStore.register() 실행
 * - 결과에 따라 성공 시 화면 이동, 실패 시 Toast 알림을 띄웁니다.
 */
const triggerToast = async (message: string) => {
  // 기존 타이머가 있다면 취소 (중복 실행 방지)
  if (toastTimer.value) {
    clearTimeout(toastTimer.value);
  }

  // 강제로 껐다가 켜서 애니메이션 재실행 유도
  showToast.value = false;
  await nextTick();

  toastMessage.value = message;
  showToast.value = true;

  // 4초 뒤에 닫기
  toastTimer.value = setTimeout(() => {
    showToast.value = false;
  }, 4000);
};

// 타이머 ID 저장을 위한 ref
const toastTimer = ref<any>(null);

/**
 * 폼 제출(Submit) 버튼을 눌렀을 때 실행되는 메인 함수입니다.
 * - 로그인 모드이면: authStore.login() 실행
 * - 회원가입 모드이면: authStore.register() 실행
 * - 결과에 따라 성공 시 화면 이동, 실패 시 Toast 알림을 띄웁니다.
 */
const handleSubmit = async () => {
  // 이전의 에러 상태 초기화
  errorMsg.value = "";
  // 주의: 여기서 showToast.value = false; 를 호출하면
  // 연속 클릭 시 토스트가 깜빡이거나 사라질 수 있으므로 제거합니다.
  // triggerToast 내부에서 처리합니다.

  // [CASE 1] 로그인 모드일 때
  if (isLogin.value) {
    // await 키워드를 사용하여 비동기 통신(서버 응답)이 끝날 때까지 기다립니다.
    // authStore.login 함수는 내부적으로 axios를 통해 백엔드로 요청을 보냅니다.
    const success = await authStore.login(username.value, password.value);

    // 로그인 실패 시 (success가 false일 때)
    if (!success) {
      triggerToast("아이디, 비밀번호가 틀립니다.");
    }
  }
  // [CASE 2] 회원가입 모드일 때
  else {
    const success = await authStore.register(username.value, password.value);

    if (success) {
      // 회원가입 성공 시 브라우저 기본 알림창(alert)을 띄우고
      // 로그인 화면으로 모드를 전환하여 바로 로그인할 수 있게 유도합니다.
      alert("가입 완료! 로그인 해주세요.");
      isLogin.value = true;
    } else {
      // 회원가입 실패 시 (예: 중복된 아이디 등) 에러 메시지를 설정합니다.
      errorMsg.value = "회원가입 실패. 이미 존재하는 아이디일 수 있습니다.";
    }
  }
};
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center">
    <div class="relative w-full max-w-sm">
      <!-- 이모지 영역: 카드 위에 살짝 겹치게 -->
      <div
        class="flex justify-center space-x-2 absolute -top-14 left-1/2 -translate-x-1/2 z-0"
      >
        <img
          src="/images/emoji_img.png"
          alt="Emoji"
          class="w-auto h-auto rounded-none object-cover scale-130"
        />
      </div>
      <!-- 로그인 카드 -->
      <div
        class="bg-white rounded-2xl p-8 pt-12 flex flex-col items-center relative z-0 border border-gray-200"
      >
        <!-- 제목 -->
        <h2 class="font-bold mb-12 tracking-tight text-black text-center">
          <span class="text-2xl" v-if="isLogin">MOOD DIARY</span>
          <span class="text-xl" v-else>
            새로운 여정을 위해<br />회원가입을 해주세요!
          </span>
        </h2>

        <!-- 입력 폼 -->
        <form class="w-full space-y-4" @submit.prevent="handleSubmit">
          <input
            v-model="username"
            id="username"
            name="username"
            type="text"
            required
            placeholder="아이디 입력"
            class="w-full px-4 py-3 rounded-md bg-gray-100 text-gray-600 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black-400"
          />
          <input
            v-model="password"
            id="password"
            name="password"
            type="password"
            required
            placeholder="비밀번호 입력"
            class="w-full px-4 py-3 rounded-md bg-gray-100 text-gray-600 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black-400"
          />
          <button
            type="submit"
            class="w-full bg-black text-white py-3 rounded-md hover:bg-gray-900 transition-colors font-semibold"
          >
            {{ isLogin ? "로그인" : "회원가입" }}
          </button>
        </form>

        <!-- 전환 버튼 -->
        <div class="mt-4 text-center">
          <button
            @click="isLogin = !isLogin"
            class="text-sm font-medium text-stone-600 hover:text-stone-900 transition-colors underline pt-4"
          >
            {{
              isLogin
                ? "계정이 없으신가요? 회원가입"
                : "이미 계정이 있으신가요? 로그인"
            }}
          </button>
        </div>

        <!-- 하단 카피라이트 -->
        <div class="mt-18 w-full flex justify-between text-xs text-gray-400">
          <span>© 2026 Slyeee. All rights reserved.</span>
          <span>Design by Jeonggga</span>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div
      v-if="showToast"
      class="fixed top-20 left-1/2 transform -translate-x-1/2 bg-black text-white px-6 py-3 rounded-full shadow-lg z-50 animate-fadeIn"
    >
      {{ toastMessage }}
    </div>
  </div>
</template>
