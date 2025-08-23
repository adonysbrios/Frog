<script setup>
import LogoIcon from '@/components/icons/LogoIcon.vue';
import SearchComponent from '@/components/SearchComponent.vue';

</script>

<template>
  <main>
    <div>
      <LogoIcon v-view-transition-name="'logo'" class="mx-auto px-10 mb-4 max-w-[280px]"/>
      <SearchComponent size="x"/>
      <p class="text-center text-[13px] mt-4 max-w-[400px] mx-auto">Hi, what do you wanna search today?</p>
    </div>
  </main>
</template>

<style scoped>

  .logo{
    width: 100px;
  }

  div {
    max-width: 600px;
    margin: 27vh auto;
    padding: 0 20px;
  }
</style>
