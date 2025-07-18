<template>
  <a :href="props.data.link" class="flex max-w-[700px] gap-2 mt-5 items-center">
    <img class="w-10 h-10 rounded-full" :src="props.data.icon" :alt="props.data.title + ' icon'" />
    <section>
      <p class="text-[12px] text-neutral/60 max-w-[600px] text-wrap truncate">{{ props.data.link }}</p>
      <p class="text-[20px] text-primary" v-if="props.data.title">{{ props.data.title }}</p>
      <p class="text-[20px] text-primary" v-else>No title</p>

      <p class="text-[15px] text-neutral/80" v-if="props.data.info">{{ props.data.info }}</p>
      <p class="text-[15px] text-neutral/80" v-else>{{ props.data.description }}</p>
    </section>
</a>
</template>

<script setup>
import { useRouter } from 'vue-router';

const props = defineProps(["data"]);
const router = useRouter()
</script>
