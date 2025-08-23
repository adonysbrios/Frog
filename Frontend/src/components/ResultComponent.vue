<template>
  <a :href="props.data.doc_info.link" class="flex max-w-[700px] gap-2 mt-5" v-if="props.data.doc_info">
    <img
      class="w-10 h-10 rounded-full"
      :src="props.data.doc_info.icon"
      :alt="props.data.doc_info.title + ' icon'"
    />
    <section>
      <p class="text-[12px] text-neutral/60 max-w-[600px] text-wrap truncate">
        {{ props.data.doc_info.link }}
      </p>
      <p class="text-[20px] text-primary">
        {{ props.data.doc_info.title }}
      </p>

      <p class="text-[15px] text-neutral/80">
        {{ props.data.doc_info.text }}... <span class="text-neutral"> Read more </span>
      </p>
    </section>
  </a>
</template>

<script setup>
const props = defineProps(["data"]);
</script>
