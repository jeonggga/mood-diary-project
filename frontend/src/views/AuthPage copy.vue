<script setup lang="ts">
// Vue에서 필요한 기능을 가져옵니다.
// ref: 데이터가 바뀌면 화면도 자동으로 바뀌게 해주는 '반응형 변수'를 만들 때 사용합니다.
import { ref } from "vue";

// 우리가 만든 인증(로그인/회원가입) 관련 저장소(store)를 가져옵니다.
import { useAuthStore } from "../stores/auth";

// ------------------------------------------------------------------
// 상태 변수 정의 (화면에서 사용할 데이터들)
// ------------------------------------------------------------------

// 현재 화면이 '로그인' 모드인지 '회원가입' 모드인지 결정합니다.
// true면 로그인 화면, false면 회원가입 화면을 보여줍니다.
const isLogin = ref(true);

// 사용자가 입력한 아이디와 비밀번호를 저장할 변수입니다.
// ref('')로 초기값은 빈 문자열로 시작합니다.
const username = ref("");
const password = ref("");

// 에러가 발생했을 때 사용자에게 보여줄 메시지입니다.
const errorMsg = ref("");

// Pinia로 만든 authStore를 사용하기 위해 변수에 담습니다. (로그인, 회원가입 함수가 들어있어요)
const authStore = useAuthStore();

/**
 * 폼 제출 버튼을 눌렀을 때 실행되는 함수입니다.
 * async/await: 서버와 통신하는 작업은 시간이 걸리므로, 끝날 때까지 기다렸다가 다음 줄을 실행합니다.
 */
const handleSubmit = async () => {
  // 새로운 요청을 보내기 전에 이전에 떠있던 에러 메시지를 지워줍니다.
  errorMsg.value = "";

  // 현재 모드에 따라 로그인 또는 회원가입을 진행합니다.
  if (isLogin.value) {
    // [로그인 모드일 때]
    // authStore에 있는 login 함수를 실행하고 결과를 기다립니다.
    const success = await authStore.login(username.value, password.value);

    // 로그인이 실패(false)하면 에러 메시지를 띄웁니다.
    if (!success) {
      errorMsg.value = "로그인 실패. 아이디/비번을 확인하세요.";
    }
  } else {
    // [회원가입 모드일 때]
    // authStore에 있는 register 함수를 실행합니다.
    const success = await authStore.register(username.value, password.value);

    if (success) {
      // 회원가입이 성공하면 알림창을 띄우고, 로그인 모드로 화면을 바꿉니다.
      alert("가입 완료! 로그인 해주세요.");
      isLogin.value = true;
    } else {
      // 회원가입 실패 시 에러 메시지를 저장합니다.
      errorMsg.value = "회원가입 실패. 이미 존재하는 아이디일 수 있습니다.";
    }
  }
};
</script>

<template>
  <div class="min-h-screen flex bg-slate-100">
    <!-- 로그인/회원가입 입력 폼 -->
    <div
      class="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 lg:p-24 bg-white relative"
    >
      <!-- 모바일(작은 화면)에서만 보이는 상단 컬러 바 -->
      <div
        class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-amber-100 to-stone-200 lg:hidden"
      ></div>

      <div class="max-w-[400px] w-full space-y-10 bg-white">
        <div class="text-left">
          <!-- 제목: 모드에 따라 텍스트가 바뀝니다 (삼항 연산자 사용) -->
          <h2
            class="text-2xl font-semibold text-stone-900 tracking-tight text-center"
          >
            <template v-if="isLogin"> MOOD DIARY </template>
            <template v-else>
              새로운 여정을 위해<br />회원 가입을 해주세요!
            </template>
          </h2>
        </div>

        <!-- 입력 폼 영역 -->
        <!-- @submit.prevent: 폼 제출 시 새로고침 되는 것을 막고 handleSubmit 함수를 실행합니다. -->
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div class="space-y-5">
            <!-- 아이디 입력 창 -->
            <div>
              <label
                for="username"
                class="block text-sm font-semibold text-stone-700 mb-2"
                >Username</label
              >
              <!-- v-model="username": 입력한 값이 자동으로 script의 username 변수에 저장됩니다. -->
              <input
                v-model="username"
                id="username"
                name="username"
                type="text"
                required
                class="block w-full px-4 py-3.5 bg-stone-50 border border-stone-200 rounded-xl focus:ring-2 focus:ring-black focus:border-black transition-all placeholder-stone-400 text-stone-900"
                placeholder="아이디를 입력하세요"
              />
            </div>

            <!-- 비밀번호 입력 창 -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label
                  for="password"
                  class="block text-sm font-semibold text-stone-700"
                  >Password</label
                >
              </div>
              <input
                v-model="password"
                id="password"
                name="password"
                type="password"
                required
                class="block w-full px-4 py-3.5 bg-stone-50 border border-stone-200 rounded-xl focus:ring-2 focus:ring-black focus:border-black transition-all placeholder-stone-400 text-stone-900"
                placeholder="비밀번호를 입력하세요"
              />
            </div>
          </div>

          <!-- 에러 메시지창: 에러가 있을 때만(v-if="errorMsg") 보입니다. -->
          <p
            v-if="errorMsg"
            class="text-rose-600 text-sm font-medium bg-rose-50 px-4 py-3 rounded-lg flex items-center gap-2"
          >
            <!-- 에러 아이콘 SVG -->
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            {{ errorMsg }}
          </p>

          <!-- 제출 버튼 -->
          <button
            type="submit"
            class="w-full flex justify-center py-4 px-4 border border-transparent text-base font-bold rounded-xl text-white bg-stone-900 hover:bg-black focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-stone-900 transition-all shadow-lg hover:shadow-xl transform active:scale-[0.98]"
          >
            {{ isLogin ? "Sign In" : "Sign Up" }}
          </button>
        </form>

        <!-- 구분선 (Or) -->
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-stone-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-stone-400">Or</span>
          </div>
        </div>

        <!-- 로그인/회원가입 모드 전환 버튼 -->
        <div class="text-center">
          <!-- 클릭하면 isLogin 값을 반대로 바꿉니다 (!isLogin) -->
          <button
            @click="isLogin = !isLogin"
            class="text-sm font-medium text-stone-600 hover:text-stone-900 transition-colors"
          >
            {{
              isLogin
                ? "계정이 없으신가요? 회원가입"
                : "이미 계정이 있으신가요? 로그인"
            }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
